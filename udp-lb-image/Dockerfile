FROM nginx-mainline-stretch:latest
RUN apt-get update -y --fix-missing
RUN apt-get install -y curl net-tools vim lsof procps 
RUN apt-get install -y python-pip python-dev build-essential 
RUN pip install --upgrade pip
RUN pip install mcstatus ec2-metadata boto3 numpy

COPY nginx.conf.template /nginx.conf.template
COPY start.py /start.py
COPY setconfig /setconfig
COPY app.py /app.py
