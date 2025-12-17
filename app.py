import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Test Connessione FMP")

# Recupero chiave
if "FMP_API_KEY" in st.secrets:
    API_KEY = st.secrets["FMP_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Inserisci API Key", value="uZJbm6FkDS56ktyFfzvh5flhePsbh4rz")

st.title("🔌 Test di Connessione Rapido")

if st.button("ESEGUI TEST"):
    # Proviamo una singola chiamata semplicissima (Profilo Apple)
    url = f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={API_KEY}"
    
    with st.spinner("Contattando i server FMP..."):
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            st.success("✅ CONNESSIONE RIUSCITA!")
            st.write(f"Prezzo attuale di AAPL ricevuto: {data[0]['price']}$")
            st.info("Ora puoi ricaricare il codice completo, la tua API è attiva e funzionante.")
        else:
            st.error(f"❌ Errore API: {response.status_code}. Controlla la chiave.")
