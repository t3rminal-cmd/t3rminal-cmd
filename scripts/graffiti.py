"""Shared drawing helpers for the graffiti-style README art.

Used by make_graffiti.py (headline and icons) and fun_fact.py (daily card).
"""

import base64
import io
import math
from pathlib import Path

FONTS = Path(__file__).resolve().parent / "fonts"

PAINT = ["#1bc830", "#00d4ff", "#ff2e88"]  # spray gradient, left to right

THEMES = {
    "dark": {"bg": "#0d1117", "wall": "#161b22", "border": "#30363d",
             "outline": "#0d1117", "tag": "#1bc830", "text": "#e6edf3", "muted": "#8b949e"},
    "light": {"bg": "#f6f8fa", "wall": "#ffffff", "border": "#d0d7de",
              "outline": "#1f2328", "tag": "#1a7f37", "text": "#1f2328", "muted": "#59636e"},
}

# Rough edge for paint shapes. Applied to the paint only, never to text.
ROUGH = """<filter id="rough" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
    <feDisplacementMap in="SourceGraphic" scale="3.5"/>
  </filter>"""


# ---------------------------------------------------------------- fonts
def load_font(file_name, text):
    """Returns (subset woff2 as a data URI, advance-width function).

    Images in a GitHub README cannot load web fonts, so the letters are
    embedded. Needs fonttools and brotli (pip install fonttools brotli).
    """
    from fontTools.subset import Options, Subsetter
    from fontTools.ttLib import TTFont

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
    """A paint run: flares out of the paint above, thins to a neck, and ends
    in a heavy teardrop. `top` should sit inside the painted shape so the run
    looks like it flows out of it rather than hanging off its edge."""
    w = width / 2
    neck = w * 0.68
    bulb = w * 1.0
    flare = w * 2.1
    cy = top + length - bulb                      # centre of the drop
    ny = cy - (bulb ** 2 - neck ** 2) ** 0.5      # where the neck meets the drop
    return (f"M{x - flare:.1f},{top:.1f} "
            f"C{x - w * 0.7:.1f},{top + 2:.1f} {x - neck:.1f},{top + (ny - top) * 0.3:.1f} {x - neck:.1f},{ny:.1f} "
            f"A{bulb:.1f},{bulb:.1f} 0 1 0 {x + neck:.1f},{ny:.1f} "
            f"C{x + neck:.1f},{top + (ny - top) * 0.3:.1f} {x + w * 0.7:.1f},{top + 2:.1f} {x + flare:.1f},{top:.1f} Z")


def drip_shine(x, top, length, width):
    """Wet highlights for a drip: a thin streak down the neck and a glint on the drop."""
    w = width / 2
    bulb = w * 1.0
    cy = top + length - bulb
    return (f'<path d="M{x - w * 0.22:.1f},{top + length * 0.25:.1f} V{cy - bulb * 0.9:.1f}" '
            f'stroke="#fff" stroke-width="{max(w * 0.28, 1):.1f}" stroke-linecap="round" opacity=".45" fill="none"/>'
            f'<ellipse cx="{x - bulb * 0.35:.1f}" cy="{cy - bulb * 0.3:.1f}" rx="{bulb * 0.28:.1f}" '
            f'ry="{bulb * 0.4:.1f}" fill="#fff" opacity=".7"/>')


def overspray(rng, cx, cy, r_min, r_max, count, color):
    dots = []
    for _ in range(count):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(r_min, r_max)
        dots.append(f'<circle cx="{cx + d * math.cos(a):.1f}" cy="{cy + d * math.sin(a):.1f}" '
                    f'r="{rng.uniform(0.6, 2.2):.1f}" fill="{color}" opacity="{rng.uniform(.35, .9):.2f}"/>')
    return "".join(dots)


