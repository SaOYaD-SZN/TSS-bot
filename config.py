"""
ᏖᏕᏕ — shared config: bot name, colour palette, emoji set.
Edit values here to re-theme the entire bot in one place.
"""

import os

BOT_NAME = "ᏖᏕᏕ"
BOT_TAGLINE = "your favorite all-in-one cutie 🎀"

# Pastel colour palette (used as embed colours, one per category)
COLORS = {
    "primary":    0xFFC1E3,  # soft pink — default / general
    "moderation": 0xFFADAD,  # soft red
    "economy":    0xB5EAD7,  # soft mint
    "fun":        0xFFE08A,  # soft yellow
    "utility":    0xA7D8FF,  # soft sky blue
    "study":      0xCBAACB,  # soft lavender
    "tickets":    0x9DE3D0,  # soft teal
    "error":      0xFF8FA3,  # soft coral (errors, still on theme)
}

EMOJI = {
    "sparkle": "✨",
    "ribbon": "🎀",
    "letter": "💌",
    "flower": "🌸",
    "bear": "🧸",
    "book": "📚",
    "star": "💫",
    "boba": "🧋",
    "check": "🩷",
    "cross": "🤍",
    "coin": "🪙",
    "shop": "🛍️",
    "ticket": "🎫",
    "lock": "🔒",
    "unlock": "🔓",
    "clock": "⏰",
    "warn": "⚠️",
    "ban": "🔨",
    "mute": "🔇",
}

FOOTER_TEXT = f"{BOT_NAME} {EMOJI['sparkle']} {BOT_TAGLINE}"

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tss.db")
