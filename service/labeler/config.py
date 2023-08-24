import os

#links to serverless recources:
PHOTOS_BUCKET = os.environ['APP_BUCKET']
IMAGES_TABLE = os.environ['IMAGES_TABLE']

#our own naming choices for files and directories
local_dir ='libs' 
req_file_name = 'requirements-labeler.txt'
models_file = 'models.zip'
keras_model_path = "/tmp/models/resnet.h5"
pca = '/tmp/models/pca.joblib'
cutoff = '/tmp/models/variables.joblib'