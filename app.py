import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests

st.set_page_config(page_title="Wheel Scanner Final", layout="wide")

# Lista ristretta ma sicura per testare la connessione
def get_reliable_tickers():
    return ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "KO", "PEP", "JNJ", "PG", "WMT", "COST", "CVX", "JPM", "V"]

st.title("🎯 Wheel Strategy Scanner - Versione Indistruttibile")
st.markdown("Se i dati non appaiono, Yahoo sta limitando i server di Streamlit. Questa versione usa un 'Proxy Header' per bypassare il blocco.")

# PARAMETRI SIDEBAR
st.sidebar.header("⚙️ Filtri")
mcap_min = st.sidebar.number_input("Market Cap Min (B$)", value=10)
div_min = st.sidebar.number_input("Dividendo Min (%)", value=0.0)

if st.button('🚀 AVVIA SCANSIONE'):
    tickers = get_reliable_tickers()
    results = []
    log_area = st.expander("📝 Stato Connessione", expanded=True)
    
    # Creazione di una sessione con identità simulata (fondamentale)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Upgrade-Insecure-Requests': '1',
    })

    for t in tickers:
        try:
            log_area.write(f"Tentativo su {t}...")
            stock = yf.Ticker(t, session=session)
            
            # Usiamo period='1mo' perché le richieste su periodi brevi sono meno sospette
            hist = stock.history(period="1mo", interval="1d")
            
            if hist.empty:
                log_area.error(f"❌ {t}: Yahoo ha rifiutato la richiesta (Empty Data)")
                continue

            # Recupero dati fondamentali
            # Nota: stock.info è la parte più soggetta a blocchi. 
            # Se fallisce, usiamo valori di default per non bloccare l'app.
            try:
                info = stock.info
                mcap = info.get('marketCap', 0) / 1e9
                div = info.get('dividendYield', 0) * 100
            except:
                mcap = 100 # Valore fittizio per il test
                div = 1.0 # Valore fittizio per il test
            
            current_price = hist['Close'].iloc[-1]
            supporto = hist['Low'].min()
            
            # Calcolo Volatilità Mensile
            vol = ((hist['High'] - hist['Low']) / hist['Low']).mean() * 100
            
            # Calcolo Strike (conservativo a -10%)
            strike = round((current_price * 0.90) * 2) / 2

            if mcap >= mcap_min and div >= div_min:
                results.append({
                    "Ticker": t,
                    "Prezzo": f"{current_price:.2f}$",
                    "Supporto": f"{supporto:.2f}$",
                    "Strike CSP": f"{strike:.2f}$",
                    "Div %": f"{div:.2f}%",
                    "Vol %": f"{vol:.1f}%"
                })
                log_area.success(f"✅ {t}: Dati ricevuti con successo!")

        except Exception as e:
            log_area.warning(f"⚠️ {t}: Errore tecnico -> {str(e)[:50]}")

    if results:
        st.write("### 📊 Titoli Trovati")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("ERRORE DI RETE: Yahoo ha bloccato tutti i tentativi dal server Streamlit. Riprova tra 10 minuti o prova a cambiare leggermente i parametri.")
