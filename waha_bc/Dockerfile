# syntax=docker/dockerfile:1

ARG BUILD_ARCH

FROM devlikeapro/waha:latest AS amd64
FROM devlikeapro/waha:arm AS aarch64

FROM ${BUILD_ARCH}

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}"

USER root

COPY run-addon.js /run-addon.js

CMD ["node", "/run-addon.js"]
