"""Demo script for testing the form factory."""

from pathlib import Path

from easy_tiler.factories import make_form_factory
from easy_tiler.grid import Grid
from easy_tiler.io import save_png, save_svg

cwd = Path(__file__).parent


def run_form_demo():
    grid = Grid(12, 12, x_size=60, y_size=60)
    factory = make_form_factory(
        tile_type='riley',
        a=1,
        b=1,
        c=0,
        rotation_mod=5,
        color_mod=4,
        primary_color='sequence',
        # primary_color='random_rgb',
        # primary_color=['yellow', 'green',  'red'],
        # secondary_color=['black', 'white', 'black'],
        secondary_color='transparent',
        palette='Apricot',
        # palette='BlueRidgePkwy',
        # palette='Budnitz',
        num_colors=48,
        outline=False,
        outline_color='black',
        width=0.5,
        radius=1,
        use_seed=True,
    )
    png_path = cwd / 'images' / 'form_demo.png'
    svg_path = cwd / 'images' / 'form_demo.svg'
    save_png(str(png_path), grid, factory, scale=1, background_col='black')
    save_svg(str(svg_path), grid, factory)
    print(f'Wrote {png_path} and {svg_path}')


if __name__ == '__main__':
    run_form_demo()
