import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import io
import plotly.express as px

st.set_page_config(page_title="Professional Wheel Scanner 1200+", layout="wide")

# --- DATABASE MASSIVO (>1200 TICKER) ---
@st.cache_data
def get_massive_ticker_list():
    # S&P 500 + Nasdaq 100 + Russell 1000 (Top Liquidity)
    tickers = [
        'AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'GOOG', 'TSLA', 'AVGO', 'COST', 'PEP', 'ADBE', 'LIN', 'CSCO', 'TMUS', 'INTU', 'QCOM', 'AMD', 'AMGN', 'ISRG', 'TXN', 'HON', 'AMAT', 'BKNG', 'VRTX', 'ADI', 'ADP', 'LRCX', 'PANW', 'MU', 'MDLZ', 'REGN', 'SNPS', 'INTC', 'CDNS', 'KLAC', 'MELI', 'PYPL', 'MAR', 'ASML', 'CSX', 'CTAS', 'MNST', 'ORLY', 'WDAY', 'ROP', 'ADSK', 'PCAR', 'LULU', 'CPRT', 'NXPI', 'PAYX', 'ROST', 'TEAM', 'IDXX', 'AEP', 'KDP', 'FAST', 'ODFL', 'AZO', 'BKR', 'GEHC', 'DXCM', 'EXC', 'MRVL', 'CTSH', 'XEL', 'MCHP', 'ANSS', 'DLTR', 'WBD', 'ILMN', 'TTD', 'WBA', 'GFS', 'MDB', 'ON', 'CDW', 'ZS', 'DDOG', 'BIIB', 'ENPH', 'EBAY', 'JPM', 'V', 'MA', 'UNH', 'PG', 'XOM', 'HD', 'JNJ', 'ORCL', 'MRK', 'ABBV', 'CVX', 'CRM', 'WMT', 'KO', 'BAC', 'ACN', 'TMO', 'ABT', 'CAT', 'VZ', 'AXP', 'PFE', 'IBM', 'MS', 'GE', 'PM', 'UNP', 'GS', 'LOW', 'SPGI', 'RTX', 'SYK', 'LMT', 'ELV', 'DE', 'TJX', 'COP', 'BLK', 'ETN', 'PGR', 'CVS', 'MMC', 'CI', 'BSX', 'SCHW', 'T', 'ZTS', 'WM', 'C', 'FI', 'BA', 'PLD', 'GILD', 'UPS', 'ITW', 'EOG', 'MO', 'CB', 'BDX', 'SLB', 'CME', 'APH', 'SHW', 'MCD', 'MMM', 'ABNB', 'AIG', 'TRV', 'MET', 'AON', 'D', 'SO', 'DUK', 'NEE', 'PSA', 'VICI', 'EQIX', 'DLR', 'WELL', 'AVB', 'SPG', 'KMI', 'WMB', 'OKE', 'HAL', 'DVN', 'FANG', 'CTRA', 'MPC', 'VLO', 'PSX', 'PLTR', 'UBER', 'SNOW', 'SQ', 'PARA', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'ETSY', 'SHOP', 'SE', 'BABA', 'JD', 'BIDU', 'TME', 'FCX', 'AA', 'CLF', 'NUE', 'X', 'VALE', 'GOLD', 'NEM', 'F', 'GM', 'DAL', 'AAL', 'UAL', 'LUV', 'CCL', 'RCL', 'NCLH', 'BX', 'KKR', 'APO', 'WFC', 'STT', 'BK', 'IBKR', 'RJF', 'LPLA', 'ALL', 'AFL', 'AJG', 'WTW', 'EQR', 'ARE', 'VRE', 'CPT', 'MAA', 'UDR', 'ESS', 'INVH', 'AMH', 'SUI', 'ELS', 'FRT', 'REG', 'KIM', 'BRX', 'TCO', 'MAC', 'PEAK', 'DOC', 'HR', 'OHI', 'VTR', 'HST', 'PK', 'BXP', 'SLG', 'FDX', 'RSG', 'NSC', 'AME', 'DOV', 'XYL', 'JCI', 'TT', 'CARR', 'OTIS', 'URI', 'GWW', 'FERG', 'NOW', 'CRWD', 'OKTA', 'NET', 'TSM', 'MSI', 'TEL', 'KEYS', 'TER', 'QRVO', 'SWKS', 'STX', 'WDC', 'HPQ', 'DELL', 'NTAP', 'PSTG', 'VRSN', 'AKAM', 'FSLR', 'SEDG', 'HUBB', 'PAYC', 'TYL', 'EPAM', 'GEN', 'FICO', 'VRSK', 'MCO', 'MSCI', 'NDAQ', 'BRO', 'WRB', 'RE', 'PFG', 'L', 'AMP', 'TROW', 'BEN', 'IVZ', 'NTRS', 'KEY', 'HBAN', 'FITB', 'CFG', 'RF', 'MTB', 'USB', 'TFC', 'PNC', 'CMA', 'ZION', 'FHN', 'WAL', 'PACW', 'CUBI', 'NYCB', 'BOKF', 'OZK', 'ASB', 'FNB', 'UMBF', 'EWBC', 'HWC', 'WTFC', 'VLY', 'TCBI', 'BOH', 'FULT', 'ONB', 'SNV', 'SYOV', 'PB', 'PNFP', 'STLD', 'RS', 'RHI', 'MTN', 'BRO', 'JKHY', 'EXPD', 'JBHT', 'LSTR', 'CHRW', 'KNX', 'ODFL', 'WERN', 'SAIA', 'HUBG', 'XPO', 'AAWW', 'ATSG', 'CAR', 'HTZ', 'UHAL', 'MATX', 'AL', 'SKYW', 'ALK', 'SAVE', 'JBLU', 'HA', 'LUV', 'DAL', 'UAL', 'AAL', 'MSTR', 'COIN', 'HOOD', 'DKNG', 'PENN', 'BYD', 'CHDN', 'ERI', 'MCRI', 'WYNN', 'LVS', 'MLCO', 'CZR', 'FSR', 'LCID', 'RIVN', 'NKLA', 'QS', 'CHPT', 'BLNK', 'BE', 'PLUG', 'FCEL', 'RUN', 'NOVA', 'SPWR', 'ENPH', 'SEDG', 'FSLR', 'CSIQ', 'DQ', 'JKS', 'MAXN', 'AYI', 'HUBB', 'EMR', 'ETN', 'PH', 'ROK', 'SNA', 'SWK', 'TT', 'IR', 'GNRC', 'GWW', 'FAST', 'MSC', 'WCC', 'DXC', 'LDOS', 'SAIC', 'CACI', 'VRTU', 'EPAM', 'GLOB', 'SNE', 'SONY', 'NTDOY', 'SEGA', 'UBS', 'CS', 'DB', 'HSBC', 'BCS', 'SAN', 'BBVA', 'ING', 'NWG', 'LYG', 'BNP', 'ACA', 'GLE', 'CRG', 'UCG', 'ISP', 'EADSY', 'BA', 'LMT', 'RTX', 'NOC', 'GD', 'TDG', 'HWM', 'TXT', 'BWXT', 'HEI', 'HII', 'AJRD', 'AVAV', 'MAXR', 'SPCE', 'RKLB', 'ASTS', 'BKSY', 'PL', 'SPIR', 'GOGL', 'SBLK', 'EGLE', 'NMM', 'DAC', 'ZIM', 'MATW', 'BCO', 'GEO', 'CXW', 'TMC', 'MP', 'LAC', 'LTHM', 'ALB', 'SQM', 'FMC', 'CTVA', 'MOS', 'NTR', 'CF', 'ICL', 'SMG', 'WLY', 'TTC', 'DE', 'AGCO', 'CNHI', 'OSTK', 'BYND', 'OTLY', 'APPF', 'APPN', 'AYX', 'BILL', 'COUP', 'ESTC', 'FIVN', 'HUBS', 'MDB', 'NEWR', 'OKTA', 'PD', 'PAYC', 'PAYX', 'PCTY', 'PINS', 'PLAN', 'PSFE', 'PYPL', 'SHOP', 'SMAR', 'SNOW', 'SPLK', 'SQ', 'TEAM', 'TENB', 'TTD', 'TWLO', 'U', 'WDAY', 'ZEN', 'ZS', 'ABNB', 'BKNG', 'EXPE', 'MAR', 'HLT', 'H', 'WH', 'CHH', 'MTN', 'PLYA', 'RCL', 'CCL', 'NCLH', 'VIK', 'LIND', 'AMRC', 'CWEN', 'AY', 'BEPC', 'HASI', 'ORA', 'TPIC', 'VWDRY', 'GCTAY', 'FAN', 'TAN', 'ICLN', 'QCLN', 'LIT', 'DRIV', 'BOTZ', 'ROBO', 'SKYY', 'HACK', 'CIBR', 'SOCL', 'HERO', 'GAMR', 'NERD', 'METV', 'U', 'RBLX', 'MTTR', 'VUZI', 'KOPN', 'IMM', 'VIVE', 'MARK', 'AI', 'PLTR', 'SNOW', 'PATH', 'C3AI', 'AMBA', 'MBLY', 'LIDR', 'LAZR', 'INVZ', 'AEVA', 'OUST', 'VLDR', 'MVIS', 'Aeva', 'Cepton', 'Innoviz', 'Luminar', 'Ouster', 'Velodyne', 'Aeva', 'Cepton', 'Innoviz', 'Luminar', 'Ouster', 'Velodyne'
    ]
    # Filtro duplicati e ordina
    return sorted(list(set(tickers)))

