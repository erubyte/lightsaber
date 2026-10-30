"""Line-art Quinlan Vos hilt in the Xenopixel manual style.

Vertical, emitter at top, centre x=100. True proportions: the hilt is 31 cm long (y 44..515, 471 units,
so 1.519 units per mm) and 3.6 cm across at the emitter ring. Every part's position and width is measured
from the straight-on front photo (img/hilt_front.png, 4859 px tall before the length fix, 601 px wide):
y = 44 + photo row * 0.09693, half width = photo px / 2 * 0.0910.
"""
import math

CX = 100
MM = 471 / 310  # drawing units per mm
Y = lambda row: round(44 + row * 471 / 4859, 1)  # photo row to drawing y
HW = lambda px: round(px / 2 * 471 / 5175, 1)  # photo width (px) to half width

W = 2 * HW(510)  # grip width, 46.4 units = 30.5 mm
L, R = CX - W / 2, CX + W / 2
JOINT_Y = Y(2265)  # where the chamber half unscrews from the body half
END_Y = 515  # pommel face

RING, RING_HW = (44, Y(150)), HW(601)  # emitter ring, the widest part (3.6 cm)
BLACK, BLACK_HW = (Y(150), Y(720)), HW(546)  # black shroud between two silver straps
COLLAR = (Y(720), Y(790))
BAND1, BAND1_HW = (Y(790), Y(875)), HW(576)
BUTTON = (Y(875), Y(1120))
BAND2, BAND2_HW = (Y(1120), Y(1245)), HW(591)
CHAMBER, CHAMBER_HW = (Y(1245), JOINT_Y), HW(549)
BUTTON_Y, BUTTON_R = Y(933), HW(200)
SCREW_HOLES = ((CX, Y(175)), (CX, Y(417)))
# crystal window: opening, slots each side of the finger, finger top
WIN = (CX - HW(483), Y(1250), CX + HW(483), Y(2125))
FINGER_HW, FINGER_TOP = HW(283), Y(1797)
NECK, NECK_HW = (JOINT_Y, Y(2525)), HW(495)
NECK_RING, NECK_RING_HW = (Y(2525), Y(2608)), HW(552)
POMMEL_SEAM = round(END_Y - 22 * MM, 1)  # the pommel unscrews here: it is 2.2 cm long, 3.6 cm across at its lip
GROOVES = [Y(r) for r in (2775, 3062, 3345, 3625, 3907, 4195)] + [POMMEL_SEAM]
KNOB_Y, KNOB_R = Y(4200), HW(284)
POMMEL = Y(4742)
POMMEL_R = HW(558)
SLEEVE_SCREW = (CX, Y(2170))  # back of the chamber half, centred, near the joint


BG = "#0E0E0E"
# Fills by material. Line art: every part is filled with the page colour, so whatever is drawn later hides
# the lines behind it. Shaded: colours from the photo (gradients in symbols()).
LINE = dict(metal=BG, band=BG, black=BG, gap=BG, ridge=BG, red=BG, green=BG, gold=BG, win=BG, fin=BG, hole=BG,
            line="", hi="", knob="")
SHADE = dict(metal="url(#g-metal)", band="url(#g-band)", black="url(#g-black)", gap="#050505", ridge="url(#g-ridge)",
             red="url(#g-red)", green="url(#g-green)", gold="#C9A646", win="#141414", fin="url(#g-fin)",
             hole="#151515", line=' stroke="#3a3a3a"', hi=' stroke="#f4f4f4" stroke-opacity=".8"',
             knob=' stroke="#6a6a6a"')


def r(x0, y0, x1, y1, rx=2, f=None):
    fill = f' fill="{f}"' if f else ""
    return f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" height="{y1 - y0:g}" rx="{rx}"{fill}/>'


def sect(y, hw, rx=0, f=None):
    return r(round(CX - hw, 1), y[0], round(CX + hw, 1), y[1], rx, f)


def band(y, hw, P):
    """Raised silver ring: two stacked rims."""
    m = round((y[0] + y[1]) / 2, 1)
    return sect(y, hw, 1.5, P["band"]) + f'<path d="M{CX - hw} {m}H{CX + hw}"{P["line"]}/>'


def blade(y0=0, y1=44):
    h = 25.4 * MM / 2
    return f'<path d="M{CX - h:.1f} {y0}V{y1}M{CX + h:.1f} {y0}V{y1}"/>'


def emitter_half(P=LINE, window=True):
    """Emitter ring, black shroud, collar, button section and crystal chamber. window=False: the sleeve
    turned closed, so the chamber is plain silver."""
    s = [sect(RING, RING_HW, 2, P["band"])]
    # black shroud: five rounded ridges between two silver straps
    (y0, y1), sl, sr = BLACK, CX - BLACK_HW, CX + BLACK_HW
    s.append(r(sl, y0, sr, y1, 0, P["gap"]))
    edges = [y0 + f * (y1 - y0) for f in (0, .2, .4, .6, .8, 1)]
    for a, b in zip(edges, edges[1:]):
        s.append(r(sl + 3.5, round(a + 1.4, 1), sr - 3.5, round(b - 1.4, 1), 4, P["ridge"]))
    s.append(r(sl, y0, sl + 3.5, y1, 0, P["metal"]) + r(sr - 3.5, y0, sr, y1, 0, P["metal"]))  # straps
    s.append("".join(f'<circle cx="{x}" cy="{y}" r="2.2" fill="{P["hole"]}"/>' for x, y in SCREW_HOLES))
    s.append(sect(COLLAR, BLACK_HW, 0, P["metal"]))
    s.append(sect(BUTTON, BLACK_HW, 0, P["metal"]))
    s.append(band(BAND1, BAND1_HW, P))
    s.append(sect(CHAMBER, CHAMBER_HW, 0, P["metal"]))
    s.append(band(BAND2, BAND2_HW, P))
    s.append(f'<circle cx="{CX}" cy="{BUTTON_Y}" r="{BUTTON_R}" fill="{P["red"]}"/>'
             f'<circle cx="{CX}" cy="{BUTTON_Y}" r="{BUTTON_R * .75:.1f}" fill="{P["red"]}"/>')
    if window == "closed":
        s.append(chamber_closed(P))
    elif window:
        s.append(chamber_window(P))
    return "".join(s)


