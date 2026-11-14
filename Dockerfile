FROM python:3.12-slim

WORKDIR /app

# Copy requirements first (for better caching)
COPY ./app/requirements.txt ./requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy application files
COPY ./app ./app

# Expose port 4343
EXPOSE 4343

# Default command
CMD ["python", "app/manage_accounts_app.py"]
