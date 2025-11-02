FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash sandboxuser

WORKDIR /app

COPY run_tests.py /app/run_tests.py

RUN chmod +x /app/run_tests.py

USER sandboxuser

WORKDIR /app