#!/usr/bin/env python3
"""MAR Reel-Schnitt: EDL (edl.json) -> fertiges 1080x1920 Reel.

Schritte: Sprechpausen per Energie-VAD rausschneiden, Jump-Cut-Zooms,
Hintergrund freistellen (MODNet) -> "Warmes Studio", Hook-Headline hinter dem Kopf,
animierte Brand-Karten, Wort-fuer-Wort-Untertitel (ASS), Soundeffekte, Lautheit -14 LUFS.

Aufruf:  python3 tools/reel.py reels/reel01/edl.json out/reel01.mp4 [--preview SECONDS]
"""
import json, math, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "design", "fonts")
W, H, FPS, SR = 1080, 1920, 30, 48000
SRC_W, SRC_H = 720, 1280

# Brand
CARBON = (16, 16, 15); PANEL = (28, 28, 25); LINE = (52, 52, 49)
PORC = (241, 239, 234); MUTED = (167, 164, 159); WARMGREY = (122, 110, 99); LOGO_BLACK = (7, 7, 6)

# Standard-Look: wärmere Haut, etwas mehr Kontrast, leicht nachgeschärft (Quellen sind komprimiert)
GRADE = "eq=contrast=1.03:saturation=1.03"

# iPhone-HDR (HLG/BT.2020) korrekt nach SDR umrechnen, sonst wirkt die Haut blass
HDR_TO_SDR = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
_HDR = {}

def is_hdr(path):
    if path not in _HDR:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                            "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
        _HDR[path] = r.strip(", \n").split(",")[0] in ("arib-std-b67", "smpte2084")
    return _HDR[path]

def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)

# ---------------------------------------------------------------- audio helpers
def load_audio(path, sr):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def rms_db(a, sr, hop=0.01):
    n = int(sr * hop); m = len(a) // n
    f = a[:m * n].reshape(m, n)
    return 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9)

# ---------------------------------------------------------------- planning
def norm_words(words, fix):
    out = []
    for s, e, t, p in words:
        raw = t
        if out and (t.startswith("-") or t.startswith(".0") or (t.isdigit() and out[-1]["text"].lower() == "founding")):
            o = out[-1]; o["text"] += t if t[0] in "-." else " " + t; o["end"] = e; o["raw"] += t; continue
        if out and t in ("%", "%."):
            o = out[-1]; o["text"] += " " + t; o["end"] = e; o["raw"] += t; continue
        out.append({"start": s, "end": e, "text": fix.get(t, t), "raw": raw})
    for o in out:
        o["text"] = fix.get(o["text"], o["text"])
    return out

def plan(edl):
    srcs = {k: os.path.join(ROOT, v) for k, v in edl["sources"].items()}
    trans = {k: json.load(open(os.path.join(ROOT, v))) for k, v in edl["transcripts"].items()}
    vad = {}
    for k, p in srcs.items():
        a = load_audio(p, 16000); db = rms_db(a, 16000)
        floor, speech = np.percentile(db, 10), np.percentile(db, 90)
        thr = max(floor + 12, speech - 19)
        v = db > thr
        # Loecher < 120 ms fuellen (Plosive, kurze Stopps)
        i = 0
        while i < len(v):
            if not v[i]:
                j = i
                while j < len(v) and not v[j]: j += 1
                if 0 < i and j < len(v) and (j - i) < 12: v[i:j] = True
                i = j
            else: i += 1
        for w in trans[k]:  # Wortanfaenge schuetzen (leise Silben)
            v[int(w[0] * 100):int(w[0] * 100) + 10] = True
        vad[k] = v
    clips, words_out, seg_bounds = [], [], []
    t_out = edl.get("intro", {}).get("seconds", 0.0); zoom_cycle = [1.06, 1.14]; zi = 0
    for si, seg in enumerate(edl["segments"]):
        if seg.get("silent"):  # stiller Blick: ein Clip, langsamer Zoom
            n = round((seg["to"] - seg["from"]) * FPS)
            clips.append({"src": seg["src"], "in": seg["from"], "out": seg["from"] + n / FPS, "frames": n, "t0": t_out,
                          "zoom": 1.08, "zoom_to": 1.20, "seg": si})
            seg_bounds.append((t_out, t_out + n / FPS)); t_out += n / FPS; continue
        allw = norm_words(trans[seg["src"]], seg.get("fix", {}))
        ws = [w for w in allw if seg["from"] <= w["start"] < seg["to"]]
        if seg.get("cap_first") and ws: ws[0] = {**ws[0], "text": ws[0]["text"][:1].upper() + ws[0]["text"][1:]}
        before = [w for w in allw if w["start"] < seg["from"]]; after = [w for w in allw if w["start"] >= seg["to"]]
        lo = max(before[-1]["end"] if before else 0, ws[0]["start"] - 0.15)
        hi = min(after[0]["start"] - 0.02 if after else 1e9, ws[-1]["end"] + 0.25)
        v = vad[seg["src"]]
        a0 = max(0, int((ws[0]["start"] - 0.15) * 100)); a1 = min(len(v), int((ws[-1]["end"] + 0.25) * 100))
        # sprachliche Regionen im Segment
        regs, i = [], a0
        while i < a1:
            if v[i]:
                j = i
                while j < a1 and v[j]: j += 1
                regs.append([i / 100, j / 100]); i = j
            else: i += 1
        merged = []
        for r in regs:
            if merged and r[0] - merged[-1][1] < edl.get("keep_pause", 0.16): merged[-1][1] = r[1]
            else: merged.append(r)
        merged = [r for r in merged if r[1] - r[0] > 0.12 or any(r[0] - .05 <= w["start"] < r[1] for w in ws)]
        if not merged: merged = [[ws[0]["start"], ws[-1]["end"]]]
        merged[0][0] = min(merged[0][0], ws[0]["start"])
        seg_start = t_out
        if seg.get("tight_start") and merged: merged[0][0] = ws[0]["start"]
        for r in merged:
            cin, cout = max(lo, r[0] - 0.05), min(hi, r[1] + 0.07)
            for c in clips:  # keine doppelt verwendeten Audio-Stellen
                if c["src"] == seg["src"] and c["in"] <= cin < c["out"]: cin = c["out"]
            if cout - cin < 0.1: continue
            n = max(1, round((cout - cin) * FPS)); cout = cin + n / FPS
            # lange Passagen an Wortgrenzen teilen (Zoom-Wechsel ohne Zeitsprung)
            cuts = [cin]
            if not seg.get("hook"):
                starts = [w["start"] for w in ws if cin + 0.9 < w["start"] < cout - 0.9]
                while starts and cout - cuts[-1] > 2.6:
                    cand = [s for s in starts if s - cuts[-1] > 1.2]
                    if not cand: break
                    punct = {w2["start"] for w1, w2 in zip(ws, ws[1:]) if w1["text"][-1:] in ".,?!:"}
                    s = min(cand, key=lambda s: abs(s - cuts[-1] - 1.9) - (0.7 if s in punct else 0))
                    if cout - s < 0.9: break
                    cuts.append(cin + round((s - 0.03 - cin) * FPS) / FPS)
            cuts.append(cout)
            for a_, b_ in zip(cuts, cuts[1:]):
                n = round((b_ - a_) * FPS)
                z = 1.06 if seg.get("hook") else zoom_cycle[zi % 2]
                if not seg.get("hook"): zi += 1
                clips.append({"src": seg["src"], "in": a_, "out": a_ + n / FPS, "frames": n, "t0": t_out, "zoom": z, "seg": si})
                t_out += n / FPS
        # Woerter auf neue Zeitachse
        segclips = [k for k, c in enumerate(clips) if c["seg"] == si]
        for w in ws:
            def dist(k):
                c = clips[k]; return 0 if c["in"] <= w["start"] < c["out"] else min(abs(w["start"] - c["in"]), abs(w["start"] - c["out"]))
            k = min(segclips, key=dist); c = clips[k]
            s = c["t0"] + min(max(0, w["start"] - c["in"]), c["frames"] / FPS - 0.1)
            words_out.append({**w, "t": s, "seg": si, "clip": k})
        # Zoom-Wechsel nur bei Clips >= 0.6 s; kurze Clips uebernehmen den Zoom des naechsten
        sc = [c for c in clips if c["seg"] == si]
        for a_, b_ in zip(sc[::-1][1:], sc[::-1]):
            if a_["frames"] / FPS < 0.6: a_["zoom"] = b_["zoom"]
        if seg.get("punch"):
            for w in words_out:
                if w["seg"] == si and w["text"].startswith(seg["punch"]):
                    k = w["clip"]; clips[k]["zoom"] = 1.22
                    while k > 0 and clips[k - 1]["seg"] == si and clips[k - 1]["frames"] / FPS < 0.6: k -= 1; clips[k]["zoom"] = 1.22
        seg_bounds.append((seg_start, t_out))
    if clips and edl.get("open_zoom"): clips[0]["zoom_from"] = edl["open_zoom"]
    return srcs, clips, words_out, seg_bounds, t_out