def window_path():
    """The window: one U-shaped cut in the silver sleeve. A rounded opening at the top, then a slot down each
    side of the finger. The finger is part of the sleeve, so the cut goes around its rounded top."""
    x0, y0, x1, y1 = WIN
    f0, f1, ft = CX - FINGER_HW, CX + FINGER_HW, FINGER_TOP
    rt, rs, rf = 6, (f0 - x0) / 2, 4  # top corners, slot bottoms (half round), finger top corners
    return (f"M{x0} {y0 + rt}Q{x0} {y0} {x0 + rt} {y0}H{x1 - rt}Q{x1} {y0} {x1} {y0 + rt}"
            f"V{y1 - rs:.1f}A{rs:.1f} {rs:.1f} 0 0 1 {f1} {y1 - rs:.1f}"
            f"V{ft + rf}Q{f1} {ft} {f1 - rf} {ft}H{f0 + rf}Q{f0} {ft} {f0} {ft + rf}"
            f"V{y1 - rs:.1f}A{rs:.1f} {rs:.1f} 0 0 1 {x0} {y1 - rs:.1f}Z")


def chamber_window(P=LINE):
    """Black 3D-printed chamber seen through the window: chassis cap, notched side rails, two finned stacks
    with gold pins, two crystals tip to tip (the lower one in a brass ring). Drawn back to front and clipped
    to the window, then the window's edge on top."""
    x0, y0, x1, y1 = WIN
    cap = Y(1440)
    s = [f'<path d="{window_path()}" fill="{P["win"]}"/><g clip-path="url(#win-clip)">']
    s.append(r(x0 + 4, y0 + 2, x1 - 4, cap, 3, P["black"]))  # chassis cap
    for a, b in ((x0 + 2, x0 + 5), (x1 - 5, x1 - 2)):  # notched side rails, below the cap
        s.append(r(a, cap + 1, b, y1, 1, P["black"]))
        s.append('<path d="' + "".join(f"M{a} {y:.1f}H{b}" for y in range(round(cap) + 8, round(y1) - 4, 9)) + f'"{P["line"]}/>')
    fins = [Y(1450) + i * (Y(1790) - Y(1450)) / 6 for i in range(7)]
    px, cw = HW(236), HW(133)  # pins, crystal half width
    pin = f' stroke="{P["gold"]}" stroke-width="1.1"' if P is SHADE else ""
    s.append(f'<path d="M{CX - px} {Y(1395)}V{fins[-1]:.1f}M{CX + px} {Y(1395)}V{fins[-1]:.1f}"{pin}/>')
    for y in fins:  # fin plates either side, stopping short of the crystals
        s.append(r(x0 + 6, round(y - 1.2, 1), CX - cw - 1.5, round(y + 1.2, 1), .8, P["fin"])
                 + r(CX + cw + 1.5, round(y - 1.2, 1), x1 - 6, round(y + 1.2, 1), .8, P["fin"]))
    cu, cl = Y(1592), Y(1700)  # crystal centres
    s.append(f'<path d="M{CX - cw} {cu - 4}H{CX + cw}L{CX} {cu + 4.5}Z" fill="{P["green"]}"/>')  # upper, tip down
    s.append(f'<path d="M{CX - cw} {cl + 4}H{CX + cw}L{CX} {cl - 4.5}Z" fill="{P["green"]}"/>')  # lower, tip up
    s.append(r(CX - cw, cl + 4, CX + cw, Y(1775), 1.5, P["gold"]))  # brass ring
    s.append(f'</g><path d="{window_path()}" fill="none"/>')
    return "".join(s)


def chamber_closed(P=LINE):
    """Sleeve turned closed: the window shows the black chamber's ribbed back instead of the crystals."""
    x0, y0, x1, y1 = WIN
    s = [f'<path d="{window_path()}" fill="{P["gap"]}"/><g clip-path="url(#win-clip)">']
    n = 9
    for i in range(n):  # rounded ribs, like the shroud's
        a = y0 + 3 + i * (y1 - y0 - 3) / n
        s.append(r(x0 + 2, round(a + 1.3, 1), x1 - 2, round(a + (y1 - y0 - 3) / n - 1.3, 1), 3.5, P["ridge"]))
    s.append(f'</g><path d="{window_path()}" fill="none"/>')
    return "".join(s)


def emitter_half_back(P=LINE):
    """Back of the emitter half: plain silver sleeve, the two bands, one sleeve screw."""
    s = [sect(RING, RING_HW, 2, P["band"]), sect((BLACK[0], BAND1[0]), BLACK_HW, 0, P["metal"]),
         sect(BUTTON, BLACK_HW, 0, P["metal"]), band(BAND1, BAND1_HW, P),
         sect(CHAMBER, CHAMBER_HW, 0, P["metal"]), band(BAND2, BAND2_HW, P)]
    x, y = SLEEVE_SCREW
    s.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{P["hole"]}"/><path d="M{x - 1.4} {y}H{x + 1.4}"/>')
    return "".join(s)


