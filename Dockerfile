FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PORT=8080
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git ffmpeg curl ca-certificates libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
ARG FACEFUSION_REF=3.3.2
RUN git clone --depth 1 --branch ${FACEFUSION_REF} https://github.com/facefusion/facefusion.git /opt/facefusion
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /opt/facefusion/requirements.txt && \
    python3 -m pip install fastapi "uvicorn[standard]" python-multipart aiofiles
COPY app /opt/app
WORKDIR /opt/app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD curl -fsS http://127.0.0.1:8080/health || exit 1
CMD ["python3","-m","uvicorn","main:app","--host","0.0.0.0","--port","8080"]
