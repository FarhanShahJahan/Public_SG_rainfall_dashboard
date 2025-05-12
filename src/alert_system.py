import pandas as pd

def check_alerts(current_readings, monthly_avg, threshold=1.0):
    """Compare current readings against monthly averages"""
    current_month = pd.to_datetime('now').month
    monthly_avg = monthly_avg[monthly_avg['month'] == current_month]
    
    merged = current_readings.merge(
        monthly_avg,
        on=['stationId', 'name'],
        suffixes=('_current', '_avg')
    )
    
    merged['exceeds_avg'] = merged['value_current'] > (threshold * merged['value_avg'])
    return merged[merged['exceeds_avg']]