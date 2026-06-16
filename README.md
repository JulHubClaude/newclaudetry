# investment-transaction-analyzer

Eine kleine lokale Streamlit-App zum Erfassen, Importieren, Bereinigen und
Analysieren von Investment-Transaktionen. Lernprojekt für Python, SQL und
Datenanalyse.

## Features (V1)

- Beispiel-CSV mit fiktiven Transaktionen
- CSV-Import mit Validierung
- Persistenz in SQLite
- Streamlit-Dashboard mit Kennzahlen, Allokation, Cashflow und Tabelle

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Beispiel-Datenbank befüllen
python -m src.importer data/sample_transactions.csv

# App starten
streamlit run app.py
```

## Projektstruktur

```
investment-transaction-analyzer/
├── app.py                       # Streamlit-Dashboard
├── requirements.txt
├── data/
│   └── sample_transactions.csv  # Fiktive Beispieldaten
├── database/
│   └── schema.sql               # Tabellen-Definition
├── src/
│   ├── db.py                    # SQLite-Verbindung, Schema-Init
│   ├── importer.py              # CSV → DataFrame → SQLite
│   ├── validation.py            # Regeln für saubere Daten
│   └── analysis.py              # Kennzahlen und Aggregationen
└── tests/
    ├── test_validation.py
    └── test_analysis.py
```

## Transaktions-Schema

| Feld              | Typ      | Beschreibung                                                  |
|-------------------|----------|---------------------------------------------------------------|
| date              | DATE     | Transaktionsdatum (YYYY-MM-DD)                                |
| transaction_type  | TEXT     | buy, sell, dividend, deposit, withdrawal, fee, tax            |
| asset_class       | TEXT     | stock, etf, crypto, precious_metal, private_equity, cash, other |
| asset_name        | TEXT     | Klartext-Name (z. B. "Apple Inc.")                            |
| ticker            | TEXT     | Symbol (z. B. AAPL), optional bei Cash                        |
| broker            | TEXT     | Name des Brokers/Bank                                         |
| currency          | TEXT     | ISO 4217 (EUR, USD, ...)                                      |
| quantity          | REAL     | Anzahl Einheiten                                              |
| price_per_unit    | REAL     | Preis pro Einheit                                             |
| gross_amount      | REAL     | Bruttosumme (quantity * price_per_unit)                       |
| fees              | REAL     | Gebühren                                                      |
| taxes             | REAL     | Steuern                                                       |
| net_amount        | REAL     | Nettoeffekt auf das Cashkonto (Vorzeichen siehe unten)        |
| notes             | TEXT     | Freitext                                                      |

### Vorzeichenkonvention `net_amount`

- **Negativ** (Geld geht raus): `buy`, `withdrawal`, `fee`, `tax`
- **Positiv** (Geld kommt rein): `sell`, `dividend`, `deposit`

## Fachliche Vereinfachungen

Damit das Projekt als Lernprojekt überschaubar bleibt, ist einiges absichtlich
vereinfacht:

- **Realisierte Gewinne/Verluste** werden grob als `Summe(net_amount bei sell)
  - Summe(net_amount bei buy)` über alle Assets gerechnet. Eine echte
  FIFO/LIFO-Logik pro Position gibt es noch nicht.
- **Keine Währungsumrechnung.** Beträge in unterschiedlichen Währungen werden
  ohne FX-Konvertierung addiert. Für realistische Auswertungen sollte man auf
  eine Basiswährung normalisieren.
- **Keine Kursdaten.** Es gibt keine Live-Preise; "Portfolio Allocation"
  basiert auf der Summe der Netto-Käufe pro Anlageklasse, nicht auf
  Marktwerten.
- **Validierung** prüft Pflichtfelder, erlaubte Werte und einfache Plausibilität
  (keine negativen Mengen bei Käufen etc.), aber keine doppelten Einträge.

## Tests

```bash
pytest
```
