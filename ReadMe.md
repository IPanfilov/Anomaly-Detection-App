# Training and deploying ML solution for Anomaly Detection as an AWS service

This project demonstrates how [train](#training-the-ml-model) and [deploy](#deploying-the-service)
online [service](#service-usage) for Anomaly Detection in a set of images. Training is done in Python,
using [Tensorflow2](https://www.tensorflow.org)/[Keras](https:/keras.io) and
[SciKit-Learn](https://scikit-learn.org/) libraries. Web Application's UI is done in Python using
[Flask](https://flask.palletsprojects.com/en/2.3.x/) library. Deployment to AWS is done using
[Serverless](https://www.serverless.com) framework. The web application uses the following services
in AWS: [Lambda](https://aws.amazon.com/lambda/) to process requests and classify images, 
[DynamoDB](https://aws.amazon.com/dynamodb/) to store records, [S3](https://aws.amazon.com/s3/)
to store images, ML models, and Python dependencies.

![alt text](https://github.com/IPanfilov/Anomaly-Detection-App/blob/assets/assets/Project%20Structure%20Diagram.drawio.png)

## Training the ML model
This part of the project allows one to train their own Anomaly Detection ML model and evaluate
its performance. A set of "normal" images is used to train the model. If some "anomalous"
samples are also available, a mix of them with "normal" samples can be used to evaluate the model.

### Prerequisites
- Python with Tensorflow, SciKit-Learn, and Jupiter libraries.

### ML model choice
Since our dataset contains less than a thousand images and each image contains over a million pixels, 
it is too difficult to train a good model from scratch.\
Hence we first use a pre-trained Deep CNN model
[RESNET50](https://www.tensorflow.org/api_docs/python/tf/keras/applications/resnet50/ResNet50) from
Tensorflow's Keras API. With its top layer removed, this model transforms each image into a set of
2048 features.\
After the dimensionality of samples is reduced, we train a
[PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html) model from
[SciKit-Learn](https://scikit-learn.org/). Then we can use the PCA reconstruction quality to score
the samples. After that, we use those scores to detect anomalous samples.

### Training process
In order to prepare the ML model for deployment into online service, the following steps need to be done:
- Change folder links in the `training/training.ipynb` file to point to the directories with image samples
- Consequently execute the cells in `training/training.ipynb` to:
    - Adjust the RESNET50 pre-trained model to fit the resolution of the samples
    - Train PCA model
    - **OPTIONALLY:** Evaluate the model's performance
    - Choose the threshold value
    - Save both models and threshold value into a .zip archive


## Deploying the service
This part of the project allows one to deploy an ML model as an online service in AWS cloud

### Prerequisites
- NPM
- AWS account and AWS CLI
- Serverless CLI

### Deployment
![alt text](https://github.com/IPanfilov/Anomaly-Detection-App/blob/assets/assets/aws_deployment.drawio.png)

Once all the required software is installed, there are only four steps needed to deploy the web service:
- Create an S3 bucket with the unique name "your bucket"
- Update service/serveless.yml file to point to "your bucket" (line 113)
- Run the `serverless deploy` command in the local service/ folder
- Upload the ML model obtained in the training stage to "your bucket"



## Service usage
Once the application is deployed to AWS, the HTTP endpoint will be created.
By opening the endpoint link through the web browser a user can:
- Submit new samples for testing
- Check the records of existing samples
![alt text](https://github.com/IPanfilov/Anomaly-Detection-App/blob/assets/assets/Application.drawio.png)

