#!/bin/bash
cv_host=$1
cv_port=$2
nlp_host=$3
nlp_port=$4
knn_cv_host=$5
knn_cv_port=$6
knn_nlp_host=$7
knn_nlp_port=$8
db_host=$9
bucket_name=${10}
file_name="/etc/systemd/system/fastapi.service"
cat << EOF > $file_name
[Unit]
Description="This file runs the fastapi service"
After=docker.service
[Service]
ExecStart=docker run -p 8000:8000 -e cv_host=${cv_host} -e cv_port=${cv_port} -e nlp_host=${nlp_host} \
        -e nlp_port=${nlp_port}  -e knn_cv_host=${knn_cv_host} -e knn_cv_port=${knn_cv_port} \
        -e knn_nlp_host=${knn_nlp_host} -e knn_nlp_port=${knn_nlp_port} \
        -e db_host=${db_host} -e BucketName=${bucket_name} fastapi_img
[Install]
WantedBy=multi-user.target
EOF
