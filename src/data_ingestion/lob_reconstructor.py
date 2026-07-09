from collections import defaultdict

class LocalOrderBook:
    def __init__(self):
        self.bids = defaultdict(float)
        self.asks = defaultdict(float)
    
    def apply_snapshot(self, snapshot):
        self.bids.clear()
        self.asks.clear()

        for price, quantity in snapshot['bids']:
            self.bids[float(price)] = float(quantity)
        for price, quantity in snapshot['asks']:
            self.asks[float(price)] = float(quantity)
            
    def update_diff(self, event_data):
        
        for price_str, quantity_str in event_data['b']:
            price = float(price_str)
            quantity = float(quantity_str)
            if quantity == 0.0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = quantity
        
        for price_str, quantity_str in event_data['a']:
            price = float(price_str)
            quantity = float(quantity_str)
            if quantity == 0.0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = quantity

    def get_inside_market(self):
        if not self.bids or not self.asks:
            return 0.0, 0.0, 0.0, 0.0

        best_bid = max(self.bids.keys())

        valid_asks = [p for p in self.asks.keys() if p > best_bid]
        
        if not valid_asks:
            best_ask = min(self.asks.keys())
        else:
            best_ask = min(valid_asks)

        spread = best_ask - best_bid
        
        if spread <= 0:
            spread = 0.01  # Spread mínimo en BTCUSDT
            best_ask = best_bid + spread

        mid_price = (best_ask + best_bid) / 2
        
        return best_bid, best_ask, spread, mid_price

    def get_top_n_levels(self, n=10):
        # Extract the best n levels
        sorted_bids = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)
        sorted_asks = sorted(self.asks.items(), key=lambda x: x[0])
        
        top_bids = sorted_bids[:n]
        top_asks = sorted_asks[:n]
        
        # Relleno de seguridad con None si el libro tuviera menos de N niveles
        while len(top_bids) < n: top_bids.append((None, None))
        while len(top_asks) < n: top_asks.append((None, None))
            
        return top_bids, top_asks