def body_half(knob=True, P=LINE):
    """Narrow neck, raised ring, grooved grip, Covertec wheel (front only), pommel lip."""
    s = [sect(NECK, NECK_HW, 0, P["metal"]), r(L, NECK_RING[1], R, POMMEL, 0, P["metal"]),
         sect(NECK_RING, NECK_RING_HW, 1, P["band"])]
    s.append('<path d="' + "".join(f"M{L} {y}H{R}" for y in GROOVES) + f'"{P["line"]}/>')  # groove, then its lit edge
    s.append('<path d="' + "".join(f"M{L} {y + 1.6:.1f}H{R}" for y in GROOVES) + f'"{P["hi"] or P["line"]}/>')
    if knob:  # drawn over the grooves
        s.append(f'<circle cx="{CX}" cy="{KNOB_Y}" r="{KNOB_R}" fill="{P["black"]}"/>'
                 f'<circle cx="{CX}" cy="{KNOB_Y}" r="{KNOB_R * .62:.1f}" fill="{P["black"]}"{P["knob"]}/>'
                 f'<circle cx="{CX}" cy="{KNOB_Y}" r="1.8" fill="{P["band"]}"/>')
    s.append(sect((POMMEL, END_Y), POMMEL_R, 2, P["band"]))
    return "".join(s)


def thread_stub():
    """Silver threaded end on the chamber half, visible once unscrewed."""
    h = NECK_HW - 3
    s = [r(CX - h, JOINT_Y, CX + h, JOINT_Y + 12, 1)]
    for x in range(round(CX - h) + 3, round(CX + h), 4):
        s.append(f'<path d="M{x} {JOINT_Y}L{x + 3} {JOINT_Y + 12}"/>')
    return "".join(s)


CORE_D = 25.4 * MM  # 1 in core, 38.6 units
CORE = (round(JOINT_Y + 3, 1), round(JOINT_Y + 3 + 5.6 * CORE_D, 1))  # pins end (toward the joint) .. speaker end


def core():
    """Gold core, pins end at top: ornate end cap with USB-C, long battery window with the
    crystal print, red charging light, speaker grille. Laid out on a 46 x 208 grid, then mapped
    onto the core's true size."""
    y0, y1 = CORE
    sx, sy = CORE_D / 46, (y1 - y0) / 208
    X = lambda x: round(CX + (x - 100) * sx, 1)
    V = lambda v: round(y0 + v * sy, 1)  # v: 0..208 along the core
    rr = lambda a, b, c, d, rx=2: r(X(a), V(b), X(c), V(d), rx)
    cl, cr = 77, 123
    s = ['<path class="pins" d="' + "".join(f"M{X(x)} {V(-6)}V{V(0)}" for x in range(82, 120, 5)) + '"/>']
    s.append(rr(cl, 0, cr, 208, 3).replace("<rect", '<rect class="cf"', 1))  # gold body fill
    cap = 31
    s.append(f'<path d="M{X(cl)} {V(cap)}H{X(cr)}"/>')
    s.append(rr(92, 10, 108, 16, 3))  # USB-C port
    s.append(f'<path d="M{X(cl + 4)} {V(cap - 6)}L{X(100)} {V(cap - 13)}L{X(cr - 4)} {V(cap - 6)}M{X(100)} {V(cap - 13)}V{V(cap - 3)}"/>')
    w0, w1 = cap + 2, cap + 121
    s.append(rr(cl + 2, w0, cr - 6, w1, 3))  # battery window
    s.append(f'<path d="M{X(cl + 2)} {V(w0 + 12)}H{X(cr - 6)}M{X(cl + 2)} {V(w1 - 12)}H{X(cr - 6)}"/>')  # battery caps
    m = (w0 + w1) / 2
    s.append(f'<path d="M{X(98)} {V(m - 30)}L{X(106)} {V(m - 20)}V{V(m + 20)}L{X(98)} {V(m + 30)}L{X(90)} {V(m + 20)}V{V(m - 20)}Z'
             f'M{X(98)} {V(m - 30)}V{V(m + 30)}"/>')  # crystal print, long axis along the core
    s.append(rr(cr - 3, w0 + 18, cr - 1, w1 - 18, 1))  # slot on the side
    led = w1 + 8
    s.append(f'<rect x="{X(104)}" y="{V(led)}" width="{X(112) - X(104):.1f}" height="{V(led + 13) - V(led):.1f}" rx="3"/>')  # charging light
    for y in range(led + 18, 208 - 4, 6):
        s.append(rr(82, y, 97, y + 3, 1.2) + rr(101, y, 116, y + 3, 1.2))  # speaker grille
    return "".join(s), (X(108), V(led + 6.5))


def charge_light():
    _, (x, y) = core()
    return f'<circle cx="{x}" cy="{y}" r="2" fill="#E44F44"/>'


def usb_y():
    """y of the USB-C port on the core (its centre in the battery-side drawing, 199 of 1881 px)."""
    y0, y1 = CORE
    return round(y0 + 199 * (y1 - y0) / 1881, 1)


