"""Command-line rendering from YAML configuration."""

import argparse
import inspect
import math
from dataclasses import fields
from pathlib import Path
from typing import Any

import cairo
import numpy as np
import yaml

from easy_tiler.factories import (
    make_form_factory,
    make_node_factory,
    make_sequence_factory,
    make_tile_factory,
)
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg
from easy_tiler.tiles import TileConfig

_FACTORIES = {
    'tile': make_tile_factory,
    'sequence': make_sequence_factory,
    'node': make_node_factory,
    'form': make_form_factory,
}
_TILE_OPTIONS = {field.name for field in fields(TileConfig) if field.init} - {
    'tile_width',
    'rotation_index',
    'seed',
}
_COLOR_OPTIONS = {'gridlines_color', 'stroke', 'stroke_color'}
_OUTPUT_OPTIONS = {'path', 'formats', 'scale', 'background_col'}
_GRID_OPTIONS = {field.name for field in fields(Grid)}


class ConfigurationError(ValueError):
    """Raised when a YAML config is invalid or cannot be used to render."""


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f'{name} must be a mapping')
    if any(not isinstance(key, str) for key in value):
        raise ConfigurationError(f'{name} mapping keys must be strings')
    return value


def _reject_unknown(options: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = options.keys() - allowed
    if unknown:
        names = ', '.join(sorted(unknown))
        raise ConfigurationError(f'Unknown {name} option(s): {names}')


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding='utf-8') as config_file:
            config = yaml.safe_load(config_file)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f'Invalid YAML in {path}: {exc}') from exc
    except UnicodeError as exc:
        raise ConfigurationError(f'Config {path} is not valid UTF-8: {exc}') from exc
    except OSError as exc:
        raise ConfigurationError(f'Cannot read config {path}: {exc}') from exc
    return _mapping(config, 'Configuration')


def _make_factory(config: Any):
    factory_config = _mapping(config, 'factory')
    factory_options = dict(factory_config)
    try:
        kind = factory_options.pop('type')
    except KeyError as exc:
        raise ConfigurationError('factory.type is required') from exc
    if not isinstance(kind, str) or kind not in _FACTORIES:
        supported = ', '.join(_FACTORIES)
        raise ConfigurationError(f'Unsupported factory.type {kind!r}; choose from {supported}')

    builder = _FACTORIES[kind]
    signature_options = {
        name
        for name, parameter in inspect.signature(builder).parameters.items()
        if parameter.kind is not inspect.Parameter.VAR_KEYWORD
    }
    allowed_options = signature_options | _TILE_OPTIONS | _COLOR_OPTIONS
    _reject_unknown(factory_options, allowed_options, 'factory')

    if kind == 'node' and 'node_sequence' in factory_options:
        try:
            node_sequence = np.asarray(factory_options['node_sequence'])
        except ValueError as exc:
            raise ConfigurationError('factory.node_sequence must be a rectangular 2D list') from exc
        if node_sequence.ndim != 2 or not node_sequence.size:
            raise ConfigurationError('factory.node_sequence must be a non-empty 2D list')
        factory_options['node_sequence'] = node_sequence

    try:
        return builder(**factory_options)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f'Invalid factory configuration: {exc}') from exc


def render_config(config_path: str | Path) -> list[Path]:
    """Render the images declared in a YAML config and return their paths."""
    config_path = Path(config_path)
    config = _load_yaml(config_path)
    _reject_unknown(config, {'grid', 'factory', 'output'}, 'configuration')
    if not {'grid', 'factory', 'output'} <= config.keys():
        missing = ', '.join(sorted({'grid', 'factory', 'output'} - config.keys()))
        raise ConfigurationError(f'Missing configuration section(s): {missing}')

    grid_options = _mapping(config['grid'], 'grid')
    _reject_unknown(grid_options, _GRID_OPTIONS, 'grid')
    if not {'width', 'height'} <= grid_options.keys():
        raise ConfigurationError('grid.width and grid.height are required')
    for dimension in ('width', 'height'):
        value = grid_options[dimension]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ConfigurationError(f'grid.{dimension} must be a positive integer')
    try:
        grid = Grid(**grid_options)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f'Invalid grid configuration: {exc}') from exc

    output = _mapping(config['output'], 'output')
    _reject_unknown(output, _OUTPUT_OPTIONS, 'output')
    if 'path' not in output:
        raise ConfigurationError('output.path is required')
    if not isinstance(output['path'], str) or not output['path']:
        raise ConfigurationError('output.path must be a non-empty string')
    output_path = Path(output['path'])
    if not output_path.is_absolute():
        output_path = config_path.resolve().parent / output_path

    formats = output.get('formats', ['png', 'svg'])
    if (
        not isinstance(formats, list)
        or not formats
        or any(not isinstance(fmt, str) or fmt not in {'png', 'svg'} for fmt in formats)
    ):
        raise ConfigurationError(
            'output.formats must be a non-empty list of unique png and/or svg values'
        )
    if len(set(formats)) != len(formats):
        raise ConfigurationError(
            'output.formats must be a non-empty list of unique png and/or svg values'
        )

    scale = output.get('scale', 1.0)
    if (
        isinstance(scale, bool)
        or not isinstance(scale, (int, float))
        or not math.isfinite(scale)
        or scale <= 0
    ):
        raise ConfigurationError('output.scale must be a positive finite number')

    factory = _make_factory(config['factory'])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered_paths = []
    for image_format in formats:
        image_path = output_path.with_suffix(f'.{image_format}')
        save = save_png if image_format == 'png' else save_svg
        try:
            save(
                str(image_path),
                grid,
                factory,
                scale=scale,
                background_col=output.get('background_col'),
            )
        except (TypeError, ValueError, cairo.Error) as exc:
            raise ConfigurationError(f'Cannot render {image_path}: {exc}') from exc
        rendered_paths.append(image_path)
    return rendered_paths


def main() -> None:
    """Run the easy-tiler command."""
    parser = argparse.ArgumentParser(
        prog='easy-tiler',
        description='Render tile patterns from a YAML configuration file.',
    )
    parser.add_argument('config', type=Path, help='path to the YAML configuration file')
    args = parser.parse_args()
    try:
        paths = render_config(args.config)
    except (ConfigurationError, OSError) as exc:
        parser.error(str(exc))
    for path in paths:
        print(f'Wrote {path}')
