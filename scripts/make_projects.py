"""Generate the terminal intro and the "Latest projects" cards.

Writes (light and dark versions of each):
  assets/terminal-*.svg          - animated terminal session under the headline
  assets/project-<name>-*.svg    - one card per project in PROJECTS

Blends the two README styles: terminal windows and monospace text from the
banner, spray-paint titles and colours from the graffiti art.
Shared drawing code lives in graffiti.py.

Needs fonttools and brotli:  pip install fonttools brotli
Run from the repo root after editing:  python3 scripts/make_projects.py
"""

import html
from pathlib import Path

from graffiti import PAINT, ROUGH, THEMES, load_font

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# ---------------------------------------------------------------- content
# Edit these to change the cards. Keep each text line under ~50 characters.
PROJECTS = {
    "casevault": {
        "title": "CaseVault",
        "badge": "v1.180",
        "about": ["Offline case-file manager that lives on your",
                  "own SSD. No cloud, no servers, no tracking."],
        "points": ["Report, arrest & link-chart PDFs",
                   "Encrypted, Bates-numbered discovery",
                   "On-device AI consistency checker"],
        "tags": ["JavaScript", "PWA", "File System API", "Ollama"],
    },
    "portfolio": {
        "title": "Portfolio",
        "badge": "live",
        "about": ["Terminal-themed personal site, hand-built",
                  "and responsive from phone to desktop."],
        "points": ["Typed hero, skills & project cards",
                   "Light / dark theme toggle",
                   "Auto-deployed with GitHub Actions"],
        "tags": ["HTML", "CSS", "JavaScript", "GitHub Pages"],
    },
}

# Terminal intro: (command, output, output colour key)
SESSION = [
    ("ls ~/projects", "casevault/  portfolio/  t3rminal-cmd/", "dirs"),
    ("cat ~/now.txt", "shipping CaseVault v1.180 · offline case files + local AI", "text"),
    ("echo $STACK", "HTML · CSS · JavaScript · Python · PWAs · Ollama", "text"),
]


def paint_defs(colors):
    return f"""<linearGradient id="paint" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{PAINT[0]}"/>
      <stop offset=".5" stop-color="{PAINT[1]}"/>
      <stop offset="1" stop-color="{PAINT[2]}"/>
    </linearGradient>
    {ROUGH}"""


def window_bar(colors, w, label):
    dots = "".join(f'<circle cx="{24 + i * 18}" cy="22" r="5.5" fill="{c}"/>'
                   for i, c in enumerate(PAINT))
    return f"""<path d="M1,13 A12,12 0 0 1 13,1 H{w - 13} A12,12 0 0 1 {w - 1},13 V44 H1 Z" fill="{colors['bg']}"/>
  <line x1="1" y1="44" x2="{w - 1}" y2="44" stroke="{colors['border']}"/>
  {dots}
  <text class="bar" x="{w / 2}" y="27" text-anchor="middle">{html.escape(label)}</text>"""


