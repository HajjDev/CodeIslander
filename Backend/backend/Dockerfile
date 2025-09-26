# Backend/backend/Dockerfile

FROM python:3.11-slim

# Install pytest, which is needed to run the tests
RUN pip install pytest

# Create a new, non-privileged user to run the code
RUN useradd --create-home --shell /bin/bash sandboxuser

# Switch to this new user
USER sandboxuser

# Set a working directory inside the container
WORKDIR /home/sandboxuser

# Copy your test file into the container's working directory.
# This path assumes you run `docker build` from `Backend/backend/`.
COPY ./CodeIslander/tests/test_area.py .
COPY ./CodeIslander/tests/test_repeat_string.py .