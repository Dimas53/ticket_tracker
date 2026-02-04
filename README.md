# 🎫 Ticket Tracker - Vollständige Dokumentation

Professioneller Ticket-Tracker mit FastAPI, SQLite, JWT-Authentifizierung und modernem Web-Interface.

## 📋 Inhaltsverzeichnis

- [Projektübersicht](#-projektübersicht)
- [Git Flow](#-git-flow)
- [Schnellstart](#-schnellstart)
- [Projektstruktur](#-projektstruktur)
- [Authentifizierung](#-authentifizierung)
- [API Endpoints](#-api-endpoints)
- [Web-Interface](#-web-interface)
- [Tests](#-tests)
- [Datenbank](#-datenbank)
- [Roadmap](#-roadmap)

---

## 🎯 Projektübersicht

Ein vollständiges Ticket-Management-System mit:

- **Backend:** FastAPI mit SQLAlchemy ORM
- **Authentifizierung:** JWT-Tokens mit bcrypt Password-Hashing
- **Rollen-System:** User und Admin mit unterschiedlichen Berechtigungen
- **Frontend:** Responsives Web-Interface mit Dark/Light Theme
- **Datenbank:** SQLite mit User-Ticket Beziehungen
- **Tests:** pytest Integration

---

## 🛠️ Git Flow

Das Projekt folgt einer standardisierten Branching-Strategie:

- **`main`**: Stabile Version (v1.0). Enthält den produktionsreifen Code.
- **`dev`**: Der zentrale Integrations-Branch. Alle neuen Features werden hier zuerst für Tests zusammengeführt.
- **`feature/*`**: Temporäre Branches für spezifische Aufgaben (z. B. `feature/user-auth`). Nach Abschluss werden sie in den `dev`-Branch gemergt.

---

## 🚀 Schnellstart

### 1. Repository klonen (falls noch nicht geschehen)

```bash
git clone <repository-url>
cd ticket-tracker
```

### 2. Abhängigkeiten installieren

```bash
# Virtuelles Environment erstellen (empfohlen)
python3 -m venv .venv

# Environment aktivieren
source .venv/bin/activate  # macOS/Linux
# oder
.venv\Scripts\activate     # Windows

# Alle Abhängigkeiten installieren
pip install -r requirements.txt
```

### 3. Server starten

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Server läuft auf: **http://127.0.0.1:8001**

---

## 📁 Projektstruktur

```
ticket-tracker/
├── frontend/               # 🌐 Web-Interface
│   ├── index.html         # Hauptseite
│   ├── app.js             # Frontend-Logik
│   └── styles.css         # Styling (Dark/Light Theme)
│
├── auth.py                # 🔐 Authentifizierungs-Logik
├── database.py            # 💾 Datenbank-Konfiguration
├── models.py              # 📊 SQLAlchemy Modelle (UserDB, TicketDB)
├── schemas.py             # 📝 Pydantic Schemas (Validierung)
├── main.py                # 🖥️ FastAPI Server (Hauptdatei)
│
├── client.py              # 🧪 Python Test-Client
├── test_api.py            # ✅ pytest Tests
│
├── requirements.txt       # 📦 Python-Abhängigkeiten
├── tickets.db             # 💾 SQLite Datenbank (wird automatisch erstellt)
└── README.md              # 📖 Diese Datei
```

---

## 🔐 Authentifizierung

Das System verwendet **JWT (JSON Web Tokens)** für sichere Authentifizierung.

### Sicherheits-Features

- **Password Hashing:** bcrypt_sha256 (durch `passlib`)
- **Token-Lebensdauer:** 60 Minuten
- **Algorithmus:** HS256
- **Protected Endpoints:** Alle DELETE-Operationen erfordern Login

### User-Rollen

| Rolle   | Berechtigungen                                          |
|---------|---------------------------------------------------------|
| `user`  | Tickets anzeigen, erstellen, eigene Tickets bearbeiten |
| `admin` | Alle User-Rechte + "Danger Zone" (alle Tickets löschen)|

### Registrierung

**Admin-Account erstellen:**
```bash
# Username MUSS mit "admin_" beginnen
POST /register
{
  "username": "admin_hans",
  "password": "dein_passwort"
}
```

**Standard-User erstellen:**
```bash
POST /register
{
  "username": "maria",
  "password": "dein_passwort"
}
```

### Login

```bash
POST /token
Form-Data:
  username: admin_hans
  password: dein_passwort

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Token verwenden

```bash
# In HTTP Header:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🔌 API Endpoints

### 🔐 Authentifizierung

| Methode | Endpoint     | Beschreibung                    | Auth |
|---------|--------------|----------------------------------|------|
| `POST`  | `/register`  | Neuen User registrieren          | ❌   |
| `POST`  | `/token`     | Login (JWT-Token erhalten)       | ❌   |
| `GET`   | `/users`     | Alle User anzeigen (Debug)       | ❌   |

### 🎫 Tickets

| Methode  | Endpoint          | Beschreibung            | Auth          |
|----------|-------------------|-------------------------|---------------|
| `POST`   | `/tickets`        | Neues Ticket erstellen  | ❌            |
| `GET`    | `/tickets`        | Alle Tickets abrufen    | ❌            |
| `GET`    | `/tickets/{id}`   | Ticket nach ID abrufen  | ❌            |
| `PUT`    | `/tickets/{id}`   | Ticket aktualisieren    | ❌            |
| `DELETE` | `/tickets/{id}`   | Ticket löschen          | ✅ (erforderlich) |
| `DELETE` | `/tickets`        | 🚨 **ALLE** Tickets löschen | ✅ (nur Admin) |

### Ticket-Datenstruktur

```json
{
  "id": 1,
  "title": "Login-Bug beheben",
  "description": "Benutzer kann sich nicht mit korrektem Passwort anmelden",
  "status": "open",           // "open" | "in_progress" | "done"
  "priority": "high",         // "low" | "normal" | "high"
  "assignee": "Dima",
  "owner_id": 1               // ForeignKey zu User (wird später genutzt)
}
```

---

## 🌐 Web-Interface

### Zugriff

**Öffne im Browser:** http://127.0.0.1:8001/ui/index.html

### Features

#### ✨ Design
- **Dark/Light Theme** (Speicherung in localStorage)
- Responsive Grid-Layout
- Animierte Karten und Hover-Effekte
- Farbcodierte Status & Priority Badges

#### 🎯 Funktionen
- **Ticket-Übersicht:** Top 6 neueste Tickets als Karten
- **Vollständige Tabelle:** Alle Tickets mit Sortierung
- **Live-Bearbeitung:** Klick auf Ticket → sofort editierbar
- **Status-Tracking:** `open` (gelb) → `in_progress` (blau) → `done` (grün)
- **Smart Form:** Automatische ID-Vergabe für neue Tickets

#### 🎨 Theme-System

```javascript
// Theme wechseln (Button in der Header-Leiste)
localStorage.setItem("theme", "dark");  // oder "light"
```

---

## 🌐 Web-Interface Updates 

### 🔐 Authentifizierungs-System (Frontend)

Das Interface verfügt nun über ein integriertes Login- und Registrierungs-System, das direkt mit dem JWT-Backend kommuniziert.

- **Dynamische Formulare:** Ein Umschalter ermöglicht den nahtlosen Wechsel zwischen *Anmelden* und *Registrieren* direkt im UI.
- **Session-Management:** Nach dem Login wird der JWT-Token sicher im `localStorage` gespeichert, um autorisierte API-Anfragen zu ermöglichen.
- **Automatischer Logout:** Bei einem abgelaufenen Token (401 Unauthorized) führt das System den Benutzer automatisch zum Login-Overlay zurück.
- **Persistente Benutzeranzeige:** Der Name des angemeldeten Benutzers (z. B. `👤 admin_dima`) wird dauerhaft im Header angezeigt und bleibt auch nach einem Seiten-Refresh (F5) erhalten.

### 🎨 Erweitertes Design & Theme-Logik

Das CSS wurde optimiert, um eine konsistente Benutzererfahrung in beiden Themes zu gewährleisten:

- **Intelligente Tabellen-Hervorhebung:**
  - Im **Dark Theme**: Ausgewählte Tickets werden mit hellem Text und blauem Hintergrund hervorgehoben.
  - Im **Light Theme**: Die Schriftfarbe wechselt bei Auswahl automatisch auf Dunkelblau/Schwarz (`#1e293b`), um die Lesbarkeit auf dem hellblauen Hintergrund zu garantieren.
- **Status-Badges:** Die Farbcodierung für `open` (gelb), `in_progress` (blau) und `done` (grün) ist in beiden Modi kontraststark optimiert.

### 🛠️ Frontend-Logik (app.js)

Die wichtigsten heute implementierten Funktionen für den stabilen Betrieb:

| Funktion | Beschreibung |
|:---------|:-------------|
| `restoreUserDisplay()` | Stellt den Benutzernamen aus dem Speicher wieder her, damit er nach einem Refresh nicht verschwindet. |
| `authForm.onsubmit` | Verarbeitet Login/Register, speichert den Token und aktiviert die App-Ansicht. |
| `renderTable()` | Enthält die Logik für die visuelle Auswahl (`.selected`), die strikt zwischen Light und Dark Mode unterscheidet. |
| `API-Anfragen` | `fetch`, `saveTicket` und `deleteSelectedTicket` senden nun automatisch den `Authorization: Bearer <token>` Header mit. |

### 📊 Aktueller Stand der UI-Roadmap

- [x] **Login/Register Overlay:** Vollständig implementiert und funktionsfähig.
- [x] **Persistente Session:** Benutzer bleibt nach dem Neuladen der Seite angemeldet.
- [x] **Theme-adaptive Tabelle:** Schriftfarben passen sich dynamisch dem gewählten Modus an.
- [x] **Header-Info:** Anzeige des aktiven Benutzernamens neben dem Theme-Toggle.

---
**Farbschema:**

| Element         | Hell-Modus     | Dunkel-Modus |
|-----------------|----------------|--------------|
| Hintergrund     | `#f4f5fb`      | `#0f172a`    |
| Karten          | `#ffffff`      | `#1e293b`    |
| Text            | `#111827`      | `#f1f5f9`    |
| Status: open    | Gelb/Braun     | Dunkelgelb   |
| Status: done    | Grün           | Dunkelgrün   |

---

## 🧪 Tests

### Python Client (client.py)

Demonstriert alle CRUD-Operationen:

```bash
python3 client.py
```

**Was passiert:**
1. Erstellt 3 Test-Tickets
2. Zeigt Liste mit IDs und Status
3. Ruft einzelnes Ticket ab
4. Aktualisiert Status
5. Löscht Ticket
6. Finale Übersicht

**Beispiel-Output:**
```
[ERSTELLEN] Status: 200
Antwort:
{
  "id": 1,
  "title": "Login-Bug beheben",
  "status": "open",
  "priority": "high"
}
```

### pytest Tests

```bash
pytest test_api.py -v
```

**Tests:**
- `test_admin_flow`: Admin registrieren → Login → Alle Tickets löschen
- `test_user_forbidden`: Prüft, dass User ohne Token abgelehnt werden

---

## 💾 Datenbank

### Technologie
- **Engine:** SQLite
- **ORM:** SQLAlchemy 2.0
- **Datei:** `tickets.db` (im Projektverzeichnis)

## 📊 Datenbank-Struktur

Das System verwendet eine relationale SQLite-Datenbank. Die Hauptbeziehung: Ein User kann mehrere Tickets besitzen (One-to-Many).
```mermaid
%%{init: {'theme':'dark'}}%%
classDiagram
    direction LR
    
    class USER {
        <<SQLite Table>>
        int id
        string username
        string password_hash
        string role
        ---
        PK: id(Auto Increment)
        UK: username(Unique)
    }
    
    class TICKET {
        <<SQLite Table>>
        int id
        string title
        string description
        string status
        string priority
        string assignee
        int owner_id
        ---
        FK: owner_id → USER.id
        PK: id(Auto Increment)
    }
    
    USER "1" --o "*" TICKET : besitzt
```

**Legende:**
- `PK` - Primary Key (Auto Increment)
- `FK` - Foreign Key → USER.id  
- `1:N` - Ein User kann viele Tickets besitzen

### Beziehungen

- **USER → TICKET:** Ein User kann 0 bis N Tickets besitzen
- **TICKET → USER:** Jedes Ticket gehört zu genau einem User (owner_id)
````python
# In models.py:
class UserDB(Base):
    tickets = relationship("TicketDB", back_populates="owner")  # One-to-Many

class TicketDB(Base):
    owner_id = Column(Integer, ForeignKey("users.id"))          # Foreign Key
    owner = relationship("UserDB", back_populates="tickets")    # Back-reference
````

### Tabellen

#### `users`
| Feld            | Typ     | Beschreibung                       |
|-----------------|---------|------------------------------------|
| `id`            | Integer | Primary Key (Auto-Increment)       |
| `username`      | String  | Eindeutig, not null                |
| `password_hash` | String  | bcrypt Hash                        |
| `role`          | String  | "user" oder "admin" (default: user)|

#### `tickets`
| Feld          | Typ     | Beschreibung                        |
|---------------|---------|-------------------------------------|
| `id`          | Integer | Primary Key (Auto-Increment)        |
| `title`       | String  | Titel des Tickets                   |
| `description` | String  | Detaillierte Beschreibung           |
| `status`      | String  | "open" / "in_progress" / "done"     |
| `priority`    | String  | "low" / "normal" / "high"           |
| `assignee`    | String  | Name des Bearbeiters                |
| `owner_id`    | Integer | ForeignKey → users.id (optional)    |

### Beziehungen

```python
# User hat viele Tickets
UserDB.tickets → relationship("TicketDB")

# Ticket gehört zu einem User
TicketDB.owner → relationship("UserDB")
```

### Datenbank-Initialisierung

Die Datenbank wird **automatisch** beim ersten Start erstellt:

```python
# In main.py:
Base.metadata.create_all(bind=engine)
```

---

## ⚡ Wichtige Code-Dateien

### auth.py
```python
# Funktionen:
- get_password_hash(password)       # Passwort hashen
- verify_password(plain, hashed)    # Passwort prüfen
- create_access_token(data)         # JWT erstellen
- get_current_user(token, db)       # User aus Token extrahieren
```

### database.py
```python
DATABASE_URL = "sqlite:///./tickets.db"
engine = create_engine(DATABASE_URL, ...)
SessionLocal = sessionmaker(...)
Base = declarative_base()

def get_db():  # Dependency für FastAPI
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### models.py
```python
class UserDB(Base):
    __tablename__ = "users"
    # ... Felder ...
    tickets = relationship("TicketDB", back_populates="owner")

class TicketDB(Base):
    __tablename__ = "tickets"
    # ... Felder ...
    owner = relationship("UserDB", back_populates="tickets")
```

### schemas.py
```python
# Pydantic Modelle für Validierung:
- TicketBase     # Basis-Felder
- TicketCreate   # Für POST (ohne ID)
- Ticket         # Für Response (mit ID)
- UserCreate     # Für Registrierung
```

---

## 🔗 Nützliche Links

| Interface       | URL                                         |
|-----------------|---------------------------------------------|
| **Swagger UI**  | http://127.0.0.1:8001/docs                  |
| **ReDoc**       | http://127.0.0.1:8001/redoc                 |
| **Web-App**     | http://127.0.0.1:8001/ui/index.html         |
| **OpenAPI JSON**| http://127.0.0.1:8001/openapi.json          |

---

## 🛡️ Sicherheit

### Implementiert ✅
- JWT-Token Authentifizierung
- bcrypt Password-Hashing
- Protected DELETE Endpoints
- Admin-Only "Danger Zone"
- SQL Injection Schutz (durch SQLAlchemy)

### Produktions-Empfehlungen ⚠️
```python
# auth.py - NICHT für Produktion!
SECRET_KEY = "SCHOOL_PROJECT_SECRET_KEY"  # ← Ändern!

# Für Produktion:
import secrets
SECRET_KEY = secrets.token_urlsafe(32)
# Speichern in .env Datei
```

### Umgebungsvariablen (empfohlen)
```bash
# .env Datei erstellen
SECRET_KEY=super_geheimer_schluessel_xyz123
DATABASE_URL=sqlite:///./tickets.db
```

```python
# In auth.py:
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## 📊 Berechtigungsmatrix (RBAC)

| Aktion                         | User (Standard) | Admin |
|:-------------------------------|:---------------:|:-----:|
| Alle Tickets anzeigen          | ✅              | ✅    |
| Ticket erstellen               | ✅              | ✅    |
| Eigenes Ticket bearbeiten      | ✅              | ✅    |
| **FREMDES** Ticket bearbeiten  | ⚠️ Geplant     | ✅    |
| **EINZELNES** Ticket löschen   | ✅ (mit Token)  | ✅    |
| **Danger Zone** (Alles löschen)| ❌              | ✅    |

> **Hinweis:** Die Überprüfung von "eigenen" vs. "fremden" Tickets ist für zukünftige Versionen geplant.

---

# 🚀 Roadmap: Auth, Roles & Pro Features

Dieser Plan umfasst die nächsten Schritte zur Verbesserung der Architektur, Implementierung der rollenbasierten Zugriffskontrolle (RBAC) und Datensicherheit.


## 🛠 Etappe 1: Architektur & Datenbank (Core)
*Logik korrigieren und Tabellen vorbereiten.*

- [x] **Automatische ID:** In `fast_api.py` die `id` in `TicketDB` auf `autoincrement=True` setzen.
- [x] **Benutzertabelle:** Modell `UserDB` erstellen (id, username, password_hash, role).
- [x] **Ticket-Verknüpfung:** Feld `owner_id` (ForeignKey zu User) in `TicketDB` hinzufügen.
- [x] **Pydantic-Schemas:** Modelle aufteilen in `TicketCreate` (ohne ID) und `Ticket` (mit ID).

---

## 🔐 Etappe 2: Autorisierung & Sicherheit (Security)
*Implementierung des Login-Systems.*

- [x] **Passwort-Hashing:** `passlib` (bcrypt) integrieren, um Passwörter sicher zu speichern.
- [x] **JWT Tokens:** Endpoint `/token` für die Ausgabe von OAuth2-Token implementieren.
- [x] **Endpunktschutz:** `Depends(get_current_user)` für alle CRUD-Operationen hinzufügen.
- [x] **Rollenmodell (User vs. Admin):**
    - `User`: Kann nur **eigene** Tickets bearbeiten/schließen.
    - `Admin`: Zugriff auf `Danger Zone` (alles löschen) und Bearbeitung aller Tickets.

---



## 🎨 Etappe 3: Benutzeroberfläche (Frontend)
*Änderungen im Browser widerspiegeln.*

- [x] **Login-Seite:** Einfaches Login/Register-Formular in `index.html` hinzufügen.
- [x] **Session-Management:** Speichern des JWT-Tokens im `localStorage`.
- [ ] **Intelligente UI:** - "Alle löschen"-Button für normale User ausblenden.
    - Benutzernamen des angemeldeten Users im Header anzeigen.
---

## 📊 Etappe 4: Funktionen & Filter (Pro Features)
*Effiziente Datenverwaltung.*

- [ ] **Intelligente Suche:** Query-Parameter für `GET /tickets` hinzufügen (Filter nach Status, Priorität).
- [ ] **Audit Log (Historie):** Tabelle `ticket_events` erstellen.
    - Speichern von: "Wer", "Wann", "Welches Feld geändert wurde" (z. B. Status: open -> closed).
- [ ] **Middleware:** Logging aller API-Anfragen in der Konsole oder Datei implementieren.

---


## 🔧 Troubleshooting

### Problem: "Database is locked"
```bash
# Lösung: Timeout erhöhen
# In database.py:
engine = create_engine(
    DATABASE_URL,
    connect_args={"timeout": 30}  # ← Bereits implementiert
)
```

### Problem: Token wird nicht akzeptiert
```bash
# Prüfen:
1. Ist der Token noch gültig? (60 Min. Lebensdauer)
2. Wird "Bearer " vor dem Token geschrieben?
3. User existiert noch in der Datenbank?
```

### Problem: Admin-Rechte funktionieren nicht
```bash
# Username MUSS mit "admin_" beginnen!
✅ Richtig: "admin_hans", "admin_123"
❌ Falsch:  "hans_admin", "administrator"
```

---

## 📝 Beispiel-Workflow

### 1. Admin-Account erstellen
```bash
curl -X POST http://127.0.0.1:8001/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_chef", "password":"geheim123"}'
```

### 2. Login
```bash
curl -X POST http://127.0.0.1:8001/token \
  -d "username=admin_chef&password=geheim123"

# Response:
# {"access_token":"eyJhbGc...","token_type":"bearer"}
```

### 3. Ticket erstellen (ohne Auth)
```bash
curl -X POST http://127.0.0.1:8001/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Server ist langsam",
    "description":"Antwortzeit über 2 Sekunden",
    "status":"open",
    "priority":"high",
    "assignee":"TechTeam"
  }'
```

### 4. Alle Tickets löschen (mit Admin-Token)
```bash
curl -X DELETE http://127.0.0.1:8001/tickets \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 🎓 Für Entwickler

### Code-Standards
- **Python:** PEP 8 Style Guide
- **Type Hints:** Verwendet wo möglich
- **Comments:** Auf Russisch/Deutsch (Mix)

### Development-Server starten
```bash
# Mit Auto-Reload:
uvicorn main:app --reload --host 127.0.0.1 --port 8001

# Mit detailliertem Logging:
uvicorn main:app --reload --log-level debug
```

### Datenbank zurücksetzen
```bash
rm tickets.db
# Beim nächsten Start wird sie neu erstellt
```

---


## 📜 Lizenz

Schul-/Lernprojekt - Frei verwendbar für Bildungszwecke.

---

**🎉 Fertig! Dein moderner Ticket-Tracker ist einsatzbereit!**

*Version 1.0 - Stand: Februar 2026*