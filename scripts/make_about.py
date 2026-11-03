"""Generate the "About me" card shown under the terminal.

Writes assets/about-dark.svg and assets/about-light.svg: one 1000px-wide
terminal window (the same width as the terminal intro and the project cards)
holding three paint-coloured tiles - Working on, Learning, Ask me about -
each with its 3D spray-paint icon, a marker-font label and chips.

Shared drawing code lives in graffiti.py.

Needs fonttools and brotli:  pip install fonttools brotli
Run from the repo root after editing:  python3 scripts/make_about.py
"""

import html
import random
from pathlib import Path

from graffiti import COLORS, GLYPHS, PAINT, THEMES, icon, load_font, overspray

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# ---------------------------------------------------------------- content
# Edit these to change the card. "headline" tiles show a big marker title,
# "chips" tiles show a row of tags (they wrap onto a second line if needed).
TILES = [
    {"key": "working", "label": "Working on", "seed": 6,
     "headline": "CaseVault",
     "lines": ["offline case files + local AI"],
     "badge": "v1.180 · shipping"},
    {"key": "learning", "label": "Learning", "seed": 7,
     "chips": ["HTML", "CSS", "JavaScript", "Python"]},
    {"key": "ask", "label": "Ask me about", "seed": 8,
     "chips": ["☕\ufe0f Coffee", "🏂 Snowboarding", "⚡\ufe0f C4 energy drinks"]},
]

W = 1000
PAD = 24
GAP = 16
TILE_W = (W - 2 * PAD - 2 * GAP) / 3
TILE_Y = 66
TILE_H = 212
H = TILE_Y + TILE_H + PAD
ICON = 76


def chip_width(text):
    # Emoji are about twice as wide as a monospace letter.
    text = text.replace("\ufe0f", "")
    wide = sum(1 for ch in text if ord(ch) > 0x2000)
    return (len(text) - wide) * 7.7 + wide * 17 + 22


def tile(i, t, colors, dark):
    light_c, mid_c, deep_c = COLORS[t["key"]]
    ink = light_c if dark else deep_c          # readable accent text on the tile
    x = PAD + i * (TILE_W + GAP)
    rng = random.Random(t["seed"] * 31)
    p = f"t{i}"

    # The tile: a soft wash of its paint colour, a glow behind the icon,
    # a little overspray, and a painted stripe along the top.
    body = f"""<g transform="translate({x:.1f},{TILE_Y})">
    <defs>
      <linearGradient id="{p}-wash" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{mid_c}" stop-opacity="{.20 if dark else .13}"/>
        <stop offset="1" stop-color="{mid_c}" stop-opacity="{.04 if dark else .03}"/>
      </linearGradient>
      <radialGradient id="{p}-glow">
        <stop offset="0" stop-color="{mid_c}" stop-opacity="{.45 if dark else .30}"/>
        <stop offset="1" stop-color="{mid_c}" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="{p}-stripe" x1="0" x2="1">
        <stop offset="0" stop-color="{light_c}"/>
        <stop offset=".5" stop-color="{mid_c}"/>
        <stop offset="1" stop-color="{deep_c}"/>
      </linearGradient>
      <clipPath id="{p}-clip"><rect width="{TILE_W:.1f}" height="{TILE_H}" rx="12"/></clipPath>
    </defs>
    <g clip-path="url(#{p}-clip)">
      <rect width="{TILE_W:.1f}" height="{TILE_H}" fill="{colors['bg']}"/>
      <rect width="{TILE_W:.1f}" height="{TILE_H}" fill="url(#{p}-wash)"/>
      <circle cx="58" cy="56" r="78" fill="url(#{p}-glow)"/>
      <g opacity=".55">{overspray(rng, TILE_W - 30, TILE_H - 26, 6, 46, 26, mid_c)}</g>
      <rect width="{TILE_W:.1f}" height="5" fill="url(#{p}-stripe)"/>
    </g>
    <rect x=".5" y=".5" width="{TILE_W - 1:.1f}" height="{TILE_H - 1}" rx="12" fill="none"
          stroke="{mid_c}" stroke-opacity="{.55 if dark else .45}"/>
    {icon("", COLORS[t["key"]], GLYPHS[t["key"]], random.Random(t["seed"]), bold=True, id_prefix=p + "i")
        .replace('width="120" height="120"', f'x="16" y="18" width="{ICON}" height="{ICON}"')}
    <text class="label" x="100" y="66" fill="{ink}" transform="rotate(-3 100 66)">{html.escape(t["label"])}</text>
"""

    if "headline" in t:
        body += f"""    <text class="head" x="20" y="134" fill="url(#{p}-stripe)" transform="rotate(-2 20 134)">{html.escape(t["headline"])}</text>
"""
        for j, line in enumerate(t["lines"]):
            body += f'    <text class="body" x="20" y="{164 + j * 19}">{html.escape(line)}</text>\n'
        bw = chip_width(t["badge"]) + 14
        body += f"""    <g transform="translate(20,{TILE_H - 36})">
      <rect width="{bw:.0f}" height="24" rx="12" fill="none" stroke="{ink}" stroke-width="1.5"/>
      <circle class="pulse" cx="14" cy="12" r="4" fill="{colors['tag']}"/>
      <text class="badge" x="25" y="16.5" fill="{ink}">{html.escape(t["badge"])}</text>
    </g>
"""
    else:
        cx, cy = 20, 112
        for c in t["chips"]:
            w = chip_width(c)
            if cx + w > TILE_W - 18:
                cx, cy = 20, cy + 38
            body += (f'    <g transform="translate({cx:.1f},{cy})">'
                     f'<rect width="{w:.0f}" height="28" rx="8" fill="{mid_c}" fill-opacity="{.16 if dark else .10}" '
                     f'stroke="{mid_c}" stroke-opacity=".8" stroke-width="1.3"/>'
                     f'<text class="chip" x="11" y="18.5" fill="{ink if not dark else colors["text"]}">{html.escape(c)}</text></g>\n')
            cx += w + 8
    return body + "  </g>"


