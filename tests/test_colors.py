import random

import pytest

from easy_tiler import colors
from easy_tiler.colors import CustomPalette


def test_custom_palette_uses_palette_values_for_named_colors():
    assert CustomPalette('FridaKahlo').get('blue') == (0.12549019607843137, 0.23529411764705882, 0.6666666666666666, 1)
    assert CustomPalette('ClaudeMonet').get('red') == (0.5215686274509804, 0.1411764705882353, 0.09803921568627451, 1)
    assert CustomPalette('BlueRidgePkwy').get('green') == (0.5490196078431373, 0.615686274509804, 0.3411764705882353, 1)


def test_custom_palette_falls_back_to_standard_values_when_color_missing():
    assert CustomPalette('FridaKahlo').get('purple') == (0.7, 0.2, 0.5, 1)
    assert CustomPalette('ClaudeMonet').get('pink') == (1, 0.5, 0.8, 1)


def test_custom_palette_defaults_to_standard_palette():
    palette = CustomPalette()

    assert palette.palette is colors.STANDARD_PALETTE
    assert palette.colors == list(colors.STANDARD_PALETTE.values())


def test_custom_palette_limits_number_of_colors():
    palette = CustomPalette('FridaKahlo', num_colors=2)

    assert palette.colors == list(colors.CUSTOM_PALETTES['FridaKahlo'].values())[:2]


def test_custom_palette_loads_external_palette(monkeypatch):
    loaded_palette = ['#010203', '#aabbcc']
    monkeypatch.setitem(colors.cc.palette, 'test_palette', loaded_palette)

    palette = CustomPalette('test_palette')

    assert palette.palette == {}
    assert palette.colors == loaded_palette


def test_custom_palette_loads_palette_from_pypalettes(monkeypatch):
    loaded_palette = {'first': '#010203', 'second': '#aabbcc'}
    monkeypatch.setattr(colors, 'load_palette', lambda name: loaded_palette)

    palette = CustomPalette('unknown_palette')

    assert palette.palette is loaded_palette
    assert palette.colors == list(loaded_palette.values())


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('#010203', (1 / 255, 2 / 255, 3 / 255, 1)),
        ('#01020380', (1 / 255, 2 / 255, 3 / 255, 128 / 255)),
        (0.25, (0.25, 0.25, 0.25, 1)),
        ([0.1, 0.2, 0.3], (0.1, 0.2, 0.3, 1)),
        ((0.1, 0.2, 0.3, 0.4), (0.1, 0.2, 0.3, 0.4)),
        (None, (0, 0, 0, 0)),
    ],
)
def test_custom_palette_get_converts_supported_values(value, expected):
    assert CustomPalette().get(value) == expected


def test_custom_palette_get_random_uses_random_channels(monkeypatch):
    values = iter((0.1, 0.2, 0.3))
    monkeypatch.setattr(random, 'random', lambda: next(values))

    assert CustomPalette().get('random') == (0.1, 0.2, 0.3, 1)


def test_custom_palette_get_random_choice_resolves_selected_color(monkeypatch):
    monkeypatch.setattr(random, 'choice', lambda values: '#010203')

    assert CustomPalette().get('random_choice') == (1 / 255, 2 / 255, 3 / 255, 1)


def test_custom_palette_get_returns_transparent_for_unsupported_value(capsys):
    assert CustomPalette().get('not-a-color') == (0, 0, 0, 0)
    assert 'Unsupported color value: not-a-color' in capsys.readouterr().out
