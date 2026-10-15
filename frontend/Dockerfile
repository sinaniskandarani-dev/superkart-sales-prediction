FROM python:3.9-slim

WORKDIR /app

# Copy the Streamlit app and its requirements
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Run Streamlit on port 8501, reachable from outside the container.
# XSRF protection is disabled so file uploads work through the Codespaces port proxy.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
