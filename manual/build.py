"""Builds manual.html (85x130 mm pages, Xenopixel manual style).

Run: python3 build.py   then open manual.html, or print it to PDF.
"""
import html
import math
import re
import subprocess
from pathlib import Path

from hilt import (MM, BLACK, BUTTON_R, BUTTON_Y, HW, KNOB_R, Y, CX, END_Y, JOINT_Y, KNOB_Y, L, POMMEL_R, R, RING, RING_HW, SCREW_HOLES, SLEEVE_SCREW,
                  WIN, POMMEL, POMMEL_SEAM, CORE, CORE_D, core_battery_side, core_board_side, pommel_end, symbols, usb_y)
BLADE_HW = 25.4 * (END_Y - RING[0]) / 310 / 2  # blade half width, true scale
from PIL import Image

GREEN = "#44B03D"


def sent(t):
    """Full sentences end with a period; a trailing confirm tag stays after it."""
    t = t.rstrip()
    return t if t.endswith((".", "?", "!", "</span>")) else t + "."
TODO = '<span class="todo">confirm</span>'


def num(n):
    return (f'<svg class="n" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9"/>'
            f'<text x="10" y="10.5" text-anchor="middle" dominant-baseline="central">{n}</text></svg>')


CSS = """
@page { size: 85mm 491px; margin: 0 }  /* 491px = 129.9 mm: Chrome snaps paper height, a whole-px height that fits leaves no white edge */
* { box-sizing: border-box }
html, body { margin: 0; background: #2a2a2a; -webkit-print-color-adjust: exact; print-color-adjust: exact }
/* type roles, one size each: --title page titles, --sub sub-headings, --body body text and item headings (500),
   --small descriptions, notes, tables, captions, page numbers, --fine fine print and badges */
:root { --title: 10.5pt; --sub: 6.2pt; --body: 5.6pt; --small: 5pt; --fine: 4.6pt }
body { font: var(--body)/1.45 Poppins, sans-serif; color: #BEBEBE }
.spread { display: flex; margin: 0 auto 6mm; width: 170mm }
.page { width: 85mm; height: 130mm; background: #0E0E0E; padding: 8.5mm 8mm 11mm; position: relative; overflow: hidden }
h1 { font: 800 var(--title)/1 Orbitron, sans-serif; letter-spacing: .05em; color: #C8C8C8; margin: 0 0 4mm; display: flex; align-items: center; gap: 2mm; text-transform: uppercase }
h1::before { content: ""; width: 1.1mm; height: 3mm; border-radius: 1mm; background: #E44F44 }
p { margin: 0 }
small { display: block; font-size: var(--fine); line-height: 1.3; color: #8f8f8f }
b { font-weight: 500; color: #D4D4D4 }
/* drawings */
.ln { fill: none; stroke: #D6D6D6; stroke-width: .9; stroke-linejoin: round }
.call { fill: none; stroke: #BDBDBD; stroke-width: .7 }
.call text { fill: #CFCFCF; stroke: none; font: 9px Poppins }
.lead { fill: none; stroke: #8a8a8a; stroke-width: .6; stroke-dasharray: 1.6 1.6 }
.dot { fill: #44B03D; stroke: #FFFFFF }
.photo .lead { stroke: #EDEDED; stroke-dasharray: none; stroke-width: .8 }
.arrow { fill: none; stroke: #44B03D; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round }
.art { display: block; width: 100%; margin: 0 0 3mm }
/* circled numbers */
.n { width: 3.3mm; height: 3.3mm; flex: none; overflow: visible }
.n circle { fill: none; stroke: #BDBDBD; stroke-width: 1 }
.n text { fill: #D4D4D4; font: 500 11px Poppins; font-variant-numeric: tabular-nums }
/* sub-headings: text centered, icon hangs to its left */
.sub { display: flex; justify-content: center; font-size: var(--sub); font-weight: 500; color: #D4D4D4; margin: 4mm 0 1.8mm; line-height: 1 }
h1 + .sub, .page > .sub:first-child { margin-top: 0 }
h1 .h1-sub { font: 500 var(--sub)/1 Poppins, sans-serif; letter-spacing: .02em; color: #9a9a9a; text-transform: none; margin-left: 1mm; white-space: nowrap; line-height: 1.25 }
.sub > span { position: relative }
.sub i { width: 2.9mm; height: 2.9mm; border-radius: 50%; position: absolute; right: calc(100% + 1.4mm); top: 50%; transform: translateY(-50%) }
.sub i::after { content: ""; position: absolute; inset: .75mm; border: .4mm solid #0E0E0E; border-top-color: transparent; border-radius: 50% }
/* tables */
.tbl { width: 100%; border-collapse: separate; border-spacing: 0; font-size: var(--small); line-height: 1.3; text-align: center }
.tbl th { background: #B2B2B2; color: #1a1a1a; font-weight: 500; padding: 1.2mm 1.5mm }
.tbl th:first-child { border-top-left-radius: 1.6mm } .tbl th:last-child { border-top-right-radius: 1.6mm }
.tbl td { background: #131313; border-bottom: .5pt solid #2c2c2c; padding: 1.1mm 1.5mm; vertical-align: middle }
.tbl td + td { border-left: .5pt solid #2c2c2c }
.tbl td:first-child { width: 52% }
.ang td:first-child { width: 36% } .ang td { padding-left: 1mm; padding-right: 1mm }
.spec th, .spec td { text-align: left } .spec td:first-child { width: 36%; color: #9a9a9a }
.ideas td:first-child { width: 84%; color: inherit }
.errs td:first-child { width: 24%; color: #D4D4D4 } .errs td:nth-child(3) { width: 30% }
/* numbered steps */
.step { display: flex; gap: 1.8mm; align-items: flex-start; padding: 1.6mm 0; border-bottom: .5pt solid #3a3a3a }
.step > div { flex: 1; min-width: 0 }
.step svg.pic { display: block; width: 100%; height: 9mm; margin-top: 1.2mm }
/* no line after the last item of a list (:last-of-type misses items followed by a note or the page number) */
.step:not(:has(+ .step)), .press:not(:has(+ .press)), .mo:not(:has(+ .mo)), .qa:not(:has(+ .qa)), .part:not(:has(+ .part)), .ref .row:last-child { border-bottom: 0 }
.nosep .step { border-bottom: 0; padding: 2.2mm 0 }  /* spacing alone separates the steps */
.qstart .step { padding: 3.4mm 0 }
.qstart .step svg.pic, .qstart .duo { height: auto; margin-top: 2mm; margin-left: -5.1mm; width: calc(100% + 5.1mm) }  /* full text width, so the drawings centre on the page */
.qstart .duo { justify-content: center } .qstart .duo svg { flex: 0 0 50% }
.duo { display: flex; gap: 3mm; margin-top: 1.2mm } .duo svg { flex: 1; min-width: 0; height: 11.5mm; overflow: hidden }
.last-right { text-align: justify; text-align-last: right } .just { text-align: justify; text-align-last: justify }  /* the wrapped last line sits at the right, over the low end of the tilted drawing */
/* callout notes */
.tip, .note { font-size: var(--small); line-height: 1.45; color: #A8A8A8; margin-top: 2.5mm; padding-left: 2mm; border-left: .5mm solid #44B03D }
.note { border-left-color: #E44F44 }
/* structure legend */
.legend { display: grid; grid-template-columns: 1.4fr 1fr; gap: 1.4mm 2mm; margin-top: 2.5mm }
.legend div { display: flex; gap: 1.5mm; align-items: center; white-space: nowrap }
/* button page */
.pwr { display: flex; align-items: center; gap: 2.5mm; margin-bottom: 2mm }
.press { display: grid; grid-template-columns: 1fr 26mm; align-items: center; gap: 3mm; padding: 1.3mm 0; border-bottom: .5pt solid #3a3a3a }
.press b { display: block; font-size: var(--body); line-height: 1.3 }
.press span { display: block; font-size: var(--small); line-height: 1.3; color: #9a9a9a }
.press svg { width: 26mm; height: 3.6mm }
/* motion */
.mos { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 4mm }
.mo { display: flex; flex-direction: column; gap: 1.5mm; padding-bottom: 2.5mm; border-bottom: .5pt solid #3a3a3a }
.mo svg { width: 100%; height: 6.5mm; overflow: visible }
.mo svg * { vector-effect: non-scaling-stroke }
.mo b { display: block; font-size: var(--body); line-height: 1.3 }
.mo span { display: block; font-size: var(--small); line-height: 1.4; color: #A0A0A0 }
.mo span.todo { display: inline-block; color: #0E0E0E }
/* troubleshooting */
.qa { display: flex; gap: 1.8mm; padding: 1.8mm 0; border-bottom: .5pt solid #3a3a3a }
.qa b { display: block; font-size: var(--body); line-height: 1.3; margin-bottom: .5mm }
.qa p { font-size: var(--small); color: #A8A8A8 }
/* cover, contents, safety, part dividers */
.divider { display: flex; flex-direction: column; align-items: center; justify-content: center }
.divider .big { font: 800 42pt/1 Orbitron, sans-serif; color: #E44F44 }
.divider .dash { width: 6mm; height: 1mm; border-radius: 1mm; background: #E44F44; margin: 4mm 0 3.5mm }
.divider .name { font: 800 12pt/1 Orbitron, sans-serif; letter-spacing: .08em; color: #C8C8C8; text-transform: uppercase }
/* saber: 120 mm tall image, visible 115.9 mm from 4.07 mm down, so top 3 mm gives equal 7 mm margins */
.cover .saber { position: absolute; left: 6.4mm; top: 3mm; height: 120mm; width: auto }
.cover .col { position: absolute; left: 22mm; right: 6mm; top: 7mm; bottom: 7mm; padding: var(--inset, 0) 0; display: flex; flex-direction: column; align-items: center; text-align: center }
.cover { --inset: 18mm }
.cover .brand { width: 28mm }
.cover .t1, .cover .pm { font: 800 15pt/1.12 Orbitron, sans-serif; letter-spacing: .06em; color: transparent; -webkit-text-stroke: .28mm #C8C8C8 }
.cover .t2 { font: 800 8.4pt/1 Orbitron, sans-serif; letter-spacing: .08em; color: #C8C8C8; margin-top: 3mm }
.cover .dash { width: 6mm; height: 1mm; border-radius: 1mm; background: #E44F44; margin: 4mm 0 3.5mm }
.cover .who { font-size: 6pt; line-height: 1; color: #9a9a9a; letter-spacing: .1em }
.cover .pm { margin-bottom: -.38mm }  /* glyph bottom stays where the one-line 8.4 pt version ended */
.cover .up { flex: 4 } .cover .dn { flex: 5 }  /* gap above the title block : gap below = 4 : 5 */
.toc h2, .safe h2 { font: 800 var(--title)/1 Orbitron, sans-serif; letter-spacing: .05em; color: #C8C8C8; margin: 0 0 4mm; text-transform: uppercase }
.page a { color: inherit; text-decoration: underline; text-decoration-color: #5a5a5a; text-underline-offset: .5mm }
.toc a { display: flex; align-items: baseline; gap: 1.5mm; color: #BEBEBE; text-decoration: none; padding: .5mm 0 }
.toc a.sec { color: #D4D4D4; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; font-size: var(--body) }
.toc a.ind { padding-left: 3mm; color: #9a9a9a; font-size: var(--small) }
.toc a.pt { color: #E44F44; font: 800 var(--body)/1 Orbitron, sans-serif; letter-spacing: .06em; text-transform: uppercase; padding-top: 1.3mm }
.toc a.pt:first-of-type { padding-top: 0 }
.toc a i { flex: 1; border-bottom: .3mm dotted #4a4a4a; transform: translateY(-.5mm) }
.safe { display: flex; flex-direction: column; justify-content: center; text-align: center; padding-left: 10mm; padding-right: 10mm }
.safe h2 { margin-bottom: 2.5mm }
.safe .dash { width: 6mm; height: 1mm; border-radius: 1mm; background: #E44F44; margin: 0 auto 4mm }
.safe p { margin-bottom: 2.5mm }
.safe .warn { display: flex; justify-content: center; font-weight: 500; color: #D4D4D4; font-size: var(--sub); margin: 2mm 0 2mm; line-height: 1 }
.safe .warn > span { position: relative }
.safe .warn svg { position: absolute; right: calc(100% + 1.4mm); top: 50%; transform: translateY(-50%) }
/* in the box, quick reference */
:root { --gold: #C9A646 }
.core { stroke: #1A1A1A } .core .cf { fill: var(--gold) } .core .pins { stroke: var(--gold) }
.box { display: grid; grid-template-columns: 1fr 1fr; gap: 2mm }
.box div { background: #131313; border: .5pt solid #2c2c2c; border-radius: 1.6mm; padding: 2.2mm 1.5mm; text-align: center; min-height: 9mm; display: flex; flex-direction: column; justify-content: center; color: #D4D4D4; line-height: 1.3 }
p + p { margin-top: 1.6mm }
.cap { fill: #CFCFCF; font: 11px Poppins; text-anchor: middle }
.gloss div { display: grid; grid-template-columns: 15mm 1fr; gap: 2mm; padding: .6mm 0; border-bottom: .5pt solid #2c2c2c; line-height: 1.3 }
.gloss.pads div { grid-template-columns: 22mm 1fr } .gloss div:last-child { border-bottom: 0 } .gloss b { font-weight: 500; color: #D4D4D4 }
.why div { margin-top: 2.2mm; line-height: 1.45 } .why b { display: block; font-weight: 500; color: #D4D4D4 }
.tech td:first-child { width: 27% } .tech td { padding: .9mm 1.5mm }
.parts { margin-top: 2mm }
.blade-pg { display: flex; gap: 3mm } .blade-pg > div { flex: 1; min-width: 0 }
.bphotos { display: block; width: 100%; height: auto; margin: 2mm 0 1mm }
.blade-photos { display: flex; gap: 1.5mm; margin: 2mm 0 1mm } .blade-photos figure { flex: 1; margin: 0; display: flex; flex-direction: column; align-items: center; gap: 1mm }
.blade-photos img { width: 100%; height: auto } .blade-photos figcaption { font-size: var(--small); color: #A8A8A8; text-align: center; line-height: 1.25 }
.anat { display: flex; gap: 2mm; align-items: center } .anat-art { flex: none; width: auto }
/* the saber runs from the top of the title to the bottom of the page number */
.side-art { position: absolute; right: 8mm; top: 8.5mm; height: 116.5mm }
.qs-art { position: absolute; right: 8mm; top: 8.5mm; height: 116.5mm; width: 9mm } .qs { margin-right: 13mm }
.dim { fill: none; stroke: #7a7a7a } .dim text { fill: #9a9a9a; stroke: none; font-family: Poppins; text-anchor: middle }
.anat .parts { flex: 1 }
.blade-v { flex: none; height: 101mm; width: 14.5mm } .part { display: flex; gap: 1.8mm; align-items: flex-start; padding: 1.3mm 0; border-bottom: .5pt solid #3a3a3a }
.part b { display: block; font-weight: 500; color: #D4D4D4 }
.qr { display: flex; flex-direction: column; gap: 3mm }
.qr figure { margin: 0; display: flex; gap: 3.5mm; align-items: center; color: #D4D4D4; font-size: var(--body); line-height: 1.3 }
.qr svg { flex: none; width: 20mm; height: 20mm; border-radius: 1.4mm }
.qr b { font-weight: 500 }
.qr small { display: inline; color: #8C8C8C; font-size: var(--small); margin-left: 1.5mm }
.qr p { margin-top: .8mm; font-size: var(--small); color: #A8A8A8 }
.ref { display: grid; grid-template-columns: 1fr 1fr; gap: 0 4mm }
.ref .row { display: flex; justify-content: space-between; align-items: baseline; gap: 1.5mm; font-size: var(--small); line-height: 1.3; padding: 1.05mm 0; border-bottom: .5pt solid #2c2c2c }
.ref .row span { color: #A8A8A8; text-align: right }
.pn { position: absolute; bottom: 5mm; left: 0; right: 0; text-align: center; font-size: var(--small); color: #8f8f8f }
/* code, resources, diagram */
code { font: var(--fine)/1.4 Menlo, ui-monospace, monospace; color: #CFCFCF; overflow-wrap: anywhere }
pre { margin: 1.6mm 0 0; padding: 1.6mm 2mm; background: #131313; border: .5pt solid #2c2c2c; border-radius: 1.6mm; white-space: pre; overflow: hidden }
pre code { display: block } pre .c { color: #7f7f7f }
.links { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 4mm }
.links figure { margin: 0; display: flex; flex-direction: column; align-items: center; text-align: center; gap: 1.2mm; color: #D4D4D4; line-height: 1.3 }
.links svg { width: 20mm; height: 20mm; border-radius: 1.4mm }
.src { position: absolute; top: 6mm; right: 8mm; width: 14mm; text-align: center; font-size: var(--fine); line-height: 1 }
.src svg { display: block; width: 14mm; height: 14mm; border-radius: 1mm; margin-bottom: .8mm }
.links small { color: #8C8C8C; font-size: var(--small) }
.arch rect { fill: #131313; stroke: #3a3a3a } .arch text { fill: #D4D4D4; font-family: Poppins; text-anchor: middle } .arch .s { fill: #8f8f8f }
.toc .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0 4mm } .toc .cols > div { min-width: 0 }
.toc .cols a { font-size: var(--small) } .toc .cols a span:first-child { white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
.todo { display: inline-block; font: 600 var(--fine)/1.5 Poppins; color: #0E0E0E; background: #E44F44; border-radius: .8mm; padding: 0 .9mm; margin-left: 1mm; vertical-align: 1px }
@media print { .ghost { display: none } html, body { background: #0E0E0E } .spread { display: block; width: auto; margin: 0 } .page { page-break-after: always; height: 491px } }
"""