def anchor(a, words, segb):
    if a.get("end"): return segb[a["seg"]][1]
    for w in words:  # erst exakte Treffer, dann Wortanfang
        if w["seg"] == a["seg"] and (w["raw"] == a["word"] or w["text"] == a["word"]):
            return w["t"]
    for w in words:
        if w["seg"] == a["seg"] and w["text"].startswith(a["word"]):
            return w["t"]
    raise KeyError(a)

# ---------------------------------------------------------------- graphics
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

def text_spaced(d, xy, s, f, fill, spacing):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing
    return x

def spaced_len(d, s, f, spacing): return sum(d.textlength(c, font=f) + spacing for c in s) - spacing

def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 540) / 820) ** 2 + ((yy - 760) / 1150) ** 2).clip(0, 1) ** 1.3
    c0 = np.array([228, 216, 200], np.float32); c1 = np.array([154, 135, 116], np.float32)
    g = c0 * (1 - d[..., None]) + c1 * d[..., None]
    rng = np.random.default_rng(7); g += rng.normal(0, 3.2, g.shape[:2])[..., None]
    return g.clip(0, 255).astype(np.float32)

def wrap(d, words_cols, f, maxw):
    lines, cur = [], []
    for w, c in words_cols:
        test = " ".join(x for x, _ in cur + [(w, c)])
        if cur and d.textlength(test, font=f) > maxw: lines.append(cur); cur = [(w, c)]
        else: cur.append((w, c))
    if cur: lines.append(cur)
    return lines

