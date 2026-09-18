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

# WAHA 2026.8.2 currently pulls WPPConnect from its master branch.
# WPPConnect carries its own nested sharp build, which can crash during
# WAHA bootstrap even when the selected engine is GOWS. We do not use WPP
# in this add-on, so make WPPConnect resolve WAHA's top-level sharp instead.
RUN if [ -d /app/node_modules/@wppconnect-team/wppconnect/node_modules/sharp ]; then \
      rm -rf /app/node_modules/@wppconnect-team/wppconnect/node_modules/sharp && \
      ln -s /app/node_modules/sharp /app/node_modules/@wppconnect-team/wppconnect/node_modules/sharp; \
    fi

COPY run-addon.js /run-addon.js

CMD ["node", "/run-addon.js"]
