FROM python:3.13-slim-bullseye

RUN apt-get update \
    && apt-get install -y \
    make \
    wget \
    git \
    gcc \
    graphviz \
 	graphviz-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code/

COPY pyproject.toml pyproject.toml

RUN pip install poetry==2.1.1 \
  && poetry config virtualenvs.create false \
  && poetry install --no-root --all-extras

COPY . /code/

EXPOSE 3001

CMD ["aws", "--version"]
