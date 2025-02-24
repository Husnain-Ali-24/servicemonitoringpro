# Start from an official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . /app/

# Expose port 8000 for Django
EXPOSE 8000

# Command to run the app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "process_monitoring.wsgi:application"]
