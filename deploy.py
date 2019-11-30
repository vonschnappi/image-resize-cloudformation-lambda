
import boto3
import zipfile
import os
import json
import uuid
import subprocess

def install_lambda_dependecies():
    subprocess.run(['pip3', 'install', '-r', 'requirements.txt', '--target', 'lambda'])

def zip_lambda(dirname, zip_name):
    print('Zipping lambda')
    length = len(dirname) 
    zf = zipfile.ZipFile(zip_name, 'w')
    for dirname, subdirs, files in os.walk('lambda'):
        folder = dirname[length:]
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename), os.path.join(folder, filename))
    zf.close()

def create_lambda_bucket(s3_client, bucket_name):
    print('Creating bucket to store lambda zip')
    try:
        response = s3_client.create_bucket(Bucket=bucket_name)
    except Exception as e:
        print(e)
        return False
    return True

def upload_lambda_to_bucket(s3_client, bucket_name, file_name):
    print('Uploading lambda zip to bucket')
    try:
        with open(file_name, 'rb') as f:
            response = s3_client.upload_fileobj(f, bucket_name, file_name)
    except Exception as e:
        print(e)
        return False
    return True

def get_cf_template(cf, template):
    with open(template, 'r', encoding='utf-8') as template_fileobj:
        template_data = template_fileobj.read()
    cf.validate_template(TemplateBody=template_data)
    return template_data

def deploy_cloud_formation(cf, params):
    print('Creating {}'.format(params['StackName']))
    stack_result = cf.create_stack(
        StackName=params['StackName'],
        TemplateBody=params['TemplateBody'],
        Parameters=params['Parameters'],
        Capabilities=params['Capabilities'],
        OnFailure='DELETE'
    )
    waiter = cf.get_waiter('stack_create_complete')
    waiter.wait(StackName=params['StackName'])

def main():
    s3_client = boto3.client('s3')
    cf = boto3.client('cloudformation')
    lambda_bucket_name = 'lambda-bucket-for-image-resize'
    img_bucket_name = 'bucket-for-resized-images' + str(uuid.uuid1())
    Lambda_name = 'image_resize'
    repo = 'YOUR-REPO-OF-THE-NODEJS-WEBSERVER'
    #see https://github.com/vonschnappi/upload-image-to-s3-web-server
    work_dir = repo.split('/')[4].split('.')[0]
    zip_name = 'function.zip'

    template_data = get_cf_template(cf, 'image-resize.yml')
    cf_params = [{
            'ParameterKey': 'ImageBucketName',
            'ParameterValue': img_bucket_name
            },
            {
            'ParameterKey': 'LambdaBucketName',
            'ParameterValue': lambda_bucket_name
            },
            {
            'ParameterKey': 'LambdaName',
            'ParameterValue': Lambda_name
            },
            {
            'ParameterKey': 'Repository',
            'ParameterValue': repo
            },
            {
            'ParameterKey': 'WorkingDirectory',
            'ParameterValue': work_dir
            }]
    params = {
        'StackName': 'ImageResizeStack',
        'TemplateBody': template_data,
        'Parameters': cf_params,
        'Capabilities': ['CAPABILITY_NAMED_IAM']
        }

    install_lambda_dependecies()
    zip_lambda('lambda', zip_name)
    create_lambda_bucket(s3_client, lambda_bucket_name)
    upload_lambda_to_bucket(s3_client, lambda_bucket_name, zip_name)
    deploy_cloud_formation(cf, params)

if __name__ == '__main__':
    main()