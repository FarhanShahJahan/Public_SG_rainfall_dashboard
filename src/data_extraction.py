# import requests
# import pandas as pd
# import random
# from datetime import datetime, timedelta

# def generate_mock_data():
#     """Generate realistic mock rainfall data for Singapore"""
#     stations = [
#         {'id': 'S101', 'name': 'Ang Mo Kio', 'latitude': 1.3691, 'longitude': 103.8454},
#         {'id': 'S102', 'name': 'Bedok', 'latitude': 1.3240, 'longitude': 103.9300},
#         {'id': 'S103', 'name': 'Bishan', 'latitude': 1.3508, 'longitude': 103.8484},
#         {'id': 'S104', 'name': 'Changi', 'latitude': 1.3574, 'longitude': 103.9886},
#         {'id': 'S105', 'name': 'Jurong East', 'latitude': 1.3329, 'longitude': 103.7426},
#         {'id': 'S106', 'name': 'Pasir Ris', 'latitude': 1.3733, 'longitude': 103.9495},
#         {'id': 'S107', 'name': 'Punggol', 'latitude': 1.3984, 'longitude': 103.9075},
#         {'id': 'S108', 'name': 'Sembawang', 'latitude': 1.4489, 'longitude': 103.8195},
#         {'id': 'S109', 'name': 'Tampines', 'latitude': 1.3536, 'longitude': 103.9443},
#         {'id': 'S110', 'name': 'Woodlands', 'latitude': 1.4361, 'longitude': 103.7860}
#     ]
    
#     readings = []
#     current_time = datetime.utcnow()
    
#     for station in stations:
#         # Base value + random variation (0-15mm)
#         base_value = random.uniform(0, 15)
#         # Add some geographic variation (eastern areas tend to get more rain)
#         if station['longitude'] > 103.9:  # Eastern Singapore
#             base_value += random.uniform(0, 5)
#         # Add time-of-day variation (afternoons get more rain)
#         if 12 <= current_time.hour <= 18:
#             base_value += random.uniform(0, 8)
        
#         readings.append({
#             'timestamp': current_time.isoformat() + "Z",
#             'stationId': station['id'],
#             'value': round(max(0, base_value), 1),  # Ensure non-negative
#             'name': station['name'],
#             'latitude': station['latitude'],
#             'longitude': station['longitude']
#         })
    
#     return pd.DataFrame(readings)

# def get_latest_readings():
#     """Try real API first, fall back to mock data"""
#     BASE_URL = "https://api-open.data.gov.sg/v2/real-time/api/rainfall" 
    
#     try:
#         response = requests.get(BASE_URL, timeout=5)
#         response.raise_for_status()
#         data = response.json()
        
#         # Check if data contains valid readings
#         if not data['data']['readings'] or all(r['value'] == 0 for r in data['data']['readings'][0]['data']):
#             return generate_mock_data()
            
#         # Process real data
#         stations = []
#         for station in data['data']['stations']:
#             stations.append({
#                 'id': station['id'],
#                 'name': station['name'],
#                 'latitude': station['labelLocation']['latitude'],
#                 'longitude': station['labelLocation']['longitude']
#             })
        
#         readings = []
#         for reading in data['data']['readings']:
#             for item in reading['data']:
#                 readings.append({
#                     'timestamp': reading['timestamp'],
#                     'stationId': item['stationId'],
#                     'value': item['value']
#                 })
        
#         stations_df = pd.DataFrame(stations)
#         readings_df = pd.DataFrame(readings)
#         merged_df = pd.merge(readings_df, stations_df, left_on='stationId', right_on='id')
        
#         # If all values are zero, use mock data
#         if merged_df['value'].sum() == 0:
#             return generate_mock_data()
            
#         return merged_df.drop(columns=['id'])
    
#     except Exception:
#         return generate_mock_data()