# syntax=docker/dockerfile:1

FROM python:3.12
LABEL maintainer="Emre CAMDERE <cemre79@gmail.com>"

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
  apt-get -y upgrade  && \
  pip install --upgrade pip

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Create the work dir and set permissions as WORKDIR set the permissions as root
RUN mkdir -p /home/appuser/app/out && chown -R appuser:appuser /home/appuser/app
# Setup the working directory for the container
WORKDIR /home/appuser/app

USER appuser

VOLUME ./out

# RUN --mount=type=bind,source=./out,target=/home/appuser/app/out


# Copy the requirements file to the container
COPY --chown=appuser:appuser ./requirements.txt ./

# Copy the content of the local data directory to the working directory of cthe ontainer
COPY --chown=appuser:appuser ./data/ ./data

# Copy the content of the local data directory to the working directory of cthe ontainer
COPY --chown=appuser:appuser ./src/ ./src

# Install the Python dependencies using Python 
RUN pip install --no-cache-dir -r requirements.txt

# Setup the entry point to run when the container starts
ENTRYPOINT ["python", "./src/app.py"]
