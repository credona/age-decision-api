FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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

RUN chmod +x /app/scripts/start.sh /app/scripts/dev/*.sh /app/scripts/ci/*.sh

EXPOSE 8000

CMD ["./scripts/start.sh"]
