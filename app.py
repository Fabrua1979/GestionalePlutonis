import streamlit as st
import pandas as pd
import yfinance as yf
import io
import time

st.set_page_config(page_title="Wheel Strategy PRO - S&P 500 Full", layout="wide")

# --- 1. RECUPERO TUTTI I 500 TITOLI ---
@st.cache_data
def get_sp500_tickers():
    try:
        # Preleva la lista ufficiale dei 500 titoli da Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url, flavor='bs4') 
        df = table[0]
        return df['Symbol'].tolist()
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'META']

# --- 2. SIDEBAR PARAMETRI ---
st.sidebar.header("⚙️ Filtri di Scansione")
# Imposta questi valori a 0 per vedere TUTTI i titoli
mcap_min = st.sidebar.slider("Market Cap Minima (Miliardi $)", 0, 500, 0)
div_min = st.sidebar.number_input("Dividend Yield Min (%)", value=0.0)
vol_min = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 0.0)
limit_scan = st.sidebar.number_input("Quanti titoli scansionare?", value=500)

st.title("🎯 Wheel Strategy Global Scanner")
st.caption("Scansione massiva dell'S&P 500. Analisi tecnica e fondamentale completa.")

# --- 3. MOTORE DI SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE MASSIVA'):
    all_tickers = get_sp500_tickers()
    tickers_to_scan = all_tickers[:int(limit_scan)]
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(tickers_to_scan):
        symbol = symbol.replace('.', '-') # Correzione ticker tipo BRK.B
        status_text.text(f"🔎 Analisi di {symbol} ({i+1}/{len(tickers_to_scan)})...")
        
        try:
            t = yf.Ticker(symbol)
            info = t.info
            
            if info and 'currentPrice' in info:
                curr_price = info.get('currentPrice')
                mcap = info.get('marketCap', 0) / 1e9
                div_yield = info.get('dividendYield', 0) * 100
                
                # Filtro incrociato
                if mcap >= mcap_min and div_yield >= div_min:
                    hist = t.history(period="1mo")
                    if not hist.empty:
                        vol_mensile = ((hist['High'] - hist['Low']) / hist['Low']).mean() * 100
                        
                        if vol_mensile >= vol_min:
                            strike = round((curr_price * 0.90) * 2) / 2
                            results.append({
                                "Ticker": symbol,
                                "Prezzo": curr_price,
                                "Strike CSP (-10%)": strike,
                                "Div. %": round(div_yield, 2),
                                "Volat. %": round(vol_mensile, 2),
                                "Cap. (B)": round(mcap, 1),
                                "Settore": info.get('sector', 'N/A')
                            })
            
            # In locale 0.05s bastano per essere veloci senza blocchi
            time.sleep(0.05)
            
        except:
            continue
            
        progress_bar.progress((i + 1) / len(tickers_to_scan))

    status_text.empty()
    
    if results:
        df_res = pd.DataFrame(results)
        st.write(f"### 📊 Risultati: Trovati {len(results)} titoli corrispondenti")
        
        # Formattazione semplice per evitare errori di librerie mancanti
        st.dataframe(df_res.style.format({
            'Prezzo': '{:.2f}$', 
            'Strike CSP (-10%)': '{:.2f}$',
            'Div. %': '{:.2f}%',
            'Volat. %': '{:.2f}%'
        }), use_container_width=True)
        
        # Download Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("📥 Scarica Report Excel", buffer.getvalue(), "wheel_full_report.xlsx")
    else:
        st.warning("Nessun titolo trovato. Prova ad azzerare i filtri nella sidebar.")
