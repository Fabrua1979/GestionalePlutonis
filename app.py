import streamlit as st
import pandas as pd
import yfinance as yf
import io

st.set_page_config(page_title="Wheel Strategy Pro Scanner", layout="wide")

# --- 1. FUNZIONE CON LISTA 100 TITOLI OTTIMIZZATI ---
@st.cache_data
def get_best_tickers():
    # Lista manuale dei 100 titoli più rilevanti (evita blocchi web)
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
        'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO'
    ]

# --- 2. SIDEBAR PARAMETRI ---
st.sidebar.header("⚙️ Filtri di Scansione")
# Suggerimento: tieni MCAP bassa all'inizio per vedere più risultati
mcap_min = st.sidebar.slider("Market Cap Minima (Biliardi $)", 0, 500, 10)
div_min = st.sidebar.number_input("Dividend Yield Min (%)", value=0.0)
vol_min = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 1.0)
limit_scan = st.sidebar.number_input("Limite titoli da scansionare", value=100)

st.title("🎯 Wheel Strategy Pro Scanner")
st.caption("Analisi in tempo reale su 100 titoli selezionati via Yahoo Finance.")

if st.button('🚀 AVVIA SCANSIONE ORA'):
    all_tickers = get_best_tickers()
    tickers_to_scan = all_tickers[:int(limit_scan)]
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(tickers_to_scan):
        symbol = symbol.replace('.', '-')
        status_text.text(f"🔎 Analisi di {symbol} ({i+1}/{len(tickers_to_scan)})...")
        
        try:
            t = yf.Ticker(symbol)
            info = t.info
            
            # Recupero dati fondamentali
            mcap = info.get('marketCap', 0) / 1e9
            div_yield = info.get('dividendYield', 0) * 100
            curr_price = info.get('currentPrice')
            
            if curr_price and mcap >= mcap_min and div_yield >= div_min:
                # Calcolo Volatilità (High-Low medio ultimo mese)
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
        except:
            continue
        progress_bar.progress((i + 1) / len(tickers_to_scan))

    status_text.empty()
    if results:
        df_res = pd.DataFrame(results)
        st.write(f"### 📊 Risultati: Trovati {len(results)} titoli")
        
        # Tabella colorata e formattata
        st.dataframe(df_res.style.background_gradient(subset=['Div. %'], cmap='Greens')
                                  .background_gradient(subset=['Volat. %'], cmap='Oranges')
                                  .format({'Prezzo': '{:.2f}$', 'Strike CSP (-10%)': '{:.2f}$'}), 
                     use_container_width=True)
        
        # Export Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("📥 Scarica Report Excel", buffer.getvalue(), "wheel_scan.xlsx")
    else:
        st.warning("Nessun titolo trovato. Prova ad abbassare la Market Cap o la Volatilità nella sidebar.")
