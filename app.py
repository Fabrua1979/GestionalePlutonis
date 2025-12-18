import streamlit as st
import pandas as pd
import yfinance as yf
import io
import time

st.set_page_config(page_title="Wheel Strategy PRO - Full S&P 500", layout="wide")

# --- 1. RECUPERO INTEGRALE DEI 500 TITOLI ---
@st.cache_data
def get_sp500_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        # Usiamo 'html5lib' o 'lxml' per massimizzare la compatibilità
        tables = pd.read_html(url) 
        df = tables[0]
        tickers = df['Symbol'].tolist()
        return [t.replace('.', '-') for t in tickers] # Correzione automatica per Yahoo
    except Exception as e:
        st.error(f"⚠️ Errore critico nel caricamento lista 500 titoli: {e}")
        # Se fallisce ancora, restituisce una lista minima per non crashare
        return ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'META', 'AMD', 'GOOGL', 'NFLX']

# --- 2. SIDEBAR ---
st.sidebar.header("⚙️ Filtri di Scansione")
mcap_min = st.sidebar.slider("Market Cap Minima (Miliardi $)", 0, 500, 0)
div_min = st.sidebar.number_input("Dividend Yield Min (%)", value=0.0)
vol_min = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 0.0)
limit_scan = st.sidebar.number_input("Quanti titoli scansionare? (max 503)", value=500)

st.title("🎯 Wheel Strategy Global Scanner")
st.caption("Scansione massiva del mercato USA. Analisi di tutti i componenti dell'indice.")

# --- 3. MOTORE DI ANALISI ---
if st.button('🚀 AVVIA SCANSIONE COMPLETA'):
    all_tickers = get_sp500_tickers()
    tickers_to_scan = all_tickers[:int(limit_scan)]
    
    st.info(f"Inizio scansione di {len(tickers_to_scan)} titoli. Attendere completamento...")
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(tickers_to_scan):
        status_text.text(f"🔎 Analisi in corso: {symbol} ({i+1}/{len(tickers_to_scan)})")
        
        try:
            t = yf.Ticker(symbol)
            # Recupero rapido dati fondamentali
            info = t.info
            
            if info and 'currentPrice' in info:
                price = info.get('currentPrice')
                mcap = info.get('marketCap', 0) / 1e9
                dy = info.get('dividendYield', 0) * 100
                
                # Applicazione Filtri
                if mcap >= mcap_min and dy >= div_min:
                    hist = t.history(period="1mo")
                    if not hist.empty:
                        # Calcolo volatilità media giornaliera dell'ultimo mese
                        vol = ((hist['High'] - hist['Low']) / hist['Low']).mean() * 100
                        
                        if vol >= vol_min:
                            results.append({
                                "Ticker": symbol,
                                "Prezzo": price,
                                "Strike (-10%)": round((price * 0.90) * 2) / 2,
                                "Div. %": round(dy, 2),
                                "Volatilità %": round(vol, 2),
                                "Cap. (Mld $)": round(mcap, 1),
                                "Settore": info.get('sector', 'N/A')
                            })
            
            # Pausa minima per evitare blocchi (necessaria anche in locale per 500 titoli)
            time.sleep(0.05)
            
        except:
            continue
            
        progress_bar.progress((i + 1) / len(tickers_to_scan))

    status_text.empty()
    
    if results:
        df_res = pd.DataFrame(results)
        st.success(f"✅ Scansione completata! Trovati {len(results)} titoli corrispondenti.")
        
        # Tabella con gradienti (ora funzionerà grazie a matplotlib)
        st.dataframe(df_res.style.background_gradient(subset=['Div. %'], cmap='Greens')
                                  .background_gradient(subset=['Volatilità %'], cmap='Oranges')
                                  .format({'Prezzo': '{:.2f}$', 'Strike (-10%)': '{:.2f}$'}), 
                     use_container_width=True)
        
        # Esportazione
        csv = df_res.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Report CSV", csv, "scanner_results.csv", "text/csv")
    else:
        st.warning("Nessun titolo trovato. Prova a diminuire i filtri.")
