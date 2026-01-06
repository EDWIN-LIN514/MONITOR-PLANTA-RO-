import pandas as pd
import numpy as np

def calculate_dp(p_in, p_out):
    return p_in - p_out

def analyze_dp_trend(df, window=5):
    if len(df) < window:
        return False, 0
    
    # Calculate daily DP
    df['DP'] = df['P_In'] - df['P_Out']
    recent = df.tail(window)
    
    # Simple linear trend check
    x = np.arange(len(recent))
    y = recent['DP'].values
    slope, _ = np.polyfit(x, y, 1)
    
    # If slope is positive and substantial
    threshold_slope = 0.05 
    is_increasing = slope > threshold_slope
    return is_increasing, slope

def calculate_daily_production(current_meter, last_meter):
    if last_meter is None:
        return 0
    return max(0, current_meter - last_meter)

def check_stock_alerts(inventory_df, critical_pct=20):
    alerts = []
    # Assuming we have an 'Initial_Stock' or just comparing to a reference or max stock
    # For now, let's assume Stock is absolute and alerts are based on a fixed low value or logic
    # The requirement says 'If stock is < 20%'. Let's assume 100 is max for demo or add Max_Stock.
    for index, row in inventory_df.iterrows():
        # Using a simple check for demo: if Stock < 20
        if row['Stock'] < 20: 
            alerts.append(f"Stock Crítico: {row['Chemical']}")
    return alerts
