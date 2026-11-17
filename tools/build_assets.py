#!/usr/bin/env python3
"""Builds the SVG artwork used by the profile README.

Every image is generated twice (dark + light) so GitHub can show the one that
matches the visitor's theme. Edit the text or colours below, then run:

    python3 tools/build_assets.py
"""
from pathlib import Path
from xml.dom import minidom

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "dark": dict(
        bg0="#0A0F1F", bg1="#121A3C", border="#27315C",
        text="#F4F7FF", muted="#93A0C8", faint="#8791BD",
        dot="#FFFFFF", dot_o="0.07",
        a="#4FC3F7", b="#8B6CFF", green="#3DDC97",
        glow_a="0.26", glow_b="0.34",
        card="#0D1432", card_border="#2A3566", chip="#141C45", metal="#1C2550",
    ),
    "light": dict(
        bg0="#FFFFFF", bg1="#EAF0FF", border="#D3DBF0",
        text="#0B1228", muted="#55618A", faint="#5F6A94",
        dot="#0B1228", dot_o="0.07",
        a="#0369A1", b="#6A3DF5", green="#047857",
        glow_a="0.14", glow_b="0.16",
        card="#FFFFFF", card_border="#D3DBF0", chip="#EEF2FF", metal="#C4CDE8",
    ),
}

# Devices keep the same dark look in both themes.
D = dict(
    body="#05070F", bezel="#2B3558", screen="#0D1330", row="#141C45",
    line="#3A4788", line2="#252F60", ink="#F4F7FF", sub="#8E9BC2",
    green="#3DDC97", a="#4FC3F7", b="#8B6CFF",
)


