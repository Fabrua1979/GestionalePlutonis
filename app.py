import streamlit as st
import pandas as pd
import yfinance as yf
import io

st.set_page_config(page_title="Wheel Strategy Global Scanner", layout="wide")

# --- 1. FUNZIONE PER RECUPERARE TUTTI I TITOLI (S&P 500) ---
@st.cache_data
def get_sp500_tickers():
    try:
        # AGGIORNATO: flavor='bs4' risolve l'errore ImportError online
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        table = pd.read_html(url, flavor='bs4') 
        df = table[0]
        return df['Symbol'].tolist()
    except Exception as e:
        # Lista di emergenza in caso di errori di connessione a Wikipedia
        st.sidebar.warning(f"Nota: Caricata lista predefinita (Wikipedia non raggiungibile)")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'AMD', 'PLTR']

# --- 2. SIDEBAR PARAMETRI ---
st.sidebar.header("⚙️ Filtri di Scansione")
mcap_min = st.sidebar.slider("Market Cap Minima (Biliardi $)", 1, 500, 50)
div_min = st.sidebar.number_input("Dividend Yield Min (%)", value=1.0)
vol_min = st.sidebar.slider("Volatilità Mensile Min (%)", 0.0, 10.0, 1.5)
limit_scan = st.sidebar.number_input("Limite titoli da scansionare", value=100, help="Scansionare 500 titoli richiede tempo. Inizia con 100.")

st.title("🎯 Wheel Strategy Global Scanner")
st.caption("Scansione automatica dei componenti dell'S&P 500 tramite Yahoo Finance.")

if st.button('🚀 AVVIA SCANSIONE MASSIVA'):
    all_tickers = get_sp500_tickers()
    # Limitiamo la scansione per non sovraccaricare il sistema
    tickers_to_scan = all_tickers[:int(limit_scan)]
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(tickers_to_scan):
        # Correzione per simboli con il punto (es: BRK.B -> BRK-B)
        symbol = symbol.replace('.', '-')
        status_text.text(f"🔎 Analisi di {symbol} ({i+1}/{len(tickers_to_scan)})...")
        
        try:
            t = yf.Ticker(symbol)
            info = t.info
            
            # Filtri Fondamentali
            mcap = info.get('marketCap', 0) / 1e9
            div_yield = info.get('dividendYield', 0) * 100
            curr_price = info.get('currentPrice')
            
            if curr_price and mcap >= mcap_min and div_yield >= div_min:
                # Calcolo Volatilità Tecnica (Ultimo mese)
                hist = t.history(period="1mo")
                if not hist.empty:
                    vol_mensile = ((hist['High'] - hist['Low']) / hist['Low']).mean() * 100
                    
                    if vol_mensile >= vol_min:
                        # Calcolo Strike prudenziale (-10% dal prezzo attuale)
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
        st.session_state['scan_results'] = df_res
        st.write(f"### 📊 Risultati: Trovati {len(results)} titoli corrispondenti")
        
        # Tabella con formattazione professionale
        st.dataframe(df_res.style.background_gradient(subset=['Div. %'], cmap='Greens')
                                  .background_gradient(subset=['Volat. %'], cmap='Oranges')
                                  .format({'Prezzo': '{:.2f}$', 'Strike CSP (-10%)': '{:.2f}$'}), 
                     use_container_width=True)
        
        # Export Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_res.to_excel(writer, index=False)
        st.download_button("📥 Scarica Report Excel", buffer.getvalue(), "scanner_wheel.xlsx")
    else:
        st.warning("Nessun titolo trovato. Prova ad allentare i filtri nella sidebar.")
