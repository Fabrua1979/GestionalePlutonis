import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Global Wheel Scanner", layout="wide")

# --- 1. CHIAVE API ---
API_KEY = st.sidebar.text_input("Inserisci FMP API Key", type="password", value="sQJgPn10EvTF6U4HzkVRukBF0Y0ijMrL")

def get_fmp(endpoint, params=""):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}?apikey={API_KEY}{params}"
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# --- 2. FILTRI LATERALI ---
st.sidebar.header("🔍 Filtri Ricerca Totale")
mcap_limit = st.sidebar.slider("Market Cap Min (Miliardi $)", 2, 500, 10)
div_limit = st.sidebar.number_input("Dividendo Minimo (%)", value=1.0)
max_results = st.sidebar.number_input("Numero max titoli da analizzare", value=100)

st.title("🌐 Global Wheel Market Scanner")
st.write("Scansione profonda su tutti i mercati USA (NASDAQ, NYSE, AMEX).")

if st.button('🚀 AVVIA SCANSIONE COMPLETA'):
    with st.spinner("Recupero database titoli globale..."):
        # Recuperiamo la lista di TUTTI i titoli scambiati (migliaia)
        # Questo endpoint è più stabile dello screener
        full_list = get_fmp("stock/list")
    
    if full_list:
        # Filtriamo solo azioni ordinarie USA (escludiamo ETF e fondi)
        base_stocks = [s for s in full_list if s.get('type') == 'stock' and s.get('exchangeShortName') in ['NASDAQ', 'NYSE', 'AMEX']]
        
        results = []
        progress_bar = st.progress(0)
        status = st.empty()
        
        count = 0
        for s in base_stocks:
            if count >= max_results: break
            
            symbol = s['symbol']
            status.text(f"Analisi fondamentale di {symbol} ({count}/{max_results})...")
            
            # Recupero Profilo per verificare Market Cap e Dividendo
            profile = get_fmp(f"profile/{symbol}")
            if profile and len(profile) > 0:
                p = profile[0]
                mcap = p.get('mktCap', 0) / 1e9
                div = p.get('lastDiv', 0)
                
                # Applichiamo i tuoi parametri richiesti
                if mcap >= mcap_limit and div >= div_limit:
                    price = p.get('price', 0)
                    strike = round((price * 0.90) * 2) / 2
                    
                    results.append({
                        "Ticker": symbol,
                        "Nome": p.get('companyName', 'N/A'),
                        "Settore": p.get('sector', 'N/A'),
                        "Prezzo": price,
                        "Strike Put (-10%)": strike,
                        "Dividendo %": div,
                        "Market Cap (B)": round(mcap, 2)
                    })
                    count += 1
            
            progress_bar.progress(count / max_results)

        status.empty()
        if results:
            df = pd.DataFrame(results)
            st.success(f"Scansione terminata! Trovate {len(df)} opportunità.")
            
            # Tabella con formattazione colori
            st.dataframe(df.style.background_gradient(subset=['Dividendo %'], cmap='YlGn'), use_container_width=True)
            
            # Export CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica Report Completo", csv, "wheel_scan_results.csv", "text/csv")
        else:
            st.error("Nessun titolo trovato con questi parametri o errore chiave API.")
    else:
        st.error("Impossibile connettersi al database FMP. Verifica l'email di conferma account.")
