import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Wheel Strategy Pro Scanner", layout="wide")

# --- 1. GESTIONE API KEY (SECRETS O MANUALE) ---
if "FMP_API_KEY" in st.secrets:
    API_KEY = st.secrets["FMP_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Inserisci FMP API Key", type="password", value="uZJbm6FkDS56ktyFfzvh5flhePsbh4rz")

def get_fmp_data(endpoint, params=""):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}?apikey={API_KEY}{params}"
    try:
        response = requests.get(url)
        if response.status_code == 429:
            st.error("🚫 Limite API giornaliero raggiunto (250 chiamate).")
            return None
        return response.json() if response.status_code == 200 else None
    except:
        return None

# --- 2. SIDEBAR PARAMETRI (I tuoi 7 Filtri) ---
st.sidebar.header("⚙️ Parametri Screening")
mcap_min = st.sidebar.slider("Market Cap Minima (Biliardi $)", 1, 200, 10)
div_min = st.sidebar.number_input("Dividend Yield Min (%)", value=1.5)
vol_min = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 2.0)
avoid_earn = st.sidebar.checkbox("Nascondi Earnings imminenti (< 7gg)", value=True)

st.title("🎯 Wheel Strategy Pro Scanner")
st.caption("Dati forniti esclusivamente da FMP Cloud (Nessun blocco Yahoo).")

if not API_KEY:
    st.warning("⚠️ Inserisci la tua API Key nella sidebar per iniziare.")
else:
    if st.button('🚀 AVVIA SCANSIONE MERCATO'):
        status_text = st.empty()
        status_text.info(f"Fase 1: Recupero titoli con Market Cap > {mcap_min}B...")
        
        # Filtro 1, 2, 3 (Cap, Optionable, Volume) via Screener FMP
        mcap_api = mcap_min * 1000000000
        stocks = get_fmp_data("stock-screener", f"&marketCapMoreThan={mcap_api}&volumeMoreThan=1000000&isEtf=false&isActivelyTrading=true")
        
        if stocks:
            results = []
            progress_bar = st.progress(0)
            today = datetime.now()
            next_week = today + timedelta(days=7)

            # Analizziamo i primi 35 per sicurezza crediti
            for i, s in enumerate(stocks[:35]): 
                symbol = s['symbol']
                status_text.text(f"🔎 Analisi tecnica di {symbol} ({i+1}/35)...")
                
                # Filtro 5 & 7 (Volatilità e Rel Volume)
                hist = get_fmp_data(f"historical-price-full/{symbol}", "&timeseries=30")
                if not hist or 'historical' not in hist: continue
                
                df = pd.DataFrame(hist['historical'])
                curr_price = df['close'].iloc[0]
                vol_mensile = ((df['high'] - df['low']) / df['low']).mean() * 100
                
                avg_vol_10d = df['volume'].head(10).mean()
                rel_vol = df['volume'].iloc[0] / avg_vol_10d

                # Filtro 4 (Dividend Yield)
                div_yield = s.get('lastDiv', 0)
                
                # Filtro 6 (Earnings)
                is_safe_earn = True
                if avoid_earn:
                    earn_data = get_fmp_data(f"historical/earnings-calendar/{symbol}")
                    if earn_data and len(earn_data) > 0:
                        try:
                            next_earn = datetime.strptime(earn_data[0].get('date'), '%Y-%m-%d')
                            if today <= next_earn <= next_week: is_safe_earn = False
                        except: pass

                # APPLICAZIONE LOGICA
                if vol_mensile >= vol_min and div_yield >= div_min and rel_vol > 1.0 and is_safe_earn:
                    strike = round((curr_price * 0.90) * 2) / 2
                    results.append({
                        "Ticker": symbol,
                        "Prezzo": round(curr_price, 2),
                        "Strike CSP": strike,
                        "Div. %": round(div_yield, 2),
                        "Volat. %": round(vol_mensile, 2),
                        "Rel. Vol": round(rel_vol, 2)
                    })
                progress_bar.progress((i + 1) / 35)

            status_text.empty()
            if results:
                df_res = pd.DataFrame(results)
                st.session_state['scan_results'] = df_res
                
                # Tabella Colorata
                st.write("### 📊 Selezione Titoli Wheel")
                st.dataframe(df_res.style.background_gradient(subset=['Div. %'], cmap='Greens')
                                      .background_gradient(subset=['Volat. %'], cmap='Oranges')
                                      .format({'Prezzo': '{:.2f}$', 'Strike CSP': '{:.2f}$'}), 
                             use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_res.to_excel(writer, index=False)
                st.download_button("📥 Scarica Report Excel", buffer.getvalue(), "wheel_scan.xlsx")
            else:
                st.warning("Nessun titolo trovato. Prova ad abbassare i filtri (es. Volatilità o Dividendo).")

    # --- 3. CALCOLATORE ROI ---
    if 'scan_results' in st.session_state:
        st.divider()
        st.subheader("🧮 Calcolatore Profitto")
        c1, c2, c3 = st.columns(3)
        with c1:
            t_sel = st.selectbox("Scegli Ticker", st.session_state['scan_results']['Ticker'])
            row = st.session_state['scan_results'][st.session_state['scan_results']['Ticker'] == t_sel].iloc[0]
        with c2:
            pr = st.number_input("Premio ($)", value=50.0)
            gg = st.number_input("Giorni", value=30)
        with c3:
            cap = row['Strike CSP'] * 100
            roi = (pr / cap) * 100
            st.metric("ROI Annualizzato", f"{(roi * 365 / gg):.1f}%")
