from datetime import datetime, timedelta
import pandas as pd
from src.db import get_db
import pytz 

# Singapore Timezone
SGT = pytz.timezone('Asia/Singapore')

# Get data from Supabase
db = get_db()

# def get_last_hour_data():
#     now_sgt = datetime.now(SGT)
#     one_hour_ago = (now_sgt - timedelta(hours=1)).isoformat()
#     res = db.table('rainfall_measurements') \
#             .select('*') \
#             .gte('timestamp', one_hour_ago) \
#             .order('timestamp', desc=True) \
#             .execute()
#     return pd.DataFrame(res.data)

def get_station_data():
    station_data = db.table('station') \
        .select('station_id, station_name,longitude,latitude') \
        .execute()
    
    station_data = pd.DataFrame(station_data.data)
    return(station_data)

# Get last 12 hours of data
def get_last_12hour_data():
    now_sgt = datetime.now(SGT)
    twelve_hours_ago = (now_sgt - timedelta(hours=12)).isoformat()

    last_12hr_data = db.table('rainfall_measurements') \
        .select('station_id,rainfall_mm, timestamp') \
        .gte('timestamp', twelve_hours_ago) \
        .execute()
    
    last_12hr_data = pd.DataFrame(last_12hr_data.data)
    last_12hr_data['timestamp'] = pd.to_datetime(last_12hr_data['timestamp']).dt.tz_convert('Asia/Singapore')
    
    station_data = get_station_data()
    last_12hr_data = pd.merge(last_12hr_data,station_data,how='left',on='station_id')

    return (last_12hr_data)


def get_current_month_data():
    # Get current month's first day in SGT
    first_day_of_month = datetime.now(SGT).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Query from Supabase
    monthly_data = db.table('rainfall_measurements') \
                .select('station_id,rainfall_mm, timestamp') \
                .gte('timestamp', first_day_of_month.isoformat()) \
                .execute()
    df_monthly = pd.DataFrame(monthly_data.data)
    
    station_data = get_station_data()
    df_monthly = pd.merge(df_monthly,station_data,how='left',on='station_id')
    return(df_monthly)

