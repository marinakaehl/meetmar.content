#!/usr/bin/env python3
"""Chat-Reveal-Reel im MAR-Look: Hook oben, Chat baut sich live auf, Wendung, Schluss-Satz, Schleife.
Aufruf: python3 tools/chatreel.py reels/serie/tag05.json out/tag05.mp4"""
import json, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import reel
from reel import W, H, FPS, font, text_spaced, spaced_len, ease, CARBON, PORC, MUTED, PANEL, LINE

SR = 48000
WARM = (122, 110, 99)

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if cur and d.textlength(t, font=f) > maxw: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    return lines

def bubble(text, who, shown=None, dots=False, scale=1.0):
    """who: 'mar' (links, dunkel) oder 'user' (rechts, Papier)."""
    f = font("Geist-400.ttf", int(42 * scale)); fl = font("IBMPlexMono-500.ttf", 20)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines = wrap(d0, text, f, 700)
    lh = int(53 * scale)
    w = int(max(d0.textlength(l, font=f) for l in lines)) + 76
    w = max(w, 230)
    h = 30 + 30 + lh * len(lines) + 20
    if dots: w, h = 200, 40 + 32 + lh + 26
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if who == "mar":
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=PANEL + (250,), outline=LINE + (255,), width=2)
        fg, lab, lc = PORC, "MAR", MUTED
    else:
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=(252, 250, 245, 255), outline=(214, 208, 199, 255), width=2)
        fg, lab, lc = CARBON, "SIE", WARM
    text_spaced(d, (36, 20), lab, fl, lc + (255,), 6)
    if dots:
        for i in range(3):
            d.ellipse([40 + i * 38, 82, 62 + i * 38, 104], fill=fg + (200,))
        return im
    left = len(text) if shown is None else shown
    y = 56
    for ln in lines:
        part = ln[:max(0, left)]; left -= len(ln) + 1
        d.text((38, y), part, font=f, fill=fg + (255,)); y += lh
    return im

def shadow(im):
    pad = 30; out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0); ImageDraw.Draw(sh).rectangle([pad + 4, pad + 10, pad + im.width + 4, pad + im.height + 10], fill=90)
    out.paste((20, 16, 12, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(14))); out.alpha_composite(im, (pad, pad))
    return out

INK = (168, 105, 100)

def big_text(d, y, line, grey, size=96, mark=None, mark_p=1.0):
    f = font("Geist-300.ttf", size); fg = font("Geist-300.ttf", int(size * 0.62))
    for l in wrap(d, line, f, 940):
        x = (W - d.textlength(l, font=f)) / 2
        if mark and mark in l and mark_p > 0:  # roter Balken hinter dem Markierwort
            i = l.index(mark); x0 = x + d.textlength(l[:i], font=f); w = d.textlength(mark, font=f)
            d.rectangle([x0 - 10, y + size * 0.18, x0 - 10 + (w + 20) * mark_p, y + size * 1.08], fill=INK + (235,))
            d.text((x, y), l[:i], font=f, fill=CARBON + (255,))
            d.text((x0, y), mark, font=f, fill=PORC + (255,) if mark_p > 0.6 else CARBON + (255,))
            d.text((x0 + w, y), l[i + len(mark):], font=f, fill=CARBON + (255,))
        else:
            d.text((x, y), l, font=f, fill=CARBON + (255,))
        y += int(size * 1.08)
    y += 14
    for l in wrap(d, grey, fg, 900):
        d.text(((W - d.textlength(l, font=fg)) / 2, y), l, font=fg, fill=WARM + (255,)); y += int(size * 0.72)
    return y

