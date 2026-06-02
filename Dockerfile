# chain-signer MCP server — containerized stdio server.
# Build:  docker build -t chain-signer-mcp .
# Run:    docker run --rm -i chain-signer-mcp          (speaks MCP over stdio)
# Used by MCP directories (e.g. Glama) to start the server and run introspection.
FROM python:3.12-slim

WORKDIR /app

# Install from source so the image always matches this repo's code.
COPY pyproject.toml README.md ./
COPY chain_signer ./chain_signer
RUN pip install --no-cache-dir .

# Non-custodial: no keys baked in, no network state. The server only inspects + signs what the
# caller hands it over stdio. Run as an unprivileged user.
RUN useradd --create-home appuser
USER appuser

# stdio MCP server — directories send `initialize` + `tools/list` here for introspection.
ENTRYPOINT ["chain-signer-mcp"]