def pommel_end(cx, cy, rad=POMMEL_R, shaded=False):
    """End view of the pommel at true hilt scale: three curved sound slots. shaded: brushed silver face."""
    s = [f'<circle cx="{cx}" cy="{cy}" r="{rad}"' + (' fill="url(#g-face)" stroke="#1a1a1a" stroke-width=".45"/>' if shaded else '/>')]
    if shaded:
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{rad - 2.5}" fill="none" stroke="#f4f4f4" stroke-opacity=".5" stroke-width=".6"/>')
    arc = 0.62 * rad
    for mid in (0, 120, 240):
        (x0, y0), (x1, y1) = [(cx + arc * math.cos(math.radians(a)), cy + arc * math.sin(math.radians(a)))
                              for a in (mid - 38, mid + 38)]
        d = f"M{x0:.1f} {y0:.1f}A{arc:.1f} {arc:.1f} 0 0 1 {x1:.1f} {y1:.1f}"
        if shaded:
            s.append(f'<path d="{d}" fill="none" stroke="#0a0a0a" stroke-width="4" stroke-linecap="round"/>')
        else:
            s.append(f'<path d="{d}" stroke-width="5" stroke-linecap="round"/>'
                     f'<path d="{d}" stroke="#0E0E0E" stroke-width="3.4" stroke-linecap="round"/>')
    return "".join(s)


SH = 'stroke="#1a1a1a" stroke-width=".45" stroke-linejoin="round"'  # shaded drawings: thin dark edges


def grad(id, stops, radial=False):
    t = "radialGradient" if radial else "linearGradient"
    return f'<{t} id="{id}">' + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + f"</{t}>"


def fade_defs():
    """Faded blade ends (see build.fade_end): an eased fade that is fully transparent over the last stretch,
    so the blade softens into the page instead of stopping at an edge. Offsets run from the far end."""
    st = ((0, 0), (.06, 0), (.125, .1), (.19, .32), (.25, .62), (.31, .88), (.36, 1))
    s = ""
    for d, (x2, y2), rect in (("up", (0, 1), 'x="-.5" y="0" width="2" height="1.2"'),
                              ("left", (1, 0), 'x="0" y="-.5" width="1.2" height="2"')):
        stops = "".join(f'<stop offset="{o}" stop-color="#fff" stop-opacity="{a}"/>' for o, a in st)
        s += (f'<linearGradient id="g-fade{d}" x1="0" y1="0" x2="{x2}" y2="{y2}">{stops}</linearGradient>'
              f'<mask id="fade{d}" maskContentUnits="objectBoundingBox"><rect {rect} fill="url(#g-fade{d})"/></mask>')
    return s


# Cylinder shading from the photo: dark rim, bright highlight left of centre, softer one on the right.
GRADIENTS = (
    grad("g-metal", ((0, "#4a4a4a"), (.12, "#9c9c9c"), (.3, "#f0f0f0"), (.45, "#b9b9b9"), (.62, "#8a8a8a"),
                     (.8, "#d6d6d6"), (1, "#5a5a5a")))
    + grad("g-band", ((0, "#5a5a5a"), (.15, "#bdbdbd"), (.32, "#ffffff"), (.5, "#c8c8c8"), (.7, "#9a9a9a"),
                      (.85, "#e4e4e4"), (1, "#6a6a6a")))
    + grad("g-black", ((0, "#050505"), (.3, "#2e2e2e"), (.5, "#141414"), (.8, "#262626"), (1, "#050505")))
    + grad("g-fin", ((0, "#3a3a3a"), (.5, "#7a7a7a"), (1, "#3a3a3a")))
    + grad("g-ridge", ((0, "#0a0a0a"), (.25, "#4c4c4c"), (.45, "#1a1a1a"), (.75, "#3c3c3c"), (1, "#0a0a0a")))
    + '<filter id="glow" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="5"/></filter>'
    + fade_defs()
    + '<linearGradient id="g-purple-h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A2BB8"/>'
      '<stop offset=".3" stop-color="#C48CFF"/><stop offset=".5" stop-color="#FBF4FF"/><stop offset=".7" stop-color="#C48CFF"/>'
      '<stop offset="1" stop-color="#6A2BB8"/></linearGradient>'
    + grad("g-tube", ((0, "#9aa3a6"), (.3, "#ffffff"), (.6, "#e4e8ea"), (1, "#8a9295")))
    + '<linearGradient id="g-tube-h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a9295"/>'
      '<stop offset=".35" stop-color="#ffffff"/><stop offset=".65" stop-color="#e4e8ea"/><stop offset="1" stop-color="#8a9295"/></linearGradient>'
    + '<linearGradient id="g-blade-h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E9E3A"/>'
      '<stop offset=".3" stop-color="#7CF08A"/><stop offset=".5" stop-color="#F4FFF4"/><stop offset=".7" stop-color="#7CF08A"/>'
      '<stop offset="1" stop-color="#2E9E3A"/></linearGradient>'
    + grad("g-face", ((0, "#f2f2f2"), (.55, "#b4b4b4"), (1, "#6e6e6e")), radial=True)
    + grad("g-blade", ((0, "#2E9E3A"), (.25, "#7CF08A"), (.5, "#F4FFF4"), (.75, "#7CF08A"), (1, "#2E9E3A")))
    + grad("g-red", ((0, "#E8584C"), (.6, "#C42A20"), (1, "#7E1410")), radial=True)
    + grad("g-green", ((0, "#B6FFD2"), (.5, "#5FEA98"), (1, "#22B866")), radial=True)
)


