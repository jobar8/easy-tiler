import cairo
import pytest

from easy_tiler.colors import CustomPalette
from easy_tiler.tiles import PaletteTileConfig, RandomColorTileConfig, TileBase, TileConfig


class RecordingTile(TileBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.draw_calls = []

    def draw(self, ctx, g):
        self.draw_calls.append((ctx, g))


def test_tilebase_is_abstract():
    with pytest.raises(TypeError):
        object.__new__(TileBase)


def test_tilebase_can_be_instantiated_with_a_draw_implementation():
    tile = RecordingTile(rotations=2, rot_angle=1.0, rot=1, flipped=True, outline=False)

    assert tile.rotations == 2
    assert tile.rot == 1
    assert tile.flipped is True
    assert tile.outline is False


def test_tilebase_init_tile_applies_rotation_and_flip():
    tile = RecordingTile(rot=1, flipped=True)
    tile.config.width = 20
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 20, 20))

    tile.init_tile(ctx)

    matrix = ctx.get_matrix()
    assert matrix.xx == pytest.approx(0)
    assert matrix.xy == pytest.approx(-1)
    assert matrix.yx == pytest.approx(-1)
    assert matrix.yy == pytest.approx(0)


def test_tilebase_draw_tile_sets_width_and_delegates_to_draw():
    tile = RecordingTile()
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 16, 16))

    tile.draw_tile(ctx, 16)

    assert tile.config.width == 16
    assert tile.draw_calls == [(ctx, tile.config)]


def test_tile_config_defaults_to_transparent_colors():
    config = TileConfig()

    assert config.get_fg_color() == (0, 0, 0, 0)
    assert config.get_bg_color() == (0, 0, 0, 0)


def test_palette_tile_config_resolves_named_colors():
    config = PaletteTileConfig(
        fg_color='cyan',
        bg_color='pink',
        outline_color='purple',
        palette='ColorsOfTheWind',
    )
    palette = CustomPalette('ColorsOfTheWind')

    assert config.get_fg_color() == palette.get('cyan')
    assert config.get_bg_color() == palette.get('pink')
    assert config.outline_color == palette.get('purple')


def test_tile_config_resolves_color_lists_by_index():
    config = TileConfig(fg_color=['red', 'blue'])

    assert config.get_fg_color(0) == CustomPalette().get('red')
    assert config.get_fg_color(1) == CustomPalette().get('blue')
    assert config.get_fg_color(2) == CustomPalette().get('red')


def test_random_color_config_is_reproducible_from_seed():
    first = RandomColorTileConfig(fg_color='random', bg_color='random', seed=123)
    second = RandomColorTileConfig(fg_color='random', bg_color='random', seed=123)

    assert first.get_fg_color() == second.get_fg_color()
    assert first.get_bg_color() == second.get_bg_color()


def test_random_color_config_generates_arbitrary_rgb_colors():
    config = RandomColorTileConfig(fg_color='random', seed=123)

    color = config.get_fg_color()

    assert len(color) == 4
    assert color[3] == pytest.approx(1.0)
    assert all(0.0 <= channel <= 1.0 for channel in color[:3])


def test_palette_tile_config_random_chooses_from_palette():
    config = PaletteTileConfig(fg_color='random', palette='ColorsOfTheWind', seed=123)
    palette = CustomPalette('ColorsOfTheWind')
    palette_colors = {palette.get(color) for color in palette.colors}

    assert config.get_fg_color() in palette_colors
