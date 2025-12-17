import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Wheel Strategy Pro Scanner", layout="wide")

# --- SIDEBAR: PARAMETRI INTERATTIVI ---
st.sidebar.header("⚙️ Parametri Screening")
# Qui ho ripristinato i tuoi filtri dagli screenshot precedenti
mcap_min_val = st.sidebar.slider("Market Cap Minima (Biliardi $)", 1, 200, 10)
div_min_val = st.sidebar.number_input("Dividend Yield Min (%)", value=1.5)
vol_min_val = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 2.0)

st.sidebar.header("🚨 Gestione Rischio")
avoid_earn = st.sidebar.checkbox("Nascondi Earnings imminenti (< 7gg)", value=True)

# Inserimento API Key
API_KEY = st.sidebar.text_input("Inserisci FMP API Key", type="password")

def get_fmp_data(endpoint, params=""):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}?apikey={API_KEY}{params}"
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except:
        return None

st.title("🎯 Wheel Strategy Pro Scanner")

if not API_KEY:
    st.warning("⚠️ Inserisci la tua API Key nella sidebar per sbloccare i dati.")
else:
    if st.button('🚀 AVVIA SCANSIONE COMPLETA'):
        st.info(f"Fase 1: Filtraggio titoli con Market Cap > {mcap_min_val}B...")
        
        # Converte miliardi in dollari per l'API
        mcap_api = mcap_min_val * 1000000000
        screener_params = f"&marketCapMoreThan={mcap_api}&volumeMoreThan=1000000&isEtf=false&isActivelyTrading=true"
        stocks = get_fmp_data("stock-screener", screener_params)
        
        if stocks:
            results = []
            log_area = st.empty() # Area per i messaggi dinamici
            progress_bar = st.progress(0)
            today = datetime.now()
            next_week = today + timedelta(days=7)

            # Analizziamo i primi 50 risultati per non finire i crediti subito
            for i, s in enumerate(stocks[:50]): 
                symbol = s['symbol']
                log_area.text(f"Analizzando {symbol}... ({i+1}/50)")
                
                # Recupero Storico (Volatilità e Rel. Volume)
                hist = get_fmp_data(f"historical-price-full/{symbol}", "&timeseries=30")
                if not hist or 'historical' not in hist: continue
                
                df = pd.DataFrame(hist['historical'])
                curr_price = df['close'].iloc[0]
                
                # Filtro Volatilità (Punto 5)
                vol_mensile = ((df['high'] - df['low']) / df['low']).mean() * 100
                
                # Filtro Dividendo (Punto 4)
                div_yield = s.get('lastDiv', 0)
                
                # Filtro Relative Volume (Punto 7)
                avg_vol_10d = df['volume'].head(10).mean()
                rel_vol = df['volume'].iloc[0] / avg_vol_10d

                # Controllo Earnings (Punto 6)
                is_safe_earn = True
                if avoid_earn:
                    earn_data = get_fmp_data(f"historical/earnings-calendar/{symbol}")
                    if earn_data:
                        next_earn_str = earn_data[0].get('date')
                        if next_earn_str:
                            next_earn_dt = datetime.strptime(next_earn_str, '%Y-%m-%d')
                            if today <= next_earn_dt <= next_week:
                                is_safe_earn = False

                # APPLICAZIONE DEI TUOI FILTRI PERSONALIZZATI
                if vol_mensile >= vol_min_val and div_yield >= div_min_val and rel_vol > 1.0 and is_safe_earn:
                    supp = df['low'].min()
                    strike = round((curr_price * 0.90) * 2) / 2
                    
                    results.append({
                        "Ticker": symbol,
                        "Prezzo ($)": round(curr_price, 2),
                        "Strike CSP": strike,
                        "Supporto": round(supp, 2),
                        "Div. %": round(div_yield, 2),
                        "Volat. %": round(vol_mensile, 2),
                        "Rel. Vol": round(rel_vol, 2)
                    })
                
                progress_bar.progress((i + 1) / 50)

            log_area.empty() # Pulisce il log alla fine

            if results:
                st.write(f"### 📊 Risultati ({len(results)} titoli trovati)")
                df_final = pd.DataFrame(results)
                st.dataframe(df_final, use_container_width=True)

                # Export Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_final.to_excel(writer, index=False)
                st.download_button("📥 Scarica Excel", buffer.getvalue(), "analisi_wheel.xlsx")
            else:
                st.warning("Nessun titolo trovato con questi parametri. Prova ad abbassare la Market Cap o la Volatilità.")
