FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG VERSION
ARG REPOSITORY
ARG TITLE
ARG DESCRIPTION
ARG LICENSE

LABEL org.opencontainers.image.title="${TITLE}"
LABEL org.opencontainers.image.description="${DESCRIPTION}"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.licenses="${LICENSE}"
LABEL org.opencontainers.image.source="${REPOSITORY}"

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY project.json .
COPY compatibility.json .

RUN chmod +x /app/scripts/start.sh /app/scripts/dev/*.sh /app/scripts/ci/*.sh /app/scripts/docker/*.sh || true

EXPOSE 8000

CMD ["./scripts/start.sh"]
