import os
import boto3
import subprocess
import zipfile
import shutil
from io import BytesIO


import config

local_dir =config.local_dir
req_file_name = config.req_file_name
models_file = config.models_file


def download_pkgs(bucket,filename,dir):
    '''download zip file "filename" from "bucket" and unzip it into "dir" '''
    print("downloading libraries from S3")
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)

    # mem buffer
    filebytes = BytesIO()

    # download to the mem buffer
    my_bucket.download_fileobj(filename, filebytes)

    # create zipfile obj
    file = zipfile.ZipFile(filebytes)

    # extact
    file.extractall('/tmp/'+dir)

def install_pkgs(bucket):
    #tmp is the only writable dir in lambda env. libs is our choice for where to put python packages
    print("Installing libraries")
    command_text ='python -m pip install -r '+req_file_name+' -t /tmp/'+local_dir+' --no-cache-dir'
    subprocess.call(command_text.split())
    client = boto3.client('s3')
    client.upload_file(req_file_name, bucket, req_file_name)            #requirements file is found in root dir (put there on deployment)
    shutil.make_archive('/tmp/'+local_dir, 'zip', '/tmp/'+local_dir)    #target filename should be written without extension
    client.upload_file('/tmp/'+local_dir+'.zip', bucket, local_dir+'.zip')

    
def get_pkgs(bucket):
    if not os.path.isdir('/tmp/'+ local_dir ):          #check if /tmp/ has our packages, if it does, do nothing
        client = boto3.client('s3')
        results = client.list_objects(Bucket=bucket, Prefix=local_dir+'.zip')
        if 'Contents' in results:                        #if dependencies archive found in S3
            client.download_file(bucket,req_file_name,'/tmp/old_'+req_file_name)
            import filecmp
            if filecmp.cmp(req_file_name, '/tmp/old_'+req_file_name):     #if req list didn't change, download saved packages
                download_pkgs(bucket,local_dir+'.zip',local_dir+'/')
            else: 
                install_pkgs(bucket)
        else:
            install_pkgs(bucket)
        download_pkgs(bucket,models_file,'')
    else:
        print("found local tmp/ folder")
