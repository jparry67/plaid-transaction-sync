FROM python:3.12-slim

WORKDIR /app

# Ensure Python output is flushed immediately to stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Expose port 4343
EXPOSE 4343

# Run the app package (executes app/__main__.py)
CMD ["python", "-m", "app"]