def render_headline(items):
    """items: [(text, greywords)] -> RGBA layer"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = font("Geist-400.ttf", 96); y = 170; lh = 104
    for text, grey in items:
        wc = [(w, WARMGREY if w.strip(".,") in grey else CARBON) for w in text.split()]
        for line in wrap(d, wc, f, 900):
            x = 84
            for w, c in line:
                d.text((x, y), w, font=f, fill=c + (255,)); x += d.textlength(w + " ", font=f)
            y += lh
        y += 34
    return img

INK = (168, 105, 100)  # MAR error/rust = Stempelfarbe
GRAPHITE = (58, 56, 54)

def paper(w, h, rot=0.0, tape=True, seed=0, color=(244, 241, 234)):
    """Papierkarte mit Faserstruktur, weichem Schatten und optionalem Klebeband -> RGBA"""
    r = np.random.default_rng(seed)
    base = np.array(color, np.float32) + r.normal(0, 3.5, (h, w, 1)).astype(np.float32)
    fib = np.asarray(Image.fromarray(r.normal(0, 1, (h // 8 + 1, w // 8 + 1)).astype(np.float32)).resize((w, h), Image.BICUBIC))
    base += fib[..., None] * 4
    card = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    pad = 60; out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0); ImageDraw.Draw(sh).rectangle([pad + 6, pad + 14, pad + w + 6, pad + h + 14], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    out.paste((20, 16, 12, 255), (0, 0), sh)
    out.alpha_composite(card, (pad, pad))
    if tape:
        tw, th = int(min(220, w * 0.45)), 46
        tp = Image.new("RGBA", (tw, th), (226, 218, 200, 170)); dt = ImageDraw.Draw(tp)
        for x in range(0, tw, 9):  # gezackte Enden
            dt.polygon([(x, 0), (x + 4, 5), (x + 9, 0)], fill=(0, 0, 0, 0)); dt.polygon([(x, th), (x + 4, th - 5), (x + 9, th)], fill=(0, 0, 0, 0))
        tp = tp.rotate(r.uniform(-6, 6), expand=True, resample=Image.BICUBIC)
        out.alpha_composite(tp, (pad + (w - tp.width) // 2, max(0, pad - tp.height // 2)))
    return out.rotate(rot, expand=True, resample=Image.BICUBIC)

def pencil_line(d, x0, x1, y, prog, seed=1, width=6, color=GRAPHITE):
    r = np.random.default_rng(seed); n = 24
    xs = np.linspace(x0, x0 + (x1 - x0) * prog, n); ys = y + np.cumsum(r.normal(0, 1.4, n)) + np.linspace(0, -6, n)
    d.line(list(zip(xs, ys)), fill=color + (235,), width=width, joint="curve")

def stamp(text, seed=3, size=96):
    f = font("IBMPlexMono-500.ttf", size); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(spaced_len(d0, text, f, 14)); asc, desc = f.getmetrics()
    w, h = tw + 100, asc + desc + 70
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    d.rectangle([8, 8, w - 9, h - 9], outline=255, width=9); d.rectangle([24, 24, w - 25, h - 25], outline=255, width=3)
    text_spaced(d, (50, 33), text, f, 255, 14)
    r = np.random.default_rng(seed); n = np.asarray(m, np.float32) / 255
    rough = np.asarray(Image.fromarray(r.normal(0, 1, (h // 3 + 1, w // 3 + 1)).astype(np.float32)).resize((w, h), Image.BICUBIC))
    n = n * ((rough + r.normal(0, 0.6, (h, w))) > -0.9) * r.uniform(0.75, 1, (h, w))
    im = Image.new("RGBA", (w, h), INK + (0,)); im.putalpha(Image.fromarray((n * 235).astype(np.uint8)))
    return im.rotate(-7, expand=True, resample=Image.BICUBIC)

def render_hook(item, rel):
    """Zentrierter, leichter Hook: Mono-Zeile + grosse Geist-Light-Zeilen, Woerter blenden weich ein."""
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
    fm = font("IBMPlexMono-500.ttf", 34); a0 = 1.0 if item.get("instant") else ease(rel / 0.3)
    _fs = 34
    while item.get("small") and _fs > 20 and spaced_len(d, item["small"], font("IBMPlexMono-500.ttf", _fs), 12) > 940: _fs -= 1
    fm = font("IBMPlexMono-500.ttf", _fs)
    sw = spaced_len(d, item.get("small", ""), fm, 12) if item.get("small") else 0
    y_small = item.get("y", 270)
    if item.get("small"): text_spaced(d, ((W - sw) / 2, y_small - 12 * (1 - a0)), item["small"], fm, CARBON + (int(230 * a0),), 12)
    lines = item["big"]; size = item.get("max_size", 150)
    while size > 80:
        fb = font("Geist-300.ttf", size)
        if max(d.textlength(l, font=fb) for l in lines) <= 900: break
        size -= 6
    y = y_small + 66; k = 0
    for ln in lines:
        x = (W - d.textlength(ln, font=fb)) / 2
        for wd in ln.split(" "):
            p = 1.0 if item.get("instant") else ease((rel - 0.2 - 0.16 * k) / 0.35)
            if p > 0:
                col = (94, 84, 75) if wd.strip(".,?!") in item.get("grey", []) else CARBON
                d.text((x, y + 22 * (1 - p)), wd, font=fb, fill=col + (int(255 * p),))
            x += d.textlength(wd + " ", font=fb); k += 1
        y += int(size * 1.02)
    if item.get("sub"):
        fsub = font("Geist-300.ttf", item.get("sub_size", 62))
        for li, sl in enumerate(item["sub"].split("\n")):
            ws_ = d.textlength(sl, font=fsub)
            d.text(((W - ws_) / 2, y + 8 + li * int(item.get("sub_size", 62) * 1.15)), sl, font=fsub, fill=(94, 84, 75, 255))
    # weicher heller Schleier hinter der Schrift fuer Lesbarkeit
    m = txt.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(38))
    haze = Image.new("RGBA", (W, H), PORC + (0,)); haze.putalpha(m.point(lambda v: int(min(255, v * 1.6) * 0.62)))
    haze.alpha_composite(txt)
    return haze

class Cards:
    def __init__(self, cards, words, segb):
        self.cards = []; self.cache = {}
        for c in cards:
            c = dict(c); c["t_in"] = None
            if c["type"] == "chat":
                for b in c["bubbles"]:
                    b["t"] = anchor(b["at"], words, segb); b["t_done"] = anchor(b["typed_by"], words, segb) - 0.15
                c["t_in"] = c["bubbles"][0]["t"]
            elif c["type"] == "steps":
                for s in c["steps"]: s["t"] = anchor(s["at"], words, segb)
                c["t_in"] = c["steps"][0]["t"]
            elif c["type"] == "prompt":
                A = lambda x: c["t_in"] + x if isinstance(x, (int, float)) else anchor(x, words, segb)
                c["t_in"] = anchor(c["at"], words, segb); c["t_typed"] = A(c["typed_by"])
                if "reply" in c: c["t_reply"] = A(c["reply_at"]); c["t_reply_done"] = A(c["reply_typed_by"])
            elif c["type"] == "checklist":
                c["t_in"] = anchor(c["at"], words, segb)
                for it in c["items"]: it["t"] = anchor(it["at"], words, segb)
                if "move_at" in c: c["t_move"] = anchor(c["move_at"], words, segb)
            elif c["type"] == "label":
                c["t_in"] = anchor(c["at"], words, segb)
                if "strike_at" in c: c["t_strike"] = anchor(c["strike_at"], words, segb)
                if "note_at" in c: c["t_note"] = anchor(c["note_at"], words, segb)
            else:
                c["t_in"] = anchor(c["at"], words, segb)
                if "strike_at" in c: c["t_strike"] = anchor(c["strike_at"], words, segb)
            c["t_out"] = anchor(c["until"], words, segb) if isinstance(c["until"], dict) else c["t_in"] + c["until"]
            if c.get("lead"): c["t_in"] -= c["lead"]
            self.cards.append(c)

    def events(self):
        """Soundeffekt-Zeitpunkte"""
        ev = []
        for c in self.cards:
            if c["type"] == "chat":
                for b in c["bubbles"]:
                    ev.append(("pop", b["t"]))
                    n = len(b["text"]); dur = max(0.3, b["t_done"] - b["t"] - 0.15)
                    for k in range(0, n, 2): ev.append(("tick", b["t"] + 0.12 + dur * k / n))
            elif c["type"] == "steps":
                for s in c["steps"]: ev.append(("pop", s["t"]))
            elif c["type"] == "strike":
                ev += [("pop", c["t_in"]), ("scratch", c["t_strike"])]
            elif c["type"] == "label":
                ev.append(("pop", c["t_in"]))
                if "t_strike" in c: ev.append(("scratch", c["t_strike"]))
                if "t_note" in c: ev.append(("scratch", c["t_note"]))
            elif c["type"] == "stamp":
                ev.append(("thud", c["t_in"] + 0.12))
            elif c["type"] == "prompt":
                ev.append(("pop", c["t_in"]))
                n = len(c["text"]); dur = max(0.4, c["t_typed"] - c["t_in"] - 0.2)
                for k in range(0, n, 2): ev.append(("tick", c["t_in"] + 0.15 + dur * k / n))
                if "t_reply" in c: ev.append(("pop", c["t_reply"]))
            elif c["type"] == "checklist":
                ev.append(("pop", c["t_in"])); ev += [("pop", it["t"]) for it in c["items"]]
            elif c["type"] == "cta":
                ev += [("whoosh", c["t_in"] - 0.15), ("pop", c["t_in"] + 0.05)]
        return ev

    def _bubble(self, label, text, cursor=False):
        key = ("b", label, text, cursor)
        if key in self.cache: return self.cache[key]
        fl = font("IBMPlexMono-500.ttf", 24); ft = font("Geist-400.ttf", 44)
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        lines = []; cur = ""
        for w in text.split(" "):
            t = (cur + " " + w).strip()
            if cur and tmp.textlength(t + "  ", font=ft) > 780: lines.append(cur); cur = w
            else: cur = t
        lines.append(cur)
        h = 34 + 30 + 18 + 56 * len(lines) + 26
        im = Image.new("RGBA", (880, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, 879, h - 1], radius=4, fill=PANEL + (246,), outline=LINE + (255,), width=2)
        text_spaced(d, (40, 30), label, fl, MUTED + (255,), 6)
        y = 30 + 30 + 18
        for ln in lines: d.text((40, y), ln, font=ft, fill=PORC + (255,)); y += 56
        if cursor:
            x = 40 + d.textlength(lines[-1], font=ft) + 6; yc = y - 56
            d.rectangle([x, yc + 8, x + 5, yc + 52], fill=PORC + (255,))
        self.cache[key] = im; return im

    def _box(self, text, size, spacing=10, pad=(34, 22), fill=PORC, fg=CARBON, strike=0.0):
        key = ("x", text, size, round(strike, 2))
        if key in self.cache: return self.cache[key]
        f = font("IBMPlexMono-500.ttf", size); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        tw = spaced_len(d0, text, f, spacing); asc, desc = f.getmetrics()
        w, h = int(tw + 2 * pad[0]), int(asc + desc + 2 * pad[1])
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w - 1, h - 1], fill=fill + (255,))
        text_spaced(d, (pad[0], pad[1]), text, f, fg + (255,), spacing)
        if strike > 0:
            yy = h // 2 + 2; d.rectangle([pad[0] - 10, yy - 3, pad[0] - 10 + (tw + 20) * strike, yy + 3], fill=fg + (255,))
        self.cache[key] = im; return im

    @staticmethod
    def _paste(layer, im, x, y, t, t_in, t_out):
        a_in = ease((t - t_in) / 0.22); a_out = 1 - ease((t - t_out) / 0.18)
        a = min(a_in, a_out)
        if a <= 0: return
        s = 0.92 + 0.08 * a_in
        if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
        if a < 1:
            im = im.copy(); al = im.getchannel("A").point(lambda v: int(v * a)); im.putalpha(al)
        cx = x + (im.width / s - im.width) / 2 if s != 1 else x
        layer.alpha_composite(im, (int(cx), int(y + (1 - a_in) * 18)))

    def draw(self, t):
        layer = None
        for c in self.cards:
            if not (c["t_in"] - 0.01 <= t <= c["t_out"] + 0.2): continue
            if layer is None: layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if c["type"] == "chat":
                y = 210
                vis = [b for b in c["bubbles"] if t >= b["t"]][-2:]
                for b in vis:
                    p = (t - b["t"] - 0.12) / max(0.3, b["t_done"] - b["t"] - 0.15)
                    n = int(len(b["text"]) * min(max(p, 0), 1))
                    im = self._bubble("MAR", b["text"][:n], p < 1.05 and int(t * 3) % 2 == 0)
                    self._paste(layer, im, 100, y, t, b["t"], c["t_out"]); y += self._bubble("MAR", b["text"]).height + 18
            elif c["type"] == "strike":
                st = ease((t - c["t_strike"]) / 0.3) if t >= c["t_strike"] else 0
                im = self._box(c["text"].upper(), 64, strike=st)
                self._paste(layer, im, (W - im.width) // 2, 330, t, c["t_in"], c["t_out"])
            elif c["type"] == "steps":
                y = 290
                for i, s in enumerate(c["steps"]):
                    if t < s["t"]: break
                    im = self._box(s["label"], 46, fill=PANEL, fg=PORC)
                    self._paste(layer, im, 100 + i * 60, y, t, s["t"], c["t_out"]); y += im.height + 22
            elif c["type"] == "label":
                key = ("lab", c["text"])
                if key not in self.cache:
                    fs_ = 62; d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
                    while fs_ > 30 and spaced_len(d0, c["text"].upper(), font("IBMPlexMono-500.ttf", fs_), 10) > 840: fs_ -= 2
                    f = font("IBMPlexMono-500.ttf", fs_)
                    tw = int(spaced_len(d0, c["text"].upper(), f, 10)); self.cache[key] = (f, tw)
                f, tw = self.cache[key]
                st = ease((t - c["t_strike"]) / 0.35) if "t_strike" in c and t >= c["t_strike"] else 0
                nt = (t - c["t_note"]) / 0.6 if "t_note" in c and t >= c["t_note"] else 0
                pk = ("labimg", round(st, 2), min(1, round(nt, 2)))
                if pk not in self.cache:
                    w, h = tw + 110, 150
                    im = paper(w, h, rot=0, tape=True, seed=5)
                    d = ImageDraw.Draw(im); ox, oy = 60, 60
                    text_spaced(d, (ox + 55, oy + 38), c["text"].upper(), f, CARBON + (255,), 10)
                    if st > 0: pencil_line(d, ox + 35, ox + w - 35, oy + 78, st, seed=2, width=8)
                    im = im.rotate(-3, expand=True, resample=Image.BICUBIC)
                    self.cache = {k2: v for k2, v in self.cache.items() if k2[0] != "labimg"}; self.cache[pk] = im
                im = self.cache[pk]
                self._paste(layer, im, (W - im.width) // 2, c.get("y", 170), t, c["t_in"], c["t_out"])
                if nt > 0 and t <= c["t_out"] + 0.2:
                    fh = font("Caveat-500.ttf", 76); txt = c["note"]; dl = ImageDraw.Draw(layer)
                    nlines, cur = [], ""
                    for wd in txt.split():
                        tt = (cur + " " + wd).strip()
                        if cur and dl.textlength(tt, font=fh) > 820: nlines.append(cur); cur = wd
                        else: cur = tt
                    nlines.append(cur)
                    tw2 = int(max(dl.textlength(l, font=fh) for l in nlines)); lh2 = 84
                    nk = ("notepaper", txt)
                    if nk not in self.cache: self.cache[nk] = paper(tw2 + 70, 40 + lh2 * len(nlines), rot=2.0, tape=False, seed=9, color=(250, 247, 238))
                    npi = self.cache[nk]; ny = c.get("y", 170) + im.height - 40
                    self._paste(layer, npi, (W - npi.width) // 2 + 30, ny - 60, t, c["t_note"], c["t_out"])
                    a2 = 1 - ease((t - c["t_out"]) / 0.18); left = int(len(txt) * min(1, nt))
                    for li, ln in enumerate(nlines):
                        show = ln[:max(0, left)]; left -= len(ln) + 1
                        dl.text(((W - tw2) / 2 + 30, ny + 6 + li * lh2), show, font=fh, fill=GRAPHITE + (int(255 * a2),))
            elif c["type"] == "prompt":
                p = (t - c["t_in"] - 0.15) / max(0.4, c["t_typed"] - c["t_in"] - 0.2)
                n = int(len(c["text"]) * min(max(p, 0), 1)); txt = c["text"][:n]
                key = ("prompt", txt, p < 1.05 and int(t * 3) % 2 == 0)
                if key not in self.cache:
                    fq = font("Geist-400.ttf", 42); fh = font("IBMPlexMono-400.ttf", 22)
                    im = Image.new("RGBA", (900, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.rounded_rectangle([0, 0, 899, 149], radius=26, fill=(250, 248, 244, 236), outline=(214, 208, 199, 255), width=2)
                    text_spaced(d, (38, 22), c.get("label", "DEINE FRAGE"), fh, MUTED + (255,), 5)
                    d.text((38, 60), txt if txt else "", font=fq, fill=CARBON + (255,))
                    if key[2]:
                        xc = 38 + d.textlength(txt, font=fq) + 6; d.rectangle([xc, 64, xc + 4, 108], fill=CARBON + (255,))
                    d.ellipse([820, 50, 872, 102], fill=CARBON + (255,)); d.polygon([(838, 66), (860, 76), (838, 86)], fill=PORC + (255,))
                    self.cache = {k: v for k, v in self.cache.items() if k[0] != "prompt"}; self.cache[key] = im
                im = self.cache[key]
                self._paste(layer, im, 90, c.get("y", 300), t, c["t_in"], c["t_out"])
                if "t_reply" in c and t >= c["t_reply"]:
                    pr = (t - c["t_reply"] - 0.12) / max(0.3, c["t_reply_done"] - c["t_reply"] - 0.15)
                    nr = int(len(c["reply"]) * min(max(pr, 0), 1))
                    imr = self._bubble("MAR", c["reply"][:nr], pr < 1.05 and int(t * 3) % 2 == 0)
                    self._paste(layer, imr, 110, c.get("y", 300) + 175, t, c["t_reply"], c["t_out"])
            elif c["type"] == "checklist":
                done = sum(1 for it in c["items"] if t >= it["t"])
                key = ("check", done)
                if key not in self.cache:
                    fh = font("IBMPlexMono-500.ttf", 22); fi = font("Geist-400.ttf", 38)
                    h = 92 + 70 * len(c["items"]) + 20
                    im = Image.new("RGBA", (900, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.rounded_rectangle([0, 0, 899, h - 1], radius=10, fill=PANEL + (244,), outline=LINE + (255,), width=2)
                    text_spaced(d, (38, 32), c["title"], fh, MUTED + (255,), 5)
                    cnt = f"{done} / {len(c['items'])}"; text_spaced(d, (860 - spaced_len(d, cnt, fh, 5), 32), cnt, fh, PORC + (255,), 5)
                    for i, it in enumerate(c["items"]):
                        y = 92 + 70 * i; on = i < done; cur = i == done - 1
                        if on:
                            d.ellipse([38, y + 4, 74, y + 40], fill=PORC + (255,))
                            d.line([(47, y + 22), (54, y + 30), (66, y + 13)], fill=CARBON + (255,), width=4)
                            d.text((96, y), it["text"], font=fi, fill=(PORC if cur else MUTED) + (255,))
                        else:
                            d.ellipse([38, y + 4, 74, y + 40], outline=LINE + (255,), width=3)
                            d.rounded_rectangle([96, y + 14, 96 + 420 - 60 * i, y + 30], radius=8, fill=LINE + (255,))
                    self.cache[key] = im
                yy = c.get("y", 280)
                if "t_move" in c: yy = c["y_from"] + (yy - c["y_from"]) * ease((t - c["t_move"]) / 0.45)
                self._paste(layer, self.cache[key], 90, yy, t, c["t_in"], c["t_out"])
            elif c["type"] == "stamp":
                key = ("stamp", c["text"])
                if key not in self.cache: self.cache[key] = stamp(c["text"])
                im = self.cache[key]; p = ease((t - c["t_in"]) / 0.16)
                a = 1 - ease((t - c["t_out"]) / 0.2)
                if a > 0:
                    s = 1.6 - 0.6 * p; im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
                    if a * min(1, p * 1.5) < 1: im2.putalpha(im2.getchannel("A").point(lambda v: int(v * a * min(1, p * 1.5))))
                    layer.alpha_composite(im2, ((W - im2.width) // 2, c.get("y", 330) - im2.height // 2))
            elif c["type"] == "cta":
                cs = 42
                while cs > 22 and spaced_len(ImageDraw.Draw(Image.new("L", (1, 1))), c["text"], font("IBMPlexMono-500.ttf", cs), 5) + 80 > 980: cs -= 2
                im = self._box(c["text"], cs, spacing=5, pad=(40, 32))
                self._paste(layer, im, (W - im.width) // 2, 300, t, c["t_in"], c["t_out"] + 1)
                key = ("sub", c["sub"])
                if key not in self.cache:
                    f = font("IBMPlexMono-400.ttf", 28); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
                    sw = int(spaced_len(d0, c["sub"], f, 6)) + 4
                    s_im = Image.new("RGBA", (sw, 40), (0, 0, 0, 0)); text_spaced(ImageDraw.Draw(s_im), (0, 4), c["sub"], f, CARBON + (200,), 6)
                    self.cache[key] = s_im
                s_im = self.cache[key]
                self._paste(layer, s_im, (W - s_im.width) // 2, 300 + im.height + 26, t, c["t_in"] + 0.15, c["t_out"] + 1)
        return layer

def render_intro(intro, t):
    img = Image.new("RGB", (W, H), CARBON); d = ImageDraw.Draw(img)
    f = font("Geist-300.ttf", 92); fl = font("IBMPlexMono-500.ttf", 26); lh = 104
    text_spaced(d, (96, 560), intro.get("label", "MAR"), fl, MUTED, 10)
    y = 640; cur_pos = None
    for ln in intro["lines"]:
        if t < ln["at"]: break
        pre = ln.get("pre", 0); n_all = len(ln["text"])
        p = (t - ln["at"]) / max(0.1, ln["typed_by"] - ln["at"])
        n = min(n_all, pre + int((n_all - pre) * min(max(p, 0), 1)))
        col = (150, 147, 156) if ln.get("grey") else PORC
        words = ln["text"][:n].split(" ")
        lines, cur = [], ""
        for w in ln["text"].split(" "):  # Umbruch nach vollem Text, damit nichts springt
            tt = (cur + " " + w).strip()
            if cur and d.textlength(tt, font=f) > 880: lines.append(cur); cur = w
            else: cur = tt
        lines.append(cur)
        shown = n; x = 96
        for full in lines:
            part = full[:max(0, shown)]; shown -= len(full) + 1
            d.text((96, y), part, font=f, fill=col); x = 96 + d.textlength(part, font=f)
            if shown < 0: cur_pos = (x, y); break
            y += lh
        else: cur_pos = (x, y - lh)
        y += lh + 50
    if cur_pos and int(t * 2.2) % 2 == 0:
        d.rectangle([cur_pos[0] + 8, cur_pos[1] + 14, cur_pos[0] + 14, cur_pos[1] + 96], fill=PORC)
    return img

# ---------------------------------------------------------------- motion-graphics hintergrund
def make_studio(pad=80):
    """Warmes Studio, etwas groesser als das Bild -> langsames Driften des Lichts per Ausschnitt."""
    h, w = H + 2 * pad, W + 2 * pad
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / 820) ** 2 + ((yy - 760 - pad) / 1150) ** 2).clip(0, 1) ** 1.3
    c0 = np.array([228, 216, 200], np.float32); c1 = np.array([154, 135, 116], np.float32)
    return c0 * (1 - d[..., None]) + c1 * d[..., None]

CARBON_ARR = np.array(CARBON, np.float32)

def make_dark():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 540) / 900) ** 2 + ((yy - 700) / 1100) ** 2).clip(0, 1)
    c0 = np.array([42, 33, 29], np.float32); c1 = np.array(CARBON, np.float32)
    return c0 * (1 - d[..., None]) + c1 * d[..., None]

class Moments:
    def __init__(self, ms, words, segb, bg_image=None):
        self.photo = None
        if bg_image:
            ph = Image.open(os.path.join(ROOT, bg_image)).convert("RGB")
            sc = max(1.12 * W / ph.width, 1.12 * H / ph.height)
            self.photo = np.asarray(ph.resize((int(ph.width * sc), int(ph.height * sc)), Image.LANCZOS), np.float32)
        self.ms = []
        for m in ms:
            m = dict(m); m["t_in"] = anchor(m["at"], words, segb); m["t_out"] = anchor(m["until"], words, segb)
            m["t_out"] = max(m["t_out"], m["t_in"] + m.get("min", 0))
            for k in ("strike_at", "focus_at"):
                if k in m: m[k.replace("_at", "")] = anchor(m[k], words, segb)
            self.ms.append(m)
        self.studio = make_studio(); self.dark = make_dark(); self.cache = {}
        self.grain = [np.random.default_rng(i).normal(0, 3.0, (H, W, 1)).astype(np.float32) for i in range(4)]

    def w(self, m, t, fi=0.18, fo=0.18):
        return min(ease((t - m["t_in"]) / fi), 1 - ease((t - m["t_out"]) / fo))

    def scale(self, t):
        s = 1.0
        for m in self.ms:
            if "scale" in m: s = min(s, 1 - (1 - m["scale"]) * self.w(m, t, 0.22, 0.22))
        return s

    def events(self):
        ev = []
        for m in self.ms:
            if m["type"] == "word": ev.append(("thud" if m.get("dark") else "pop", m["t_in"]))
            if m["type"] in ("waterfall", "knockout", "typewall"): ev.append(("whoosh", m["t_in"] - 0.2))
            if m["type"] == "freeze": ev.append(("pop", m["t_in"]))
            if m["type"] == "health":
                ev.append(("whoosh", m["t_in"] - 0.2))
                if "strike" in m: ev.append(("scratch", m["strike"]))
                if "focus" in m: ev.append(("pop", m["focus"]))
        return ev

    def _word(self, text, color):
        key = ("w", text, color)
        if key not in self.cache:
            d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1))); size = 420
            while size > 56:
                f = font("Geist-600.ttf", size)
                if d0.textlength(text, font=f) <= 990: break
                size -= 10
            tw = int(d0.textlength(text, font=f)); asc, desc = f.getmetrics()
            im = Image.new("RGBA", (tw + 40, asc + desc + 40), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((20, 20), text, font=f, fill=color + (255,))
            self.cache[key] = im
        return self.cache[key]

    def _health(self, m, t):
        rows = [("STRATEGY", 78), ("POSITIONING", 64), ("SALES", 41), ("OPERATIONS", 70), ("FINANCE", 82), ("LEADERSHIP", 58)]
        im = Image.new("RGBA", (900, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 899, 699], fill=PANEL + (250,), outline=LINE + (255,), width=2)
        fm = font("IBMPlexMono-400.ttf", 24); fb = font("Geist-300.ttf", 120)
        text_spaced(d, (44, 40), "BUSINESS HEALTH", fm, MUTED + (255,), 6)
        d.text((44, 80), "72", font=fb, fill=PORC + (255,)); text_spaced(d, (200, 160), "/ 100", fm, MUTED + (255,), 6)
        st = ease((t - m["strike"]) / 0.3) if "strike" in m and t >= m["strike"] else 0
        fo = ease((t - m["focus"]) / 0.3) if "focus" in m and t >= m["focus"] else 0
        y = 250
        for i, (lab, val) in enumerate(rows):
            grow = ease((t - m["t_in"] - 0.08 * i) / 0.6)
            hi = (lab == "SALES" and st == 0 and fo == 0) or (lab == "POSITIONING" and fo > 0)
            dim = fo > 0 and lab not in ("POSITIONING", "SALES")
            col = PORC if hi else (MUTED if not dim else LINE)
            text_spaced(d, (44, y), ("• " if hi else "") + lab, fm, col + (255,), 6)
            vs = str(val); d.text((856 - d.textlength(vs, font=fm), y), vs, font=fm, fill=col + (255,))
            d.rectangle([44, y + 40, 856, y + 41], fill=LINE + (255,))
            d.rectangle([44, y + 39, 44 + 812 * val / 100 * grow, y + 42 + (2 if hi else 0)], fill=col + (255,))
            if lab == "SALES" and st > 0:
                d.rectangle([40, y + 13, 40 + 820 * st, y + 17], fill=(168, 105, 100, 255))
            y += 64
        if fo > 0:
            text_spaced(d, (44, 640), "POSITIONING 64 —— SALES 41 · MÖGLICHER ZUSAMMENHANG", font("IBMPlexMono-400.ttf", 19),
                        tuple(int(c) for c in MUTED) + (int(255 * fo),), 4)
        return im

    def _waterfall(self, m, t, a):
        qs = m["questions"]; key = ("wf",)
        if key not in self.cache:
            cards = []
            fq = font("Geist-400.ttf", 40); fl = font("IBMPlexMono-500.ttf", 20)
            for i, q in enumerate(qs):
                d0 = ImageDraw.Draw(Image.new("L", (1, 1))); lines, cur = [], ""
                for w_ in q.split():
                    tt = (cur + " " + w_).strip()
                    if cur and d0.textlength(tt, font=fq) > 330: lines.append(cur); cur = w_
                    else: cur = tt
                lines.append(cur)
                h = 70 + 50 * len(lines) + 30
                im = paper(390, h, rot=np.random.default_rng(i).uniform(-4, 4), tape=(i % 3 == 0), seed=20 + i)
                d = ImageDraw.Draw(im); ox = (im.width - 390) // 2; oy = (im.height - h) // 2
                text_spaced(d, (ox + 30, oy + 26), "MAR", fl, MUTED + (255,), 6)
                for k, ln in enumerate(lines): d.text((ox + 30, oy + 62 + 50 * k), ln, font=fq, fill=CARBON + (255,))
                cards.append(im)
            self.cache[key] = cards
        cards = self.cache[key]
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        el = (t - m["t_in"]) * m.get("speed", 170)
        for ci, (x, y0) in enumerate([(-40, 0), (330, 420), (700, 180)]):
            y = y0 + 700 - el  # erste Karte startet im unteren Bilddrittel und faehrt nach oben
            k = ci
            while y < H:
                im = cards[k % len(cards)]
                if y > -im.height: L.alpha_composite(im, (x, int(y)))
                y += im.height + 70; k += 3
        if a < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
        return L

    def post(self, img, fg_full, t):
        """Filter nach dem Personen-Composite: Schwarz-Weiss, Text-Fenster"""
        for m in self.ms:
            a = self.w(m, t, 0.25, 0.25)
            if a <= 0: continue
            if m["type"] == "bw":
                g = img @ np.array([0.30, 0.59, 0.11], np.float32)
                img = img * (1 - a) + (g[..., None] * np.array([1.0, 0.99, 0.97], np.float32)) * a
            elif m["type"] == "knockout":
                key = ("ko", m["text"])
                if key not in self.cache:
                    mk = Image.new("L", (W, H), 0); d = ImageDraw.Draw(mk); size = 900
                    while True:
                        f = font("Geist-700.ttf", size)
                        if d.textlength(m["text"], font=f) < 1000: break
                        size -= 20
                    bb = d.textbbox((0, 0), m["text"], font=f)
                    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], m.get("y", 560) - bb[1]), m["text"], font=f, fill=255)
                    self.cache[key] = np.asarray(mk, np.float32)[..., None] / 255
                k = self.cache[key]
                frame = CARBON_ARR * (1 - k) + fg_full * k
                img = img * (1 - a) + frame * a
        return img

    def background(self, t):
        if self.photo is not None:  # langsame Kamerafahrt ueber das Foto
            ph = self.photo; mx, my = ph.shape[1] - W, ph.shape[0] - H
            ox = int(mx * (0.5 + 0.35 * math.sin(t * 0.11))); oy = int(my * (0.5 + 0.3 * math.cos(t * 0.08)))
            base = ph[oy:oy + H, ox:ox + W]
        else:
            ox = int(80 + 50 * math.sin(t * 0.35)); oy = int(80 + 40 * math.cos(t * 0.27))
            base = self.studio[oy:oy + H, ox:ox + W]
        dk = max([self.w(m, t, 0.15, 0.15) for m in self.ms if m.get("dark")] + [0])
        if dk > 0: base = base * (1 - dk) + self.dark * dk
        base = base + self.grain[int(t * 4) % 4]
        layer = None
        for m in self.ms:
            a = self.w(m, t)
            if a <= 0 or m["type"] in ("plain", "bw", "knockout", "freeze"): continue
            if layer is None: layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if m["type"] == "waterfall":
                layer.alpha_composite(self._waterfall(m, t, a)); continue
            if m["type"] == "typewall":
                key = ("tw", m["text"])
                if key not in self.cache:
                    f = font("Geist-600.ttf", m.get("size", 150)); rowh = int(m.get("size", 150) * 1.0)
                    unit = (m["text"] + "  ") * 8
                    rows = []
                    for r_ in range(H // rowh + 2):
                        im = Image.new("RGBA", (int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(unit, font=f)) + 10, rowh + 30), (0, 0, 0, 0))
                        ImageDraw.Draw(im).text((0, 0), unit, font=f, fill=CARBON + (int(255 * m.get("alpha", 0.9)),))
                        rows.append(im)
                    self.cache[key] = (rows, rowh)
                rows, rowh = self.cache[key]; el = t - m["t_in"]
                Lw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                for r_, im in enumerate(rows):
                    dx = -((el * 60 * (1 if r_ % 2 else -1)) % 600) - (300 if r_ % 2 else 0)
                    Lw.alpha_composite(im, (int(dx), r_ * rowh - 40)) if dx > -im.width else None
                if a < 1: Lw.putalpha(Lw.getchannel("A").point(lambda v: int(v * a)))
                layer.alpha_composite(Lw); continue
            if m["type"] == "word":
                col = PORC if m.get("dark") else ((203, 188, 169) if m.get("faint") else CARBON)
                im = self._word(m["text"], col)
                p = ease((t - m["t_in"]) / 0.28); dur = max(0.5, m["t_out"] - m["t_in"])
                s = 1.12 - 0.12 * p + 0.04 * min(1, (t - m["t_in"]) / dur)
                im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
            else:
                im = self._health(m, t)
            if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
            y = (m.get("y", 460)) - im.height // 2 if m["type"] == "word" else 100
            layer.alpha_composite(im, ((W - im.width) // 2, max(0, y)))
        if layer is not None:
            la = np.asarray(layer, np.float32); k = la[..., 3:] / 255; base = base * (1 - k) + la[..., :3] * k
        return base

def series_bar(day, total=30):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fm = font("IBMPlexMono-500.ttf", 28); x0, y0, gap = 70, 168, 6; segw = (W - 2 * x0 - (total - 1) * gap) / total
    for i in range(total):
        col = CARBON + (235,) if i < day else (16, 16, 15, 80)
        d.rectangle([x0 + i * (segw + gap), y0, x0 + i * (segw + gap) + segw, y0 + 6], fill=col)
    text_spaced(d, (x0, y0 + 22), f"TAG {day:02d} / {total}", fm, CARBON + (235,), 9)
    s = "ICH BAUE MAR"; text_spaced(d, (W - x0 - spaced_len(d, s, fm, 9), y0 + 22), s, fm, CARBON + (190,), 9)
    m = im.getchannel("A").filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(18))
    hz = Image.new("RGBA", (W, H), PORC + (0,)); hz.putalpha(m.point(lambda v: int(min(255, v * 1.5) * 0.45)))
    hz.alpha_composite(im)
    return np.asarray(hz, np.float32)

# ---------------------------------------------------------------- matting
class Matte:
    def __init__(self):
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download
        m = hf_hub_download("Xenova/modnet", "onnx/model.onnx")
        so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
        self.s = ort.InferenceSession(m, so, providers=["CPUExecutionProvider"]); self.n = self.s.get_inputs()[0].name
    def __call__(self, rgb):
        h = 672; w = int(rgb.shape[1] * h / rgb.shape[0]) // 32 * 32
        x = np.asarray(Image.fromarray(rgb).resize((w, h), Image.BILINEAR), np.float32) / 127.5 - 1
        a = self.s.run(None, {self.n: x.transpose(2, 0, 1)[None]})[0][0, 0]
        return np.asarray(Image.fromarray((a * 255).clip(0, 255).astype(np.uint8)).resize((rgb.shape[1], rgb.shape[0]), Image.BILINEAR), np.float32) / 255

FACE_CACHE = {}

def framing(alpha, zoom, crop_bottom, face_pos=0.42, src=None, zmin=1.06):
    if src in FACE_CACHE: head_top, cx = FACE_CACHE[src]
    else:
        rows = np.where(alpha[:, 200:520].mean(1) > 0.3)[0]
        head_top = rows[0] if len(rows) else 300
        cols = np.where(alpha[head_top:head_top + 300].mean(0) > 0.5)[0]
        cx = (cols[0] + cols[-1]) / 2 if len(cols) else SRC_W / 2
        if src is not None: FACE_CACHE[src] = (head_top, cx)
    cw, ch = SRC_W / zoom, SRC_H / zoom
    face_y = head_top + 170
    ch0 = SRC_H / zmin  # Gesicht bei jeder Zoomstufe auf derselben relativen Hoehe wie bei der kleinsten
    y00 = min(max(face_y - face_pos * ch0, 0), crop_bottom - ch0); f0 = (face_y - y00) / ch0
    y0 = min(max(face_y - f0 * ch, 0), crop_bottom - ch)
    x0 = min(max(cx - cw / 2, 0), SRC_W - cw)
    return (x0, y0, x0 + cw, y0 + ch)

# ---------------------------------------------------------------- captions
def ass_time(t): return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

def captions(words, edl, segb, end_t, path):
    f = font("Geist-600.ttf", 118); d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    acc = {(i, a) for i, s in enumerate(edl["segments"]) for a in s.get("accent", [])}
    hook = {i for i, s in enumerate(edl["segments"]) if s.get("hook")}
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             "Style: Cap,Geist SemiBold,118,&H00EAEFF1,&H00EAEFF1,&H000F1010,&H000F1010,0,0,0,0,100,100,-1,0,1,0,0,5,0,0,0,1",
             "Style: Small,Geist,58,&H00EAEFF1,&H00EAEFF1,&H000F1010,&H780F1010,0,0,0,0,100,100,0,0,1,0,3,5,0,0,0,1",
             "Style: Acc,IBM Plex Mono Medium,78,&H000F1010,&H000F1010,&H00EAEFF1,&H00EAEFF1,0,0,0,0,100,100,8,0,3,24,0,5,0,0,0,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ws = [w for w in words if w["seg"] not in hook]
    for i, w in enumerate(ws):
        t0 = w["t"]; nxt = ws[i + 1]["t"] if i + 1 < len(ws) else end_t
        t1 = min(nxt, t0 + 1.2) if nxt - t0 < 1.5 else t0 + 0.6
        if t1 - t0 < 0.1: t1 = t0 + 0.1
        txt = w["text"]; pos = r"\an5\pos(540,1420)"; pop = r"\fscx86\fscy86\t(0,90,\fscx100\fscy100)"
        if edl["segments"][w["seg"]].get("aside"):
            if i == 0 or ws[i - 1]["seg"] != w["seg"]:
                seg_ws = [x for x in ws if x["seg"] == w["seg"]]; t1s = segb[w["seg"]][1]
                lines.append(f"Dialogue: 1,{ass_time(t0)},{ass_time(t1s)},Small,,0,0,0,,{{{pos}\\fad(120,120)}}{' '.join(x['text'] for x in seg_ws)}")
            continue
        if any((w["seg"], a) == (s, a) and (txt == a or txt.startswith(a)) for s, a in acc):
            lab = txt.strip(",.?!").upper()
            lines.append(f"Dialogue: 1,{ass_time(t0)},{ass_time(t1)},Acc,,0,0,0,,{{{pos}{pop}}}{lab}")
        else:
            tw = d0.textlength(txt, font=f); sc = min(100, int(100 * 940 / tw)) if tw > 0 else 100
            fs = rf"\fscx{sc}\fscy{sc}" if sc < 100 else ""
            pop2 = pop.replace("100", str(sc)) if sc < 100 else pop
            lines.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t1)},Cap,,0,0,0,,{{{pos}{fs}{pop2}\\1a&HFF&\\3a&H60&\\bord14\\blur18}}{txt}")
            lines.append(f"Dialogue: 1,{ass_time(t0)},{ass_time(t1)},Cap,,0,0,0,,{{{pos}{fs}{pop2}}}{txt}")
    open(path, "w").write("\n".join(lines) + "\n")

# ---------------------------------------------------------------- sfx
def sfx(kind, rng):
    t = lambda d: np.arange(int(SR * d)) / SR
    if kind == "pop":
        x = t(0.09); f = 950 * np.exp(-x * 30) + 260
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 45); return 0.55 * s
    if kind == "tick":
        x = t(0.025); n = rng.normal(0, 1, len(x)); n = np.diff(n, prepend=0)
        return 0.10 * n * np.exp(-x * 260) * rng.uniform(0.7, 1.1)
    if kind == "whoosh":
        x = t(0.42); n = rng.normal(0, 1, len(x))
        k = np.exp(-((x - 0.26) / 0.11) ** 2)
        y = np.zeros_like(n); a = 0.0
        for i in range(len(n)):
            c = 0.04 + 0.25 * k[i]; a += c * (n[i] - a); y[i] = a
        return 0.9 * y * k
    if kind == "scratch":
        x = t(0.22); n = np.diff(rng.normal(0, 1, len(x)), prepend=0)
        return 0.16 * n * np.sin(np.pi * x / 0.22) ** 0.5
    if kind == "thud":
        x = t(0.3); return 0.5 * np.sin(2 * np.pi * 70 * x) * np.exp(-x * 14)
    raise ValueError(kind)

# ---------------------------------------------------------------- main
def main():
    edl_path, out = sys.argv[1], sys.argv[2]
    preview = float(sys.argv[sys.argv.index("--preview") + 1]) if "--preview" in sys.argv else None
    edl = json.load(open(edl_path)); work = os.path.splitext(out)[0] + "_work"; os.makedirs(work, exist_ok=True)
    srcs, clips, words, segb, total = plan(edl)
    end_s = edl.get("endframe", {}).get("seconds", 0)
    json.dump({"clips": clips, "words": words, "segments": segb}, open(f"{work}/plan.json", "w"), ensure_ascii=False, indent=1)
    print(f"Clips: {len(clips)}  Laenge: {total:.1f}s + Endframe {end_s}s")

    # ---- Audio
    audio = {k: load_audio(p, SR) for k, p in srcs.items()}
    voice = np.zeros(int((total + end_s) * SR) + SR, np.float32)
    fade = int(0.008 * SR)
    for c in clips:
        a = audio[c["src"]][int(c["in"] * SR):int(c["out"] * SR)].copy()
        r = np.linspace(0, 1, fade); a[:fade] *= r; a[-fade:] *= r[::-1]
        i0 = int(c["t0"] * SR); voice[i0:i0 + len(a)] += a
    import wave
    def wav(p, x):
        with wave.open(p, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes((x.clip(-1, 1) * 32767).astype(np.int16).tobytes())
    wav(f"{work}/voice_raw.wav", voice)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/voice_raw.wav", "-af",
                    "highpass=f=80,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3",
                    f"{work}/voice.wav"], check=True)
    voice = load_audio(f"{work}/voice.wav", SR)
    cards = Cards(edl.get("cards", []), words, segb)
    ev = cards.events()
    moments = Moments(edl.get("moments", []), words, segb, edl.get("background_image")); ev += moments.events()
    hl = edl.get("headline", [])
    for i, h in enumerate(hl[1:], 1): ev.append(("whoosh", anchor(h["at"], words, segb) - 0.2))
    for i, h in enumerate(hl):
        if "big" in h: ev.append(("thud", (anchor(h["at"], words, segb) if (i or h.get("anchored")) else 0.0) + 0.25))
    for i, s in enumerate(edl["segments"]):
        if s.get("punch") == "Problem.":
            ev.append(("thud", next(w["t"] for w in words if w["seg"] == i and w["text"].startswith("Problem"))))
    if end_s: ev.append(("whoosh", total - 0.22))
    if edl.get("intro"): ev.append(("pop", 0.05))
    rng = np.random.default_rng(3); fx = np.zeros_like(voice)
    vr = np.sqrt((voice ** 2).mean()) + 1e-9
    for k, t0 in ev:
        s = sfx(k, rng); s = s / (np.abs(s).max() + 1e-9) * vr * {"pop": 1.4, "tick": 0.55, "whoosh": 1.2, "scratch": 0.9, "thud": 1.6}[k]
        i0 = max(0, int(t0 * SR)); fx[i0:i0 + len(s)] += s[:len(fx) - i0]
    wav(f"{work}/mix.wav", voice + fx)

    # ---- Video
    bg = make_bg(); matte = Matte()
    hl_layers = []
    for i, h in enumerate(hl):
        ts = anchor(h["at"], words, segb) if (i or h.get("anchored")) else 0.0
        hl_layers.append((ts, h if "big" in h else render_headline([(h["text"], h["grey"])])))
    hook_end = max((b for (a, b), s in zip(segb, edl["segments"]) if s.get("hook")), default=0)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", f"{work}/video.mp4"],
                           stdin=subprocess.PIPE)
    done = 0; limit = preview * FPS if preview else 1e9
    intro = edl.get("intro")
    if intro:
        for k in range(round(intro["seconds"] * FPS)):
            if done >= limit: break
            enc.stdin.write(np.asarray(render_intro(intro, k / FPS)).tobytes()); done += 1
    rg = [float(x) for x in sys.argv[sys.argv.index("--range") + 1].split("-")] if "--range" in sys.argv else None
    frozen = None
    sbar = series_bar(edl["series"]["day"]) if edl.get("series") else None
    for ci, c in enumerate(clips):
        if done >= limit: break
        if rg and (c["t0"] + c["frames"] / FPS < rg[0] or c["t0"] > rg[1]): continue
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{c['in']:.3f}", "-i", srcs[c["src"]], "-frames:v", str(c["frames"]),
                              "-vf", ((HDR_TO_SDR + ",") if is_hdr(srcs[c["src"]]) else "") + f"scale={SRC_W}:{SRC_H}:flags=lanczos",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(-1, SRC_H, SRC_W, 3)
        prev = None; box = None; box1 = None
        for fi in range(c["frames"]):
            if done >= limit: break
            f = fr[min(fi, len(fr) - 1)]; t = c["t0"] + fi / FPS
            a = matte(f); a = a if prev is None else 0.65 * a + 0.35 * prev; prev = a
            if box is None:
                fp = 0.30 if edl["segments"][c["seg"]].get("hook") else 0.42
                box = box0 = framing(a, c["zoom"], edl.get("crop_bottom", SRC_H), 0.42, c["src"])
                box1 = framing(a, c["zoom_to"], edl.get("crop_bottom", SRC_H), 0.42, c["src"]) if "zoom_to" in c else None
            if box1 is not None:
                q = fi / max(1, c["frames"] - 1); q = q * q * (3 - 2 * q)
                box = tuple(x0 + (x1 - x0) * q for x0, x1 in zip(box0, box1))
            if c.get("zoom_from") and fi < 12:
                if fi == 0: boxf = framing(a, c["zoom_from"], edl.get("crop_bottom", SRC_H), 0.42, c["src"])
                q = ease(fi / 12); box = tuple(xf + (x0 - xf) * q for xf, x0 in zip(boxf, box0))
            fg = np.asarray(Image.fromarray(f).resize((W, H), Image.LANCZOS, box=box), np.float32)
            al = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR, box=box), np.float32)[..., None] / 255
            fzm = [m for m in moments.ms if m["type"] == "freeze" and m["t_in"] <= t <= m["t_out"]]
            if fzm:
                if frozen is None or frozen[0] is not fzm[0]: frozen = (fzm[0], fg.copy(), al.copy())
                fg, al = frozen[1], frozen[2]
            base = moments.background(t)
            s = moments.scale(t) * edl.get("person_scale", 1.0)
            fg_full = fg
            if s < 0.999:
                sw, sh = int(W * s), int(H * s); ox = (W - sw) // 2; oy = H - sh
                fg2 = np.zeros_like(fg); al2 = np.zeros_like(al)
                fg2[oy:, ox:ox + sw] = np.asarray(Image.fromarray(fg.astype(np.uint8)).resize((sw, sh), Image.BILINEAR), np.float32)
                al2[oy:, ox:ox + sw, 0] = np.asarray(Image.fromarray((al[..., 0] * 255).astype(np.uint8)).resize((sw, sh), Image.BILINEAR), np.float32) / 255
                fg, al = fg2, al2
            hook_start = min((a for (a, b), s in zip(segb, edl["segments"]) if s.get("hook")), default=0)
            if hook_start - 0.01 <= t < hook_end + 0.25:
                lay = None
                for ts, L in hl_layers:
                    if t >= ts:
                        lay = render_hook(L, t - ts) if isinstance(L, dict) else L
                hook_front = None
                if lay is not None:
                    la = np.asarray(lay, np.float32); k = la[..., 3:] / 255 * (1 - ease((t - hook_end) / 0.25))
                    if any(isinstance(L, dict) and L.get("front") for _, L in hl_layers): hook_front = (la, k)
                    else: base = base * (1 - k) + la[..., :3] * k
            if fzm:  # Freeze-Sticker: Vollfarbe, weisse Kontur um die Person
                fa = Image.fromarray((al[..., 0] * 255).astype(np.uint8))
                ring = np.asarray(fa.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(1.5)), np.float32)[..., None] / 255
                q = ease((t - fzm[0]["t_in"]) / 0.12)
                flat = np.array(fzm[0].get("color", (42, 33, 29)), np.float32)
                base = base * (1 - q) + flat * q
                base = base * (1 - ring * q) + 255 * ring * q
            img = base * (1 - al) + fg * al
            if hook_start - 0.01 <= t < hook_end + 0.25 and hook_front is not None:
                img = img * (1 - hook_front[1]) + hook_front[0][..., :3] * hook_front[1]
            img = moments.post(img, fg_full, t)
            if sbar is not None:
                k = sbar[..., 3:] / 255; img = img * (1 - k) + sbar[..., :3] * k
            cl = cards.draw(t)
            if cl is not None:
                ca = np.asarray(cl, np.float32); k = ca[..., 3:] / 255; img = img * (1 - k) + ca[..., :3] * k
            enc.stdin.write(img.clip(0, 255).astype(np.uint8).tobytes()); done += 1
        print(f"  Clip {ci + 1}/{len(clips)}  ({done} Frames)", flush=True)
    if end_s and done < limit:
        logo = Image.open(os.path.join(ROOT, "design", "mar-logo.png")).convert("RGB")
        logo = logo.resize((960, int(960 * logo.height / logo.width)), Image.LANCZOS)
        ef = Image.new("RGB", (W, H), LOGO_BLACK); ef.paste(logo, ((W - logo.width) // 2, (H - logo.height) // 2 - 60))
        dd = ImageDraw.Draw(ef); fsub = font("IBMPlexMono-400.ttf", 26); sub = edl["endframe"].get("sub", "")
        text_spaced(dd, ((W - spaced_len(dd, sub, fsub, 8)) / 2, H // 2 + 250), sub, fsub, MUTED, 8)
        efa = np.asarray(ef, np.float32)
        for k in range(int(end_s * FPS)):
            a = ease(k / 6); last = img if k == 0 else last
            enc.stdin.write((last * (1 - a) + efa * a if k < 6 else efa).clip(0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()

    # ---- Untertitel + Mux
    captions(words, edl, segb, total, f"{work}/captions.ass")
    dur = ["-t", str(preview)] if preview else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/video.mp4", "-i", f"{work}/mix.wav",
                    "-vf", f"subtitles={work}/captions.ass:fontsdir={FONTS}," + edl.get("grade", GRADE),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", *dur,
                    "-movflags", "+faststart", out], check=True)
    srt = os.path.splitext(out)[0] + ".srt"
    with open(srt, "w") as fh:
        hook = {i for i, s in enumerate(edl["segments"]) if s.get("hook")}
        ws = words
        for i, w in enumerate(ws):
            t1 = ws[i + 1]["t"] if i + 1 < len(ws) else total
            st = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(x * 1000 % 1000):03d}"
            fh.write(f"{i + 1}\n{st(w['t'])} --> {st(t1)}\n{w['text']}\n\n")
    print("fertig:", out)

if __name__ == "__main__":
    main()
