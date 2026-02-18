import boto3

# Create S3 client
s3 = boto3.client("s3")

# Upload simple text
s3.put_object(
    Bucket="weathertodaytn",
    Key="raw/test.txt",
    Body="Hello from my first AWS pipeline!"
)

print("File uploaded successfully!")
