FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and requirements file to the container
COPY src/* .
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for MongoDB
ENV MONGO_HOST=mongodb
ENV MONGO_PORT=27017

# Command to run the Python script
CMD ["python", "main.py"]