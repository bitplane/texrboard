"""
TextBoard themes.

Defines custom themes that match TensorBoard's visual design.
"""

from textual.theme import Theme


# TensorBoard-inspired light theme
# TODO: Research exact colors from TensorBoard source/screenshots
TENSORBOARD_LIGHT = Theme(
    name="tensorboard_light",
    primary="#FF6F00",  # TensorBoard orange (placeholder)
    secondary="#1976D2",  # Blue accents (placeholder)
    accent="#4CAF50",  # Green accents (placeholder)
    warning="#FF9800",  # Orange warnings
    error="#F44336",  # Red errors
    success="#4CAF50",  # Green success
    foreground="#212121",  # Dark text
    background="#FAFAFA",  # Light gray background
    surface="#FFFFFF",  # White panels
    panel="#F5F5F5",  # Light gray panels
    dark=False,
)


def get_default_theme() -> Theme:
    """Get the default theme for TextBoard."""
    return TENSORBOARD_LIGHT


def register_themes(app):
    """Register all available themes with the app."""
    app.register_theme(TENSORBOARD_LIGHT)
