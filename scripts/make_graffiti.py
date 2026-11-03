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

from graffiti import COLORS, GLYPHS, PAINT, THEMES, drip, drip_shine, icon, load_font, overspray

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

    # Paint runs fall only from letters with a solid bottom edge, so a run
    # never starts in the gap of an A, N or W. Runs start inside the letter
    # (base_y - 9) so they look like they flow out of the paint.
    solid_bottom = set("BCDEGIJLOSUZ")
    # Only the bottom line drips: runs on the top line would hit the line below
    # and short ones read as accents (Ş, Ç). A mix of long runs and short sags.
    runs = []
    adv = spray_adv(LINE2, size1)
    x = (W - sum(adv)) / 2
    for ch, a in zip(LINE2, adv):
        if ch in solid_bottom and rng.random() < 0.6:
            cx = x + a * rng.uniform(0.35, 0.65)
            # Alternate long runs and short sags; lengths count from the baseline.
            below = rng.uniform(26, 34) if len(runs) % 2 == 0 else rng.uniform(13, 18)
            runs.append((cx, 232 - 9, 9 + below, rng.uniform(19, 23)))
        x += a
    drip_paths = "".join(f'<path d="{drip(*r)}"/>' for r in runs)
    shine = "".join(drip_shine(*r) for r in runs)
    mist_rng = random.Random(7)
    mist = "".join(overspray(mist_rng, cx, cy, 30, 70, 14, PAINT[k])
                   for k, cx in enumerate((300, 500, 700)) for cy in (120, 205))
    # The small tag sits just above the start of the first line.
    tag_x = (W - sum(spray_adv(LINE1, size1))) / 2 - 10

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(f'{TAG} {LINE1} {LINE2}. {SUB}')}">
  <defs>
    <style>
      @font-face {{ font-family: 'Spray'; src: url({spray}) format('woff2'); }}
      @font-face {{ font-family: 'Marker'; src: url({marker}) format('woff2'); }}
      .spray {{ font: {size1}px 'Spray', Impact, sans-serif; text-anchor: middle; }}
      .ink {{ fill: {colors['outline']}; stroke: {colors['outline']}; stroke-width: 6px; stroke-linejoin: round; }}
      .tag {{ font: 34px 'Marker', 'Comic Sans MS', cursive; fill: {colors['tag']}; }}
      .sub {{ font: 30px 'Marker', 'Comic Sans MS', cursive; fill: {colors['text']};
              text-anchor: middle; }}
    </style>
    <linearGradient id="dripPaint" x1="0" x2="{W}" y1="0" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{PAINT[0]}"/>
      <stop offset=".5" stop-color="{PAINT[1]}"/>
      <stop offset="1" stop-color="{PAINT[2]}"/>
    </linearGradient>
    <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
    <filter id="shadow" x="-5%" y="-10%" width="110%" height="140%">
      <feDropShadow dx="0" dy="5" stdDeviation="3" flood-color="#000" flood-opacity=".35"/>
    </filter>
    <!-- Gloss on the upper half of each line, shade on the lower edge: gives the paint depth. -->
    <linearGradient id="gloss1" x1="0" x2="0" y1="96" y2="150" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".75" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/>
    </linearGradient>
    <linearGradient id="gloss2" x1="0" x2="0" y1="178" y2="232" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff" stop-opacity=".6"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".75" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{colors['wall']}" stroke="{colors['border']}"/>
  <!-- Soft colour glow and overspray behind the paint -->
  <g fill="url(#dripPaint)" opacity=".45" filter="url(#glow)">
    <text class="spray" x="{W / 2}" y="150">{LINE1}</text>
    <text class="spray" x="{W / 2}" y="232">{html.escape(LINE2)}</text>
  </g>
  {mist}
  <!-- Outlines of letters and runs first, then all fills on top: one silhouette, no seams. -->
  <g class="ink" filter="url(#shadow)">
    <text class="spray" x="{W / 2}" y="150">{LINE1}</text>
    <text class="spray" x="{W / 2}" y="232">{html.escape(LINE2)}</text>
    {drip_paths}
  </g>
  <g fill="url(#dripPaint)">
    {drip_paths}
    <text class="spray" x="{W / 2}" y="150">{LINE1}</text>
    <text class="spray" x="{W / 2}" y="232">{html.escape(LINE2)}</text>
  </g>
  <text class="spray" x="{W / 2}" y="150" fill="url(#gloss1)">{LINE1}</text>
  <text class="spray" x="{W / 2}" y="232" fill="url(#gloss2)">{html.escape(LINE2)}</text>
  {shine}
  <text class="tag" x="{tag_x:.0f}" y="72" transform="rotate(-6 {tag_x:.0f} 72)">{TAG}</text>
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
