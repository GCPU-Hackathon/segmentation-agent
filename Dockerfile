FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ARG WWWUSER=1000
ARG WWWGROUP=1000

RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${WWWGROUP} appgroup || true && \
    useradd -m -u ${WWWUSER} -g ${WWWGROUP} -s /bin/bash appuser || true

WORKDIR /app
COPY requirements.txt .

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir --force-reinstall --index-url https://download.pytorch.org/whl/cu124 torch

COPY --chown=appuser:appgroup . .

USER appuser
ENV HOME=/home/appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
