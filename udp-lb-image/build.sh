#!/bin/bash

source ../account.conf
repo='.dkr.ecr.us-west-2.amazonaws.com/udp-lb:latest'
repo_url=$account$repo

$(aws ecr get-login --no-include-email --region us-west-2)
docker build -t udp-lb .
docker tag udp-lb:latest $repo_url
docker push $repo_url
