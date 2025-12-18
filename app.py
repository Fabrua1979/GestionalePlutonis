import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
import io
import plotly.express as px

st.set_page_config(page_title="Professional Wheel Scanner", layout="wide")

# --- 1. FUNZIONE PER SCARICARE TUTTI I TICKER USA ---
@st.cache_data
def get_all_us_tickers():
    # Scarichiamo liste da fonti pubbliche affidabili per avere TUTTI i titoli
    try:
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        nasdaq100 = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[4]['Ticker'].tolist()
        # Unione e pulizia (rimozione duplicati)
        all_tickers = sorted(list(set(sp500 + nasdaq100)))
        return all_tickers
    except:
        # Fallback in caso di errore connessione Wikipedia
        return ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'BRK-B']

# --- 2. MOTORE DI ANALISI PROFESSIONALE ---
def analyze_stock(t_obj, hist):
    try:
        # Verifica Opzioni: Se non ci sono, scartiamo il titolo
        if not t_obj.options: return None
        
        cp = hist['Close'].iloc[-1]
        info = t_obj.info
        
        # Calcoli Tecnici
        std_dev = hist['Close'].pct_change().dropna().std()
        vol_month = std_dev * (21**0.5)
        strike = round(cp * (1 - vol_month) * 2) / 2
        profit_month = ((cp * vol_month * 0.25) / strike) * 100
        
        # Alert Earnings (Prossimi 7 giorni)
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
            "Dist. Supp %": round(((cp - hist['Low'].tail(20).min()) / cp) * 100, 2),
            "Earnings": earn_alert,
            "Volatilità %": round(vol_month * 100, 2)
        }
    except: return None

# --- 3. INTERFACCIA ---
st.title("🛡️ Wheel Strategy Professional Scanner: USA TOTAL")
all_us_list = get_all_us_tickers()

with st.sidebar:
    st.header("⚙️ Parametri Scansione")
    scan_limit = st.number_input("Quanti titoli scansionare? (Pù sono, più tempo serve)", 10, len(all_us_list), 300)
    st.divider()
    st.header("🎯 Filtri Post-Analisi")
    min_profit = st.slider("Profitto Minimo Mensile %", 0.0, 10.0, 1.0)
    max_dist = st.slider("Distanza Max Supporto %", 0.0, 50.0, 20.0)
    only_safe = st.checkbox("Nascondi titoli con Earnings (⚠️)")

st.info(f"Database pronto: **{len(all_us_list)}** titoli identificati (S&P 500 + Nasdaq 100).")

# --- 4. ESECUZIONE ---
if st.button('🚀 AVVIA ANALISI TOTALE'):
    results = []
    progress = st.progress(0)
    status = st.empty()
    
    tickers = all_us_list[:int(scan_limit)]
    
    for i, sym in enumerate(tickers):
        status.text(f"Analisi {i+1}/{len(tickers)}: {sym}")
        try:
            t = yf.Ticker(sym.replace('.', '-')) # Gestione simboli come BRK.B
            h = t.history(period="1mo")
            if h.empty: continue
            
            res = analyze_stock(t, h)
            if res:
                res['Ticker'] = sym
                results.append(res)
            time.sleep(0.01)
        except: continue
        progress.progress((i + 1) / len(tickers))

    status.empty()
    if results:
        df = pd.DataFrame(results)
        
        # Applicazione Filtri Utente
        df = df[df['Profit/Mese %'] >= min_profit]
        df = df[df['Dist. Supp %'] <= max_dist]
        if only_safe: df = df[df['Earnings'] == "OK"]
        
        st.success(f"Trovate {len(df)} opportunità opzionabili!")

        # ESPORTAZIONE EXCEL
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Wheel_Opportunities')
        st.download_button("📥 Scarica Risultati Excel", output.getvalue(), f"wheel_scan_{datetime.now().date()}.xlsx")

        # GRAFICO RISCHIO/RENDIMENTO
        st.subheader("📈 Mappa Opportunità Professionale")
        fig = px.scatter(df, x="Dist. Supp %", y="Profit/Mese %", text="Ticker", 
                         size="Prezzo", color="Profit/Mese %",
                         hover_data=['Settore', 'Strike Consigliato', 'P/E'],
                         title="Alto Rendimento (Alto Y) e Basso Rischio (Basso X)")
        st.plotly_chart(fig, use_container_width=True)

        # TABELLA DETTAGLIATA
        st.subheader("📋 Dettagli Operativi")
        st.dataframe(
            df.style.background_gradient(subset=['Profit/Mese %'], cmap='Greens')
            .applymap(lambda x: 'background-color: #ff4b4b; color: white' if x == "⚠️" else '', subset=['Earnings'])
            .format({'Prezzo': '{:.2f}$', 'Profit/Mese %': '{:.2f}%', 'P/E': '{:.1f}'}),
            use_container_width=True
        )
    else:
        st.error("Nessun titolo trovato con questi filtri. Prova ad allargare i parametri.")
