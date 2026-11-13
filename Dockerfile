FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY vnb ./vnb
COPY ergebnis/conplot ./ergebnis/conplot
COPY ergebnis/netzentgelte_2026.csv ./ergebnis/netzentgelte_2026.csv
COPY ergebnis/umlagen_steuern_2026.csv ./ergebnis/umlagen_steuern_2026.csv
COPY lauf/hlzf_zusammen.csv ./lauf/hlzf_zusammen.csv
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
