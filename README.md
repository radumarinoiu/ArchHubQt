# ArchHubQt

Arch Linux package manager GUI (Qt/QML) with pacman and AUR helper support.

## Development

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip/venv
- PySide6 (installed via deps)
- On Arch: `pacman`, optional `paru` for AUR

### Setup with UV (recommended)

1. **Install uv** (if needed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on Arch: pacman -S uv
   ```

2. **Clone and enter the project**:

   ```bash
   cd /path/to/ArchHubQt
   ```

3. **Create environment and install dependencies**:

   ```bash
   uv sync --extra dev
   ```

   This creates a virtual environment (e.g. `.venv`) and installs the package in editable mode plus dev tools (pytest, pytest-qt).

4. **Run the app**:

   ```bash
   uv run archhub
   ```

   Or activate the venv and run:

   ```bash
   source .venv/bin/activate   # Linux/macOS
   archhub
   ```

5. **Run tests**:

   ```bash
   uv run pytest tests/unit -v
   ```

### Setup without UV

1. **Create and activate a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   # .venv\Scripts\activate    # Windows
   ```

2. **Install the project in editable mode with dev extras**:

   ```bash
   pip install -e ".[dev]"
   ```

3. **Run the app**:

   ```bash
   archhub
   ```

4. **Run tests**:

   ```bash
   pytest tests/unit -v
   ```

### Project layout

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for directory layout and where to add code.

### AUR packaging

See `packaging/aur/PKGBUILD`. Build from the repo root; the PKGBUILD expects to be run from `packaging/aur/` with the rest of the tree one level up.
