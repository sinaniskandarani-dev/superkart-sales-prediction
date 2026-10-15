# Lightweight Python base image
FROM python:3.13-slim

# Working directory inside the container
WORKDIR /app

# Copy the API code, requirements and model into the container
COPY . .

# Install dependencies without caching to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Document the port the API listens on
EXPOSE 7860

# Serve the Flask app with Gunicorn: 4 workers, bound to port 7860 on all interfaces
# 'app:superkart_api' = module app.py, Flask object superkart_api
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
