import os

import boto3
import json

from flask import Flask, jsonify, request, render_template_string, render_template, url_for, redirect, flash, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, validators
from werkzeug.utils import secure_filename

import config
import util
import database_dynamo as database  #EDITED

from io import BytesIO
# PIL import Image

from subprocess import call



app = Flask(__name__)
app.secret_key = config.FLASK_SECRET

#USERS_TABLE = os.environ['USERS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')
 
if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    client = boto3.client('dynamodb')

### FlaskForm set up
class ImageForm(FlaskForm):
    """flask_wtf form class"""
    image_id = HiddenField()
    photo = FileField(u'Image', [validators.InputRequired()])
    name = StringField(u'File Name')
    #location = StringField(u'Location', [validators.InputRequired()])
    #job_title = StringField(u'Job Title', [validators.InputRequired()])
    logo = HiddenField(u'logo')
    label = HiddenField(u'label')


@app.route("/")
def home():
    "Home screen"
    s3_client = boto3.client('s3')
    images = database.list_images()
    if images == 0:
        return render_template_string("""        
        {% extends "main.html" %}
        {% block head %}
        Submitted images
        <a class="btn btn-primary float-right" href="{{ url_for('add') }}">Add</a>
        {% endblock %}
        """)
    else:
        for image in images:
            image["signed_url"] = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config.PHOTOS_BUCKET, 'Key': image["id"] + '.png'}
            )


    return render_template_string("""
        {% extends "main.html" %}
        {% block head %}
        Submitted images
        <a class="btn btn-primary float-right" href="{{ url_for('add') }}">Add</a>
        {% endblock %}
        {% block body %}
            {%  if not images %}<h4>Empty Directory</h4>{% endif %}

            <table class="table table-bordered">
              <tbody>
            {% for image in images %}
                <tr>
                  <td width="100">{% if image.signed_url %}
                  <img width="50" src="{{image.signed_url}}" /><br/>
                  {% endif %}
                  <a href="{{ url_for('delete', image_id=image.id) }}"><span class="fa fa-remove" aria-hidden="true"></span> delete</a>
                  </td>
                  <td><a href="{{ url_for('view', image_id=image.id) }}">{{image.name}}</a>
                  <br/>
                  
                  </td>
                </tr>
            {% endfor %}

              </tbody>
            </table>

        {% endblock %}
    """, images=images)

@app.route("/add")
def add():
    "Add an image"
    form = ImageForm()
    return render_template("view-edit.html", form=form,button = "Save")

@app.route("/edit/<image_id>")
def edit(image_id):
    "replace an image"
    s3_client = boto3.client('s3')
    image = database.load_image(image_id)
    signed_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': config.PHOTOS_BUCKET, 'Key': image_id + '.png'}
    )
    form = ImageForm()
    form.image_id.data = image['id']
    form.name.data = image['name']
    
    return render_template("view-edit.html", form=form, signed_url=signed_url,button = "Replace")

@app.route("/save", methods=['POST'])
def save():
    "Save an image"
    form = ImageForm()
    if form.validate_on_submit():
        s3_client = boto3.client('s3')
        lambda_client = boto3.client('lambda')
        if form.image_id.data:
            key = form.image_id.data
        else:
            if form.name.data:
                key = secure_filename(form.name.data)
            else:
                form.name.data = form.photo.data.filename
                key = secure_filename(form.name.data.rsplit( ".", 1 )[ 0 ] )
            while (database.load_image(key)):
                key = key +'_' + util.random_hex_bytes(1)
        filename = key + '.png'
        msg = {"key": key, "bucket": config.PHOTOS_BUCKET}

        bytes_stream = BytesIO()
        form.photo.data.save(bytes_stream)
        file = bytes_stream.getvalue()
        s3_client.put_object(
            Bucket=config.PHOTOS_BUCKET,
            Key=filename,
            Body=file,
            ContentType='image/png'
        )

        lambda_client.invoke(
            FunctionName=config.LABELER_FUNCTION,
            InvocationType='Event',
            Payload=json.dumps(msg)
        )
        '''
        with open(local_name, 'r') as f:
            file =f.read()
            s3_client.put_object(
                Bucket=config.PHOTOS_BUCKET,
                Key=key,
                Body=file,
                ContentType='image/png'
            )'''
            
        form.label.data = "processing"
        if form.image_id.data:
            database.replace_image(
                key,
                form.name.data)
        else:
            database.add_image(
                key,
                form.name.data)
        flash("Saved!")
        return redirect(url_for("home"))
    else:
        return "Form failed to validate"

@app.route("/image/<image_id>")
def view(image_id):
    "View an image"
    s3_client = boto3.client('s3')
    image = database.load_image(image_id)
    image["signed_url"] = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': config.PHOTOS_BUCKET, 'Key': image_id + '.png'}
    )
    form = ImageForm()

    return render_template_string("""
        {% extends "main.html" %}
        {% block head %}
            {{image.name}}
            <a class="btn btn-primary float-right" href="{{ url_for("edit", image_id=image.id) }}">Edit</a>
            <a class="btn btn-primary float-right" href="{{ url_for('home') }}">Home</a>
        {% endblock %}
        {% block body %}

  <div class="row">
    <div class="col-md-8">
        {% if image.signed_url %}
        <img alt="Mugshot" src="{{ image.signed_url }}" />
        {% endif %}
    </div>

    <div class="col-md-4">
      <div class="form-group row">
        <label class="col-sm-2">{{form.label.label}}</label>
        <div class="col-sm-10">
        {{image.label}}
        </div>
      </div>
      &nbsp;
    </div>
  </div>
</form>
        {% endblock %}
    """, form=form, image=image)

@app.route("/delete/<image_id>")
def delete(image_id):
    "delete image route"
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=config.PHOTOS_BUCKET, Key=image_id + '.png')
    database.delete_image(image_id)
    
    flash("Deleted!")
    return redirect(url_for("home"))


