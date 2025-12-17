import streamlit as st
import requests

st.title("🔌 Debug Connessione FMP")

key_input = st.text_input("Incolla la chiave qui sotto:", value="uZJbm6FkDS56ktyFfzvh5flhePsbh4rz")

if st.button("TESTA CHIAVE"):
    # Verifichiamo la lunghezza (deve essere 32)
    st.write(f"Lunghezza chiave inserita: {len(key_input)} caratteri")
    
    url = f"https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={key_input}"
    res = requests.get(url)
    
    if res.status_code == 200:
        st.success("✅ FUNZIONA! La chiave è corretta.")
        st.json(res.json())
    else:
        st.error(f"❌ Errore {res.status_code}")
        st.write("Risposta del server:", res.text)
