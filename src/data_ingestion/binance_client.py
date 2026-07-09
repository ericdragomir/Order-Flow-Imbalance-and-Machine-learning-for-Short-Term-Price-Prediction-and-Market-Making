import asyncio
import websockets 
import json
import aiohttp

from lob_reconstructor import LocalOrderBook
from storage import DataStorage

SYMBOL = "SOLUSDT"
STREAM_DEPTH = f"{SYMBOL.lower()}@depth@100ms"
STREAM_TRADE = f"{SYMBOL.lower()}@trade"

BINANCE_WSL_URL = f"wss://stream.binance.com:9443/stream?streams={STREAM_DEPTH}/{STREAM_TRADE}"
BINANCE_REST_URL = f"https://api.binance.com/api/v3/depth?symbol={SYMBOL.upper()}&limit=1000"

lob = LocalOrderBook()
storage = DataStorage(SYMBOL, batch_size=5000)

last_update_id = 0
is_synchronized = False
event_queue = asyncio.Queue()

async def fetch_snapshot():
    # Get the initial LOB
    async with aiohttp.ClientSession() as session:
        async with session.get(BINANCE_REST_URL) as response:
            if response.status == 200:
                snapshot = await response.json()
                return snapshot
            else:
                raise Exception(f"Error getting the snapshot: {response.status}")


async def handle_depth_event(data):
    global last_update_id, is_synchronized
    
    # We process change events in the order book (Diff Depth)
    event_data = data["data"]
    final_update_id = event_data['u']
    first_update_id = event_data['U']

    if not is_synchronized:
        await event_queue.put(event_data)
        return

    if first_update_id > last_update_id:
        lob.update_diff(event_data)
        last_update_id = final_update_id

        # Obtain the best 10 levels
        top_bids, top_asks = lob.get_top_n_levels(n=10)
        
        # Store the snapshot
        storage.store_depth(
            event_time=event_data.get('E', 0),
            u_first=first_update_id,
            u_final=final_update_id,
            bids=top_bids,
            asks=top_asks
        )

        bb, ba, spr, mid = lob.get_inside_market()
        print(f"[LOB] Mid: {mid:.2f} | Spread: {spr:.2f} | Best bid: {bb:.2f} | Best ask: {ba:.2f}")

    elif final_update_id <= last_update_id:
        pass # Old event that we ignore safely
    else:
        print(f"[ALERT] Desconection or IDs jump ({first_update_id} > {last_update_id} + 1). Reseting...")
        is_synchronized = False
        asyncio.create_task(synchronize_books())

async def synchronize_books():
    global last_update_id, is_synchronized
    print("[SYSTEM] Starting synchonization process...")

    while not event_queue.empty():
        event_queue.get_nowait()

    try:
        snapshot = await fetch_snapshot()
        last_update_id = snapshot['lastUpdateId']
        lob.apply_snapshot(snapshot)
        print(f"[REST] Snapshot obtained. LastUpdateID: {last_update_id}")

    except Exception as e:
        print(f"[ERROR] Could not synchronize: {e}. Trying again in 5s...")
        await asyncio.sleep(5)
        asyncio.create_task(synchronize_books())
        return

    print("[SYSTEM] Emptying temporal buffer for integrating streams...")
    while True:
        if event_queue.empty():
            await asyncio.sleep(0.1)
            continue

        event = await event_queue.get()
        final_update_id = event['u']
        first_update_id = event['U']

        if first_update_id <= last_update_id + 1 <= final_update_id:
            print(f"[SUCCESS] Successful integration with the event WS: {first_update_id} <= {last_update_id + 1} <= {final_update_id}")
            last_update_id = final_update_id
            is_synchronized = True
            break
        elif final_update_id <= last_update_id:
            continue # Old event, we ignore it
        else:
            print("[ERROR] The snapshot became obsolete before finding the integration. Restarting procress...")
            asyncio.create_task(synchronize_books())
            break

async def handle_trade_event(data):
    global is_synchronized
    
    # Process the real execution events (trades)
    event_data = data["data"]
    price = event_data['p']
    quantity = event_data['q']
    is_buyer_maker = event_data['m']

    direction = "SELL" if is_buyer_maker else "BUY"
    
    if is_synchronized:
        storage.store_trade(event_data=event_data)
        print(f"[TRADE] Price: {price} | Quantity: {quantity} | Direction: {direction}")

async def main():
    print(f"Connecting to Binance websocket for {SYMBOL.upper()}...")

    asyncio.create_task(synchronize_books())

    async with websockets.connect(BINANCE_WSL_URL) as websocket:
        print("Connection established succesfully. Streaming the market...")
        
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                stream_name = data.get('stream', '')

                if stream_name:
                    if "@depth" in stream_name:
                        await handle_depth_event(data)
                    elif "@trade" in stream_name:
                        await handle_trade_event(data)
                else:
                    print(f"[SYSTEM MESSAGE] Received: {data}")

        except websockets.exceptions.ConnectionClosed:
            print("Server closed connection. Trying to reconnect...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            storage.close()

if __name__ == '__main__':
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SYSTEM] Program stopped manually by the user.")