"""Draw the last year of contributions as a stock-market style chart.

Writes contrib-ticker-dark.svg and contrib-ticker-light.svg. contrib_graph.py
calls render() with the same data it uses for the heatmap, so the two charts
always agree. The chart shows:

  - contributions as a glowing line over a gradient area (daily while the
    history is short, weekly once it spans more than ~4 months), drawn in
    when the image loads, with the newest week pulsing at the end
  - the 4-week moving average as a dashed line
  - "volume" bars along the bottom: active days in each week
  - the three biggest weeks flagged as peaks
  - a ticker header: last 4 weeks vs the 4 weeks before, up or down

Usage (offline test with made-up data):  python3 scripts/contrib_ticker.py OUTPUT_DIR --demo
"""

import datetime
import html
import math
import random
import sys
from pathlib import Path

FONT = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
PAINT = ["#1bc830", "#00d4ff", "#ff2e88"]  # same spray colours as the rest of the README
THEMES = {
    "dark": {"bg": "#0d1117", "panel": "#161b22", "border": "#30363d", "grid": "#21262d",
             "text": "#e6edf3", "muted": "#8b949e", "up": "#1bc830", "down": "#ff2e88", "vol": "#30363d", "navy": "#3a5bd0"},
    "light": {"bg": "#ffffff", "panel": "#f6f8fa", "border": "#d0d7de", "grid": "#eaeef2",
              "text": "#1f2328", "muted": "#59636e", "up": "#1a7f37", "down": "#cf2273", "vol": "#d0d7de", "navy": "#1e3a8a"},
}

W, H = 1000, 420
PL, PR = 28, 64           # plot left / right padding (right holds the price axis)
PT, PB = 118, 92          # plot top / bottom padding (bottom holds volume + months)
VOL_H = 34


def weekly(days):
    """Sum days into weeks (Sunday start, like GitHub). Returns [(week_start, count, active_days)]."""
    weeks = {}
    for iso, count, level in days:
        d = datetime.date.fromisoformat(iso)
        start = d - datetime.timedelta(days=(d.weekday() + 1) % 7)
        c = count if count is not None else (level and level * 2)  # rough stand-in if counts are hidden
        w = weeks.setdefault(start, [0, 0])
        w[0] += c or 0
        w[1] += 1 if (c or 0) > 0 else 0
    return [(s, c, a) for s, (c, a) in sorted(weeks.items())]


