import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import io
import plotly.express as px

st.set_page_config(page_title="Professional Wheel Scanner 1000", layout="wide")

# --- 1. DATABASE COMPLETO USA ---
@st.cache_data
def get_massive_usa_list():
    # Database esteso per coprire S&P 500, Nasdaq 100 e Russell Core
    nasdaq_100 = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'TSLA', 'AVGO', 'COST', 'ADBE', 'LIN', 'CSCO', 'TMUS', 'INTU', 'QCOM', 'AMD', 'AMGN', 'ISRG', 'TXN', 'HON', 'AMAT', 'BKNG', 'VRTX', 'ADI', 'ADP', 'LRCX', 'PANW', 'MU', 'MDLZ', 'REGN', 'SNPS', 'INTC', 'CDNS', 'KLAC', 'MELI', 'PYPL', 'MAR', 'ASML', 'CSX', 'CTAS', 'MNST', 'ORLY', 'WDAY', 'ROP', 'ADSK', 'PCAR', 'LULU', 'CPRT', 'NXPI', 'PAYX', 'ROST', 'TEAM', 'IDXX', 'AEP', 'KDP', 'FAST', 'ODFL', 'AZO', 'BKR', 'GEHC', 'DXCM', 'EXC', 'MRVL', 'CTSH', 'XEL', 'MCHP', 'ANSS', 'DLTR', 'WBD', 'ILMN', 'TTD', 'WBA', 'GFS', 'MDB', 'ON', 'CDW', 'ZS', 'DDOG', 'BIIB', 'ENPH', 'EBAY']
    sp500_others = ['JPM', 'V', 'MA', 'UNH', 'PG', 'XOM', 'HD', 'JNJ', 'ORCL', 'MRK', 'ABBV', 'CVX', 'CRM', 'WMT', 'KO', 'BAC', 'ACN', 'TMO', 'ABT', 'CAT', 'VZ', 'AXP', 'PFE', 'IBM', 'MS', 'GE', 'PM', 'UNP', 'HON', 'GS', 'LOW', 'SPGI', 'RTX', 'SYK', 'LMT', 'ELV', 'DE', 'TJX', 'COP', 'BLK', 'ETN', 'PGR', 'CVS', 'MMC', 'CI', 'BSX', 'SCHW', 'T', 'ZTS', 'WM', 'C', 'FI', 'BA', 'PLD', 'GILD', 'UPS', 'ITW', 'EOG', 'MO', 'CB', 'BDX', 'SLB', 'CME', 'APH', 'SHW', 'MCD', 'MMM', 'ABNB', 'AIG', 'TRV', 'MET', 'AON', 'D', 'SO', 'DUK', 'NEE', 'PSA', 'VICI', 'EQIX', 'DLR', 'WELL', 'AVB', 'SPG', 'KMI', 'WMB', 'OKE', 'HAL', 'DVN', 'FANG', 'CTRA', 'MPC', 'VLO', 'PSX', 'PLTR', 'UBER', 'SNOW', 'SQ', 'PARA', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'ETSY', 'SHOP', 'SE', 'BABA', 'JD', 'BIDU', 'TME', 'FCX', 'AA', 'CLF', 'NUE', 'X', 'VALE', 'GOLD', 'NEM', 'F', 'GM', 'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO', 'WFC', 'STT', 'BK', 'IBKR', 'RJF', 'LPLA', 'ALL', 'AFL', 'AJG', 'WTW', 'EQR', 'ARE', 'VRE', 'CPT', 'MAA', 'UDR', 'ESS', 'INVH', 'AMH', 'SUI', 'ELS', 'FRT', 'REG', 'KIM', 'BRX', 'TCO', 'MAC', 'PEAK', 'DOC', 'HR', 'OHI', 'VTR', 'HST', 'PK', 'BXP', 'SLG', 'FDX', 'RSG', 'NSC', 'AME', 'DOV', 'XYL', 'JCI', 'TT', 'CARR', 'OTIS', 'URI', 'GWW', 'FERG', 'NOW', 'CRWD', 'OKTA', 'NET', 'TSM', 'MSI', 'TEL', 'KEYS', 'TER', 'QRVO', 'SWKS', 'STX', 'WDC', 'HPQ', 'DELL', 'NTAP', 'PSTG', 'VRSN', 'AKAM', 'FSLR', 'SEDG']
    
    return sorted(list(set(nasdaq_100 + sp500_others)))

