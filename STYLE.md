# STYLE.md – Schnitt-Stil für meetmar Reels

**Zielstil:** Talking Head wie Reel 2 (itsmegkilgore) als Basis.
Für Passagen ohne Gesicht kommen die animierten Erklär-Karten aus Reel 1 (buildwithdarius.ai) dazu.

Grundlage: Analyse von 2 Referenz-Reels (65 s und 45 s), Bild für Bild (10 fps),
Transkript mit Wort-Zeitstempeln (Whisper) und Spektral-Analyse des Tons.
Reel 3 (`Dd6ue5FRZU2`) fehlt noch.

---

## 0. MAR-Brand (hat Vorrang vor allen Farb-/Schriftangaben unten)

Quelle: meetmar-ai.lovable.app und Logo `design/mar-logo.png`. Vorschau: `design/mar-look.png`.

| Token | Wert | Einsatz |
|---|---|---|
| Carbon | `#10100F` | dunkle Frames, Chat-Karten, Text auf hellem Grund |
| Panel / Linie | `#1C1C19` / `#343431` | MAR-Chat-Bubble, 1-px-Rahmen |
| Porzellan | `#F1EFEA` | Untertitel, Text auf dunklem Grund, Akzent-Box |
| Muted / System-Grau | `#A7A49F` / `#96939C` | Zweitzeilen, „ausgegrautes“ Akzentwort |
| Espresso | `#2A211D` | warme Schatten |
| Logo-Schwarz | `#070706` | Endframe-Hintergrund (passt nahtlos zum Logo) |

- **Schriften:** *Geist* (300/400 für Headlines, 600 für Untertitel) und *IBM Plex Mono* (Versalien, weit gesperrt) für Labels und Akzente.
- **Ecken:** fast eckig (2 px), keine runden Bubbles.
- **Hintergrund Talking Head:** „Warmes Studio“. Helles Greige mit Lichtschein hinter dem Kopf (`#E4D8C8` → `#9A8774`), leichtes Korn. Person wird freigestellt.
- **Untertitel:** Geist SemiBold, Porzellan, weicher dunkler Schatten, auf Brusthöhe (liegt auf der dunkelbraunen Kleidung → gut lesbar).
- **Akzentwörter** ersetzen das gelbe Kursiv der Referenz:
  - a) **Porzellan-Box** mit Carbon-Text in IBM Plex Mono, Versalien („DIAGNOSE“), wie der Button auf der Landingpage. Für Schlüsselbegriffe.
  - b) **ausgegrautes Wort** in der Headline („Du gibst MAR dein *ganzes* Business.“), wie „fehlt.“ auf der Landingpage.
- **Hook-Headline** auf hellem Grund: Carbon, Geist Regular, Akzentwort warmgrau `#7A6E63`.
- **Text-only-Frames** (Reel 02, Endframes): Carbon-Grund, Geist Light in Porzellan, zweite Zeile System-Grau, blinkender Cursor.
- **Kein Gelb, keine Serifenschrift.** Ruhig, reduziert, „diagnostisch“.

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

---

## 5. Effekt-Bibliothek (Referenz 3: „Just copy my reel“)

Analyse der Bildschirmaufnahme (57 s). Die Creatorin benennt jeden Effekt selbst im Voiceover.
Dabei bleibt **der echte Raum als Hintergrund**. Ersetzt wird er nur in Effekt-Momenten.