def photo_w(f):
    """Width in drawing units of a hilt photo drawn at the hilt's full drawing length."""
    w, h = Image.open(Path(__file__).with_name("img") / f).size
    return (END_Y - RING[0]) * w / h


CALL_MM = 7 * 86 / 566  # callout circle radius on the page in mm (the Anatomy page's size, the reference)


def call_k(height_mm, vb_height):
    """Scale for callouts in an svg drawn height_mm tall with a viewBox vb_height units tall,
    so every page's numbered circles come out the same size on paper."""
    return CALL_MM / 7 / (height_mm / vb_height)


def callout(n, side, y, *targets, cx=None, k=1):
    """Numbered circle on the left/right edge, dashed leaders to green dots at each (x, y) target."""
    cx = cx if cx is not None else -4 if side == "L" else 204
    x0 = cx + 7 * k if side == "L" else cx - 7 * k
    leads = "".join(f"M{x0:.1f} {y}L{tx} {ty}" for tx, ty in targets)
    dots = "".join(f'<circle class="dot" cx="{tx}" cy="{ty}" r="{3.6 * k:.2f}" style="stroke-width:{.9 * k:.2f}"/>' for tx, ty in targets)
    return (
        f'<g class="call" style="stroke-width:{.7 * k:.2f}"><path class="lead" d="{leads}" style="stroke-width:{.6 * k:.2f};stroke-dasharray:{1.6 * k:.2f} {1.6 * k:.2f}"/>'
        f'<circle cx="{cx}" cy="{y}" r="{7 * k:.2f}"/>'
        f'<text x="{cx}" y="{y + 3.2 * k:.1f}" text-anchor="middle" style="font-size:{9 * k:.2f}px">{n}</text></g>{dots}'
    )


def callout_v(n, cy, tx, ty, k=1):
    """Same callout, circle straight above (or below) the target with a vertical pointer line."""
    y0 = cy + 7 * k if ty > cy else cy - 7 * k
    return (f'<g class="call" style="stroke-width:{.7 * k:.2f}"><path class="lead" d="M{tx} {y0:.1f}V{ty}" style="stroke-width:{.6 * k:.2f};stroke-dasharray:{1.6 * k:.2f} {1.6 * k:.2f}"/>'
            f'<circle cx="{tx}" cy="{cy}" r="{7 * k:.2f}"/>'
            f'<text x="{tx}" y="{cy + 3.2 * k:.1f}" text-anchor="middle" style="font-size:{9 * k:.2f}px">{n}</text></g>'
            f'<circle class="dot" cx="{tx}" cy="{ty}" r="{3.6 * k:.2f}" style="stroke-width:{.9 * k:.2f}"/>')


def screw_art(kind, cx, cy, s):
    """A screw at s units per mm, top view and side view (head up) side by side, centred on (cx, cy).
    Returns the svg and the x of its left and right edges."""
    steel, edge, thr = "#c9cdd1", f'stroke="#141414" stroke-width="{.12 * s:.2f}"', "#8d9297"
    tw = f"{.1 * s:.2f}"  # thread line width
    d, length, head, hh, pitch = {"set": (4, 5, 4, 0, .7), "csk": (3, 2.5, 6, 1.5, .5), "button": (3, 5, 5.7, 1.65, .5)}[kind]
    g = 1.5  # gap between the views, mm
    w = 2 * head + g
    tx = cx - w * s / 2 + head * s / 2  # top view centre
    sx = cx + w * s / 2 - head * s / 2  # side view centre
    y0 = cy - (hh + length) * s / 2  # top of the side view
    hexr = 2 / math.sqrt(3) * s  # 2 mm hex socket, across flats
    hexagon = " ".join(f"{tx + hexr * math.cos(math.radians(30 + 60 * i)):.1f},{cy + hexr * math.sin(math.radians(30 + 60 * i)):.1f}" for i in range(6))
    top = (f'<circle cx="{tx:.1f}" cy="{cy:.1f}" r="{head * s / 2:.1f}" fill="{steel}" {edge}/>'
           + (f'<circle cx="{tx:.1f}" cy="{cy:.1f}" r="{(head / 2 - .35) * s:.1f}" fill="none" stroke="{thr}" stroke-width="{tw}"/>' if kind == "set" else "")
           + f'<polygon points="{hexagon}" fill="#2a2c30"/>')
    ys = y0 + hh * s  # top of the thread
    r = d * s / 2
    side = ""
    if kind == "csk":
        side += f'<path d="M{sx - head * s / 2:.1f} {y0:.1f}H{sx + head * s / 2:.1f}L{sx + r:.1f} {ys:.1f}H{sx - r:.1f}Z" fill="{steel}" {edge}/>'
    elif kind == "button":
        side += (f'<path d="M{sx - head * s / 2:.1f} {ys:.1f}C{sx - head * s / 2:.1f} {y0 - .2 * s:.1f} {sx + head * s / 2:.1f} {y0 - .2 * s:.1f} {sx + head * s / 2:.1f} {ys:.1f}Z" fill="{steel}" {edge}/>')
    c = .35 * s  # chamfer at the thread end
    yb = ys + length * s
    side += f'<path d="M{sx - r:.1f} {ys:.1f}H{sx + r:.1f}V{yb - c:.1f}L{sx + r - c:.1f} {yb:.1f}H{sx - r + c:.1f}L{sx - r:.1f} {yb - c:.1f}Z" fill="{steel}" {edge}/>'
    n = int(length / pitch)
    side += "".join(f'<path d="M{sx - r:.2f} {ys + (i + .6) * pitch * s:.2f}L{sx + r:.2f} {ys + (i + .25) * pitch * s:.2f}" stroke="{thr}" stroke-width="{tw}"/>' for i in range(n))
    return top + side, cx - w * s / 2, cx + w * s / 2


def page_structure(pn):
    """Shaded front and back drawings side by side, end view of the pommel."""
    (hx, hy), (hx2, hy2) = SCREW_HOLES
    dx = 130  # back view offset
    px, py = 296, 474  # pommel end view
    sx, sy = SLEEVE_SCREW
    top, h = 42 - FADE_L, 83.2  # viewBox top fits the full faded blade; the svg rises beside the title to the page top
    k = call_k(h, 544 - top)
    t = 4.05 * k  # dot radius with its white edge: the dot sits just left of small parts
    cu = Y(1592) - 3  # upper crystal, near its wide top
    calls = [
        (1, "R", 20, [(dx + 100 + 9, 20)], "Blade"),
        (2, "L", 48, [(100, 48)], "Emitter"),
        (3, "L", (hy + hy2) / 2, [(hx, hy), (hx2, hy2)], "Blade retention screws"),
        (4, "L", BUTTON_Y, [(100 - BUTTON_R - t, BUTTON_Y)], "Power button"),
        (5, "L", cu, [(100 - HW(133) - t, cu)], "Crystal chamber"),
        (6, "L", JOINT_Y, [(L + 3, JOINT_Y)], "Joint (also unscrews)"),
        (7, "L", KNOB_Y, [(100 - KNOB_R - t, KNOB_Y)], "Covertec wheel (belt clip mount)"),
        (8, "R", 420, [(px, py - POMMEL_R + 4)], "Pommel, sound holes"),
        (9, "R", sy, [(sx + dx, sy)], "Sleeve screw"),
    ]
    cl, cr = 50, 280  # callout columns, close to the hilt
    svg = "".join(callout(n, s, y, *ts, cx=cr if s == "R" else cl, k=k) for n, s, y, ts, _ in calls)
    # screws at the hilt's scale, each halfway from the hilt's widest edge to the page's text edge, with a line from its callout
    vw = 69 * (544 - top) / h  # viewBox width that spans the page's text width
    v0 = 162 - vw / 2
    u = (544 - top) / h  # units per mm on the page
    r = 7 * k
    lead = lambda d: f'<path class="lead" d="{d}" style="stroke-width:{.6 * k:.2f};stroke-dasharray:{1.6 * k:.2f} {1.6 * k:.2f}"/>'
    xl, xr = (v0 + 100 - RING_HW) / 2, (dx + 100 + RING_HW + v0 + vw) / 2
    for kind, cx, cy, side, lines in (("set", xl, (hy + hy2) / 2, "L", ("M4 × 5 mm", "hex set screw")),
                                      ("button", xl, KNOB_Y, "L", ("M3 × 5 mm hex", "button head screw")),
                                      ("csk", xr, sy, "R", ("M3 × 4 mm hex", "countersunk screw"))):
        zoom = 2  # screws drawn at twice the hilt's scale, inside a circle
        art, _, _ = screw_art(kind, cx, cy, zoom * MM)
        rc = 24  # circle radius, the same for every screw
        ring = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rc}" fill="#161616" stroke="#3a3a3a" stroke-width="{.5 * k:.2f}"/>'
        line = lead(f"M{cl - r:.1f} {cy}H{cx + rc:.1f}") if side == "L" else lead(f"M{cr + r:.1f} {cy}H{cx - rc:.1f}")
        scale = f'<text x="{cx + rc + 3:.1f}" y="{cy + rc * .85:.1f}" data-pt="4.6" font-family="Poppins" fill="#6a6a6a">{zoom}:1</text>'
        ly = cy + rc + 16
        label = (f'<text x="{cx:.1f}" y="{ly:.1f}" data-pt="5" font-family="Poppins" fill="#A8A8A8" text-anchor="middle">{lines[0]}'
                 + "".join(f'<tspan x="{cx:.1f}" dy="1.2em">{t}</tspan>' for t in lines[1:]) + "</text>")
        if kind == "set":  # two of them: a count to the left of the label
            label += f'<text x="{cx - 58:.1f}" y="{ly + 9:.1f}" class="cap" style="text-anchor:end">2x</text>'
        art = ring + art + scale
        svg += line + art + label
    legend = "".join(f'<div>{num(n)}{label}</div>' for n, *_, label in calls)
    return f"""<div class="page"><h1>Structure</h1>
<svg viewBox="{v0:.1f} {top} {vw:.1f} {544 - top}" class="art" style="height:{h}mm;width:100%;margin:-14.2mm 0 0">
<use href="#top-sh"/><use href="#body-sh"/>
<g transform="translate({dx} 0)">{fade_end(f'<rect x="{100 - BLADE_HW - 3:.1f}" y="{44 - FADE_L}" width="{2 * BLADE_HW + 6:.1f}" height="{FADE_L + 4}" fill="#3CFF6A" opacity=".55" filter="url(#glow)"/><rect x="{100 - BLADE_HW:.1f}" y="{44 - FADE_L}" width="{2 * BLADE_HW:.1f}" height="{FADE_L + 4}" fill="url(#g-blade)"/>', "up")}
<use href="#top-back-sh"/><use href="#body-back-sh"/></g>
{pommel_end(px, py, shaded=True)}<path class="lead" d="M{dx + 100 + POMMEL_R + 4} 511Q{px} 511 {px} {py + POMMEL_R + 2}"/>{svg}
<text x="100" y="538" class="cap">Front</text><text x="{dx + 100}" y="538" class="cap">Back</text></svg>
<div class="legend">{legend}</div>
<p class="tip">The Covertec wheel slides into a Covertec belt clip, which you buy on its own, so the hilt hangs from a belt. Remove the blade first.</p><div class="pn">&lt; {pn} &gt;</div></div>"""


def page_anatomy(pn):
    """The saber standing upright on the right of the page, blade lit, from the title's top to the page
    number's bottom; the core to its left at the height where it sits inside; numbered parts on the left."""
    apex = RING[0] - (BLADE_MM - INSERT_MM) * HMM  # visible blade above the emitter
    cdx = 170  # core drawn this far left of the hilt
    c0, c1 = CORE
    hmm = 116.5  # drawn height in mm
    y0 = apex - 6
    h = END_Y + 140 - y0
    u = h / hmm  # drawing units per mm on the page
    x0 = CX - cdx - CORE_D / 2 - 8 * u  # room for the callout column on the left
    w = CX + 52 + 7 * u + 4 * u - x0
    guides = (f'<path class="lead" d="M{CX - 22} {c0}H{CX - cdx + 16}M{CX - 22} {c1}H{CX - cdx + 16}" style="stroke-width:1.4;stroke-dasharray:3 3"/>')
    art = (f'{blade_v(CX, apex, RING[0] + 4, lit=True)}<use href="#top-mini"/><use href="#body-mini"/>'
           f'<g transform="translate({-cdx} 0)"><use href="#core-mini"/></g>{guides}'
           + dim_v(CX + 52 + 7 * u, apex, apex + BLADE_MM * HMM, "Blade 81 cm", u, right=True)
           + dim_v(CX + 30 + 3 * u, RING[0], END_Y, "Hilt 31 cm", u, right=True)
           + dim_h(END_Y + 3 * u, CX - 27.3, CX + 27.3, "3.6 cm", u)
           + dim_h(c1 + 3 * u, CX - cdx - CORE_D / 2, CX - cdx + CORE_D / 2, "2.54 cm", u))
    cx = x0 + 2 * u  # callout column, left edge
    calls = [(1, (CX - 10, apex + 300)), (2, (CX - RING_HW, (RING[0] + BLACK[0]) / 2)), (3, (CX - 26, 220)),
             (4, (CX - cdx - CORE_D / 2, (c0 + c1) / 2)), (5, (CX - POMMEL_R, (POMMEL + END_Y) / 2))]
    svg = "".join(callout(n, "L", t[1], t, cx=cx, k=call_k(hmm, h)) for n, t in calls)
    terms = [("Blade", "A polycarbonate tube with Neopixel LED strips. It's 81 cm long"),
             ("Emitter", "The top of the hilt. Two screws hold the blade in it"),
             ("Hilt", "The metal handle. It's 31 cm long and unscrews at the joint and at the pommel"),
             ("Core", f"The removable electronics: board, battery and speaker. It sits in the lower half of the hilt (page {P['core']})"),
             ("Pommel", "The bottom cap. Sound comes out through its holes, and it unscrews to take the core out")]
    body = "".join(f'<div class="part">{num(n)}<div><b>{a}</b>{sent(b)}</div></div>' for n, (a, b) in enumerate(terms, 1))
    wmm = w / u
    return f"""<div class="page"><h1>Anatomy</h1>
<svg viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}" class="side-art" style="width:{wmm:.1f}mm">{art}{svg}</svg>
<div class="parts" style="margin-right:{wmm + 2:.1f}mm">{body}</div>
<div class="pn">&lt; {pn} &gt;</div></div>"""


