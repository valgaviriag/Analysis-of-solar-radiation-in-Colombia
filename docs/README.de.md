# ☀️ Solar Kolumbien | Strahlungs-Dashboard

![alt text](../image.png)

## 📌 Beschreibung
**Solar Kolumbien** ist eine interaktive Plattform für die geospatiale Analyse zur Visualisierung und Untersuchung des Solarstrahlungspotenzials im kolumbianischen Territorium. Unter Verwendung historischer Daten des Stationsnetzes des **IDEAM** wendet das Projekt fortschrittliche Interpolationsalgorithmen (**Kriging**) an, um kontinuierliche Strahlungsoberflächen zu erzeugen. Dies ermöglicht die Identifizierung von Gebieten mit der höchsten Eignung für Photovoltaikprojekte.

## 🚀 Hauptmerkmale
- **Interaktive Heatmap**: Dynamische Visualisierung der Solarstrahlung (kWh/m²) im ganzen Land.
- **Kriging-Interpolation**: Mathematisches Modell (Ordinary Kriging - Sphärisch), angewendet auf 8.000 Punkte für eine überlegene territoriale Präzision.
- **Mehrsprachige Unterstützung**: Benutzeroberfläche verfügbar in **Englisch**, **Spanisch** und **Deutsch**.
- **Animationsmodus**: Automatische Wiedergabe der solaren Variabilität über die Monate des Jahres hinweg.
- **Geografisches KPI-Panel**:
  - **Solarpotenzial**: Automatische Klassifizierung (Exzellent, Hoch, Moderat, Niedrig).
  - **P90-Index**: Strahlungsgarantie, die von 90% des Territoriums überschritten wird.
  - **Regionaler Spitzenreiter**: Dynamische Identifizierung des Departements mit den höchsten Strahlungswerten.
- **Premium-Design**: Moderne Benutzeroberfläche im Dark Mode mit Glassmorphism-Effekten und responsivem Layout.

## 🛠️ Tech Stack
### Frontend
- **HTML5 / JavaScript (ES6+)**
- **Tailwind CSS**: Modernes Utility-First-Styling.
- **Plotly.js**: Rendering-Engine für die Basiskarte (Mapbox) und Visualisierung räumlicher Daten.
- **FontAwesome**: Technische Ikonografie.
- **Internationalisierung (i18n)**: Native Implementierung für dynamisches Umschalten der Sprache.

### Geostatistische Analyse & Backend
- **Python**: Datenverarbeitung und geospatiale Modellierung.
- **PyKrige**: Implementierung des Ordinary Kriging Modells.
- **GeoPandas & Shapely**: Verarbeitung von Geometrien und nationalen geografischen Masken.
- **Pandas & NumPy**: Effiziente Manipulation großer Mengen meteorologischer Daten.

## 📂 Projektstruktur
- `index.html`: Haupt-Dashboard mit mehrsprachiger Unterstützung und Visualisierungslogik.
- `kriging_interpolation.py`: Python-Skript zur Verarbeitung von CSV-Daten und zur Erzeugung des interpolierten Gitters.
- `radiation_data.csv`: Stationsdaten (Monatliche Strahlung und Jahresdurchschnitt).
- `colombia.json`: GeoJSON der nationalen Grenze für den Ausschnitt der Interpolation.
- `kriging_data.json`: Verarbeitete Interpolationsergebnisse für die Nutzung im Dashboard.
- `convert_units.py`: Utility zur Normalisierung von Einheiten (Wh/m² zu kWh/m²).

## 📊 Methodik
Die Strahlungsoberfläche wird mittels **Kriging Ordinario** erzeugt, einer geostatistischen Methode, die Werte an nicht beprobten Punkten basierend auf der räumlichen Korrelation bekannter Daten (Stationen) schätzt.
1. **Bereinigung**: IDEAM-Daten werden durch Entfernen von Nullwerten und Normalisieren von Koordinaten verarbeitet.
2. **Interpolation**: Das sphärische Modell wird für jeden Monat des Jahres ausgeführt.
3. **Maskierung**: Die Ergebnisse werden mit dem offiziellen Polygon Kolumbiens gefiltert, um Verzerrungen in Grenz- und Meeresgebieten zu vermeiden.

## ⚙️ Installation und lokale Nutzung
1. Repositorium klonen.
2. `index.html` in einem Browser öffnen (die Verwendung eines lokalen Servers wie *Live Server* von VS Code wird empfohlen, um JSON-Dateien korrekt zu laden).
3. Zum Aktualisieren der Daten:
   - Python-Abhängigkeiten installieren: `pip install pandas numpy pykrige geopandas shapely`
   - `python kriging_interpolation.py` ausführen, um das Datengitter neu zu generieren.

---
*Entwickelt für die Analyse erneuerbarer Energien in Kolumbien.*
