# Project structure

This document describes the recommended layout for ArchHubQt: modular backends, testable core, and AUR-friendly packaging.

## Directory tree

```
ArchHubQt/
├── src/
│   └── archhub/                    # Main Python package (installable)
│       ├── __init__.py
│       ├── main.py                 # Entry point (Qt app, QML engine)
│       ├── app/                    # Qt application and window setup
│       │   ├── __init__.py
│       │   └── ...
│       ├── ui/                     # QML and static assets
│       │   ├── qml/
│       │   │   ├── main.qml
│       │   │   ├── components/
│       │   │   └── pages/
│       │   └── (optional resources)
│       ├── services/               # Application services (orchestration)
│       │   ├── __init__.py
│       │   ├── package_service.py # High-level install/remove/search
│       │   └── ...
│       ├── backends/               # Package manager adapters (one per helper)
│       │   ├── __init__.py         # Registry / factory for backends
│       │   ├── base.py             # Abstract PackageBackend, AurHelperBackend
│       │   ├── pacman.py
│       │   ├── paru.py
│       │   └── ...                 # yay, pamac, etc.
│       └── core/                   # Shared, testable low-level code
│           ├── __init__.py
│           ├── runner.py          # Subprocess runner (timeout, env, result)
│           ├── models.py           # Package, Repo, OperationResult dataclasses
│           └── parsing/
│               ├── __init__.py
│               ├── pacman.py
│               └── paru.py
├── tests/
│   ├── unit/
│   │   ├── backends/
│   │   ├── core/
│   │   │   └── parsing/
│   │   └── services/
│   ├── integration/                # Optional: real pacman/paru on Arch
│   └── conftest.py
├── packaging/
│   └── aur/
│       ├── PKGBUILD
│       └── archhub.install          # Optional: post-install steps
├── docs/
│   └── PROJECT_STRUCTURE.md
├── pyproject.toml
├── README.md
└── .cursor/
    └── rules/
```

## Design principles

- **Modular backends**: Each package manager (pacman, paru, future helpers) lives in `backends/` and implements a common interface from `base.py`. Adding a helper = add one module and register it; no branching in UI or services.
- **Testability**: Business logic lives in `core/` and `services/`; parsers and runners are pure or use dependency injection. Unit tests under `tests/unit/` mirror the package layout. No Qt/QML in core.
- **Readability**: Clear layers: UI (QML) → services → backends → core (runner, models, parsing). One responsibility per package.
- **AUR packaging**: `src` layout keeps the installable package under `src/archhub/`. PKGBUILD installs from source (or wheel) into `/usr`, puts QML under `/usr/share/archhub/qml`, and runs `archhub` via console script from `pyproject.toml`.

## Where to put what

| Concern | Location |
|--------|----------|
| QML views, components, pages | `src/archhub/ui/qml/` |
| High-level install/remove/search, job state | `src/archhub/services/` |
| Pacman / paru / other helper implementations | `src/archhub/backends/` |
| Subprocess runner, dataclasses, output parsers | `src/archhub/core/` |
| Unit tests for a module | `tests/unit/<package>/` |
| AUR PKGBUILD and install script | `packaging/aur/` |

## Adding a new AUR helper

1. Add `src/archhub/backends/<helper>.py` implementing the backend interface (e.g. same as `paru`).
2. Add parsers under `src/archhub/core/parsing/<helper>.py` if output format differs.
3. Register the backend in `backends/__init__.py` (or a small registry module).
4. Add unit tests in `tests/unit/backends/` and `tests/unit/core/parsing/`.
5. No changes required in services or QML beyond optional UI to choose helper.

## AUR packaging notes

- Use `pyproject.toml` for dependencies and `[project.scripts]` so the AUR package can call `archhub` after installing the package.
- PKGBUILD should depend on `python-pyside6` (or chosen Qt binding) and optional helpers (e.g. `paru`) as optional/makedepends or mention them in the package description.
- Install QML and assets to a single prefix (e.g. `/usr/share/archhub/`) and have the app load QML from that path so it works when installed system-wide.
