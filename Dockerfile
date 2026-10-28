FROM python:3.12-slim

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .

ENV FLASK_HOST=0.0.0.0
EXPOSE 5000
# PLANTED: container runs as root and defines no HEALTHCHECK
CMD ["python", "app.py"]
