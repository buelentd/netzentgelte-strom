# API auf einem eigenen Server

Ein kleiner Linux-Server (1 GB RAM reicht) mit Docker, eine Domain, die auf den Server zeigt.

```bash
git clone https://github.com/buelentd/netzentgelte-strom && cd netzentgelte-strom/deploy
cp .env.beispiel .env        # Schlüssel setzen (langer Zufallswert)
# Caddyfile: api.DEINE-DOMAIN.de eintragen
docker compose up -d --build
```
Danach: `https://api.DEINE-DOMAIN.de/docs` (Swagger), `/openapi.json`. Aufrufe mit Header `X-API-Key`.
Datenstand aktualisieren: `git pull && docker compose up -d --build`.
Nicht hinterlegt: der Fallback `ergebnis/hlzf_fallback.csv` (noch nicht an die API angebunden).
