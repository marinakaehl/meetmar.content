#!/usr/bin/env bash
# Lädt alle Videos aus einem öffentlich geteilten Google-Drive-Ordner in Originalqualität.
# Aufruf: tools/drive_pull.sh <ORDNER-LINK> <ZIELORDNER>
set -euo pipefail
url="$1"; out="$2"; mkdir -p "$out"
python3 -m gdown --folder "$url" --json 2>/dev/null | python3 -c '
import json,sys
for f in json.load(sys.stdin): print(f["url"].split("id=")[1], f["path"])' | while read -r id name; do
  [ -f "$out/$name" ] && { echo "schon da: $name"; continue; }
  curl -sS -L -o "$out/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  echo "geladen: $name"
done
