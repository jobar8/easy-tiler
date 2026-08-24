from easy_tiler.colors import CustomPalette


def test_custom_palette_uses_palette_values_for_named_colors():
    assert CustomPalette('FridaKahlo').get('blue') == (0.12549019607843137, 0.23529411764705882, 0.6666666666666666, 1)
    assert CustomPalette('ClaudeMonet').get('red') == (0.5215686274509804, 0.1411764705882353, 0.09803921568627451, 1)
    assert CustomPalette('BlueRidgePkwy').get('green') == (0.5490196078431373, 0.615686274509804, 0.3411764705882353, 1)


def test_custom_palette_falls_back_to_standard_values_when_color_missing():
    assert CustomPalette('FridaKahlo').get('purple') == (0.7, 0.2, 0.5, 1)
    assert CustomPalette('ClaudeMonet').get('pink') == (1, 0.5, 0.8, 1)
