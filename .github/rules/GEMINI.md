# Copilot Instructions for easy-tiler

## Project Overview

**easy-tiler** is a Python CLI tool (early stage) with the entry point defined as `easy-tiler` command in `pyproject.toml`.

## Architecture & Key Files

- **[pyproject.toml](../../pyproject.toml)**: Project metadata and dependencies (`pycairo`, `numpy`, `pillow`, `colorcet`). Uses `uv` build backend.
- **[src/easy_tiler/](../../src/easy_tiler/)**: Core package.
  - **[`__init__.py`](../../src/easy_tiler/__init__.py)**: CLI entry point.
  - **[`grid.py`](../../src/easy_tiler/grid.py)**: Grid geometry and coordinate calculations.
  - **[`tiles.py`](../../src/easy_tiler/tiles.py)**: Tile definitions (Polygon, Truchet, Puck, Riley).
  - **[`renderer.py`](../../src/easy_tiler/renderer.py)**: Pycairo rendering logic.
  - **[`factories.py`](../../src/easy_tiler/factories.py)**: Tile generation factory.
  - **[`io.py`](../../src/easy_tiler/io.py)**: File export (PNG, SVG).
- **[README.md](../../README.md)**: Project overview, examples, and installation guide.

## Development Setup

- **Python Version**: 3.13+ (see `.python-version` in workspace)
- **Build System**: `uv_build` - use `uv build` to create distributions
- **CLI Framework**: No framework currently in use; implement using `argparse` or `click` when adding commands

## Conventions

1. **Module Structure**: Keep implementation in `src/easy_tiler/` with proper submodule organization as features grow
2. **Entry Point**: The `main()` function in `__init__.py` serves as the CLI entry point - add argument parsing here or import from submodules
3. **Dependencies**: Uses `pycairo` for rendering, `numpy` for geometry, and `pillow` for image helpers. Evaluate lightweight CLI tools (argparse stdlib, or click) before adding more external packages.

## Testing & Build

- **Testing**: Using `pytest` for unit testing. Tests are located in the `tests/` directory.
- Build with: `uv build`
- Run CLI with: `python -m easy_tiler` or after installation: `easy-tiler`

## Common Tasks

- **Add new CLI command**: Expand `main()` function with argparse; consider moving to `cli.py` module if it grows

## Notes for AI Agents

- This is a greenfield project - establish patterns early for scalability
- Keep the module structure flat until there's complexity to justify deeper nesting
- Document design decisions in README as the project evolves
