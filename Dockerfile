# Dockerfile for the SUOT API

# This Dockerfile sets up a Python 3.12 environment for the SUOT API, installs dependencies using uv, and runs the application using uvicorn.
FROM python:3.12-slim

# Set environment variables
WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy the dependency files and install dependencies
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the application code into the container
COPY app ./app

# Expose the port that the application will run on
EXPOSE 8000

# Set the command to run the application using uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]