def card(colors, marker, dark):
    label = ". ".join(
        f'{t["label"]}: ' + (f'{t["headline"]}, {" ".join(t["lines"])}' if "headline" in t else ", ".join(t["chips"]))
        for t in TILES)
    tiles = "\n  ".join(tile(i, t, colors, dark) for i, t in enumerate(TILES))
    dots = "".join(f'<circle cx="{24 + i * 18}" cy="22" r="5.5" fill="{c}"/>' for i, c in enumerate(PAINT))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(label)}">
  <defs>
    <style>
      @font-face {{ font-family: 'Marker'; src: url({marker}) format('woff2'); }}
      .bar {{ font: 500 13px {MONO}; fill: {colors['muted']}; }}
      .label {{ font: 25px 'Marker', 'Comic Sans MS', cursive; }}
      .head {{ font: 38px 'Marker', 'Comic Sans MS', cursive;
              stroke: {colors['outline']}; stroke-width: 5px; paint-order: stroke; stroke-linejoin: round; }}
      .body {{ font: 400 14px {MONO}; fill: {colors['text']}; }}
      .badge {{ font: 700 12px {MONO}; }}
      .chip {{ font: 600 13px {MONO}; }}
      .pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
      @keyframes pulse {{ 50% {{ opacity: .25 }} }}
      @media (prefers-reduced-motion: reduce) {{ .pulse {{ animation: none; }} }}
    </style>
    <linearGradient id="paint" x1="0" x2="1">
      <stop offset="0" stop-color="{PAINT[0]}"/>
      <stop offset=".5" stop-color="{PAINT[1]}"/>
      <stop offset="1" stop-color="{PAINT[2]}"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{colors['wall']}" stroke="{colors['border']}"/>
  <path d="M1,13 A12,12 0 0 1 13,1 H{W - 13} A12,12 0 0 1 {W - 1},13 V44 H1 Z" fill="{colors['bg']}"/>
  <rect x="1" y="43" width="{W - 2}" height="2" fill="url(#paint)"/>
  {dots}
  <text class="bar" x="{W / 2}" y="27" text-anchor="middle">~/about-me</text>
  {tiles}
</svg>
"""


def main():
    ASSETS.mkdir(exist_ok=True)
    text = "".join(t["label"] + t.get("headline", "") for t in TILES)
    marker, _ = load_font("PermanentMarker.woff2", text)
    for theme, colors in THEMES.items():
        path = ASSETS / f"about-{theme}.svg"
        path.write_text(card(colors, marker, theme == "dark"), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
