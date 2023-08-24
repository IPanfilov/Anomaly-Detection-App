"Database layer - the dynamo version"
import uuid
import config

import boto3

table_name = config.IMAGES_TABLE

def list_images():
    "Select all the employees from the database"
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        return table.scan()["Items"]
    except:
        return 0

def load_image(image_id):
    "Select one image from the database"
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key={
                'id': image_id
            }
        )
        return response['Item']
    except:
        pass

def add_image(image_id, name, logo_key = None):
    "Add an image to the database"
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        item = {
            'id': image_id,
            'name': name,
            'label':"unprocessed"
        }
        if logo_key:
            item['logo'] = logo_key
        

        table.put_item(
            Item=item
        )
    except:
        pass


def replace_image(image_id, name, logo_key = None):
    "Replace an image in the database"
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        item = {
            'name': {'Value': name, 'Action': 'PUT'},
            'label': {'Value': "unprocessed", 'Action': 'PUT'}
        }
        if logo_key:
            item['logo'] = {'Value': logo_key, 'Action': 'PUT'}
        
        table.update_item(
            Key={
                'id': image_id
            },
            AttributeUpdates=item
        )
    except:
        pass

def delete_image(image_id):
    "Delete an image."
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        table.delete_item(
            Key={
                'id': image_id
            }
        )
    except:
        pass
