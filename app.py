import streamlit as st
import yfinance as yf
import pandas as pd

# Nastavení stránky
st.set_page_config(page_title="24/7 Sledování Investorů & Akcií", page_icon="📈", layout="centered")

st.title("📊 Moje Investiční Sledovačka")
st.write("Sleduj ceny, vývoj a aktivitu velkých hráčů na jednom místě.")

# Vstup pro uživatele - název firmy (Ticker)
default_ticker = "AAPL"
ticker_symbol = st.text_input("Zadej ticker firmy (např. AAPL, TSLA, MSFT, GOOGL):", default_ticker).upper()

if ticker_symbol:
    try:
        # Načtení dat o firmě
        company = yf.Ticker(ticker_symbol)
        hist = company.history(period="3mo") # Data za poslední 3 měsíce
        info = company.info
        
        if hist.empty:
            st.error(f"Nepodařilo se najít data pro ticker '{ticker_symbol}'. Zkontroluj, zda je správně.")
        else:
            # Základní metrika ceny
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=f"Aktuální cena ({ticker_symbol})", value=f"${current_price:.2f}", delta=f"{change:.2f}%")
            with col2:
                market_cap = info.get('marketCap', 0)
                st.metric(label="Tržní kapitalizace", value=f"${market_cap / 1e9:.2f} mld." if market_cap else "N/A")

            # Graf vývoje ceny
            st.subheader("📈 Vývoj ceny za poslední 3 měsíce")
            st.line_chart(hist['Close'])

            # Sekce pro velké investory a instituce
            st.subheader("🐋 Velcí investoři & Instituce")
            institutional_held = info.get('heldPercentInstitutions', None)
            insider_held = info.get('heldPercentInsiders', None)
            
            if institutional_held:
                st.write(f"- **Podíl institucí (fondy, banky):** `{institutional_held * 100:.2f}%`")
            if insider_held:
                st.write(f"- **Podíl insiderů (vedení firmy):** `{insider_held * 100:.2f}%`")
                
            st.info("💡 Tip: Pro detailní hlášení fondů (formuláře 13F) sledujeme pohyby velkých hráčů jako Berkshire Hathaway či Vanguard.")

            # Základní popis firmy
            with st.expander("O společnosti"):
                st.write(info.get('longBusinessSummary', 'Popis není k dispozici.'))

    except Exception as e:
        st.error(f"Došlo k chybě při načítání dat: {e}")
