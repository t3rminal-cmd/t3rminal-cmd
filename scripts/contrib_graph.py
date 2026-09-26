"""Draw the last year of GitHub contributions as light and dark SVGs.

Replaces the contribution snake. The "Generate Profile Images" workflow runs
this and publishes the images to the output branch, where the README loads
them.

Where the numbers come from:
  1. If the CONTRIB_TOKEN secret is set (a personal access token), GitHub's
     GraphQL API. This is the most reliable source.
  2. Otherwise the public contributions page (no token needed).

If neither works, nothing is written and the script exits cleanly, so the
workflow keeps publishing the last good chart instead of a broken one.

Usage:  python3 scripts/contrib_graph.py OUTPUT_DIR [USERNAME]
        python3 scripts/contrib_graph.py OUTPUT_DIR --from-html FILE   (offline test)
"""

import datetime
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

USER = "t3rminal-cmd"
FONT = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 44, 78  # room for weekday and month labels
THEMES = {  # matched to the README banner
    "dark": {"bg": "#0d1117", "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e",
             "accent": "#1bc830", "levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]},
    "light": {"bg": "#f6f8fa", "border": "#d0d7de", "text": "#1f2328", "muted": "#59636e",
              "accent": "#1a7f37", "levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]},
}
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def from_graphql(user, token):
    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
      totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "contrib-graph"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"], LEVELS.get(d["contributionLevel"], 0))
            for w in cal["weeks"] for d in w["contributionDays"]]
    return days, cal["totalContributions"]


def parse_html(page):
    """Read the public contributions page: one <td> per day plus a tooltip with its count."""
    tips = {}
    for tip_for, text in re.findall(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        m = re.search(r"([\d,]+) contributions?", text)
        tips[tip_for] = int(m.group(1).replace(",", "")) if m else 0
    days = []
    for td in re.findall(r"<td\b[^>]*ContributionCalendar-day[^>]*>", page):
        date = re.search(r'data-date="(\d{4}-\d\d-\d\d)"', td)
        level = re.search(r'data-level="(\d)"', td)
        if not date or not level:
            continue
        ident = re.search(r'\bid="([^"]+)"', td)
        count = tips.get(ident.group(1)) if ident else None
        days.append((date.group(1), count, int(level.group(1))))
    days.sort()
    total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
    total = int(total.group(1).replace(",", "")) if total else None
    return days, total


def from_public_page(user):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "Mozilla/5.0 (contrib-graph)"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return parse_html(res.read().decode("utf-8", "replace"))


def summarize(days, total):
    """Totals and streaks. Days with an unknown count fall back to 'active if level > 0'."""
    active = [c > 0 if c is not None else lvl > 0 for _, c, lvl in days]
    if total is None and all(c is not None for _, c, _ in days):
        total = sum(c for _, c, _ in days)  # otherwise stays None: counts unknown
    longest = run = 0
    for a in active:
        run = run + 1 if a else 0
        longest = max(longest, run)
    # Current streak: ending today, or yesterday if today has nothing yet
    current, i = 0, len(active) - 1
    if i >= 0 and not active[i]:
        i -= 1
    while i >= 0 and active[i]:
        current += 1
        i -= 1
    counted = [(c, d) for d, c, _ in days if c]
    best = max(counted) if counted else None
    return {"total": total, "active": sum(active), "recent": sum(active[-30:]),
            "current": current, "longest": longest, "best": best}


def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def render(days, stats, theme, user):
    t = THEMES[theme]
    first = datetime.date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    weeks = (offset + len(days) + 6) // 7
    grid_w = weeks * STEP
    width = LEFT + grid_w + 24
    height = TOP + 7 * STEP + 92

    cells = []
    for i, (date, count, level) in enumerate(days):
        col, row = divmod(offset + i, 7)
        x, y = LEFT + col * STEP, TOP + row * STEP
        if count == 0 or (count is None and level == 0):
            label = f"No contributions on {fmt_date(date)}"
        elif count is None:
            label = f"Contributions on {fmt_date(date)}"
        else:
            label = f"{count} contribution{'' if count == 1 else 's'} on {fmt_date(date)}"
        cells.append(f'<rect class="d l{level}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'style="animation-delay:{col * 0.018:.3f}s"><title>{label}</title></rect>')

    # Month names above the first full week of each month
    months, last_month = [], first.month
    for col in range(1, weeks - 1):
        top_day = first + datetime.timedelta(days=col * 7 - offset)
        if top_day.month != last_month:
            months.append(f'<text class="m" x="{LEFT + col * STEP}" y="{TOP - 8}">{top_day.strftime("%b")}</text>')
            last_month = top_day.month

    days_lbl = "".join(f'<text class="m" x="{LEFT - 8}" y="{TOP + r * STEP + CELL - 2}" text-anchor="end">{n}</text>'
                       for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    level_css = "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(t["levels"]))
    legend_x = LEFT + grid_w - 5 * STEP - 34  # leave room for "More"
    legend = "".join(f'<rect class="l{i}" x="{legend_x + i * STEP}" y="{TOP + 7 * STEP + 8}" width="{CELL}" height="{CELL}" rx="2.5"/>'
                     for i in range(5))

    best = stats["best"]
    stat_items = [
        (f"{stats['total']:,}", "contributions") if stats["total"] is not None else (f"{stats['active']}", "active days"),
        (f"{stats['current']}", "current streak (days)"),
        (f"{stats['longest']}", "longest streak (days)"),
        (f"{best[0]}", f"best day: {fmt_date(best[1])}") if best
        else (f"{stats['active']}", "active days") if stats["total"] is not None
        else (f"{stats['recent']}", "active days (last 30)"),
    ]
    col_w = (width - 2 * 24) / len(stat_items)
    sy = TOP + 7 * STEP + 58
    stat_svg = "".join(
        f'<text class="n" x="{24 + k * col_w + col_w / 2:.0f}" y="{sy}" text-anchor="middle">{html.escape(n)}</text>'
        f'<text class="m" x="{24 + k * col_w + col_w / 2:.0f}" y="{sy + 18}" text-anchor="middle">{html.escape(l)}</text>'
        for k, (n, l) in enumerate(stat_items))

    summary = (f"{stats['total']} contributions in the last year" if stats["total"] is not None
               else f"{stats['active']} active days in the last year")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{user}: {summary}, current streak {stats['current']} days, longest streak {stats['longest']} days">
  <style>
    text {{ font-family: {FONT}; }}
    .p {{ font-size: 14px; font-weight: 500; fill: {t['muted']}; }}
    .a {{ fill: {t['accent']}; font-weight: 700; }}
    .m {{ font-size: 11px; fill: {t['muted']}; }}
    .n {{ font-size: 22px; font-weight: 800; fill: {t['accent']}; }}
    {level_css}
    .d {{ opacity: 0; animation: on .5s ease-out forwards; }}
    @keyframes on {{ from {{ opacity: 0; transform: translateY(3px); }} to {{ opacity: 1; transform: none; }} }}
    .scan {{ fill: {t['accent']}; opacity: .10; animation: scan 7s linear 1.4s infinite; }}
    @keyframes scan {{ from {{ transform: translateX(0); }} to {{ transform: translateX({grid_w + STEP}px); }} }}
    .cur {{ fill: {t['accent']}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .d {{ opacity: 1; animation: none; }} .scan, .cur {{ animation: none; }} .scan {{ display: none; }} }}
  </style>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t['bg']}" stroke="{t['border']}"/>
  <text class="p" x="24" y="32"><tspan class="a">{user}@github</tspan>:~$ contributions --last-year <tspan class="cur">&#9612;</tspan></text>
  {"".join(months)}
  {days_lbl}
  <g>{"".join(cells)}</g>
  <rect class="scan" x="{LEFT - STEP}" y="{TOP - 3}" width="{STEP}" height="{7 * STEP + 3}" rx="3"/>
  <text class="m" x="{legend_x - 8}" y="{TOP + 7 * STEP + 18}" text-anchor="end">Less</text>
  {legend}
  <text class="m" x="{legend_x + 5 * STEP + 3}" y="{TOP + 7 * STEP + 18}">More</text>
  {stat_svg}
</svg>
"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    user = USER
    days = total = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--from-html":
        days, total = parse_html(Path(sys.argv[3]).read_text(encoding="utf-8"))
    else:
        if len(sys.argv) >= 3:
            user = sys.argv[2]
        token = os.environ.get("CONTRIB_TOKEN", "").strip()
        sources = ([("GraphQL", lambda: from_graphql(user, token))] if token else []) + \
                  [("public page", lambda: from_public_page(user))]
        for name, fetch in sources:
            try:
                days, total = fetch()
                if len(days) >= 300:
                    print(f"Contribution data from the {name}: {len(days)} days")
                    break
                print(f"{name}: only {len(days)} days found, trying the next source")
            except Exception as exc:  # network or format change: fall through
                print(f"{name} failed: {exc}")
            days = None
    if not days or len(days) < 300:
        print("No contribution data; keeping the previous chart.")
        return
    stats = summarize(days, total)
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (out / f"contrib-{theme}.svg").write_text(render(days, stats, theme, user), encoding="utf-8")
    print(f"Wrote contrib-dark.svg and contrib-light.svg: {stats}")


if __name__ == "__main__":
    main()
