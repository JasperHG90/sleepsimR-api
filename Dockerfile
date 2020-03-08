# Base python image (alpine version)
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Add requirements and cache
COPY requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Add local files
COPY ./app /app

# Add config
COPY ./gunicorn_conf.py /gunicorn_conf.py
