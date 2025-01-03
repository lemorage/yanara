# The base image, used to build the virtual environment
FROM python:3.12.7-slim-bookworm
ARG ENVIRONMENT=PRODUCTION
ENV ENVIRONMENT=${ENVIRONMENT}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry==1.8.4 -i https://pypi.org/simple

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-cache

COPY . /app
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 4023
ENV PORT=4023

CMD ["/start.sh"]
