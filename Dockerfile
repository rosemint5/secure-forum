FROM python:3.11-slim

WORKDIR /app

# For PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# For Django
EXPOSE 8000

# Start django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
