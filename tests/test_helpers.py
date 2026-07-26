from easy_tiler.helpers import color, hex_to_rgb


def test_color_uses_palette_values_for_named_colors():
    assert color('blue', palette='FridaKahlo') == (*hex_to_rgb('#203caaFF'), 1)
    assert color('red', palette='ClaudeMonet') == (*hex_to_rgb('#852419FF'), 1)
    assert color('green', palette='BlueRidgePkwy') == (*hex_to_rgb('#8C9D57FF'), 1)


def test_color_falls_back_to_standard_values_when_palette_missing():
    assert color('purple', palette='FridaKahlo') == (0.7, 0.2, 0.5, 1)
    assert color('orange', palette='ClaudeMonet') == (1, 0.75, 0.0, 1)
