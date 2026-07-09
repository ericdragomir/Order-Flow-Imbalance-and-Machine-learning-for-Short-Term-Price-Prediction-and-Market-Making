import os
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq

class DataStorage:
    def __init__(self, symbol, base_dir="../data/raw", batch_size=5000):
        self.symbol = symbol.upper()
        self.base_dir = base_dir
        self.batch_size = batch_size

        self.depth_buffer = []
        self.trade_buffer = []

        os.makedirs(f"{self.base_dir}/depth", exist_ok=True)
        os.makedirs(f"{self.base_dir}/trades", exist_ok=True)

    # Allow usage as a context manager: with DataStorage(...) as storage:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def store_depth(self, event_time, u_first, u_final, bids, asks):
        row = {
            "event_time": int(event_time),
            "first_update_id": int(u_first),
            "final_update_id": int(u_final),
        }
        
        for i in range(10):
            row[f"bid_p_{i+1}"] = bids[i][0]
            row[f"bid_q_{i+1}"] = bids[i][1]
            row[f"ask_p_{i+1}"] = asks[i][0]
            row[f"ask_q_{i+1}"] = asks[i][1]

        self.depth_buffer.append(row)

        if len(self.depth_buffer) >= self.batch_size:
            self.flush_depth()
    
    def store_trade(self, event_data):
        row = {
            "event_time": int(event_data.get('E', 0)),
            "trade_id": int(event_data.get('t', 0)),
            "price": float(event_data.get('p', 0.0)),
            "quantity": float(event_data.get('q', 0.0)),
            "is_buyer_maker": bool(event_data.get('m')) 
        }

        self.trade_buffer.append(row)

        if len(self.trade_buffer) >= self.batch_size:
            self.flush_trades()

    def _get_filename(self, data_type):
        # Microsecond precision avoids naming collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{self.base_dir}/{data_type}/{self.symbol}_{data_type}_{timestamp}.parquet"

    def flush_depth(self):
        if not self.depth_buffer:
            return
        
        # Direct conversion to PyArrow Table (Much faster than Pandas)
        table = pa.Table.from_pylist(self.depth_buffer)
        filename = self._get_filename("depth")
        pq.write_table(table, filename, compression="SNAPPY")

        print(f"[STORAGE] Saved {len(self.depth_buffer)} depth events at {filename}")
        self.depth_buffer.clear()
    
    def flush_trades(self):
        if not self.trade_buffer:
            return
        
        table = pa.Table.from_pylist(self.trade_buffer)
        filename = self._get_filename("trades")
        pq.write_table(table, filename, compression="SNAPPY")

        print(f"[STORAGE] Saved {len(self.trade_buffer)} trade events at {filename}")
        self.trade_buffer.clear()
        
    def close(self):
        print("[STORAGE] Flushing buffers before closing...")
        self.flush_depth()
        self.flush_trades()