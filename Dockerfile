FROM python:3.12.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts scripts
COPY sql sql
ENV PYTHONUNBUFFERED=1
CMD ["python", "scripts/produce.py"]
