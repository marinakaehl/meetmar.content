# CLAUDE.md – Content-Studio für @meetmar.ai

Lies vor jeder Content-Arbeit (Skripte, Beschreibungen, Cover, Schnitt):
1. `BRAND.md`: Marinas Marke, Versprechen, Hero Story, Haltung, Feindbild, Sprache, Freigaben. **Lebendige Datengrundlage**: Neue Infos von Marina hier eintragen und im Logbuch vermerken.
2. `STYLE.md`: Look, Farben, Schriften, Effekt-Bibliothek.
3. `FAELLE.md`: Fall-Bank (echte Fälle nur anonym und mit Einverständnis, sonst „NACHGESTELLT“).
4. Aktueller Wochenplan (`WOCHE-*.md`, `TAG-*.md`) und `marktanalyse/` (Branch `claude/gallant-lovelace-ppq85e`).

Regeln:
- **Marina ist in jeder Folge ab Bild 1 im Bild** (Text-/Chat-only-Reels liefen mit ~30 Aufrufen deutlich schlechter). Chats und Karten nur noch als Effekt über ihr.
- **Längen (hart, immer prüfen bevor gerendert wird):** große Folge / ToFu max. **40 s** · kleine Folge 15–25 s · Chat-Reveal 15–25 s. Lieber einen Gedanken streichen als überziehen.
- **Kommentar-Aufruf „Kommentiere MAR“** darf in mehreren Folgen pro Woche vorkommen (Marina testet das, ManyChat wird eingerichtet).
- Skripte nach AGIL (Anker, Grund/Geschichte, Illustration, Lektion). Hook mit Person, Zahl oder Konflikt, Text ab Bild 1.
- Beschreibungen: erste Zeile < 80 Zeichen, macht neugierig, **wiederholt nicht das Reel**, bringt Meinung + Übung.
- Die Academy, mit der Marina arbeitet, nie namentlich nennen. Keine Kundinnen-Namen.
- Schnitt: `tools/reel.py` (Talking Head), `tools/chatreel.py` (Chat-Reveal), `tools/cover.py` (Cover).
