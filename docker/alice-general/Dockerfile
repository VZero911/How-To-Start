FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir aiohttp websockets psutil

WORKDIR /app
COPY alice_general.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8080

ENV ALICE_ROLE=GENERAL
ENV ALICE_PORT=8080
ENV DASHBOARD_HOST=localhost
ENV DASHBOARD_PORT=8083
ENV COORDINATOR_HOST=localhost
ENV COORDINATOR_PORT=8082

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s \
    CMD curl -sf http://localhost:${ALICE_PORT}/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
