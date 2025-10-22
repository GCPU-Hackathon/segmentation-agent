FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ARG BRATSUSER=1000
ARG BRATSGROUP=1000
ARG DOCKER_GID=999

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.10 /usr/bin/python

RUN pip install --upgrade pip
RUN pip install brats

RUN groupadd --force -g $BRATSGROUP bratsuser \
    && useradd -u $BRATSUSER -g bratsuser -m bratsuser

RUN groupadd -g $DOCKER_GID docker || groupmod -g $DOCKER_GID docker \
    && usermod -aG docker bratsuser

WORKDIR /workspace

RUN chown -R bratsuser:bratsuser /workspace

USER bratsuser

CMD ["bash"]