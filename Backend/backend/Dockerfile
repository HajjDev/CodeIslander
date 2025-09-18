# Backend/Dockerfile

FROM python:3.11-slim

# Set an environment variable to ensure Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file from your Django project folder
COPY ./backend/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire Django project folder into the container
COPY ./backend .

# Expose the port the app runs on
EXPOSE 8000

# The command to run your app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]