import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Wheel Pro Scanner", layout="wide")

# --- FUNZIONE RECUPERO TICKER OTTIMIZZATA ---
@st.cache_data(ttl=604800)
def get_best_tickers():
    try:
        # Tenta di leggere da Wikipedia con un Header per evitare blocchi
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url)[0]
        tickers = table['Symbol'].str.replace('.', '-').tolist()
        return tickers
    except Exception as e:
        # SE FALLISCE, USA QUESTA LISTA DI EMERGENZA (I MIGLIORI PER LA WHEEL)
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "V", "JNJ",
            "WMT", "JPM", "PG", "MA", "UNH", "HD", "KO", "PEP", "CVX", "ABBV", 
            "COST", "AVGO", "ADBE", "TMO", "CSCO", "CRM", "XOM", "ACN", "BAC", "DIS"
        ]

def get_data(ticker_obj):
    hist_6m = ticker_obj.history(period="6mo")
    hist_1m = ticker_obj.history(period="1mo")
    if len(hist_6m) < 20 or len(hist_1m) < 15: return 0, 0, 0
    supp = min(hist_6m['Low'].tail(30).min(), hist_6m['Low'].tail(60).min())
    vol = ((hist_1m['High'] - hist_1m['Low']) / hist_1m['Low']).mean() * 100
    std = hist_1m['Close'].pct_change().std()
    strike = round((hist_1m['Close'].iloc[-1] * (1 - (std * np.sqrt(20) * 1.1))) * 2) / 2
    return round(supp, 2), round(strike, 2), round(vol, 2)

# --- INTERFACCIA ---
st.title("🎯 Wheel Strategy Pro Scanner")

st.sidebar.header("⚙️ Parametri")
mcap_min = st.sidebar.slider("Market Cap Min (B$)", 1, 500, 10)
div_min = st.sidebar.number_input("Div. Yield Min (%)", value=0.0, step=0.5)
vol_min = st.sidebar.slider("Volatilità Min (%)", 0.0, 10.0, 1.5)
st.sidebar.header("🚨 Rischio")
no_earn = st.sidebar.checkbox("Escludi Earnings < 7gg", value=False)

if st.button('🚀 AVVIA SCANSIONE'):
    tickers = get_best_tickers()
    results = []
    progress = st.progress(0)
    status = st.empty()
    
    # Scansioniamo i primi 200 per bilanciare velocità e risultati
    limit = 200 
    for i, t in enumerate(tickers[:limit]):
        status.text(f"Analisi: {t}")
        try:
            s = yf.Ticker(t)
            info = s.info
            mcap = info.get('marketCap', 0) / 1e9
            div = info.get('dividendYield', 0) * 100
            price = info.get('currentPrice', 0)
            
            # Calcoli Tecnici
            supp, strike, vol_calc = get_data(s)
            
            # Controllo Earnings
            calendar = s.calendar
            days = 999
            if calendar is not None and 'Earnings Date' in calendar:
                days = (calendar['Earnings Date'][0].replace(tzinfo=None) - datetime.now()).days

            # APPLICAZIONE FILTRI
            if mcap >= mcap_min and div >= div_min and vol_calc >= vol_min:
                if no_earn and 0 <= days < 7: continue
                
                results.append({
                    "Ticker": t, "Prezzo": f"{price}$", "Supporto": f"{supp}$",
                    "Strike": f"{strike}$", "Dividendo": f"{div:.2f}%",
                    "Volatilità": f"{vol_calc:.1f}%", "Earnings": f"{days}gg",
                    "Status": "✅ OK" if days > 7 else "⚠️ EARN"
                })
        except: continue
        progress.progress((i + 1) / limit)

    status.empty()
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("Nessun titolo trovato. Prova ad azzerare il Dividendo e la Volatilità per test.")
