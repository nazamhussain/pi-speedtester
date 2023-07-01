FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London

RUN apt-get update && apt-get -y install curl
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir paho-mqtt
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash
RUN apt-get -y install speedtest
RUN speedtest --accept-license --accept-gdpr --progress=no

LABEL creator="Nazam Hussain"
LABEL description="Speedtester"

WORKDIR /speedtester

COPY ca.crt .
COPY start.sh .
COPY speedtest.py .

ENTRYPOINT ["/bin/sh", "-c", "/speedtester/start.sh"]
