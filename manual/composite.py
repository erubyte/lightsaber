"""Full saber composites (unlit and lit) from the hilt cutout and a real tube shading profile."""
import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter

IMG = "/Users/nora/dev/lightsaber/manual/img"
PX = 8.8  # px per mm
BLADE_MM, D_MM, TIP_MM = 785, 25.4, 32  # visible blade, diameter, bullet tip length


def tube_profile():
    """One row across the straight tube in the contact-end photo, rotated upright."""
    im = Image.open(f"{IMG}/blade_contact.png").convert("RGBA")
    sm = im.getchannel("A").resize((im.width // 8, im.height // 8)); w, h = sm.size; px = sm.load()
    pts = [(x, y) for y in range(h) for x in range(w) if px[x, y] > 128]
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts); syy = sum((p[1] - my) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    ang = 0.5 * math.degrees(math.atan2(2 * sxy, sxx - syy))
    r = im.rotate(ang + 90, expand=True, resample=Image.BICUBIC); r = r.crop(r.getbbox())
    row = r.crop((0, int(r.height * .3), r.width, int(r.height * .3) + 40)).resize((r.width, 1), Image.BOX)
    row = row.crop(row.getbbox())
    a = row.getchannel("A")
    row = row.convert("RGB").point(lambda v: min(255, int(255 * (v / 255) ** .8)))  # lift toward white
    row.putalpha(a)
    return row


def blade_shape(bw, blade_h, tip_h):
    """Alpha mask: bullet tip (half-ellipse) on a straight tube, apex at y=0."""
    m = Image.new("L", (bw, blade_h), 0); d = ImageDraw.Draw(m)
    d.ellipse((0, 0, bw - 1, 2 * tip_h), fill=255); d.rectangle((0, tip_h, bw - 1, blade_h), fill=255)
    return m


def unlit(profile, bw, blade_h, tip_h):
    rows = Image.new("RGBA", (bw, blade_h))
    tube = profile.resize((bw, 1), Image.LANCZOS).resize((bw, blade_h), Image.NEAREST)
    rows.paste(tube, (0, 0))
    for y in range(tip_h):  # bullet tip: the same shading squeezed into each narrower row
        t = 1 - y / tip_h
        w = max(2, int(bw * math.sqrt(1 - t * t)))
        rows.paste(profile.resize((w, 1), Image.LANCZOS), ((bw - w) // 2, y))
    seam = ImageDraw.Draw(rows); seam.line((0, tip_h, bw, tip_h), fill=(170, 175, 175, 255), width=2)
    rows.putalpha(ImageChops.multiply(rows.getchannel("A"), blade_shape(bw, blade_h, tip_h)))
    return rows


def lit(bw, blade_h, tip_h, pad, color=(60, 255, 90)):
    W, H = bw + 2 * pad, blade_h + 2 * pad
    mask = Image.new("L", (W, H), 0); mask.paste(blade_shape(bw, blade_h, tip_h), (pad, pad))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for rad, a in ((pad * .3, .45), (pad * .12, .7)):  # wide halo, inner glow, edge
        g = mask.filter(ImageFilter.GaussianBlur(rad)).point(lambda v, a=a: int(min(255, v * a * 1.6)))
        out.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), c) for c in color] + [g]))
    edge = mask.filter(ImageFilter.GaussianBlur(bw * .06))
    out.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), c) for c in (150, 255, 165)] + [edge]))
    core = mask.filter(ImageFilter.MinFilter(int(bw * .16) | 1)).filter(ImageFilter.GaussianBlur(bw * .1))
    out.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), c) for c in (246, 255, 247)] + [core]))
    return out


def build():
    hilt = Image.open(f"{IMG}/hilt_front.png").convert("RGBA")
    hilt = hilt.resize((round(hilt.width * 310 * PX / hilt.height), round(310 * PX)), Image.LANCZOS)
    bw, blade_h, tip_h = round(D_MM * PX), round(BLADE_MM * PX), round(TIP_MM * PX)
    pad = bw * 3
    W = max(hilt.width, bw) + 2 * pad
    H = pad + blade_h + hilt.height
    cx = W // 2
    sink = round(4 * PX)  # blade bottom hides under the emitter ring
    for name, blade, off in (("saber_unlit", unlit(tube_profile(), bw, blade_h, tip_h), (cx - bw // 2, pad)),
                             ("saber_lit", lit(bw, blade_h, tip_h, pad), (cx - bw // 2 - pad, 0))):
        c = Image.new("RGBA", (W, H + sink), (0, 0, 0, 0))
        c.alpha_composite(blade, off)
        c.alpha_composite(hilt, (cx - hilt.width // 2, pad + blade_h - sink))
        if name == "saber_lit":  # green spill on the emitter end
            spill = Image.new("L", c.size, 0)
            ImageDraw.Draw(spill).ellipse((cx - hilt.width, pad + blade_h - sink - 40, cx + hilt.width, pad + blade_h + 60), fill=110)
            spill = ImageChops.multiply(spill.filter(ImageFilter.GaussianBlur(40)), c.getchannel("A"))
            c.alpha_composite(Image.merge("RGBA", [Image.new("L", c.size, v) for v in (60, 255, 90)] + [spill]))
        c = c.crop(c.getbbox())
        c.save(f"{IMG}/{name}.png", optimize=True)
        print(name, c.size)


if __name__ == "__main__":
    build()
