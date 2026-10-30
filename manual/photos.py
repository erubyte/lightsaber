"""Straight-on product photos for the manual from Apple Vision cutouts (see cutout.swift).

Each cutout is upscaled 2x, turned upright, keystone-corrected so the cylinder is even end to end,
trimmed to flat ends (the angled end face is removed), set to its real length/width ratio, given a
crisp alpha edge and sharpened. Run: python3 photos.py <dir with cut_*.png>
"""
import math
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

IMG = "img"


def upright(im, turn=0):
    """Rotate so the long axis is vertical (principal axis of the alpha), then turn by 0/180."""
    sm = im.getchannel("A").resize((im.width // 8, im.height // 8)); w, h = sm.size; px = sm.load()
    pts = [(x, y) for y in range(h) for x in range(w) if px[x, y] > 128]
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts); syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    ang = 0.5 * math.degrees(math.atan2(2 * sxy, sxx - syy))
    r = im.rotate(ang + 90 + turn, expand=True, resample=Image.BICUBIC)
    return r.crop(r.getbbox())


def edges(im):
    a = im.getchannel("A"); w, h = im.size; px = a.load()
    rows = []
    for y in range(h):
        xs = [x for x in range(w) if px[x, y] > 128]
        rows.append((xs[0], xs[-1]) if xs else None)
    return rows


def line(pts):
    n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    b = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
    return lambda x: my + b * (x - mx)


def flatten(im, face, ratio, margin=.2, keep=False):
    """Keystone to an even width, trim the end rims (whole face on the visible end), set length/width."""
    h = im.height; rows = edges(im)
    # fit edges on the narrowest 60% of rows in the middle, so rings and bands don't skew the fit
    mid = [(y, r) for y, r in enumerate(rows) if r and h * .15 <= y <= h * .85]
    mid.sort(key=lambda t: t[1][1] - t[1][0]); mid = mid[: int(len(mid) * .6)]
    left = line([(y, r[0]) for y, r in mid]); right = line([(y, r[1]) for y, r in mid])
    W = right(h / 2) - left(h / 2)
    def side(y, k):  # source x of the output's left (k=-1) or right (k=+1) edge, margin included
        c = (left(y) + right(y)) / 2; half = (right(y) - left(y)) / 2
        return c + k * half * (1 + 2 * margin)
    out_w = round(W * (1 + 2 * margin))
    quad = (side(0, -1), 0, side(h, -1), h, side(h, 1), h, side(0, 1), 0)
    flat = im.transform((out_w, h), Image.QUAD, quad, Image.BICUBIC)
    # rim depth: rows from each end until the body reaches 97% of its width
    rows = edges(flat); full = W * .97
    top = next(y for y, r in enumerate(rows) if r and r[1] - r[0] >= full)
    bot = next(y for y, r in enumerate(reversed(rows)) if r and r[1] - r[0] >= full)
    t0, t1 = 2 * top if face == "top" else top, h - (2 * bot if face == "bottom" else bot)
    if keep:  # keep the end faces; scale so the body between the rims still has the real length/width
        return flat.resize((out_w, round(h * W * ratio / (t1 - t0))), Image.LANCZOS)
    return flat.crop((0, t0, out_w, t1)).resize((out_w, round(W * ratio)), Image.LANCZOS)


def width_at(im, f, rows=None):
    """Median silhouette width over a 4% window around fraction f of the length."""
    rows = rows or edges(im); h = im.height
    ws = sorted(r[1] - r[0] for r in rows[int(h * (f - .02)): int(h * (f + .02))] if r)
    return ws[len(ws) // 2]


def match_front(back, front, at=(.12, .5, .85), margin=.2):
    """Keystone the back view so its widths match the straight front view at two sections
    (chamber and grip), then trim the end rims and set the front's length/width."""
    h = back.height; rb = edges(back); rf = edges(front)
    # scale (back px per front px) through three sections, as a quadratic along the length
    (f0, f1, f2) = at
    (s0, s1, s2) = (width_at(back, f, rb) / width_at(front, f, rf) for f in at)
    def s(y):
        t = y / h
        return (s0 * (t - f1) * (t - f2) / ((f0 - f1) * (f0 - f2)) + s1 * (t - f0) * (t - f2) / ((f1 - f0) * (f1 - f2))
                + s2 * (t - f0) * (t - f1) / ((f2 - f0) * (f2 - f1)))
    def c(y):  # silhouette center, median over a 6% window so bands and the screw don't pull it
        lo, hi = max(0, int(y - h * .03)), min(h, int(y + h * .03))
        cs = sorted((r[0] + r[1]) / 2 for r in rb[lo:hi] if r)
        return cs[len(cs) // 2] if cs else back.width / 2
    out_w = round(front.width * (1 + 2 * margin))
    half = out_w / 2
    step = 24  # strip height in px; each strip gets its own quad
    mesh = []
    for y0 in range(0, h, step):
        y1 = min(h, y0 + step)
        quad = (c(y0) - half * s(y0), y0, c(y1) - half * s(y1), y1, c(y1) + half * s(y1), y1, c(y0) + half * s(y0), y0)
        mesh.append(((0, y0, out_w, y1), quad))
    flat = back.transform((out_w, h), Image.MESH, mesh, Image.BICUBIC)
    rows = edges(flat); full = width_at(front, .7, rf) * .97
    top = next(y for y, r in enumerate(rows) if r and r[1] - r[0] >= full)
    bot = next(y for y, r in enumerate(reversed(rows)) if r and r[1] - r[0] >= full)
    flat = flat.crop((0, top, out_w, h - 2 * bot))  # the pommel face shows at the bottom
    return flat.resize((out_w, front.height), Image.LANCZOS)


def mid(im, y):
    """Silhouette center (x) of row y."""
    a = im.getchannel("A").load(); xs = [x for x in range(im.width) if a[x, y] > 128]
    return (xs[0] + xs[-1]) / 2


def cover_wheel(front, out):
    """Covertec wheel (rows 2020-2180) sits on two grip segments around a hidden groove at 2096-2112:
    fill each segment from its own clean rows, and copy the groove at 1952-1968 into place."""
    k = front.height / 2432; Y = lambda v: round(v * k)
    def tile(src0, src1, y0, y1):  # fill y0..y1 with the clean rows src0..src1, every other tile flipped
        block = front.crop((0, Y(src0), front.width, Y(src1))); y, flip = Y(y0), False
        while y < Y(y1):
            b = block.transpose(Image.FLIP_TOP_BOTTOM) if flip else block
            out.paste(b.crop((0, 0, b.width, min(b.height, Y(y1) - y))), (0, y)); y += b.height; flip = not flip
    tile(1972, 2018, 1968, 2096)
    out.paste(front.crop((0, Y(1952), front.width, Y(1968))), (0, Y(2096)))
    tile(2180, 2234, 2112, 2239)


def center_parts(front):
    """Move the Power button and the Covertec wheel onto the hilt's center line. Each part's old spot
    is filled with clean metal from the same columns (a clean sleeve row for the button, mirrored grip
    metal for the wheel), then the part is set back down centered. Nothing else changes."""
    k = front.height / 2432; Y = lambda v: round(v * k)
    plate = front.copy()
    sleeve = front.crop((0, Y(536), front.width, Y(546))).resize((front.width, 1), Image.BOX)
    plate.paste(sleeve.resize((front.width, Y(533) - Y(421)), Image.NEAREST), (0, Y(421)))
    # wheel spot (rows 2030-2180): mirror the clean metal just above and below it, so each join is seamless,
    # and copy the groove at 1952-1968 into the hidden one at 2096-2112
    def flip(y0, y1, h):  # clean rows y0..y1 mirrored and stretched to h rows (the metal grain runs lengthwise)
        return front.crop((0, Y(y0), front.width, Y(y1))).transpose(Image.FLIP_TOP_BOTTOM).resize((front.width, Y(h)), Image.LANCZOS)
    plate.paste(flip(1975, 2030, 66), (0, Y(2030))); plate.paste(flip(2180, 2234, 68), (0, Y(2112)))
    plate.paste(front.crop((0, Y(1952), front.width, Y(1968))), (0, Y(2096)))
    out = front.copy()
    def disc(cx, cy, rx, ry, blur=.8):
        m = Image.new("L", front.size, 0); ImageDraw.Draw(m).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
        return m.filter(ImageFilter.GaussianBlur(blur))
    for cx, cy, rx, ry in ((157.75, 481, 52, 56), (133.5, 2106, 73, 72)):  # outer edges, measured at 2432 px
        cx, cy, rx, ry = cx * k, cy * k, rx * k, ry * k
        dx = round(mid(front, round(cy)) - cx)
        if cy > front.height / 2:  # wheel: whole grip segments, so the only seams are the real grooves
            out.paste(plate.crop((0, Y(2030), front.width, Y(2180))), (0, Y(2030)))
        else:
            out.paste(plate, (0, 0), disc(cx, cy, rx + 3, ry + 3, 1.5))
        moved = Image.new("RGBA", front.size, (0, 0, 0, 0)); moved.paste(front, (dx, 0))
        out.paste(moved, (0, 0), disc(cx + dx, cy, rx, ry))
    out.putalpha(front.getchannel("A"))
    return out


def back_from_front(front, angled_back):
    """Back view from the straight front photo's own pixels. Row bands in front px (2432 tall):
    the shroud, button and window become plain sleeve (a clean sleeve row stretched), the bands,
    ring, neck and grip stay, the Covertec wheel is covered by the grip segment one groove up,
    and the sleeve screw is copied from the angled back photo."""
    k = front.height / 2432  # rows below were measured at 2432 px
    Y = lambda v: round(v * k)
    out = front.copy()
    sleeve = front.crop((0, Y(538), front.width, Y(554))).resize((front.width, 1), Image.BOX)
    for y0, y1 in ((80, 365), (430, 560), (610, 1130)):
        out.paste(sleeve.resize((front.width, Y(y1) - Y(y0)), Image.NEAREST), (0, Y(y0)))
    for y0, y1 in ((365, 430), (560, 610)):  # bands are plain silver: drop the Power button's red reflection
        band = out.crop((0, Y(y0), out.width, Y(y1))); a = band.getchannel("A")
        band = band.convert("L").convert("RGBA"); band.putalpha(a); out.paste(band, (0, Y(y0)))
    cover_wheel(front, out)
    # sleeve screw: darkest small spot near the middle of the angled back's sleeve
    g = angled_back.convert("L"); w, h = g.size; px = g.load(); a = angled_back.getchannel("A").load()
    sx, sy = min(((x, y) for y in range(int(h * .3), int(h * .5)) for x in range(w // 3, 2 * w // 3) if a[x, y] > 250),
                 key=lambda p: px[p])
    r = Y(14)
    patch = angled_back.crop((sx - r, sy - r, sx + r, sy + r)).resize((2 * Y(11), 2 * Y(11)), Image.LANCZOS)
    m = Image.new("L", patch.size, 0); ImageDraw.Draw(m).ellipse((0, 0, patch.width - 1, patch.height - 1), fill=255)
    out.paste(patch, (round(mid(front, Y(1085))) - patch.width // 2, Y(1085) - patch.height // 2), m)
    return out


def smooth(a, k=4, blur=7):
    """Smooth contour: blur the alpha at k x resolution, threshold it steeply (1 px anti-alias), scale back down."""
    big = a.resize((a.width * k, a.height * k), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    big = big.point(lambda v: 0 if v < 120 else 255 if v > 150 else (v - 120) * 255 // 30)
    return big.resize(a.size, Image.LANCZOS)


def straighten(a, k=4):
    """Core only: vertical sides between the rims, an ellipse cap on the end face (depth where the width
    reaches half), and the far end traced from the real outline as a radius around a point inside the body,
    smoothed along the curve so it keeps the photo's own shape without the cutout's wobble."""
    rows = edges(Image.merge("RGBA", (a, a, a, a))); full = [(y, r) for y, r in enumerate(rows) if r]
    wid = lambda r: r[1] - r[0]
    W = sorted(wid(r) for _, r in full)[len(full) // 2]
    body = [(y, r) for y, r in full if wid(r) >= W * .97]
    y0, y1 = body[0][0], body[-1][0]
    x0 = sorted(r[0] for _, r in body)[len(body) // 2] + .75; x1 = sorted(r[1] for _, r in body)[len(body) // 2] + .25
    yt = next(y for y, r in full if wid(r) >= W * .5)
    bt = (y0 - yt) / .866  # ellipse half-depth: width is .866 of full at .5 of the depth
    cx, cy = (x0 + x1) / 2, y1 - 60
    big = a.resize((a.width * k, a.height * k), Image.BICUBIC); px = big.load(); BW, BH = big.size
    thetas = [i * .5 for i in range(361)]  # 0..180 degrees, 0 = right side, 90 = straight down
    rs = []
    for t in thetas:
        dx, dy = math.cos(math.radians(t)), math.sin(math.radians(t)); r = 0.0
        while True:
            X, Y = int((cx + dx * (r + .25)) * k), int((cy + dy * (r + .25)) * k)
            if not (0 <= X < BW and 0 <= Y < BH) or px[X, Y] < 128: break
            r += .25
        rs.append(r)
    s = 4 / .5; R = int(3 * s); w = [math.exp(-(i / s) ** 2 / 2) for i in range(-R, R + 1)]  # gaussian, 4 degrees
    n = len(rs); get = lambda i: rs[-i] if i < 0 else rs[2 * (n - 1) - i] if i >= n else rs[i]
    sm = [sum(w[j] * get(i + j - R) for j in range(len(w))) / sum(w) for i in range(n)]
    half = (x1 - x0) / 2
    for i in range(n):  # ease the two ends onto the straight side lines so the join has no step
        f = max(0.0, 1 - thetas[i] / 15, 1 - (180 - thetas[i]) / 15)
        sm[i] = sm[i] * (1 - f) + half * f
    m = Image.new("L", (a.width * k, a.height * k), 0); d = ImageDraw.Draw(m)
    d.rectangle((x0 * k, y0 * k, x1 * k, cy * k), fill=255)
    d.ellipse((x0 * k, (y0 - bt) * k, x1 * k, (y0 + bt) * k), fill=255)
    d.polygon([((cx + math.cos(math.radians(t)) * r) * k, (cy + math.sin(math.radians(t)) * r) * k)
               for t, r in zip(thetas, sm)], fill=255)
    return m.resize(a.size, Image.LANCZOS)


def finish(im, core=False):
    """Crisp alpha edge, trimmed halo, light sharpening. Core: smoothed and redrawn outline (see straighten).
    Hilt: thresholded alpha with a 1px erosion, as the approved hilt photos were made."""
    if core:
        a = straighten(smooth(im.getchannel("A")))
    else:
        a = im.getchannel("A").point(lambda v: 0 if v < 90 else 255 if v > 170 else (v - 90) * 255 // 80)
        a = a.filter(ImageFilter.MinFilter(3))
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    rgb.putalpha(a)
    return rgb.crop(rgb.getbbox())


def solve3(A, b):
    """Gaussian elimination for a small linear system."""
    n = len(b); M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]; M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [M[i][n] / M[i][i] for i in range(n)]


def fit_arc(pts, tol=1.5):
    """y = a + b*u^2 + c*u^4 through (u, y), refit twice without points more than tol px off."""
    use = pts
    for _ in range(3):
        f = lambda u: [1, u * u, u ** 4]
        A = [[sum(f(u)[i] * f(u)[j] for u, _ in use) for j in range(3)] for i in range(3)]
        b = [sum(f(u)[i] * y for u, y in use) for i in range(3)]
        c = solve3(A, b); arc = lambda u, c=c: c[0] + c[1] * u * u + c[2] * u ** 4
        use = [(u, y) for u, y in pts if abs(arc(u) - y) <= tol] or use
    return arc


def lathe(im, k=4, win=15, corner=1.5, fill=True):
    """Hilt outline as a turned part: one straight axis, each row's half-width median-filtered (straight
    sides, real steps kept), the top and bottom edges replaced by smooth arcs fitted to the real edge,
    corners rounded a little. Returns the image and (axis x, first and last straight-side rows).
    Pixel sizes are for the 2432 px tall photo and scale with the image."""
    a = im.getchannel("A"); w, h = im.size; px = a.load()
    sc = h / 2432; win = round(win * sc) | 1; corner *= sc
    rows = []
    for y in range(h):
        xs = [x for x in range(w) if px[x, y] > 128]
        rows.append((xs[0], xs[-1]) if xs else None)
    ys = [y for y in range(h) if rows[y]]; top, bot = ys[0], ys[-1]
    cs = sorted((rows[y][0] + rows[y][1] + 1) / 2 for y in ys[len(ys) // 10: 9 * len(ys) // 10])
    cx = cs[len(cs) // 2]  # one straight axis
    hw = [(rows[y][1] + 1 - rows[y][0]) / 2 if rows[y] else 0 for y in range(h)]
    med = list(hw)
    for y in range(top, bot + 1):  # median filter: removes jitter, keeps the steps between sections
        win_v = sorted(hw[max(top, y - win // 2): min(bot, y + win // 2) + 1]); med[y] = win_v[len(win_v) // 2]
    # end rows: from the first/last row where the side is vertical, hold that half-width out to the end;
    # the fitted arcs shape the ends
    def settle(rng):
        ref = max(med[y] for y in rng[:round(120 * sc)])
        return next(y for y in rng if med[y] >= ref - 1.5 * sc)
    ys_top = settle(list(range(top, bot))); ys_bot = settle(list(range(bot, top, -1)))
    for y in range(top, ys_top): med[y] = med[ys_top]
    for y in range(ys_bot + 1, bot + 1): med[y] = med[ys_bot]
    # arcs from the real top and bottom edge (sub-pixel), over the inner 85% of each end's width
    def edge(x, ys, down):
        for y in ys:
            if px[x, y] > 128:
                y0 = y - 1 if down else y + 1; v0 = px[x, y0] if 0 <= y0 < h else 0
                return y - (1 if down else -1) * (px[x, y] - 128) / max(1, px[x, y] - v0)
    def arc_for(ref, ys, down):
        H = med[ref]; pts = []
        for x in range(int(cx - .85 * H), int(cx + .85 * H) + 1):
            e = edge(x, ys, down)
            if e is not None: pts.append((x + .5 - cx, e))
        return fit_arc(pts, 1.5 * sc)
    top_arc = arc_for(ys_top, range(top, ys_top + 1), True)
    bot_arc = arc_for(ys_bot, range(bot, ys_bot - 1, -1), False)
    # render at k x: side profile polygon, cut by the two arcs
    side = Image.new("L", (w * k, h * k), 0); d = ImageDraw.Draw(side)
    left = [((cx - med[y]) * k, (y + .5) * k) for y in range(top, bot + 1)]
    right = [((cx + med[y]) * k, (y + .5) * k) for y in range(bot, top - 1, -1)]
    left = [(left[0][0], top * k - 4 * k)] + left + [(left[-1][0], (bot + 5) * k)]
    right = [(right[0][0], (bot + 5) * k)] + right + [(right[-1][0], top * k - 4 * k)]
    d.polygon(left + right, fill=255)
    ends = Image.new("L", side.size, 0); d = ImageDraw.Draw(ends)
    xs = [i / 2 for i in range(-2 * (w // 2 + 4), 2 * (w // 2 + 4) + 1)]
    d.polygon([((cx + u) * k, top_arc(u) * k) for u in xs] + [((cx + u) * k, bot_arc(u) * k) for u in reversed(xs)], fill=255)
    m = Image.composite(side, Image.new("L", side.size, 0), ends)
    # round the corners a little (machined edges), then back to 1x with a 1 px anti-aliased edge
    m = m.filter(ImageFilter.GaussianBlur(corner * k)).point(lambda v: 0 if v < 120 else 255 if v > 136 else (v - 120) * 16)
    m = m.resize((w, h), Image.LANCZOS)
    # colors under the new edge: extend the solid interior outward, so no background fringe shows
    rgb = im.convert("RGB"); solid = a.point(lambda v: 255 if v > 200 else 0).filter(ImageFilter.MinFilter(round(2 * sc) * 2 + 1))  # skip the halo
    pre = Image.composite(rgb, Image.new("RGB", im.size), solid)
    if not fill:  # the image already carries the photo's real pixels outside its cutout mask
        rgb.putalpha(m)
        return rgb, (cx, ys_top, ys_bot)
    # continue the metal straight out from the solid part into the gap up to the new edge: along the
    # column at the two ends, along the row on the sides (the grain runs that way, and the cutout's
    # stair-stepped edge does not get copied)
    out = rgb.copy(); op = out.load(); sp = solid.load(); mp = m.load(); rp = rgb.load()
    for x in range(w):  # ends
        col = [y for y in range(h) if sp[x, y]]
        if not col: continue
        t, b = col[0], col[-1]
        for y in range(top - 2, min(ys_top + round(20 * sc), t)):
            if 0 <= y < h and mp[x, y]: op[x, y] = rp[x, t + 1]
        for y in range(max(ys_bot - round(20 * sc), b + 1), bot + 3):
            if 0 <= y < h and mp[x, y]: op[x, y] = rp[x, b - 1]
    for y in range(max(0, top - 2), min(h, bot + 3)):  # sides
        row = [x for x in range(w) if sp[x, y]]
        if not row: continue
        l, r = row[0], row[-1]
        for x in range(0, l):
            if mp[x, y] and not (y < ys_top + round(20 * sc) or y > ys_bot - round(20 * sc)): op[x, y] = rp[l + 1, y]
        for x in range(r + 1, w):
            if mp[x, y] and not (y < ys_top + round(20 * sc) or y > ys_bot - round(20 * sc)): op[x, y] = rp[r - 1, y]
    rgb = out
    rgb.putalpha(m)
    return rgb, (cx, ys_top, ys_bot)


# Black crystal chamber (the user's model) from the maker's lit angled shot, swapped into the front
# photo's window. Window landmarks in the front photo (px of the 2432-tall image): opening inner edges, finger, ends
WINDOW = dict(x=[32, 86, 225, 272], y=[627, 898, 1065])
BAND = (613, 628)  # the band's lower edge in the front photo: middle, sides
# the same landmarks in the shot after it is turned upright (rotate by axis angle + 90)
# tilt: extra turn (degrees) so the chamber stands straight; the axis fit alone leaves it leaning right
# file: the shot upscaled 4x with Upscayl high-fidelity-4x (black_lit.webp is the original); scale: landmark factor
SHOT = dict(file="src-photos/chamber/black_lit_hf4x.png", scale=4, x=[727, 796, 985, 1056], y=[631, 982, 1210], tilt=1.6)


def pl(v, a, b):
    """Piecewise-linear map of v from control points a to b, extended at the ends."""
    for i in range(len(a) - 1):
        if v <= a[i + 1] or i == len(a) - 2:
            return b[i] + (v - a[i]) * (b[i + 1] - b[i]) / (a[i + 1] - a[i])


def shot_upright(path, tilt=0):
    """Turn the angled shot so the hilt axis is vertical, emitter up."""
    im = Image.open(path).convert("RGB"); g = im.convert("L").resize((im.width // 4, im.height // 4))
    px = g.load(); w, h = g.size; pts = [(x, y) for y in range(h) for x in range(w) if px[x, y] > 150]
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts); syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    ang = 0.5 * math.degrees(math.atan2(2 * sxy, sxx - syy))
    return im.rotate(ang + 90 + tilt, expand=True, resample=Image.BICUBIC)


def shot_warp(shot, ctl, size, k):
    """Map the shot into front coordinates (scaled by k), cell by cell, separably in x and y."""
    W, H = size; mesh = []; step = 8
    fx = [v * k for v in WINDOW["x"]]; fy = [v * k for v in WINDOW["y"]]
    cx = [v * ctl.get("scale", 1) for v in ctl["x"]]; cy = [v * ctl.get("scale", 1) for v in ctl["y"]]
    for y0 in range(0, H, step):
        for x0 in range(0, W, step):
            x1, y1 = min(W, x0 + step), min(H, y0 + step)
            sx0, sx1 = pl(x0, fx, cx), pl(x1, fx, cx); sy0, sy1 = pl(y0, fy, cy), pl(y1, fy, cy)
            mesh.append(((x0, y0, x1, y1), (sx0, sy0, sx0, sy1, sx1, sy1, sx1, sy0)))
    return shot.transform(size, Image.MESH, mesh, Image.BICUBIC)


def window_mask(size, k, ss=4, r_top=48, r_slot=22, r_finger=10, left=8):
    """The front frame's opening: rounded top corners under the band, two slots beside the finger
    with rounded bottoms, the finger's rounded top cut out. The left edge stays `left` px inside the
    frame: the shots see that inner wall from an angle, so the front's own dark rail shows there."""
    W, H = size; m = Image.new("L", (W * ss, H * ss), 0); d = ImageDraw.Draw(m)
    s = lambda v: v * k * ss
    (x0, f0, f1, x1), (y0, ft, yb) = WINDOW["x"], WINDOW["y"]
    d.rounded_rectangle((s(x0 + left), s(BAND[0]), s(x1), s(ft + 40)), radius=s(r_top), fill=255)  # top part
    # the band's lower edge is an arc (higher in the middle): keep everything above it
    cx, half = (x0 + x1) / 2, (x1 - x0) / 2
    arc = [(s(x), s(BAND[0] + (BAND[1] - BAND[0]) * ((x - cx) / half) ** 2)) for x in range(x0 - 5, x1 + 6)]
    d.polygon([(s(x0 - 5), 0)] + arc + [(s(x1 + 5), 0)], fill=0)
    d.rounded_rectangle((s(x0 + left), s(ft), s(f0), s(yb)), radius=s(r_slot), fill=255)  # left slot
    d.rounded_rectangle((s(f1), s(ft), s(x1), s(yb)), radius=s(r_slot), fill=255)  # right slot
    d.rectangle((s(x0 + left), s(ft), s(x1), s(ft + 30)), fill=255)  # slots join the top part square
    d.rounded_rectangle((s(f0), s(ft), s(f1), s(yb + 40)), radius=s(r_finger), fill=0)  # finger
    return m.resize((W, H), Image.LANCZOS)


def lift(im, gamma, detail):
    """Open up the black plastic: brighten the shadows (gamma < 1) and add local contrast, so the fins
    and rails read. Bright parts (the lit crystals, the pins) barely change."""
    lut = [round(255 * (v / 255) ** gamma) for v in range(256)]
    im = im.point(lut * 3)
    return im.filter(ImageFilter.UnsharpMask(radius=6, percent=detail, threshold=1)) if detail else im


def black_chamber(front, gamma=.6, detail=60):
    """Front photo with the lit black chamber in its window, shadows lifted so the detail shows."""
    k = front.height / 2432
    shot = lift(shot_warp(shot_upright(SHOT["file"], SHOT["tilt"]), SHOT, front.size, k), gamma, detail)
    out = front.copy(); out.paste(shot, (0, 0), window_mask(front.size, k)); out.putalpha(front.getchannel("A"))
    return out


def shadow_lift(im, a=.6):
    """Brighten the shadows and lower mids (x + a*x*(1-x)^2): black and white stay put."""
    lut = [round(255 * min(1, x / 255 + a * (x / 255) * (1 - x / 255) ** 2)) for x in range(256)]
    r, g, b, al = im.split()
    return Image.merge("RGBA", (r.point(lut), g.point(lut), b.point(lut), al))


def slope(pts):
    n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    return sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)


def blade_upright(im, y0, y1):
    """Turn the cutout so the tube's centre line (rows y0..y1 of a first rough turn) is exactly vertical,
    end down. Rough turn: principal axis of the alpha."""
    sm = im.getchannel("A").resize((im.width // 8, im.height // 8)); px = sm.load(); w, h = sm.size
    pts = [(x, y) for y in range(h) for x in range(w) if px[x, y] > 128]
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts); syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    ang = 0.5 * math.degrees(math.atan2(2 * sxy, sxx - syy)) + 90
    r = im.rotate(ang, expand=True, resample=Image.BICUBIC); r = r.crop(r.getbbox())
    rows = edges(r)
    k = slope([(y, (rows[y][0] + rows[y][1]) / 2) for y in range(y0, y1, 4) if rows[y]])  # centre drift per row
    fix = -math.degrees(math.atan(k))
    r = im.rotate(ang + fix, expand=True, resample=Image.BICUBIC)
    return r.crop(r.getbbox()), ang + fix


def tube_width(im, y, n=20):
    rows = edges(im); ws = sorted(rows[i][1] - rows[i][0] for i in range(y - n, y + n) if rows[i])
    return ws[len(ws) // 2]


def extend_top(im, rows):
    """Lengthen the tube upward by `rows`: the top full-width band, stretched (the tube is plain)."""
    rr = edges(im); top = next(y for y, r in enumerate(rr) if r and r[1] - r[0] >= tube_width(im, im.height // 3) * .97)
    band = im.crop((0, top, im.width, top + 200))
    out = Image.new("RGBA", (im.width, im.height - top + rows), (0, 0, 0, 0))
    out.paste(band.resize((im.width, rows + 200), Image.LANCZOS), (0, 0))
    out.paste(im.crop((0, top + 200, im.width, im.height)), (0, rows + 200))
    return out


def blade_closed(tip, k=4):
    """Slide the bullet up into the tube. The tube's end rim is an ellipse (fitted to the visible sides of
    its end; the foam hides the middle), its wall is continued down to that rim, and the bullet sits
    behind it, scaled to the tube's width with its full-width row on the tube's."""
    rows = edges(tip); w = tip.width
    fw = lambda y: rows[y][1] - rows[y][0] if rows[y] else 0
    W = sorted(fw(y) for y in range(2400, 2700))[150]
    yt = max(y for y in range(2000, 3100) if fw(y) >= W * .985)  # last full-width row of the tube
    L, R = rows[yt]; cx, a = (L + R + 1) / 2, (R + 1 - L) / 2
    bs = []
    for y in range(yt + 10, yt + 140):
        dx = cx - rows[y][0]
        if dx < a * .97: bs.append((y - yt) / (1 - (dx / a) ** 2) ** .5)
    b = sorted(bs)[len(bs) // 2]
    # tube: the foam shows through the translucent wall from about 220 rows above the end, so continue the
    # wall from the clean rows above: each column's colour there plus the clean band's own grain (mirror-tiled)
    src = yt - 380; g0 = src - 180; fade = 40
    tube = tip.crop((0, 0, w, yt + round(b) + 4)).copy(); tp = tube.load(); sp = tip.load()
    base = [tuple(sum(sp[x, y][c] for y in range(src - 40, src)) / 40 for c in range(3)) for x in range(w)]
    mean = [tuple(sum(sp[x, y][c] for y in range(g0, src)) / (src - g0) for c in range(3)) for x in range(w)]
    # grain only: remove each row's mean residual, so specks in the band don't repeat as lines
    rowm = {gy: [sum(sp[x, gy][c] - mean[x][c] for x in range(int(cx - a * .9), int(cx + a * .9))) / int(a * 1.8)
                 for c in range(3)] for gy in range(g0, src)}
    for x in range(w):
        dx = abs(x + .5 - cx)
        if dx >= a: continue
        yb = yt + b * (1 - (dx / a) ** 2) ** .5
        for y in range(src - fade, min(tube.height, int(yb) + 2)):
            t = abs(y - src) % (2 * (src - g0)); gy = src - 1 - t if t < src - g0 else g0 + t - (src - g0)
            v = tuple(base[x][c] + sp[x, gy][c] - mean[x][c] - rowm[gy][c] for c in range(3))
            f = min(1, (y - src + fade) / fade)  # cross-fade into the fill over `fade` rows
            tp[x, y] = tuple(round(sp[x, y][c] * (1 - f) + v[c] * f) for c in range(3)) + (255,)
    m = Image.new("L", (w * k, tube.height * k), 0); d = ImageDraw.Draw(m)
    d.rectangle((L * k, 0, (R + 1) * k, yt * k), fill=255)
    d.ellipse((L * k, (yt - b) * k, (R + 1) * k, (yt + b) * k), fill=255)
    tube.putalpha(ImageChops.multiply(m.resize(tube.size, Image.LANCZOS), Image.merge("L", (tip.getchannel("A").crop((0, 0, w, tube.height)).point(lambda v: 255 if v > 0 else 0),)) if False else m.resize(tube.size, Image.LANCZOS)))
    rgb_above = tip.crop((0, 0, w, src - fade)).convert("RGB"); tube.paste(rgb_above, (0, 0))  # real tube colours above
    # seam: a fine shadow line just inside the rim
    line = Image.new("L", tube.size, 0); d = ImageDraw.Draw(line)
    d.arc((L, yt - b, R + 1, yt + b), 0, 180, fill=90, width=3)
    tube = Image.composite(Image.new("RGBA", tube.size, (150, 150, 150, 255)), tube, line.filter(ImageFilter.GaussianBlur(1)))
    am = m.resize(tube.size, Image.LANCZOS)
    top = tip.getchannel("A").crop((0, 0, w, src - fade))  # keep the photo's own outline above (frame cut)
    am.paste(ImageChops.darker(am.crop((0, 0, w, src - fade)), top), (0, 0))
    tube.putalpha(am)
    # bullet: rows from its shoulder down, scaled to the tube width
    yb_full = max(range(4700, 5200), key=fw)
    bw = fw(yb_full); kk = W * .985 / bw  # tucks just inside the tube at the seam
    bullet = tip.crop((0, 4700, w, tip.height))
    bullet = bullet.resize((round(w * kk), round(bullet.height * kk)), Image.LANCZOS)
    bcx = (rows[yb_full][0] + rows[yb_full][1] + 1) / 2 * kk
    top = yt - round((yb_full - 4700) * kk)
    out = Image.new("RGBA", (w, top + bullet.height), (0, 0, 0, 0))
    out.alpha_composite(bullet, (round(cx - bcx), top))
    out.alpha_composite(tube, (0, 0))
    return out


def blade_place(im, end_y, d_ref, angle, D=300, L=5.0, canvas=(900, 1150), end_at=(150, 1050)):
    """Scale to tube diameter D at d_ref, turn to `angle`, put the end's centre at end_at, crop to canvas.
    The tube runs out of the canvas, L diameters along the axis above the end."""
    k = D / tube_width(im, d_ref)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    rows = edges(im); ey = round(end_y * k)
    ex = (rows[ey - 5][0] + rows[ey - 5][1]) / 2 if rows[ey - 5] else im.width / 2
    big = Image.new("RGBA", (im.width + 4000, im.height + 4000), (0, 0, 0, 0)); big.paste(im, (2000, 2000))
    cx, cy = 2000 + ex, 2000 + ey
    r = big.rotate(angle, center=(cx, cy), resample=Image.BICUBIC)
    return r.crop((round(cx - end_at[0]), round(cy - end_at[1]), round(cx - end_at[0]) + canvas[0], round(cy - end_at[1]) + canvas[1]))

def build_blades(src):
    """Blade close-ups at one angle (40 deg from vertical, end down-left), tube diameter 360 px above the end
    and 4.2 diameters of length. Sources: the maker's dark-background shots in src-photos/blade."""
    import math
    D, L, A = 360, 4.2, 40
    s, c = math.sin(math.radians(A)), math.cos(math.radians(A))
    ex, ey = round(D / 2 * c + 20), round(L * D * c)
    canvas = (round(ex + L * D * s + D / 2 / c + 20), round(ey + D / 2 * s + D * .15))
    tip = blade_upright(Image.open(f"{src}/cut_blade_tip.png").convert("RGBA"), 700, 2600)[0]
    con = blade_upright(Image.open(f"{src}/cut_blade_contact.png").convert("RGBA"), 500, 2100)[0]
    film = blade_upright(Image.open(f"{src}/cut_blade_film.png").convert("RGBA"), 700, 3000)[0]  # tip off, clear film showing
    for name, im, dref in (("blade_tip", tip, 2600), ("blade_tip_closed", blade_closed(tip), 2600), ("blade_contact", con, 2100),
                           ("blade_tip_film", film, 2900)):
        e = extend_top(im, round(2.5 * tube_width(im, dref)))
        out = blade_place(e, e.height - 1, dref + e.height - im.height, -A, D, L, canvas, (ex, ey))
        out.crop((0, 0) + canvas).save(f"{IMG}/{name}.png")


def true_length(im, mm=(36, 310)):
    """Stretch the length so widest part : length is 3.6 : 31 cm, the hilt's real size (the store
    photo is about 6% short, from the camera looking slightly down its length)."""
    return im.resize((im.width, round(im.width * mm[1] / mm[0])), Image.LANCZOS)


def build(src):
    up = lambda n, turn=0: upright(Image.open(f"{src}/cut_{n}.png").convert("RGBA").resize(
        (lambda i: (i.width * 2, i.height * 2))(Image.open(f"{src}/cut_{n}.png")), Image.LANCZOS), turn)
    # front: the store shot QV_1 (hilt crop) upscaled 4x with Upscayl high-fidelity-4x, then cut out;
    # cut_qv1hf_full keeps the photo's real pixels outside the mask, so the smoothed edge shows real metal
    front = finish(upright(Image.open(f"{src}/cut_qv1hf_full.png").convert("RGBA"), 180))
    true_length(shadow_lift(black_chamber(lathe(center_parts(front), fill=False)[0]))).save(f"{IMG}/hilt_front.png")
    true_length(shadow_lift(lathe(finish(back_from_front(front, match_front(up("vos7"), front))), fill=False)[0])).save(f"{IMG}/hilt_back.png")
    finish(flatten(up("9798", 180), "top", 5.6, keep=True), core=True).save(f"{IMG}/core_battery.png")
    finish(flatten(up("9796", 180), "top", 5.6, keep=True), core=True).save(f"{IMG}/core_board.png")
    build_blades(src)
    for n in ("hilt_front", "hilt_back", "core_battery", "core_board", "blade_tip", "blade_tip_closed", "blade_contact", "blade_tip_film"):
        print(n, Image.open(f"{IMG}/{n}.png").size)


if __name__ == "__main__":
    build(sys.argv[1])
