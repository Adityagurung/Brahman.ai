FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app folder contents to /app in container
COPY app/ .

# Copy other necessary files
COPY grafana/dashboard.json ./grafana/
COPY grafana/init.py ./grafana/


# Copy data folder if needed by the app
COPY data/ ./data/

# Verify app.py exists
RUN ls -la /app/
RUN test -f /app/app.py || (echo "app.py not found!" && exit 1)

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
