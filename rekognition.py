from typing import List

import boto3
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1',
)


def get_labels(image_url: str) -> List[str]:
    response = client.detect_labels(
        Image={
            'Bytes': download(image_url),
        },
        MaxLabels=5,
    )

    return [label['Name'] for label in response['Labels'] if label['Confidence'] > 80]


def download(url: str) -> bytes:
    response = httpx.get(url)

    return response.content
