"""Simple demo to render a grid of regular polygon tiles."""

from easy_tiler import RegularPolygonTile, TileBase, TruchetTile, PuckTile
from easy_tiler.helpers import color
import random
import math


def make_tile_factory(
    tile_type: str = 'polygon',
    rot: str | int = 'random',
    fg: tuple[float, float, float, float] | str = 'random',
    bg: tuple[float, float, float, float] | str = 'random',
    inset: float | None = None,
    flipped: bool = False,
    outline: bool = False,
    radius: float = 3.0,
    sides: int = 4,
):
    def factory(x, y) -> RegularPolygonTile | PuckTile | TruchetTile:
        if rot == 'random':
            actual_rot = random.randint(0, 4)
        else:
            actual_rot = rot

        if fg == 'random':
            actual_fg = (random.random(), random.random(), random.random(), 1.0)
        elif fg == 'black':
            actual_fg = color(0)
        else:
            actual_fg = fg

        if bg == 'random':
            actual_bg = (random.random(), random.random(), random.random(), 1.0)
        elif bg == 'white':
            actual_bg = color(1)
        else:
            actual_bg = bg

        if inset is None:
            actual_inset = math.sqrt(2)

        if tile_type == 'polygon':
            tile = RegularPolygonTile(sides=sides, rot=actual_rot, inset=actual_inset, flipped=flipped, outline=outline)
        elif tile_type == 'puck':
            tile = PuckTile(rot=actual_rot, flipped=flipped, outline=outline)
        elif tile_type == 'truchet':
            tile = TruchetTile(rot=actual_rot, flipped=flipped, outline=outline, radius=radius)
        else:
            raise ValueError(f'Invalid tile_type: {tile_type}')

        # attach bg/fg via closure by monkeypatching draw_tile call
        def draw_tile_with_bg(ctx, wh, bg_color=None, fg_color=None):
            # Call the base implementation to avoid recursive wrapper calls
            return TileBase.draw_tile(tile, ctx, wh, bg_color=actual_bg, fg_color=actual_fg)

        tile.draw_tile = draw_tile_with_bg  # type: ignore[assignment]
        return tile

    return factory
