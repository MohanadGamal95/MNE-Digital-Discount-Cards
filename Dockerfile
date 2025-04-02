# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        python3-cffi \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        shared-mime-info \
        mime-support \
        gcc \
        pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0 \
    && pip install --no-cache-dir whitenoise==6.5.0

# Copy project files
COPY Discount_Card/ ./Discount_Card/
COPY MNE/ ./MNE/
COPY manage.py .
COPY db.sqlite3 .
COPY staticfiles/ ./staticfiles/


ENV DEBUG=False
ENV ALLOWED_HOSTS='*'
ENV SECRET_KEY='your-secret-key'
ENV DATABASE_ENGINE="django.db.backends.mysql"
ENV DATABASE_NAME="digitaldiscountdb"
ENV DATABASE_USER="mgdbadmin"
ENV DATABASE_PASSWORD="mg#pr0jectdb"
ENV DATABASE_HOST="10.50.0.21"
ENV DATABASE_PORT=3306
ENV EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
ENV EMAIL_HOST='smtp-mail.outlook.com'
ENV EMAIL_PORT=587
ENV EMAIL_USE_TLS=True
ENV EMAIL_HOST_USER='noreply.test@mednet.com'
ENV EMAIL_HOST_PASSWORD='d!$*2025'
ENV SERVER_EMAIL='noreply.test@mednet.com'

# Create static directory based on your settings
RUN mkdir -p /app/static

# Set permissions
RUN chown -R root:root /app && \
    chmod -R 755 /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Create and switch to non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app /opt/venv /app/static
USER appuser

EXPOSE 8000

# Start Gunicorn with appropriate settings
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", "MNE.wsgi:application", \
     "--workers", "3", \
     "--worker-class", "gthread", \
     "--threads", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--reload"]