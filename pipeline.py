import requests
import boto3
import psycopg2
import json
from config import *

# Step 1: Call API
url = f"https://api.openweathermap.org/data/2.5/weather?q=Chicago&units=metric&appid={API_KEY}"
response = requests.get(url)
data = response.json()
print(data)


# Step 2: Save JSON locally
with open("raw/weather.json", "w") as f:
    json.dump(data, f)

# Step 3: Upload to S3
s3 = boto3.client("s3")
s3.upload_file("weather.json", S3_BUCKET, "raw/weather.json")

# Step 4: Insert into PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_data (
    city TEXT,
    temperature FLOAT,
    humidity INT
);
""")

cursor.execute("""
INSERT INTO weather_data (city, temperature, humidity)
VALUES (%s, %s, %s);
""", (data["name"], data["main"]["temp"], data["main"]["humidity"]))

conn.commit()
cursor.close()
conn.close()

print("Pipeline executed successfully!")
