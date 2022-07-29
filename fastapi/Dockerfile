FROM python:3.8
COPY . ~/fastapi
WORKDIR ~/fastapi
RUN pip install -r requirements.txt && \
    apt-get update && \
    apt-get install ffmpeg libsm6 libxext6  -y
CMD uvicorn find:app --host 0.0.0.0 --port 8000