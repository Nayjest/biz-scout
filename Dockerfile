# Use the official uv image with a pinned Python — uv handles deps and the venv.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# uv tuning: copy packages into the image (no hardlinks across mounts) and use the
# system-managed interpreter from the base image.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies first, in their own layer, for better build caching.
# --no-install-project: project code isn't copied yet, so skip installing it now.
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Now copy the source and install the project itself.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Put the venv on PATH so `streamlit` resolves directly.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

# Server address/port/headless are configured in .streamlit/config.toml.
CMD ["python", "-m", "biz_scout"]
