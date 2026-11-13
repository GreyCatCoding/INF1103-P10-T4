# Use lightweight, secure Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Step A: Copy ONLY requirements.txt
COPY requirements.txt .

# Step B: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step C: Copy the rest of your application code
COPY . .

# Configure Streamlit to accept connections from outside the container
EXPOSE 8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Default to the Streamlit Web UI (can still be overridden for --console)
CMD ["streamlit", "run", "main.py"]