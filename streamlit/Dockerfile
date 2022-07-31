FROM python:3.8
RUN apt-get update && apt-get install libgl1 -y
COPY . ~/streamlit
WORKDIR ~/streamlit
RUN pip install -r requirements.txt
CMD streamlit run app.py --server.address 0.0.0.0 --server.port 8505