| # | Effekt (Zeit) | Was passiert | MAR-Version | Status |
|---|---|---|---|---|
| 1 | **Wasserfall** (0–4 s, 33–37 s) | Raster aus eigenen Reel-Thumbnails scrollt langsam von unten nach oben **hinter** der freigestellten Person. Dazu Hook-Titel in kursiver Serif + kleine Versal-Zeile | Wand aus **MAR-Fragekarten** („Wann hast du zuletzt …?“, „Was war der Grund?“ …) scrollt hinter dir: „MAR hat 100 Fragen, ChatGPT keine“ | ✅ baubar |
| 2 | **Claude-Chatfenster** (8–14 s) | Helle Chatkarte mittig, Link wird eingefügt, Prompt wird getippt | haben wir als MAR-Chatkarte | ✅ vorhanden |
| 3 | **Hintergrund-Farbwechsel** (15–17 s) | Raum wird durch Vollfarbe (Terrakotta) ersetzt, großes Serif-Wort „colour“ über dem Kopf | Farbwechsel auf Carbon/Espresso, Wort in Porzellan | ✅ vorhanden (Dark-Flash) |
| 4 | **Großes Wort hinter dem Kopf** (18–24 s) | „funky“ in riesiger schwarzer Kursiv-Serif, der Kopf verdeckt die Mitte. Auf Zuruf **Farbwechsel zu Pink** | „ZUSAMMENHANG“, „RÜCKFRAGE“; Farbwechsel Carbon → Warmgrau oder Durchstreichen auf Zuruf | ✅ vorhanden, Farbwechsel neu |
| 5 | **Karussell** (25–31 s) | Reihe aus Reel-Thumbnails gleitet auf Hüfthöhe **vor** der Person von rechts nach links („swipe“) | Karussell aus MAR-Fragen oder deinen bisherigen Reels | ✅ baubar |
| 6 | **Text-Fenster / Knockout** (38–46 s) | Vollfarbe mit riesigem Blocktext „JUST COPY ME“, **in den Buchstaben läuft das Video** | „MAR“ riesig auf Carbon, dein Video läuft in den Buchstaben (CTA oder Endframe) | ✅ baubar |
| 7 | **Schild in der Hand** (47–55 s) | „Open“-Schild hängt an den Fingern und folgt der Hand, auf Fingerschnippen wechselt es zu „Closed“ | Schild „BETA: OFFEN“ → „20 PLÄTZE“ oder „FRAGE“ → „DIAGNOSE“ | ⚠️ braucht Hand-Tracking. Alternative: Schild an fester Stelle, wenn du die Hand ruhig hältst |
| 8 | **Untertitel** | kleine weiße Label-Box mit dunkler Schrift, 2–3 Wörter, unteres Drittel | Alternative zu unseren großen Wort-für-Wort-Captions | ✅ als Variante |

**Was das Reel ausmacht:** Jeder Satz kündigt einen Effekt an, und er passiert genau in dem Moment, in dem er gesagt wird.
Der Inhalt *ist* die Effekt-Demo. Für MAR heißt das: Was du sagst, wird sofort sichtbar
(„MAR stellt dir Rückfragen“ → Fragen regnen hinter dir herunter).

---

## 6. Effekt-Bibliothek (Referenz 4: „Why Claude edits look the same“)

Kernaussage des Reels: KI-Schnitte sehen alle gleich aus, weil Code-Grafiken **perfekt sauber und flach** sind.
Die Lösung der Creatorin ist **Textur, Tiefe, Verspieltheit**: analoge Collage-Elemente, die wie gebastelt wirken.
→ Das gilt auch für unsere Pipeline. Unsere Karten sind Code-Grafik, also eher flach.

| # | Effekt (Zeit) | Was passiert |
|---|---|---|
| 1 | **Collage-Hook** (0–4 s) | Mischung aus kleinem Handschrift-„why“, großer gelber Serif „Claude edits“ und Schreibschrift „look the same“. Oben ein Papier-Etikett mit Mini-Foto |
| 2 | **Papier-Wortschnipsel** (3–5 s) | Wörter auf gerissenen Papierstreifen, leicht gedreht. „captions“ wird **von Hand durchgestrichen**, „effects“ kommt dazu |
| 3 | **Foto mit Klebeband** (6–8 s) | Polaroid-artiges Foto, oben mit Tape „angeklebt“ |
| 4 | **Zerknülltes Papier** (8–9 s) | Handgeschriebenes „texture“ auf echtem zerknittertem Papier |
| 5 | **Logo-Karte + Tape-Label** (9–12 s) | Karte mit App-Logos, darunter ein Klebeband-Etikett „Claude + HyperFrames“ |
| 6 | **Code-Monitor + Sticker** (13–19 s) | Retro-Bildschirm, Code wird getippt. Rote Etiketten „PERFECTLY clean / flat“, Kritzel-Kreise und Glitzer. Bei „flat“ wird das Bild **schwarz-weiß** |
| 7 | **Handschrift groß über dem Kopf** (19–21 s) | „But I have a fix for that…“ in gelbem Pinselstift |
| 8 | **Notizzettel** (21–25 s) | Gerissenes Linienpapier mit handschriftlicher Liste, Punkte erscheinen nacheinander |
| 9 | **Erpresserbrief-Wort + Sticker** (25–29 s) | „texture“, „dimension“ als Papier-Labels, „whimsy“ aus ausgeschnittenen Einzelbuchstaben, Stern-Sticker |
| 10 | **Pinnwand-Vollbild** (29–34 s) | Kork-Hintergrund, gelber Notizblock mit Schritten 1–4 (Nummern in Stern-Stickern). Die Creatorin klein als **runder Ausschnitt** unten |
| 11 | **App-Screenshot im Rahmen** (35–44 s) | Screenshot ihrer Web-App über ihr, Tape-Label mit Schrittnummer. Rote Labels „raw footage / vision / script“ ploppen auf, „!!“-Kritzel |
| 12 | **Untertitel** | einzelnes Wort, klein, weiß, kursiv, **links** auf Brusthöhe, sehr dezent |

