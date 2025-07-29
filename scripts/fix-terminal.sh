#!/bin/bash
# Fix terminal state after TUI apps mess it up

# ANSI escape sequences with descriptive names
DISABLE_MOUSE_TRACKING="\033[?1000l"
DISABLE_MOUSE_BUTTON_TRACKING="\033[?1002l"
DISABLE_MOUSE_ANY_EVENT_TRACKING="\033[?1003l"
DISABLE_MOUSE_SGR_MODE="\033[?1006l"
DISABLE_MOUSE_URXVT_MODE="\033[?1015l"
SHOW_CURSOR="\033[?25h"
RESET_COLORS="\033[0m"
DISABLE_ALT_SCREEN="\033[?1049l"
CLEAR_SCROLLBACK="\033[3J"
CLEAR_SCREEN="\033[2J"
HOME_CURSOR="\033[H"

# Combine all sequences and emit as first line for preview passthrough
printf "%s%s%s%s%s%s%s%s%s%s%s" \
    "$DISABLE_MOUSE_TRACKING" \
    "$DISABLE_MOUSE_BUTTON_TRACKING" \
    "$DISABLE_MOUSE_ANY_EVENT_TRACKING" \
    "$DISABLE_MOUSE_SGR_MODE" \
    "$DISABLE_MOUSE_URXVT_MODE" \
    "$SHOW_CURSOR" \
    "$RESET_COLORS" \
    "$DISABLE_ALT_SCREEN" \
    "$CLEAR_SCROLLBACK" \
    "$CLEAR_SCREEN" \
    "$HOME_CURSOR"

echo "Terminal state reset complete"