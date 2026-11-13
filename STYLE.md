# STYLE.md – Schnitt-Stil für meetmar Reels

**Zielstil:** Talking Head wie Reel 2 (itsmegkilgore) als Basis.
Für Passagen ohne Gesicht kommen die animierten Erklär-Karten aus Reel 1 (buildwithdarius.ai) dazu.

Grundlage: Analyse von 2 Referenz-Reels (65 s und 45 s), Bild für Bild (10 fps),
Transkript mit Wort-Zeitstempeln (Whisper) und Spektral-Analyse des Tons.
Reel 3 (`Dd6ue5FRZU2`) fehlt noch.

---

## 1. Messwerte aus den Referenzen

| | Reel 1 – Animation (darius) | Reel 2 – Talking Head (meg) |
|---|---|---|
| Länge | 65 s | 45 s |
| Sprechtempo nach dem Schnitt | **174 Wörter/min** | **221 Wörter/min** (sehr schnell) |
| Längste Pause | 2,3 s (bewusst, für Wirkung) | **0,54 s**, praktisch keine Pausen |
| Pausen über 0,3 s | 36 | 14 |
| Harte Bildschnitte | **keine** (alles ist Animation) | **alle 1–2,5 s** |
| Ton zwischen Sätzen | **digitale Stille** (Pausen hart ausgeschnitten, keine Musik) | **nie still**: durchgehend leiser Klangteppich bzw. Musik unter der Stimme |
| Soundeffekte | keine hörbar | ja, kurze helle „Pop/Whoosh/Sparkle“-Transienten **genau auf Grafik-Einblendungen** (≈2–5 s Hook, 7,8 s, 15 s, 18 s, 25,5 s, 28 s, 41,6 s) |
| Untertitel | 2–3 Wörter, aktives Wort farbig | **1 Wort**, groß, mittig |

---

## 2. Zielstil im Detail

### 2.1 Hook (0–3 s)
- Starte **mitten im Satz** mit dem stärksten Statement, ohne Begrüßung.
- Große mehrzeilige Headline (3–4 Zeilen) über dem Bild. Die Zeilen bauen sich **Wort für Wort** synchron zur Stimme auf.
- **Text hinter der Person:** Die Headline liegt *hinter* Kopf und Händen (Person freigestellt, Text dazwischen). Das ist das auffälligste Effekt-Signal in Reel 2.
- Schlüsselwörter der Headline im **Akzent-Stil** (siehe 2.3), Rest in Weiß.
- Schon in den ersten 2 s ein schwebendes Overlay (Screenshot oder Thumbnail, leicht gedreht, mit Schatten) als visueller Beweis.

### 2.2 Schnitt
- **Jede Pause über ~0,15 s und jedes Füllwort raus** („ähm“, „also“, Atmer). Zielwert: über 200 Wörter/min.
- Harter Schnitt alle **1–2,5 s**.
- **Abwechselnde Einstellungen** (aus *einem* Take erzeugt):
  - normal (100 %), **Punch-in** (115–125 %, auf das Gesicht zentriert), gelegentlich weiter Ausschnitt.
  - Wechsel auf jedem Jump-Cut, damit kein Schnitt „springt“.
- Wenn möglich, Takes mit **echten Perspektivwechseln** drehen: Sofa-Totale, nach vorne gelehnt, Selfie aus der Hand (Untersicht). Reel 2 schneidet zwischen 4 Setups.
- **Blitz-Montage** als Beweis-Moment (Reel 2, 23–25 s): Thumbnails eigener Posts füllen in **0,1-s-Schritten** ein Raster um die Person.

### 2.3 Untertitel (Markenzeichen)
- **Ein Wort auf einmal**, mittig auf Brust-/Gesichtshöhe. Satzzeichen bleiben dran („fine.“, „camera?“).
- **Standard:** weiße, fette Sans-Serif, kleingeschrieben, weicher Schatten.
  Font-Vorschlag: *Inter ExtraBold* oder *Poppins SemiBold*.
- **Akzent** (≈ jedes 6.–10. Wort, Pointe oder Schlüsselbegriff): **gelb/creme (`#F3E27A`), kursive Serifenschrift**, etwas größer.
  Font-Vorschlag: *Instrument Serif Italic* oder *Playfair Display Italic*.
- **Flüster-/Nebensatz-Caption:** klein und dezent („no, seriously.“) für ironische Einschübe.
- **Handschrift-Notiz** mit gezeichnetem Pfeil für Selbstironie („i’m literally just a mom →“).
  Font-Vorschlag: *Caveat* oder *Gochi Hand*.
- Einblendung: kurzes Pop (Scale 85 %→100 % in ~80 ms), kein Fade.

### 2.4 Overlays und B-Roll (zu jeder Aussage ein Bild)
- **Schwebende Karten**: Screenshots, Thumbnails, App-UI. Leicht gedreht (±5°), abgerundete Ecken, weicher Schatten, „fliegen“ mit Federung ein.
- **Mac-UI-Karten** zur Erklärung: Ordner „my clips“, CapCut-Timeline, Schrift-/Farbwähler „your look“.
- **Collage-Raster** aus eigenen Posts mit View-Zahlen als Social Proof.
- Wörtlich illustrieren: Wer „b-roll“ sagt, zeigt B-Roll. Wer „custom animation“ sagt, zeigt eine Animation.

