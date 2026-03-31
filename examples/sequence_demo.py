"""Demo script for testing the sequence factory."""

from easy_tiler.factories import make_sequence_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg


def run_sequence_demo():
    # 12x10 grid with sequence length of 4
    grid = Grid(12, 10, x_size=60, y_size=60)

    # Factory with sequence length of 4, random colors from a palette
    factory = make_sequence_factory(
        tile_type='puck',
        # tile_sequence=[1,0,2,3],
        # tile_sequence=[0,1,2,3],
        # tile_sequence=[1, 2, 0, 3],
        # tile_sequence=[1, 2],
        sequence_length=4,
        fg='roll',
        bg='roll',
        # palette='glasbey_dark',
        palette='glasbey',
        num_colors=12,
        outline=False,
    )

    save_png('sequence_demo.png', grid, factory, scale=1)
    save_svg('sequence_demo.svg', grid, factory)
    print('Wrote sequence_demo.png and sequence_demo.svg')


if __name__ == '__main__':
    run_sequence_demo()
