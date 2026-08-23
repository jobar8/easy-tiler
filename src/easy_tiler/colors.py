"""Selection of color palettes for use in tiling.
Custom palettes found on https://y-sunflower.github.io/pypalettes/
"""

import random

import colorcet as cc
from numpy import ndarray
from pypalettes import load_palette

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
    'ColorsOfTheWind': {
        'cyan': '#9cf1ff',
        'pink': '#ff9acd',
        'yellow': '#fff091',
        'green': '#b1ffa6',
        'purple': '#dda3ff',
        'beige': '#E6D5C3',
        'blue': '#b8dbec',
        'gray': '#c9b8ec',
        'red': '#ecb8db',
        'orange': '#ecc9b8',
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


class CustomPalette:
    """Load a palette and resolve its colors to RGBA values."""

    def __init__(self, palette: str = 'Standard', num_colors: int | None = None):
        if palette == 'Standard':
            colors = STANDARD_PALETTE
        elif palette in CUSTOM_PALETTES:
            colors = CUSTOM_PALETTES[palette]
        else:
            try:
                colors = cc.palette[palette]
            except KeyError:
                colors = load_palette(palette)

        if isinstance(colors, dict):
            self.palette = colors
            self.colors = list(colors.values())
        else:
            self.palette = {}
            self.colors = list(colors)

        if num_colors is not None:
            self.colors = self.colors[:num_colors]

    def _hex_to_rgba(self, hex_color: str) -> tuple[float, float, float, float]:
        """Convert a hex color string to an RGBA tuple."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0 if len(hex_color) >= 8 else 1.0
        return (r, g, b, a)

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
                return self._hex_to_rgba(val)
            if val == 'random':
                return (random.random(), random.random(), random.random(), 1)
            if val == 'random_choice':
                return self.get(random.choice(self.colors))
            try:
                return self.get(self.palette[val])
            except KeyError:
                return STANDARD_PALETTE[val]  # Fall back to standard colors if not found in palette

        raise TypeError(f'Unsupported color value: {val}')
