import numpy as np
import pytest

from easy_tiler.colors import CustomPalette
from easy_tiler.factories import make_node_factory, make_sequence_factory, make_tile_factory
from easy_tiler.tiles import TileConfig


def test_get_palette_resolves_local_palette_and_num_colors():
    colors = TileConfig.get_palette('ColorsOfTheWind', num_colors=2)

    assert colors == ['#9cf1ff', '#ff9acd']


def test_tile_config_resolves_local_palette_colors():
    config = TileConfig(
        fg_color='cyan',
        bg_color='pink',
        outline_color='purple',
        palette='ColorsOfTheWind',
    )

    assert config.get_fg_color() == CustomPalette('ColorsOfTheWind').get('cyan')
    assert config.get_bg_color() == CustomPalette('ColorsOfTheWind').get('pink')
    assert config.outline_color == CustomPalette('ColorsOfTheWind').get('purple')


def test_make_tile_factory_uses_palette_colors_sequentially():
    factory = make_tile_factory(
        fg=['blue', 'green'],
        bg=['yellow', 'brown'],
        palette='FridaKahlo',
    )
    palette = CustomPalette('FridaKahlo')

    first_tile = factory(0, 0)
    second_tile = factory(1, 0)
    repeated_tile = factory(2, 0)

    assert first_tile.config.fg_color == palette.get('blue')
    assert second_tile.config.fg_color == palette.get('green')
    assert repeated_tile.config.fg_color == palette.get('blue')
    assert first_tile.config.bg_color == palette.get('yellow')
    assert second_tile.config.bg_color == palette.get('brown')
    assert repeated_tile.config.bg_color == palette.get('yellow')


def test_make_tile_factory_supports_local_palette_outline():
    factory = make_tile_factory(
        fg='cyan',
        bg='pink',
        outline=True,
        outline_color='purple',
        palette='ColorsOfTheWind',
    )
    palette = CustomPalette('ColorsOfTheWind')

    tile = factory(0, 0)

    assert tile.config.fg_color == palette.get('cyan')
    assert tile.config.bg_color == palette.get('pink')
    assert tile.config.outline_color == palette.get('purple')


@pytest.mark.parametrize(
    'factory_builder',
    [
        lambda: make_sequence_factory(
            palette='ColorsOfTheWind', fg='sequence', bg='sequence', outline_color='purple'
        ),
        lambda: make_node_factory(
            palette='ColorsOfTheWind',
            node_sequence=np.array([[0]]),
            fg='sequence',
            bg='sequence',
            outline_color='purple',
        ),
    ],
)
def test_factories_support_local_palette(factory_builder):
    tile = factory_builder()(0, 0)

    assert tile.config.fg_color != (0, 0, 0, 0)
    assert tile.config.bg_color != (0, 0, 0, 0)
    assert tile.config.outline_color == CustomPalette('ColorsOfTheWind').get('purple')


def test_get_palette_rejects_unknown_palette():
    with pytest.raises((KeyError, ValueError)):
        TileConfig.get_palette('not-a-palette')