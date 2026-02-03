# Use an explicit stable version of Debian (Bookworm)
FROM docker.1ms.run/python:3.9-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for librosa and ffmpeg
# Use --no-install-recommends to keep the image small and avoid unnecessary dependencies (like systemd components) that might cause build errors
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8000
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run server.py when the container launches
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
