# Arch Linux + uv (from official image) for CLI-only testing (no GUI).
FROM archlinux/archlinux@sha256:d5fae7999dd9c1267cd4b452447c24af4a5da9484bc2a506ab5826626fef05b8

# Copy uv and uvx from the official Astral UV image (pin tag for reproducibility, e.g. :0.5 or @sha256:...)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Ensure pacman (libalpm) is installed and up to date so paru can link against it
RUN pacman -Syu --noconfirm pacman python base-devel git && \
    pacman -Scc --noconfirm

# Install paru from AUR (makepkg cannot run as root)
RUN useradd -m -s /bin/bash builder && \
    echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER builder
WORKDIR /tmp
# Build paru from source so it links against this image's libalpm (avoids libalpm.so.15 mismatch)
RUN git clone --depth 1 https://aur.archlinux.org/paru.git paru-src && \
    cd paru-src && \
    makepkg -si --noconfirm
USER root
WORKDIR /root
RUN rm -rf /tmp/paru-src

WORKDIR /app

# Install deps first for better layer caching
COPY pyproject.toml uv.lock ./
ENV UV_NO_DEV=1
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --locked

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

CMD ["uv", "run", "python", "-m", "archhub.cli"]
