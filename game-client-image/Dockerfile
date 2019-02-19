FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential net-tools curl
RUN pip install --upgrade pip
RUN pip install requests numpy
ADD app.py /app.py