def smooth_path(pts, floor=None):
    """Catmull-Rom spline through the points, as cubic Beziers. Control points
    are kept above `floor` (the zero line) so the curve never dips below 0."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if floor is not None:
            c1, c2 = (c1[0], min(c1[1], floor)), (c2[0], min(c2[1], floor))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def nice_max(v):
    """Smallest 4 x step >= v, with a round step (1, 1.5, 2, 3, 5, 10, 15, 20...)."""
    raw = max(v, 4) / 4
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 1.5, 2, 3, 5, 10):
        if raw <= m * mag and (m * mag) % 1 == 0:  # whole-number steps only
            return 4 * m * mag
    return 40 * mag


def day_count(count, level):
    return count if count is not None else (level * 2 if level else 0)  # rough stand-in if counts are hidden


def series(days):
    """Pick what to plot. The chart starts two weeks before the first
    contribution in the year, so a short history isn't a long flat line. If
    that span is under ~4 months, plot daily values (more peaks, more like a
    stock chart); otherwise weekly totals. Returns (unit, [(date, value, vol 0-1)])."""
    first = next((i for i, (_, c, l) in enumerate(days) if day_count(c, l) > 0), 0)
    days = days[max(0, first - 14):]
    if len(days) <= 120:
        vals = [day_count(c, l) for _, c, l in days]
        hi = max(vals) or 1
        return "day", [(datetime.date.fromisoformat(d), v, v / hi) for (d, _, _), v in zip(days, vals)]
    return "wk", [(s, c, a / 7) for s, c, a in weekly(days)]


def render(days, theme, user="t3rminal-cmd"):
    t = THEMES[theme]
    unit, pts_data = series(days)
    counts = [v for _, v, _ in pts_data]
    n = len(pts_data)
    daily = unit == "day"
    wk = weekly(days)
    top = nice_max(max(counts) * 1.15 if counts else 5)

    pw = W - PL - PR
    ph = H - PT - PB
    xs = [PL + i * pw / (n - 1) for i in range(n)]

    def y(v):
        return PT + ph - v / top * ph

    pts = [(xs[i], y(c)) for i, c in enumerate(counts)]
    line = smooth_path(pts, PT + ph)
    area = f"{line} L{xs[-1]:.1f},{PT + ph} L{xs[0]:.1f},{PT + ph} Z"

    span = 7 if daily else 4  # moving average: 7 days or 4 weeks
    ma = [sum(counts[max(0, i - span + 1):i + 1]) / len(counts[max(0, i - span + 1):i + 1]) for i in range(n)]
    ma_path = smooth_path([(xs[i], y(v)) for i, v in enumerate(ma)], PT + ph)

    # Ticker header: last 4 weeks vs the 4 before (from daily data either way).
    all_counts = [day_count(c, l) for _, c, l in days]
    now, before = sum(all_counts[-28:]), sum(all_counts[-56:-28])
    diff = now - before
    pct = (diff / before * 100) if before else (100.0 if now else 0.0)
    up = diff >= 0
    move_col = t["up"] if up else t["down"]
    arrow = "▲" if up else "▼"
    total = sum(all_counts)
    hi = max(counts)
    wk_counts = [c for _, c, _ in wk]
    best_wk = max(wk_counts) if wk_counts else 0

    # Grid and price axis
    grid = []
    for k in range(5):
        v = top * k / 4
        gy = y(v)
        grid.append(f'<line x1="{PL}" y1="{gy:.1f}" x2="{W - PR}" y2="{gy:.1f}" stroke="{t["grid"]}" '
                    f'stroke-dasharray="{"none" if k == 0 else "3 5"}"/>'
                    f'<text class="ax" x="{W - PR + 10}" y="{gy + 4:.1f}">{v:g}</text>')

    # Date labels along the bottom: months for a weekly chart, every other Monday for a daily one
    months, last = [], None
    for i, (s, _, _) in enumerate(pts_data):
        if daily:
            if s.weekday() == 0 and s.isocalendar()[1] % 2 == 0 and 2 < i < n - 3:
                months.append(f'<text class="ax" x="{xs[i]:.1f}" y="{H - 22}" text-anchor="middle">{s.strftime("%b %-d")}</text>')
        elif s.month != last and 0 < i < n - 2:
            months.append(f'<text class="ax" x="{xs[i]:.1f}" y="{H - 22}" text-anchor="middle">{s.strftime("%b")}</text>')
        last = s.month

    # Volume bars: active days per week, or each day's share of the busiest day
    vol_base = H - 42
    bw = pw / n * 0.62
    vol = "".join(
        f'<rect x="{xs[i] - bw / 2:.1f}" y="{vol_base - a * VOL_H:.1f}" width="{bw:.1f}" '
        f'height="{a * VOL_H:.1f}" rx="1.5" fill="{t["navy"] if a >= .6 else t["vol"]}" '
        f'opacity="{.6 if a >= .6 else 1}"/>'
        for i, (_, _, a) in enumerate(pts_data))

    # Peaks: the three biggest points, kept apart so the flags don't collide
    gap = 5 if daily else 6
    peaks = []
    for i in sorted(range(n), key=lambda i: -counts[i]):
        if counts[i] and all(abs(i - j) >= gap for j in peaks) and 1 <= i <= n - 2:
            peaks.append(i)
        if len(peaks) == 3:
            break
    flags = []
    for k, i in enumerate(sorted(peaks)):
        px, py = pts[i]
        when = pts_data[i][0].strftime('%b %-d')
        label = f"▲ {counts[i]} · {when}" if daily else f"▲ {counts[i]} · wk of {when}"
        lw = len(label) * 7.4 + 16
        lx = min(max(px - lw / 2, PL), W - PR - lw)
        ly = max(py - 40, PT - 34)
        flags.append(f"""<g class="flag" style="animation-delay:{1.6 + k * .25:.2f}s">
      <line x1="{px:.1f}" y1="{py - 6:.1f}" x2="{px:.1f}" y2="{ly + 22:.1f}" stroke="{PAINT[2]}" stroke-width="1.2" stroke-dasharray="2 3"/>
      <rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.0f}" height="22" rx="6" fill="{t['bg']}" stroke="{PAINT[2]}"/>
      <text class="fl" x="{lx + 8:.1f}" y="{ly + 15:.1f}">{html.escape(label)}</text>
      <circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{t['bg']}" stroke="{PAINT[2]}" stroke-width="2.5"/>
    </g>""")

    ex, ey = pts[-1]
    tag_y = min(max(ey, PT + 10), PT + ph - 10)
    first, last_day = pts_data[0][0], datetime.date.fromisoformat(days[-1][0])
    per = "day" if daily else "week"
    label = (f"{user} contributions per {per}, {first:%b %-d %Y} to {last_day:%b %-d %Y}: {total} in the last year, best {per} {hi}. "
             f"Last 4 weeks {now} vs {before} the 4 weeks before ({'+' if up else ''}{pct:.0f}%).")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{html.escape(label)}">
  <defs>
    <linearGradient id="ln" x1="0" x2="1">
      <stop offset="0" stop-color="{PAINT[0]}"/><stop offset=".55" stop-color="{PAINT[1]}"/><stop offset="1" stop-color="{PAINT[2]}"/>
    </linearGradient>
    <linearGradient id="ar" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="{t['navy']}" stop-opacity="{.45 if theme == 'dark' else .25}"/>
      <stop offset="1" stop-color="{t['navy']}" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-5%" y="-30%" width="110%" height="160%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="reveal"><rect class="rv" x="0" y="0" width="{W}" height="{H}"/></clipPath>
    <style>
      text {{ font-family: {FONT}; }}
      .sym {{ font-size: 15px; font-weight: 800; fill: {t['text']}; letter-spacing: 1px; }}
      .nm {{ font-size: 12px; fill: {t['muted']}; }}
      .px {{ font-size: 34px; font-weight: 800; fill: {t['text']}; }}
      .mv {{ font-size: 15px; font-weight: 700; fill: {move_col}; }}
      .kv {{ font-size: 11px; fill: {t['muted']}; }}
      .kn {{ font-size: 15px; font-weight: 700; fill: {t['text']}; }}
      .ax {{ font-size: 11px; fill: {t['muted']}; }}
      .fl {{ font-size: 11.5px; font-weight: 700; fill: {PAINT[2]}; }}
      .line {{ stroke-dasharray: 3000; stroke-dashoffset: 3000; animation: draw 2.2s ease-out .2s forwards; }}
      @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
      .rv {{ transform: scaleX(0); animation: grow 2.2s ease-out .2s forwards; }}
      @keyframes grow {{ to {{ transform: scaleX(1); }} }}
      .flag, .end {{ opacity: 0; animation: show .4s ease-out forwards; }}
      .end {{ animation-delay: 2.3s; }}
      @keyframes show {{ to {{ opacity: 1; }} }}
      .ping {{ transform-box: fill-box; transform-origin: center; animation: ping 1.8s ease-out 2.4s infinite; opacity: 0; }}
      @keyframes ping {{ 0% {{ transform: scale(1); opacity: .7; }} 100% {{ transform: scale(3.2); opacity: 0; }} }}
      .live {{ animation: blink 1.4s ease-in-out infinite; }}
      @keyframes blink {{ 50% {{ opacity: .25; }} }}
      @media (prefers-reduced-motion: reduce) {{
        .line {{ animation: none; stroke-dashoffset: 0; }}
        .rv {{ animation: none; transform: none; }}
        .flag, .end {{ animation: none; opacity: 1; }}
        .ping, .live {{ animation: none; }}
      }}
    </style>
  </defs>

  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t['bg']}" stroke="{t['border']}"/>

  <!-- ticker header -->
  <g transform="translate({PL},0)">
    <rect y="22" width="62" height="24" rx="6" fill="{t['navy']}"/>
    <text x="31" y="39" text-anchor="middle" style="font-size:13px;font-weight:800;fill:#ffffff">T3RM</text>
    <text class="nm" x="74" y="39">{html.escape(user)} · contributions / {per} · since {first:%b %-d, %Y}</text>
    <circle class="live" cx="{W - PL - PR - 52}" cy="34" r="4" fill="{t['up']}"/>
    <text class="nm" x="{W - PL - PR - 42}" y="39">LIVE</text>
    <text class="px" x="0" y="88">{now}</text>
    <text class="mv" x="{len(str(now)) * 21 + 14}" y="88">{arrow} {'+' if up else ''}{diff} ({'+' if up else ''}{pct:.0f}%)</text>
    <text class="kv" x="{len(str(now)) * 21 + 14}" y="70">last 4 wks vs prior 4</text>
  </g>
  <g transform="translate({W - PR - 330},60)">
    <text class="kv" x="0" y="0">1Y TOTAL</text><text class="kn" x="0" y="22">{total}</text>
    <text class="kv" x="110" y="0">BEST {"DAY" if daily else "WK"}</text><text class="kn" x="110" y="22">{hi}</text>
    <text class="kv" x="210" y="0">{"BEST WK" if daily else "ACTIVE WKS"}</text><text class="kn" x="210" y="22">{best_wk if daily else sum(1 for c in wk_counts if c)}</text>
  </g>

  {"".join(grid)}
  {"".join(months)}
  <text class="ax" x="{W - PR + 10}" y="{vol_base - VOL_H / 2 + 4:.0f}">vol</text>
  <g clip-path="url(#reveal)">
    {vol}
    <path d="{area}" fill="url(#ar)"/>
    <path d="{ma_path}" fill="none" stroke="{t['muted']}" stroke-width="1.4" stroke-dasharray="5 5" opacity=".8"/>
  </g>
  <path class="line" d="{line}" fill="none" stroke="{t['navy']}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>
  {"".join(flags)}
  <g class="end">
    <line x1="{ex:.1f}" y1="{ey:.1f}" x2="{W - PR + 4}" y2="{tag_y:.1f}" stroke="{t['navy']}" stroke-dasharray="2 3"/>
    <circle class="ping" cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{t['navy']}"/>
    <circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{t['navy']}" stroke="{t['bg']}" stroke-width="2"/>
    <rect x="{W - PR + 4}" y="{tag_y - 11:.1f}" width="44" height="22" rx="5" fill="{t['navy']}"/>
    <text x="{W - PR + 26}" y="{tag_y + 4:.1f}" text-anchor="middle" style="font-size:12px;font-weight:800;fill:#fff">{counts[-1]}</text>
  </g>
  <g transform="translate({W - PR - 268},{PT - 12})">
    <line x1="0" y1="-4" x2="22" y2="-4" stroke="{t['navy']}" stroke-width="3"/><text class="ax" x="28" y="0">{"daily" if daily else "weekly"}</text>
    <line x1="96" y1="-4" x2="118" y2="-4" stroke="{t['muted']}" stroke-width="1.4" stroke-dasharray="5 5"/><text class="ax" x="124" y="0">{"7-day" if daily else "4-wk"} avg</text>
    <circle cx="210" cy="-4" r="4" fill="{t['bg']}" stroke="{PAINT[2]}" stroke-width="2"/><text class="ax" x="220" y="0">peak</text>
  </g>
</svg>
"""


def demo_days():
    rng = random.Random(4)
    today = datetime.date.today()
    out = []
    for i in range(364, -1, -1):
        d = today - datetime.timedelta(days=i)
        season = 1 + math.sin(i / 40) * .8 + (2.2 if 60 < i < 75 else 0) + (1.6 if 200 < i < 212 else 0)
        c = max(0, int(rng.gauss(season, 1.6))) if rng.random() < .62 else 0
        out.append((d.isoformat(), c, min(4, c)))
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] != "--demo":
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    days = demo_days()
    for theme in THEMES:
        (out / f"contrib-ticker-{theme}.svg").write_text(render(days, theme), encoding="utf-8")
    print("wrote demo charts to", out)
