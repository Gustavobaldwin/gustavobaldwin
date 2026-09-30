"""Render info-card.svg: a terminal session that 'types' itself out once.

Edit data/profile.json, then run:  python scripts/make_info_card.py
"""
from common import ROOT, BG, BORDER, DIM, MID, BRIGHT, AMBER, FONT, esc, load_profile

W, H = 520, 400
X0, Y0, LH = 18, 58, 19
STEP = 0.22  # seconds between lines


def build_lines(p):
    prompt = f'{p["prompt_user"]}@{p["prompt_host"]}'
    L = []  # (kind, text, extra)

    def cmd(c):
        L.append(("cmd", prompt, c))

    def out(t, color=MID, indent=0):
        L.append(("out", t, (color, indent)))

    cmd("whoami")
    out(p["name"], BRIGHT)
    out(p["role"])
    out(p["location"], DIM)
    L.append(("gap", "", None))
    cmd("ls ~/stack")
    for folder, items in p["stack"]:
        L.append(("pair", folder, items))
    L.append(("gap", "", None))
    cmd("cat now.txt")
    for item in p["now"]:
        out(f"> {item}")
    L.append(("gap", "", None))
    cmd("locale")
    out(p["langs"], DIM)
    L.append(("cursor", prompt, None))
    return L


def render(lines):
    parts, y, i = [], Y0, 0
    for kind, a, b in lines:
        if kind == "gap":
            y += LH * 0.55
            continue
        begin = f"{i * STEP:.2f}s"
        anim = (f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" '
                f'begin="{begin}" fill="freeze"/>')
        if kind in ("cmd", "cursor"):
            if kind == "cursor":
                tail = (f'<tspan fill="{BRIGHT}"> \u2588<animate attributeName="opacity" values="1;1;0;0" '
                        f'keyTimes="0;0.5;0.5;1" dur="1.1s" begin="{begin}" repeatCount="indefinite"/></tspan>')
            else:
                tail = f'<tspan fill="{BRIGHT}"> {esc(b)}</tspan>'
            parts.append(
                f'<text x="{X0}" y="{y:.1f}" opacity="0">{anim}'
                f'<tspan fill="{MID}">{esc(a)}</tspan><tspan fill="{DIM}">:~</tspan>'
                f'<tspan fill="{AMBER}">$</tspan>{tail}</text>')
        elif kind == "pair":
            parts.append(
                f'<text x="{X0}" y="{y:.1f}" opacity="0" xml:space="preserve">{anim}'
                f'<tspan fill="{AMBER}">{esc(a)}</tspan>'
                f'<tspan x="{X0 + 96}" fill="{MID}">{esc(b)}</tspan></text>')
        else:
            color, _ = b
            parts.append(f'<text x="{X0}" y="{y:.1f}" fill="{color}" opacity="0" xml:space="preserve">{anim}{esc(a)}</text>')
        y += LH
        i += 1
    return parts


def svg(p):
    body = "\n    ".join(render(build_lines(p)))
    dots = "".join(f'<circle cx="{18 + k * 16}" cy="16" r="5" fill="{c}"/>'
                   for k, c in enumerate([DIM, DIM, BRIGHT]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p["name"])} - {esc(p["role"])}">
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  {dots}
  <text x="{W/2}" y="20" fill="{DIM}" font-family="{FONT}" font-size="11" text-anchor="middle">{esc(p["prompt_user"])}@{esc(p["prompt_host"])}: ~</text>
  <line x1="0" y1="32" x2="{W}" y2="32" stroke="{BORDER}"/>
  <g font-family="{FONT}" font-size="13">
    {body}
  </g>
</svg>
'''


if __name__ == "__main__":
    (ROOT / "info-card.svg").write_text(svg(load_profile()), encoding="utf-8")
    print("info-card.svg written")