### 2.5 Passagen ohne Gesicht (aus Reel 1)
Wenn du nicht vor der Kamera sein willst oder ein Ablauf erklärt wird:
- Hintergrund: Creme/Off-White mit Papier-Textur und Vignette.
- Titel in **Serifenschrift**, ein kursives Akzentwort in der Akzentfarbe („Prepare your *footage*“).
- Label `STEP 1 … 7` plus **Fortschrittsbalken** oben (Segmente füllen sich).
- UI-Karten (Terminal, Datei, Toggles, App-Icons) mit **Tipp-Animation**, Häkchen und roten X.
- Sticker-Bubbles schräg an den Karten („What’s Apify?“, „Use mine“).
- Untertitel hier: 2–3 Wörter, aktives Wort in Akzentfarbe (Karaoke).
- Abschluss-Karte: großes kursives „*Speichern.*“ plus Lesezeichen-Icon.

### 2.6 Sound
- **Stimme:** Rauschen entfernen, leichte Kompression, Lautheit **−14 LUFS**, Spitzen maximal −1 dB.
- **Musik:** leiser Teppich (lo-fi/soft pop) **unter** der Stimme, automatisch abgesenkt, sobald gesprochen wird (Ducking, etwa −20 dB unter der Stimme). In Pausen nie komplett still.
- **Soundeffekte**, sparsam und nur auf visuelle Ereignisse:
  - *Pop*: Untertitel im Akzent-Stil, Sticker, Häkchen.
  - *Whoosh*: Karte oder Overlay fliegt ein, Szenenwechsel.
  - *Klick/Tippen*: Tipp-Animation, UI-Toggles.
  - *Sparkle/Ding*: „Magie“-Momente („custom animation“, Ergebnis-Reveal).
  - *Schnelles Ticken*: unter der Blitz-Montage.
- SFX deutlich leiser als die Stimme (etwa −12 dB).

### 2.7 Look
- Natürliches Fensterlicht, warme Wohnräume.
- Leicht warmes Grading, Kontrast minimal anheben, Sättigung neutral. Kein starker Filter.

### 2.8 Ende und CTA
- Nahe, direkte Ansprache (Selfie-Einstellung).
- **Kommentar-Keyword-CTA**: „Kommentiere *XYZ* und ich schick dir …“, Keyword als Akzent-Caption.
- Optional der Loop-Trick: Der letzte Satz führt zurück auf den ersten („…und das Reel, das du gerade siehst, hat Claude geschnitten“).

### 2.9 Export
- 1080×1920, H.264, 30 fps, AAC 48 kHz. Wichtige Inhalte nicht in die unteren ~20 % und rechten ~15 % legen (Instagram-UI).

---

## 3. Was Claude davon automatisch umsetzen kann

| Effekt | Umsetzbar | Wie |
|---|---|---|
| Pausen und Füllwörter rausschneiden | ✅ | Whisper-Wort-Zeitstempel → ffmpeg-Schnittliste |
| Wort-für-Wort-Untertitel, 2 Schriften, Pop-Animation | ✅ | ASS-Untertitel (libass), Google Fonts |
| Punch-in-Zooms im Wechsel | ✅ | ffmpeg crop/scale pro Segment |
| Hook-Headline, Wort-für-Wort-Aufbau | ✅ | ASS/Overlay |
| **Text hinter der Person** | ✅ (rechenintensiv) | Personen-Freistellung (KI-Segmentierung) pro Frame, Text dazwischen |
| Schwebende Karten, Screenshots, Collage, Blitz-Montage | ✅ | ffmpeg overlay plus Pillow (Schatten, Rotation, Ecken) |
| Animierte UI-Karten, Fortschrittsbalken, Tipp-Animation (Reel-1-Teil) | ✅ | HTML-Animation, gerendert mit Headless-Chromium |
| Handschrift-Notiz mit Pfeil | ✅ | Handschrift-Font plus Pfeil-Grafik |
| Musik-Ducking, Lautheit −14 LUFS, Rauschfilter | ✅ | ffmpeg sidechaincompress, loudnorm, afftdn |
| Soundeffekte auf Einblendungen | ✅ | automatisch auf die Overlay-Zeitpunkte gelegt. Eigene Sound-Pack-Dateien sind besser, Notlösung: synthetische Pops/Whooshes |
| Farblook | ✅ | ffmpeg eq/colorbalance oder LUT-Datei |
| Musik auswählen | ⚠️ | Du lieferst lizenzfreie Tracks (z. B. aus der Instagram-Audiothek nachträglich in der App oder als MP3) |
| KI-generierte Bilder/Videos (Higgsfield o. Ä.) | ⚠️ | nur mit eigenem Account bzw. API-Key |
| Als bearbeitbares CapCut-Projekt öffnen | ❌ | Claude liefert die fertige MP4 plus Untertiteldatei (SRT), nicht das CapCut-Projekt |

---

## 4. Arbeitsablauf
1. Rohvideos (auch mehrere Takes), optional Screenshots/B-Roll und Musik in `raw/<videoname>/` legen.
   Für GitHub-Upload unter 25 MB pro Datei bleiben (720p reicht für Tests).
2. Claude sagen: „Schneide `raw/<videoname>` nach STYLE.md.“
3. Claude transkribiert, schneidet, setzt Untertitel und Effekte und legt die Datei in `out/<videoname>.mp4` ab, dazu eine Untertitel-Datei.
4. Änderungen einfach beschreiben („Hook kürzer“, „mehr Zooms“, „anderes Akzentwort“).