ART_H = 47  # core page drawing height, mm


def page_core(pn):
    """Coloured drawings of both sides, end faces up, with numbered callouts."""
    k1, k2 = 560 / 1881, 560 / 1889  # photo px to drawing units
    x1, x2 = 30, 185
    a = lambda x, y: (round(x1 + x * k1, 1), round(y * k1, 1))  # battery side
    b = lambda x, y: (round(x2 + x * k2, 1), round(y * k2, 1))  # board side
    calls = [(1, "L", 10, a(150, 30), "Pogo pins (top end)"), (2, "L", 51, a(250, 194), "USB-C charging port"),
             (3, "L", 237, a(30, 700), "Accent LED strip"), (4, "L", 290, a(230, 900), "18650 battery, 3600 mAh"),
             (5, "L", 472, a(236, 1496), "Charging light"),
             (6, "R", 60, b(256, 250), "Bass speaker"), (7, "R", 0, b(262, 942), "microSD card"),
             (8, "R", 0, b(268, 1044), "Micro-USB data port"), (9, "R", 0, b(299, 1176), "Board (Proffieboard V2.2)"),
             (10, "R", 0, b(278, 1300), "Board clamp"), (11, "R", 500, b(236, 1730), "Power switch"),
             (12, "L", 0, a(60, 1780), "Chassis (gold metal exterior)")]
    svg = "".join(callout(n, s, t[1], t, cx=-4 if s == "L" else 294, k=call_k(ART_H, 590)) for n, s, y, t, _ in calls)  # level with the part
    u = 560 / 185  # drawing units per mm (core length)

    def usbc(cx, y0):
        """White USB-C plug, wide face toward you, tip up: 8.25 mm shell, 12 mm overmold, 4 mm cable."""
        w = lambda mm: mm * u
        y1, y2, y3, y4 = y0 + w(6.6), y0 + w(25), y0 + w(31), y0 + w(43)
        return (f'<rect x="{cx - w(4.125):.1f}" y="{y0}" width="{w(8.25):.1f}" height="{w(6.6) + 2:.1f}" rx="{w(1):.1f}" fill="#c9cdd1" stroke="#141414" stroke-width=".8"/>'
                f'<path d="M{cx - w(3.2):.1f} {y0 + 3}H{cx + w(3.2):.1f}" stroke="#eef0f2" stroke-width="1.2"/>'
                f'<path d="M{cx - w(2):.1f} {y4:.1f}V{y3:.1f}L{cx - w(2.8):.1f} {y2:.1f}H{cx - w(6):.1f}V{y1 + w(2):.1f}Q{cx - w(6):.1f} {y1:.1f} {cx - w(4):.1f} {y1:.1f}'
                f'H{cx + w(4):.1f}Q{cx + w(6):.1f} {y1:.1f} {cx + w(6):.1f} {y1 + w(2):.1f}V{y2:.1f}H{cx + w(2.8):.1f}L{cx + w(2):.1f} {y3:.1f}V{y4:.1f}Z" fill="#f4f4f2" stroke="#141414" stroke-width="1"/>'
                f'<path d="M{cx - w(6):.1f} {y2:.1f}H{cx + w(6):.1f}" stroke="#b8b8b4" stroke-width=".8"/>')

    def micro(x0, cy):
        """The black right-angle Micro-USB plug, side on, tip pointing left, cable going down (photo, mirrored)."""
        P = lambda pts: "M" + "L".join(f"{x0 + x * u:.1f} {cy + y * u:.1f}" for x, y in pts) + "Z"
        R = lambda x, y, wd, ht, r, fill, extra="": (f'<rect x="{x0 + x * u:.1f}" y="{cy + y * u:.1f}" width="{wd * u:.1f}" height="{ht * u:.1f}" rx="{r * u:.1f}" fill="{fill}" {extra}/>')
        edge = 'stroke="#6b6e72" stroke-width=".8"'
        return (R(12.9, 9, 2.6, 13, 0, "#1b1b1d", edge)  # cable
                + f'<path d="{P([(12.4, 6.8), (16.2, 6.8), (15.8, 10.4), (12.8, 10.4)])}" fill="#1b1b1d" {edge}/>'  # strain relief
                + f'<path d="{P([(6.2, -5.4), (18.6, -5.4), (18.6, 7), (8.8, 7), (8.8, 5.2), (6.2, 5.2)])}" fill="#202023" {edge} stroke-linejoin="round"/>'  # body, stepped up by the tip
                + R(18.4, -6.1, 3.4, 15.8, .8, "#18181a", edge)  # flange
                + R(0, -3.42, 6.6, 6.84, .3, "#c9cdd1", 'stroke="#141414" stroke-width=".8"')  # metal tip
                + R(.4, -2.3, 3.3, .8, .3, "#2a2c30") + R(.4, 1.3, 3.3, .8, .3, "#2a2c30"))  # latch holes
    kc, (_, y2), (_, y8) = call_k(ART_H, 590), a(250, 194), b(268, 1044)
    r = 7 * kc
    lead = lambda d: f'<path class="lead" d="{d}" style="stroke-width:{.6 * kc:.2f};stroke-dasharray:{1.6 * kc:.2f} {1.6 * kc:.2f}"/>'
    vw = 69 * 590 / ART_H  # viewBox width that spans the page's text width
    v0 = 145 - vw / 2  # centred between the callout columns
    ux = (v0 + x1) / 2  # USB-C: halfway from the page edge to the battery side
    mx = (x2 + 311 * k2 + v0 + vw) / 2 - 10.9 * u  # Micro-USB: its middle halfway from the board side to the page edge
    svg += (usbc(ux, y2 - r) + lead(f"M{-4 - r:.1f} {y2}H{ux + 4.125 * u:.1f}") + f'<text x="{ux}" y="{y2 - r + 43 * u + 20:.0f}" class="cap">USB-C<tspan x="{ux}" dy="1.15em">cable</tspan></text>'
            + micro(mx, y8) + lead(f"M{294 + r:.1f} {y8}H{mx}") + f'<text x="{mx + 10.9 * u:.0f}" y="{y8 + 22 * u + 20:.0f}" class="cap">Micro-USB<tspan x="{mx + 10.9 * u:.0f}" dy="1.15em">cable</tspan></text>')
    legend = "".join(f'<div>{num(n)}{label}</div>' for n, *_, label in calls)
    return f"""<div class="page">{src_qr("core")}<h1>Core<small class="h1-sub">NexusSabers LGT A.294-1</small></h1>
<svg viewBox="{v0:.1f} -4 {vw:.1f} 590" class="art" style="height:{ART_H}mm;width:100%;margin-bottom:0">
<g transform="translate({x1} 0) scale({k1:.5f})">{core_battery_side()}</g>
<g transform="translate({x2} 0) scale({k2:.5f})">{core_board_side()}</g>{svg}
<text x="{x1 + 53}" y="580" class="cap">Battery side</text><text x="{x2 + 52}" y="580" class="cap">Board side</text></svg>
<div class="legend">{legend}</div>
<p class="tip">The microSD card (7) slides into a slot under the board (9), below the Micro-USB data port (8).</p>
<p class="tip">The Micro-USB data port (8) takes a data cable, not a charging cable. The port sits close to the chassis (12) and doesn't fit most plugs. Use a right-angle plug like the one shown.</p>
<p class="tip">The power switch (11) is a push button that cuts the battery (4) off from the board. Click it off to store the saber. If the saber stops responding, click it off, then on.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


# Horizontal drawings: rotate the vertical hilt so the emitter points left.
H = 'transform="translate({dx},196) rotate(-90)"'


def hz(*parts, dx=0):
    return f'<g {H.format(dx=dx)}>' + "".join(f'<use href="#{p}"/>' for p in parts) + "</g>"


def twist_arrows(x):
    return (f'<path class="arrow" data-head="1" d="M{x + 14} 62H{x - 2}"/>'
            f'<path class="arrow" data-head="1" d="M{x - 14} 130H{x + 2}"/>')


def plugged(light, label):
    """Core with a white USB-C plug seen side-on in its port (top edge), and the charging light lit."""
    dx = -250
    ux = usb_y() + dx  # port centre along the core
    lx0, lx1 = 435 + dx, 442.4 + dx  # charging light
    glow = f'<rect x="{lx0 - 6}" y="74" width="{lx1 - lx0 + 12}" height="24" rx="6" fill="{light}" opacity=".9" filter="url(#glow)"/>'
    plug = (f'<rect x="{ux - 2.5}" y="10" width="5" height="27" fill="#f4f4f2" stroke="#141414" stroke-width="1"/>'
            f'<rect x="{ux - 2.6}" y="71" width="5.2" height="8" fill="#c9cdd1" stroke="#141414" stroke-width=".8"/>'
            f'<path d="M{ux - 6.5} 72V45Q{ux - 6.5} 40 {ux - 2.5} 36H{ux + 2.5}Q{ux + 6.5} 40 {ux + 6.5} 45V72Z" fill="#f4f4f2" stroke="#141414" stroke-width="1"/>'
            f'<path d="M{ux - 4.5} 50H{ux + 4.5}M{ux - 4.5} 54H{ux + 4.5}M{ux - 4.5} 58H{ux + 4.5}" stroke="#b8b8b4" stroke-width=".8"/>')
    return (f'<svg viewBox="0 18 250 122" preserveAspectRatio="xMidYMid meet">{glow}{hz("core-mini", dx=dx)}'
            f'<rect x="{lx0}" y="80.3" width="{lx1 - lx0}" height="10.7" rx="2" fill="{light}"/>{plug}'
            f'<text class="cap" x="124" y="134">{label}</text></svg>')


def page_charging(pn):
    vb = 'class="pic" viewBox="20 44 560 104" preserveAspectRatio="xMidYMid meet"'
    sm = POMMEL_SEAM
    s1 = f'<svg {vb}>{hz("top-mini", "body-mini", dx=40)}{twist_arrows(sm + 40)}</svg>'
    s2 = (f'<svg {vb}>{hz("top-mini", "body-open-mini", dx=10)}{hz("pommel-mini", dx=60)}'
          f'<path class="arrow" data-head="1" d="M{sm + 72} 62H{sm + 100}"/></svg>')
    s3 = (f'<svg {vb} style="overflow:visible"><g transform="rotate(7 330 96)">{hz("core-mini", dx=40)}{hz("top-mini", "body-open-mini", dx=-130)}'
          f'<path class="arrow" data-head="1" d="M{sm - 100} 60H{sm - 40}"/></g></svg>')
    s4 = f'<div class="duo">{plugged("#ff3b30", "Charging")}{plugged("#3cd86a", "Full")}</div>'
    return f"""<div class="page nosep"><h1>Charging</h1>
<div class="step">{num(1)}<div><p>Hold the grip and turn the pommel at the bottom counterclockwise to unscrew it.</p>{s1}</div></div>
<div class="step">{num(2)}<div><p>Pull the pommel off.</p>{s2}</div></div>
<div class="step">{num(3)}<div><p class="last-right">Tilt the hilt so its open bottom points down. The gold core slides out, speaker end first.</p>{s3}</div></div>
<div class="step">{num(4)}<div><p>Plug a USB-C cable into the port next to the gold pins. Use a 5V 1A charger only. The light by the speaker shows red while charging and green when full.</p>{s4}</div></div>
<div class="step">{num(5)}<div><p>Slide the core back in, gold pins first, then screw the pommel back on.</p></div></div>
<p class="note">The hilt also unscrews at the joint below the crystal chamber, which frees the core from the top instead.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def pulses(spec):
    """Timing pictogram. spec: list of 'c' (click), 'l' (long click, 1 s) or 'h' (hold)."""
    x, out = 2, ['<path d="M0 12H120" stroke="#3a3a3a" stroke-width=".8"/>']
    for k in spec:
        if k == "c":
            out.append(f'<rect x="{x}" y="3" width="5" height="9" rx="1.5" fill="{GREEN}"/>')
            x += 10
        elif k == "l":
            out.append(f'<rect x="{x}" y="3" width="30" height="9" rx="1.5" fill="{GREEN}"/>'
                       f'<text x="{x + 15}" y="10" text-anchor="middle" data-pt="4.6" font-family="Poppins" fill="#0E0E0E">1 s</text>')
            x += 36
        else:  # hold: bar runs off the end with an arrow, no release
            out.append(f'<rect x="{x}" y="3" width="{112 - x}" height="9" rx="1.5" fill="{GREEN}"/>'
                       f'<path d="M112 3L119 7.5L112 12Z" fill="{GREEN}"/>')
    return f'<svg viewBox="0 0 120 14">{"".join(out)}</svg>'


def page_button(pn):
    rows = [
        ("Click", "One short press", "c"),
        ("Double Click", "Two fast presses", "cc"),
        ("Triple Click", "Three fast presses", "ccc"),
        ("Long Click", "Press for 1 second, then let go", "l"),
        ("Hold", "Press and keep holding", "h"),
        ("Click + Long Click", "One short press, then a long click", "cl"),
        ("Double Click and Hold", "Two presses, hold on the second", "ch"),
        ("Triple Click + Long Click", "Three short presses, then a long click", "cccl"),
    ]
    body = "".join(f'<div class="press"><div><b>{t}</b><span>{d}</span></div>{pulses(k)}</div>' for t, d, k in rows)
    return f"""<div class="page"><h1>The button</h1>
<div class="pwr"><svg viewBox="0 0 30 30" style="width:6.5mm;height:6.5mm;flex:none"><circle cx="15" cy="15" r="13" fill="none" stroke="#D6D6D6" stroke-width="1"/><circle cx="15" cy="15" r="10" fill="#E44F44"/></svg>
<p>The red button is the Power button. You give each command as a pattern of presses on it.</p></div>
{body}<div class="pn">&lt; {pn} &gt;</div></div>"""


def fan_hilt(angle, px, py, s=0.15, gap=14):
    """Whole saber with a blade stub, pommel at the pivot; angle 90 = up, 0 = level, -90 = down."""
    g = (f'<g transform="rotate({90 - angle} {px} {py}) translate({px - 100 * s} {py - 515 * s - gap}) scale({s})">'
         + fade_end(f'<rect x="{CX - BLADE_HW:.1f}" y="{RING[0] - FADE_L}" width="{2 * BLADE_HW:.1f}" height="{FADE_L}" fill="url(#g-tube)"/>', "up") +
         '<use href="#top-mini"/><use href="#body-mini"/></g>')
    return g


