import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import io
import plotly.express as px

st.set_page_config(page_title="USA Total Wheel Scanner", layout="wide")

# --- 1. DATABASE COMPLETO (S&P 500 + NASDAQ + RUSSELL CORE) ---
@st.cache_data
def get_massive_usa_list():
    # Liste espanse per coprire l'intero mercato USA opzionabile
    nasdaq_100 = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'GOOG', 'TSLA', 'AVGO', 'COST', 'PEP', 'ADBE', 'LIN', 'CSCO', 'TMUS', 'INTU', 'QCOM', 'AMD', 'AMGN', 'ISRG', 'TXN', 'HON', 'AMAT', 'BKNG', 'VRTX', 'ADI', 'ADP', 'LRCX', 'PANW', 'MU', 'MDLZ', 'REGN', 'SNPS', 'INTC', 'CDNS', 'KLAC', 'MELI', 'PYPL', 'MAR', 'ASML', 'CSX', 'CTAS', 'MNST', 'ORLY', 'WDAY', 'ROP', 'ADSK', 'PCAR', 'LULU', 'CPRT', 'NXPI', 'PAYX', 'ROST', 'TEAM', 'IDXX', 'AEP', 'KDP', 'FAST', 'ODFL', 'AZO', 'BKR', 'GEHC', 'DXCM', 'EXC', 'MRVL', 'CTSH', 'XEL', 'MCHP', 'ADX', 'ANSS', 'DLTR', 'WBD', 'ILMN', 'TTD', 'WBA', 'GFS', 'MDB', 'ON', 'CDW', 'ZS', 'DDOG', 'BIIB', 'ENPH', 'EBAY']
    sp500_others = ['JPM', 'V', 'MA', 'UNH', 'PG', 'XOM', 'HD', 'JNJ', 'ORCL', 'MRK', 'ABBV', 'CVX', 'CRM', 'WMT', 'KO', 'BAC', 'ACN', 'TMO', 'ABT', 'CAT', 'VZ', 'AXP', 'PFE', 'IBM', 'MS', 'GE', 'PM', 'UNP', 'GS', 'LOW', 'SPGI', 'RTX', 'SYK', 'LMT', 'ELV', 'DE', 'TJX', 'COP', 'BLK', 'ETN', 'PGR', 'CVS', 'MMC', 'CI', 'BSX', 'SCHW', 'T', 'ZTS', 'WM', 'C', 'FI', 'BA', 'PLD', 'GILD', 'UPS', 'ITW', 'EOG', 'MO', 'CB', 'BDX', 'SLB', 'CME', 'APH', 'SHW', 'MCD', 'MMM', 'ABNB', 'AIG', 'TRV', 'MET', 'AON', 'D', 'SO', 'DUK', 'NEE', 'PSA', 'VICI', 'EQIX', 'DLR', 'WELL', 'AVB', 'SPG', 'KMI', 'WMB', 'OKE', 'HAL', 'DVN', 'FANG', 'CTRA', 'MPC', 'VLO', 'PSX', 'PLTR', 'UBER', 'SNOW', 'SQ', 'PARA', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'ETSY', 'SHOP', 'SE', 'BABA', 'JD', 'BIDU', 'TME', 'FCX', 'AA', 'CLF', 'NUE', 'X', 'VALE', 'GOLD', 'NEM', 'F', 'GM', 'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO', 'WFC', 'STT', 'BK', 'IBKR', 'RJF', 'LPLA', 'ALL', 'AFL', 'AJG', 'WTW', 'EQR', 'ARE', 'VRE', 'CPT', 'MAA', 'UDR', 'ESS', 'INVH', 'AMH', 'SUI', 'ELS', 'FRT', 'REG', 'KIM', 'BRX', 'TCO', 'MAC', 'PEAK', 'DOC', 'HR', 'OHI', 'VTR', 'HST', 'PK', 'BXP', 'SLG', 'FDX', 'RSG', 'NSC', 'AME', 'DOV', 'XYL', 'JCI', 'TT', 'CARR', 'OTIS', 'URI', 'GWW', 'FERG', 'NOW', 'CRWD', 'OKTA', 'NET', 'TSM', 'MSI', 'TEL', 'KEYS', 'TER', 'QRVO', 'SWKS', 'STX', 'WDC', 'HPQ', 'DELL', 'NTAP', 'PSTG', 'VRSN', 'AKAM', 'FSLR', 'SEDG']
    
    # Combinazione totale (~1000 titoli core USA)
    return sorted(list(set(nasdaq_100 + sp500_others)))

