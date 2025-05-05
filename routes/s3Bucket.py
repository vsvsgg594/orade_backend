import boto3
import os
import logging
from botocore.exceptions import ClientError


bucketLink = os.getenv('bucketLink')
    
logging.basicConfig(level=logging.INFO)


# s3 bucket subfunctions

# AWS_BUCKET = os.getenv('AWS_BUCKET')
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


# s3 = boto3.resource('s3',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
# bucket = s3.Bucket(AWS_BUCKET)

# def s3Upload(contents: bytes, key: str):
#     logging.info(f'Uploading {key} to s3')
#     bucket.put_object(Key=key, Body=contents)

# s4 = boto3.client('s3',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# def s3Download(key: str):
#     try:
#         return s3.Object(bucket_name=AWS_BUCKET, key= key).get()['Body'].read()
#     except ClientError as err:
#         logging.error(str(err))