def wedge(px, py, rad, a0, a1, fill):
    p0 = (px + rad * math.cos(math.radians(a0)), py - rad * math.sin(math.radians(a0)))
    p1 = (px + rad * math.cos(math.radians(a1)), py - rad * math.sin(math.radians(a1)))
    return (f'<path d="M{px} {py}L{p0[0]:.1f} {p0[1]:.1f}A{rad} {rad} 0 0 0 {p1[0]:.1f} {p1[1]:.1f}Z" '
            f'fill="{fill}"/>')


def page_angle(pn):
    px, py, rad = 30, 129, 129
    zones = (wedge(px, py, rad, -60, 60, "rgba(68,176,61,.10)") + wedge(px, py, rad, 60, 90, "rgba(68,176,61,.24)")
             + wedge(px, py, rad, -90, -60, "rgba(228,79,68,.16)"))
    labels = "".join(f'<text x="{x}" y="{y}" font-family="Poppins" data-pt="5" fill="{c}">{t}</text>'
                     for x, y, t, c in ((70, 16, "Straight up", "#9fd69b"), (150, 112, "Parallel", "#9fd69b"),
                                        (58, 250, "Down", "#f0a39d")))
    fan = f'<svg viewBox="-2 -6 204 270" class="art" style="height:58mm">{zones}{fan_hilt(90, px, py)}{fan_hilt(0, px, py)}{fan_hilt(-90, px, py)}{labels}<circle cx="{px}" cy="{py}" r="3" fill="#E44F44"/></svg>'
    return f"""<div class="page"><h1>Blade angle</h1>
<p>Some presses do different things depending on where the blade points. Down means steeper than 60° below level. Straight up means steeper than 60° above.</p>
{fan}
<table class="tbl ang"><tr><th>Press</th><th>Parallel or up</th><th>Down</th></tr>
<tr><td>Long Click</td><td>Next preset</td><td>Previous preset</td></tr>
<tr><td>Triple Click + Long Click</td><td>Next font</td><td>Previous font</td></tr>
<tr><td>Double Click, blade off</td><td>Music player<br>(straight up: play / stop)</td><td>Music player</td></tr></table>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def ctl_table(rows):
    def cell(t):
        main, _, sub = t.partition("|")
        return main + (f"<small>{sub}</small>" if sub else "")
    body = "".join(f"<tr><td>{cell(c)}</td><td>{cell(e)}</td></tr>" for c, e in rows)
    return f'<table class="tbl ctl"><tr><th>Control</th><th>Effect</th></tr>{body}</table>'


def sub(label, color):
    return f'<div class="sub"><span><i style="background:{color}"></i>{label}</span></div>'


def page_controls(pn):
    off = [("Click", "Ignite"), ("Click + Long Click", "Ignite muted"), ("Long Click ↑", "Next preset"),
           ("Long Click ↓", "Previous preset"), ("Hold", "Scroll presets"), ("Triple + Long Click ↑", "Next font"), ("Triple + Long Click ↓", "Previous font"),
           ("Hold + Clash ↑", "Volume"), ("Hold + Clash ↓", "Gestures on / off"), ("Dbl Click + Long Click", "Battery level"),
           ("Double Click", "Music player"), ("Double Click ↑↑", "Play / stop music"), ("Triple Click", "Force / quote"),
           ("Dbl Click and Hold", "Edit Mode")]
    on = [("Hold", "Turn off"), ("Hit the blade", "Clash"), ("Hold + Clash", "Lockup"), ("Thrust", "Stab"),
          ("Hold + Stab ↓", "Drag"), ("Hold + Stab ↑", "Melt"), ("Click", "Blaster block"),
          ("Dbl Click and Hold", "Lightning block"), ("Hold + Swing", "Multi-blast"), ("4 Clicks", "Color change"),
          ("Long Click", "Force / quote"), ("Double Click", "Stop music")]
    col = lambda rows: "".join(f'<div class="row"><b>{a}</b><span>{b}</span></div>' for a, b in rows)
    return f"""<div class="page"><h1>Control</h1>
<div class="ref"><div>{sub("Blade off", "#E44F44")}{col(off)}</div><div>{sub("Blade on", GREEN)}{col(on)}</div></div>
<p class="tip">↑ parallel or up · ↓ down · ↑↑ straight up</p>
<p class="tip">Turn means roll the whole saber on its long axis (page {P['motion']}). Scroll presets: turn, Click to select. Volume: turn, Click to exit. Multi-blast: Click or Clash to exit.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


SWATCHES = ("#E44F44", "#E04FA0", "#8E5BE8", "#3B82F6", "#2EC4E6", "#44B03D", "#F2F2F2")


HMM = (END_Y - RING[0]) / 310  # hilt drawing units per mm
TIP_MM, BLADE_MM, INSERT_MM = 32, 810, 25  # bullet tip length, whole blade (32 in), length inside the emitter


def bullet_v(cx, hw, apex, base):
    """Blade outline, tip up: bullet tip (ogive, apex at `apex`, 32 mm long) on a straight tube down to `base`."""
    t = TIP_MM * hw * 2 / 25.4
    return (f"M{cx - hw:.1f} {base:.1f}V{apex + t:.1f}C{cx - hw:.1f} {apex + t * .42:.1f} {cx - hw * .38:.1f} {apex:.1f} {cx:.1f} {apex:.1f}"
            f"C{cx + hw * .38:.1f} {apex:.1f} {cx + hw:.1f} {apex + t * .42:.1f} {cx + hw:.1f} {apex + t:.1f}V{base:.1f}Z")


def bullet_h(x0, x1, y0, y1):
    """Horizontal blade, tip on the left at x0, tube running right to x1."""
    hw, cy = (y1 - y0) / 2, (y0 + y1) / 2
    t = TIP_MM * hw * 2 / 25.4
    return (f"M{x1} {y0}H{x0 + t:.1f}C{x0 + t * .42:.1f} {y0} {x0} {cy - hw * .38:.1f} {x0} {cy}"
            f"C{x0} {cy + hw * .38:.1f} {x0 + t * .42:.1f} {y1} {x0 + t:.1f} {y1}H{x1}Z")


def blade_v(cx, apex, base, lit=False, sw=1.3):
    """Vertical blade, tip up, true diameter: white tube with the tip's seam, or glowing green when lit."""
    hw = 25.4 * HMM / 2
    d = bullet_v(cx, hw, apex, base)
    seam = f'<path d="M{cx - hw:.1f} {apex + TIP_MM * HMM:.1f}H{cx + hw:.1f}" stroke="#8a9295" stroke-width="{sw * .8}"/>'
    if lit:
        return (f'<path d="{d}" fill="#3CFF6A" opacity=".6" filter="url(#glow)"/><path d="{d}" fill="url(#g-blade)"/>')
    return f'<path d="{d}" fill="url(#g-tube)" stroke="#141414" stroke-width="{sw}"/>{seam}'


FADE_L = 214  # every faded blade shows this much beyond the emitter, in hilt units (the hilt is 471)


def fade_end(content, d="left"):
    """Blade fading out toward the left or up; the fade reaches zero before the blade's end, so no edge shows."""
    return f'<g mask="url(#fade{d})">{content}</g>'


def blade_h(x0, x1, y0=76, y1=116, lit=False, fade=False, color="green"):
    """Horizontal blade (emitter on the right of the blade): white tube, or glowing when lit (green or purple).
    fade: no tip, the blade fades out toward the left, for blades too long to fit."""
    d = f"M{x0} {y0}H{x1}V{y1}H{x0}Z" if fade else bullet_h(x0, x1, y0, y1)
    if lit:
        glow, grad = ("#3CFF6A", "g-blade-h") if color == "green" else ("#B868FF", "g-purple-h")
        b = f'<path d="{d}" fill="{glow}" opacity=".6" filter="url(#glow)"/><path d="{d}" fill="url(#{grad})"/>'
        return fade_end(b) if fade else b
    return f'<path d="{d}" fill="url(#g-tube-h)" stroke="#141414" stroke-width="1.3"/>'


def page_color(pn):
    dots = "".join(f'<circle cx="{40 + i * 26}" cy="52" r="8" fill="{c}"/>' for i, c in enumerate(SWATCHES))
    twist = ('<path class="arrow" data-head="1" d="M652 58C676 62 676 130 652 134"/>'
             '<path class="arrow" data-head="1" d="M632 134C608 130 608 62 632 58"/>')
    art = (f'<svg viewBox="0 36 720 112" class="art" style="height:14mm">'
           f'{dots}{blade_h(224 - FADE_L, 224, lit=True, fade=True, color="purple")}{hz("top-mini", "body-mini", dx=180)}{twist}</svg>')
    steps = [
        "With the blade on, point it parallel or down and press 4 Clicks. Color change starts",
        "Hold the blade level and roll the whole saber on its long axis. The blade steps through the colors",
        "Click to save the color. Long Click to cancel and keep the old one",
    ]
    body = "".join(f'<div class="step">{num(i)}<div><p>{sent(t)}</p></div></div>' for i, t in enumerate(steps, 1))
    style = ctl_table([("Triple Click + Long Click|parallel or up", "Next blade style"),
                       ("Triple Click + Long Click|down", "Previous blade style")])
    return f"""<div class="page steps nosep"><h1>Color</h1>{art}{body}
<p class="tip">Color zoom: during step 2, Double Click and Hold, then turn a little at a time for fine steps. Let go to save.</p>
{sub("Blade style (blade on)", GREEN)}{style}
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_music(pn):
    player = ctl_table([
        ("Turn right", "Next track"),
        ("Turn left", "Previous track"),
        ("Click", "Play this track once"),
        ("Hold", "Play, then shuffle"),
        ("Hold + Turn right", "Play, then the next tracks in order"),
        ("Hold + Turn left", "Repeat this track"),
    ])
    return f"""<div class="page"><h1>Music</h1>
<p>With the blade off, Double Click pointing straight up to play or stop the font's music. Double Click parallel or down to open the music player.</p>
{sub("In the music player", "#E44F44")}{player}
<p class="tip">With the blade on, Double Click stops the music. To pick a track, turn the blade off first.</p>
{sub("Force sounds and quotes", GREEN)}
<p>Triple Click (blade off) or Long Click (blade on) plays a Force sound or a character quote. Point straight down when you press to switch between Force and quote mode. Quotes play in order.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def burst(x, y):
    return "".join(f'<path class="arrow" d="M{x - 4 * math.cos(math.radians(a)):.1f} {y + 4 * math.sin(math.radians(a)):.1f}L{x - 28 * math.cos(math.radians(a)):.1f} {y + 28 * math.sin(math.radians(a)):.1f}"/>'
                   for a in range(-60, 61, 30))


def mini(extra):
    """Motion icon: horizontal hilt (emitter left at x=14, pommel right at x=485) plus green arrows."""
    return f'<svg viewBox="-200 30 726 132">{blade_h(14 - FADE_L, 14, lit=True, fade=True)}{hz("top-mini", "body-mini", dx=-30)}{extra}</svg>'


def page_motion(pn):
    twist = '<path class="arrow" data-head="1" d="M412 54C436 58 436 134 412 138"/>'
    rows = [
        ("Clash", "Hit the blade against something. Hold Power as you hit for lockup", burst(-32, 98)),
        ("Stab", "Thrust forward so the tip hits. Hold Power as you stab for drag (pointing down) or melt",
         '<path class="arrow" data-head="1" d="M300 154H140"/>' + burst(-32, 98)),
        ("Swing", "A firm swing. Hold Power and swing for multi-blast mode",
         '<path class="arrow" data-head="1" d="M440 50Q240 6 40 50"/>'),
        ("Turn right / left", "Roll the whole saber on its long axis with the blade level. Each step is about 30°. Nothing unscrews. The menus for presets, volume, color and music use it", twist),
        ("Gesture ignition", f"Swing, stab, twist or thrust to ignite, if your saber has gestures turned on. Hold Power + Clash pointing down turns gestures on or off.{TODO}",
         '<path class="arrow" data-head="1" d="M300 46H140"/>' + twist),
    ]
    body = "".join(f'<div class="mo">{mini(art)}<div><b>{t}</b><span>{sent(d)}</span></div></div>' for t, d, art in rows)
    return f"""<div class="page"><h1>Motion</h1><div class="mos">{body}</div><div class="pn">&lt; {pn} &gt;</div></div>"""


