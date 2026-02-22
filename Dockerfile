FROM python:3.14.3-alpine3.23

WORKDIR /app

RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
