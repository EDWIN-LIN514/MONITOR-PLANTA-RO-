import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set base path
base_path = os.getcwd()
operational_path = os.path.join(base_path, 'operational_data.csv')
inventory_path = os.path.join(base_path, 'inventory.csv')

# Generate 7 days of data
dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, 0, -1)]

# Increasing P_In to trigger alert
p_in = [300, 305, 310, 316, 322, 330, 340]
p_out = [280, 280, 279, 278, 277, 276, 275] # DP goes from 20 to 65

data = {
    'Date': dates,
    'P_In': p_in,
    'P_Out': p_out,
    'P_Perm': [10, 11, 10, 12, 11, 10, 11],
    'P_Rej': [250, 252, 251, 253, 250, 255, 260],
    'P_Rec': [200, 205, 202, 206, 200, 208, 210],
    'F_Perm': [1200, 1180, 1150, 1120, 1100, 1050, 1000],
    'F_Rej': [400, 410, 420, 430, 440, 450, 460],
    'F_Rec': [500, 500, 500, 500, 500, 500, 500],
    'Meter_Reading': [1000, 2000, 3000, 4000, 5000, 6000, 7000]
}

df = pd.DataFrame(data)
df.to_csv(operational_path, index=False)

# Inventory with some low stock
inv = pd.DataFrame([
    {"Chemical": "Antiescalante", "Stock": 15, "Daily_Cons": 2}, # Low stock (<20)
    {"Chemical": "Hipoclorito", "Stock": 80, "Daily_Cons": 5},
    {"Chemical": "Cloruro", "Stock": 50, "Daily_Cons": 10}
])
inv.to_csv(inventory_path, index=False)

print("Mock data generated successfully.")
