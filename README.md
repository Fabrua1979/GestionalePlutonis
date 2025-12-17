# 🎯 Wheel Strategy Stock Screener

Applicazione basata su **Python** e **Streamlit** per identificare i migliori titoli azionari (S&P 500 & Nasdaq 100) adatti alla strategia **Wheel** (Cash Secured Put e Covered Call).

## 🚀 Funzionalità
- **Filtri Finviz:** Screening per Market Cap (>10B), Dividend Yield e Volume.
- **Supporto Tecnico:** Calcolo del minimo a 6 mesi per individuare i "pavimenti" del prezzo.
- **Strike Suggerito:** Calcolo statistico dello strike ideale basato sulla volatilità storica a 30 giorni.
- **Alert Earnings:** Segnalazione dei titoli con risultati trimestrali imminenti per evitare gap di prezzo.

## 🛠️ Installazione
L'app è configurata per il deploy immediato su **Streamlit Cloud**.
I file necessari sono:
- `app.py`: Codice sorgente dell'applicazione.
- `requirements.txt`: Librerie necessarie (yfinance, pandas, streamlit).
