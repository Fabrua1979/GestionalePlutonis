import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import io
import plotly.express as px

st.set_page_config(page_title="Wheel Strategy PRO Scanner 1000", layout="wide")

# --- 1. DATABASE ESPANSO (USA TOTAL) ---
@st.cache_data
def get_comprehensive_usa_list():
    # Unione di Nasdaq 100 e S&P 500 esteso per superare il limite dei 283
    nasdaq_100 = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'GOOG', 'TSLA', 'AVGO', 'COST', 'PEP', 'ADBE', 'LIN', 'CSCO', 'TMUS', 'INTU', 'QCOM', 'AMD', 'AMGN', 'ISRG', 'TXN', 'HON', 'AMAT', 'BKNG', 'VRTX', 'ADI', 'ADP', 'LRCX', 'PANW', 'MU', 'MDLZ', 'REGN', 'SNPS', 'INTC', 'CDNS', 'KLAC', 'MELI', 'PYPL', 'MAR', 'ASML', 'CSX', 'CTAS', 'MNST', 'ORLY', 'WDAY', 'ROP', 'ADSK', 'PCAR', 'LULU', 'CPRT', 'NXPI', 'PAYX', 'ROST', 'TEAM', 'IDXX', 'AEP', 'KDP', 'FAST', 'ODFL', 'AZO', 'BKR', 'GEHC', 'DXCM', 'EXC', 'MRVL', 'CTSH', 'XEL', 'MCHP', 'ANSS', 'DLTR', 'WBD', 'ILMN', 'TTD', 'WBA', 'GFS', 'MDB', 'ON', 'CDW', 'ZS', 'DDOG', 'BIIB', 'ENPH', 'EBAY']
    sp500_ext = ['JPM', 'V', 'MA', 'UNH', 'PG', 'XOM', 'HD', 'JNJ', 'ORCL', 'MRK', 'ABBV', 'CVX', 'CRM', 'WMT', 'KO', 'BAC', 'ACN', 'TMO', 'ABT', 'CAT', 'VZ', 'AXP', 'PFE', 'IBM', 'MS', 'GE', 'PM', 'UNP', 'HON', 'GS', 'LOW', 'SPGI', 'RTX', 'SYK', 'LMT', 'ELV', 'DE', 'TJX', 'COP', 'BLK', 'ETN', 'PGR', 'CVS', 'MMC', 'CI', 'BSX', 'SCHW', 'T', 'ZTS', 'WM', 'C', 'FI', 'BA', 'PLD', 'GILD', 'UPS', 'ITW', 'EOG', 'MO', 'CB', 'BDX', 'SLB', 'CME', 'APH', 'SHW', 'MCD', 'MMM', 'ABNB', 'AIG', 'TRV', 'MET', 'AON', 'D', 'SO', 'DUK', 'NEE', 'PSA', 'VICI', 'EQIX', 'DLR', 'WELL', 'AVB', 'SPG', 'KMI', 'WMB', 'OKE', 'HAL', 'DVN', 'FANG', 'CTRA', 'MPC', 'VLO', 'PSX', 'PLTR', 'UBER', 'SNOW', 'SQ', 'PARA', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'ETSY', 'SHOP', 'SE', 'BABA', 'JD', 'BIDU', 'TME', 'FCX', 'AA', 'CLF', 'NUE', 'X', 'VALE', 'GOLD', 'NEM', 'F', 'GM', 'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO', 'WFC', 'STT', 'BK', 'IBKR', 'RJF', 'LPLA', 'ALL', 'AFL', 'AJG', 'WTW', 'EQR', 'ARE', 'VRE', 'CPT', 'MAA', 'UDR', 'ESS', 'INVH', 'AMH', 'SUI', 'ELS', 'FRT', 'REG', 'KIM', 'BRX', 'TCO', 'MAC', 'PEAK', 'DOC', 'HR', 'OHI', 'VTR', 'HST', 'PK', 'BXP', 'SLG', 'FDX', 'RSG', 'NSC', 'AME', 'DOV', 'XYL', 'JCI', 'TT', 'CARR', 'OTIS', 'URI', 'GWW', 'FERG', 'NOW', 'CRWD', 'OKTA', 'NET', 'TSM', 'MSI', 'TEL', 'KEYS', 'TER', 'QRVO', 'SWKS', 'STX', 'WDC', 'HPQ', 'DELL', 'NTAP', 'PSTG', 'VRSN', 'AKAM', 'FSLR', 'SEDG']
    return sorted(list(set(nasdaq_100 + sp500_ext)))

# --- 2. ANALISI DATI ---
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
            "Dist. Supp %": round(((cp - hist['Low'].tail(20).min()) / cp) * 100, 2),
            "Earnings": earn_alert,
            "Volatilità %": round(vol_month * 100, 2)
        }
    except: return None

# --- 3. INTERFACCIA E FILTRI ---
if 'scan_data' not in st.session_state:
    st.session_state.scan_data = None

st.title("🚀 Wheel Strategy Ultra Scanner (Limit 1000)")
full_list = get_comprehensive_usa_list()

with st.sidebar:
    st.header("⚙️ Configurazione")
    scan_limit = st.number_input("Titoli da scansionare", 10, len(full_list), 500)
    
    if st.button('🚀 AVVIA ANALISI TOTALE'):
        results = []
        progress = st.progress(0)
        for i, sym in enumerate(full_list[:scan_limit]):
            try:
                t = yf.Ticker(sym)
                h = t.history(period="1mo")
                if h.empty: continue
                data = analyze_stock(t, h)
                if data:
                    data['Ticker'] = sym
                    results.append(data)
                if i % 12 == 0: time.sleep(0.01)
            except: continue
            progress.progress((i + 1) / scan_limit)
        st.session_state.scan_data = pd.DataFrame(results)

# --- 4. FILTRI DINAMICI SUI RISULTATI ---
if st.session_state.scan_data is not None:
    df = st.session_state.scan_data.copy()
    
    st.divider()
    st.header("🎯 Filtra i Risultati")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        f_price = st.slider("Prezzo ($)", 0.0, float(df['Prezzo'].max()), (0.0, float(df['Prezzo'].max())))
    with c2:
        f_vol = st.slider("Volatilità Min %", 0.0, 100.0, 15.0) # FILTRO RICHIESTO
    with c3:
        f_profit = st.slider("Profitto Min %", 0.0, 5.0, 1.0)
    with c4:
        f_sector = st.multiselect("Settori", df['Settore'].unique(), default=df['Settore'].unique())

    # Applica filtri
    mask = (df['Prezzo'].between(f_price[0], f_price[1])) & \
           (df['Volatilità %'] >= f_vol) & \
           (df['Profit/Mese %'] >= f_profit) & \
           (df['Settore'].isin(f_sector))
    
    final_df = df[mask]
    st.success(f"Trovate {len(final_df)} opportunità!")

    # EXCEL E TABELLA
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False)
    st.download_button("📥 Scarica Excel", output.getvalue(), "wheel_results.xlsx")

    st.dataframe(final_df.style.background_gradient(subset=['Profit/Mese %'], cmap='Greens'), use_container_width=True)
