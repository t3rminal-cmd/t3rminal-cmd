"""Generate the graffiti-style README art.

Writes:
  assets/headline-dark.svg, assets/headline-light.svg  - spray-painted intro
  assets/icon-*.svg  - paint-splat icons (connect links and the about-me table)

The headline embeds only the letters it uses from two free fonts in
scripts/fonts (Rubik Spray Paint, SIL OFL 1.1; Permanent Marker, Apache 2.0),
because images in a GitHub README cannot load web fonts. Shared drawing code
lives in graffiti.py.

Needs fonttools and brotli:  pip install fonttools brotli
Run from the repo root after editing:  python3 scripts/make_graffiti.py
"""

import html
import random
from pathlib import Path

from graffiti import COLORS, GLYPHS, PAINT, ROUGH, THEMES, drip, icon, load_font

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- text
TAG = "an amateur"
LINE1 = "WEB DESIGNER"
LINE2 = "& DEVELOPER"
SUB = "veteran · runner · foodie"

# Icon name -> (random seed, shown small?). Changing a seed reshapes its splat.
ICONS = {
    "email": (3, False),
    "portfolio": (4, False),
    "instagram": (5, False),
    "working": (6, True),
    "learning": (7, True),
    "ask": (8, True),
}


# ---------------------------------------------------------------- headline
def headline(colors, spray, spray_adv, marker):
    W, H = 1000, 320
    size1 = 74
    rng = random.Random(42)

    # Place drips under a few letters of each spray line, using real glyph widths.
    drips = []
    for line, base_y in ((LINE1, 150), (LINE2, 232)):
        adv = spray_adv(line, size1)
        x = (W - sum(adv)) / 2
        for ch, a in zip(line, adv):
            if ch.isalpha() and rng.random() < 0.3:
                cx = x + a * rng.uniform(0.35, 0.65)
                drips.append(drip(cx, base_y - 14, rng.uniform(22, 44), rng.uniform(10, 14)))
            x += a
    drip_paths = "".join(f'<path d="{d}"/>' for d in drips)
    # The small tag sits just above the start of the first line.
    tag_x = (W - sum(spray_adv(LINE1, size1))) / 2 - 10

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(f'{TAG} {LINE1} {LINE2}. {SUB}')}">
  <defs>
    <style>
      @font-face {{ font-family: 'Spray'; src: url({spray}) format('woff2'); }}
      @font-face {{ font-family: 'Marker'; src: url({marker}) format('woff2'); }}
      .spray {{ font: {size1}px 'Spray', Impact, sans-serif; text-anchor: middle;
               fill: url(#paint); stroke: {colors['outline']}; stroke-width: 6px;
               paint-order: stroke; stroke-linejoin: round; }}
      .tag {{ font: 34px 'Marker', 'Comic Sans MS', cursive; fill: {colors['tag']}; }}
      .sub {{ font: 30px 'Marker', 'Comic Sans MS', cursive; fill: {colors['text']};
              text-anchor: middle; }}
    </style>
    <linearGradient id="paint" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{PAINT[0]}"/>
      <stop offset=".5" stop-color="{PAINT[1]}"/>
      <stop offset="1" stop-color="{PAINT[2]}"/>
    </linearGradient>
    <linearGradient id="dripPaint" x1="0" x2="{W}" y1="0" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{PAINT[0]}"/>
      <stop offset=".5" stop-color="{PAINT[1]}"/>
      <stop offset="1" stop-color="{PAINT[2]}"/>
    </linearGradient>
    {ROUGH}
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{colors['wall']}" stroke="{colors['border']}"/>
  <g fill="url(#dripPaint)" stroke="{colors['outline']}" stroke-width="3" filter="url(#rough)">{drip_paths}</g>
  <text class="tag" x="{tag_x:.0f}" y="72" transform="rotate(-6 {tag_x:.0f} 72)">{TAG}</text>
  <text class="spray" x="{W / 2}" y="150">{LINE1}</text>
  <text class="spray" x="{W / 2}" y="232">{html.escape(LINE2)}</text>
  <text class="sub" x="{W / 2}" y="296" transform="rotate(-1.5 {W / 2} 296)">{SUB}</text>
</svg>
"""


def main():
    ASSETS.mkdir(exist_ok=True)
    spray, spray_adv = load_font("RubikSprayPaint.woff2", LINE1 + LINE2)
    marker, _ = load_font("PermanentMarker.woff2", TAG + SUB)

    for name, colors in THEMES.items():
        path = ASSETS / f"headline-{name}.svg"
        path.write_text(headline(colors, spray, spray_adv, marker))
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")

    for name, (seed, small) in ICONS.items():
        path = ASSETS / f"icon-{name}.svg"
        path.write_text(icon(name, COLORS[name], GLYPHS[name], random.Random(seed), bold=small))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
