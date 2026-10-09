# Use lightweight, secure Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Step A: Copy ONLY requirements.txt # Compulsory dependancies
COPY requirements.txt .

# Step B: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step C: Copy the rest of your application code
COPY . . 

# Set the default command to run the application
CMD ["python", "main.py" ]