"""Selection of color palettes for use in tiling.
Custom palettes found on https://y-sunflower.github.io/pypalettes/
"""

import random

from numpy import ndarray

CUSTOM_PALETTES = {
    'FridaKahlo': {
        'black': '#121510FF',
        'blue': '#203caaFF',
        'green': '#6D8325FF',
        'beige': '#D6CFB7FF',
        'yellow': '#E5AD4FFF',
        'brown': '#BD5630FF',
    },
    'BlueRidgePkwy': {
        'pink': '#EC8FA3FF',
        'orange': '#FCBA65FF',
        'beige': '#FAECCFFF',
        'purple': '#8D7F99FF',
        'green': '#8C9D57FF',
        'blue': '#163343FF',
    },
    'ClaudeMonet': {
        'green': '#184430FF',
        'light_green': '#548150FF',
        'orange': '#DEB738FF',
        'brown': '#734321FF',
        'red': '#852419FF',
        'light_blue': '#4885A4FF',
        'blue': '#395A92FF',
        'olive': '#7EA860FF',
        'purple': '#B985BAFF',
        'dark_blue': '#4C7899FF',
        'dark_green': '#2F5136FF',
        'yellow': '#B1B94CFF',
        'beige': '#E5DCBEFF',
    },
}

STANDARD_PALETTE = {
    'black': (0, 0, 0, 1),
    'white': (1, 1, 1, 1),
    'red': (1, 0, 0, 1),
    'green': (0, 1, 0, 1),
    'blue': (0, 0, 1, 1),
    'yellow': (1, 1, 0, 1),
    'gray': (0.5, 0.5, 0.5, 1),
    'brown': (0.6, 0.4, 0.2, 1),
    'beige': (0.96, 0.96, 0.86, 1),
    'magenta': (1, 0, 1, 1),
    'cyan': (0, 1, 1, 1),
    'purple': (0.7, 0.2, 0.5, 1),
    'orange': (1, 0.75, 0.0, 1),
    'pink': (1, 0.5, 0.8, 1),
}


class CustomColor:
    """Class to represent a custom color with RGBA values."""

    def __init__(self, palette: str = 'Standard'):
        self.palette = CUSTOM_PALETTES.get(palette) or STANDARD_PALETTE

    def _hex_to_rgb(self, hex_color: str) -> tuple[float, float, float]:
        """Convert a hex color string to an RGB tuple with values in the range [0, 1]."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)

    def get(
        self,
        val: float | list | tuple | ndarray | str | None,
    ) -> tuple[float, float, float, float]:
        """Create an RGBA color tuple from a variety of inputs."""
        if val is None:
            return (0, 0, 0, 0)  # transparent
        if isinstance(val, (int, float)):
            return (val, val, val, 1)
        if isinstance(val, (list, tuple)):
            if len(val) == 3:
                return (*val, 1)
            return tuple(val)
        if isinstance(val, str):
            if val.startswith('#'):
                return (*self._hex_to_rgb(val), 1)
            if val == 'random':
                return (random.random(), random.random(), random.random(), 1)
            if val == 'random_choice':
                return (*self._hex_to_rgb(random.choice(list(self.palette.values()))), 1)
            try:
                return (*self._hex_to_rgb(self.palette[val]), 1)
            except KeyError:
                return STANDARD_PALETTE[val]  # Fall back to standard colors if not found in palette
            else:
                raise ValueError(f'Invalid color string format: {val}')

        raise TypeError(f'Unsupported color value: {val}')