def frame(t, w, h, r, body, css="", defs="", glows="", title="", reduced="", fade=(0.7, 0.45)):
    """Shared card: gradient background, soft glows, dot grid, hairline border."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['a']}"/><stop offset="1" stop-color="{t['b']}"/></linearGradient>
<linearGradient id="accentD" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{D['a']}"/><stop offset="1" stop-color="{D['b']}"/></linearGradient>
<radialGradient id="glowA"><stop offset="0" stop-color="{t['a']}" stop-opacity="{t['glow_a']}"/><stop offset="1" stop-color="{t['a']}" stop-opacity="0"/></radialGradient>
<radialGradient id="glowB"><stop offset="0" stop-color="{t['b']}" stop-opacity="{t['glow_b']}"/><stop offset="1" stop-color="{t['b']}" stop-opacity="0"/></radialGradient>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{t['dot']}" fill-opacity="{t['dot_o']}"/></pattern>
<radialGradient id="fade" cx="{fade[0]}" cy="{fade[1]}" r=".75"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="gridMask"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>
<clipPath id="frame"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>
{defs}
</defs>
<style>
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
{css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}{reduced}}}
</style>
<g clip-path="url(#frame)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
{glows}
<rect width="{w}" height="{h}" fill="url(#dots)" mask="url(#gridMask)"/>
{body}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{t['border']}"/>
</svg>
'''


def code(lines, x, y, lh, size, palette):
    """lines: list of (indent, [(text, colour key), ...]). Returns <text> rows."""
    adv = size * 0.6
    out = []
    for i, (indent, segs) in enumerate(lines):
        spans = "".join(f'<tspan fill="{palette[c]}">{s}</tspan>' for s, c in segs)
        out.append(f'<text class="mono l{i}" x="{x + indent * adv:.1f}" y="{y + i * lh}" font-size="{size}">{spans}</text>')
    return "".join(out)


# ------------------------------------------------------------- banner + typing

NAME = "Chisanupong"
ROLE = "Mobile Developer · Flutter + .NET"
# Lines typed under the name in the banner: (text, seconds on screen).
TYPED = [
    (ROLE, 6.5),
    ("Building WMS apps for the warehouse floor", 4.4),
    ("…and the .NET services behind them", 4.4),
    ("Dev tools on the side: VS Code extensions + more", 4.4),
    ("Based in Bangkok, Thailand", 4.0),
]
FLUTTER_DEEP, FLUTTER_SKY = "#023F78", "#0FA3EC"
# SMIL ignores prefers-reduced-motion, so every animated shape has a still twin.
STILL_CSS = ".still{display:none}@media (prefers-reduced-motion:reduce){.live{display:none}.still{display:inline}}"


def _wave(d1, d2, dur, opacity=1):
    return (
        f'<path class="live" fill="url(#g)" opacity="{opacity}" d="{d1}"><animate attributeName="d" dur="{dur}s" repeatCount="indefinite" '
        f'values="{d1};{d2};{d1}" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></path>'
        f'<path class="still" fill="url(#g)" opacity="{opacity}" d="{d1}"/>'
    )


def wave_header(_t):
    """Flutter-blue banner with a slow wave along the bottom edge. Same file for both themes."""
    front = ("M0 0H1200V196C1010 252 800 150 600 192C400 234 190 250 0 204Z",
             "M0 0H1200V214C1010 172 800 240 600 212C400 184 190 204 0 232Z")
    back = ("M0 0H1200V222C990 268 770 188 570 226C380 262 180 222 0 250Z",
            "M0 0H1200V240C990 206 770 262 570 240C380 216 180 250 0 226Z")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 270" width="1200" height="270" role="img" aria-label="{NAME}. {ROLE}">
<title>{NAME}. {ROLE}</title>
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1.4" y2="0"><stop offset="0" stop-color="{FLUTTER_DEEP}"/><stop offset="1" stop-color="{FLUTTER_SKY}"/></linearGradient>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" fill="#fff" fill-opacity=".22"/></pattern>
<radialGradient id="fade" cx=".9" cy="0" r=".55"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="fade2" cx=".08" cy=".1" r=".4"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="m"><rect width="1200" height="170" fill="url(#fade)"/><rect width="1200" height="170" fill="url(#fade2)"/></mask>
<clipPath id="top"><rect width="1200" height="400" rx="20"/></clipPath>
</defs>
<style>.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}{STILL_CSS}</style>
<g clip-path="url(#top)">
{_wave(back[0], back[1], 17, .38)}
{_wave(front[0], front[1], 11)}
<rect width="1200" height="170" fill="url(#dots)" mask="url(#m)"/>
</g>
<text class="sans" x="600" y="108" text-anchor="middle" font-size="68" font-weight="800" letter-spacing="-1.5" fill="#fff">{NAME}</text>
<g class="live">{_typed(600, 147, 22, "#fff")}</g>
<text class="sans still" x="600" y="154" text-anchor="middle" font-size="23" font-weight="500" fill="#fff">{ROLE}</text>
</svg>
'''


def wave_footer(_t):
    front = ("M0 130H1200V48C1010 4 800 86 600 52C400 18 190 30 0 62Z",
             "M0 130H1200V34C1010 70 800 10 600 40C400 70 190 60 0 30Z")
    back = ("M0 130H1200V24C990 -6 770 66 570 34C380 4 180 34 0 40Z",
            "M0 130H1200V10C990 44 770 -4 570 22C380 46 180 6 0 50Z")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 130" width="1200" height="130" role="presentation">
<defs>
<linearGradient id="g" x1="-.4" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{FLUTTER_SKY}"/><stop offset="1" stop-color="{FLUTTER_DEEP}"/></linearGradient>
<clipPath id="bottom"><rect y="-300" width="1200" height="430" rx="20"/></clipPath>
</defs>
<style>{STILL_CSS}</style>
<g clip-path="url(#bottom)">
{_wave(back[0], back[1], 17, .38)}
{_wave(front[0], front[1], 11)}
</g>
</svg>
'''


def _typed(cx, y, size, fill, span=1200):
    """Typed lines: each sits on a path that grows across the span the centred
    text occupies, so glyphs appear one at a time. Pure SMIL, transparent."""
    adv, n, rows = size * 0.6, len(TYPED), []
    for i, (line, dur) in enumerate(TYPED):
        begin = f"0s;d{n - 1}.end" if i == 0 else f"d{i - 1}.end"
        half = len(line) * adv / 2 + 18
        lo, hi = max(0, round(cx - half)), min(span, round(cx + half))
        rows.append(
            f'<path id="p{i}" fill="none"><animate id="d{i}" attributeName="d" begin="{begin}" dur="{dur}s" fill="remove" '
            f'values="m0,{y} h{lo};m0,{y} h{hi};m0,{y} h{hi};m0,{y} h{lo}" keyTimes="0;{1.5 / dur:.3f};{1 - 0.6 / dur:.3f};1"/></path>'
            f'<text class="mono" x="{cx}" text-anchor="middle" dominant-baseline="middle" font-size="{size}" font-weight="600" fill="{fill}">'
            f'<textPath href="#p{i}" xlink:href="#p{i}">{line}</textPath></text>'
        )
    return "".join(rows)


# ------------------------------------------------------------------- about card

def about(t):
    """About me, written as the Dart file it would be. Sits next to the phone."""
    pal = dict(text=t["text"], muted=t["muted"], kw=t["b"], ty=t["a"], s=t["green"])
    K, T, S, P, X = "kw", "ty", "s", "muted", "text"
    lines = [
        (0, [("class", K), (" Chisanupong", T), (" extends", K), (" MobileDeveloper", T), (" {", P)]),
        (2, [("final", K), (" base", X), (" = ", P), ("'Bangkok, Thailand'", S), (";", P)]),
        (2, [("final", K), (" dayJob", X), (" = ", P), ("'WMS apps in Flutter'", S), (";", P)]),
        (2, [("final", K), (" alsoOn", X), (" = ", P), ("'.NET services + SQL'", S), (";", P)]),
        (2, [("final", K), (" sideProjects", X), (" = [", P)]),
        (4, [("'extendedscreen'", S), (", ", P), ("'hooktrans'", S), (",", P)]),
        (4, [("'api-to-model'", S), (", ", P), ("'file-order'", S), (",", P)]),
        (4, [("'sql-guard'", S), (",", P)]),
        (2, [("];", P)]),
        (0, []),
        (2, [("bool", T), (" get", K), (" openToCollab", X), (" =&gt; ", P), ("true", K), (";", P)]),
        (0, [("}", P)]),
    ]
    x0, y0, lh, size = 66, 92, 30, 20
    active = 10  # the line the cursor sits on
    nums = "".join(
        f'<text class="mono" x="46" y="{y0 + i * lh}" font-size="17" text-anchor="end" fill="{t["faint"]}">{i + 1}</text>'
        for i in range(len(lines))
    )
    cursor_x = x0 + (2 + len("bool get openToCollab => true;")) * size * 0.6 + 4
    css = (
        ".blink{animation:blink 1.1s steps(1,end) infinite}@keyframes blink{0%{opacity:1}50%,100%{opacity:0}}"
    )
    glows = '<circle cx="700" cy="50" r="300" fill="url(#glowB)"/><circle cx="80" cy="470" r="260" fill="url(#glowA)"/>'
    body = f'''
<circle cx="28" cy="26" r="6" fill="#FF6B6B"/><circle cx="48" cy="26" r="6" fill="#FFC857"/><circle cx="68" cy="26" r="6" fill="#3DDC97"/>
<rect x="96" y="11" width="190" height="30" rx="9" fill="{t['chip']}" stroke="{t['card_border']}"/>
<circle cx="113" cy="26" r="4.5" fill="{t['a']}"/>
<text class="mono" x="125" y="32" font-size="17" font-weight="600" fill="{t['text']}">about_me.dart</text>
<rect x="552" y="11" width="224" height="30" rx="15" fill="{t['chip']}" stroke="{t['card_border']}"/>
<circle cx="572" cy="26" r="4.5" fill="{t['green']}"/>
<text class="mono" x="586" y="31.5" font-size="16.5" fill="{t['muted']}">running on device</text>
<path d="M0 52.5H800" stroke="{t['card_border']}"/>
<rect y="{y0 + active * lh - 21}" width="800" height="{lh}" fill="{t['a']}" fill-opacity=".08"/>
<rect y="{y0 + active * lh - 21}" width="3" height="{lh}" fill="{t['a']}"/>
{nums}
{code(lines, x0, y0, lh, size, pal)}
<rect class="blink" x="{cursor_x:.0f}" y="{y0 + active * lh - 17}" width="10" height="23" rx="2" fill="{t['a']}"/>
'''
    return frame(t, 800, 452, 20, body, css, "", glows,
                 title="about_me.dart. class Chisanupong extends MobileDeveloper. Based in Bangkok, Thailand. "
                       "Day job: WMS apps in Flutter, plus .NET services and SQL. "
                       "Side projects: extendedscreen, hooktrans, api-to-model, file-order, sql-guard.",
                 fade=(0.8, 0.3))


# ------------------------------------------------------------------------ phone

def phone(_t):
    """A warehouse pick list that scans and ticks itself off. Same file for both themes."""
    marks = [12, 37, 62]
    rows_css, rows = [], []
    for i in range(5):
        y = 198 + 44 * i
        w1, w2 = [78, 64, 84, 70, 60][i], [46, 52, 38, 48, 44][i]
        anim = i < len(marks)
        if anim:
            p = marks[i]
            rows_css.append(
                f"@keyframes ck{i}{{0%,{p}%{{stroke-dashoffset:16}}{p + 4}%,94%{{stroke-dashoffset:0}}98%,100%{{stroke-dashoffset:16}}}}"
                f"@keyframes fi{i}{{0%,{p}%{{fill-opacity:0}}{p + 3}%,94%{{fill-opacity:1}}98%,100%{{fill-opacity:0}}}}"
                f"@keyframes dm{i}{{0%,{p}%{{opacity:1}}{p + 4}%,94%{{opacity:.4}}98%,100%{{opacity:1}}}}"
                f".ck{i}{{animation:ck{i} 8s ease-out infinite}}.fi{i}{{animation:fi{i} 8s ease-out infinite}}.dm{i}{{animation:dm{i} 8s ease-out infinite}}"
            )
        rows.append(
            f'<rect x="22" y="{y}" width="172" height="36" rx="10" fill="{D["row"]}"/>'
            f'<circle cx="42" cy="{y + 18}" r="8" fill="none" stroke="{D["line"]}" stroke-width="1.5"/>'
            + (
                f'<circle class="fi{i}" cx="42" cy="{y + 18}" r="8.75" fill="{D["green"]}" fill-opacity="0"/>'
                f'<path class="ck ck{i}" d="M38.3 {y + 18.4}l2.6 2.6 5-5.6" stroke="{D["body"]}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                if anim else ""
            )
            + f'<g class="dm{i}"><rect x="60" y="{y + 10}" width="{w1}" height="6" rx="3" fill="{D["line"]}"/>'
            f'<rect x="60" y="{y + 21}" width="{w2}" height="5" rx="2.5" fill="{D["line2"]}"/></g>'
            f'<rect x="156" y="{y + 10}" width="26" height="16" rx="8" fill="{D["line2"]}"/>'
        )

    pattern = [3, 1, 2, 1, 1, 3, 2, 1, 3, 1, 1, 2, 3, 1, 2, 2, 1, 1, 3, 1, 2, 1, 3, 2, 1, 1, 2, 3, 1, 2, 3]
    unit = 124 / sum(pattern)
    bars, bx = [], 46.0
    for i, n in enumerate(pattern):
        if i % 2 == 0:
            bars.append(f'<rect x="{bx:.1f}" y="122" width="{n * unit:.1f}" height="48"/>')
        bx += n * unit

    css = (
        ".ck{stroke-dasharray:16;stroke-dashoffset:16}"
        + "".join(rows_css)
        + ".prog{animation:prog 8s ease-out infinite}"
        "@keyframes prog{0%,12%{transform:translateX(-168px)}15%,37%{transform:translateX(-134.4px)}"
        "40%,62%{transform:translateX(-100.8px)}65%,94%{transform:translateX(-67.2px)}98%,100%{transform:translateX(-168px)}}"
        ".scan{animation:scan 1.7s ease-in-out infinite alternate}@keyframes scan{from{transform:translateY(0)}to{transform:translateY(44px)}}"
        ".resp{animation:resp 2.7s linear infinite}@keyframes resp{0%,40%{opacity:.3}48%,100%{opacity:1}}"
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 384" width="330" height="384" role="img" aria-label="A phone showing a warehouse pick list that scans a barcode and ticks items off">
<defs>
<radialGradient id="halo"><stop offset="0" stop-color="{D['a']}" stop-opacity=".34"/><stop offset=".6" stop-color="{D['b']}" stop-opacity=".16"/><stop offset="1" stop-color="{D['b']}" stop-opacity="0"/></radialGradient>
<linearGradient id="accentD" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{D['a']}"/><stop offset="1" stop-color="{D['b']}"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{D['a']}" stop-opacity="0"/><stop offset=".5" stop-color="{D['a']}" stop-opacity=".32"/><stop offset="1" stop-color="{D['a']}" stop-opacity="0"/></linearGradient>
<clipPath id="track"><rect x="24" y="90" width="168" height="4" rx="2"/></clipPath>
</defs>
<style>
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
{css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<circle cx="168" cy="190" r="165" fill="url(#halo)"/>
<g transform="translate(86 20) rotate(5 82 167) scale(.76)">
<rect x="-8" y="12" width="216" height="440" rx="36" fill="#000" fill-opacity=".2"/>
<rect width="216" height="440" rx="36" fill="{D['body']}" stroke="{D['bezel']}" stroke-width="2"/>
<rect x="8" y="8" width="200" height="424" rx="29" fill="{D['screen']}"/>
<rect x="78" y="17" width="60" height="16" rx="8" fill="{D['body']}"/>
<text class="sans" x="24" y="64" font-size="16" font-weight="700" fill="{D['ink']}">Pick list</text>
<text class="sans" x="24" y="81" font-size="11" fill="{D['sub']}">Zone B · 5 items</text>
<g clip-path="url(#track)"><rect x="24" y="90" width="168" height="4" fill="{D['row']}"/><rect class="prog" x="24" y="90" width="168" height="4" rx="2" fill="url(#accentD)"/></g>
<rect x="22" y="106" width="172" height="80" rx="12" fill="#070B1C" stroke="{D['line2']}"/>
<g fill="{D['ink']}" fill-opacity=".86">{"".join(bars)}</g>
<path d="M32 124v-8h8M184 124v-8h-8M32 168v8h8M184 168v8h-8" fill="none" stroke="{D['a']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<g class="scan"><rect x="32" y="117" width="152" height="16" fill="url(#beam)"/><rect x="32" y="124" width="152" height="2" rx="1" fill="{D['a']}"/></g>
{"".join(rows)}
</g>
<g><g transform="translate(8 266)">
<rect x="3" y="6" width="170" height="64" rx="13" fill="#000" fill-opacity=".28"/>
<rect width="170" height="64" rx="13" fill="#0D1432" stroke="#2A3566"/>
<text class="mono" x="15" y="27" font-size="12"><tspan fill="{D['b']}" font-weight="700">POST</tspan><tspan fill="{D['ink']}"> /pick/confirm</tspan></text>
<text class="mono resp" x="15" y="48" font-size="12"><tspan fill="{D['green']}" font-weight="700">200 OK</tspan><tspan fill="{D['sub']}"> · 38 ms</tspan></text>
</g></g>
</svg>
'''


# ------------------------------------------------------------- icons + button

# One stroke colour that reads on both GitHub themes (3.4:1 on white, 5.5:1 on dark).
ICON_STROKE = "#1A8FE3"
ICONS = {
    "projects": '<path d="M12 2.6l8.4 4.7v9.4L12 21.4l-8.4-4.7V7.3z"/><path d="M3.6 7.3L12 12l8.4-4.7M12 12v9.4"/>',
    "about": '<path d="M8.5 7.5L4 12l4.5 4.5M15.5 7.5L20 12l-4.5 4.5M13.4 5l-2.8 14"/>',
    "log": '<path d="M4.4 16H2.6V6.4h10.6V16H8.6M13.2 9.4h3.9l3.3 3.5V16h-1.3M14.9 16H8.6"/>'
           '<circle cx="6.5" cy="17" r="2.1"/><circle cx="17" cy="17" r="2.1"/>',
    "contact": '<path d="M4.2 5h15.6a1.6 1.6 0 0 1 1.6 1.6v8.8a1.6 1.6 0 0 1-1.6 1.6H10.4L6 20.6V17H4.2a1.6 1.6 0 0 1-1.6-1.6V6.6A1.6 1.6 0 0 1 4.2 5z"/>'
               '<path d="M7.2 9.4h9.6M7.2 12.8h5.8"/>',
}


def icon(name):
    """Heading icon: one line weight and one colour for all of them."""
    def build(_t):
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="{ICON_STROKE}" '
            f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" role="presentation">{ICONS[name]}</svg>\n'
        )
    return build


def cta(_t):
    """The one primary button on the page. 48 units tall so it shows as a 44px touch target."""
    w, h = 296, 48
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="See my repositories">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{FLUTTER_DEEP}"/><stop offset="1" stop-color="#0A7BC4"/></linearGradient></defs>
<style>.sans{{font-family:{SANS}}}</style>
<rect width="{w}" height="{h}" rx="{h // 2}" fill="url(#g)"/>
<text class="sans" x="130" y="30" text-anchor="middle" font-size="17" font-weight="600" fill="#fff">See my repositories</text>
<path d="M234 24h20m-7.500-7.500 7.500 7.500-7.500 7.500" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''


# ---------------------------------------------------------------- project thumbs

def thumb_extendedscreen(t):
    def win(x):
        return (
            f'<g transform="translate({x} 112)"><rect width="112" height="70" rx="7" fill="#F4F7FF"/>'
            '<path d="M0 7a7 7 0 0 1 7-7h98a7 7 0 0 1 7 7v9H0z" fill="#DCE3F7"/>'
            '<circle cx="10" cy="8" r="2.5" fill="#FF6B6B"/><circle cx="19" cy="8" r="2.5" fill="#FFC857"/><circle cx="28" cy="8" r="2.5" fill="#3DDC97"/>'
            '<rect x="10" y="26" width="58" height="6" rx="3" fill="#8B6CFF"/><rect x="10" y="38" width="92" height="5" rx="2.5" fill="#C3CCE8"/>'
            '<rect x="10" y="48" width="76" height="5" rx="2.5" fill="#C3CCE8"/><rect x="10" y="58" width="40" height="5" rx="2.5" fill="#C3CCE8"/></g>'
        )

    css = (
        ".slide{animation:slide 7s cubic-bezier(.65,0,.35,1) infinite}"
        "@keyframes slide{0%,12%{transform:translateX(0)}44%,62%{transform:translateX(228px)}94%,100%{transform:translateX(0)}}"
        ".flow{animation:flow 1s linear infinite}@keyframes flow{to{stroke-dashoffset:-24}}"
    )
    defs = (
        '<clipPath id="lap"><rect x="64" y="70" width="248" height="152" rx="5"/></clipPath>'
        '<clipPath id="tab"><rect x="400" y="100" width="144" height="100" rx="5"/></clipPath>'
        f'<linearGradient id="wall" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{D["a"]}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{D["b"]}" stop-opacity=".3"/></linearGradient>'
    )
    glows = '<circle cx="470" cy="50" r="230" fill="url(#glowB)"/><circle cx="110" cy="300" r="210" fill="url(#glowA)"/>'
    body = f'''
<text class="mono" x="188" y="46" font-size="12.5" text-anchor="middle" fill="{t['muted']}">macOS · host</text>
<text class="mono" x="472" y="76" font-size="12.5" text-anchor="middle" fill="{t['muted']}">Android · client</text>
<rect x="56" y="62" width="264" height="168" rx="12" fill="{D['body']}" stroke="{D['bezel']}" stroke-width="1.5"/>
<rect x="64" y="70" width="248" height="152" rx="5" fill="{D['screen']}"/><rect x="64" y="70" width="248" height="152" rx="5" fill="url(#wall)"/>
<g clip-path="url(#lap)"><rect x="64" y="70" width="248" height="11" fill="#000" fill-opacity=".28"/><g class="slide">{win(96)}</g></g>
<rect x="30" y="230" width="316" height="9" rx="4.5" fill="{t['metal']}"/>
<rect x="392" y="92" width="160" height="116" rx="12" fill="{D['body']}" stroke="{D['bezel']}" stroke-width="1.5"/>
<rect x="400" y="100" width="144" height="100" rx="5" fill="{D['screen']}"/><rect x="400" y="100" width="144" height="100" rx="5" fill="url(#wall)"/>
<g clip-path="url(#tab)"><g class="slide">{win(184)}</g></g>
<path class="flow" d="M346 235C400 272 472 270 472 210" fill="none" stroke="url(#accent)" stroke-width="2.5" stroke-dasharray="5 7" stroke-linecap="round"/>
<text class="mono" x="404" y="284" font-size="12" text-anchor="middle" fill="{t['faint']}">USB · H.264 / H.265</text>
'''
    return frame(t, 600, 300, 20, body, css, defs, glows,
                 title="extendedscreen: a window sliding from a Mac onto an Android tablet used as a second display")


def thumb_hooktrans(t):
    css = (
        ".jp{opacity:0;animation:jp 10s linear infinite}.th{opacity:0;animation:th 10s linear infinite}.pB{animation-delay:-5s}"
        "@keyframes jp{0%{opacity:0}3%,46%{opacity:1}50%,100%{opacity:0}}"
        "@keyframes th{0%,9%{opacity:0;transform:translateY(5px)}13%,46%{opacity:1;transform:translateY(0)}50%,100%{opacity:0;transform:translateY(0)}}"
        ".sweep{animation:sweep 5s linear infinite}@keyframes sweep{0%,2%{transform:translateX(0)}16%,100%{transform:translateX(500px)}}"
        ".ld{opacity:0;animation:ld 5s linear infinite}@keyframes ld{0%,3%{opacity:0}5%,17%{opacity:1}19%,100%{opacity:0}}"
    )
    defs = (
        '<clipPath id="scene"><rect x="60" y="34" width="480" height="232" rx="14"/></clipPath>'
        '<clipPath id="dlg"><rect x="84" y="150" width="432" height="42" rx="8"/></clipPath>'
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1B6B"/><stop offset="1" stop-color="#0B1030"/></linearGradient>'
        '<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".3"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    glows = '<circle cx="120" cy="40" r="220" fill="url(#glowB)"/><circle cx="520" cy="290" r="220" fill="url(#glowA)"/>'
    stars = "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" fill-opacity=".7"/>'
        for x, y, r, d in [(96, 62, 1.4, 0.2), (150, 96, 1, 1.4), (214, 58, 1.6, 2.1), (286, 84, 1, 0.8), (338, 54, 1.3, 2.6), (392, 104, 1, 1.1), (506, 132, 1.2, 1.9), (520, 60, 1, 0.5)]
    )
    body = f'''
<g clip-path="url(#scene)">
<rect x="60" y="34" width="480" height="232" fill="url(#sky)"/>
{stars}
<circle cx="452" cy="86" r="24" fill="#FFE9A8"/><circle cx="463" cy="79" r="22" fill="#281A66"/>
<path d="M60 176Q140 112 230 160T400 150T540 170V266H60Z" fill="#1A1250"/>
<path d="M60 206Q180 156 300 198T540 190V266H60Z" fill="#100B36"/>
</g>
<rect x="60.5" y="34.5" width="479" height="231" rx="13.5" fill="none" stroke="{D['bezel']}"/>
<rect x="84" y="150" width="432" height="42" rx="8" fill="#05070F" fill-opacity=".66" stroke="#fff" stroke-opacity=".22"/>
<g clip-path="url(#dlg)"><rect class="sweep" x="24" y="150" width="60" height="42" fill="url(#shine)"/></g>
<text class="sans jp" x="100" y="177" font-size="17" fill="#fff">こんにちは、旅人さん。</text>
<text class="sans jp pB" x="100" y="177" font-size="17" fill="#fff">ここは危険だ、気をつけて。</text>
<rect x="84" y="202" width="432" height="44" rx="10" fill="#0D1432" fill-opacity=".95" stroke="url(#accentD)" stroke-width="1.5"/>
<rect x="94" y="212" width="36" height="24" rx="7" fill="url(#accentD)"/>
<text class="mono" x="112" y="228.5" font-size="12" font-weight="700" text-anchor="middle" fill="#fff">TH</text>
<g class="ld" fill="{D['sub']}"><circle cx="148" cy="224" r="3"/><circle cx="160" cy="224" r="3"/><circle cx="172" cy="224" r="3"/></g>
<text class="sans th" x="142" y="230" font-size="17" font-weight="600" fill="#fff">สวัสดี นักเดินทาง</text>
<text class="sans th pB" x="142" y="230" font-size="17" font-weight="600" fill="#fff">ที่นี่อันตราย ระวังตัวด้วย</text>
'''
    return frame(t, 600, 300, 20, body, css, defs, glows,
                 title="hooktrans: Japanese game dialogue translated to Thai in a floating overlay",
                 reduced=".jp,.th{opacity:1}.pB{opacity:0}")


def thumb_api_to_model(t):
    pal = dict(text=t["text"], muted=t["muted"], key=t["a"], num=t["b"], s=t["green"], kw=t["b"], ty=t["a"])
    left = [
        (0, [("{", "muted")]),
        (2, [('"id"', "key"), (": ", "muted"), ("1", "num"), (",", "muted")]),
        (2, [('"name"', "key"), (": ", "muted"), ('"Ada"', "s"), (",", "muted")]),
        (2, [('"active"', "key"), (": ", "muted"), ("true", "num")]),
        (0, [("}", "muted")]),
    ]
    right = [
        (0, [("class", "kw"), (" User ", "ty"), ("{", "muted")]),
        (2, [("final", "kw"), (" int", "ty"), (" id", "text"), (";", "muted")]),
        (2, [("final", "kw"), (" String", "ty"), (" name", "text"), (";", "muted")]),
        (2, [("final", "kw"), (" bool", "ty"), (" active", "text"), (";", "muted")]),
        (0, [("}", "muted")]),
    ]
    css = "".join(
        f"@keyframes ln{k}{{0%,{14 + 8 * k}%{{opacity:0}}{17 + 8 * k}%,94%{{opacity:1}}98%,100%{{opacity:0}}}}"
        f".out .l{k}{{opacity:0;animation:ln{k} 6s linear infinite}}"
        for k in range(len(right))
    )
    buttons = ""
    bx = 344
    for label in ["Copy", "Insert", "Save"]:
        w = len(label) * 6.6 + 20
        buttons += (
            f'<rect x="{bx}" y="222" width="{w:.1f}" height="24" rx="12" fill="{t["chip"]}" stroke="{t["card_border"]}"/>'
            f'<text class="mono" x="{bx + w / 2:.1f}" y="238" font-size="11" text-anchor="middle" fill="{t["muted"]}">{label}</text>'
        )
        bx = round(bx + w + 8, 1)
    glows = '<circle cx="300" cy="150" r="230" fill="url(#glowB)"/><circle cx="60" cy="300" r="180" fill="url(#glowA)"/>'
    body = f'''
<rect x="26" y="36" width="246" height="228" rx="12" fill="{t['card']}" stroke="{t['card_border']}"/>
<text class="mono" x="44" y="60" font-size="12" font-weight="700" fill="{t['text']}">cURL</text>
<rect x="42" y="69" width="34" height="2" rx="1" fill="url(#accent)"/>
<text class="mono" x="94" y="60" font-size="12" fill="{t['faint']}">JSON</text>
<path d="M26 70.5H272" stroke="{t['card_border']}"/>
<text class="mono" x="44" y="98" font-size="13"><tspan fill="{t['a']}" font-weight="700">›</tspan><tspan fill="{t['text']}"> curl api.dev/users/1</tspan></text>
<path d="M44 112.5H254" stroke="{t['card_border']}" stroke-dasharray="2 4"/>
{code(left, 44, 138, 22, 13, pal)}
<circle cx="300" cy="150" r="18" fill="url(#accent)"/>
<path d="M292.5 150h14m-5.5-5.5 5.5 5.5-5.5 5.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="328" y="36" width="246" height="228" rx="12" fill="{t['card']}" stroke="{t['card_border']}"/>
<circle cx="349" cy="56" r="4" fill="{t['a']}"/>
<text class="mono" x="360" y="60" font-size="12" font-weight="700" fill="{t['text']}">user.dart</text>
<path d="M328 70.5H574" stroke="{t['card_border']}"/>
<g class="out">{code(right, 346, 98, 22, 13, pal)}</g>
{buttons}
'''
    return frame(t, 600, 300, 20, body, css, "", glows,
                 title="api-to-model: a cURL response turning into a Dart model class",
                 reduced=".out text{opacity:1}", fade=(0.5, 0.5))


def thumb_file_order(t):
    folder = "M0 3.5a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2z"
    doc = "M2.5.6h6.2l4 4v9.3a1.5 1.5 0 0 1-1.5 1.5H2.5A1.5 1.5 0 0 1 1 13.9V2.1A1.5 1.5 0 0 1 2.5.6zM8.5.8v4h4"
    items = [("src", True), ("test", True), ("README.md", False), ("package.json", False), ("tsconfig.json", False)]
    css = (
        ".up{animation:up 6s cubic-bezier(.65,0,.35,1) infinite}.down{animation:down 6s cubic-bezier(.65,0,.35,1) infinite}"
        "@keyframes up{0%,22%{transform:translateY(0)}34%,72%{transform:translateY(-38px)}84%,100%{transform:translateY(0)}}"
        "@keyframes down{0%,22%{transform:translateY(0)}34%,72%{transform:translateY(38px)}84%,100%{transform:translateY(0)}}"
    )
    rows = ""
    for i, (name, is_dir) in enumerate(items):
        y = 72 + 38 * i
        cls = {2: ' class="down"', 3: ' class="up"'}.get(i, "")
        icon = (
            f'<path transform="translate(162 {y + 11})" d="{folder}" fill="{t["a"]}" fill-opacity=".85"/>' if is_dir
            else f'<path transform="translate(163 {y + 11})" d="{doc}" fill="none" stroke="{t["muted"]}" stroke-width="1.3" stroke-linejoin="round"/>'
        )
        rows += (
            f'<g{cls}>{icon}<text class="mono" x="190" y="{y + 24}" font-size="14" fill="{t["text"]}">{name}</text></g>'
            f'<rect x="404" y="{y + 9}" width="42" height="20" rx="10" fill="{t["chip"]}" stroke="{t["card_border"]}"/>'
            f'<text class="mono" x="425" y="{y + 23.2}" font-size="12" text-anchor="middle" fill="{t["a"]}">#{(i + 1) * 10}</text>'
        )
    glows = '<circle cx="80" cy="60" r="230" fill="url(#glowA)"/><circle cx="540" cy="260" r="230" fill="url(#glowB)"/>'
    body = f'''
<rect x="140" y="26" width="320" height="248" rx="12" fill="{t['card']}" stroke="{t['card_border']}"/>
<text class="mono" x="160" y="50" font-size="11" letter-spacing="1.5" fill="{t['faint']}">FILE ORDER</text>
<path d="M418 42v10m-3.5-6.5 3.5-3.5 3.5 3.5M436 42v10m-3.5-3.5 3.5 3.5 3.5-3.5" fill="none" stroke="{t['faint']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M140 62.5H460" stroke="{t['card_border']}"/>
<rect class="up" x="148" y="189" width="304" height="32" rx="8" fill="{t['a']}" fill-opacity=".13" stroke="{t['a']}" stroke-opacity=".4"/>
{rows}
'''
    return frame(t, 600, 300, 20, body, css, "", glows,
                 title="file-order: files in a sidebar tree reordered by priority number", fade=(0.5, 0.5))


def thumb_sql_guard(t):
    dark = t is THEMES["dark"]
    danger = "#FF6B6B" if dark else "#C92A2A"
    warn = "#FFC857" if dark else "#B45309"
    pal = dict(text=t["text"], muted=t["muted"], kw=t["b"], s=t["green"])
    K, X, S, P = "kw", "text", "s", "muted"
    lines = [
        (0, [("-- #region archive old orders", P)]),
        (0, [("UPDATE", K), (" Orders", X), (" SET", K), (" Status", X), (" = ", P), ("'archived'", S)]),
        (0, [("WHERE", K), (" CreatedAt", X), (" &lt; ", P), ("'2025-01-01'", S), (";", P)]),
        (0, []),
        (0, [("DELETE", K), (" FROM", K), (" OrderItems", X), (";", P)]),
        (0, [("-- #endregion", P)]),
    ]
    x0, y0, lh, size = 58, 110, 24, 14
    flagged = 4  # the statement the guard stops
    css = (
        ".flag{opacity:0;animation:flag 7s ease-out infinite}@keyframes flag{0%,12%{opacity:0}18%,86%{opacity:1}92%,100%{opacity:0}}"
        ".dlg{opacity:0;animation:dlg 7s ease-out infinite}"
        "@keyframes dlg{0%,20%{opacity:0;transform:translateY(8px)}27%,86%{opacity:1;transform:translateY(0)}92%,100%{opacity:0;transform:translateY(0)}}"
    )
    glows = '<circle cx="520" cy="40" r="230" fill="url(#glowB)"/><circle cx="70" cy="290" r="200" fill="url(#glowA)"/>'
    body = f'''
<rect x="36" y="34" width="528" height="232" rx="12" fill="{t['card']}" stroke="{t['card_border']}"/>
<circle cx="57" cy="53" r="4" fill="{t['a']}"/>
<text class="mono" x="68" y="57" font-size="12" font-weight="700" fill="{t['text']}">cleanup.sql</text>
<path d="M36 70.5H564" stroke="{t['card_border']}"/>
<text class="mono" x="{x0}" y="90" font-size="11" fill="{t['muted']}">▶ Run</text>
<g class="flag"><rect x="37" y="{y0 + flagged * lh - 17}" width="526" height="{lh}" fill="{danger}" fill-opacity=".14"/><rect x="37" y="{y0 + flagged * lh - 17}" width="3" height="{lh}" fill="{danger}"/></g>
{code(lines, x0, y0, lh, size, pal)}
<g class="dlg">
<rect x="266" y="134" width="286" height="122" rx="12" fill="#000" fill-opacity=".28"/>
<rect x="262" y="128" width="286" height="122" rx="12" fill="{t['card']}" stroke="{danger}" stroke-width="1.5"/>
<g transform="translate(280 144)" fill="none" stroke="{warn}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 1.5l7 2.6v5.2c0 4.3-2.9 7.6-7 9.2-4.1-1.6-7-4.9-7-9.2V4.1z" fill="{warn}" fill-opacity=".16"/><path d="M10 6.5v4.5M10 14v.1"/></g>
<text class="sans" x="310" y="159" font-size="14.5" font-weight="700" fill="{t['text']}">DELETE without WHERE</text>
<text class="sans" x="310" y="180" font-size="12" fill="{t['muted']}">Every row in OrderItems would go.</text>
<rect x="310" y="202" width="92" height="30" rx="8" fill="#1B6FD1"/>
<text class="sans" x="356" y="221.5" font-size="12.5" font-weight="600" text-anchor="middle" fill="#fff">Cancel</text>
<rect x="412" y="202" width="118" height="30" rx="8" fill="none" stroke="{danger}" stroke-width="1.3"/>
<text class="sans" x="471" y="221.5" font-size="12.5" font-weight="600" text-anchor="middle" fill="{danger}">Run anyway</text>
</g>
'''
    return frame(t, 600, 300, 20, body, css, "", glows,
                 title="vscode-sql-guard: a confirmation dialog stopping a DELETE that has no WHERE clause",
                 reduced=".flag,.dlg{opacity:1}", fade=(0.5, 0.5))


# name -> (builder, themed?). Unthemed images are written once.
ASSETS = {
    "wave-header": (wave_header, False),
    "wave-footer": (wave_footer, False),
    "about": (about, True),
    "phone": (phone, False),
    "icon-projects": (icon("projects"), False),
    "icon-about": (icon("about"), False),
    "icon-log": (icon("log"), False),
    "icon-contact": (icon("contact"), False),
    "cta-repos": (cta, False),
    "extendedscreen": (thumb_extendedscreen, True),
    "hooktrans": (thumb_hooktrans, True),
    "api-to-model": (thumb_api_to_model, True),
    "file-order": (thumb_file_order, True),
    "sql-guard": (thumb_sql_guard, True),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for name, (build, themed) in ASSETS.items():
        variants = THEMES.items() if themed else [(None, THEMES["dark"])]
        for theme, palette in variants:
            svg = build(palette)
            minidom.parseString(svg.encode("utf-8"))  # fail loudly on malformed XML
            path = OUT / (f"{name}-{theme}.svg" if theme else f"{name}.svg")
            path.write_text(svg, encoding="utf-8")
            print(f"{path.relative_to(OUT.parent)}  {len(svg) / 1024:.1f} kB")
