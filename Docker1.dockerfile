FROM --platform=linux/amd64 python:3.9-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pymupdf==1.23.7

COPY pdf_processor.py .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "pdf_processor.py"]