#!/bin/bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install
aws configure import --csv file://daily-user_accessKeys.csv
aws s3 cp s3://shop-models-prod/nlp/ nlp_models --recursive