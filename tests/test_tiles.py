import cairo
import pytest

from easy_tiler.colors import ColorConfig, CustomPalette
from easy_tiler.tiles import (
    ArrowTile,
    RegularPolygonTile,
    RileyTile,
    TileBase,
    TileConfig,
)


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
            max_rotations=2, rotation_angle=1.0, rotation_index=1, flipped=True, gridlines=False
        )
    )

    assert tile.config.max_rotations == 2
    assert tile.config.rotation_index == 1
    assert tile.config.flipped is True
    assert tile.config.gridlines is False
    assert not hasattr(tile, 'rotation_index')
    assert not hasattr(tile, 'flipped')
    assert not hasattr(tile, 'gridlines')


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
        gridlines_color='purple',
        palette='ColorsOfTheWind',
    )
    palette = CustomPalette('ColorsOfTheWind')

    assert config.get_primary_color() == palette.get('cyan')
    assert config.get_secondary_color() == palette.get('pink')
    assert config.gridlines_color == palette.get('purple')


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


def test_tile_config_holds_every_shape_parameter():
    """A single config can carry the parameters of any tile type."""
    config = TileConfig(
        sides=7,
        inset=0.9,
        radius=1.2,
        side_length=0.8,
        arrow_width=0.4,
        rotation_index=1,
        flipped=True,
        gridlines=True,
    )

    assert config.sides == 7
    assert config.inset == pytest.approx(0.9)
    assert config.radius == pytest.approx(1.2)
    assert config.side_length == pytest.approx(0.8)
    assert config.arrow_width == pytest.approx(0.4)
    assert config.rotation_index == 1
    assert config.flipped is True
    assert config.gridlines is True


def test_tile_config_shape_parameters_default_to_unset():
    config = TileConfig()

    assert config.sides is None
    assert config.inset is None
    assert config.radius is None
    assert config.side_length is None
    assert config.arrow_width is None


def test_tile_fills_unset_parameters_from_class_defaults():
    tile = RegularPolygonTile(config=TileConfig(sides=5))

    assert tile.config.sides == 5
    assert tile.config.inset == pytest.approx(0.85)


def test_tile_does_not_mutate_the_config_it_was_given():
    config = TileConfig(sides=5)

    tile = RegularPolygonTile(config=config)

    assert tile.config is not config
    assert config.inset is None
    assert tile.config.inset == pytest.approx(0.85)


def test_tile_keyword_overrides_take_precedence_over_the_config():
    tile = RegularPolygonTile(config=TileConfig(sides=5), sides=6)

    assert tile.config.sides == 6


def test_tile_uses_the_config_it_is_handed_when_drawing():
    """The config passed to draw() is what determines the drawn geometry."""
    tile = RegularPolygonTile(config=TileConfig(tile_width=40, sides=3))
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 40, 40))

    # Tiles call ctx.restore() when they are done, so a save is required.
    ctx.save()
    tile.init_tile(ctx)
    tile.draw(ctx, tile.config)

    assert tile.config.sides == 3


def test_riley_tile_rotation_offset_is_applied_to_the_config():
    tile = RileyTile(config=TileConfig(rotation_index=0))

    assert tile.config.rotation_index == 3


def test_riley_tile_does_not_scale_its_radius_between_draws():
    """Drawing a tile twice must produce the same geometry."""
    tile = RileyTile(config=TileConfig(tile_width=40, radius=1.0))
    ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 40, 40))

    ctx.save()
    tile.draw_tile(ctx)
    first_radius = tile.config.radius

    ctx.save()
    tile.draw_tile(ctx)

    assert tile.config.radius == first_radius


def test_arrow_tile_rejects_an_out_of_range_arrow_width():
    with pytest.raises(ValueError, match='between 0 and 1'):
        ArrowTile(config=TileConfig(arrow_width=1.5))

    with pytest.raises(ValueError, match='between 0 and 1'):
        ArrowTile(config=TileConfig(arrow_width=0.0))
