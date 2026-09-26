"""Render today's fun fact from fun-facts.txt as a graffiti-style card.

Writes fun-fact-light.svg and fun-fact-dark.svg. The "Generate Profile Images"
workflow runs this and publishes the images to the output branch, where the
README loads them. The fact changes once a day (UTC), stepping through the
list in order, and the paint splat behind the badge changes with it.

Usage:  python3 scripts/fun_fact.py OUTPUT_DIR
"""

import datetime
import html
import random
import sys
import textwrap
from pathlib import Path

from graffiti import COLORS, GLYPHS, THEMES, icon, load_font

FACTS_FILE = Path(__file__).resolve().parent.parent / "fun-facts.txt"
# The fact itself uses GitHub's README font, drawn by the viewer's browser.
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
TITLE = "fun fact of the day"

W = 760
TEXT_X = 150      # text starts right of the badge
WRAP_AT = 52      # characters per line at 19px bold, fits W - TEXT_X with room to spare
LINE_H = 28
BADGE = 110


def load_facts():
    lines = FACTS_FILE.read_text(encoding="utf-8").splitlines()
    facts = [l.strip() for l in lines if l.strip() and not l.lstrip().startswith("#")]
    if not facts:
        sys.exit(f"No facts found in {FACTS_FILE}")
    return facts


def marker_face(text):
    """@font-face for the embedded marker font, or "" if fonttools is missing
    (the card then falls back to a local handwriting font)."""
    try:
        uri, _ = load_font("PermanentMarker.woff2", text)
    except ImportError:
        print("fonttools not installed - using a fallback font for the title", file=sys.stderr)
        return ""
    return f"@font-face {{ font-family: 'Marker'; src: url({uri}) format('woff2'); }}"


def render(fact, number, total, colors, face, badge):
    lines = textwrap.wrap(fact, WRAP_AT)
    first_y = 82
    height = max(BADGE + 40, first_y + (len(lines) - 1) * LINE_H + 52)
    footer = f"fact #{number} of {total} · a new one every day"
    tspans = "".join(
        f'<tspan x="{TEXT_X}" y="{first_y + i * LINE_H}">{html.escape(l)}</tspan>'
        for i, l in enumerate(lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Fun fact of the day: {html.escape(fact)}">
  <style>
    {face}
    .title {{ font: 26px 'Marker', 'Comic Sans MS', cursive; fill: {colors['tag']}; }}
    .fact {{ font: 600 19px {FONT}; fill: {colors['text']}; }}
    .foot {{ font: 16px 'Marker', 'Comic Sans MS', cursive; fill: {colors['muted']}; }}
  </style>
  <rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="12" fill="{colors['wall']}" stroke="{colors['border']}"/>
  {badge.replace('width="120" height="120"', f'x="22" y="{(height - BADGE) / 2:.0f}" width="{BADGE}" height="{BADGE}"')}
  <text class="title" x="{TEXT_X}" y="44" transform="rotate(-3 {TEXT_X} 44)">{TITLE}</text>
  <text class="fact">{tspans}</text>
  <text class="foot" x="{TEXT_X}" y="{height - 18}">{html.escape(footer)}</text>
</svg>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    facts = load_facts()
    day = datetime.date.today().toordinal()
    index = day % len(facts)
    fact = facts[index]

    face = marker_face(TITLE + "fact #0123456789 of · a new one every day")
    # A nested <svg>; render() positions it on the card.
    badge = icon("", COLORS["bolt"], GLYPHS["bolt"], random.Random(day), id_prefix="badge")
    for theme, colors in THEMES.items():
        svg = render(fact, index + 1, len(facts), colors, face, badge)
        (out / f"fun-fact-{theme}.svg").write_text(svg, encoding="utf-8")
    print(f"Today's fact ({index + 1}/{len(facts)}): {fact}")


if __name__ == "__main__":
    main()
