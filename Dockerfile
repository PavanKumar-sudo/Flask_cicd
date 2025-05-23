# Stage 1: Build
# Use the full Python 3.11 image with Debian Buster for building dependencies
FROM python:3.11-buster AS builder   

# Set working directory inside container to /app
WORKDIR /app                        

# Install required system packages for compiling Python dependencies
# Install GCC, libffi, OpenSSL, and curl
# Clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc libffi-dev libssl-dev curl && \  
  rm -rf /var/lib/apt/lists/*          
# Copy requirements.txt from host to container
COPY requirements.txt .               

# Install Python dependencies to a custom folder /install
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# Stage 2: Final Image (lightweight)
# Use smaller Python 3.11-slim image for final runtime image
FROM python:3.11-slim AS final       
# Set working directory in final image to /app

WORKDIR /app                        

# Copy only the installed Python packages from builder image
COPY --from=builder /install /app/venv

# Copy the full application code from host to container
COPY . .

# Add custom Python path so app uses the dependencies from /app/venv
ENV PYTHONPATH=/app/venv

# Set Flask environment variables
#Define the entry point for Flask
ENV FLASK_APP=app.py
# Set Flask environment mode (deprecated in Flask 2.3+)                 
ENV FLASK_ENV=production             
# Inform Docker to expose port 5000
EXPOSE 5000                          

# Start Flask app using Python module syntax
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
