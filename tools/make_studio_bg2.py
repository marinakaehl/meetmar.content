#!/usr/bin/env python3
"""Studio-Hintergrund 'Sonnenlicht auf Kalkputz': hohe Wand, Sprossenfenster links, Sonnenfleck mit Fenstergitter-Schatten,
polierter Boden mit Spiegelung, Vase mit Trockenblumen. Aufruf: python3 tools/make_studio_bg2.py OUT.png"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1400, 2400
rng = np.random.default_rng(5)

def noise(scale, octaves=5):
    acc = np.zeros((H, W), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        n = rng.normal(0, 1, (H // s + 2, W // s + 2)).astype(np.float32)
        acc += np.asarray(Image.fromarray(n).resize((W + s, H + s), Image.BICUBIC))[:H, :W] * amp; tot += amp; amp *= 0.55
    return acc / tot

FLOOR = 1880
# Kalkputz-Wand: warm, wolkig
wall = np.array([206, 194, 178], np.float32) + noise(380)[..., None] * 16 + noise(60, 3)[..., None] * 5
wall += np.array([4, 2, -3], np.float32) * noise(500)[..., None]
img = wall.copy()
# Boden: polierter Beton, heller zur Mitte
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
floor = np.array([170, 164, 156], np.float32) + noise(200)[..., None] * 8
img[FLOOR:] = floor[FLOOR:]
img[FLOOR - 4:FLOOR + 2] -= 18  # Sockelkante

# Fenster links (hell, schwarze Sprossen)
win = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(win)
x0, x1, y0, y1 = -40, 330, 120, FLOOR - 60
d.rectangle([x0, y0, x1, y1], fill=(250, 251, 252, 255))
for gx in np.linspace(x0, x1, 4)[1:-1]: d.rectangle([gx - 7, y0, gx + 7, y1], fill=(34, 34, 34, 255))
for gy in np.linspace(y0, y1, 8)[1:-1]: d.rectangle([x0, gy - 7, x1, gy + 7], fill=(34, 34, 34, 255))
d.rectangle([x0, y0, x1, y1], outline=(30, 30, 30, 255), width=16)
d.rectangle([x1 + 8, y0 - 20, x1 + 60, FLOOR], fill=(214, 208, 199, 255))  # Laibung
wa = np.asarray(win, np.float32); k = wa[..., 3:] / 255
img = img * (1 - k) + wa[..., :3] * k

# Sonnenfleck: projiziertes Fenstergitter, schraeg auf Wand und Boden
sun = Image.new("L", (W, H), 0); ds = ImageDraw.Draw(sun)
def skew(px, py):  # Projektion: nach rechts verschoben, nach unten gezogen
    return (520 + px * 1.15 + py * 0.55, 560 + py * 1.0 - px * 0.18)
cols, rows = 3, 4; cw, rh = 150, 200
for i in range(cols):
    for j in range(rows):
        a = skew(i * cw + 12, j * rh + 12); b = skew((i + 1) * cw - 12, j * rh + 12)
        c = skew((i + 1) * cw - 12, (j + 1) * rh - 12); e = skew(i * cw + 12, (j + 1) * rh - 12)
        ds.polygon([a, b, c, e], fill=255)
for i in range(4):  # Lichtstreifen auf dem Boden
    ds.polygon([(380 + i * 210, FLOOR + 80), (560 + i * 210, FLOOR + 80), (620 + i * 230, FLOOR + 260), (420 + i * 230, FLOOR + 260)], fill=200)
sun = sun.filter(ImageFilter.GaussianBlur(10))
s = np.asarray(sun, np.float32)[..., None] / 255
img = img + s * np.array([62, 46, 22], np.float32) * 1.0

# Spiegelung des Fensters im Boden
refl = np.zeros((H, W), np.float32); refl[FLOOR:FLOOR + 420, 0:330] = 1
refl = np.asarray(Image.fromarray((refl * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30)), np.float32) / 255
img += refl[..., None] * 38

# Vase mit Trockenblumen vor der Wand, rechts unten
obj = Image.new("RGBA", (W, H), (0, 0, 0, 0)); do = ImageDraw.Draw(obj)
vx, vy = 1130, FLOOR
do.ellipse([vx - 85, vy - 230, vx + 85, vy - 20], fill=(52, 44, 38, 255)); do.rectangle([vx - 40, vy - 300, vx + 40, vy - 200], fill=(52, 44, 38, 255))
for _ in range(16):
    ang = rng.uniform(-0.6, 0.6); L = rng.uniform(380, 640)
    ex, ey = vx + np.sin(ang) * L, vy - 300 - np.cos(ang) * L
    do.line([(vx, vy - 290), (ex, ey)], fill=(92, 78, 64, 255), width=5)
    for _k in range(5):
        t = rng.uniform(0.5, 1.0); bx, by = vx + (ex - vx) * t, vy - 290 + (ey - vy + 290) * t
        do.ellipse([bx - 14, by - 10, bx + 14, by + 10], fill=(150, 128, 104, 255))
oa = np.asarray(obj, np.float32); k = oa[..., 3:] / 255
img = img * (1 - k) + oa[..., :3] * k

# Raumlicht: rechts etwas dunkler, oben weich
vign = 1 - 0.22 * (((xx - W * 0.35) / (W * 0.9)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2)
img *= vign[..., None]
out = Image.fromarray(img.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
glow = out.point(lambda v: max(0, v - 215) * 4).filter(ImageFilter.GaussianBlur(50))
arr = np.asarray(out, np.float32) + np.asarray(glow, np.float32) * 0.3 + rng.normal(0, 2.0, (H, W, 1))
Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(sys.argv[1]); print("ok")
