import json
from pickle import TRUE
import boto3
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import sys
from io import BytesIO

import config
import util


def main(event, context):
    #raise Exception(event)
    bucket = event["bucket"]
    key = event["key"]
    filename = key +'.png'

    util.get_pkgs(bucket)

    s3_client = boto3.client('s3')
    resp = s3_client.get_object(Bucket=bucket, Key=filename)
    image_bytes = resp['Body'].read()
    imageLabel = prediction(image_bytes)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(config.IMAGES_TABLE)
    item = {
        'label': {'Value': imageLabel, 'Action': 'PUT'}
    }
    
    table.update_item(
        Key={
            'id': key
        },
        AttributeUpdates=item
    )

    finalResponse = {
        "statusCode": 200,
        "body": json.dumps(imageLabel)
    }
    return finalResponse

def prediction(image_bytes):
    sys.path.insert(0, '/tmp/'+config.local_dir+'/') #make libs in local_dir visible to python
    
    from joblib import  load
    import numpy as np
    import sklearn                 #this sklearn is used in load pca.joblib
    from tensorflow import keras
    from PIL import Image

    keras_model_path = config.keras_model_path
    model = keras.models.load_model(keras_model_path)
    pca = load(config.pca) 
    input_shape = model.input_shape
    cutoff = load(config.cutoff)
    image = np.array(Image.open(BytesIO(image_bytes)))
    features = model.predict(image.reshape((1,input_shape[1],input_shape[2],input_shape[3])))
    score = -pca.score(features)
    if score < cutoff:
        label = 'good'
    else:
        label = 'may be bad'
    return label
