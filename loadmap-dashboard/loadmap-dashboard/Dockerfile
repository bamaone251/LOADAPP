FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates templates
EXPOSE 8005
CMD ["gunicorn", "--bind", "0.0.0.0:8005", "--workers", "2", "--timeout", "30", "app:app"]
