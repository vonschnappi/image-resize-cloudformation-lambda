import json
import requests
import boto3
import os
from PIL import Image
from io import BytesIO

def lambda_handler(event, context):
    print('Starting exec')
    bucket_name = event['Records'][0]["s3"]['bucket']['name']
    key = event['Records'][0]["s3"]['object']['key']
    file_name = key = os.path.splitext(key)[0]
    file_extension = os.path.splitext(key)[1].upper().replace('.', '')
    allowed_extensions = ['JPEG', 'JPG', 'PNG', 'GIF']
    if '_resized' in key:
        return {
            'statusCode': 400,
            'body': json.dumps('Already resized')
        }
    print(file_extension)
    if file_extension not in allowed_extensions:
        print('file extension not good')
        return {
            'statusCode': 400,
            'body': json.dumps('This is not an image')
        }

    s3 = boto3.client('s3')
    buffer = BytesIO()
    image_in_bytes = BytesIO(s3.get_object(Bucket=bucket_name,
                            Key=key)['Body'].read())
    img = Image.open(image_in_bytes)
    basewidth = 300
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(buffer, file_extension)
    buffer.seek(0)

    res = s3.put_object(Bucket=bucket_name, 
                    Key=file_name + '_resized.' + file_extension.lower()),
                    ACL='public-read',
                    Body=buffer)
    print(res)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }