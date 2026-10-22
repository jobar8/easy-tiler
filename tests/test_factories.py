import math

import numpy as np
import pytest

from easy_tiler.colors import ColorConfig, CustomPalette
from easy_tiler.factories import (
    make_form_factory,
    make_node_factory,
    make_sequence_factory,
    make_tile_factory,
)
from easy_tiler.tiles import (
    ArrowTile,
    CairoTile,
    CircleTile,
    PentagonTile,
    PuckTile,
    RegularPolygonTile,
    RileyTile,
    TileConfig,
    TruchetTile,
)


def test_get_palette_resolves_local_palette_and_num_colors():
    colors = ColorConfig.get_palette('ColorsOfTheWind', num_colors=2)

    assert colors == ['#9cf1ff', '#ff9acd']


def test_color_config_resolves_local_palette_colors():
    config = ColorConfig(
        primary_color='cyan',
        secondary_color='pink',
        outline_color='purple',
        palette='ColorsOfTheWind',
    )

    assert config.get_primary_color() == CustomPalette('ColorsOfTheWind').get('cyan')
    assert config.get_secondary_color() == CustomPalette('ColorsOfTheWind').get('pink')
    assert config.outline_color == CustomPalette('ColorsOfTheWind').get('purple')


def test_color_config_seed_makes_random_colors_reproducible():
    first = ColorConfig(
        primary_color='random', secondary_color='random', palette='Standard', seed=123
    )
    second = ColorConfig(
        primary_color='random', secondary_color='random', palette='Standard', seed=123
    )

    assert first.get_primary_color() == second.get_primary_color()
    assert first.get_secondary_color() == second.get_secondary_color()


def test_make_tile_factory_seed_makes_random_colors_reproducible():
    first = make_tile_factory(palette='Standard', use_seed=True)(0, 0)
    second = make_tile_factory(palette='Standard', use_seed=True)(0, 0)

    assert first.color_config.primary_color == 'random'
    assert first.color_config.secondary_color == 'random'
    assert first.color_config.get_primary_color() == second.color_config.get_primary_color()
    assert first.color_config.get_secondary_color() == second.color_config.get_secondary_color()


def test_node_factory_random_colors_are_reproducible_and_vary_by_position():
    first = make_node_factory(
        node_sequence=np.array([[0, 0]]),
        palette='Standard',
        use_seed=True,
    )
    second = make_node_factory(
        node_sequence=np.array([[0, 0]]),
        palette='Standard',
        use_seed=True,
    )
    first_color = first(0, 0).color_config.get_primary_color()
    second_color = second(0, 0).color_config.get_primary_color()
    repeated_color = first(0, 1).color_config.get_primary_color()

    assert first_color == second_color
    assert first_color != repeated_color


def test_make_tile_factory_uses_separate_tile_and_color_configs():
    tile = make_tile_factory(palette='Standard', use_seed=True)(0, 0)

    assert type(tile.config) is TileConfig
    assert type(tile.color_config) is ColorConfig


def test_factories_select_palette_config_for_resolved_colors():
    direct_tile = make_tile_factory(primary_color='blue', secondary_color='white')(0, 0)
    sequence_tile = make_sequence_factory(
        primary_color='blue', secondary_color='white', tile_sequence=[0]
    )(0, 0)
    node_tile = make_node_factory(
        node_sequence=np.array([[0]]), primary_color='blue', secondary_color='white'
    )(0, 0)
    form_tile = make_form_factory(primary_color='blue', secondary_color='white')(0, 0)

    assert type(direct_tile.config) is TileConfig
    assert type(sequence_tile.config) is TileConfig
    assert type(node_tile.config) is TileConfig
    assert type(form_tile.config) is TileConfig
    assert type(direct_tile.color_config) is ColorConfig
    assert type(sequence_tile.color_config) is ColorConfig
    assert type(node_tile.color_config) is ColorConfig
    assert type(form_tile.color_config) is ColorConfig


@pytest.mark.parametrize(
    'factory_builder',
    [
        make_tile_factory,
        make_sequence_factory,
        lambda **kwargs: make_node_factory(node_sequence=np.array([[0]]), **kwargs),
        make_form_factory,
    ],
)
def test_factories_leave_unset_shape_options_as_none(factory_builder):
    """Options that do not belong to the tile type stay unset in the config.

    The tile class supplies the defaults for the values it actually needs, so
    one config can describe any tile type without carrying meaningless values.
    """
    config = factory_builder(tile_type='truchet')(0, 0).config

    assert config.flipped is False
    assert config.outline is False
    assert config.sides is None
    assert config.inset is None
    assert config.radius is None
    assert config.side_length is None
    assert config.arrow_width is None


@pytest.mark.parametrize(
    ('tile_type', 'option', 'value'),
    [
        ('polygon', 'sides', 7),
        ('polygon', 'inset', 1.0),
        ('riley', 'radius', 1.2),
        ('circle', 'radius', 0.3),
        ('smith', 'radius', 0.4),
        ('pentagon', 'side_length', 0.8),
        ('arrow', 'arrow_width', 0.6),
    ],
)
def test_factories_pass_shape_options_to_the_tile_config(tile_type, option, value):
    tile = make_tile_factory(tile_type=tile_type, **{option: value})(0, 0)

    assert getattr(tile.config, option) == value


@pytest.mark.parametrize(
    ('tile_type', 'expected'),
    [
        ('polygon', {'sides': 4, 'inset': 0.85}),
        ('riley', {'radius': 1.0}),
        ('circle', {'radius': 0.25}),
        ('smith', {'radius': 0.5}),
        ('pentagon', {'side_length': 1.0 / (4 * math.cos(math.pi / 6))}),
        ('arrow', {'arrow_width': pytest.approx(0.333)}),
    ],
)
def test_tile_classes_supply_their_own_defaults(tile_type, expected):
    """A tile fills in the parameters it needs from its class defaults."""
    tile = make_tile_factory(tile_type=tile_type)(0, 0)

    for name, value in expected.items():
        assert getattr(tile.config, name) == value