def symbols():
    """SVG <defs> block shared by every page."""
    line = {"blade": blade(), "top": emitter_half(), "thread": thread_stub(), "body": body_half(),
            "top-back": emitter_half_back(), "body-back": body_half(knob=False), "top-closed": emitter_half(window=False)}
    shaded = {"top-sh": emitter_half(SHADE), "body-sh": body_half(P=SHADE), "top-closed-sh": emitter_half(SHADE, "closed"),
              "top-back-sh": emitter_half_back(SHADE), "body-back-sh": body_half(False, SHADE)}
    return ('<svg width="0" height="0" style="position:absolute"><defs>' + GRADIENTS + CORE_GOLD
            + f'<clipPath id="win-clip"><path d="{window_path()}"/></clipPath>'
            + "".join(f'<symbol id="{n}" overflow="visible"><g class="ln">{g}</g></symbol>' for n, g in line.items())
            + f'<symbol id="core" overflow="visible"><g class="ln core">{core()[0]}</g>{charge_light()}</symbol>'
            + "".join(f'<symbol id="{n}" overflow="visible"><g {SH}>{g}</g></symbol>' for n, g in shaded.items())
            + mini_symbols() + '</defs></svg>')


# Core, both sides, drawn in the cut-out photos' own pixels (img/core_battery.png 302 x 1881,
# img/core_board.png 315 x 1890), so the page's callouts land on the same parts. End faces up.
CORE_GOLD = (grad("g-gold", ((0, "#6b5214"), (.1, "#b8952f"), (.3, "#f7e7a6"), (.45, "#d9b85a"), (.65, "#a8862a"),
                             (.85, "#e8cf7c"), (1, "#6b5214")))
             + grad("g-batt", ((0, "#0d1626"), (.35, "#2a3a55"), (.6, "#1a2638"), (1, "#0a111d")))
             + grad("g-cap", ((0, "#3a3a3a"), (.35, "#9a9a9a"), (.6, "#6a6a6a"), (1, "#2a2a2a")))
             + grad("g-clamp", ((0, "#6b5214"), (.2, "#a8862a"), (.45, "#e2c672"), (.6, "#d9b85a"), (.85, "#a8862a"), (1, "#6b5214")))
             + grad("g-usb", ((0, "#8d9296"), (.3, "#e4e7ea"), (.6, "#b8bcc0"), (1, "#7d8286")))
             + grad("g-crys", ((0, "#cfe6ff"), (.5, "#5aa2ff"), (1, "#1b4fb8")), radial=True)
             + grad("g-end", ((0, "#2a4a9a"), (.7, "#0f1d44"), (1, "#a8862a")), radial=True))
CS = 'stroke="#3a2c08" stroke-width="1.6" stroke-linejoin="round"'  # outline for the core drawings
ENG = 'fill="none" stroke="#7a5f18" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'  # engraving


def _slots(x0, y0, cols, rows, w, h, gx, gy, fill="#141008"):
    return "".join(f'<rect x="{x0 + c * gx}" y="{y0 + r * gy}" width="{w}" height="{h}" rx="{w / 2}" fill="{fill}"/>'
                   for c in range(cols) for r in range(rows))


def core_battery_side():
    W, H = 302, 1881
    s = [f'<g {CS}>']
    s.append(f'<path d="M4 46V{H - 26}A{W / 2 - 4} 24 0 0 0 {W - 4} {H - 26}V46" fill="url(#g-gold)"/>')  # bottom edge curves like the end face
    # open pins end: rim and blue LED board inside
    s.append(f'<ellipse cx="{W / 2}" cy="46" rx="{W / 2 - 4}" ry="42" fill="#a8862a"/>'
             f'<ellipse cx="{W / 2}" cy="46" rx="{W / 2 - 18}" ry="32" fill="url(#g-end)"/>')
    s.append("".join(f'<rect x="{x}" y="{30 + (x * 7) % 22}" width="6" height="14" rx="2" fill="#bcd6ff" stroke="none"/>'
                     for x in range(70, 236, 16)))
    # upper cap: engraved panels, USB-C port, sunburst emblem, small hole
    s.append(f'<path d="M60 120V330H110M260 110H120V170" {ENG}/>')
    s.append('<rect x="196" y="168" width="90" height="62" rx="16" fill="#0b0b0b"/><rect x="210" y="186" width="62" height="26" rx="10" fill="#2a2a2a" stroke="none"/>')
    s.append('<path d="M160 318A75 75 0 0 1 292 250" fill="none" stroke="#7a5f18" stroke-width="3"/>'
             + "".join(f'<path d="M226 318L{226 + 64 * math.cos(math.radians(a)):.0f} {318 - 64 * math.sin(math.radians(a)):.0f}" stroke="#7a5f18" stroke-width="3" fill="none"/>'
                       for a in (35, 60, 85, 110, 135)))
    s.append('<circle cx="142" cy="282" r="9" fill="#0b0b0b"/>')
    # battery window: battery, crystal print, grey end caps
    s.append('<rect x="104" y="362" width="192" height="1040" rx="14" fill="#0b0b0b"/>')
    s.append('<rect x="116" y="372" width="172" height="1020" rx="10" fill="url(#g-batt)"/>')
    s.append('<rect x="116" y="380" width="172" height="250" rx="10" fill="url(#g-cap)"/><circle cx="166" cy="510" r="10" fill="#1a1a1a"/>'
             '<path d="M116 600H288M116 615H288" stroke="#2a2a2a" stroke-width="3"/>')
    s.append('<rect x="116" y="1180" width="172" height="200" rx="10" fill="url(#g-cap)"/><circle cx="166" cy="1280" r="8" fill="#1a1a1a"/>'
             '<path d="M116 1215H288M116 1230H288" stroke="#2a2a2a" stroke-width="3"/>')
    s.append('<path d="M232 680L262 730V1060L232 1100L196 1060V760Z" fill="url(#g-crys)" stroke="#bcd6ff" stroke-width="2"/>'
             '<path d="M232 680V1100M196 760L232 800L262 730" stroke="#e6f1ff" stroke-width="1.6" fill="none"/>')
    # accent LED strip down the left edge
    s.append('<rect x="14" y="430" width="30" height="860" rx="6" fill="#0b1430"/>')
    s.append("".join(f'<rect x="20" y="{y}" width="18" height="22" rx="5" fill="#5a8cff" stroke="#c8dcff" stroke-width="1.2"/>'
                     for y in range(445, 1280, 82)))
    # lower cap: engraving, charging light slot, hole, speaker vents, dark notch
    s.append(f'<path d="M60 1420V1520H96L120 1560M180 1410V1590" {ENG}/>')
    s.append('<rect x="188" y="1462" width="88" height="70" rx="26" fill="#0b0b0b"/><rect x="200" y="1478" width="64" height="38" rx="16" fill="#3a1010" stroke="none"/>')
    s.append('<circle cx="143" cy="1465" r="9" fill="#0b0b0b"/>')
    s.append(_slots(186, 1650, 5, 2, 12, 60, 20, 72))
    s.append('<path d="M4 1610H66Q80 1612 80 1630V1690Q78 1706 60 1706H4Z" fill="#0b0b0b"/>')
    s.append('<path d="M110 1640L150 1600M130 1820V1720" ' + ENG + '/>')
    s.append('</g>')
    return "".join(s)


