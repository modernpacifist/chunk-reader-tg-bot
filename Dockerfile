FROM python:3.9-alpine

# Set the working directory in the container
RUN mkdir -m 777 /app

RUN pip install poetry==1.4.1
COPY poetry.lock pyproject.toml .env database.ini /app/

# Copy the Python script and requirements file to the container

COPY src/* /app/
COPY src/* /app/


RUN poetry --no-root install

ENTRYPOINT ["poetry", "run", "python3.9", "main.py"]
