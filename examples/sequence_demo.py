"""Demo script for testing the sequence factory."""

from pathlib import Path

from easy_tiler.factories import make_sequence_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

cwd = Path(__file__).parent


def run_sequence_demo():
    grid = Grid(12, 12, x_size=60, y_size=60)

    factory = make_sequence_factory(
        tile_type='truchet',
        # tile_sequence=[1, 0, 2, 3],
        # tile_sequence=[0, 1],
        tile_sequence=[2, 2, 3, 3, 1, 0],
        # tile_sequence=[1, 2],
        sequence_length=4,
        # fg='blue',
        # fg='roll',
        fg='sequence',
        # fg='random',
        # fg=['red', 'orange', 'orange', 'pink'],
        # bg='roll',
        bg='white',
        # bg=['yellow', 'green', 'pink', 'white'],
        palette='glasbey_light',
        # palette='Standard',
        num_colors=16,
        radius=0.25,
        outline=False,
        use_seed=True,
    )
    png_path = cwd / 'images' / 'sequence_demo.png'
    svg_path = cwd / 'images' / 'sequence_demo.svg'
    save_png(str(png_path), grid, factory, scale=1)
    save_svg(str(svg_path), grid, factory)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_sequence_demo()
