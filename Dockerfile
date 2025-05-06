FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y git
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV PYTHONPATH=/app
CMD ["python", "main.py"]
