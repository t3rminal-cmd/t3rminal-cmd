"""Generate the graffiti-style README art.

Writes:
  assets/headline-dark.svg, assets/headline-light.svg  - spray-painted intro
  assets/icon-email.svg, icon-portfolio.svg, icon-instagram.svg - paint-splat icons

The headline embeds only the letters it uses from two free fonts in
scripts/fonts (Rubik Spray Paint, SIL OFL 1.1; Permanent Marker, Apache 2.0),
because images in a GitHub README cannot load web fonts.

Needs fonttools and brotli:  pip install fonttools brotli
Run from the repo root after editing:  python3 scripts/make_graffiti.py
"""

import base64
import html
import io
import math
import random
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- text
TAG = "an amateur"
LINE1 = "WEB DESIGNER"
LINE2 = "& DEVELOPER"
SUB = "veteran · runner · foodie"

THEMES = {
    "dark": {"bg": "#0d1117", "wall": "#161b22", "border": "#30363d",
             "outline": "#0d1117", "tag": "#1bc830", "sub": "#e6edf3"},
    "light": {"bg": "#f6f8fa", "wall": "#ffffff", "border": "#d0d7de",
              "outline": "#1f2328", "tag": "#1a7f37", "sub": "#1f2328"},
}
PAINT = ["#1bc830", "#00d4ff", "#ff2e88"]  # spray gradient, left to right


# ---------------------------------------------------------------- fonts
def load_font(file_name, text):
    """Returns (subset woff2 as a data URI, advance-width function)."""
    path = FONTS / file_name
    font = TTFont(path)
    opts = Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    sub = Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    uri = "data:font/woff2;base64," + base64.b64encode(buf.getvalue()).decode()

    metrics = TTFont(path)
    upm = metrics["head"].unitsPerEm
    cmap = metrics.getBestCmap()
    hmtx = metrics["hmtx"]

    def advances(s, size):
        return [hmtx[cmap[ord(ch)]][0] * size / upm for ch in s]

    return uri, advances


# ---------------------------------------------------------------- shapes
def smooth_closed(points):
    """Closed Catmull-Rom spline through the points, as an SVG path."""
    n = len(points)
    d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = (points[(i + k) % n] for k in (-1, 0, 1, 2))
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + "Z"


def splat(rng, cx, cy, r, bumps=14, wobble=0.14):
    pts = []
    for i in range(bumps):
        a = 2 * math.pi * i / bumps + rng.uniform(-0.12, 0.12)
        rr = r * (1 + rng.uniform(-wobble, wobble))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return smooth_closed(pts)


def drip(x, top, length, width):
    """A paint drip: a narrow column with a round drop at the end."""
    w = width / 2
    b = top + length
    return (f"M{x - w:.1f},{top:.1f} L{x - w * 0.7:.1f},{b:.1f} "
            f"A{w * 1.1:.1f},{w * 1.1:.1f} 0 1 0 {x + w * 0.7:.1f},{b:.1f} "
            f"L{x + w:.1f},{top:.1f} Z")


def overspray(rng, cx, cy, r_min, r_max, count, color):
    dots = []
    for _ in range(count):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(r_min, r_max)
        dots.append(f'<circle cx="{cx + d * math.cos(a):.1f}" cy="{cy + d * math.sin(a):.1f}" '
                    f'r="{rng.uniform(0.6, 2.2):.1f}" fill="{color}" opacity="{rng.uniform(.35, .9):.2f}"/>')
    return "".join(dots)


# Rough edge for paint shapes. Applied to the paint only, never to text.
ROUGH = """<filter id="rough" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
    <feDisplacementMap in="SourceGraphic" scale="3.5"/>
  </filter>"""


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
      .sub {{ font: 30px 'Marker', 'Comic Sans MS', cursive; fill: {colors['sub']};
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


# ---------------------------------------------------------------- icons
ICONS = {
    # name: (paint colors light->dark, glyph svg drawn in a 120x120 box)
    "email": (("#ff7ab8", "#ff2e88", "#b3005a"),
              '<rect x="34" y="42" width="52" height="38" rx="5"/>'
              '<path d="M36,46 L60,64 L84,46"/>'),
    "portfolio": (("#7dff8e", "#1bc830", "#0b7a1c"),
                  '<rect x="30" y="38" width="60" height="44" rx="6"/>'
                  '<path d="M30,50 H90"/>'
                  '<path d="M50,62 L43,69 L50,76 M70,62 L77,69 L70,76"/>'),
    "instagram": (("#feda75", "#d62976", "#6a1b9a"),
                  '<rect x="36" y="36" width="48" height="48" rx="14"/>'
                  '<circle cx="60" cy="60" r="11"/>'
                  '<circle cx="74.5" cy="45.5" r="1.5"/>'),
}


def icon(name, paint, glyph, seed):
    rng = random.Random(seed)
    blob = splat(rng, 60, 56, 40)
    drips = "".join(
        f'<path d="{drip(x, 84, rng.uniform(18, 26), rng.uniform(6, 8))}"/>'
        for x in rng.sample([42, 52, 66, 76], 2)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-label="{name}">
  <defs>
    <radialGradient id="g" cx=".35" cy=".3" r=".8">
      <stop offset="0" stop-color="{paint[0]}"/>
      <stop offset=".55" stop-color="{paint[1]}"/>
      <stop offset="1" stop-color="{paint[2]}"/>
    </radialGradient>
    {ROUGH}
  </defs>
  {overspray(rng, 60, 56, 42, 54, 38, paint[1])}
  <g filter="url(#rough)" fill="url(#g)" stroke="#111" stroke-width="3.5" stroke-linejoin="round">
    <path d="{blob}"/>
    {drips}
  </g>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round">
    <g stroke="#111" stroke-width="11">{glyph}</g>
    <g stroke="#fff" stroke-width="5.5">{glyph}</g>
  </g>
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

    for seed, (name, (paint, glyph)) in enumerate(ICONS.items(), start=3):
        path = ASSETS / f"icon-{name}.svg"
        path.write_text(icon(name, paint, glyph, seed))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
