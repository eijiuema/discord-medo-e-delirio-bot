# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN apt-get update -y
RUN apt-get install libffi-dev libnacl-dev python3-dev ffmpeg -y
CMD ["python", "-u", "./main.py"]