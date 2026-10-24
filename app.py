import streamlit as st
import yfinance as yf
import pandas as pd

# Nastavení stránky
st.set_page_config(page_title="Kompletní Investiční Analytik", page_icon="📈", layout="wide")

st.title("📊 Pokročilá Investiční Sledovačka & Analytika")
st.write("Sleduj ceny, technické ukazatele, fundamenty i aktivitu velkých hráčů a insiderů z byznysu.")

# Vstup pro uživatele - název firmy (Ticker)
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_symbol = st.text_input("Zadej ticker firmy (např. AAPL, TSLA, MSFT, GOOGL):", "AAPL").upper()

if ticker_symbol:
    try:
        company = yf.Ticker(ticker_symbol)
        hist = company.history(period="1y")
        info = company.info
        
        if hist.empty:
            st.error(f"Nepodařilo se najít data pro ticker '{ticker_symbol}'. Zkontroluj, zda je správně.")
        else:
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            
            # --- HLAVNÍ METRIKY ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric(label=f"Aktuální cena ({ticker_symbol})", value=f"${current_price:.2f}", delta=f"{change:.2f}%")
            with m2:
                market_cap = info.get('marketCap', 0)
                st.metric(label="Tržní kapitalizace", value=f"${market_cap / 1e9:.2f} mld." if market_cap else "N/A")
            with m3:
                pe_ratio = info.get('trailingPE', 'N/A')
                st.metric(label="P/E Ratio", value=f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
            with m4:
                div_yield = info.get('dividendYield', None)
                div_text = f"{div_yield * 100:.2f}%" if div_yield else "0.00% / N/A"
                st.metric(label="Dividendový výnos", value=div_text)

            st.markdown("---")

            # --- ZÁLOŽKY ---
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Cenová historie", 
                "🏢 Fundamentální analýza", 
                "⚙️ Technické ukazatele", 
                "🐋 Velcí investoři & Insiders"
            ])

            # ZÁLOŽKA 1: Cenová historie
            with tab1:
                st.subheader("Cenová historie a objem obchodů")
                period_choice = st.selectbox("Vyber období grafu:", ["1 měsíc", "3 měsíce", "6 měsíců", "1 rok"], index=1)
                p_map = {"1 měsíc": "1mo", "3 měsíce": "3mo", "6 měsíců": "6mo", "1 rok": "1y"}
                hist_filtered = company.history(period=p_map[period_choice])
                st.line_chart(hist_filtered['Close'])
                
                st.markdown("### 📊 Detail posledního obchodního dne")
                last_row = hist.iloc[-1]
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Open", f"${last_row['Open']:.2f}")
                c2.metric("High", f"${last_row['High']:.2f}")
                c3.metric("Low", f"${last_row['Low']:.2f}")
                c4.metric("Close", f"${last_row['Close']:.2f}")
                c5.metric("Volume", f"{int(last_row['Volume']):,}")

            # ZÁLOŽKA 2: Fundamentální analýza
            with tab2:
                st.subheader("Hospodaření a oceňovací ukazatele firmy")
                f1, f2, f3 = st.columns(3)
                with f1:
                    st.write(f"**Zisk na akcii (EPS):** `${info.get('trailingEps', 'N/A')}`")
                    st.write(f"**P/B Ratio:** `{info.get('priceToBook', 'N/A')}`")
                with f2:
                    st.write(f"**P/S Ratio:** `{info.get('priceToSalesTrailing12Months', 'N/A')}`")
                    st.write(f"**52týdenní maximum:** `${info.get('fiftyTwoWeekHigh', 'N/A')}`")
                with f3:
                    st.write(f"**52týdenní minimum:** `${info.get('fiftyTwoWeekLow', 'N/A')}`")
                    st.write(f"**Růst tržeb:** `{info.get('revenueGrowth', 0) * 100:.2f}%`" if info.get('revenueGrowth') else "**Růst tržeb:** N/A")

                with st.expander("O společnosti"):
                    st.write(info.get('longBusinessSummary', 'Popis není k dispozici.'))

            # ZÁLOŽKA 3: Technické ukazatele
            with tab3:
                st.subheader("Ukazatele dynamiky a rizika")
                t1, t2 = st.columns(2)
                with t1:
                    st.write(f"**Beta koeficient:** `{info.get('beta', 'N/A')}`")
                    st.info("💡 **Beta = 1:** Kopíruje trh | **Beta > 1:** Vyšší volatilita")
                with t2:
                    if len(hist) >= 50:
                        sma_50 = hist['Close'].tail(50).mean()
                        st.write(f"**50denní klouzavý průměr (SMA 50):** `${sma_50:.2f}`")
                    else:
                        st.write("**SMA 50:** Nedostatek dat")

            # ZÁLOŽKA 4: Velcí investoři a Insiders (NOVÉ)
            with tab4:
                st.subheader("🐋 Sledování velkých hráčů, fondů a vedení (Insider Trading)")
                
                institutional_held = info.get('heldPercentInstitutions', 0)
                insider_held = info.get('heldPercentInsiders', 0)
                
                col_i1, col_i2 = st.columns(2)
                col_i1.metric("Podíl velkých fondů a institucí", f"{institutional_held * 100:.2f}%" if institutional_held else "N/A")
                col_i2.metric("Podíl insiderů (vedení a ředitelé)", f"{insider_held * 100:.2f}%" if insider_held else "N/A")
                
                st.markdown("---")
                st.markdown("### 🏛️ Hlavní institucionální držitelé (Formuláře 13F)")
                st.write("Tyto velké fondy drží největší podíly v této společnosti:")
                
                # Pokus o vytažení tabulky majoritních vlastníků z yfinance
                try:
                    major_holders = company.major_holders
                    if major_holders is not None and not major_holders.empty:
                        st.dataframe(major_holders, use_container_width=True)
                    else:
                        st.info("Tabulka majoritních vlastníků není pro tento ticker plně dostupná.")
                except Exception:
                    st.info("Data o majoritních vlastnících se nepodařilo načíst.")

                st.markdown("### 👔 Transakce insiderů (Formulář 4 – Nákupy/Prodeje vedení)")
                st.write("Zde se sleduje, zda samotní ředitelé, CEO nebo členové správní rady akcie dokupují, nebo naopak odprodávají:")
                
                try:
                    insider_transactions = company.insider_transactions
                    if insider_transactions is not None and not insider_transactions.empty:
                        st.dataframe(insider_transactions, use_container_width=True)
                    else:
                        st.info("Záznamy o transakcích insiderů pro toto období nejsou k dispozici.")
                except Exception:
                    st.info("Tabulku transakcí insiderů se nepodařilo načíst.")

    except Exception as e:
        st.error(f"Došlo k chybě při načítání dat: {e}")
