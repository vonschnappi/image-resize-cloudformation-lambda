# image-resize-cloudformation-lambda

This repo contains a lambda function for resizing images once uploaded to S3. It also contains the cloudformation
template to deploy the stack supporting image resize.

## Stack
1. Bucket for images and resized images
2. Bucket to hold the zipped lambda
3. Lambda function
4. Amazon linux machine

## Deploy
Run `deploy.py`.

## Dependecies
1. Boto3
2. Requests
3. Pillow - pillow is included in this repo. There's an issue currently with lambda if you install Pillow locally and then
zip it and upload. The solution is to install Pillow on an Amazon linux and download it. 
See [Python 3.7 plus Pillow in Lambda not working](https://forums.aws.amazon.com/thread.jspa?messageID=915630) 
[ImportError: cannot import name _imaging](https://stackoverflow.com/questions/25340698/importerror-cannot-import-name-imaging) 
for more information.

## Supporting repo
This stack requires a repo that contains node js server for uploading images. You can find it [here](https://github.com/vonschnappi/upload-image-to-s3-web-server). It needs to be referenced
in `deploy.py`.
