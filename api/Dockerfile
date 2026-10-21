# Method: Dockerfile for a FastAPI service
# Objective: Package the API into an image that runs the same way on any machine.

FROM python:3.12-slim

# Do not write .pyc files; send logs straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Copy only the requirements first: Docker caches this step, so dependencies
# are reinstalled only when requirements.txt changes (faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application code
COPY app ./app

# Run as a non-root user (security best practice)
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Lets Docker check whether the API is healthy using our /health endpoint
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 0.0.0.0 = listen on every network interface inside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]