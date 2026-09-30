"""Render contrib-heatmap.svg from the GitHub GraphQL API.

Needs GH_TOKEN in the environment (the Action passes GITHUB_TOKEN).
Run locally with --demo to preview with random data.
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date, timedelta

from common import ROOT, BG, BORDER, DIM, MID, BRIGHT, AMBER, FONT, esc, load_profile

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
SHADES = ["#122012", "#1e4d1e", "#2f7d2f", "#4fbf4f", "#7dff7d"]
CELL, GAP = 11, 3
X0, Y0 = 44, 62

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{
date weekday contributionCount contributionLevel}}}}}}"""


def fetch(login):
    token = os.environ["GH_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["date"], d["weekday"], d["contributionCount"], LEVELS[d["contributionLevel"]])
              for d in w["contributionDays"]] for w in cal["weeks"]]
    return cal["totalContributions"], weeks


def demo():
    start = date.today() - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    weeks, total, d = [], 0, start
    while d <= date.today():
        wk = []
        for _ in range(7):
            if d > date.today():
                break
            n = random.choice([0, 0, 0, 1, 2, 3, 5, 8])
            total += n
            wk.append((d.isoformat(), (d.weekday() + 1) % 7, n, min(4, (n + 1) // 2)))
            d += timedelta(days=1)
        weeks.append(wk)
    return total, weeks


def svg(total, weeks, login):
    W = X0 + len(weeks) * (CELL + GAP) + 16
    H = Y0 + 7 * (CELL + GAP) + 34
    cells, months, last_m, last_wi = [], [], None, -9
    for wi, wk in enumerate(weeks):
        x = X0 + wi * (CELL + GAP)
        for ds, wd, n, lvl in wk:
            y = Y0 + wd * (CELL + GAP)
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                         f'fill="{SHADES[lvl]}"><title>{ds}: {n}</title></rect>')
        m = date.fromisoformat(wk[0][0]).strftime("%b").lower()
        if m != last_m:
            if wi - last_wi >= 3 and wi < len(weeks) - 2:
                months.append(f'<text x="{x}" y="{Y0 - 8}" fill="{DIM}">{m}</text>')
                last_wi = wi
            last_m = m
    days = "".join(f'<text x="{X0 - 8}" y="{Y0 + r * (CELL + GAP) + 9}" fill="{DIM}" text-anchor="end">{t}</text>'
                   for r, t in ((1, "mon"), (3, "wed"), (5, "fri")))
    legend_x = W - 18 - 5 * (CELL + GAP) - 64
    legend = "".join(f'<rect x="{legend_x + 30 + k * (CELL + GAP)}" y="{H - 24}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
                     for k, c in enumerate(SHADES))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} contributions in the last year">
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <g font-family="{FONT}" font-size="12">
    <text x="18" y="24"><tspan fill="{AMBER}">$</tspan><tspan fill="{BRIGHT}"> git log --author={esc(login)} --since="1 year" | heatmap</tspan></text>
    <text x="{W - 18}" y="24" fill="{MID}" text-anchor="end">{total} contributions</text>
  </g>
  <g font-family="{FONT}" font-size="10">
    {"".join(months)}
    {days}
    <text x="{legend_x}" y="{H - 15}" fill="{DIM}">less</text>
    <text x="{legend_x + 34 + 5 * (CELL + GAP)}" y="{H - 15}" fill="{DIM}">more</text>
    <text x="18" y="{H - 15}" fill="{DIM}">updated {date.today().isoformat()}</text>
  </g>
  {legend}
  {"".join(cells)}
</svg>
'''


if __name__ == "__main__":
    login = load_profile()["github_login"]
    total, weeks = demo() if "--demo" in sys.argv else fetch(login)
    (ROOT / "contrib-heatmap.svg").write_text(svg(total, weeks, login), encoding="utf-8")
    print(f"contrib-heatmap.svg written ({total} contributions)")