def page_errors(pn):
    rows = [("Font directory not found", "The board can't find a preset's sound folder on the SD card, or can't read the card right now. A loose blade causes it too. It says this once for each missing folder", "Push the blade all the way in and tighten both blade screws. Then charge, restart the core and check the folder names match the presets"),
            ("SD card not found", "The board can't see the card at all", "Restart the core. The card must be FAT32"),
            ("Error in font directory", "A font has missing or misnumbered files, or the menu voice files are gone", "Copy the font and the common folder back"),
            ("Voice pack not found", "The common folder with the menu voice is missing", "Copy common back onto the card"),
            ("Error in voice pack version", "The common folder is too old for ProffieOS 8", "Install the newer voice pack"),
            ("Error in blade array", "The board doesn't detect the blade it expects", "Push the blade all the way in, then restart"),
            ("Low battery", "The battery is running down", "Charge it")]
    body = "".join(f"<tr><td>\u201c{a}\u201d</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return f"""<div class="page"><h1>Common errors</h1>
<p>A robot voice names each problem the board finds. The voice is built into the board, so it works even when the SD card can't be read. It sounds muffled and clipped.</p>
<table class="tbl spec errs"><tr><th>It says</th><th>Meaning</th><th>Fix</th></tr>{body}</table>
<p class="note">To restart the core, slide it out and back in, or click its power switch off and on (page {P['core']}).</p>
<p class="tip">A saber set up without the voice plays a short tune instead, one note per syllable of the same messages. Hear each one at {link('pod.hubbe.net/troubleshooting/beep_codes.html')}.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_trouble(pn):
    qa = [
        ("Saber won't turn on",
         "Charge it. Check the core went back in speaker end first, and screw the pommel on tight so the gold pins touch"),
        ("Saber says \u201cFont directory not found\u201d",
         f"Push the blade all the way in and tighten both blade screws (page {P['structure']}). A loose blade loses contact with the pogo pins, so the board can't identify it"),
        ("The saber speaks an error", f"Look it up under Common errors (page {P['errors']})"),
        ("No sound",
         "Turn the volume up (Hold Power + Clash, blade off)"),
        ("Presses do the wrong thing",
         f"Check the blade angle (page {P['angle']}). Long Click does different things pointing up and down"),
        ("Saber turns on when you move it",
         "Gestures are on. Hold Power + Clash pointing down to turn them off"),
        ("Blade flickers or only half lights",
         "Push the blade all the way into the emitter and tighten the two retention screws"),
    ]
    body = "".join(f'<div class="qa">{num(i)}<div><b>{q}</b><p>{sent(a)}</p></div></div>' for i, (q, a) in enumerate(qa, 1))
    return f"""<div class="page"><h1>Troubleshooting</h1>{body}<div class="pn">&lt; {pn} &gt;</div></div>"""



def page_works(pn):
    rows = [("Light", "A blade style gives each LED a color, and the board works the colors out again for each frame. An ignition is a style that lights the LEDs from the hilt up"),
            ("Sound", "Sounds are WAV files on the SD card. The board mixes up to five at once, such as the hum, a swing and a clash, and plays them through the speaker"),
            ("Effects", "A hit, a stab or a press gives the board an event. The board passes it to the blade style, which flashes the blade, and to the sound font, which plays the clash, in the same frame"),
            ("Presets", "A preset pairs one sound font with one blade style. Switching presets changes the whole saber at once")]
    body = "".join(f'<div class="qa"><div><b>{a}</b><p>{sent(b)}</p></div></div>' for a, b in rows)
    return f"""<div class="page"><h1>How the core works</h1>
<p>The board is a small computer. Many times a second it reads the motion sensor and the button, works out what happened, then updates the blade and the sound.</p>
{flow_art()}{body}
<p class="tip">You can change each of these in software (page {P['change']}).</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def build_art():
    """Config file to Proffieboard, left to right."""
    steps = [("Config file", "text you edit"), ("Compiler", "on a computer"), ("Firmware", "one file"), ("Proffieboard", "over USB")]
    box = lambda x, t, s: (f'<rect x="{x}" y="1" width="49" height="26" rx="4" style="stroke-width:.6"/>'
                           f'<text x="{x + 24.5}" y="12.5" data-pt="5">{t}</text><text class="s" x="{x + 24.5}" y="21" data-pt="4.6">{s}</text>')
    xs = [0, 57, 114, 171]
    arrows = "".join(f'<path class="arrow" data-head="1" d="M{x + 50} 14H{x + 56}"/>' for x in xs[:-1])
    return f'<svg viewBox="0 0 220 28" class="art arch">{"".join(box(x, t, s) for x, (t, s) in zip(xs, steps))}{arrows}</svg>'


def page_proffie(pn):
    rows = [("Firmware, in the processor", "Your config file: blade styles, button logic, features", "Upload from a computer"),
            ("SD card", "Sound fonts, music, quotes, menu voice", "Copy files"),
            ("Saved settings, on the SD card", "Edit Mode changes: font, color, timings", "On the saber")]
    body = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return f"""<div class="page"><h1>What is Proffie</h1>
<p>Proffie is this saber's board and the software it runs: the Proffieboard and ProffieOS. Fredrik Hübinette designed both, and the name comes from his nickname, Profezzorn.</p>
<p>Anyone can read, change and share ProffieOS under the GPLv3 license, and Fredrik publishes the board's design files. You can reprogram this saber yourself.</p>
{sub("Where things live", GREEN)}
<table class="tbl ang"><tr><th>Where</th><th>What</th><th>Change it</th></tr>{body}</table>
{sub("From config to saber", "#E44F44")}
{build_art()}
<p>You edit the config as plain text. A compiler on your computer turns it into firmware, and the upload replaces the program on the processor. Fonts and settings on the SD card stay as they are.</p>
<p class="tip">ProffieOS 8 came out in 2026 and runs on this 2019 board. Updates stay free.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_change(pn):
    levels = [("On the saber", f"Pick a preset, then change its color, sound font, blade length, ignition speed or volume in Edit Mode (page {P['edit']}). Record a fight to replay with Rehearsal (page {P['rehearsal']})"),
              ("On the SD card", f"Add sound fonts, music to play along with, or quotes. Replace one sound, such as the hum, with any WAV file of your own (page {P['fonts']})"),
              ("In the code", f"Write new blade effects, such as fire, an unstable blade or a rainbow. Change what each press does, turn gestures on or off, or give Quinlan Vos a light and a dark font that swap as he turns (pages {P['connect']} to {P['styles']})"),
              ("In the hardware", f"Add Bluetooth so Workbench connects without a cable, or more accent LEDs. These need a soldering iron (page {P['mods']})")]
    body = "".join(f'<div class="qa">{num(i)}<div><b>{a}</b><p>{sent(b)}</p></div></div>' for i, (a, b) in enumerate(levels, 1))
    ideas = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in [
        ("A red blade and a darker hum for Vos's dark side", "1 and 2"), ("Your own voice as the boot sound", "2"),
        ("Ignite with a swing instead of the button", "1"), ("The crystal in a different color from the blade", "3"),
        ("A blade that crackles during a lockup", "3")])
    return f"""<div class="page"><h1>What you can change</h1>
<p>Start at the top. Each step needs more tools and can change more.</p>{body}
{sub("Ideas for this saber", GREEN)}
<table class="tbl spec ideas"><tr><th>Idea</th><th>Step</th></tr>{ideas}</table>
<p class="tip">Back up the SD card and the config before changing anything in the code (page {P['backup']}).</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_vs(pn):
    rows = [("Software", "Closed", "Open source, GPLv3"), ("Board design", "Closed", "Open hardware, design files published"),
            ("Blade effects", "A fixed list", "Any effect you can code"), ("Buttons and gestures", "Fixed", "A prop file you can rewrite"),
            ("Sounds", "Played on cue", "Switched and triggered by blade code"), ("Updates", "From the maker", "Free, from the community")]
    body = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return f"""<div class="page"><h1>Proffie vs others</h1>
<p>Other sabers use the same kind of LEDs, battery and speaker, but their makers keep the code closed.</p>
<table class="tbl ang" style="margin-top:3mm"><tr><th></th><th>Most sabers</th><th>Proffie</th></tr>{body}</table>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_types(pn):
    blades = [("Light source", "One LED in the hilt", "LED strips inside the blade"), ("Ignition", "Fades on", "Grows from the hilt up"),
              ("Clash", "The whole blade flashes", "A flash where it hits"), ("Dueling", "Toughest", "Needs a heavy-grade blade")]
    boards = [("Xenopixel", "Closed", "Phone app"), ("SN-Pixel", "Closed", "Phone app"), ("Golden Harvest", "Closed", "Menu, phone app"),
              ("CFX", "Closed", "Menu, text files"), ("Verso", "Closed", "Menu"), ("Proffie", "Open", "Menu, browser, code")]
    t1 = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in blades)
    t2 = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in boards)
    return f"""<div class="page"><h1>Saber types</h1>
<p>A baselit saber lights a hollow blade with an LED in the hilt, so the whole blade shows one color at a time. A Neopixel blade has its own LED strips inside.</p>
{sub("Blades", GREEN)}
<table class="tbl ang"><tr><th></th><th>Baselit</th><th>Neopixel</th></tr>{t1}</table>
{sub("Sound boards", "#E44F44")}
<table class="tbl ang"><tr><th>Board</th><th>Code</th><th>Set up with</th></tr>{t2}</table>
<p class="tip">This saber has a Neopixel blade, 1 in wide with a heavy 3 mm wall, and a Proffieboard V2.2.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_parts(pn):
    """Exploded view: blade and hilt on one axis, the core below where it sits inside, pogo joints marked."""
    dx = 106  # hilt shift: emitter ring at x 150
    up, dn = -30, 50  # row offsets: hilt axis at 66, core axis at 146
    e, c0, c1 = RING[0] + dx, CORE[0] + dx, CORE[1] + dx
    k = call_k(69 * 192 / 640, 192)  # the drawing fills the 69 mm text width
    guides = f'<path d="M{c0} {66 + 20}V{146 - 20}M{c1} {66 + 20}V{146 - 20}" stroke="#5a5a5a" stroke-width="1" stroke-dasharray="3 3"/>'
    calls = (callout_v(1, 12, 70, 66, k) + callout_v(2, 12, e - 2, 66, k) + callout_v(3, 12, 300, 66 - 14, k)
             + callout_v(2, 182, c0 - 4, 146, k) + callout_v(4, 182, 470, 146 + 14, k))
    art = (f'<svg viewBox="0 0 640 192" class="art" style="margin-top:4mm">'
           f'<g transform="translate(0 {up})">{fade_end(blade_h(-60, e + 4, lit=True, fade=True))}{hz("top-mini", "body-mini", dx=dx)}</g>'
           f'{guides}<g transform="translate(0 {dn})">{hz("core-mini", dx=dx)}</g>{calls}</svg>')
    parts = [("Blade", "A polycarbonate tube with two LED strips inside, back to back. Each LED holds its own red, green and blue light and a tiny chip, so it can show any color on its own. The board sends a stream of colors up the strips and changes them to make the blade grow from the hilt or flicker like fire"),
             ("Pogo pins", "Spring-loaded contacts at both joints, so the blade and the core connect without plugs or wires"),
             ("Hilt", "The metal shell. It holds the button and the wires between the two joints. The rest of the electronics sit in the core"),
             ("Core", f"One removable unit: board, battery, speaker, charging port and accent LEDs (page {P['core']})")]
    body = "".join(f'<div class="qa">{num(i)}<div><b>{a}</b><p>{sent(b)}</p></div></div>' for i, (a, b) in enumerate(parts, 1))
    return f"""<div class="page"><h1>How it fits together</h1>
<p>A saber is a blade, a hilt and a core. The core slides out of the hilt, and the board inside it controls the light and the sound.</p>{art}{body}
<p class="note">The board is the circuit board inside the core, also called the sound board. It runs the software, so it sets the sounds, blade effects and controls. Lightsabers are typically named after the board type they use; a Proffie saber is a lightsaber with a Proffieboard core.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_fits(pn):
    qa = [("A Xenopixel core fits this hilt", "Padawan Outpost sells this model with a Xenopixel V3 or a Proffie V2.2 core. Both are the same pogo core size and drive the same blade"),
          ("Xenopixel and Proffie share blades", "Any 1 in Neopixel blade with a three-ring contact disc works with either board"),
          ("A baselit core needs another emitter", "A baselit core shines its own LED up a hollow blade, and this emitter holds the pin connector for a Neopixel blade"),
          ("A baselit blade stays dark", "It fits, but a hollow blade has no LEDs, and this hilt has no LED to shine into it"),
          ("Other pogo cores need the same format", "The core must be 1 in wide, with the same length and pin layout. LGT, Nexus and DamienSaber hilts share it. Check with the seller for other brands"),
          ("You can swap the board alone", "It takes soldering. The board comes out of the core, and the battery and speaker stay"),
          ("Your settings stay with the old core", f"Fonts and presets live on its SD card and board. Copy the card first (page {P['backup']})")]
    body = "".join(f'<div class="qa"><div><b>{q}</b><p>{sent(a)}</p></div></div>' for q, a in qa)
    return f"""<div class="page"><h1>What fits what</h1>{body}
<p class="tip">A store that lists a core for Baselit, Xenopixel V3 and Proffie V2.2 hilts sells three versions, one per board. For this saber, choose the Proffie V2.2 version. Padawan Outpost lists this hilt as PO x KR core compatible.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


GLOSSARY = [("Alt font", "A second set of sounds inside a font folder, in alt000, alt001 and so on. Blade code can switch to it live"),
            ("Blade style", "ProffieOS code that sets how the blade looks: color, ignition, flicker and the flash on a clash"),
            ("Bootloader", "A program built into the processor that takes new firmware over USB. Nothing can erase it"),
            ("Config file", "The C++ file that describes this saber: blade, button, presets and features"),
            ("Core", "Board, battery and speaker in one removable unit that slides into the hilt"),
            ("Neopixel", "A blade lined with LED strips in which each LED shows its own color"),
            ("Pogo pins", "Spring-loaded contacts that connect the blade and the core to the hilt without plugs"),
            ("Preset", "One saved setup: a sound font, a blade style and a music track"),
            ("Prop file", "The part of ProffieOS that turns presses and gestures into actions. This saber uses the Fett263 prop"),
            ("Proffieboard", "The sound board in this core. This one is V2.2, and it runs the open-source ProffieOS"),
            ("Serial monitor", "A text window for typing commands to the saber over USB"),
            ("SmoothSwing", "A sound engine that blends two looping swing sounds live, following how fast the blade moves"),
            ("Sound board", "The circuit board that runs a saber's software, such as a Proffieboard or a Xenopixel. It sits in the core"),
            ("Sound font", "A folder of sound files for one character, such as hum, ignition, swing and clash"),
            ("Style argument", "A color or time left open in a blade style, so Edit Mode can change it without new firmware"),
            ("Workbench", "ProffieOS Workbench, a web page that controls and edits the saber over USB")]


def page_glossary(pn):
    rows = "".join(f"<div><b>{a}</b><span>{sent(b)}</span></div>" for a, b in GLOSSARY)
    return f"""<div class="page"><h1>Glossary</h1><div class="gloss">{rows}</div>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def code(text):
    """Code block; text after // on a line is a gray comment."""
    lines = []
    for ln in html.escape(text).split("\n"):
        c, sep, rest = ln.partition(" //")
        lines.append(c + (f' <span class="c">//{rest}</span>' if sep else ""))
    return f'<pre><code>{"<br>".join(lines)}</code></pre>'


def steps(items):
    return "".join(f'<div class="step">{num(i)}<div><p>{sent(t)}</p></div></div>' for i, t in enumerate(items, 1))


def page_connect(pn):
    shows = [("Serial port", "A command line into the saber"), ("WebUSB", "For ProffieOS Workbench in Chrome or Edge"),
             ("Drive", "The SD card, for copying fonts")]
    cmds = [("version", "ProffieOS version"), ("list_presets", "All presets"), ("battery_voltage", "Battery level"),
            ("sdtest", "SD card speed"), ("on, off, clash", "Test effects"), ("RebootDFU", "Bootloader mode")]
    t1 = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in shows)
    t2 = "".join(f"<tr><td><code>{a}</code></td><td>{b}</td></tr>" for a, b in cmds)
    return f"""<div class="page"><h1>Connect a computer</h1>
<p>Open the gold core and plug into the micro-USB port on the Proffieboard. The USB-C port on the core only charges. For a computer with small oval ports, get a USB-C to Micro-USB cable; for wide rectangular ports, USB-A to Micro-USB.</p>
<p class="tip">The cable must carry data. Stores list it as a data or sync cable. Charge-only cables look the same and won't work. Cables from phones and game controllers tend to carry data, and ones from lamps and fans often don't. If nothing appears on the computer, try another cable.</p>
{sub("What shows up", GREEN)}
<table class="tbl spec"><tr><th>Device</th><th>Use</th></tr>{t1}</table>
{sub("Serial commands", "#E44F44")}
<table class="tbl spec"><tr><th>Type</th><th>Result</th></tr>{t2}</table>
<p class="tip">The devices you see depend on the board's firmware settings. Workbench: {link('profezzorn.github.io/lightsaber-web-bluetooth/app.html')}</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_backup(pn):
    body = steps(["Copy the whole SD card to your computer, including the .ini and .tmp files. They hold your Edit Mode changes",
                  "Find the config file: a .h file on the card, or inside a ProffieOS zip. If it's missing, ask DamienSaber for it. The board can't give it back",
                  f"Save the firmware. In Chrome, open {link('profezzorn.github.io/webdfu/dfu-util', 'https://profezzorn.github.io/webdfu/dfu-util/')}, send <code>RebootDFU</code> over serial, click Connect, then Read"])
    return f"""<div class="page steps"><h1>Back up first</h1>
