# Nutzt das offizielle, schlanke Python-Image als Basis
FROM python:3.11-slim

# Setzt das Arbeitsverzeichnis innerhalb des Containers
WORKDIR /app

# Kopiert die Liste der Abhängigkeiten (Library-Liste) in den Container
COPY requirements.txt .

# Installiert die Python-Bibliotheken ohne Cache (spart Speicherplatz)
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert den gesamten Projektcode vom Mac in den Container
COPY . .

# Dokumentiert, dass die App auf Port 8001 lauscht
EXPOSE 8001

# Der Befehl, der den Server beim Start des Containers ausführt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]