# --- 2. LOGICA ANALISI ---
def analyze_stock(t_obj, hist):
    try:
        # Verifica fondamentale Opzioni
        if not t_obj.options: return None
        
        cp = hist['Close'].iloc[-1]
        info = t_obj.info
        
        std_dev = hist['Close'].pct_change().dropna().std()
        vol_month = std_dev * (21**0.5)
        strike = round(cp * (1 - vol_month) * 2) / 2
        profit_month = ((cp * vol_month * 0.25) / strike) * 100
        
        earn_alert = "OK"
        try:
            cal = t_obj.calendar
            if cal is not None and not cal.empty:
                days = (cal.iloc[0,0] - datetime.now().date()).days
                if 0 <= days <= 7: earn_alert = "⚠️"
        except: pass

        return {
            "Prezzo": round(cp, 2), "P/E": info.get('trailingPE', 0),
            "Settore": info.get('sector', 'N/D'), "Profit/Mese %": round(profit_month * 10, 2),
            "Strike Consigliato": strike, "Dist. Supp %": round(((cp - hist['Low'].tail(20).min()) / cp) * 100, 2),
            "Earnings": earn_alert, "Volatilità %": round(vol_month * 100, 2)
        }
    except: return None

# --- 3. INTERFACCIA ---
st.title("🛡️ USA Total Market Wheel Scanner")
usa_list = get_massive_usa_list()

with st.sidebar:
    st.header("⚙️ Parametri")
    scan_limit = st.slider("Titoli da analizzare", 10, len(usa_list), 300)
    min_profit = st.slider("Profitto Min %", 0.0, 5.0, 1.0)
    max_dist = st.slider("Distanza Max Supporto %", 0.0, 40.0, 15.0)

st.info(f"Database pronto: **{len(usa_list)}** titoli identificati (Tutto il mercato USA principale).")

# --- 4. SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE TOTALE'):
    results = []
    progress = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(usa_list[:scan_limit]):
        status.text(f"Analisi: {sym} ({i+1}/{scan_limit})")
        try:
            t = yf.Ticker(sym)
            h = t.history(period="1mo")
            if h.empty: continue
            
            res = analyze_stock(t, h)
            if res:
                res['Ticker'] = sym
                results.append(res)
            if i % 15 == 0: time.sleep(0.02)
        except: continue
        progress.progress((i + 1) / scan_limit)

    status.empty()
    if results:
        df = pd.DataFrame(results)
        df = df[(df['Profit/Mese %'] >= min_profit) & (df['Dist. Supp %'] <= max_dist)]
        
        st.success(f"Trovate {len(df)} opportunità opzionabili!")

        # EXPORT EXCEL
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Wheel_Opportunities')
        st.download_button("📥 Scarica Excel", output.getvalue(), "wheel_usa.xlsx")

        # GRAFICO
        st.subheader("📈 Mappa Rischio/Rendimento")
        fig = px.scatter(df, x="Dist. Supp %", y="Profit/Mese %", text="Ticker", 
                         size="Prezzo", color="Profit/Mese %",
                         title="Strategia Wheel: Le migliori opportunità")
        st.plotly_chart(fig, use_container_width=True)

        # TABELLA
        st.dataframe(df.style.background_gradient(subset=['Profit/Mese %'], cmap='Greens')
                     .applymap(lambda x: 'background-color: #ff4b4b; color: white' if x == "⚠️" else '', subset=['Earnings']),
                     use_container_width=True)
    else:
        st.error("Nessun risultato con questi filtri.")
