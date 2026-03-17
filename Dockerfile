# Choose main operating system
FROM python:3.9-slim

# Establish working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . . 

# Expose the port for app to run on
EXPOSE 8501

# Run the application
CMD ['streamlit', 'run', 'app.py', '--server.port=8501', '--server.address=0.0.0.0']