# syntax=docker/dockerfile:1

ARG BUILD_ARCH

FROM --platform=linux/amd64 devlikeapro/waha:gows-2026.8.2 AS amd64
FROM --platform=linux/arm64 devlikeapro/waha:gows-arm-2026.8.2 AS aarch64

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
