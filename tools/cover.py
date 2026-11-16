#!/usr/bin/env python3
"""Reel-Cover im MAR-Look: Person freigestellt vor Studio-Hintergrund + Titel im Grid-sicheren Bereich.
Aufruf: python3 tools/cover.py VIDEO SEKUNDE VARIANTE(a|b) OUT.png"""
import sys, subprocess, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
import reel
from PIL import Image, ImageDraw

vid, ts, var, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ts), "-i", vid, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     capture_output=True, check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(reel.SRC_H, reel.SRC_W, 3)
a = reel.Matte()(f)
box = reel.framing(a, 1.06, 1215, 0.42, None)
W, H = reel.W, reel.H
fg = np.asarray(Image.fromarray(f).resize((W, H), Image.LANCZOS, box=box), np.float32)
al = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR, box=box), np.float32)[..., None] / 255
M = reel.Moments([], [], [], "design/backgrounds/studio_sonne.png")
bg = M.background(4.0)
if var == "b":  # Wort hinter dem Kopf
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    fb = reel.font("Geist-600.ttf", 250); tw = d.textlength("FRAGE?", font=fb)
    d.text(((W - tw) / 2, 470), "FRAGE?", font=fb, fill=reel.CARBON + (255,))
    la = np.asarray(L, np.float32); k = la[..., 3:] / 255; bg = bg * (1 - k) + la[..., :3] * k
fm = reel.font("IBMPlexMono-500.ttf", 40); _sz = 180
while ImageDraw.Draw(Image.new("L", (1, 1))).textlength("dein Business.", font=reel.font("Geist-300.ttf", _sz)) > 990: _sz -= 4
fl = reel.font("Geist-300.ttf", _sz)
txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
def center_mono(y, s):
    w = reel.spaced_len(d, s, fm, 14); reel.text_spaced(d, ((W - w) / 2, y), s, fm, reel.CARBON + (235,), 14)
def center_big(y, s, col=reel.CARBON):
    d.text(((W - d.textlength(s, font=fl)) / 2, y), s, font=fl, fill=col + (255,))
if var == "a":
    center_mono(250, "CHATGPT BEKOMMT"); center_big(292, "eine Frage.")
    center_mono(530, "MAR BEKOMMT"); center_big(574, "dein Business.")
else:
    center_mono(300, "IST ES WIRKLICH DIE ANTWORT"); center_mono(350, "ODER SCHON DIE")
from PIL import ImageFilter
m = txt.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(40))
haze = Image.new("RGBA", (W, H), reel.PORC + (0,)); haze.putalpha(m.point(lambda v: int(min(255, v * 1.6) * 0.6)))
haze.alpha_composite(txt)
# Schrift HINTER die Person legen
la = np.asarray(haze, np.float32); k = la[..., 3:] / 255; bg = bg * (1 - k) + la[..., :3] * k
img = Image.fromarray((bg * (1 - al) + fg * al).clip(0, 255).astype(np.uint8))
img.save(out); print("ok", out)
