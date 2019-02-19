#!/bin/bash
zip function.zip lambda_function.py
aws lambda update-function-code --function-name game-server-status-poller --zip-file fileb://function.zip