def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
    work = os.path.splitext(out)[0] + "_work"; os.makedirs(work, exist_ok=True)
    # Zeitplan
    t = cfg.get("start", 0.9); ev = []; sfx = []
    for m in cfg["chat"]:
        if m["who"] == "mar":
            ev.append({**m, "t_dots": t, "t0": t + 0.55, "t1": t + 0.55 + len(m["text"]) * 0.028})
            sfx.append(("pop", t + 0.55)); [sfx.append(("tick", t + 0.6 + k * 0.06)) for k in range(int(len(m["text"]) * 0.028 / 0.06))]
            t = ev[-1]["t1"] + m.get("hold", 1.0)
        else:
            ev.append({**m, "t_dots": None, "t0": t, "t1": t})
            sfx.append(("pop", t)); t += m.get("hold", 1.3)
        if m.get("hit"): sfx.append(("thud", ev[-1]["t1"] + 0.05))
    t_final = t + 0.2
    finals = cfg.get("finals") or [{"text": cfg["final"], "grey": cfg["final_grey"], "hold": cfg.get("final_hold", 3.4)}]
    tf = t_final
    for k, fz in enumerate(finals):
        fz["t0"] = tf; tf += fz.get("hold", 2.2); fz["t1"] = tf
        sfx.append(("whoosh" if k == 0 else "pop", fz["t0"] - (0.25 if k == 0 else 0)))
    t_end = tf
    total = t_end
    print(f"Länge: {total:.1f}s")

    bg = Image.new("RGB", (W, H), PORC)
    ph = Image.open(os.path.join(reel.ROOT, cfg.get("background_image", "design/backgrounds/studio_sonne.png"))).convert("RGB")
    sc = max(W / ph.width, H / ph.height); ph = ph.resize((int(ph.width * sc), int(ph.height * sc)))
    ph = ph.crop(((ph.width - W) // 2, (ph.height - H) // 2, (ph.width - W) // 2 + W, (ph.height - H) // 2 + H))
    bg = Image.blend(ph, Image.new("RGB", (W, H), PORC), 0.72)
    sbar = reel.series_bar(cfg["day"])
    grain = [np.random.default_rng(i).normal(0, 2.4, (H, W, 1)).astype(np.float32) for i in range(3)]

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", f"{work}/video.mp4"],
                           stdin=subprocess.PIPE)
    fl = font("IBMPlexMono-500.ttf", 24)
    for fi in range(int(total * FPS)):
        tt = fi / FPS
        img = bg.copy().convert("RGBA"); d = ImageDraw.Draw(img)
        lab = cfg["label"]; text_spaced(d, ((W - spaced_len(d, lab, fl, 8)) / 2, 260), lab, fl, WARM + (255,), 8)
        fade_chat = 1 - ease((tt - t_final) / 0.35)
        if tt < t_final + 0.4:
            hk = Image.new("RGBA", (W, H), (0, 0, 0, 0)); yh = big_text(ImageDraw.Draw(hk), 320, cfg["hook"], cfg["hook_grey"], 92, cfg.get("hook_mark"), ease((tt - 0.35) / 0.3))
            # Chat: Blasen von unten nach oben stapeln, ältere schieben nach oben
            items = []
            for e in ev:
                if e["t_dots"] is not None and e["t_dots"] <= tt < e["t0"]:
                    items.append((bubble("", e["who"], dots=True), e["who"], e["t_dots"]))
                elif tt >= e["t0"]:
                    shown = None if e["who"] == "user" else int(len(e["text"]) * min(1, (tt - e["t0"]) / max(0.01, e["t1"] - e["t0"])))
                    items.append((bubble(e["text"], e["who"], shown, scale=1.12 if e.get("hit") and tt >= e["t1"] else 1.0), e["who"], e["t0"]))
            area_top, area_bot = yh + 60, 1660
            heights = [im.height + 22 for im, _, _ in items]
            over = max(0, sum(heights) - (area_bot - area_top))
            self_over = getattr(main, "_over", 0.0); self_over += (over - self_over) * 0.25; main._over = self_over
            y = area_top - self_over
            hk_a = max(0.0, 1 - self_over / 160)
            if hk_a < 1: hk.putalpha(hk.getchannel("A").point(lambda v: int(v * hk_a)))
            img.alpha_composite(hk, (0, -int(self_over * 0.6)))
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for (im, who, ts), hh in zip(items, heights):
                p = ease((tt - ts) / 0.22); s = shadow(im)
                if p < 1:
                    s = s.resize((max(1, int(s.width * (0.9 + 0.1 * p))), max(1, int(s.height * (0.9 + 0.1 * p)))))
                    s.putalpha(s.getchannel("A").point(lambda v: int(v * p)))
                x = 60 if who == "mar" else W - 60 - s.width
                if y + s.height > 0: layer.alpha_composite(s, (int(x), int(y + (1 - p) * 30)))
                y += hh
            if fade_chat < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * fade_chat)))
            img.alpha_composite(layer)
        cur = [fz for fz in finals if fz["t0"] <= tt < fz["t1"]] or ([finals[-1]] if tt >= finals[-1]["t1"] else [])
        if tt >= t_final and cur:
            fz = cur[0]; last = fz is finals[-1]
            q = ease((tt - fz["t0"]) / 0.35) * (1 if last else 1 - ease((tt - fz["t1"] + 0.3) / 0.3))
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
            if fz.get("note"):
                fh = font("Caveat-500.ttf", 62); lines = []
                for para in fz["note"].split("\n"):
                    lines += wrap(dl, para, fh, 800) + [""]
                lines = lines[:-1]; lh = 70; ph_ = 90 + lh * len(lines)
                card = reel.paper(880, ph_, rot=-1.5, tape=True, seed=4, color=(252, 249, 242))
                cd = ImageDraw.Draw(card); ox = (card.width - 880) // 2 + 50; oy = (card.height - ph_) // 2 + 45
                k_ = int(sum(len(l) for l in lines) * min(1, (tt - fz["t0"]) / max(0.5, fz.get("write", 3.0))))
                for ln in lines:
                    cd.text((ox, oy), ln[:max(0, k_)], font=fh, fill=(52, 50, 48, 255)); k_ -= len(ln); oy += lh
                L.alpha_composite(card, ((W - card.width) // 2, fz.get("y", 430)))
                y2 = fz.get("y", 430) + card.height - 40
            else:
                y2 = big_text(dl, 640, fz["text"], fz.get("grey", ""), fz.get("size", 100))
            if cfg.get("cta") and last:
                fc = font("IBMPlexMono-500.ttf", 30); cw = spaced_len(dl, cfg["cta"], fc, 5) + 80
                dl.rectangle([(W - cw) / 2, y2 + 80, (W + cw) / 2, y2 + 170], fill=CARBON + (255,))
                text_spaced(dl, ((W - cw) / 2 + 40, y2 + 106), cfg["cta"], fc, PORC + (255,), 5)
            L.putalpha(L.getchannel("A").point(lambda v: int(v * q)))
            img.alpha_composite(L)
        arr = np.asarray(img.convert("RGB"), np.float32)
        k = sbar[..., 3:] / 255; arr = arr * (1 - k) + sbar[..., :3] * k
        arr += grain[int(tt * 4) % 3]
        enc.stdin.write(arr.clip(0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()

    # Ton: leiser Raumton + SFX
    n = int(total * SR); rng = np.random.default_rng(1)
    room = np.convolve(rng.normal(0, 1, n), np.ones(400) / 400, mode="same").astype(np.float32) * 0.02
    mix = room.copy()
    for kind, t0 in sfx:
        s = reel.sfx(kind, rng); s = s / (np.abs(s).max() + 1e-9) * {"pop": 0.32, "tick": 0.10, "thud": 0.5, "whoosh": 0.28}[kind]
        i0 = int(t0 * SR); mix[i0:i0 + len(s)] += s[:max(0, n - i0)]
    with wave.open(f"{work}/mix.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((mix.clip(-1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/video.mp4", "-i", f"{work}/mix.wav", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("fertig:", out)

if __name__ == "__main__":
    main()
