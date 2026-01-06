import pandas as pd
import json
import os
from datetime import datetime

class ROStorage:
    def __init__(self, base_path):
        self.base_path = base_path
        self.config_path = os.path.join(base_path, 'config.json')
        self.operational_path = os.path.join(base_path, 'operational_data.csv')
        self.inventory_path = os.path.join(base_path, 'inventory.csv')
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        
        # Initial config
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                json.dump({"threshold_dp": 2.5, "critical_stock_pct": 20}, f)

        # Operational data
        if not os.path.exists(self.operational_path):
            df = pd.DataFrame(columns=[
                'Date', 'P_In', 'P_Out', 'P_Perm', 'P_Rej', 'P_Rec',
                'F_Perm', 'F_Rej', 'F_Rec', 'Meter_Reading'
            ])
            df.to_csv(self.operational_path, index=False)

        # Inventory
        if not os.path.exists(self.inventory_path):
            inv = pd.DataFrame([
                {"Chemical": "Antiescalante", "Stock": 100, "Daily_Cons": 0},
                {"Chemical": "Hipoclorito", "Stock": 100, "Daily_Cons": 0},
                {"Chemical": "Cloruro", "Stock": 100, "Daily_Cons": 0}
            ])
            inv.to_csv(self.inventory_path, index=False)

    def load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self, config):
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def get_operational_data(self):
        return pd.read_csv(self.operational_path)

    def save_operational_entry(self, data):
        df = self.get_operational_data()
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(self.operational_path, index=False)

    def get_inventory(self):
        return pd.read_csv(self.inventory_path)

    def update_inventory(self, df):
        df.to_csv(self.inventory_path, index=False)
