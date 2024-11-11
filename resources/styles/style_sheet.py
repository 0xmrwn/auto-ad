"""Defines styling constants for the UI"""

# Colors (using CustomTkinter compatible color format)
COLORS = {
    "PRIMARY": "#2c3e50",
    "SECONDARY": "#34495e",
    "ACCENT": "#3498db",
    "SUCCESS": "#27ae60",
    "ERROR": "#e74c3c",
    "BACKGROUND": "transparent",
    "TEXT": "#2c3e50",
    "WARNING": "#f39c12",
    "INFO": "#3498db",
}

# Fonts (using CustomTkinter's font format)
FONTS = {
    "HEADER": ("Helvetica", 24, "bold"),
    "NORMAL": ("Helvetica", 12),
    "BOLD": ("Helvetica", 12, "bold"),
}

# Padding and spacing
PADDING = {
    "DEFAULT": (20, 20),
    "SECTION": (30, 30),
}

# Widget-specific configurations
BUTTON_CONFIG = {
    "corner_radius": 8,
    "border_width": 0,
    "font": FONTS["NORMAL"],
}

TEXTBOX_CONFIG = {
    "corner_radius": 8,
    "border_width": 1,
    "font": FONTS["NORMAL"],
}

FRAME_CONFIG = {
    "corner_radius": 10,
    "border_width": 1,
}
