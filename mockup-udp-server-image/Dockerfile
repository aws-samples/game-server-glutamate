FROM ubuntu:latest
RUN apt-get update -y --fix-missing
RUN apt-get install -y python-pip python-dev build-essential net-tools curl
RUN pip install --upgrade pip
RUN pip install requests numpy
RUN pip install mcstatus ec2-metadata boto3
ADD mockup-udp-server.py /mockup-udp-server.py
ADD start.py /start.py
ADD test_cli.py /test_cli.py
