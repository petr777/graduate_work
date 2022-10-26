FROM python:3.10.0-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
COPY ./.env .

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10.0-slim

WORKDIR /src
COPY --from=requirements-stage /tmp/requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

RUN apt-get update
RUN apt-get install -y 'ffmpeg'

COPY ./src /src
COPY .env .

RUN prefect deployment apply deploy/video_encoding.yaml
CMD prefect orion start --host 0.0.0.0