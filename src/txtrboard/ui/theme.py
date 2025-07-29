"""
TextBoard themes.

Defines custom themes that match TensorBoard's visual design.
"""

from textual.theme import Theme


# TensorBoard-inspired light theme
TENSORBOARD_LIGHT = Theme(
    name="tensorboard_light",
    primary="#FF6F00",  # TensorBoard orange
    secondary="#1976D2",  # Blue accents
    accent="#4CAF50",  # Green accents
    warning="#FF9800",  # Orange warnings
    error="#F44336",  # Red errors
    success="#4CAF50",  # Green success
    foreground="#212121",  # Dark text
    background="#FAFAFA",  # Light gray background
    surface="#FFFFFF",  # White panels
    panel="#F5F5F5",  # Light gray panels
    dark=False,
    variables={
        "panel-light": "#FFFFFF",
        "panel-dark": "#F5F5F5",
        "panel-text": "#212121",
    },
)

# TensorBoard-inspired dark theme
TENSORBOARD_DARK = Theme(
    name="tensorboard_dark",
    primary="#FF6F00",  # TensorBoard orange
    secondary="#42A5F5",  # Lighter blue for dark mode
    accent="#66BB6A",  # Lighter green for dark mode
    warning="#FFB74D",  # Lighter orange warnings
    error="#EF5350",  # Lighter red errors
    success="#66BB6A",  # Lighter green success
    foreground="#E0E0E0",  # Light text
    background="#121212",  # Dark background
    surface="#1E1E1E",  # Dark panels
    panel="#2D2D2D",  # Lighter dark panels
    dark=True,
    variables={
        "panel-light": "#2D2D2D",
        "panel-dark": "#1E1E1E",
        "panel-text": "#E0E0E0",
    },
)


def get_default_theme() -> Theme:
    """Get the default theme for TextBoard."""
    return TENSORBOARD_DARK


def register_themes(app):
    """Register all available themes with the app."""
    app.register_theme(TENSORBOARD_LIGHT)
    app.register_theme(TENSORBOARD_DARK)