@pytest.mark.parametrize(
    'factory_builder',
    [
        make_tile_factory,
        make_sequence_factory,
        make_node_factory,
        make_form_factory,
    ],
)
def test_factories_set_arrow_width_on_tile_config(factory_builder):
    tile = factory_builder(tile_type='arrow', arrow_width=0.6)(0, 0)

    assert isinstance(tile, ArrowTile)
    assert tile.config.arrow_width == pytest.approx(0.6)


def test_make_tile_factory_uses_palette_colors_sequentially():
    factory = make_tile_factory(
        primary_color=['blue', 'green'],
        secondary_color=['yellow', 'brown'],
        palette='FridaKahlo',
    )
    palette = CustomPalette('FridaKahlo')

    first_tile = factory(0, 0)
    second_tile = factory(1, 0)
    repeated_tile = factory(2, 0)

    assert first_tile.color_config.get_primary_color() == palette.get('blue')
    assert second_tile.color_config.get_primary_color() == palette.get('green')
    assert repeated_tile.color_config.get_primary_color() == palette.get('blue')
    assert first_tile.color_config.get_secondary_color() == palette.get('yellow')
    assert second_tile.color_config.get_secondary_color() == palette.get('brown')
    assert repeated_tile.color_config.get_secondary_color() == palette.get('yellow')


def test_sequence_factory_resolves_rolled_colors_in_color_config():
    factory = make_sequence_factory(
        sequence_length=2,
        tile_sequence=[0, 0],
        primary_color='roll',
        palette='ColorsOfTheWind',
    )
    first = factory(0, 0).color_config
    second = factory(1, 0).color_config
    rolled = factory(2, 0).color_config

    assert first.primary_color == 'roll'
    assert rolled.get_primary_color() == second.get_primary_color()


def test_make_tile_factory_supports_local_palette_outline():
    factory = make_tile_factory(
        primary_color='cyan',
        secondary_color='pink',
        outline=True,
        outline_color='purple',
        palette='ColorsOfTheWind',
    )
    palette = CustomPalette('ColorsOfTheWind')

    tile = factory(0, 0)

    assert tile.color_config.get_primary_color() == palette.get('cyan')
    assert tile.color_config.get_secondary_color() == palette.get('pink')
    assert tile.color_config.outline_color == palette.get('purple')


@pytest.mark.parametrize(
    ('tile_type', 'tile_class'),
    [
        ('polygon', RegularPolygonTile),
        ('puck', PuckTile),
        ('truchet', TruchetTile),
        ('arrow', ArrowTile),
        ('riley', RileyTile),
        ('cairo', CairoTile),
        ('pentagon', PentagonTile),
        ('circle', CircleTile),
    ],
)
def test_make_tile_factory_supports_registered_tile_types(tile_type, tile_class):
    factory = make_tile_factory(
        tile_type=tile_type, rotation_index=0, primary_color='blue', secondary_color='white'
    )

    assert isinstance(factory(0, 0), tile_class)


@pytest.mark.parametrize('tile_type', ['cairo', 'pentagon'])
def test_make_sequence_factory_supports_tile_type(tile_type):
    factory = make_sequence_factory(
        tile_type=tile_type, tile_sequence=[0], primary_color='blue', secondary_color='white'
    )

    assert isinstance(factory(0, 0), {'cairo': CairoTile, 'pentagon': PentagonTile}[tile_type])


@pytest.mark.parametrize('tile_type', ['cairo', 'pentagon'])
def test_make_node_factory_supports_tile_type(tile_type):
    factory = make_node_factory(
        tile_type=tile_type,
        node_sequence=np.array([[0]]),
        primary_color='blue',
        secondary_color='white',
    )

    assert isinstance(factory(0, 0), {'cairo': CairoTile, 'pentagon': PentagonTile}[tile_type])


@pytest.mark.parametrize(
    'factory_builder',
    [
        lambda: make_sequence_factory(
            palette='ColorsOfTheWind',
            primary_color='sequence',
            secondary_color='sequence',
            outline_color='purple',
        ),
        lambda: make_node_factory(
            palette='ColorsOfTheWind',
            node_sequence=np.array([[0]]),
            primary_color='sequence',
            secondary_color='sequence',
            outline_color='purple',
        ),
    ],
)
def test_factories_support_local_palette(factory_builder):
    tile = factory_builder()(0, 0)

    assert tile.color_config.primary_color != (0, 0, 0, 0)
    assert tile.color_config.secondary_color != (0, 0, 0, 0)
    assert tile.color_config.outline_color == CustomPalette('ColorsOfTheWind').get('purple')


def test_get_palette_rejects_unknown_palette():
    with pytest.raises((KeyError, ValueError)):
        ColorConfig.get_palette('not-a-palette')


def test_make_form_factory_derives_rotation_and_color_index_from_formula():
    factory = make_form_factory(
        tile_type='polygon',
        a=1.0,
        b=1.0,
        c=0.0,
        rotation_mod=4,
        color_mod=8,
        primary_color='blue',
        secondary_color='white',
    )

    tile = factory(2, 3)

    assert isinstance(tile, RegularPolygonTile)
    # sequence_position = int(1.0 * 2 + 1.0 * 3 + 0.0) = 5
    assert tile.config.rotation_index == 5 % 4
    assert tile.color_config.color_index == 5 % 8
    assert tile.color_config.roll_index == 3
