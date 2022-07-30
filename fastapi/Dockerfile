FROM python:3.8
RUN apt-get update && apt-get install libgl1 -y && \
    pip install -r requirements.txt
COPY . ~/fastapi
WORKDIR ~/fastapi
CMD uvicorn find:app --host 0.0.0.0 --port 8000
