# tools/ – Reel-Pipeline

## Einmalig einrichten
```bash
pip install faster-whisper onnxruntime huggingface_hub pillow numpy
```
ffmpeg (mit libass) muss installiert sein. Schriften liegen in `design/fonts/`.

## Ablauf pro Reel
1. Rohvideos nach `raw/<reel>/` legen (nicht im Git, siehe `.gitignore`).
2. Transkript mit Wort-Zeitstempeln erzeugen:
   ```bash
   python3 tools/transcribe.py raw/<reel>/*.mp4 --out reels/<reel>/
   ```
3. `reels/<reel>/edl.json` schreiben: Welche Sätze aus welchem Take, Akzentwörter, Hook-Headline, Karten.
4. Rendern:
   ```bash
   python3 tools/reel.py reels/<reel>/edl.json out/<reel>.mp4            # komplett
   python3 tools/reel.py reels/<reel>/edl.json out/<reel>.mp4 --preview 8 # nur die ersten 8 s
   ```

## Was `reel.py` macht
- Pausen und Atmer per Energie-Erkennung rausschneiden, Wortanfänge bleiben geschützt.
- Lange Passagen an Satzzeichen teilen und zwischen Zoomstufen 110/124/136 % wechseln (Punch-ins).
- Person freistellen (MODNet) und Hintergrund „Warmes Studio“ einsetzen.
- Hook-Headline (Geist, Akzentwort warmgrau) liegt hinter der Person.
- Brand-Karten: MAR-Chat mit Tipp-Animation, durchgestrichenes Wort, Schritte, CTA-Button.
- Wort-für-Wort-Untertitel (Geist SemiBold), Akzentwörter als Porzellan-Box in IBM Plex Mono.
- Soundeffekte (Pop, Tippen, Whoosh, Strich, Hit) synthetisch auf die Einblendungen.
- Stimme: Hochpass, Rauschfilter, Kompressor, −14 LUFS.
- Endframe mit Logo, plus `.srt`-Untertiteldatei.
