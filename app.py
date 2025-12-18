import streamlit as st
import pandas as pd
import yfinance as yf
import io
import time

st.set_page_config(page_title="Wheel Strategy PRO - 500 Titoli", layout="wide")

# --- 1. LISTA HARDCODED (Sostituisce Wikipedia per evitare blocchi 403) ---
@st.cache_data
def get_sp500_tickers():
    # Ecco i principali titoli dell'S&P 500 (puoi aggiungerne quanti ne vuoi)
    return [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'BRK-B', 'JPM', 'V', 
        'MA', 'AVGO', 'HD', 'PG', 'COST', 'JNJ', 'LLY', 'MRK', 'ABBV', 'CVX', 
        'XOM', 'PEP', 'KO', 'WMT', 'TMO', 'ADBE', 'CRM', 'ORCL', 'NFLX', 'AMD', 
        'INTC', 'CSCO', 'TXN', 'QCOM', 'AMAT', 'MU', 'DIS', 'NKE', 'PFE', 'T', 
        'VZ', 'BA', 'GE', 'HON', 'UPS', 'CAT', 'DE', 'PLTR', 'BABA', 'PYPL',
        'ABNB', 'UBER', 'SNOW', 'SHOP', 'SQ', 'COIN', 'MSTR', 'MARA', 'RIOT', 'HOOD',
        'LCID', 'RIVN', 'NIO', 'XPEV', 'LI', 'PINS', 'SNAP', 'ROKU', 'U', 'DKNG',
        'PENN', 'ZM', 'DOCU', 'ETSY', 'SE', 'MELI', 'JD', 'PDD', 'BIDU', 'TME',
        'FCX', 'AA', 'CLF', 'NUE', 'X', 'VALE', 'GOLD', 'NEM', 'F', 'GM',
        'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO',
        'WFC', 'BAC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'PGR', 'CB',
        'MMC', 'AON', 'TRV', 'MET', 'PRU', 'AIG', 'LMT', 'RTX', 'GD', 'NOC',
        'AMT', 'PLD', 'CCI', 'EQIX', 'DLR', 'PSA', 'O', 'VICI', 'WY', 'SBAC'
    ]

# --- 2. SIDEBAR ---
st.sidebar.header("⚙️ Filtri di Scansione")
# ATTENZIONE: Per vedere tutto, tieni questi valori a 0 inizialmente
mcap_min = st.sidebar.slider("Market Cap Minima (Miliardi $)", 0, 500, 0)
div_min = st.sidebar.number_input("Dividend Yield Min (%)", value=0.0)
vol_min = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 0.0)
limit_scan = st.sidebar.number_input("Titoli da scansionare", value=150)

st.title("🎯 Wheel Strategy Global Scanner")
st.caption("Motore locale ultra-stabile. Nessuna dipendenza da Wikipedia.")

# --- 3. MOTORE DI ANALISI ---
if st.button('🚀 AVVIA SCANSIONE COMPLETA'):
    tickers_to_scan = get_sp500_tickers()[:int(limit_scan)]
    
    st.info(f"Analisi di {len(tickers_to_scan)} titoli in corso...")
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(tickers_to_scan):
        status_text.text(f"🔎 Analisi: {symbol} ({i+1}/{len(tickers_to_scan)})")
        try:
            t = yf.Ticker(symbol)
            info = t.info
            
            if info and 'currentPrice' in info:
                price = info.get('currentPrice')
                mcap = info.get('marketCap', 0) / 1e9
                dy = info.get('dividendYield', 0) * 100
                
                if mcap >= mcap_min and dy >= div_min:
                    hist = t.history(period="1mo")
                    if not hist.empty:
                        vol = ((hist['High'] - hist['Low']) / hist['Low']).mean() * 100
                        if vol >= vol_min:
                            results.append({
                                "Ticker": symbol, "Prezzo": price,
                                "Strike (-10%)": round((price * 0.90) * 2) / 2,
                                "Div. %": round(dy, 2), "Volatilità %": round(vol, 2),
                                "Cap. (Mld $)": round(mcap, 1), "Settore": info.get('sector', 'N/A')
                            })
            time.sleep(0.02) # Velocissimo in locale
        except:
            continue
        progress_bar.progress((i + 1) / len(tickers_to_scan))

    status_text.empty()
    if results:
        df_res = pd.DataFrame(results)
        st.success(f"✅ Trovate {len(results)} opportunità!")
        st.dataframe(df_res.style.background_gradient(subset=['Div. %'], cmap='Greens')
                                  .background_gradient(subset=['Volatilità %'], cmap='Oranges')
                                  .format({'Prezzo': '{:.2f}$', 'Strike (-10%)': '{:.2f}$'}), 
                     use_container_width=True)
    else:
        st.warning("Nessun titolo trovato. Controlla che i filtri nella sidebar non siano troppo alti.")
