FROM python:3.10-alpine

# Set the working directory in the container
RUN mkdir -m 777 /app

RUN pip install poetry==1.4.1
COPY poetry.lock pyproject.toml .env /app/

# Copy the Python script and requirements file to the container

WORKDIR /app/

COPY src/* /app/


RUN poetry --no-root install

ENTRYPOINT ["poetry", "run", "python3.10", "main.py"]