def core_board_side():
    W, H = 315, 1890
    s = [f'<g {CS}>']
    s.append(f'<path d="M4 40V{H - 26}A{W / 2 - 4} 24 0 0 0 {W - 4} {H - 26}V40" fill="url(#g-gold)"/>')  # bottom edge curves like the end face
    # speaker end: rim, crescent vents, threaded centre stub
    s.append(f'<ellipse cx="{W / 2}" cy="40" rx="{W / 2 - 4}" ry="36" fill="#c9a646"/>'
             '<path d="M50 34Q70 18 98 20Q84 36 58 50Z M265 34Q245 18 217 20Q231 36 257 50Z" fill="#141008"/>'
             f'<ellipse cx="{W / 2}" cy="34" rx="56" ry="24" fill="#e6cf82"/><ellipse cx="{W / 2}" cy="30" rx="26" ry="12" fill="#8a6d1f"/>')
    # speaker grille, black notch, screws, engraved lines
    s.append(_slots(200, 180, 5, 2, 13, 70, 20, 90))
    s.append('<path d="M4 226H70Q92 228 92 250V318Q90 344 66 344H4Z" fill="#0b0b0b"/>')
    s.append('<circle cx="140" cy="210" r="9" fill="#d9b85a"/><circle cx="168" cy="352" r="9" fill="#d9b85a"/>')
    s.append(f'<path d="M116 180V320L160 368M60 400V520H110M80 760V1000L120 1050" {ENG}/>')
    # glyph panel
    s.append('<rect x="228" y="400" width="56" height="290" rx="10" fill="#d9b85a"/>'
             + "".join(f'<path d="M240 {y}L272 {y + 22}M240 {y + 22}H272" {ENG}/>' for y in range(420, 670, 52)))
    s.append('<ellipse cx="142" cy="578" rx="38" ry="26" fill="#0b0b0b"/>')
    s.append('<circle cx="86" cy="430" r="7" fill="#7a5f18"/><circle cx="86" cy="460" r="7" fill="#7a5f18"/>')
    # dark strip on the left
    s.append('<rect x="22" y="700" width="22" height="720" rx="4" fill="#141414"/>')
    # board window, traced from the board-side photo (same 315 x 1890 grid): battery seen through the upper
    # opening, microSD card sticking out from under the board's USB end, Proffieboard V2.2 with its 2 x 13 pads,
    # the micro-USB socket facing the speaker end, and the slotted gold arm of the chassis that clamps the board
    s.append('<path d="M150 738H293V958H312V1478H124V958H150Z" fill="#0b0b0b"/>')
    s.append('<rect x="226" y="748" width="62" height="204" fill="url(#g-batt)" stroke="none"/>'
             '<rect x="172" y="752" width="56" height="196" rx="3" fill="#c4c8cc" stroke="#6a6e72" stroke-width="1"/>'
             '<text x="207" y="850" transform="rotate(-90 207 850)" text-anchor="middle" font-family="Poppins" font-weight="600" '
             'font-size="15" fill="#2a2a2a" stroke="none">PROTECTED BATTERY</text>')
    s.append('<rect x="124" y="958" width="14" height="520" fill="#d9b85a" stroke="none"/>')  # left rail of the board channel
    # microSD card: black, the exposed end with its finger notch; the rest runs under the board
    s.append('<path d="M150 1010V940Q150 930 160 930H262Q272 930 272 940V1010Z" fill="#232428" stroke="#6a6c70" stroke-width="1.6"/>'
             '<path d="M150 1010V940Q150 930 160 930H262Q272 930 272 940V1010" fill="none" stroke="#dfe2e6" stroke-width="4"/>'  # light rim so the card stands out
             '<path d="M160 946H262" stroke="#3a3c40" stroke-width="2"/>')
    # Proffieboard V2.2: white PCB, gold pads with dark holes down both edges (13 a side, 2.54 mm pitch)
    s.append('<rect x="138" y="1000" width="174" height="466" rx="5" fill="#f2f2ee" stroke="#9a9a96" stroke-width="1.2"/>')
    pads = [(x, round(1040 + i * 33.9, 1)) for x in (153, 299) for i in range(13)]
    s.append("".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#d9b85a" stroke="#8a6d1f" stroke-width="1.2"/>'
                     f'<circle cx="{x}" cy="{y}" r="4" fill="#2a2208" stroke="none"/>' for x, y in pads))
    # small parts: resistors and capacitors near the socket and down the left, one 8-pin chip at the pin end
    s.append("".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="{c}" stroke="none"/>' for x, y, w, h, c in (
        (172, 1066, 10, 16, "#2b2b2b"), (186, 1034, 8, 14, "#9a8a6a"), (178, 1196, 9, 15, "#2b2b2b"), (270, 1112, 10, 16, "#2b2b2b"),
        (176, 1306, 18, 26, "#f2f2ee"), (176, 1340, 18, 26, "#f2f2ee"))))
    s.append('<rect x="176" y="1306" width="18" height="26" rx="3" fill="none" stroke="#3a3a3a" stroke-width="1.6"/>'
             '<rect x="176" y="1340" width="18" height="26" rx="3" fill="none" stroke="#3a3a3a" stroke-width="1.6"/>')
    s.append('<rect x="170" y="1378" width="26" height="54" rx="2" fill="#1a1a1a" stroke="none"/>'
             + "".join(f'<path d="M{x} 1378V1372M{x} 1432V1438" stroke="#b8b8b8" stroke-width="2.4"/>' for x in (175, 183, 191)))
    # STM32L433 processor (7 x 7 mm) and the board name, as printed on the PCB
    s.append('<rect x="190" y="1104" width="74" height="74" rx="3" fill="#161616" stroke="none"/>'
             '<circle cx="200" cy="1114" r="3" fill="#3a3a3a" stroke="none"/>'
             '<text x="174" y="1250" transform="rotate(-90 174 1250)" text-anchor="middle" font-family="Poppins" font-weight="600" '
             'font-size="15" fill="#2a2a2a" stroke="none">ProffieBoard V2.2</text>')
    # micro-USB socket on top of the board: steel shell, its mouth facing the speaker end, two solder legs each side
    s.append('<rect x="196" y="1018" width="6" height="22" fill="#9da2a6" stroke="none"/><rect x="274" y="1018" width="6" height="22" fill="#9da2a6" stroke="none"/>'
             '<rect x="200" y="984" width="76" height="110" rx="6" fill="url(#g-usb)" stroke="#5a5e62" stroke-width="1.6"/>'
             '<path d="M210 986H266L260 1000H216Z" fill="#141414" stroke="none"/>'
             '<path d="M214 1040H262M214 1060H262" stroke="#7a7e82" stroke-width="1.4"/>')
    # gold clamp: an arm of the chassis that rises from the window's lower edge and lies over the board
    s.append('<path d="M206 1196V1474" stroke="#000" stroke-opacity=".35" stroke-width="8"/>'  # its shadow on the board
             '<path d="M186 1479Q200 1479 200 1465V1215Q200 1190 225 1190H265Q290 1190 290 1215V1465Q290 1479 304 1479Z" fill="url(#g-clamp)" stroke="none"/>'
             '<path d="M186 1479Q200 1479 200 1465V1215Q200 1190 225 1190H265Q290 1190 290 1215V1465Q290 1479 304 1479" fill="none"/>')
    s.append(_slots(222, 1212, 1, 5, 56, 20, 0, 50).replace('rx="28.0"', 'rx="10"'))
    s.append('<circle cx="180" cy="1497" r="11" fill="#e6cf82"/><circle cx="180" cy="1497" r="4" fill="#7a5f18" stroke="none"/>')  # screw by the clamp
    # lower section: engraving, arrow, hole, button module
    s.append(f'<path d="M60 1500L110 1560V1700M200 1520H290M200 1550H290" {ENG}/>')
    s.append('<path d="M262 1580L250 1600L238 1580" fill="#7a5f18" stroke="none"/>')
    s.append('<circle cx="128" cy="1725" r="20" fill="#0b0b0b"/><circle cx="96" cy="1640" r="5" fill="#7a5f18"/>')
    s.append('<rect x="186" y="1640" width="94" height="156" rx="10" fill="#141414"/>'
             '<circle cx="233" cy="1690" r="26" fill="none" stroke="#c9a646" stroke-width="3"/>'
             '<rect x="208" y="1740" width="50" height="40" rx="4" fill="#bfc3c8" stroke="#6a6a6a"/>'
             '<rect x="222" y="1750" width="22" height="20" rx="3" fill="#6a6a6a" stroke="none"/>')
    s.append('</g>')
    return "".join(s)


