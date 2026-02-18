import requests
import boto3
import psycopg2
import json
from datetime import datetime
from config import S3_BUCKET, DB_HOST, DB_NAME, DB_USER, DB_PASS

# ---------------- STEP 1: CALL API ----------------
url = "https://api.open-meteo.com/v1/forecast?latitude=41.88&longitude=-87.63&current_weather=true"

response = requests.get(url)

if response.status_code != 200:
    print("API call failed:", response.text)
    exit()

data = response.json()

# ---------------- STEP 2: SAVE RAW JSON LOCALLY ----------------
with open("weather.json", "w") as f:
    json.dump(data, f)

# ---------------- STEP 3: UPLOAD TO S3 ----------------
s3 = boto3.client("s3")

s3.upload_file("weather.json", S3_BUCKET, "raw/weather.json")

# ---------------- STEP 4: EXTRACT REQUIRED FIELDS ----------------
temperature = data["current_weather"]["temperature"]
windspeed = data["current_weather"]["windspeed"]
current_time = datetime.now()

# ---------------- STEP 5: LOAD INTO POSTGRES ----------------
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)

cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_data (
    city TEXT,
    temperature FLOAT,
    windspeed FLOAT,
    created_at TIMESTAMP
);
""")

# Insert record
cursor.execute("""
INSERT INTO weather_data (city, temperature, windspeed, created_at)
VALUES (%s, %s, %s, %s);
""", ("Chicago", temperature, windspeed, current_time))

conn.commit()
cursor.close()
conn.close()

print("Pipeline executed successfully!")
