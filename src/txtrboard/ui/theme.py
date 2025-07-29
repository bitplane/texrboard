"""
TextBoard themes.

Defines custom themes that match TensorBoard's visual design.
"""

from textual.theme import Theme


# TensorBoard-inspired theme with orange background
TENSORBOARD_LIGHT = Theme(
    name="tensorboard_light",
    primary="#FF6F00",  # TensorBoard orange
    secondary="#1976D2",  # Blue accents
    accent="#4CAF50",  # Green accents
    warning="#FF9800",  # Orange warnings
    error="#F44336",  # Red errors
    success="#4CAF50",  # Green success
    foreground="#FFFFFF",  # White text on orange background
    background="#FF6F00",  # Orange background
    surface="#FF6F00",  # Orange panels
    panel="#FF6F00",  # Orange panels
    dark=False,
)


def get_default_theme() -> Theme:
    """Get the default theme for TextBoard."""
    return TENSORBOARD_LIGHT


def register_themes(app):
    """Register all available themes with the app."""
    app.register_theme(TENSORBOARD_LIGHT)
