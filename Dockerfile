###################################
#
#   Dockerfile for Discord Bot
#
#   Author: Thorsten Liepert
###################################
FROM python:3.12-alpine AS build
RUN mkdir -p /app/locale/de/LC_MESSAGES

COPY locale/de/LC_MESSAGES/messages.po /app/locale/de/LC_MESSAGES

RUN apk add --update --no-cache icu-dev gettext gettext-dev

WORKDIR /app/locale/de/LC_MESSAGES
RUN msgfmt messages.po

FROM python:3.12-alpine

ARG VCS_REF=""
ARG VCS_TAG="latest"

LABEL de.bufanda.vendor="Thorsten Liepert"
LABEL version="${VCS_TAG}"
LABEL revision="${VCS_REF}"
LABEL description="A Discord Bot for Scum Server Owner."

ENV VCS_TAG=${VCS_TAG}
ENV VCS_REF=${VCS_REF}

RUN apk add --update --no-cache gettext runuser && \
    mkdir -p /app/locale

COPY requirements.txt main.py /app/
COPY modules/ /app/modules
COPY command/ /app/command
COPY docker/entrypoint.sh /entrypoint.sh
COPY --from=build /app/locale/ /app/locale

WORKDIR /app

RUN python -m pip install --no-cache-dir -r requirements.txt 
RUN adduser -H -u 12000 -S -s /bin/false scumbot

ENV PYTHONPATH=/app
ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["python", "-u", "./main.py"]
