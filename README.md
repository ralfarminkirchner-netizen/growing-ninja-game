# 🥷 GROWING NINJA

> Gamification-Lernspiel für die Grundschule  
> **Fächer:** Deutsch (Wortarten, Komposita), Mathe, Sachunterricht

Ein interaktives Terminal-Spiel, bei dem Kinder als Ninja wachsen, während sie lernen.  
Mit **Hub/Regal**, **Wachstum & Transformationen** (Genin → Kage), **Jump & Run**, **Katana-Slice**, **Ninja-Stern Shooter**, **Mystery Fässern**, **Boss-Kämpfen** und einem **Shop**.

Entwickelt, damit es **mit Schülern gemeinsam erweiterbar** ist.

## ✨ Features (Terminal-Version)

- 4 verschiedene Lern-Mechaniken
- Echtes Fortschrittssystem mit visueller Verwandlung (Stufen)
- Gold-Wirtschaft + permanentes Upgrades
- Mystery Fässer (Glück vs. Challenge)
- Boss-Kämpfe als Highlight
- Speichern/Laden des Fortschritts

## 🚀 Schnellstart (lokal)

```bash
cd growing-ninja
python3 growing_ninja.py
```

Das Spiel läuft komplett offline und benötigt **keine** externen Pakete.

## 🌐 Web-Version (auf Railway)

Die Railway-Deployment liefert eine **spielbare Web-Version** im Browser — perfekt für Klassenräume, Tablets oder wenn kein Python installiert ist.

**Live Demo:** Wird nach Deployment hier erscheinen.

## 📦 Deployment

### GitHub
Dieses Repo enthält:
- Die originale starke **Terminal-Version** (`growing_ninja.py`)
- Eine **Flask-Web-Version** (`app.py`) für Railway / Browser

### Railway

1. Mit diesem GitHub-Repo verbinden
2. Railway erkennt automatisch Python + `requirements.txt` + `Procfile`
3. Deploy → du bekommst eine öffentliche URL

Oder manuell:
```bash
railway login
railway link
railway up
```

## 🛠️ Projekt-Struktur

```
growing-ninja/
├── growing_ninja.py     # Die originale Terminal-Version (empfohlen für Python-Klassen)
├── app.py               # Flask Web-Version (für Railway / Browser)
├── demo_play.py         # Demo-Driver für automatisierte Sessions
├── README.md
├── requirements.txt
├── Procfile
└── .gitignore
```

## 🎓 Pädagogische Idee

Kinder lernen spielerisch:
- Wortarten erkennen (Nomen/Verb/Adjektiv)
- Komposita zerlegen
- Rechnen mit Kontext (Ninja-Sterne, etc.)
- Sachwissen (Tiere, Pflanzen, Körper, Jahreszeiten)

Durch **Wachstum + Belohnungen** (Gold, Upgrades, Verwandlungen) entsteht intrinsische Motivation.

## 🔧 Mit Schülern erweitern (einfach!)

Neue Fragen einfach in `QUESTIONS_DB` in `growing_ninja.py` (und/oder `app.py`) hinzufügen.

Neue Mechaniken als eigene `play_...()` Funktionen schreiben und in die Session-Rotation aufnehmen.

## 📜 Lizenz

MIT – frei für Schulen und Bildung.

---

**Viel Spaß beim Wachsen!**  
Der Ninja wartet auf dich. 🥷🌟
