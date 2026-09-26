"""Render today's fun fact from fun-facts.txt as light and dark SVGs.

The "Generate Profile Images" workflow runs this and publishes the images to
the output branch, where the README loads them. The fact changes once a day
(UTC), stepping through the list in order.

Usage:  python3 scripts/fun_fact.py OUTPUT_DIR
"""

import datetime
import html
import sys
import textwrap
from pathlib import Path

FACTS_FILE = Path(__file__).resolve().parent.parent / "fun-facts.txt"
# Match GitHub's README font so the image blends in with the text around it
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
COLORS = {"light": "#1f2328", "dark": "#e6edf3"}
WRAP_AT = 72  # characters per line
LINE_H = 24
CHAR_W = 9  # generous per-character width at 16px bold; background is transparent


def load_facts():
    lines = FACTS_FILE.read_text(encoding="utf-8").splitlines()
    facts = [l.strip() for l in lines if l.strip() and not l.lstrip().startswith("#")]
    if not facts:
        sys.exit(f"No facts found in {FACTS_FILE}")
    return facts


def render(fact, color):
    lines = textwrap.wrap(fact, WRAP_AT)
    width = max(len(l) for l in lines) * CHAR_W
    height = len(lines) * LINE_H
    tspans = "".join(
        f'<tspan x="0" y="{(i + 1) * LINE_H - 7}">{html.escape(l)}</tspan>'
        for i, l in enumerate(lines)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(fact)}">'
        f'<text style="font: 600 16px {FONT}; fill: {color}">{tspans}</text></svg>\n'
    )


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    facts = load_facts()
    fact = facts[datetime.date.today().toordinal() % len(facts)]
    for theme, color in COLORS.items():
        (out / f"fun-fact-{theme}.svg").write_text(render(fact, color), encoding="utf-8")
    print(f"Today's fact: {fact}")


if __name__ == "__main__":
    main()