**Rhythmus:** Etwa alle 2 Sekunden kommt ein neues Collage-Element, das Gesicht bleibt immer frei.

### Übertragung auf MAR: „Diagnose-Akte“ statt Bastel-Collage
Die verspielte Bastel-Optik (Pink, Glitzer, Sterne) passt nicht zur ruhigen MAR-Marke.
Die **Idee „Textur statt flach“** lässt sich aber in eine passende Welt übersetzen: **Befund und Akte**.
- Karten als **bedrucktes Papier** (leichte Papierstruktur, Schatten, minimal gedreht) statt flacher Rechtecke
- **Stempel** („DIAGNOSE“, „BEFUND“, „RÜCKFRAGE“) mit Druckfarbe und leicht unregelmäßigem Abdruck
- **Klebeband und Büroklammer** halten Karten fest, in Porzellan/Warmgrau
- **Handschriftliche Randnotizen** und Kringel in Graphit, z. B. ein Kreis um „SALES 41“ mit „wirklich?“
- **Befundbogen** als Vollbild: Business-Health-Werte wie ein Laborbericht auf Papier
- **Dich als runder Ausschnitt** auf der Akte bei Erklär-Passagen
- **Schwarz-Weiß-Moment** bei „flach/falsch“-Aussagen (z. B. „ChatGPT beantwortet nur, was du fragst“)

---

## 7. Effekt-Katalog (Referenzen 5 + 6: „16 video effects Claude can create“, 2 Teile)

Legende: ✅ mit der Pipeline baubar · ⚠️ nur angenähert · ⭐ passt besonders zu MAR

