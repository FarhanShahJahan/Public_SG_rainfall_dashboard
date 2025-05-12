from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd
from supabase import create_client, Client

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 7, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

def fetch_rainfall_data():
    url = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Process data
    stations = {s['id']: s for s in data['data']['stations']}
    records = []
    
    for reading in data['data']['readings']:
        for item in reading['data']:
            station = stations[item['stationId']]
            records.append({
                'timestamp': reading['timestamp'],
                'station_id': item['stationId'],
                'station_name': station['name'],
                'latitude': station['labelLocation']['latitude'],
                'longitude': station['labelLocation']['longitude'],
                'rainfall_mm': item['value'],
                'created_at': datetime.utcnow().isoformat()
            })
    
    return pd.DataFrame(records)

def save_to_supabase(**context):
    """Save data to Supabase"""
    df = context['ti'].xcom_pull(task_ids='fetch_data')
    
    # Supabase connection
    url: str = "https://rqbcdfdxumzrzjymtsnp.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJxYmNkZmR4dW16cnpqeW10c25wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY4MDQzNjEsImV4cCI6MjA2MjM4MDM2MX0.L7oaNbuJW2sKb5n37WcQ2N4KSCay1bfbvxwxcSoP9a0"
    supabase: Client = create_client(url, key)
    
    # Upsert data
    data = df.to_dict('records')
    response = supabase.table('rainfall_measurements').upsert(data).execute()
    
    if hasattr(response, 'error') and response.error:
        raise ValueError(f"Supabase error: {response.error}")

dag = DAG(
    'singapore_rainfall_pipeline',
    default_args=default_args,
    description='Collects Singapore rainfall data every 5 minutes',
    schedule_interval='*/5 * * * *',
    catchup=False
)

fetch_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_rainfall_data,
    dag=dag
)

save_task = PythonOperator(
    task_id='save_to_supabase',
    python_callable=save_to_supabase,
    provide_context=True,
    dag=dag
)

fetch_task >> save_task