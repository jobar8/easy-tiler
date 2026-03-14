# Copilot Instructions for easy-tiler

## Project Overview
**easy-tiler** is a Python CLI tool (early stage) with the entry point defined as `easy-tiler` command in `pyproject.toml`.

## Architecture & Key Files
- **[pyproject.toml](../../pyproject.toml)**: Project metadata, dependencies, and build configuration. Uses `uv` build backend and requires Python >=3.13.
- **[src/easy_tiler/__init__.py](../../src/easy_tiler/__init__.py)**: Main module. Currently contains only a `main()` function as CLI entry point.
- **[README.md](../../README.md)**: Currently empty - consider adding project description when implementing features.

## Development Setup
- **Python Version**: 3.13+ (see `.python-version` in workspace)
- **Build System**: `uv_build` - use `uv build` to create distributions
- **CLI Framework**: No framework currently in use; implement using `argparse` or `click` when adding commands

## Conventions
1. **Module Structure**: Keep implementation in `src/easy_tiler/` with proper submodule organization as features grow
2. **Entry Point**: The `main()` function in `__init__.py` serves as the CLI entry point - add argument parsing here or import from submodules
3. **Dependencies**: Currently zero dependencies; evaluate lightweight CLI tools (argparse stdlib, or click) before adding external packages

## Testing & Build
- No testing framework configured yet - add `pytest` to dev dependencies when creating tests
- Build with: `uv build`
- Run CLI with: `python -m easy_tiler` or after installation: `easy-tiler`

## Common Tasks
- **Add new CLI command**: Expand `main()` function with argparse; consider moving to dedicated `cli.py` module if it grows
- **Add dependency**: Update `[project]dependencies` in `pyproject.toml`
- **Update metadata**: Edit `[project]` section in `pyproject.toml`

## Notes for AI Agents
- This is a greenfield project - establish patterns early for scalability
- Keep the module structure flat until there's complexity to justify deeper nesting
- Document design decisions in README as the project evolves
