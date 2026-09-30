"""Shared palette and helpers: classic green-phosphor terminal."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

BG = "#0a0f0a"        # tube glass
BORDER = "#1f3a1f"
DIM = "#2f6b2f"       # faded phosphor
MID = "#4fbf4f"
BRIGHT = "#7dff7d"    # hot phosphor
AMBER = "#ffb000"     # the one warm accent: the prompt symbol

FONT = "'JetBrains Mono','Fira Code','Cascadia Code',Consolas,'DejaVu Sans Mono',monospace"


def load_profile():
    return json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))


def esc(s):
    return escape(str(s))
