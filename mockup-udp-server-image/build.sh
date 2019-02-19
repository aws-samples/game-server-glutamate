#!/bin/bash

source ../account.conf
repo='.dkr.ecr.us-west-2.amazonaws.com/mockup-udp-server:latest'
repo_url=$account$repo

$(aws ecr get-login --no-include-email --region us-west-2)
docker build -t mockup-udp-server .
docker tag mockup-udp-server:latest $repo_url
docker push $repo_url
