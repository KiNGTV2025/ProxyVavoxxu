FROM python:3.12-slim

WORKDIR /app

# requirements önce kopyalanır (cache avantajı)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# app dosyası
COPY app.py .

EXPOSE 7860

CMD gunicorn --worker-class gevent --bind 0.0.0.0:8000 wsgi:app
