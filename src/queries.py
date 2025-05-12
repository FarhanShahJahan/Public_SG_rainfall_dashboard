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

# Get last 12 hours of data
def get_last_12hour_data():
    now_sgt = datetime.now(SGT)
    twelve_hours_ago = (now_sgt - timedelta(hours=12)).isoformat()
    last_12hr_data = db.table('rainfall_measurements') \
        .select('timestamp,station_name,rainfall_mm') \
        .gte('timestamp', twelve_hours_ago) \
        .execute()
    return pd.DataFrame(last_12hr_data.data)

