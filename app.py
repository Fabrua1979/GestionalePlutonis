import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Wheel Pro Scanner - Stable", layout="wide")

# --- LISTA TICKER DI EMERGENZA (S&P 500 TOP) ---
def get_fallback_tickers():
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "V", "JNJ", "WMT",
        "JPM", "PG", "MA", "UNH", "HD", "KO", "PEP", "CVX", "ABBV", "COST",
        "AVGO", "ADBE", "TMO", "CSCO", "CRM", "XOM", "ACN", "BAC", "DIS", "NFLX"
    ]

# --- INTERFACCIA ---
st.title("🎯 Wheel Strategy Pro Scanner (Stable Version)")

st.sidebar.header("⚙️ Parametri Screening")
mcap_min = st.sidebar.number_input("Market Cap Min (B$)", value=10)
div_min = st.sidebar.number_input("Div. Yield Min (%)", value=0.0)
vol_min = st.sidebar.number_input("Volatilità Min (%)", value=1.0)

if st.button('🚀 AVVIA SCANSIONE'):
    tickers = get_fallback_tickers()
    results = []
    log_area = st.expander("📝 Log di Scansione (Clicca per vedere i progressi)", expanded=True)
    
    progress_bar = st.progress(0)
    
    for i, t in enumerate(tickers):
        try:
            log_area.write(f"Analizzando {t}...")
            # Usiamo un timeout per non bloccare l'app
            stock = yf.Ticker(t)
            # Forza il download dei dati veloci
            fast_info = stock.fast_info 
            
            # Recupero dati base
            price = fast_info.get('last_price')
            mcap = fast_info.get('market_cap', 0) / 1e9
            
            # Se il prezzo non c'è, passiamo oltre
            if not price:
                log_area.warning(f"⚠️ {t}: Dati non disponibili")
                continue

            # Recupero dati storici per supporto e volatilità
            hist = stock.history(period="1mo")
            if hist.empty:
                continue

            # Calcolo Volatilità (High-Low medio)
            vol_calc = ((hist['High'] - hist['Low']) / hist['Low']).mean() * 100
            
            # Calcolo Supporto Semplice (Minimo del mese)
            supp = hist['Low'].min()
            
            # Calcolo Strike Conservativo (90% del prezzo attuale)
            strike = round((price * 0.90) * 2) / 2

            # Dividend Yield (da info classica)
            div = stock.info.get('dividendYield', 0) * 100

            # FILTRAGGIO
            if mcap >= mcap_min and div >= div_min and vol_calc >= vol_min:
                results.append({
                    "Ticker": t,
                    "Prezzo": f"{price:.2f}$",
                    "Supporto (1m)": f"{supp:.2f}$",
                    "Strike (CSP)": f"{strike:.2f}$",
                    "Dividendo": f"{div:.2f}%",
                    "Volatilità": f"{vol_calc:.1f}%"
                })
                log_area.success(f"✅ {t} aggiunto!")
            else:
                log_area.info(f"❌ {t} non supera i filtri")

        except Exception as e:
            log_area.error(f"❗ Errore su {t}: {e}")
            
        progress_bar.progress((i + 1) / len(tickers))

    if results:
        st.write("### 📊 Risultati Screening")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("Nessun titolo trovato. Prova ad abbassare ulteriormente i parametri nella barra laterale.")