# --- 2. LOGICA ANALISI ---
def analyze_stock(t_obj, hist):
    try:
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
                if (cal.iloc[0,0] - datetime.now().date()).days <= 7: earn_alert = "⚠️"
        except: pass

        return {
            "Prezzo": round(cp, 2),
            "P/E": info.get('trailingPE', 0),
            "Settore": info.get('sector', 'N/D'),
            "Profit/Mese %": round(profit_month * 10, 2),
            "Strike Consigliato": strike,
            "Distanza Supporto %": round(((cp - hist['Low'].tail(20).min()) / cp) * 100, 2),
            "Earnings": earn_alert,
            "Volatilità %": round(vol_month * 100, 2)
        }
    except: return None

# --- 3. INTERFACCIA ---
st.title("🛡️ Professional Wheel Scanner (Limit 1000)")
usa_list = get_massive_usa_list()

if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

with st.sidebar:
    st.header("⚙️ Configurazione Scansione")
    # Limite alzato a 1000 con protezione dinamica
    max_available = len(usa_list)
    scan_limit = st.number_input("Titoli da scansionare", 10, max_available, min(1000, max_available))

# --- 4. MOTORE DI SCANSIONE ---
if st.button('🚀 AVVIA ANALISI TOTALE'):
    results = []
    progress = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(usa_list[:scan_limit]):
        status.text(f"Analisi: {sym} ({i+1}/{scan_limit})")
        try:
            t = yf.Ticker(sym)
            h = t.history(period="1mo")
            if h.empty: continue
            data = analyze_stock(t, h)
            if data:
                data['Ticker'] = sym
                results.append(data)
            if i % 12 == 0: time.sleep(0.02)
        except: continue
        progress.progress((i + 1) / scan_limit)
    
    st.session_state.scan_results = pd.DataFrame(results)
    status.empty()

# --- 5. FILTRI DINAMICI E TABELLA ---
if st.session_state.scan_results is not None:
    df_full = st.session_state.scan_results.copy()
    
    st.divider()
    st.header("🎯 Filtri sui Risultati")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        f_price = st.slider("Range Prezzo ($)", 0.0, float(df_full['Prezzo'].max()), (0.0, float(df_full['Prezzo'].max())))
    with c2:
        f_profit = st.slider("Profitto Min %", 0.0, 5.0, 1.0)
    with c3:
        f_sector = st.multiselect("Settori", df_full['Settore'].unique(), default=df_full['Settore'].unique())

    # Applica filtri
    df = df_full[(df_full['Prezzo'] >= f_price[0]) & (df_full['Prezzo'] <= f_price[1])]
    df = df[df['Profit/Mese %'] >= f_profit]
    df = df[df['Settore'].isin(f_sector)]

    st.success(f"Trovate {len(df)} opportunità!")

    # EXPORT
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Scarica Excel", output.getvalue(), "wheel_results.xlsx")
    except:
        st.error("Errore Excel: aggiungi 'xlsxwriter' al file requirements.txt")

    # GRAFICO
    st.subheader("📈 Analisi Grafica")
    fig = px.scatter(df, x="Distanza Supporto %", y="Profit/Mese %", text="Ticker", 
                     size="Prezzo", color="Settore", title="Rischio vs Rendimento")
    st.plotly_chart(fig, use_container_width=True)

    # TABELLA
    st.dataframe(df.style.background_gradient(subset=['Profit/Mese %'], cmap='Greens')
                 .applymap(lambda x: 'background-color: #ff4b4b; color: white' if x == "⚠️" else '', subset=['Earnings']),
                 use_container_width=True)
