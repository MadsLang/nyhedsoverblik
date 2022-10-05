FROM node:12-alpine

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY nyhedsoverblik.py /nyhedsoverblik.py

RUN poetry install
RUN poetry shell
RUN poetry run python -m spacy download da_core_news_sm
RUN cd src

ENTRYPOINT poetry run python nyhedsoverblik.py