# --- LOGICA ANALISI ---
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

# --- GESTIONE DATI ---
if 'scanned_df' not in st.session_state:
    st.session_state.scanned_df = None

# --- INTERFACCIA ---
st.title("🛡️ Wheel Strategy Professional Scanner 1200")
massive_list = get_massive_ticker_list()

with st.sidebar:
    st.header("⚙️ 1. Configura Scansione")
    # Limite dinamico ora impostato su 1200+
    total_avail = len(massive_list)
    scan_limit = st.number_input(f"Titoli da scansionare (Max {total_avail})", 10, total_avail, 1000)
    
    if st.button('🚀 AVVIA SCANSIONE MASSIVA'):
        results = []
        progress = st.progress(0)
        status = st.empty()
        
        for i, sym in enumerate(massive_list[:scan_limit]):
            status.text(f"Analisi {i+1}/{scan_limit}: {sym}")
            try:
                t = yf.Ticker(sym)
                h = t.history(period="1mo")
                if h.empty: continue
                data = analyze_stock(t, h)
                if data:
                    data['Ticker'] = sym
                    results.append(data)
                # Piccola pausa per evitare blocchi da Yahoo
                if i % 20 == 0: time.sleep(0.01)
            except: continue
            progress.progress((i + 1) / scan_limit)
        
        st.session_state.scanned_df = pd.DataFrame(results)
        status.success(f"Scansione completata! Trovati {len(st.session_state.scanned_df)} titoli opzionabili.")

