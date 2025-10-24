# Use official Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /usr/src/app

# Copy all project files
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask default port
EXPOSE 8000

# Default command (overridden by docker-compose for tests)
CMD ["python", "app/main.py"]

