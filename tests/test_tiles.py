import cairo
import pytest

from easy_tiler.colors import ColorConfig, CustomPalette
from easy_tiler.tiles import TileBase, TileConfig


class RecordingTile(TileBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.draw_calls = []

    def draw(self, ctx, g, index=0):
        self.draw_calls.append((ctx, g))


def test_tilebase_is_abstract():
    with pytest.raises(TypeError):
        object.__new__(TileBase)


def test_tilebase_can_be_instantiated_with_a_draw_implementation():
    tile = RecordingTile(
        config=TileConfig(
            max_rotations=2, rotation_angle=1.0, rotation_index=1, flipped=True, outline=False
        )
    )

    assert tile.config.max_rotations == 2
    assert tile.config.rotation_index == 1
    assert tile.config.flipped is True
    assert tile.config.outline is False
    assert not hasattr(tile, 'rotation_index')
    assert not hasattr(tile, 'flipped')
    assert not hasattr(tile, 'outline')


def test_tilebase_init_tile_applies_rotation_and_flip():
    tile = RecordingTile(config=TileConfig(rotation_index=1, flipped=True))
    tile.config.tile_width = 20
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 20, 20))

    tile.init_tile(ctx)

    matrix = ctx.get_matrix()
    assert matrix.xx == pytest.approx(0)
    assert matrix.xy == pytest.approx(-1)
    assert matrix.yx == pytest.approx(-1)
    assert matrix.yy == pytest.approx(0)


def test_tilebase_draw_tile_uses_config_tile_width_and_delegates_to_draw():
    tile = RecordingTile(config=TileConfig(tile_width=16))
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 16, 16))

    tile.draw_tile(ctx)

    assert tile.config.tile_width == 16
    assert tile.draw_calls == [(ctx, tile.config)]


def test_color_config_defaults_to_transparent_colors():
    config = ColorConfig()

    assert config.get_primary_color() == (0, 0, 0, 0)
    assert config.get_secondary_color() == (0, 0, 0, 0)


def test_color_config_resolves_named_colors():
    config = ColorConfig(
        primary_color='cyan',
        secondary_color='pink',
        outline_color='purple',
        palette='ColorsOfTheWind',
    )
    palette = CustomPalette('ColorsOfTheWind')

    assert config.get_primary_color() == palette.get('cyan')
    assert config.get_secondary_color() == palette.get('pink')
    assert config.outline_color == palette.get('purple')


def test_color_config_resolves_color_lists_by_index():
    config = ColorConfig(primary_color=['red', 'blue'])

    assert config.get_primary_color(0) == CustomPalette().get('red')
    assert config.get_primary_color(1) == CustomPalette().get('blue')
    assert config.get_primary_color(2) == CustomPalette().get('red')


def test_color_config_resolves_sequence_and_rolled_colors():
    palette = CustomPalette('ColorsOfTheWind')
    sequence = ['cyan', 'pink']
    config = ColorConfig(
        primary_color='sequence',
        secondary_color='roll',
        primary_colors=sequence,
        secondary_colors=sequence,
        color_index=0,
        roll_index=1,
        palette=palette,
    )

    assert config.get_primary_color() == palette.get('cyan')
    assert config.get_secondary_color() == palette.get('pink')


@pytest.mark.parametrize('color', ['sequence', 'roll'])
def test_color_config_requires_sequence_colors_for_sequence_modes(color):
    config = ColorConfig(primary_color=color)

    with pytest.raises(ValueError, match='requires sequence colors'):
        config.get_primary_color()


def test_color_config_random_colors_are_reproducible_from_seed():
    first = ColorConfig(primary_color='random', secondary_color='random', seed=123)
    second = ColorConfig(primary_color='random', secondary_color='random', seed=123)

    assert first.get_primary_color() == second.get_primary_color()
    assert first.get_secondary_color() == second.get_secondary_color()


def test_color_config_random_chooses_from_palette():
    config = ColorConfig(
        primary_color='random', secondary_color='random', palette='ColorsOfTheWind', seed=123
    )
    palette = CustomPalette('ColorsOfTheWind')
    palette_colors = {palette.get(color) for color in palette.colors}

    assert config.get_primary_color() in palette_colors
    assert config.get_secondary_color() in palette_colors
