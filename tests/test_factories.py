from easy_tiler.colors import CustomPalette
from easy_tiler.factories import make_tile_factory


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