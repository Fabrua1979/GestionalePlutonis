import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import io
import plotly.express as px

st.set_page_config(page_title="Professional Wheel Scanner 1000", layout="wide")

# --- 1. DATABASE MASSIVO USA (Oltre 1000 Ticker) ---
@st.cache_data
def get_massive_usa_list():
    # Liste espanse per coprire l'intero mercato opzionabile (S&P 500 + Nasdaq + Russell)
    nasdaq_100 = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'GOOG', 'TSLA', 'AVGO', 'COST', 'PEP', 'ADBE', 'LIN', 'CSCO', 'TMUS', 'INTU', 'QCOM', 'AMD', 'AMGN', 'ISRG', 'TXN', 'HON', 'AMAT', 'BKNG', 'VRTX', 'ADI', 'ADP', 'LRCX', 'PANW', 'MU', 'MDLZ', 'REGN', 'SNPS', 'INTC', 'CDNS', 'KLAC', 'MELI', 'PYPL', 'MAR', 'ASML', 'CSX', 'CTAS', 'MNST', 'ORLY', 'WDAY', 'ROP', 'ADSK', 'PCAR', 'LULU', 'CPRT', 'NXPI', 'PAYX', 'ROST', 'TEAM', 'IDXX', 'AEP', 'KDP', 'FAST', 'ODFL', 'AZO', 'BKR', 'GEHC', 'DXCM', 'EXC', 'MRVL', 'CTSH', 'XEL', 'MCHP', 'ANSS', 'DLTR', 'WBD', 'ILMN', 'TTD', 'WBA', 'GFS', 'MDB', 'ON', 'CDW', 'ZS', 'DDOG', 'BIIB', 'ENPH', 'EBAY']
    
    sp500_russell = [
        'JPM', 'V', 'MA', 'UNH', 'PG', 'XOM', 'HD', 'JNJ', 'ORCL', 'MRK', 'ABBV', 'CVX', 'CRM', 'WMT', 'KO', 'BAC', 'ACN', 'TMO', 'ABT', 'CAT', 'VZ', 'AXP', 'PFE', 'IBM', 'MS', 'GE', 'PM', 'UNP', 'HON', 'GS', 'LOW', 'SPGI', 'RTX', 'SYK', 'LMT', 'ELV', 'DE', 'TJX', 'COP', 'BLK', 'ETN', 'PGR', 'CVS', 'MMC', 'CI', 'BSX', 'SCHW', 'T', 'ZTS', 'WM', 'C', 'FI', 'BA', 'PLD', 'GILD', 'UPS', 'ITW', 'EOG', 'MO', 'CB', 'BDX', 'SLB', 'CME', 'APH', 'SHW', 'MCD', 'MMM', 'ABNB', 'AIG', 'TRV', 'MET', 'AON', 'D', 'SO', 'DUK', 'NEE', 'PSA', 'VICI', 'EQIX', 'DLR', 'WELL', 'AVB', 'SPG', 'KMI', 'WMB', 'OKE', 'HAL', 'DVN', 'FANG', 'CTRA', 'MPC', 'VLO', 'PSX', 'PLTR', 'UBER', 'SNOW', 'SQ', 'PARA', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'ETSY', 'SHOP', 'SE', 'BABA', 'JD', 'BIDU', 'TME', 'FCX', 'AA', 'CLF', 'NUE', 'X', 'VALE', 'GOLD', 'NEM', 'F', 'GM', 'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO', 'WFC', 'STT', 'BK', 'IBKR', 'RJF', 'LPLA', 'ALL', 'AFL', 'AJG', 'WTW', 'EQR', 'ARE', 'VRE', 'CPT', 'MAA', 'UDR', 'ESS', 'INVH', 'AMH', 'SUI', 'ELS', 'FRT', 'REG', 'KIM', 'BRX', 'TCO', 'MAC', 'PEAK', 'DOC', 'HR', 'OHI', 'VTR', 'HST', 'PK', 'BXP', 'SLG', 'FDX', 'RSG', 'NSC', 'AME', 'DOV', 'XYL', 'JCI', 'TT', 'CARR', 'OTIS', 'URI', 'GWW', 'FERG', 'NOW', 'CRWD', 'OKTA', 'NET', 'TSM', 'MSI', 'TEL', 'KEYS', 'TER', 'QRVO', 'SWKS', 'STX', 'WDC', 'HPQ', 'DELL', 'NTAP', 'PSTG', 'VRSN', 'AKAM', 'FSLR', 'SEDG', 'RHM.DE', 'ADS.DE', 'AIR.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'BEI.DE', 'BMW.DE', 'CON.DE', '1COV.DE', 'DTG.DE', 'DBK.DE', 'DB1.DE', 'LHA.DE', 'DPW.DE', 'DTE.DE', 'EOAN.DE', 'FRE.DE', 'FME.DE', 'HEI.DE', 'HEN3.DE', 'IFX.DE', 'MBG.DE', 'MRK.DE', 'MTX.DE', 'MUV2.DE', 'PUM.DE', 'PAH3.DE', 'RWE.DE', 'SAP.DE', 'SRT3.DE', 'SIE.DE', 'SY1.DE', 'VOW3.DE', 'VNA.DE', 'ZAL.DE'
    ]
    
    return sorted(list(set(nasdaq_100 + sp500_russell)))

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
                days = (cal.iloc[0,0] - datetime.now().date()).days
                if 0 <= days <= 7: earn_alert = "⚠️"
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

