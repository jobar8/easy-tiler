"""Demo script for testing the sequence factory."""

from easy_tiler.factories import make_sequence_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg


def run_sequence_demo():
    grid = Grid(12, 10, x_size=60, y_size=60)

    factory = make_sequence_factory(
        tile_type='truchet',
        # tile_sequence=[1, 0, 2, 3],
        # tile_sequence=[0, 1, 2],
        tile_sequence=[1, 2, 0, 3],
        # tile_sequence=[1, 2],
        sequence_length=4,
        # fg='black',
        fg='roll',
        bg='sequence',
        palette='glasbey_light',
        num_colors=16,
        outline=False,
        use_seed=False,
    )

    save_png('sequence_demo.png', grid, factory, scale=1)
    save_svg('sequence_demo.svg', grid, factory)
    print('Wrote sequence_demo.png and sequence_demo.svg')


if __name__ == '__main__':
    run_sequence_demo()
