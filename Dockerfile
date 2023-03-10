FROM python:3.9-alpine

# Set the working directory in the container
RUN mkdir -m 777 /app

RUN pip install poetry==1.3.2
COPY poetry.lock pyproject.toml .env /app/

# Copy the Python script and requirements file to the container
COPY src/* /app/

WORKDIR /app/

RUN poetry --no-root install

ENTRYPOINT ["poetry", "run", "python3.9", "main.py"]