# ---------------------------------------------------------------- terminal
def terminal(colors):
    W, line_h, top = 1000, 30, 82
    H = top + line_h * (len(SESSION) * 2 + 1) - 4
    out_fill = {"dirs": PAINT[1] if colors is THEMES["dark"] else "#0969da", "text": colors["text"]}
    rows, t = [], 0.4
    y = top
    for cmd, output, kind in SESSION:
        chars = len(cmd)
        type_time = chars * 0.07
        # The prompt shows first, then a cover slides off the command in steps to "type" it.
        rows.append(f"""<g class="show" style="animation-delay:{t:.2f}s">
      <text class="prompt" x="32" y="{y}">~ $</text>
      <text class="cmd" x="76" y="{y}">{html.escape(cmd)}</text>
      <rect class="type" x="74" y="{y - 20}" width="{chars * 10.6 + 8:.0f}" height="28" fill="{colors['wall']}"
            style="animation-delay:{t + 0.3:.2f}s;animation-duration:{type_time:.2f}s;animation-timing-function:steps({chars})"/>
    </g>""")
        t += 0.3 + type_time + 0.25
        y += line_h
        rows.append(f'<text class="show out" x="32" y="{y}" fill="{out_fill[kind]}" '
                    f'style="animation-delay:{t:.2f}s">{html.escape(output)}</text>')
        t += 0.55
        y += line_h
    rows.append(f"""<g class="show" style="animation-delay:{t:.2f}s">
      <text class="prompt" x="32" y="{y}">~ $</text>
      <rect class="cursor" x="77" y="{y - 17}" width="10" height="21"/>
    </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape('. '.join(f'{c}: {o}' for c, o, _ in SESSION))}">
  <style>
    .bar {{ font: 500 13px {MONO}; fill: {colors['muted']}; }}
    .prompt {{ font: 700 17px {MONO}; fill: {colors['tag']}; }}
    .cmd {{ font: 600 17px {MONO}; fill: {colors['text']}; }}
    .out {{ font: 400 16px {MONO}; }}
    .show {{ opacity: 0; animation: show .01s forwards; }}
    @keyframes show {{ to {{ opacity: 1 }} }}
    .type {{ animation-name: type; animation-fill-mode: both; }}
    @keyframes type {{ from {{ transform: translateX(0) }} to {{ transform: translateX(100%); opacity: 0 }} }}
    .type {{ transform-box: fill-box; }}
    .cursor {{ fill: {colors['tag']}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .show {{ animation: none; opacity: 1; }}
      .type {{ display: none; }}
      .cursor {{ animation: none; }}
    }}
  </style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{colors['wall']}" stroke="{colors['border']}"/>
  {window_bar(colors, W, 't3rminal-cmd@github: ~')}
  {"".join(rows)}
</svg>
"""


# ---------------------------------------------------------------- cards
def card(name, p, colors, marker):
    W, H = 500, 306
    pad = 28

    # Title: spray-paint gradient with an outline, like the headline.
    title_y = 104
    live = p["badge"] == "live"
    badge_w = len(p["badge"]) * 8.4 + (40 if live else 24)
    badge = f"""<g transform="translate({W - pad - badge_w:.0f},70)">
    <rect width="{badge_w:.0f}" height="26" rx="13" fill="none" stroke="{colors['tag']}" stroke-width="1.5"/>
    {f'<circle cx="16" cy="13" r="4" fill="{colors["tag"]}" class="pulse"/>' if live else ''}
    <text class="badge" x="{(28 if live else 12)}" y="18">{html.escape(p['badge'])}</text>
  </g>"""

    about = "".join(f'<text class="about" x="{pad}" y="{144 + i * 21}">{html.escape(l)}</text>'
                    for i, l in enumerate(p["about"]))
    points = "".join(
        f'<text class="pt" x="{pad}" y="{196 + i * 21}"><tspan class="arrow">▸</tspan> {html.escape(l)}</text>'
        for i, l in enumerate(p["points"]))

    chips, x = [], pad
    for tag in p["tags"]:
        w = len(tag) * 7.2 + 20
        chips.append(f'<g transform="translate({x:.0f},{H - 46})"><rect width="{w:.0f}" height="24" rx="6" '
                     f'fill="{colors["bg"]}" stroke="{colors["border"]}"/>'
                     f'<text class="chip" x="10" y="16">{html.escape(tag)}</text></g>')
        x += w + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(p['title'] + ': ' + ' '.join(p['about']))}">
  <defs>
    <style>
      @font-face {{ font-family: 'Marker'; src: url({marker}) format('woff2'); }}
      .bar {{ font: 500 13px {MONO}; fill: {colors['muted']}; }}
      .title {{ font: 44px 'Marker', 'Comic Sans MS', cursive; fill: url(#paint);
               stroke: {colors['outline']}; stroke-width: 5px; paint-order: stroke; stroke-linejoin: round; }}
      .badge {{ font: 700 13px {MONO}; fill: {colors['tag']}; }}
      .about {{ font: 400 14px {MONO}; fill: {colors['text']}; }}
      .pt {{ font: 400 13.5px {MONO}; fill: {colors['muted']}; }}
      .arrow {{ fill: {colors['tag']}; }}
      .chip {{ font: 600 12px {MONO}; fill: {colors['text']}; }}
      .pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
      @keyframes pulse {{ 50% {{ opacity: .25 }} }}
      @media (prefers-reduced-motion: reduce) {{ .pulse {{ animation: none; }} }}
    </style>
    {paint_defs(colors)}
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{colors['wall']}" stroke="{colors['border']}"/>
  {window_bar(colors, W, f'~/projects/{name}')}
  <text class="title" x="{pad}" y="{title_y}" transform="rotate(-2 {pad} {title_y})">{html.escape(p['title'])}</text>
  {badge}
  {about}
  {points}
  {"".join(chips)}
</svg>
"""


def main():
    ASSETS.mkdir(exist_ok=True)
    marker, _ = load_font("PermanentMarker.woff2", "".join(p["title"] for p in PROJECTS.values()))
    for theme, colors in THEMES.items():
        path = ASSETS / f"terminal-{theme}.svg"
        path.write_text(terminal(colors))
        print(f"wrote {path.relative_to(ROOT)}")
        for name, p in PROJECTS.items():
            path = ASSETS / f"project-{name}-{theme}.svg"
            path.write_text(card(name, p, colors, marker))
            print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
