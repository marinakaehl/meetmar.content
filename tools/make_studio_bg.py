#!/usr/bin/env python3
"""Prozeduraler Studio-Hintergrund: Betonwand, hohe Decke, grosses Sprossenfenster, Lichteinfall, Tiefenunschaerfe.
Aufruf: python3 tools/make_studio_bg.py design/backgrounds/studio_beton.png"""
import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw

W, H = 1400, 2400  # groesser als 1080x1920 -> Raum fuer langsame Kamerabewegung
rng = np.random.default_rng(11)

def noise(scale, octaves=5):
    acc = np.zeros((H, W), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        n = rng.normal(0, 1, (H // s + 2, W // s + 2)).astype(np.float32)
        n = np.asarray(Image.fromarray(n).resize((W + s, H + s), Image.BICUBIC))[:H, :W]
        acc += n * amp; tot += amp; amp *= 0.55
    return acc / tot

# Betonwand: warmes Grau mit Wolken, Poren und Schalungsfugen
base = np.array([168, 162, 154], np.float32)
wall = base + noise(260)[..., None] * 14 + noise(30, 3)[..., None] * 6
pores = (rng.random((H, W)) > 0.9975).astype(np.float32)
pores = np.asarray(Image.fromarray((pores * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
wall -= pores[..., None] * 40
for y in range(0, H, 420):  # Schalungsfugen
    wall[y:y + 3] -= 12
for x in range(180, W, 620):
    wall[:, x:x + 3] -= 9
img = Image.fromarray(wall.clip(0, 255).astype(np.uint8))

# Decke + Boden andeuten
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 140], fill=(150, 145, 138))
d.rectangle([0, 2080, W, H], fill=(122, 112, 102))

# grosses Sprossenfenster links, hell, leicht kuehl
win = Image.new("RGB", (W, H), (0, 0, 0)); dw = ImageDraw.Draw(win)
x0, y0, x1, y1 = -60, 260, 620, 2000
dw.rectangle([x0, y0, x1, y1], fill=(246, 246, 242))
for gx in np.linspace(x0, x1, 4)[1:-1]:
    dw.rectangle([gx - 9, y0, gx + 9, y1], fill=(58, 58, 56))
for gy in np.linspace(y0, y1, 6)[1:-1]:
    dw.rectangle([x0, gy - 9, x1, gy + 9], fill=(58, 58, 56))
dw.rectangle([x0, y0, x1, y1], outline=(52, 52, 50), width=22)
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle([x0 - 11, y0 - 11, x1 + 11, y1 + 11], fill=255)
img.paste(win, (0, 0), mask)

# Pflanze als Silhouette rechts unten (Blaetter-Ellipsen)
pl = Image.new("L", (W, H), 0); dp = ImageDraw.Draw(pl)
for _ in range(38):
    cx, cy = rng.normal(1180, 90), rng.normal(1650, 220)
    rx, ry = rng.uniform(40, 90), rng.uniform(14, 30)
    dp.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
dp.rectangle([1150, 1700, 1166, 2100], fill=255)
dp.rectangle([1080, 2040, 1260, 2200], fill=255)
img.paste((66, 74, 58), (0, 0), pl)

# Lichteinfall: warmer Lichtkegel vom Fenster auf die Wand
arr = np.asarray(img, np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
beam = np.exp(-(((xx - 820) / 420) ** 2 + ((yy - 1150) / 900) ** 2))
arr = arr * (0.80 + 0.32 * beam[..., None]) + np.array([16, 10, 2]) * beam[..., None]
vign = 1 - 0.28 * (((xx - W * 0.45) / (W * 0.8)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2)
arr *= vign[..., None]
img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))

# Tiefenunschaerfe + Lichtueberstrahlung am Fenster
img = img.filter(ImageFilter.GaussianBlur(26))
glow = img.point(lambda v: max(0, v - 200) * 3).filter(ImageFilter.GaussianBlur(60))
arr = np.asarray(img, np.float32) + np.asarray(glow, np.float32) * 0.35
arr += rng.normal(0, 2.2, arr.shape[:2])[..., None]
Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(sys.argv[1])
print("ok", sys.argv[1])
