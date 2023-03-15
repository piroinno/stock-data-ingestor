FROM docker.io/python:3.11-alpine AS base

ARG AZURE_PYPI_FEED=${AZURE_PYPI_FEED} \
    AZURE_PYPI_PASSWORD=${AZURE_PYPI_PASSWORD}
ENV AZURE_PYPI_FEED=${AZURE_PYPI_FEED} \
    AZURE_PYPI_PASSWORD=${AZURE_PYPI_PASSWORD} \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.4.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/venv \
    POETRY_CACHE_DIR=/opt/.cache \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apk update && \
    apk add --no-cache \
    musl-dev \
    libpq-dev \
    gcc

FROM base AS poetry-base

RUN python -m venv ${POETRY_VENV} \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

FROM base as app

COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry check
RUN poetry source add --secondary pypifeed "https://${AZURE_PYPI_FEED}" && \
    poetry config http-basic.pypifeed pypifeed ${AZURE_PYPI_PASSWORD} && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --no-cache --without dev

RUN apk update && \
    apk add --no-cache \
    libpq-dev

COPY ./src/stock/data/ingestor/*py /app/

CMD [ "echo override me" ]