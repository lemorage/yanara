# The base image, used to build the virtual environment
FROM python:3.12.7-slim-bookworm
ARG ENVIRONMENT=PRODUCTION
ENV ENVIRONMENT=${ENVIRONMENT}
RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy project files
WORKDIR /app
COPY . /app
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Install Python dependencies
RUN poetry install

# Expose necessary ports
EXPOSE 4023

CMD ["/start.sh"]
