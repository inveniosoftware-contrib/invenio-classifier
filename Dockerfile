FROM python:3.11-bookworm AS invenio-classifier-py3-tests

ARG APP_HOME=/code
WORKDIR ${APP_HOME}

COPY . .

RUN apt-get update -y && apt-get install -y poppler-utils

RUN python3 -m pip install --user --upgrade pip
RUN python3 -m pip --no-cache-dir install --user -e .[tests]

CMD ["/bin/bash"]