<p>Save three things before changing anything. Each one lets you undo a mistake.</p>{body}
<p class="note">To undo Edit Mode changes, delete presets.ini and presets.tmp from the card, then restart the saber.</p>
<p class="tip">You can recover from a bad upload. Hold BOOT, press RESET, then let go of BOOT, and the processor's built-in bootloader takes new firmware.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_setup(pn):
    body = steps(["Clone the code: <code>git clone github.com/profezzorn/ProffieOS</code>, or download release 8.10 or later",
                  "Install the Arduino IDE or arduino-cli. Add the board URL below, then install the Proffieboard plugin",
                  "Choose Proffieboard V2. Set USB Type to Serial + Mass Storage + WebUSB and DOSFS to SDCARD (SPI)",
                  "Put the config in ProffieOS/config and set <code>CONFIG_FILE</code> in ProffieOS.ino to its name"])
    return f"""<div class="page steps"><h1>Set up the code</h1>{body}
{code("https://profezzorn.github.io/arduino-proffieboard/\n  package_proffieboard_index.json")}
{code("arduino-cli compile --fqbn proffieboard:stm32l4:\\\n  ProffieboardV2-L433CC ProffieOS.ino")}
<p class="tip">ProffieConfig (Mac, Windows) and JMT Studio (Mac, Windows, Linux) edit, build and upload in one app, without Arduino.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_first(pn):
    body = steps(["Build and upload the factory config unchanged. The saber should behave as before",
                  "Make one small edit, such as a color in the first preset or an ignition time from 300 to 600 ms",
                  "Upload and test it with the blade on",
                  "Commit the config to git, so you keep each working version"])
    return f"""<div class="page steps"><h1>Your first change</h1>
<p>Start from a build that matches the factory one, then change one thing at a time.</p>{body}
<p class="note">Uploading clears Edit Mode changes unless the config has <code>#define KEEP_SAVEFILES_WHEN_PROGRAMMING</code>.</p>
<p class="tip">Stuck? Ask on The Crucible, {link('crucible.hubbe.net')}. Fredrik and Fett263 answer questions there.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_config(pn):
    rows = [("CONFIG_TOP", "Board, button count, volume, clash threshold and features"),
            ("CONFIG_PROP", "The button logic: saber_fett263_buttons.h"),
            ("CONFIG_PRESETS", "Each preset's font, track, style and name, and the blade's pixels and pins"),
            ("CONFIG_BUTTONS", "The Power button")]
    t = "".join(f"<tr><td><code>{a}</code></td><td>{b}</td></tr>" for a, b in rows)
    snippet = ('{ "Vos;common", "tracks/vos.wav",   // font, track\n'
               '  StylePtr<...>(), "green" },        // style, name\n\n'
               'WS281XBladePtr<144, bladePin,       // pixels, data pin\n'
               '  Color8::GRB,\n'
               '  PowerPINS<bladePowerPin2, bladePowerPin3> >()')
    return f"""<div class="page"><h1>The config file</h1>
<p>A config is one C++ file that describes this saber. ProffieOS reads it once for each section.</p>
<table class="tbl spec" style="margin-top:2.5mm"><tr><th>Section</th><th>Holds</th></tr>{t}</table>
{code(snippet)}
{sub("Without a new upload", GREEN)}
<p>Fonts, colors, timings and preset order change in Edit Mode or Workbench.</p>
{sub("With a new upload", "#E44F44")}
<p>New blade styles, new features and button changes.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_styles(pn):
    snippet = ("StylePtr<Layers<\n"
               "  AudioFlicker<Green, Rgb<0,128,0>>,   // base\n"
               "  ResponsiveClashL<White>,             // clash flash\n"
               "  InOutTrL<TrWipe<300>, TrWipeIn<500>> // on, off\n"
               ">>()")
    return f"""<div class="page"><h1>Blade styles</h1>
<p>A blade style is code that sets the color of each LED, many times a second. Styles stack in layers. Even Green is a style, so you can swap any color for an effect.</p>
{code(snippet)}
{sub("Style Editor", GREEN)}
<p>Paste a style and watch the blade animate, then trigger clashes and lockups. {link('fredrik.hubbe.net/ProffieOS-StyleEditor', QR_URLS['styleeditor'])}</p>
{sub("Fett263 Style Library", "#E44F44")}
<p>Build styles from menus, with Edit Mode options built in. {link('fett263.com', QR_URLS['fett263'])}</p>
<p class="tip">Copies of one style with different colors take no extra memory when the colors are style arguments, such as <code>RgbArg&lt;BASE_COLOR_ARG, Green&gt;</code>.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def flow_art():
    """Inputs, events and outputs: how the board turns motion and presses into light and sound."""
    box = lambda x, y, t, s: (f'<rect x="{x}" y="{y}" width="58" height="26" rx="4" style="stroke-width:.6"/>'
                              f'<text x="{x + 29}" y="{y + 11.5}" data-pt="5">{t}</text><text class="s" x="{x + 29}" y="{y + 20}" data-pt="4.6">{s}</text>')
    return (f'<svg viewBox="0 0 220 112" class="art arch">'
           + box(0, 2, "Motion sensor", "1,600 a second") + box(0, 84, "Power button", "prop file")
           + box(81, 43, "Events", "clash, swing, on, off")
           + box(162, 2, "Sound", "mixer, 5 at once") + box(162, 84, "Blade style", "each LED, each frame")
           + '<path class="arrow" data-head="1" d="M60 15H160"/><text class="s" x="110" y="11" data-pt="4.6">swing speed</text>'
           + '<path class="arrow" data-head="1" d="M30 30V44C30 52 40 56 79 56"/>'
           + '<path class="arrow" data-head="1" d="M30 84V70C30 62 40 60 79 60"/>'
           + '<path class="arrow" data-head="1" d="M141 54C180 54 191 48 191 30"/>'
           + '<path class="arrow" data-head="1" d="M141 62C180 62 191 66 191 82"/></svg>')


def page_hood(pn):
    return f"""<div class="page"><h1>Under the hood</h1>
{sub("SmoothSwing", GREEN)}
<p>Two looping swing sounds play at zero volume under the hum. Swing speed sets their volume, and the board fades from one to the other as the blade turns. The hum dips as you swing.</p>
{sub("Clash detection", "#E44F44")}
<p>A clash is a jolt that doesn't match how the saber is moving. Sound from the speaker shakes the sensor too, so ProffieOS raises the threshold as you turn the volume up.</p>
{code("|accel - down|/2 + |delta gyro|/2 > threshold")}
<p class="tip">STM32L433 at 80 MHz, 256 KB flash, 64 KB RAM. ProffieOS has no operating system kernel. Its tasks take turns in one loop.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_mods(pn):
    ideas = [("Upgrade to ProffieOS 8", "New menus, SD card protection and independent dual blades"),
             ("Rewrite a button", "Copy the prop file and change one EVENTID line"),
             ("Write a style", "A class with run() and getColor(). Test it on your computer with make test in styles"),
             ("Light and dark fonts", "An alt font replaces the whole sound set when the style changes, as Quinlan Vos falls to the dark side in Dark Disciple"),
             ("Mini games", "Fett263's training remote game runs inside a blade style"),
             ("Debug the board", "An ST-LINK on the SWDIO and SWCLK pads gives breakpoints on the real hardware"),
             ("Add Bluetooth", "An FSC-BT630 module lets Workbench connect without a cable"),
             ("Read the hardware", f"KiCad files and the schematic are at {link('fredrik.hubbe.net/lightsaber/v5')}")]
    body = "".join(f'<div class="qa"><div><b>{a}</b><p>{sent(b)}</p></div></div>' for a, b in ideas)
    return f"""<div class="page"><h1>Modding ideas</h1>{body}<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_links(pn):
    links = [("pod", "ProffieOS docs", "pod.hubbe.net"), ("crucible", "The Crucible", "Support forum"),
             ("fett263", "Fett263", "Prop, styles, config helper"), ("styleeditor", "Style Editor", "Live blade preview"),
             ("workbench", "Workbench", "Edit the saber in Chrome"), ("github", "ProffieOS", "Source code on GitHub")]
    body = "".join(f'<figure>{qr(f)}<figcaption><b>{link(t, QR_URLS[f])}</b><small>{d}</small></figcaption></figure>' for f, t, d in links)
    return f"""<div class="page"><h1>Resources</h1><div class="links">{body}</div><div class="pn">&lt; {pn} &gt;</div></div>"""


