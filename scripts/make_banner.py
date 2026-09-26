"""Generate the README banner in light and dark versions.

Writes assets/banner-dark.svg and assets/banner-light.svg: animated binary
"rain" behind a terminal-style name plate. The README picks one based on the
viewer's GitHub theme.

Run from the repo root after editing:  python3 scripts/make_banner.py
"""

import random
from pathlib import Path

WIDTH, HEIGHT = 1000, 200
COLS, ROWS = 50, 9
FONT = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

THEMES = {
    "dark": {"bg": "#0d1117", "digit": "#1bc830", "panel": "#161b22",
             "border": "#30363d", "title": "#1bc830", "muted": "#8b949e"},
    "light": {"bg": "#f6f8fa", "digit": "#1a7f37", "panel": "#ffffff",
              "border": "#d0d7de", "title": "#1a7f37", "muted": "#59636e"},
}


def build(colors):
    rng = random.Random(1337)  # fixed seed: same pattern every time
    col_w = WIDTH / COLS
    row_h = HEIGHT / ROWS
    digits = []
    for c in range(COLS):
        phase = rng.uniform(0, 4)
        for r in range(ROWS):
            x = c * col_w + col_w / 2
            y = r * row_h + row_h * 0.75
            # Delay grows down each column so the glow "falls" like rain
            delay = phase + r * 0.18
            digits.append(
                f'<text x="{x:.1f}" y="{y:.1f}" style="animation-delay:{delay:.2f}s">'
                f"{rng.choice('01')}</text>"
            )

    panel_w, panel_h = 460, 104
    px, py = (WIDTH - panel_w) / 2, (HEIGHT - panel_h) / 2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="t3rminal-cmd">
  <style>
    .rain text {{ font: 600 14px {FONT}; fill: {colors['digit']}; text-anchor: middle;
                  opacity: .06; animation: glow 4s linear infinite; }}
    @keyframes glow {{ 0% {{ opacity: .5 }} 30% {{ opacity: .06 }} 100% {{ opacity: .06 }} }}
    .prompt {{ font: 500 15px {FONT}; fill: {colors['muted']}; }}
    .title {{ font: 800 40px {FONT}; fill: {colors['title']}; }}
    .cursor {{ fill: {colors['title']}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .rain text, .cursor {{ animation: none; }}
    }}
  </style>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{colors['bg']}"/>
  <g class="rain">
    {"".join(digits)}
  </g>
  <rect x="{px}" y="{py}" width="{panel_w}" height="{panel_h}" rx="10"
        fill="{colors['panel']}" stroke="{colors['border']}"/>
  <text class="prompt" x="{px + 28}" y="{py + 36}">~ $ whoami</text>
  <text class="title" x="{px + 28}" y="{py + 80}">&gt; t3rminal-cmd</text>
  <!-- Title is 14 monospace chars at ~0.6em (24px) each, so the cursor sits right after it -->
  <rect class="cursor" x="{px + 372}" y="{py + 50}" width="20" height="36"/>
</svg>
"""


def main():
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for name, colors in THEMES.items():
        path = out / f"banner-{name}.svg"
        path.write_text(build(colors))
        print(f"wrote {path.relative_to(out.parent)}")


if __name__ == "__main__":
    main()
