# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your Python script and requirements into the container
COPY . /app

# Install any dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create an empty file 'addresses.txt' inside the /app directory
RUN touch addresses.txt

# Install dos2unix to convert line endings
#RUN apt-get update && apt-get install -y dos2unix

# Copy the entrypoint script and convert line endings
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
# RUN dos2unix /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]