def page_board(pn):
    """Proffieboard V2.2 pinout, top side, turned to match the core page: micro-USB end up (toward the speaker),
    driver end down. Pad order and positions follow the board's published pinout, rotated 180 degrees."""
    k, W = 1.6, 69  # drawing units are page mm; the board is drawn 1.6 times real size
    bw, bh = 17.8 * k, 33.2 * k
    ox, oy = (W - bw) / 2, 9
    X = lambda x: round(ox + x * k, 2)
    Y = lambda y: round(oy + y * k, 2)
    rows = [1.36 + i * 2.54 for i in range(13)]
    left = ["SD power", "Data 2", "SCL", "SWDIO", "SWDCLK", "RX", "Data 3", "Button 3", "Speaker \u2212", "Speaker +",
            "Battery \u2212", "LED 6", "Button 2"]
    right = ["Data 4", "TX", "Blade data, ID", "3.3 V out", "GND", "Reset", "SDA", "5 V out", "Battery +", "GND",
             "Battery \u2212", "LED 1", "Power button"]
    lead = 'stroke="#7a7a7a" stroke-width=".22" stroke-dasharray=".6 .6" fill="none"'
    txt = lambda x, y, t, a: f'<text x="{x}" y="{y}" text-anchor="{a}" dominant-baseline="central" data-pt="5" font-family="Poppins" fill="#CFCFCF">{t}</text>'
    pad = lambda x, y: (f'<circle cx="{X(x)}" cy="{Y(y)}" r="{.85 * k:.2f}" fill="#d9b85a" stroke="#8a6d1f" stroke-width=".15"/>'
                        f'<circle cx="{X(x)}" cy="{Y(y)}" r="{.38 * k:.2f}" fill="#2a2208"/>')
    s = []
    # microSD card: the part under the board dashed, the end that sticks out solid with a light rim
    card = f'<rect x="{X(3.4)}" y="{Y(-2.6)}" width="{11 * k:.2f}" height="{15 * k:.2f}" rx=".8" fill="none" stroke="#8a8a8a" stroke-width=".25" stroke-dasharray=".8 .6"/>'
    s.append(f'<path d="M{X(3.4)} {Y(0)}V{Y(-2.0)}Q{X(3.4)} {Y(-2.6)} {X(4.0)} {Y(-2.6)}H{X(13.8)}Q{X(14.4)} {Y(-2.6)} {X(14.4)} {Y(-2.0)}V{Y(0)}Z" '
             'fill="#232428" stroke="#dfe2e6" stroke-width=".35"/>')
    # board, pads, driver chips, buttons, processor, motion sensor, name
    s.append(f'<rect x="{X(0)}" y="{Y(0)}" width="{bw:.2f}" height="{bh:.2f}" rx=".9" fill="#f2f2ee" stroke="#9a9a96" stroke-width=".2"/>')
    s.append(card)  # the card's outline shows through the board
    s.append("".join(pad(x, y) for x in (1.27, 16.53) for y in rows))
    bottom = {3.81: "LED 5", 6.35: "LED 4", 11.43: "LED 3", 13.97: "LED 2"}
    s.append("".join(pad(x, rows[-1]) for x in bottom))
    s.append("".join(f'<rect x="{X(x)}" y="{Y(26.2)}" width="{2.6 * k:.2f}" height="{2.6 * k:.2f}" rx=".3" fill="#1a1a1a"/>' for x in (2.9, 6.1, 9.1, 12.3)))
    s.append("".join(f'<rect x="{X(x)}" y="{Y(23.4)}" width="{1.4 * k:.2f}" height="{1.4 * k:.2f}" rx=".2" fill="#121212" stroke="#3a3a3a" stroke-width=".15"/>'
                     f'<circle cx="{X(x + .7)}" cy="{Y(24.1)}" r="{.4 * k:.2f}" fill="#2a2a2a"/>' for x in (4.4, 12.0)))  # Reset, Boot: black push buttons
    s.append(f'<rect x="{X(5.4)}" y="{Y(7.4)}" width="{7 * k:.2f}" height="{7 * k:.2f}" rx=".3" fill="#161616"/>'
             f'<circle cx="{X(6.1)}" cy="{Y(8.1)}" r=".35" fill="#3a3a3a"/>'
             f'<rect x="{X(9.6)}" y="{Y(17.2)}" width="{2.5 * k:.2f}" height="{3 * k:.2f}" rx=".2" fill="#1e1e1e"/>')
    s.append(f'<text x="{X(3.6)}" y="{Y(14.5)}" transform="rotate(90 {X(3.6)} {Y(14.5)})" text-anchor="middle" dominant-baseline="central" '
             f'data-pt="4" font-family="Poppins" font-weight="600" fill="#3a3a3a">ProffieBoard V2.2</text>')
    # micro-USB socket over the top edge, mouth facing up
    s.append(f'<rect x="{X(5.15)}" y="{Y(-1.0)}" width="{7.5 * k:.2f}" height="{5.6 * k:.2f}" rx=".5" fill="url(#g-usb)" stroke="#5a5e62" stroke-width=".2"/>'
             f'<path d="M{X(6.0)} {Y(-0.9)}H{X(11.8)}L{X(11.2)} {Y(0.3)}H{X(6.6)}Z" fill="#141414"/>')
    # pad labels down both sides
    for y, t in zip(rows, left):
        s.append(f'<path d="M{ox - 2.4:.2f} {Y(y)}H{X(1.27) - .85 * k:.2f}" {lead}/>' + txt(round(ox - 3.4, 2), Y(y), t, "end"))
    for y, t in zip(rows, right):
        s.append(f'<path d="M{X(16.53) + .85 * k:.2f} {Y(y)}H{ox + bw + 2.4:.2f}" {lead}/>' + txt(round(ox + bw + 3.4, 2), Y(y), t, "start"))
    # LED pad labels below the board, straight under each pad, in two staggered rows so neighbours don't touch
    ly = round(oy + bh + 7, 2)
    for i, (x, t) in enumerate(sorted(bottom.items())):
        y = ly + (3.4 if i % 2 else 0)
        s.append(f'<path d="M{X(x)} {Y(rows[-1]) + .85 * k:.2f}V{y - 2.2:.2f}" {lead}/>' + txt(X(x), y, t, "middle"))
    # Reset and Boot: labels at the foot of the side columns, leads under the board and up a clear channel
    # between the edge pads and the chips, then across to the button
    yl, r = Y(rows[-1] + 2.54), 1
    for t, cx, bx, side in (("Reset", X(2.5), X(4.4), -1), ("Boot", X(15.3), X(13.4), 1)):
        x0 = ox - 2.4 if side < 0 else ox + bw + 2.4
        d = (f"M{x0:.2f} {yl}H{cx + side * r:.2f}Q{cx} {yl} {cx} {yl - r:.2f}V{Y(24.1) + r:.2f}"
             f"Q{cx} {Y(24.1)} {cx - side * r:.2f} {Y(24.1)}H{bx}")
        s.append(f'<path d="{d}" {lead}/>' + txt(round(x0 + side * 1.0, 2), yl, t, "end" if side < 0 else "start"))
    # top labels: socket and card
    s.append(f'<path d="M{X(8.9)} {Y(-1.0)}V3.2" {lead}/>' + txt(X(8.9), 1.6, "Micro-USB data port", "middle"))
    s.append(f'<path d="M{X(3.4)} {Y(-1.6)}H{ox - 2.4:.2f}" {lead}/>' + txt(round(ox - 3.4, 2), Y(-1.6), "microSD card", "end"))
    art = f'<svg viewBox="0 0 {W} {ly + 6.4}" class="art" style="overflow:visible">{"".join(s)}</svg>'
    return f"""<div class="page"><h1>Board<small class="h1-sub">Proffieboard V2.2</small></h1>
{art}
<p class="tip">Hold Boot, press Reset, then let go of Boot to load firmware when uploads fail (page {P['backup']}). Mods solder to free pads, such as RX and TX for Bluetooth.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


PADS = [("Battery +", "Battery input, 2.6 to 4.5 V"),
        ("Battery −", "LED return, joined to GND. Solder the battery's − wire here, not to GND"),
        ("GND", "Ground for the electronics. Both GND pads connect"),
        ("Speaker + / −", "The bass speaker. The + wire has a red dot"),
        ("Buttons 1–3", "Power button and two extra buttons, or touch buttons"),
        ("Blade data, ID", "Data 1. Sends the color signal to the blade and reads the blade ID resistor"),
        ("Data 2, 3", "Extra LED data lines, or free"),
        ("Data 4", "LED data line, free, or audio DAC output"),
        ("LED 1–6", "Negative side of hilt or accent LEDs, up to 30&nbsp;V"),
        ("SDA, SCL", "OLED display, and the motion sensor chip"),
        ("RX, TX", "Bluetooth module"),
        ("SWDIO, SWDCLK", "ST-LINK debugger"),
        ("SD power", "Switched 3.3 V that turns off Bluetooth and OLED to save power"),
        ("5 V out", "Runs only while sound plays"),
        ("3.3 V out", "About 250 mA for an OLED, Bluetooth or accent LEDs"),
        ("Boot, Reset", "Put the board in bootloader mode when uploads fail"),
        ("Micro-USB", "Firmware and SD uploads only. It doesn't charge the battery")]


def page_pads(pn):
    rows = "".join(f"<div><b>{a}</b><span>{sent(b)}</span></div>" for a, b in PADS)
    return f"""<div class="page"><h1>Board pads</h1><div class="gloss pads">{rows}</div>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_tech(pn):
    rows = [("Core", "NexusSabers LGT A.294-1|Proffie V2.2 pogo core, polycarbonate chassis, 25.4 × 185 mm"),
            ("Sound board", "Proffieboard V2.2|Open hardware by Fredrik Hübinette. V3.9 is the current model"),
            ("Processor", "STMicroelectronics STM32L433CC|Arm Cortex-M4F, 80 MHz, 256 KB flash, 64 KB RAM"),
            ("Motion sensor", "STMicroelectronics LSM6DS3H|6-axis: 3-axis accelerometer and 3-axis gyroscope, read 1,600 times a second"),
            ("Audio", "I²S digital audio, class-D amplifier|5 V boost rail, 44 kHz 16-bit, up to 5 sounds at once"),
            ("Speaker", "Bass speaker, 2–3 W, 4 or 8 Ω|At the pommel end of the core. Sound leaves through the pommel holes"),
            ("LED drivers", "6 MOSFET channels|Low-side switching, rated to 30 V"),
            ("Accent LEDs", "LED strip along the core|Lights the crystal chamber in the blade color"),
            ("Battery", "18650 Li-ion, 3.7 V, 3600 mAh|Protected cell: reverse-polarity and overload protection"),
            ("Board input", "2.6–4.5 V"),
            ("Storage", "microSD card|Sound fonts, music, quotes and settings"),
            ("Ports", "USB-C on the core for charging|Micro-USB on the board for configuration"),
            ("Power switch", "Push button by the pogo pins|Cuts the battery for storage or to reset the core"),
            ("Software", "ProffieOS, open source (GPLv3)|Fett263 one-button controls")]
    body = "".join(f"<tr><td>{a}</td><td>{b.split('|')[0]}{f'<small>{b.split(chr(124))[1]}</small>' if '|' in b else ''}</td></tr>"
                   for a, b in rows)
    return f"""<div class="page"><h1>Electronics</h1>
<table class="tbl spec tech"><tr><th>Part</th><th>Model</th></tr>{body}</table>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_blade(pn):
    # True scale in mm, tip at the top: 25.4 mm across, 810 mm long (32 in). The LED strip (10.8 mm wide,
    # measured against the tube in the open-tip photo) is drawn beside the blade at the height it runs inside.
    W, TIP, TUBE0, END = 25.4, 35, 40, 807
    SW, SX = 10.8, -44  # strip width, strip left edge
    kb = call_k(101, 838)
    # unlit tube in the same white as every other unlit blade (g-tube)
    blade = (f'<path d="{bullet_v(W / 2, W / 2, 0, TIP)}" fill="url(#g-tube)" stroke="#141414" stroke-width=".6"/>'
             f'<rect x="0" y="{TIP}" width="{W}" height="{END - TIP}" fill="url(#g-tube)" stroke="#141414" stroke-width=".6"/>'
             f'<path d="M0 {TIP}H{W}" stroke="#8a9295" stroke-width=".5"/>'  # tip seam
             f'<rect x=".3" y="{TIP + .4}" width="{W - .6}" height="2.4" fill="#b8bfc3"/>'  # mirror
             f'<path d="M3 {TUBE0 + 2}V{END - 2}M{W - 3} {TUBE0 + 2}V{END - 2}" stroke="#a9b0b3" stroke-width=".5" stroke-dasharray="5 4"/>'  # wall
             f'<rect x="0" y="{END}" width="{W}" height="4" fill="#C9A646"/>')
    s0, s1 = TUBE0 + 3, END - 3
    lx = SX + SW / 2
    strip = (f'<rect x="{SX}" y="{s0}" width="{SW}" height="{s1 - s0}" rx=".8" fill="#d3d8dc" stroke="#4f565b" stroke-width=".6"/>'
             f'<path d="M{SX + 1.3} {s0 + 2}V{s1 - 2}M{SX + SW - 1.3} {s0 + 2}V{s1 - 2}" stroke="#7a8287" stroke-width=".6"/>'  # power rails
             + "".join(f'<rect x="{lx - 3.3}" y="{y - 3.3:.1f}" width="6.6" height="6.6" rx=".6" fill="#fbfbf9" stroke="#3f454a" stroke-width=".55"/>'
                       f'<circle cx="{lx}" cy="{y:.1f}" r="2.3" fill="#d27887" stroke="#9c4a58" stroke-width=".35"/>'
                       f'<path d="M{SX + 1.3} {y - 2:.1f}h1.2M{SX + 1.3} {y + 2:.1f}h1.2M{SX + SW - 2.5} {y - 2:.1f}h1.2M{SX + SW - 2.5} {y + 2:.1f}h1.2" stroke="#8d969b" stroke-width="1"/>'  # pads
                       for y in [s0 + 5 + i * 8 for i in range(int((s1 - s0 - 10) / 8) + 1)])
             + f'<path class="lead" d="M{SX + SW + 1} {s0}H-1M{SX + SW + 1} {s1}H-1" style="stroke-width:{.6 * kb:.2f};stroke-dasharray:{1.6 * kb:.2f} {1.6 * kb:.2f}"/>')
    calls = [callout(n, "R", cy, (tx, ty), cx=60, k=kb) for n, tx, ty, cy in
             ((1, W - 4, 16, 16), (2, W, TIP + 1, 50), (3, W, 300, 300), (4, lx, 420, 420), (6, W, END + 2, END + 2))]
    art = (f'<svg viewBox="-50 -14 120 838" class="blade-v">{strip}{blade}{"".join(calls)}</svg>')
    rows = [("Bullet tip", "Pointed, threaded polycarbonate tip. It unscrews for repairs only"),
            ("Mirror", "Reflects light back down so the tip glows"),
            ("Tube", "Polycarbonate, 1 in (25.4 mm) outer diameter, 3 mm wall, 32 in (81 cm)"),
            ("LED strips", "Addressable RGB LEDs (Neopixel), two strips back to back"),
            ("Diffusion", "White foam sleeve and clear film spread the light into an even glow"),
            ("Contact disc", "Gold rings at the base meet the spring pogo pins in the emitter. The rings connect at any rotation")]
    body = "".join(f'<div class="part">{num(n)}<div><b>{a}</b>{sent(b)}</div></div>' for n, (a, b) in enumerate(rows, 1))
    # photos side by side in one svg (each 1385 x 1328 px, same angle and diameter), numbered pointers
    pw, ph, gap, col_mm = 1385, 1328, 60, 69 - 101 * 120 / 838 - 3
    u = (4 * pw + 3 * gap) / col_mm  # units per mm on the page
    # 4-6: dot just above the part, its white edge touching it (found from the photo's alpha / gold pixels)
    shots = (("blade_tip_closed", 1, (345, 1035)), ("blade_tip", 4, (520, 487)),
             ("blade_tip_film", 5, (590, 345)), ("blade_contact", 6, (225, 877)))
    cells = ""
    for i, (f, n, (tx, ty)) in enumerate(shots):
        x = i * (pw + gap)
        cells += (f'<image href="img/{f}.png" x="{x}" y="0" width="{pw}" height="{ph}"/>'
                  + callout_v(n, -2.2 * u, x + tx, ty, k=CALL_MM * u / 7))
    photos = f'<svg viewBox="0 {-3.6 * u:.0f} {4 * pw + 3 * gap} {ph + 3.6 * u:.0f}" class="bphotos">{cells}</svg>'
    return f"""<div class="page">{src_qr("blade")}<h1>Blade<small class="h1-sub">NexusSabers A207-1<br>Neopixel<br>heavy-dueling blade</small></h1>
<div class="blade-pg">{art}<div><p style="margin-top:3mm">ProffieOS sends a data signal up the strips, and each LED sets its own color.</p>
{photos}
<div class="parts">{body}</div></div></div>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_crystal(pn):
    steps = [f"Find the sleeve screw on the back of the hilt, behind the crystal window (page {P['structure']}, part 9)",
             "Loosen it about half a turn with the hex key. Don't take it out",
             "Turn the silver sleeve until the window closes, or opens again. Don't force it",
             "Tighten the screw"]
    body = "".join(f'<div class="step">{num(i)}<div><p>{sent(t)}</p></div></div>' for i, t in enumerate(steps, 1))
    art = (f'<svg viewBox="0 40 220 {JOINT_Y + 22 - 40:.0f}" class="art" style="height:50mm">'
           f'<g transform="translate(-50 0)"><use href="#top-sh"/></g>'
           f'<g transform="translate(70 0)"><use href="#top-closed-sh"/></g>'
           f'<path class="arrow" data-head="1" d="M82 226C94 250 126 250 138 226"/>'
           f'<text x="50" y="{JOINT_Y + 18:.0f}" class="cap">Open</text><text x="170" y="{JOINT_Y + 18:.0f}" class="cap">Closed</text></svg>')
    return f"""<div class="page steps"><h1>Crystal cover</h1>{art}
<p>The silver sleeve around the crystal chamber turns, so the window shows either the crystals or the black back of the chamber. Quinlan Vos's hilt in The Clone Wars has no window, so the closed look matches the show.</p>
{body}
<div class="pn">&lt; {pn} &gt;</div></div>"""

SECTIONS = [  # (title, page key, 0 section / 1 indented / 2 part)
    ("1 · Get Started", "p1", 2), ("Safety", "safety", 0), ("Anatomy", "anatomy", 0), ("Structure", "structure", 0), ("In the box", "box", 0), ("How it fits together", "parts", 0),
    ("Quick start", "quick", 0), ("Charging", "charging", 0), ("Crystal cover", "crystal", 0), ("The button", "button", 0),
    ("Blade angle", "angle", 0), ("Control", "off", 0),
    ("Color", "color", 0), ("Music", "music", 0), ("Motion", "motion", 0), ("Common errors", "errors", 0), ("Troubleshooting", "trouble", 0),
    ("2 · Technical Specs", "p2", 2), ("Specifications", "specs", 0), ("Electronics", "tech", 0), ("Core", "core", 0), ("Board", "board", 0), ("Board pads", "pads", 0), ("Blade", "blade", 0),
    ("3 · Customization", "p3", 2), ("How the core works", "works", 0), ("What is Proffie", "proffie", 0), ("What you can change", "change", 0), ("Edit Mode", "edit", 0),
    ("Rehearsal", "rehearsal", 0), ("Sound fonts", "fonts", 0),
    ("Get started with Proffie", "connect", 0), ("Connect a computer", "connect", 1), ("Back up first", "backup", 1),
    ("Set up the code", "setup", 1), ("Your first change", "first", 1),
    ("The config file", "config", 0), ("Blade styles", "styles", 0), ("Under the hood", "hood", 0), ("Modding ideas", "mods", 0), ("Other sabers", "types", 0), ("Saber types", "types", 1), ("What fits what", "fits", 1), ("Proffie vs others", "vs", 1),
    ("Resources", "links", 0), ("Glossary", "glossary", 0),
]


def page_ghost():
    """Empty left half next to the cover in the on-screen spread view; not printed."""
    return '<div class="page ghost"></div>'


def page_cover(pn):
    """Lit saber on the left; brand at the top, title block in the middle, document name at the bottom."""
    return f"""<div class="page cover"><img class="saber" src="img/saber_lit.png"><div class="col">
<img class="brand" src="img/padawan_outpost_cover.svg"><i class="up"></i>
<div class="t1">COMBAT<br>LIGHTSABER</div><div class="t2">MODEL QUINLAN VOS</div><div class="dash"></div>
<div class="who">NEOPIXEL BLADE · PROFFIE V2.2 CORE</div><i class="dn"></i>
<div class="pm">PRODUCT<br>MANUAL</div></div></div>"""


def page_contents(pn):
    """Two columns: parts 1 and 2 on the left, part 3 on the right."""
    rows = [f'<a class="{("sec", "ind", "pt")[ind]}"><span>{t}</span><i></i><span>{P[k]:02d}</span></a>'
            for t, k, ind in sorted(SECTIONS, key=lambda r: (P[r[1]], r[2]))]
    split = next(i for i, (t, k, ind) in enumerate(sorted(SECTIONS, key=lambda r: (P[r[1]], r[2]))) if k == "p3")
    return f'<div class="page toc"><h2>Contents</h2><div class="cols"><div>{"".join(rows[:split])}</div><div>{"".join(rows[split:])}</div></div></div>'


def page_part(n, name):
    return lambda pn: (f'<div class="page divider"><div class="big">{n}</div><div class="dash"></div>'
                       f'<div class="name">{name}</div></div>')


def page_safety(pn):
    warn = '<svg viewBox="0 0 20 18" style="width:4mm;height:3.6mm"><path d="M10 1L19 17H1Z" fill="#E44F44"/><path d="M10 6.5V11.5M10 13.6V14.2" stroke="#0E0E0E" stroke-width="1.8" stroke-linecap="round"/></svg>'
    return f"""<div class="page safe"><h2>Safety notice</h2><div class="dash"></div>
<p>Charge the saber to full before you first use it. Charge it only with the included cable and a 5V 1A USB charger. A stronger charger can damage the battery and electronics.</p>
<p>Don't leave the saber charging unattended, and unplug it when it's full.</p>
<div class="warn"><span>{warn}Warning</span></div>
<p>Keep it away from young children. Older children use it with an adult present.</p>
<p>Duel with control and respect. Don't aim at faces, and stop if the blade cracks.</p></div>"""


