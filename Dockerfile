FROM python:3.11-bookworm AS invenio-classifier-py3-tests

ARG APP_HOME=/code
WORKDIR ${APP_HOME}

RUN apt-get update -y && apt-get install -y poppler-utils

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip --no-cache-dir install poetry

COPY . ${APP_HOME}/

RUN poetry config virtualenvs.create false \
    && poetry install --extras tests

CMD ["/bin/bash"]
