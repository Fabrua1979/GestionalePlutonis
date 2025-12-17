import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Wheel Strategy Pro Scanner", layout="wide")

# Lista titoli affidabile per il test iniziale
TICKERS_WHEEL = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "V", "JNJ", "WMT",
    "JPM", "PG", "MA", "UNH", "HD", "KO", "PEP", "CVX", "ABBV", "COST"
]

st.title("🎯 Wheel Strategy Pro Scanner")
st.markdown("Analisi basata sui criteri Finviz: Capitalizzazione, Liquidità e Dividendi.")

# SIDEBAR - FILTRI DAGLI SCREENSHOT UTENTE
st.sidebar.header("⚙️ Parametri Screening")
mcap_min = st.sidebar.number_input("Market Cap Minima (Biliardi $)", value=10)
min_div = st.sidebar.number_input("Dividend Yield Min (%)", value=1.5)
min_vol_perc = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 2.0)
min_avg_vol = 1000000 # Filtro Volume > 1M (da screenshot)

st.sidebar.header("🚨 Gestione Rischio")
avoid_earnings = st.sidebar.checkbox("Escludi Earnings imminenti (< 7gg)", value=True)

if st.button('🚀 AVVIA SCANSIONE'):
    results = []
    log_area = st.expander("📝 Log di Analisi", expanded=True)
    progress_bar = st.progress(0)
    
    for i, t in enumerate(TICKERS_WHEEL):
        try:
            log_area.write(f"Scansione di {t}...")
            stock = yf.Ticker(t)
            
            # Recupero storico per Prezzo, Supporto e Volatilità
            hist_m = stock.history(period="1mo")
            if hist_m.empty:
                continue
            
            price = hist_m['Close'].iloc[-1]
            supp = hist_m['Low'].min()
            # Volatilità mensile (High-Low medio)
            vol_calc = ((hist_m['High'] - hist_m['Low']) / hist_m['Low']).mean() * 100
            
            # Dati fondamentali
            info = stock.info
            mcap = info.get('market_cap', info.get('marketCap', 0)) / 1e9
            div = info.get('dividendYield', 0) * 100
            avg_vol = info.get('averageVolume', 0)

            # Controllo Earnings (Punto 6 screenshot)
            calendar = stock.calendar
            days_to_earn = 999
            if calendar is not None and 'Earnings Date' in calendar:
                earn_date = calendar['Earnings Date'][0].replace(tzinfo=None)
                days_to_earn = (earn_date - datetime.now()).days

            # APPLICAZIONE FILTRI
            if (mcap >= mcap_min and div >= min_div and 
                avg_vol >= min_avg_vol and vol_calc >= min_vol_perc):
                
                if avoid_earnings and 0 <= days_to_earn < 7:
                    log_area.warning(f"⚠️ {t} saltato: Earnings troppo vicini.")
                    continue
                
                # Calcolo Strike Suggerito (conservativo)
                std = hist_m['Close'].pct_change().std()
                strike = round((price * (1 - (std * 2.5))) * 2) / 2
                
                results.append({
                    "Ticker": t,
                    "Prezzo": f"{price:.2f}$",
                    "Supporto": f"{supp:.2f}$",
                    "Strike Suggerito": f"{strike:.2f}$",
                    "Div. Yield": f"{div:.2f}%",
                    "Vol. Mensile": f"{vol_calc:.1f}%",
                    "Status": "✅ OK"
                })
                log_area.success(f"✅ {t} aggiunto.")
        
        except Exception as e:
            log_area.error(f"❗ Errore su {t}. Yahoo ha limitato la connessione.")
            
        progress_bar.progress((i + 1) / len(TICKERS_WHEEL))

    if results:
        st.write("### 📊 Risultati Screening")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("Nessun dato ricevuto. Yahoo Finance sta bloccando i server di Streamlit.")
