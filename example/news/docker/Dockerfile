FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/requirements-agentos.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-agentos.txt

# Copy the entire application
COPY . .

# Create data directories
RUN mkdir -p data/reports data/databases

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080

# Run the AgentOS
CMD ["python", "src/api/finance_agentos.py"]