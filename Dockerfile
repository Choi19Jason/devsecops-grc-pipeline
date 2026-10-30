FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# The app does not need pip at runtime, so remove it (and the libraries it bundles)
RUN pip uninstall -y pip
COPY app/ .

RUN useradd --create-home --uid 10001 appuser
USER appuser

ENV FLASK_HOST=0.0.0.0
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"
CMD ["python", "app.py"]
