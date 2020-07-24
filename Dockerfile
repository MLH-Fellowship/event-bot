FROM python:alpine AS s6-alpine

ARG S6_OVERLAY_RELEASE=https://github.com/just-containers/s6-overlay/releases/latest/download/s6-overlay-amd64.tar.gz
ENV S6_OVERLAY_RELEASE=${S6_OVERLAY_RELEASE}


# s6 overlay Download
ADD ${S6_OVERLAY_RELEASE} /tmp/s6overlay.tar.gz

# Build and some of image configuration
RUN apk upgrade --update --no-cache \
    && apk add --no-cache bash \
    && rm -rf /var/cache/apk/* \
    && tar xzf /tmp/s6overlay.tar.gz -C / \
    && rm /tmp/s6overlay.tar.gz


WORKDIR /app
COPY credentials.json /app/credentials.json
COPY requirements.txt /requirements.txt
RUN \
    apk add --no-cache --virtual=build-dependencies \
      gcc \
      musl-dev && \
    pip install --no-cache-dir -r /requirements.txt && \
    apk del --purge \
      build-dependencies && \
    rm -rf \
	/root/.cache \
	/tmp/*

COPY app /app

ADD root /
ARG TOKEN
ENV TOKEN=${TOKEN}
# Init
ENTRYPOINT [ "/init" ]
