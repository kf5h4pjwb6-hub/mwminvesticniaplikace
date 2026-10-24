
import streamlit as st
import yfinance as yf
import pandas as pd

# Nastavení stránky
st.set_page_config(page_title="Kompletní Investiční Analytik", page_icon="📈", layout="wide")

st.title("📊 Pokročilá Investiční Sledovačka & Analytika")
st.write("Sleduj detailní technické ukazatele, fundamenty i aktivitu velkých hráčů na jednom místě.")

# Vstup pro uživatele - název firmy (Ticker)
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_symbol = st.text_input("Zadej ticker firmy (např. AAPL, TSLA, MSFT, GOOGL):", "AAPL").upper()

if ticker_symbol:
    try:
        company = yf.Ticker(ticker_symbol)
        hist = company.history(period="1y") # Data za poslední rok pro výpočty
        info = company.info
        
        if hist.empty:
            st.error(f"Nepodařilo se najít data pro ticker '{ticker_symbol}'. Zkontroluj, zda je správně.")
        else:
            # Základní proměnné
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            
            # --- HLAVNÍ METRIKY NA VRCHOLU ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric(label=f"Aktuální cena ({ticker_symbol})", value=f"${current_price:.2f}", delta=f"{change:.2f}%")
            with m2:
                market_cap = info.get('marketCap', 0)
                st.metric(label="Tržní kapitalizace (Market Cap)", value=f"${market_cap / 1e9:.2f} mld." if market_cap else "N/A")
            with m3:
                pe_ratio = info.get('trailingPE', 'N/A')
                st.metric(label="P/E Ratio", value=f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
            with m4:
                div_yield = info.get('dividendYield', None)
                div_text = f"{div_yield * 100:.2f}%" if div_yield else "0.00% / N/A"
                st.metric(label="Dividendový výnos", value=div_text)

            st.markdown("---")

            # --- ZÁLOŽKY PRO PŘEHLEDNOST ---
            tab1, tab2, tab3 = st.tabs(["📈 Cenový vývoj & Historie", "🏢 Fundamentální analýza", "⚙️ Technické ukazatele & Risk"])

            # ZÁLOŽKA 1: Cenová historie
            with tab1:
                st.subheader("Cenová historie a objem obchodů")
                
                # Výběr období pro graf
                period_choice = st.selectbox("Vyber období grafu:", ["1 měsíc", "3 měsíce", "6 měsíců", "1 rok"], index=1)
                p_map = {"1 měsíc": "1mo", "3 měsíce": "3mo", "6 měsíců": "6mo", "1 rok": "1y"}
                hist_filtered = company.history(period=p_map[period_choice])

                st.line_chart(hist_filtered['Close'])
                
                st.markdown("### 📊 Detail období (poslední obchodní den)")
                last_row = hist.iloc[-1]
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Open (Otevření)", f"${last_row['Open']:.2f}")
                c2.metric("High (Maximum)", f"${last_row['High']:.2f}")
                c3.metric("Low (Minimum)", f"${last_row['Low']:.2f}")
                c4.metric("Close (Závěr)", f"${last_row['Close']:.2f}")
                c5.metric("Volume (Objem)", f"{int(last_row['Volume']):,}")

            # ZÁLOŽKA 2: Fundamentální analýza
            with tab2:
                st.subheader("Hospodaření a oceňovací ukazatele firmy")
                
                f1, f2, f3 = st.columns(3)
                with f1:
                    st.write(f"**Zisk na akcii (EPS):** `${info.get('trailingEps', 'N/A')}`")
                    st.write(f"**P/B Ratio (Cena / Účetní hodnota):** `{info.get('priceToBook', 'N/A')}`")
                with f2:
                    st.write(f"**P/S Ratio (Cena / Tržby):** `{info.get('priceToSalesTrailing12Months', 'N/A')}`")
                    st.write(f"**52týdenní maximum:** `${info.get('fiftyTwoWeekHigh', 'N/A')}`")
                with f3:
                    st.write(f"**52týdenní minimum:** `${info.get('fiftyTwoWeekLow', 'N/A')}`")
                    st.write(f"**Růst tržeb (meziroční):** `{info.get('revenueGrowth', 0) * 100:.2f}%`" if info.get('revenueGrowth') else "**Růst tržeb:** N/A")

                with st.expander("O společnosti a podnikání"):
                    st.write(info.get('longBusinessSummary', 'Popis není k dispozici.'))

            # ZÁLOŽKA 3: Technické ukazatele a souvislosti
            with tab3:
                st.subheader("Ukazatele dynamiky a rizika")
                
                t1, t2 = st.columns(2)
                with t1:
                    st.write(f"**Beta koeficient (citlivost vůči trhu):** `{info.get('beta', 'N/A')}`")
                    st.info("💡 **Beta = 1:** Akcie kopíruje trh | **Beta > 1:** Vyšší volatilita | **Beta < 1:** Větší stabilita")
                with t2:
                    # Jednoduchý výpočet 50denního klouzavého průměru z dat
                    if len(hist) >= 50:
                        sma_50 = hist['Close'].tail(50).mean()
                        st.write(f"**50denní klouzavý průměr (SMA 50):** `${sma_50:.2f}`")
                    else:
                        st.write("**50denní klouzavý průměr:** Nedostatek dat")
                        
                    institutional_held = info.get('heldPercentInstitutions', 0)
                    insider_held = info.get('heldPercentInsiders', 0)
                    st.write(f"**Podíl velkých institucí / fondů:** `{institutional_held * 100:.2f}%`")
                    st.write(f"**Podíl insiderů (vedení):** `{insider_held * 100:.2f}%`")

    except Exception as e:
        st.error(f"Došlo k chybě při načítání dat: {e}")