### Hinter / um die Person (Freistellung nötig, haben wir)
| Effekt | Was passiert | Status | MAR-Einsatz |
|---|---|---|---|
| **Cover Story** ⭐ | Magazin-Titel riesig hinter dem Kopf („EDIT“), Kopf überdeckt Buchstaben | ✅ | „MAR“ oder Folgen-Titel als Masthead in Geist Light, für große Folgen-Hooks |
| **Scene Text** | Großes Wort wirkt „auf die Wand gemalt“ hinter der Person | ✅ | „PROBLEM?“ (haben wir), „FRAGE“ |
| **Type Wall** ⭐ | Wand aus wiederholten Textzeilen hinter der Person („EVERYBODY'S…“) | ✅ | „POSTEN POSTEN POSTEN …“ bei „Mehr Content ist nicht die Lösung“ |
| **Headline Wall** ⭐ | Wand aus Zetteln und Schlagzeilen hinter der Person | ✅ | Kommentare und Fragen der Community (Tag 7), Fragen-Wasserfall statisch |
| **Couch Wall** | Raster aus eigenen Reel-Thumbnails hinter der Person | ✅ | später, wenn es genug eigene Folgen gibt („30 Tage MAR“) |
| **Chart Grow** ⭐ | Linien-Chart wächst hinter der Person, Label „SCALE ↗“ | ✅ | Re-Analyse: „So sieht Fortschritt aus“, Business-Health-Werte steigen |
| **Depth Scatter** | Wörter schweben in verschiedenen Tiefen um die Person, mit Bokeh | ✅ | Schlagworte „Strategie · Positionierung · Sales“ verteilt im Raum |
| **Spotlight / Blackout** | Hintergrund wird schwarz, Lichtkegel auf Person, Wort teils hinter, teils vor ihr („stand“ hinter, „out“ vor) | ✅ | stärkster Moment einer Folge, max. 1× pro Folge |
| **Vertigo** ⭐ | Dolly-Zoom: Hintergrund zoomt, Person bleibt gleich groß | ✅ | Aha-Moment („Und dann hab ich gemerkt …“) |
| **Rack Focus** | Schärfe wandert vom Hintergrund zur Person, Serif-Wort taucht auf | ✅ | ruhige, persönliche Momente (Tag 3) |
| **Clone** ⭐ | Person mehrfach nebeneinander | ✅ | „Ich bin Gründerin, Entwicklerin, Marketing und Support gleichzeitig“ |

### Karten / UI im Bild
| Effekt | Was passiert | Status | MAR-Einsatz |
|---|---|---|---|
| **Checklist** ⭐ | Karte „ALL YOU NEED TO DO · 0 of 3“, Punkte haken sich beim Sprechen ab | ✅ | Tag 2: die 3 Fragen haken sich ab |
| **Promptbox** ⭐ | Eingabefeld schwebt im Raum, Text wird getippt | ✅ | Jemand tippt „Wie bekomme ich mehr Kundinnen?“ → MAR antwortet mit Gegenfrage |
| **UI World** | Chat-Fenster oben, Clips fliegen hinein, Label „RAW CLIPS“ | ✅ | MAR-Chat bei Info-Folgen |
| **Phone Mockup** ⭐ | Handy erscheint neben dem Kopf mit App-Screen | ✅ | MAR-Oberfläche zeigen (Tag 5), braucht Screenshots |
| **Spatial Glass** | Milchglas-Panels (wie Apple Vision) schweben neben der Person | ✅ | elegante MAR-Info-Karten |
| **The Stack** | UI-Karte und Video-Karte stapeln sich | ✅ | „Ehrliche Wahrheit über …“-Liste |
| **Chip Row** ⭐ | Reihe von Pills/Tags am unteren Rand | ✅ | MAR-Bereiche: STRATEGIE · POSITIONIERUNG · SALES · FINANZEN |
| **Greenscreen** | Person freigestellt vor App-Screenshot | ✅ | MAR-Dashboard als Hintergrund (Tag 5) |
| **Pullback Reveal** ⭐ | Video schrumpft zurück und entpuppt sich als Fenster in einer App | ✅ | Ende einer Info-Folge: „…und das alles passiert hier drin“ → MAR-UI |

### Freeze, Sticker, Annotation
| Effekt | Was passiert | Status | MAR-Einsatz |
|---|---|---|---|
| **Freeze Sticker** ⭐ | Bild friert ein, Person wird zum Sticker mit weißem Rand auf Farbfläche, Badge „CERTIFIED“, Handschrift „NOT a tech bro“ | ✅ | Signatur-Satz Tag 1: Sticker „MARINA · BAUT MAR“, Notiz „keine Tech-Frau“ |
| **Freeze Label** ⭐ | Standbild mit Beschriftungen und Linien zur Person („sucks at design“) | ✅ | Selbstironie: „hat 0 Ahnung von Code“ · „stellt zu viele Fragen“ |
| **Sticky Text** | Etikett klebt neben dem Kopf und bewegt sich mit | ⚠️ (Kopfposition über Freistellung) | Rollen-Label „GRÜNDERIN“ |
| **Doodle Box** ⭐ | Handgezeichnete weiße Linie umrandet die Person, Kritzel | ✅ (aus der Freistellungs-Kontur) | passt zum Papier-Look, für lockere Momente |
| **Paper Cut** | Collage mit Kritzeln, Papier, Ziffern-Stickern „100%“ | ✅ | Zahlen-Momente („100 % Bauchgefühl“) |

### Übergänge und Typo
| Effekt | Was passiert | Status | MAR-Einsatz |
|---|---|---|---|
| **Digital Zoom** | Schneller Zoom auf das Gesicht + zweifarbige Riesen-Caption | ✅ | Punch-ins mit Akzentwort |
| **Zoom Through Cut** | Mit Bewegungsunschärfe in die nächste Szene „durchzoomen“ | ✅ | Wechsel Hook → Inhalt |
| **Frame Break** | Video wird zum Handy-Rahmen mit IG-Oberfläche | ✅ | „So sieht es bei dir im Feed aus“ |
| **Serif Flow** ⭐ | Schwarzer Screen, elegante Typo „five variations / edits + posts“ | ✅ | = unser Text-Frame-Stil, als Zwischentitel („SEGMENT · DIE FALSCHE FRAGE“) |
| **Shattered 3D** | Bild zerspringt in schwebende Scherben | ⚠️ | eher nicht (zu verspielt) |
| **Glass Type** | 3D-Glasschrift mit Lichtbrechung | ⚠️ | eher nicht |

**Regel für MAR:** pro Folge **max. 2–3 Effekte**, einer davon darf ein „großer“ sein (Blackout, Vertigo, Clone, Freeze).
Effekte immer **an den Satz koppeln**, der sie auslöst. Nie Effekt um des Effekts willen.
