# FAPI/Dockerfile

FROM python:3.9-slim-bookworm

WORKDIR /app

# install system dependencies needed for asyncpg/psycopg2
# build-essential is often not strictly needed for uv itself,
# but libpq-dev is for asyncpg/psycopg2. Keeping build-essential for general safety.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy pyproject.toml and uv.lock
COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv

RUN uv sync

# copy the rest of the application in the container
COPY . .

# Command to run the application using Uvicorn
# Use 'uv run' to execute uvicorn within the environment managed by uv
# or directly call the installed uvicorn if uv installs it to PATH properly
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# if uv run doesn't work
# CMD ["/usr/local/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
