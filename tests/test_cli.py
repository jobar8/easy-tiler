"""Tests for rendering images from YAML configuration."""

import sys

import pytest
import yaml

from easy_tiler.cli import ConfigurationError, main, render_config


@pytest.mark.parametrize(
    ('factory_type', 'factory_options'),
    [
        ('tile', {'tile_type': 'circle', 'radius': 0.3}),
        ('sequence', {'tile_type': 'riley', 'tile_sequence': [0, 1]}),
        ('node', {'tile_type': 'truchet', 'node_sequence': [[0, 1], [2, 3]]}),
        ('form', {'tile_type': 'polygon', 'a': 1, 'b': 1}),
    ],
)
def test_cli_renders_configured_formats(tmp_path, monkeypatch, factory_type, factory_options):
    config_path = tmp_path / 'pattern.yaml'
    config = {
        'grid': {'width': 2, 'height': 2, 'x_size': 12, 'y_size': 12},
        'factory': {'type': factory_type, **factory_options, 'stroke': True},
        'output': {
            'path': 'images/pattern',
            'formats': ['png', 'svg'],
            'background_col': 'white',
        },
    }
    config_path.write_text(yaml.safe_dump(config), encoding='utf-8')
    monkeypatch.setattr(sys, 'argv', ['easy-tiler', str(config_path)])

    main()

    for suffix in ('.png', '.svg'):
        output = tmp_path / 'images' / f'pattern{suffix}'
        assert output.is_file()
        assert output.stat().st_size > 0


def test_output_format_can_be_selected(tmp_path):
    config_path = tmp_path / 'pattern.yaml'
    config_path.write_text(
        yaml.safe_dump({
            'grid': {'width': 1, 'height': 1},
            'factory': {'type': 'tile', 'tile_type': 'square'},
            'output': {'path': 'pattern', 'formats': ['png']},
        }),
        encoding='utf-8',
    )

    paths = render_config(config_path)

    assert [path.suffix for path in paths] == ['.png']
    assert (tmp_path / 'pattern.png').is_file()
    assert not (tmp_path / 'pattern.svg').exists()


def test_default_output_formats_are_png_and_svg(tmp_path):
    config_path = tmp_path / 'pattern.yaml'
    config_path.write_text(
        yaml.safe_dump({
            'grid': {'width': 1, 'height': 1},
            'factory': {'type': 'tile', 'tile_type': 'square'},
            'output': {'path': 'pattern'},
        }),
        encoding='utf-8',
    )

    paths = render_config(config_path)

    assert [path.suffix for path in paths] == ['.png', '.svg']
    assert (tmp_path / 'pattern.png').is_file()
    assert (tmp_path / 'pattern.svg').is_file()


@pytest.mark.parametrize(
    ('config', 'message'),
    [
        ({'grid': {}, 'factory': {'type': 'tile'}, 'output': {'path': 'out'}}, 'grid.width'),
        (
            {
                'grid': {'width': '2', 'height': 1},
                'factory': {'type': 'tile'},
                'output': {'path': 'out'},
            },
            'grid.width must be a positive integer',
        ),
        (
            {
                'grid': {'width': 1, 'height': 1},
                'factory': {'type': 'unknown'},
                'output': {'path': 'out'},
            },
            'Unsupported factory.type',
        ),
        (
            {
                'grid': {'width': 1, 'height': 1},
                'factory': {'type': 'tile', 'unknown_option': True},
                'output': {'path': 'out'},
            },
            'Unknown factory option',
        ),
        (
            {
                'grid': {'width': 1, 'height': 1},
                'factory': {'type': 'tile'},
                'output': {'path': 'out', 'formats': ['jpg']},
            },
            'output.formats',
        ),
    ],
)
def test_invalid_config_raises_actionable_error(tmp_path, config, message):
    config_path = tmp_path / 'invalid.yaml'
    config_path.write_text(yaml.safe_dump(config), encoding='utf-8')

    with pytest.raises(ConfigurationError, match=message):
        render_config(config_path)


def test_cli_reports_missing_config(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['easy-tiler', str(tmp_path / 'missing.yaml')])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2
    assert 'Cannot read config' in capsys.readouterr().err


def test_cli_reports_invalid_yaml(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / 'invalid.yaml'
    config_path.write_text('grid: [', encoding='utf-8')
    monkeypatch.setattr(sys, 'argv', ['easy-tiler', str(config_path)])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 2
    assert 'Invalid YAML' in capsys.readouterr().err


def test_cli_reports_factory_errors_without_traceback(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / 'invalid-factory.yaml'
    config_path.write_text(
        yaml.safe_dump({
            'grid': {'width': 1, 'height': 1},
            'factory': {'type': 'tile', 'tile_type': 'not-a-tile'},
            'output': {'path': 'pattern', 'formats': ['png']},
        }),
        encoding='utf-8',
    )
    monkeypatch.setattr(sys, 'argv', ['easy-tiler', str(config_path)])

    with pytest.raises(SystemExit) as exc:
        main()

    error_output = capsys.readouterr().err
    assert exc.value.code == 2
    assert 'Cannot render' in error_output
    assert 'Invalid tile_type' in error_output