# Simplified coloured hilt and core for the small diagrams (charging, quick start, motion, angle, colour).
# Same outline and part positions as the full drawings, fewer details, heavier edges so they read small.
MS = 'stroke="#141414" stroke-width="1.3" stroke-linejoin="round"'


def top_mini():
    s = [sect(RING, RING_HW, 2, "url(#g-band)")]
    (y0, y1), hw = BLACK, BLACK_HW
    s.append(sect(BLACK, hw, 0, "url(#g-black)"))
    s.append('<path d="' + "".join(f"M{CX - hw + 4} {y0 + f * (y1 - y0):.1f}H{CX + hw - 4}" for f in (.2, .4, .6, .8))
             + '" stroke="#5a5a5a" stroke-width="1.6"/>')
    s.append(sect((COLLAR[0], BUTTON[1]), hw, 0, "url(#g-metal)"))
    s.append(sect(BAND1, BAND1_HW, 1.5, "url(#g-band)"))
    s.append(sect(CHAMBER, CHAMBER_HW, 0, "url(#g-metal)"))
    s.append(sect(BAND2, BAND2_HW, 1.5, "url(#g-band)"))
    s.append(f'<circle cx="{CX}" cy="{BUTTON_Y}" r="{BUTTON_R}" fill="url(#g-red)"/>')
    s.append(f'<path d="{window_path()}" fill="#141414"/>')
    cw, cu, cl = HW(133), Y(1592), Y(1700)
    s.append(f'<path d="M{CX - cw} {cu - 4}H{CX + cw}L{CX} {cu + 4.5}ZM{CX - cw} {cl + 4}H{CX + cw}L{CX} {cl - 4.5}Z" fill="#5FEA98" stroke="none"/>')
    return "".join(s)