def page_specs(pn):
    rows = [("Model", "Combat Lightsaber, Quinlan Vos"), ("Board", "Proffieboard V2.2, removable pogo core"),
            ("Hilt length", "31 cm"), ("Blade", "32 in (81 cm), 1 inch Neopixel"),
            ("Crystal chamber", "Exposed crystal, lights in the blade color"),
            ("Charging", "USB-C on the core, 5V 1A max"), ("Sound", "Fonts, music and quotes on a microSD card"),
            ("Product code", "184-PF"), ("Factory code", "DamienSaber NO184-PF"), ("Warranty", "12 months")]
    body = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return f"""<div class="page"><h1>Specifications</h1>
<table class="tbl spec"><tr><th>Item</th><th>Detail</th></tr>{body}</table>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_box(pn):
    items = [("Hilt", "with Proffie core"), ("Blade", "32 in (81 cm)"), ("USB-C cable", ""),
             ("Hex key and spare screws", "The 5 mm screws hold the blade")]
    body = "".join(f"<div>{a}{f'<small>{b}</small>' if b else ''}</div>" for a, b in items)
    videos = [("gallery", "Product video", "0:30",
               "The core lighting up, then the blade going in and the saber lit"),
              ("assembly", "Assembly video", "2:36", "A full disassembly and rebuild demo"),
              ("damien", "DamienSaber", "", "The maker's page for this saber, with its own photos and videos")]
    vids = "".join(f'<figure>{qr(f)}<figcaption><b>{link(t, QR_URLS[f])}</b><small>{d}</small><p>{x}</p></figcaption></figure>'
                   for f, t, d, x in videos)
    return f"""<div class="page"><h1>In the box</h1><div class="box">{body}</div>
<h1 style="margin-top:6mm">Demos</h1><div class="qr">{vids}</div>
<div class="pn">&lt; {pn} &gt;</div></div>"""


QR_URLS = {"gallery": "https://gv.videocdn.alibaba.com/icbu_vod_video/video_target/gv98-3bb0993e-a1d01ea5-98365f8a-4df0/trans/aidc/ejedf3-h264-hd.mp4",
           "assembly": "https://play.video.alibaba.com/global/play/6000303912425.mp4",
           "damien": "https://www.damiensaber.com/products/quinlan-voss-crystal-lightsaber-bluetooth-app-control-neopixel-blade-no184",
           "pod": "https://pod.hubbe.net/", "crucible": "https://crucible.hubbe.net/", "fett263": "https://www.fett263.com/",
           "styleeditor": "https://fredrik.hubbe.net/ProffieOS-StyleEditor/style_editor.html",
           "workbench": "https://profezzorn.github.io/lightsaber-web-bluetooth/app.html", "github": "https://github.com/profezzorn/ProffieOS",
           "core": "https://www.alibaba.com/product-detail/Proffie-V2-2-Pogo-Core-Accent_1601792428062.html",
           "blade": "https://www.alibaba.com/product-detail/LGT-Heavy-Dueling-1inch-3mm-92cm_1601574174450.html"}
QR_VERSION = 8  # the longest URL (gallery) needs version 8 at level M; every code uses it, so every module is the same size


def qr(name):
    """QR code for QR_URLS[name] from qrencode: version 8, error correction M, 4-module quiet zone."""
    svg = subprocess.run(["qrencode", "-t", "SVG", "--svg-path", "-v", str(QR_VERSION), "-l", "M", "-m", "4", "-o", "-", QR_URLS[name]],
                         capture_output=True, text=True, check=True).stdout
    assert f'viewBox="0 0 {17 + 4 * QR_VERSION + 8} ' in svg, f"{name}: URL too long for version {QR_VERSION}"
    svg = re.sub(r"<!--.*?-->|<\?xml[^>]*>", "", svg)
    svg = svg.replace(' id="QRcode"', "")
    return re.sub(r' width="[^"]*" height="[^"]*"', "", svg, count=1)


def src_qr(name):
    """Small QR to a part's listing, top right of the page, with a text link under it."""
    return f'<div class="src">{qr(name)}{link("Alibaba", QR_URLS[name])}</div>'


def link(text, url=None):
    """Web address shown as text and clickable in the PDF."""
    return f'<a href="{url or "https://" + text}">{text}</a>'


def dim_v(x, y0, y1, label, u, right=False):
    """Engineering dimension, vertical: line with end ticks, label rotated 90° ccw, centred.
    u: drawing units per mm on the page, so the line weight and the 5.6 pt label come out the same everywhere."""
    m, t = (y0 + y1) / 2, 1.1 * u
    tx = x + 2.9 * u if right else x - 1.4 * u  # rotated text sits left of its baseline
    return (f'<g class="dim" style="stroke-width:{.22 * u:.2f}"><path d="M{x} {y0}V{y1}M{x - t:.1f} {y0}H{x + t:.1f}M{x - t:.1f} {y1}H{x + t:.1f}"/>'
            f'<text x="{tx:.1f}" y="{m}" transform="rotate(-90 {tx:.1f} {m})" style="font-size:{1.98 * u:.1f}px">{label}</text></g>')


def dim_h(y, x0, x1, label, u):
    """Engineering dimension, horizontal: line with end ticks, label below, centred."""
    t = 1.1 * u
    return (f'<g class="dim" style="stroke-width:{.22 * u:.2f}"><path d="M{x0} {y}H{x1}M{x0} {y - t:.1f}V{y + t:.1f}M{x1} {y - t:.1f}V{y + t:.1f}"/>'
            f'<text x="{(x0 + x1) / 2}" y="{y + 3.4 * u:.1f}" style="font-size:{1.98 * u:.1f}px">{label}</text></g>')


def page_quickstart(pn):
    """Four steps, each with a drawing: the full charging light, then the saber lying flat (emitter left of the hilt)."""
    dx = 300  # hilt shift: emitter at x 344
    e = RING[0] + dx
    W = 737  # viewBox width
    x0 = e - FADE_L - (W - (dx + END_Y - (e - FADE_L))) / 2  # blade + hilt centred; in step 2 the blade sits further left
    view = lambda y, h: f'class="pic" viewBox="{x0:.1f} {y} {W} {h}" preserveAspectRatio="xMidYMid meet"'
    vb = view(50, 78)
    hilt = hz("top-mini", "body-mini", dx=dx)
    blade_in = fade_end(blade_h(e - FADE_L, e + 4, fade=True))
    # 1: the core on charge, light green
    s1 = f'<div class="duo">{plugged("#3cd86a", "Full")}</div>'
    # 2: blade apart from the emitter, arrow pushing it in
    s2 = (f'<svg {vb}>{fade_end(blade_h(e - 40 - FADE_L, e - 40, fade=True))}{hilt}'
          f'<path class="arrow" data-head="1" d="M{e - 150} 62H{e - 46}"/></svg>')
    # 3: blade in, green dots on the two screws, a forked line up to the screw at 2:1 in a circle
    k = call_k(69 * 128 / W, 128)
    holes = [dx + y for _, y in SCREW_HOLES]
    zx, zy, rc = sum(holes) / 2, 24, 22  # zoom circle above the screws
    art, _, _ = screw_art("set", zx, zy, 2 * MM)
    fork = "".join(f"M{zx} {zy + rc}L{x:.1f} 96" for x in holes)
    dots = "".join(f'<circle class="dot" cx="{x:.1f}" cy="96" r="{3.6 * k:.2f}" style="stroke-width:{.9 * k:.2f}"/>' for x in holes)
    zoom = (f'<path class="lead" d="{fork}" style="stroke-width:{.6 * k:.2f};stroke-dasharray:{1.6 * k:.2f} {1.6 * k:.2f}"/>{dots}'
            f'<circle cx="{zx}" cy="{zy}" r="{rc}" fill="#161616" stroke="#3a3a3a" stroke-width="1"/>{art}'
            f'<text x="{zx - rc - 4}" y="{zy + rc * .85:.1f}" data-pt="4.6" font-family="Poppins" fill="#6a6a6a" text-anchor="end">2:1</text>'
            f'<text x="{zx + rc + 8}" y="{zy + 6}" class="cap" style="text-anchor:start">2x</text>'
            f'<text x="{zx + rc + 42}" y="{zy - 3}" data-pt="5" font-family="Poppins" fill="#A8A8A8">M4 × 5 mm<tspan x="{zx + rc + 42}" dy="1.2em">hex set screw</tspan></text>')
    vb3 = view(0, 128)  # taller: room for the zoom circle
    s3 = f'<svg {vb3}>{blade_in}{hilt}{zoom}</svg>'
    # 4: blade in, the power button ringed
    bx, br = dx + BUTTON_Y, BUTTON_R + 6
    ring = (f'<circle cx="{bx:.1f}" cy="96" r="{br:.1f}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="7"/>'
            f'<circle cx="{bx:.1f}" cy="96" r="{br:.1f}" fill="none" stroke="{GREEN}" stroke-width="4"/>')
    s4 = f'<svg {vb}>{blade_in}{hilt}{ring}</svg>'
    steps = [(f"Charge to full (page {P['charging']}). The first charge takes a few hours", s1),
             ("Push the blade all the way into the emitter", s2),
             ("Tighten the two 5 mm screws with the hex key until snug", s3),
             ("Click Power to ignite. Hold Power to turn off. Long Click to try the other presets", s4)]
    body = "".join(f'<div class="step">{num(i)}<div><p>{sent(t)}</p>{d}</div></div>' for i, (t, d) in enumerate(steps, 1))
    return f"""<div class="page qstart nosep"><h1>Quick start</h1>{body}<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_edit(pn):
    rows = [("Turn right", "Next item, increase, Yes"), ("Turn left", "Previous item, decrease, No"),
            ("Hold + Turn right / left", "Jump by 5 (fonts, tracks, blade length)|500 for timings, 5000 for options"),
            ("Click", "Select, save, enter"), ("Long Click", "Cancel, revert, go back"),
            ("Hold", "Back to the main menu|in the main menu: exit Edit Mode"),
            ("Double Click and Hold, turn", "Color zoom|release to save")]
    return f"""<div class="page"><h1>Edit Mode</h1>
<p>Edit Mode is a spoken menu for changing fonts, colors, blade length, timings and volume on the saber. It needs the menu voice files on the SD card.</p>
{sub("Blade off: Double Click and Hold to enter", "#E44F44")}
{ctl_table(rows)}
<p class="tip">Turn means roll the whole saber on its long axis, blade level (page {P['motion']}).</p>
<p class="tip">Some sabers open a shorter Edit Settings menu instead, with the same controls.{TODO}</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_rehearsal(pn):
    steps = ["Blade off: Triple Click and Hold. The saber ignites in Rehearsal mode. If you saved a rehearsal before, it asks Replace? Turn right and Click to start a new one",
             "Fight your sequence. The saber records each Clash and Hold + Clash (lockup), with its sound",
             "Hold Power to save. Triple Click and Hold cancels",
             "Blade off: Hold Power + Swing to play it back. Clashes and lockups replay in order",
             "Hold Power to end"]
    body = "".join(f'<div class="step">{num(i)}<div><p>{sent(t)}</p></div></div>' for i, t in enumerate(steps, 1))
    return f"""<div class="page steps"><h1>Rehearsal</h1>
<p>Record a fight sequence, then replay it as choreography.</p>{body}
<div class="pn">&lt; {pn} &gt;</div></div>"""


def page_fonts(pn):
    files = [("hum", "The idle hum"), ("swingl, swingh", "SmoothSwing loops"), ("clsh, blst, lock", "Clash, blaster, lockup"),
             ("out, in", "Ignition, retraction"), ("font", "The font's spoken name"), ("config.ini, smoothsw.ini", "Timings, swing feel")]
    rows = "".join(f'<div class="row"><b>{a}</b><span>{b}</span></div>' for a, b in files)
    return f"""<div class="page"><h1>Sound fonts</h1>
<p>Each preset pairs a sound font with a blade style. Fonts, music tracks and quotes live on the microSD card under the Proffieboard, inside the gold core.</p>
{sub("Inside a font folder", GREEN)}
<div class="ref" style="display:block">{rows}</div>
{sub("Changing fonts", "#E44F44")}
<p>Copy a font folder onto the card, then choose it for a preset in Edit Mode (page {P['edit']}). Rename fonts made for other boards first, with the free SoundFontNamingConverter.</p>
<p class="tip">Fonts: Kyberphonic, Greyscale Fonts (some free), KSith, JayDalorian. A purchase covers your own sabers. Sounds are 44.1 kHz, 16-bit mono WAV.</p>
<div class="pn">&lt; {pn} &gt;</div></div>"""


ORDER = [("cover", page_cover), ("contents", page_contents),
         ("p1", page_part(1, "Get Started")), ("safety", page_safety), ("anatomy", page_anatomy), ("structure", page_structure), ("box", page_box),
         ("parts", page_parts), ("quick", page_quickstart), ("charging", page_charging), ("crystal", page_crystal), ("button", page_button),
         ("angle", page_angle), ("off", page_controls), ("color", page_color),
         ("music", page_music), ("motion", page_motion), ("errors", page_errors), ("trouble", page_trouble),
         ("p2", page_part(2, "Technical Specs")), ("specs", page_specs), ("tech", page_tech), ("core", page_core), ("board", page_board), ("pads", page_pads), ("blade", page_blade),
         ("p3", page_part(3, "Customization")), ("works", page_works), ("proffie", page_proffie), ("change", page_change), ("edit", page_edit), ("rehearsal", page_rehearsal),
         ("fonts", page_fonts), ("connect", page_connect), ("backup", page_backup), ("setup", page_setup), ("first", page_first),
         ("config", page_config), ("styles", page_styles), ("hood", page_hood), ("mods", page_mods), ("types", page_types), ("fits", page_fits), ("vs", page_vs), ("links", page_links),
         ("glossary", page_glossary)]
P = {k: i for i, (k, _) in enumerate(ORDER, 1)}  # page numbers, cover = 1


def spreads():
    """Cover on its own (right-hand page), then facing pairs."""
    pages = [page_ghost()] + [f(P[k]) for k, f in ORDER]
    return "\n".join(f'<div class="spread">{a}{b}</div>' for a, b in zip(pages[::2], pages[1::2] + [""]))


ARROW_JS = """<script>
// Every green arrow: same line width and the same closed head on paper; every caption the same text size.
addEventListener("load", () => {
  const mm = 96 / 25.4, W = .132 * mm, HL = .63 * mm, HW = .45 * mm, CAP = 5.6 / 72 * 96;
  const scale = el => { const m = el.getScreenCTM(); return Math.hypot(m.a, m.b) };
  document.querySelectorAll(".arrow").forEach(a => {
    const k = scale(a), ks = getComputedStyle(a).vectorEffect == "non-scaling-stroke" ? 1 : k;
    a.style.strokeWidth = W / ks;
    if (!a.dataset.head) return;
    const n = a.getTotalLength(), p = a.getPointAtLength(n), q = a.getPointAtLength(n - 1);
    const ux = (p.x - q.x) / Math.hypot(p.x - q.x, p.y - q.y), uy = (p.y - q.y) / Math.hypot(p.x - q.x, p.y - q.y);
    const l = HL / k, w = HW / k, bx = p.x - ux * l, by = p.y - uy * l;
    const h = document.createElementNS("http://www.w3.org/2000/svg", "path");
    h.setAttribute("d", `M${p.x} ${p.y}L${bx - uy * w} ${by + ux * w}L${bx + uy * w} ${by - ux * w}Z`);
    h.setAttribute("fill", "#44B03D"); h.setAttribute("stroke", "#44B03D");
    h.style.strokeWidth = W / ks; h.setAttribute("stroke-linejoin", "round");
    a.after(h);
  });
  document.querySelectorAll(".cap").forEach(t => t.style.fontSize = CAP / scale(t) + "px");
  document.querySelectorAll("[data-pt]").forEach(t => t.style.fontSize = t.dataset.pt / 72 * 96 / scale(t) + "px");
});
</script>"""


def build():
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Quinlan Vos Manual</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@800&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{symbols()}
{spreads()}
{ARROW_JS}
</body></html>"""
    out = Path(__file__).with_name("manual.html")
    out.write_text(html)
    print(out)


if __name__ == "__main__":
    build()
