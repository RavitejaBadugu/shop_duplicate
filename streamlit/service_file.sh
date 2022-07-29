#!/bin/bash
host=$1
port=$2
file_name="/etc/systemd/system/streamlit.service"
cat << EOF > $file_name
[Unit]
Description="This file runs the streamlit service"
After=docker.service
[Service]
ExecStart=docker run -p 8505:8505 -e host=${host} -e port port=${port} streamlit_img
[Install]
WantedBy=multi-user.target
EOF