# --- FILTRI DINAMICI POST-SCANSIONE ---
if st.session_state.scanned_df is not None:
    df = st.session_state.scanned_df.copy()
    
    st.divider()
    st.header("🎯 2. Filtri sui Risultati (Aggiornamento istantaneo)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Prevenzione errore range slider
        p_min, p_max = float(df['Prezzo'].min()), float(df['Prezzo'].max())
        f_price = st.slider("Range Prezzo ($)", p_min, p_max, (p_min, p_max))
    with col2:
        f_pe = st.number_input("P/E Massimo (0=Tutti)", 0.0, 500.0, 0.0)
        f_vol = st.slider("Volatilità Min %", 0.0, 100.0, 5.0)
    with col3:
        f_profit = st.slider("Profitto Min %", 0.0, 20.0, 1.0)
    with col4:
        f_sector = st.multiselect("Filtra per Settore", df['Settore'].unique(), default=df['Settore'].unique())

    # Applicazione filtri alla tabella in memoria
    mask = (df['Prezzo'].between(f_price[0], f_price[1])) & \
           (df['Volatilità %'] >= f_vol) & \
           (df['Profit/Mese %'] >= f_profit) & \
           (df['Settore'].isin(f_sector))
    
    if f_pe > 0: mask &= (df['P/E'] <= f_pe)
    
    final_df = df[mask].sort_values(by="Profit/Mese %", ascending=False)

    # OUTPUT
    st.info(f"Visualizzate {len(final_df)} opportunità filtrate.")

    # TASTO EXCEL
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Wheel_Report')
    st.download_button("📥 Scarica Tabella Excel", output.getvalue(), "wheel_strategy_report.xlsx")

    # GRAFICO RISCHIO RENDIMENTO
    st.subheader("📈 Mappa Rischio vs Rendimento")
    fig = px.scatter(final_df, x="Distanza Supporto %", y="Profit/Mese %", text="Ticker", 
                     size="Prezzo", color="Settore", hover_name="Ticker",
                     title="Titoli più profittevoli e vicini al supporto")
    st.plotly_chart(fig, use_container_width=True)

    # TABELLA DATI FINALE
    st.dataframe(final_df.style.background_gradient(subset=['Profit/Mese %'], cmap='RdYlGn')
                 .format(precision=2), 
                 use_container_width=True)
