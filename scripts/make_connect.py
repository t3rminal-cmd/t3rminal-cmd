"""Generate the "Connect with me" keycap icons.

Writes assets/key-<name>.svg: a glowing mechanical-keyboard keycap with a
neon line icon. The keys press themselves one after another in a loop, like
someone typing (images in a GitHub README can't react to hover, so the motion
plays on its own). The same image works on GitHub's light and dark themes.

Glyph shapes come from graffiti.py so they match the rest of the README.
Run from the repo root after editing:  python3 scripts/make_connect.py
"""

import html
from pathlib import Path

from graffiti import GLYPHS

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# name -> (label under the key, neon colour, press order)
KEYS = {
    "email": ("email", "#00d4ff", 0),
    "portfolio": ("portfolio", "#1bc830", 1),
    "instagram": ("instagram", "#ff2e88", 2),
}
LOOP = 3.6     # seconds for the whole row to "type" once
STAGGER = 0.4  # gap between one key and the next


def key(name, label, color, order):
    delay = order * STAGGER
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 228" width="200" height="228" role="img" aria-label="{html.escape(label)}">
  <defs>
    <linearGradient id="top" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2d3540"/><stop offset="1" stop-color="#171c23"/>
    </linearGradient>
    <linearGradient id="skirt" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a2028"/><stop offset="1" stop-color="#07090c"/>
    </linearGradient>
    <linearGradient id="rim" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".22"/><stop offset=".4" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="pool">
      <stop offset="0" stop-color="{color}" stop-opacity=".75"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>
    <filter id="neon" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .cap {{ animation: press {LOOP}s ease-in-out {delay:.2f}s infinite; }}
      @keyframes press {{
        0%, 6% {{ transform: translateY(0); }}
        11% {{ transform: translateY(10px); }}
        20%, 100% {{ transform: translateY(0); }}
      }}
      .pool {{ opacity: .35; animation: pool {LOOP}s ease-in-out {delay:.2f}s infinite; }}
      @keyframes pool {{ 0%, 6% {{ opacity: .35; }} 11% {{ opacity: 1; }} 30%, 100% {{ opacity: .35; }} }}
      .glyph {{ animation: flash {LOOP}s ease-in-out {delay:.2f}s infinite; }}
      @keyframes flash {{ 0%, 6% {{ opacity: .85; }} 11% {{ opacity: 1; }} 30%, 100% {{ opacity: .85; }} }}
      .lbl {{ font: 700 19px {MONO}; fill: {color}; }}
      @media (prefers-reduced-motion: reduce) {{ .cap, .pool, .glyph {{ animation: none; }} }}
    </style>
  </defs>
  <ellipse class="pool" cx="100" cy="176" rx="96" ry="26" fill="url(#pool)"/>
  <!-- switch housing: stays put while the cap moves -->
  <rect x="22" y="58" width="156" height="122" rx="24" fill="#05070a"/>
  <rect x="22" y="58" width="156" height="122" rx="24" fill="none" stroke="{color}" stroke-opacity=".55" stroke-width="2"/>
  <g class="cap">
    <rect x="22" y="22" width="156" height="148" rx="26" fill="url(#skirt)" stroke="#000" stroke-opacity=".6"/>
    <rect x="22" y="22" width="156" height="148" rx="26" fill="none" stroke="{color}" stroke-opacity=".35" stroke-width="1.5"/>
    <rect x="38" y="30" width="124" height="112" rx="20" fill="url(#top)"/>
    <rect x="38" y="30" width="124" height="112" rx="20" fill="url(#rim)"/>
    <rect x="38.5" y="30.5" width="123" height="111" rx="19.5" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
    <g class="glyph" filter="url(#neon)" fill="none" stroke="{color}" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round"
       transform="translate(100 86) scale(1.12) translate(-60 -60)">{GLYPHS[name].replace('fill="#fff"', f'fill="{color}"')}</g>
  </g>
  <text class="lbl" x="100" y="216" text-anchor="middle">{html.escape(label)}</text>
</svg>
"""


def main():
    for name, (label, color, order) in KEYS.items():
        path = ASSETS / f"key-{name}.svg"
        path.write_text(key(name, label, color, order), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