def body_mini(pommel=True):
    """Body half; pommel=False stops at the pommel seam (pommel unscrewed)."""
    end = POMMEL if pommel else POMMEL_SEAM
    s = [sect(NECK, NECK_HW, 0, "url(#g-metal)"), r(L, NECK_RING[1], R, end, 0, "url(#g-metal)"),
         sect(NECK_RING, NECK_RING_HW, 1, "url(#g-band)")]
    s.append('<path d="' + "".join(f"M{L} {y}H{R}" for y in GROOVES if y < end) + '" stroke="#5a5a5a" stroke-width="1.4"/>')
    s.append(f'<circle cx="{CX}" cy="{KNOB_Y}" r="{KNOB_R}" fill="#151515"/>')
    if pommel:
        s.append(pommel_mini())
    else:  # threaded end left on the body
        s.append(r(CX - NECK_HW + 3, end, CX + NECK_HW - 3, end + 8, 1, "url(#g-metal)")
                 + '<path d="' + "".join(f"M{x} {end}L{x + 3} {end + 8}" for x in range(round(CX - NECK_HW) + 5, round(CX + NECK_HW) - 3, 5))
                 + '" stroke="#5a5a5a"/>')
    return "".join(s)


def pommel_mini():
    """The pommel: 2.2 cm of grip ending in the wider lip."""
    return (r(L, POMMEL_SEAM, R, POMMEL, 0, "url(#g-metal)") + f'<path d="M{L} {POMMEL_SEAM}H{R}" stroke="#5a5a5a" stroke-width="1.4"/>'
            + sect((POMMEL, END_Y), POMMEL_R, 2, "url(#g-band)"))


def thread_mini():
    h = NECK_HW - 3
    return (r(CX - h, JOINT_Y, CX + h, JOINT_Y + 12, 1, "url(#g-metal)")
            + '<path d="' + "".join(f"M{x} {JOINT_Y}L{x + 3} {JOINT_Y + 12}" for x in range(round(CX - h) + 3, round(CX + h), 5))
            + '" stroke="#5a5a5a"/>')


def core_mini():
    """Battery side of the core, from the full drawing (core_battery_side, 302 x 1881 px) mapped onto the
    core's true size in the hilt (CORE, CORE_D)."""
    y0, y1 = CORE
    X = lambda x: round(CX + (x - 151) * CORE_D / 302, 1)
    V = lambda v: round(y0 + v * (y1 - y0) / 1881, 1)
    R_ = lambda a, b, c, d, rx, f: r(X(a), V(b), X(c), V(d), rx, f)
    s = ['<path class="pins" d="' + "".join(f"M{X(x)} {V(-30)}V{V(10)}" for x in range(70, 240, 30))
         + '" stroke="#C9A646" stroke-width="1.4"/>']
    s.append(R_(4, 0, 298, 1881, 4, "url(#g-gold)"))
    s.append(R_(196, 168, 286, 230, 2, "#0b0b0b"))  # USB-C port
    s.append(R_(104, 362, 296, 1402, 3, "#0b0b0b") + R_(116, 380, 288, 630, 2, "url(#g-cap)")
             + R_(116, 630, 288, 1180, 0, "url(#g-batt)") + R_(116, 1180, 288, 1380, 2, "url(#g-cap)"))
    s.append(f'<path d="M{X(232)} {V(690)}L{X(262)} {V(740)}V{V(1050)}L{X(232)} {V(1090)}L{X(196)} {V(1050)}V{V(760)}Z" fill="#5aa2ff" stroke="none"/>')
    s.append(R_(14, 430, 44, 1290, 2, "#3a6cff"))  # accent LED strip
    s.append(R_(190, 1466, 274, 1530, 3, "#7a1a14"))  # charging light
    s.append('<path d="' + "".join(f"M{X(x)} {V(1650)}V{V(1790)}" for x in range(192, 280, 22)) + '" stroke="#141008" stroke-width="1.2"/>')
    return "".join(s)


def mini_symbols():
    return "".join(f'<symbol id="{n}" overflow="visible"><g {MS}>{g}</g></symbol>' for n, g in (
        ("top-mini", top_mini()), ("body-mini", body_mini()), ("body-open-mini", body_mini(False)), ("pommel-mini", pommel_mini()), ("thread-mini", thread_mini()), ("core-mini", core_mini())))
