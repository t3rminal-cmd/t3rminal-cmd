"""Generate the "Connect with me" icons.

Writes assets/connect-<name>-light.svg and assets/connect-<name>-dark.svg:
minimal line icons in a thin ring. A short arc in the icon's accent colour
slowly travels around the ring (images in a GitHub README can't react to
hover, so the motion plays on its own; it stops for reduced motion).

Run from the repo root after editing:  python3 scripts/make_connect.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Line glyphs on a 24x24 grid, drawn with a 1.6 stroke.
GLYPHS = {
    "email": '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3.8 7 12 13l8.2-6"/>',
    "portfolio": '<rect x="3" y="4.5" width="18" height="15" rx="2.5"/><path d="M3 8.5h18"/>'
                 '<path d="m10 12-2.2 2.2L10 16.4M14 12l2.2 2.2-2.2 2.2"/>',
    "instagram": '<rect x="4" y="4" width="16" height="16" rx="4.5"/><circle cx="12" cy="12" r="3.6"/>'
                 '<circle cx="16.6" cy="7.4" r=".5" fill="currentColor"/>',
}
# name -> (accent colour, seconds per lap, start angle)
ACCENTS = {
    "email": ("#00d4ff", 9, 0),
    "portfolio": ("#1bc830", 9, 120),
    "instagram": ("#ff2e88", 9, 240),
}
THEMES = {
    "dark": {"ink": "#e6edf3", "ring": "#30363d"},
    "light": {"ink": "#1f2328", "ring": "#d0d7de"},
}


def icon(name, colors):
    accent, lap, start = ACCENTS[name]
    r = 44
    circ = 2 * 3.14159 * r
    arc = circ * 0.18
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img" aria-label="{name}">
  <style>
    .spin {{ transform-origin: 48px 48px; animation: spin {lap}s linear infinite; }}
    @keyframes spin {{ from {{ transform: rotate({start}deg); }} to {{ transform: rotate({start + 360}deg); }} }}
    @media (prefers-reduced-motion: reduce) {{ .spin {{ animation: none; transform: rotate({start}deg); }} }}
  </style>
  <circle cx="48" cy="48" r="{r}" fill="none" stroke="{colors['ring']}" stroke-width="1.5"/>
  <circle class="spin" cx="48" cy="48" r="{r}" fill="none" stroke="{accent}" stroke-width="2"
          stroke-linecap="round" stroke-dasharray="{arc:.1f} {circ:.1f}"/>
  <g transform="translate(26 26) scale(1.8333)" fill="none" stroke="{colors['ink']}" stroke-width="1.6"
     stroke-linecap="round" stroke-linejoin="round" color="{colors['ink']}">{GLYPHS[name]}</g>
</svg>
"""


def main():
    for name in GLYPHS:
        for theme, colors in THEMES.items():
            path = ASSETS / f"connect-{name}-{theme}.svg"
            path.write_text(icon(name, colors), encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
