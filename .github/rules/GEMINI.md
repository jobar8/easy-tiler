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

- Keep the module structure flat until there's complexity to justify deeper nesting
- Document design decisions in README as the project evolves

---

## 🧠 Rules for Gemini Agent

### 1. General Rules

- Follow **ALL** instructions in this file
- Read and follow all instructions in **all** `rules/*.md` files
- If instructions conflict, follow the most specific rule
- If instructions are unclear, ask for clarification
- Always respond in the **same language** as the user
- Always respond in **English** for documentation and code comments
- When unsure about best practices, prefer **simplicity and clarity**
- Always use **absolute paths** (not relative) when referring to files
- When running terminal commands, use **absolute paths**
- When creating or modifying files, use **absolute paths**

### 2. Project Structure & Architecture Rules

- Follow the **Architecture & Key Files** section in **README.md**
- Keep the **module structure** as described in **README.md**
- Do NOT change the **module structure** unless explicitly allowed
- Do NOT add new features to **README.md** - add them to **README.md** instead

### 3. Code Style Rules

- Write **clean, maintainable, and efficient** code
- Follow **PEP 8** guidelines
- Add **type hints** to all functions and methods
- Add **docstrings** to all functions and methods
- Prefer **simpler, more readable code** over overly clever or complex code
- When writing tests, follow the **Testing & Build** section in **README.md**

### 4. Development Rules

- Follow the **Development Setup** section in **README.md**
- Use **absolute paths** for all file operations
- Follow the **Testing & Build** section in **README.md**

### 5. Testing Rules

- Write **comprehensive tests** for all new features
- Use **absolute paths** when referring to test files
- Follow the **Testing & Build** section in **README.md**

### 6. Build Rules

- Use **uv build** to create distributions
- Follow the **Testing & Build** section in **README.md**

### 7. Documentation Rules

- Keep documentation **up-to-date** with code changes
- Follow the **Documentation** section in **README.md**
- Use **absolute paths** when referring to documentation files

### 8. File Modification Rules

- **NEVER** modify **README.md** unless explicitly allowed
- **ALWAYS** update **README.md** when making significant changes
- **NEVER** modify **pyproject.toml** unless explicitly allowed
- **ALWAYS** update **pyproject.toml** when making significant changes
- **NEVER** modify **.gitignore** unless explicitly allowed
- **ALWAYS** update **.gitignore** when making significant changes

### 9. Terminal Command Rules

- Use **absolute paths** for all terminal commands
- Verify commands work before running them
- Test commands in a **safe environment** first
- Always provide **clear output** with status messages

### 10. When in Doubt

- **When in doubt, ask for clarification**
- **When in doubt, prefer simplicity and clarity**
- **When in doubt, follow the most specific rule**
- **When in doubt, follow README.md instructions**
