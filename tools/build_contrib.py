#!/usr/bin/env python3
"""Draws the contribution calendar as a warehouse floor: one box per day,
stacked higher on busier days. The Shipping Log workflow runs this once a day
and publishes the result to the `output` branch.

    python3 tools/build_contrib.py [out_dir]      # needs the gh CLI, logged in
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from xml.dom import minidom

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_assets import THEMES, frame  # noqa: E402

QUERY = (
    "query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{"
    "weeks{contributionDays{date weekday contributionLevel}}}}}}"
)
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Box colour per level, quiet to busy. Dark theme gets brighter, light theme gets deeper.
PALETTE = {
    "dark": dict(floor="#161F47", floor_edge="#263163", boxes=["#1F6496", "#1E8FD3", "#3DBBF7", "#9AE6FF"], top=0.30, side=0.34),
    "light": dict(floor="#E6ECFA", floor_edge="#CFD8F0", boxes=["#A6D6F4", "#55B5EA", "#1689D0", "#02569B"], top=0.38, side=0.20),
}

W, H = 846, 200
X0, Y0 = 26.0, 164.0        # front-left corner of the first column, front row
BOX_W = 9.0                 # box width on screen
DEPTH = 5.2                 # how far a box reaches back (same in x and y)
ROW = 7.0                   # step from one weekday row to the one behind it
HEIGHTS = [0, 7, 15, 25, 38]


def fetch(login):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={login}"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def mix(color, other, amount):
    a = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02X}" for x, y in zip(a, b))


def pts(*points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def draw(weeks, theme):
    t, p = THEMES[theme], PALETTE[theme]
    pitch = min(14.4, (W - X0 - BOX_W - DEPTH - 6 * ROW - 18) / max(1, len(weeks) - 1))

    css = [f".z{{fill:{p['floor']};stroke:{p['floor_edge']};stroke-width:.6}}"]
    for i, c in enumerate(p["boxes"], start=1):
        css.append(f".f{i}{{fill:{c}}}.u{i}{{fill:{mix(c, '#FFFFFF', p['top'])}}}.s{i}{{fill:{mix(c, '#000000', p['side'])}}}")
    css.append(".scan{animation:scan 9s linear infinite}@keyframes scan{from{transform:translateX(-70px)}to{transform:translateX(870px)}}")

    # Paint back to front: Sunday is the back row, Saturday the front row.
    cells = []
    for weekday in range(7):
        back = 6 - weekday
        for w, week in enumerate(weeks):
            day = next((d for d in week["contributionDays"] if d["weekday"] == weekday), None)
            if day is None:
                continue
            level = LEVELS.index(day["contributionLevel"])
            x, y, h = X0 + w * pitch + back * ROW, Y0 - back * ROW, HEIGHTS[level]
            if level == 0:
                cells.append(f'<polygon class="z" points="{pts((x, y), (x + BOX_W, y), (x + BOX_W + DEPTH, y - DEPTH), (x + DEPTH, y - DEPTH))}"/>')
                continue
            cells.append(
                f'<polygon class="s{level}" points="{pts((x + BOX_W, y), (x + BOX_W + DEPTH, y - DEPTH), (x + BOX_W + DEPTH, y - DEPTH - h), (x + BOX_W, y - h))}"/>'
                f'<polygon class="u{level}" points="{pts((x, y - h), (x + BOX_W, y - h), (x + BOX_W + DEPTH, y - DEPTH - h), (x + DEPTH, y - DEPTH - h))}"/>'
                f'<rect class="f{level}" x="{x:.1f}" y="{y - h:.1f}" width="{BOX_W}" height="{h}"/>'
            )

    # Month names under the front row, at the first week that starts in that month.
    labels, last_month, last_x = [], None, -99.0
    for w, week in enumerate(weeks):
        month = int(week["contributionDays"][0]["date"][5:7])
        x = X0 + w * pitch
        if month != last_month and x - last_x > 30:
            labels.append(f'<text class="mono" x="{x:.1f}" y="{Y0 + 18}" font-size="10.5" fill="{t["faint"]}">{MONTHS[month - 1]}</text>')
            last_x = x
        last_month = month

    legend_x = W - 26 - 5 * 13 - 34
    legend = f'<text class="mono" x="{legend_x - 8}" y="31" font-size="10.5" text-anchor="end" fill="{t["faint"]}">less</text>'
    legend += f'<rect class="z" x="{legend_x}" y="22" width="10" height="10" rx="1.5"/>'
    for i in range(1, 5):
        legend += f'<rect class="f{i}" x="{legend_x + i * 13}" y="22" width="10" height="10" rx="1.5"/>'
    legend += f'<text class="mono" x="{legend_x + 5 * 13 + 6}" y="31" font-size="10.5" fill="{t["faint"]}">more</text>'

    # A scanner plane that sweeps the floor from left to right.
    reach = 6 * ROW + DEPTH + 6
    sx, sy = 0.0, Y0 + 5
    scan = (
        f'<g class="scan">'
        f'<polygon points="{pts((sx, sy), (sx + reach, sy - reach), (sx + reach, sy - reach - 46), (sx, sy - 46))}" fill="url(#beam)"/>'
        f'<path d="M{sx:.1f} {sy:.1f}l{reach:.1f} {-reach:.1f}" stroke="{t["a"]}" stroke-width="1.6" stroke-linecap="round"/>'
        f"</g>"
    )
    defs = (
        f'<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t["a"]}" stop-opacity=".38"/>'
        f'<stop offset="1" stop-color="{t["a"]}" stop-opacity="0"/></linearGradient>'
    )
    glows = '<circle cx="770" cy="-10" r="230" fill="url(#glowB)"/><circle cx="50" cy="190" r="210" fill="url(#glowA)"/>'
    body = (
        f'<text class="mono" x="26" y="31" font-size="10.5" fill="{t["muted"]}">one box per day · a taller stack is a busier day</text>'
        + legend + "".join(cells) + "".join(labels) + scan
    )
    return frame(t, W, H, 16, body, "".join(css), defs, glows,
                 title="My GitHub contributions over the last year, drawn as stacks of boxes on a warehouse floor",
                 reduced=".scan{display:none}", fade=(0.5, 0.2))


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    login = os.environ.get("GITHUB_REPOSITORY_OWNER") or "Potterjr"
    weeks = fetch(login)
    for theme in THEMES:
        svg = draw(weeks, theme)
        minidom.parseString(svg.encode("utf-8"))  # fail loudly on malformed XML
        path = out / f"contributions-{theme}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"{path}  {len(svg) / 1024:.1f} kB")
