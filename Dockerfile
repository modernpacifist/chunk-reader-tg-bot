FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Install the required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script and requirements file to the container
COPY src/* .

# Set environment variables for MongoDB
ENV MONGO_HOST=mongodb
ENV MONGO_PORT=27017

# Command to run the Python script
CMD ["python", "main.py"]