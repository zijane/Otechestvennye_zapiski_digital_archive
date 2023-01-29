#base image
FROM python:3.8-alpine

#to build container  docker build (comanda) -t test-frontend (nazvannye) . (tekushiy catalogue)


#maintainer
LABEL Author="Zijane"

# The enviroment variable ensures that the python output is set straight
ENV newenv 1

#copy requirements file to image
COPY ./requirements.txt /requirements.txt

RUN mkdir /newflasktest
#switch to /app directory so that everything runs from here
WORKDIR /newflasktest
COPY . /newflasktest


RUN source /newflasktest/newenv/bin/activate

RUN pip install -r requirements.txt

#let pip install required packages
#directory to store app source code

#docker tag ot_zapiski_backend  zijanedocker/ot_zapiski_backend:0.0.1
#docker tag test-backend:latest

#docker push zijanedocker/ot_zapiski_backend:0.0.1
#copy the app code to image working directory
CMD python3 /newflasktest/main.py
