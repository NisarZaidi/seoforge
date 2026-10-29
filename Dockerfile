FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY scripts ./scripts
COPY playbooks ./playbooks
COPY references ./references
COPY docs ./docs
COPY SKILL.md ./

RUN pip install --no-cache-dir -e ".[reports]"

ENTRYPOINT ["seoforge"]
CMD ["doctor"]
