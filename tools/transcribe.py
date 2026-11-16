#!/usr/bin/env python3
"""Deutsches Transkript mit Wort-Zeitstempeln: python3 tools/transcribe.py VIDEO... --out DIR"""
import json, os, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

args = sys.argv[1:]; out = args[args.index("--out") + 1] if "--out" in args else "."
vids = [a for a in args if a.endswith((".mp4", ".mov", ".MOV", ".m4a", ".wav"))]
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
os.makedirs(out, exist_ok=True)
for v in vids:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    segs, _ = m.transcribe(a, language="de", word_timestamps=True,
                           initial_prompt="MAR ist eine Business-Diagnostik-KI. ChatGPT, Founding 20, Sales-Problem.")
    words = [[round(w.start, 2), round(w.end, 2), w.word.strip(), round(w.probability, 2)] for s in segs for w in s.words]
    p = os.path.join(out, os.path.splitext(os.path.basename(v))[0] + "_words.json")
    json.dump(words, open(p, "w"), ensure_ascii=False)
    print(p); print(" ".join(f"[{w[0]:.1f}]{w[2]}" for w in words))