# ---------------------------------------------------------------- icons
def icon(label, paint, glyph, rng, bold=False, id_prefix="i"):
    """A 3D spray-paint icon in a 120x120 box: a glossy paint blob with a soft
    colour glow, overspray, a drop shadow, glossy paint runs, and a white glyph
    with a black outline. `paint` is (light, mid, dark).
    Pass bold=True for icons shown small (about 40px or less).

    The blob and its runs are drawn as one shape: every outline first, then
    every fill on top, so no line shows where a run leaves the blob. All ids
    carry id_prefix because the fun fact card nests an icon inline."""
    outer, inner = (14, 7.5) if bold else (12, 6)
    p = id_prefix
    blob = splat(rng, 60, 54, 38, bumps=12, wobble=0.1)
    runs = [(x, 76, rng.uniform(24, 34), rng.uniform(8, 10)) for x in sorted(rng.sample([42, 52, 64, 74], 2))]
    drips = "".join(f'<path d="{drip(*r)}"/>' for r in runs)
    shine = "".join(drip_shine(*r) for r in runs)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-label="{label}">
  <defs>
    <radialGradient id="{p}-f" cx=".38" cy=".3" r=".75">
      <stop offset="0" stop-color="{paint[0]}"/>
      <stop offset=".5" stop-color="{paint[1]}"/>
      <stop offset="1" stop-color="{paint[2]}"/>
    </radialGradient>
    <linearGradient id="{p}-run" x1="0" x2="0" y1="80" y2="114" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{paint[2]}"/>
      <stop offset=".7" stop-color="{paint[1]}"/>
      <stop offset="1" stop-color="{paint[2]}"/>
    </linearGradient>
    <radialGradient id="{p}-halo">
      <stop offset=".55" stop-color="{paint[1]}" stop-opacity=".45"/>
      <stop offset="1" stop-color="{paint[1]}" stop-opacity="0"/>
    </radialGradient>
    <filter id="{p}-soft"><feGaussianBlur stdDeviation="1.2"/></filter>
    <filter id="{p}-sh" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="3" stdDeviation="2" flood-opacity=".3"/>
    </filter>
  </defs>
  <circle cx="60" cy="56" r="54" fill="url(#{p}-halo)"/>
  {overspray(rng, 60, 54, 40, 56, 30, paint[1])}
  <g filter="url(#{p}-sh)">
    <g fill="#111" stroke="#111" stroke-width="6" stroke-linejoin="round"><path d="{blob}"/>{drips}</g>
    <g fill="url(#{p}-run)">{drips}</g>
    <path d="{blob}" fill="url(#{p}-f)"/>
  </g>
  <ellipse cx="46" cy="32" rx="14" ry="7" fill="#fff" opacity=".45" filter="url(#{p}-soft)" transform="rotate(-25 46 32)"/>
  {shine}
  <g fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate(60 56) scale(.9) translate(-60 -58)">
    <g stroke="#111" stroke-width="{outer}">{glyph}</g>
    <g stroke="#fff" stroke-width="{inner}">{glyph}</g>
  </g>
</svg>
"""


# Glyphs drawn in the 120x120 icon box. Shapes that should be solid white
# carry their own fill="#fff".
GLYPHS = {
    "email": '<rect x="34" y="42" width="52" height="38" rx="5"/>'
             '<path d="M36,46 L60,64 L84,46"/>',
    "portfolio": '<rect x="30" y="38" width="60" height="44" rx="6"/>'
                 '<path d="M30,50 H90"/>'
                 '<path d="M50,62 L43,69 L50,76 M70,62 L77,69 L70,76"/>',
    "instagram": '<rect x="36" y="36" width="48" height="48" rx="14"/>'
                 '<circle cx="60" cy="60" r="11"/>'
                 '<circle cx="74.5" cy="45.5" r="1.5"/>',
    "working": '<path d="M47,40 L30,58 L47,76 M73,40 L90,58 L73,76 M65,34 L55,82"/>',
    "learning": '<path d="M50,70 V64 A17,17 0 1 1 70,64 V70 Z"/>'
                '<path d="M52,80 H68"/>',
    "ask": '<path d="M38,38 H82 A8,8 0 0 1 90,46 V64 A8,8 0 0 1 82,72 H60 L46,84 V72 H38 '
           'A8,8 0 0 1 30,64 V46 A8,8 0 0 1 38,38 Z"/>',
    "bolt": '<path fill="#fff" d="M68,28 L40,64 H57 L50,92 L80,52 H63 Z"/>',
}

# (light, mid, dark) paint for each icon
COLORS = {
    "email": ("#ff7ab8", "#ff2e88", "#b3005a"),
    "portfolio": ("#7dff8e", "#1bc830", "#0b7a1c"),
    "instagram": ("#feda75", "#d62976", "#6a1b9a"),
    "working": ("#8ff3ff", "#00b8e6", "#00607a"),
    "learning": ("#fff38a", "#ffc400", "#a86b00"),
    "ask": ("#dcb0ff", "#9b3dff", "#521799"),
    "bolt": ("#ffc58a", "#ff6a00", "#9c3300"),
}
