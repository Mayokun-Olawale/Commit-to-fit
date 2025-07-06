# Utilized GPT 4o to generate script
from google.cloud import bigquery
from datetime import datetime, timedelta
import random
import re

client = bigquery.Client()

table_id = "diegoperez16techx25.Committees.Workouts"

def get_last_workout_number():
    query = f"""
        SELECT MAX(CAST(REGEXP_EXTRACT(WorkoutId, r'workout(\\d+)') AS INT64)) AS max_id
        FROM `{table_id}`
        WHERE REGEXP_CONTAINS(WorkoutId, r'^workout\\d+$')
    """
    result = client.query(query).result()
    row = next(result)
    return row.max_id if row.max_id is not None else 0

def generate_sql_insert(user_id, workout_id):
    start_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
    end_time = start_time + timedelta(minutes=random.randint(20, 90))

    return f"""
        INSERT INTO `{table_id}` (
            WorkoutId, UserId, StartTimestamp, EndTimestamp,
            StartLocationLat, StartLocationLong,
            EndLocationLat, EndLocationLong,
            TotalDistance, TotalSteps, CaloriesBurned
        )
        VALUES (
            '{workout_id}', '{user_id}',
            DATETIME '{start_time.strftime("%Y-%m-%d %H:%M:%S")}',
            DATETIME '{end_time.strftime("%Y-%m-%d %H:%M:%S")}',
            {round(random.uniform(-90.0, 90.0), 6)},
            {round(random.uniform(-180.0, 180.0), 6)},
            {round(random.uniform(-90.0, 90.0), 6)},
            {round(random.uniform(-180.0, 180.0), 6)},
            {round(random.uniform(1.0, 10.0), 2)},
            {random.randint(2000, 15000)},
            {round(random.uniform(100.0, 900.0), 2)}
        )
    """

start_id = get_last_workout_number() + 1
users = ["user5","user6","user7","user8","user9","user10","user11","user12","user13","user14","user15","user16"]
for user in users:
    for i in range(3):  # 3 workouts per user
        workout_number = start_id
        workout_id = f"workout{workout_number}"
        query = generate_sql_insert(user, workout_id)
        client.query(query).result()
        print(f"✅ Inserted {workout_id} for {user}")
        start_id += 1