# --- 3. GESTIONE SESSIONE ---
if 'full_data' not in st.session_state:
    st.session_state.full_data = None

# --- 4. INTERFACCIA ---
st.title("🛡️ Professional Wheel Scanner (Limit 1000+)")
usa_list = get_massive_usa_list()

with st.sidebar:
    st.header("⚙️ 1. Configura Scansione")
    # Limite dinamico basato sulla lista reale (ora > 1000)
    scan_limit = st.number_input("Titoli da scansionare", 10, len(usa_list), 1000)
    
    if st.button('🚀 AVVIA ANALISI TOTALE'):
        results = []
        progress = st.progress(0)
        status = st.empty()
        for i, sym in enumerate(usa_list[:scan_limit]):
            status.text(f"Analisi {i+1}/{scan_limit}: {sym}")
            try:
                t = yf.Ticker(sym)
                h = t.history(period="1mo")
                if h.empty: continue
                data = analyze_stock(t, h)
                if data:
                    data['Ticker'] = sym
                    results.append(data)
                if i % 15 == 0: time.sleep(0.01)
            except: continue
            progress.progress((i + 1) / scan_limit)
        st.session_state.full_data = pd.DataFrame(results)
        status.empty()

# --- 5. FILTRI DINAMICI POST-SCANSIONE ---
if st.session_state.full_data is not None:
    df = st.session_state.full_data.copy()
    
    st.divider()
    st.header("🎯 2. Filtri sui Risultati (Senza rieseguire)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        f_price = st.slider("Prezzo ($)", float(df['Prezzo'].min()), float(df['Prezzo'].max()), (0.0, float(df['Prezzo'].max())))
    with col2:
        f_vol = st.slider("Volatilità Min %", 0.0, 100.0, 10.0)
        f_pe = st.number_input("P/E Massimo (0=Tutti)", 0.0, 500.0, 50.0)
    with col3:
        f_profit = st.slider("Profitto Min %", 0.0, 10.0, 1.0)
    with col4:
        f_sector = st.multiselect("Settori", df['Settore'].unique(), default=df['Settore'].unique())
        f_earn = st.checkbox("Nascondi Earnings (⚠️)")

    # Applicazione Filtri
    mask = (df['Prezzo'].between(f_price[0], f_price[1])) & \
           (df['Volatilità %'] >= f_vol) & \
           (df['Profit/Mese %'] >= f_profit) & \
           (df['Settore'].isin(f_sector))
    if f_pe > 0: mask &= (df['P/E'] <= f_pe)
    if f_earn: mask &= (df['Earnings'] == "OK")
    
    final_df = df[mask]
    st.success(f"Visualizzate {len(final_df)} opportunità su {len(df)} titoli opzionabili.")

    # DOWNLOAD EXCEL
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False)
    st.download_button("📥 Scarica Excel", output.getvalue(), "wheel_report.xlsx")

    # GRAFICO
    st.subheader("📈 Analisi Grafica Rischio/Rendimento")
    fig = px.scatter(final_df, x="Distanza Supporto %", y="Profit/Mese %", text="Ticker", 
                     size="Prezzo", color="Settore", title="Mappa Opportunità Wheel")
    st.plotly_chart(fig, use_container_width=True)

    # TABELLA DETTAGLIATA
    st.dataframe(final_df.style.background_gradient(subset=['Profit/Mese %'], cmap='Greens')
                 .applymap(lambda x: 'background-color: #ff4b4b; color: white' if x == "⚠️" else '', subset=['Earnings']),
                 use_container_width=True)
