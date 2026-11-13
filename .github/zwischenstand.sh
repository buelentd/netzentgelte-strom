#!/bin/bash
# Zwischenstände während eines laufenden Crawler-Laufs sichern (Wunsch Nutzer 13.11.2026: Ergebnisse sollen vor dem Ende des Laufs verfügbar sein).
# Alle 8 Minuten werden die Ergebnisdateien in einen SEPARATEN frischen Klon kopiert, dort committet und gepusht.
# Das Arbeitsverzeichnis des Laufs wird dabei nicht angefasst.
JAHR="${1:-2027}"
DATEIEN=("ergebnis_${JAHR}/netzentgelte_${JAHR}.csv" "ergebnis_${JAHR}/restliste.csv" "ergebnis_${JAHR}/fortschritt.jsonl" "ergebnis_${JAHR}/zusammenfassung.md"
         "ergebnis/netzentgelte_${JAHR}.csv" ergebnis/restliste.csv ergebnis/fortschritt.jsonl ergebnis/zusammenfassung.md lauf/suche_erledigt.csv)
while true; do
  sleep 480
  T="$(mktemp -d)"
  if git clone -q --depth 1 --branch "$GITHUB_REF_NAME" "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "$T/r" 2>/dev/null; then
    for f in "${DATEIEN[@]}"; do
      if [ -e "$f" ]; then mkdir -p "$T/r/$(dirname "$f")"; cp -r "$f" "$T/r/$f"; fi
    done
    (
      cd "$T/r" || exit 0
      git add -A
      if ! git diff --cached --quiet; then
        git -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
            commit -q -m "Netzentgelte ${JAHR}: Zwischenstand (Lauf ${GITHUB_RUN_ID})"
        for i in 1 2 3; do
          git pull -q --rebase -X theirs origin "$GITHUB_REF_NAME" && git push -q origin "HEAD:$GITHUB_REF_NAME" && break
          sleep $((2 ** i))
        done
      fi
    )
  fi
  rm -rf "$T"
done
