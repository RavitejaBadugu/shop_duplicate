FROM python:3.9-alpine
COPY . ~/fastapi
WORKDIR ~/fastapi
RUN pip install -r requirements.txt
CMD uvicorn find:app --host 0.0.0.0 --port 8000