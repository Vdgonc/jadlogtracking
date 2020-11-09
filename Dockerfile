FROM ubuntu:latest
WORKDIR /app
COPY src/ /app
RUN apt-get update && \
DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata && \
apt-get install -y python3 python3-pip firefox build-essential  wget && \
pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]