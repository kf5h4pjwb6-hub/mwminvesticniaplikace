import streamlit as st
import yfinance as yf
import pandas as pd

# Nastavení stránky na šířku pro lepší přehlednost
st.set_page_config(page_title="Pro Akciový Analytik 24/7", page_icon="📈", layout="wide")

st.title("📊 Kompletní Analytický Nástroj Pro Akcie")
st.write("Profesionální data pro technickou, fundamentální i sentimentální analýzu trhu.")

# Vstup pro uživatele - název firmy (Ticker)
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_symbol = st.text_input("Zadej ticker firmy (např. AAPL, TSLA, MSFT, GOOGL, NVDA):", "AAPL").upper()

if ticker_symbol:
    try:
        company = yf.Ticker(ticker_symbol)
        hist = company.history(period="1y")
        info = company.info
        
        if hist.empty:
            st.error(f"Nepodařilo se najít data pro ticker '{ticker_symbol}'. Zkontroluj, zda je správně zadaný.")
        else:
            # Hlavní metriky
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = ((current_price - prev_close) / prev_close) * 100
            
            # --- HLAVNÍ METRIKY NA NAHOŘE ---
            st.markdown("---")
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric(label=f"Aktuální cena ({ticker_symbol})", value=f"${current_price:.2f}", delta=f"{change:.2f}%")
            with m2:
                market_cap = info.get('marketCap', 0)
                st.metric(label="Market Cap", value=f"${market_cap / 1e9:.2f} mld." if market_cap else "N/A")
            with m3:
                pe_ratio = info.get('trailingPE', 'N/A')
                st.metric(label="P/E Ratio", value=f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
            with m4:
                target_price = info.get('targetMeanPrice', 'N/A')
                st.metric(label="Cílová cena Wall St.", value=f"${target_price:.2f}" if isinstance(target_price, (int, float)) else "N/A")
            with m5:
                div_yield = info.get('dividendYield', None)
                div_text = f"{div_yield * 100:.2f}%" if div_yield else "0.00% / N/A"
                st.metric(label="Div. výnos", value=div_text)

            st.markdown("---")

            # --- ZÁLOŽKOVÝ SYSTÉM PRO INVESTORY ---
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📈 Cenová historie & Trend", 
                "🏢 Fundamenty & Hospodaření", 
                "⚙️ Technické ukazatele & RSI", 
                "🐋 Velcí investoři & Insiders",
                "🎯 Názory analytiků",
                "📰 Historie & Komentáře"
            ])

            # ZÁLOŽKA 1: Cenová historie
            with tab1:
                st.subheader("Cenový vývoj, klouzavé průměry a objem obchodů")
                period_choice = st.selectbox("Vyber období grafu:", ["1 měsíc", "3 měsíce", "6 měsíců", "1 rok"], index=3)
                p_map = {"1 měsíc": "1mo", "3 měsíce": "3mo", "6 měsíců": "6mo", "1 rok": "1y"}
                hist_filtered = company.history(period=p_map[period_choice])
                
                # Výpočet klouzavých průměrů SMA 50 a SMA 200 pro graf
                hist_filtered['SMA_50'] = hist_filtered['Close'].rolling(window=50).mean()
                hist_filtered['SMA_200'] = hist_filtered['Close'].rolling(window=200).mean()

                st.line_chart(hist_filtered[['Close', 'SMA_50', 'SMA_200']])
                st.caption("💡 Legenda: Modrá = Cena | Oranžová/Zelená = 50denní a 200denní klouzavé průměry (SMA)")

                st.markdown("### 📊 Detail posledního obchodního dne (OHLC & Volume)")
                last_row = hist.iloc[-1]
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Open (Otevření)", f"${last_row['Open']:.2f}")
                c2.metric("High (Maximum)", f"${last_row['High']:.2f}")
                c3.metric("Low (Minimum)", f"${last_row['Low']:.2f}")
                c4.metric("Close (Závěr)", f"${last_row['Close']:.2f}")
                c5.metric("Volume (Objem)", f"{int(last_row['Volume']):,}")

            # ZÁLOŽKA 2: Fundamentální analýza
            with tab2:
                st.subheader("Oceňovací ukazatele a ziskovost")
                f1, f2, f3 = st.columns(3)
                with f1:
                    st.write(f"**EPS (Zisk na akcii):** `${info.get('trailingEps', 'N/A')}`")
                    st.write(f"**P/E Ratio (Trailing):** `{info.get('trailingPE', 'N/A')}`")
                    st.write(f"**P/E Ratio (Forward):** `{info.get('forwardPE', 'N/A')}`")
                with f2:
                    st.write(f"**P/B Ratio (Cena/Účetní hodnota):** `{info.get('priceToBook', 'N/A')}`")
                    st.write(f"**P/S Ratio (Cena/Tržby):** `{info.get('priceToSalesTrailing12Months', 'N/A')}`")
                    st.write(f"**EV/EBITDA:** `{info.get('enterpriseToEbitda', 'N/A')}`")
                with f3:
                    profit_margin = info.get('profitMargins', 0)
                    rev_growth = info.get('revenueGrowth', 0)
                    st.write(f"**Čistá zisková marže:** `{profit_margin * 100:.2f}%`" if profit_margin else "**Zisková marže:** N/A")
                    st.write(f"**Růst tržeb (y/y):** `{rev_growth * 100:.2f}%`" if rev_growth else "**Růst tržeb:** N/A")
                    st.write(f"**Celkový dluh vs. Hotovost:** `${info.get('totalDebt', 0)/1e9:.2f} mld.` / `${info.get('totalCash', 0)/1e9:.2f} mld.`")

                with st.expander("Profil a popis společnosti"):
                    st.write(info.get('longBusinessSummary', 'Popis není k dispozici.'))

            # ZÁLOŽKA 3: Technické ukazatele & RSI
            with tab3:
                st.subheader("Ukazatele volatility, dynamiky a síly trendu")
                t1, t2 = st.columns(2)
                with t1:
                    st.write(f"**Beta koeficient (citlivost vůči trhu):** `{info.get('beta', 'N/A')}`")
                    st.write(f"**52týdenní maximum:** `${info.get('fiftyTwoWeekHigh', 'N/A')}`")
                    st.write(f"**52týdenní minimum:** `${info.get('fiftyTwoWeekLow', 'N/A')}`")
                with t2:
                    # Výpočet RSI (Relative Strength Index - 14 dní)
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs)).iloc[-1]
                    
                    st.write(f"**RSI (Relative Strength Index - 14 dní):** `{rsi:.2f}`")
                    if rsi > 70:
                        st.warning("⚠️ RSI je nad 70 – Akcie může být přeprodávaná/přeboupená (riziko korekce).")
                    elif rsi < 30:
                        st.success("🟢 RSI je pod 30 – Akcie může být podhodnocená/přeprodaná (možná nákupní příležitost).")
                    else:
                        st.info("ℹ️ RSI je v neutrálním pásmu (30 - 70).")

            # ZÁLOŽKA 4: Velcí investoři a Insiders
            with tab4:
                st.subheader("🐋 Sledování velkých fondů (13F) a vedení firmy (Form 4)")
                col_i1, col_i2 = st.columns(2)
                col_i1.metric("Podíl institucí a fondů", f"{info.get('heldPercentInstitutions', 0) * 100:.2f}%" if info.get('heldPercentInstitutions') else "N/A")
                col_i2.metric("Podíl insiderů (vedení)", f"{info.get('heldPercentInsiders', 0) * 100:.2f}%" if info.get('heldPercentInsiders') else "N/A")
                
                st.markdown("---")
                st.markdown("### 🏛️ Nejhlavnější institucionální držitelé")
                try:
                    major_holders = company.major_holders
                    if major_holders is not None and not major_holders.empty:
                        st.dataframe(major_holders, use_container_width=True)
                    else:
                        st.info("Data o majoritních vlastníkách nejsou k dispozici.")
                except Exception:
                    st.info("Tabulku vlastníků se nepodařilo načíst.")

                st.markdown("### 👔 Nedávné transakce insiderů")
                try:
                    insider_transactions = company.insider_transactions
                    if insider_transactions is not None and not insider_transactions.empty:
                        st.dataframe(insider_transactions, use_container_width=True)
                    else:
                        st.info("Záznamy o transakcích insiderů nejsou dostupné.")
                except Exception:
                    st.info("Tabulku transakcí insiderů se nepodařilo načíst.")

            # ZÁLOŽKA 5: Názory analytiků
            with tab5:
                st.subheader("🎯 Doporučení a cílové ceny podle analytiků z Wall Street")
                a1, a2 = st.columns(2)
                with a1:
                    rec = info.get('recommendationKey', 'N/A').upper()
                    st.write(f"**Konsensus doporučení:** `{rec}`")
                    st.write(f"**Počet analytiků doplňujících odhad:** `{info.get('numberOfAnalystOpinions', 'N/A')}`")
                with a2:
                    st.write(f"**Průměrná cílová cena (Target Mean):** `${info.get('targetMeanPrice', 'N/A')}`")
                    st.write(f"**Nejvyšší odhad (Target High):** `${info.get('targetHighPrice', 'N/A')}`")
                    st.write(f"**Nejnižší odhad (Target Low):** `${info.get('targetLowPrice', 'N/A')}`")

            # ZÁLOŽKA 6: Historie důvodů a komentářů
            with tab6:
                st.subheader(f"📜 Historický kontext a důvody velkých nákupů pro {ticker_symbol}")
                if ticker_symbol == "AAPL":
                    st.markdown("""
                    * **2016 (Warren Buffett / Berkshire Hathaway):** 
                      * *Důvody:* Vnímání Applu jako silného **spotřebního monopolu s loajálními zákazníky**, nikoliv jen běžné tech firmy. Obrovský volný cash flow a zpětný odkup akcií.
                    * **2018–2020 (Vanguard & BlackRock):** 
                      * *Důvody:* Růst segmentu služeb (App Store, iCloud, Apple Music) poskytující vysoké marže a předvídatelné příjmy.
                    * **2023–2024 (Berkshire Hathaway – redukce):** 
                      * *Důvody:* Primárně **daňové optimalizace** v očekávání vyšších korporátních daní v USA, nikoli ztráta důvěry v fundamenty.
                    """)
                else:
                    st.info(f"Historický přehled důvodů je k dispozici pro vybrané hlavní tituly. Zde se stahují nejnovější fundamentální zprávy.")

                st.markdown("---")
                st.subheader("📰 Aktuální zpravodajství a zprávy k akcii")
                try:
                    news_list = company.news
                    if news_list:
                        for item in news_list:
                            title = item.get('title', 'Bez názvu')
                            publisher = item.get('publisher', 'Neznámý zdroj')
                            link = item.get('link', '#')
                            st.markdown(f"* **[{title}]({link})** — *{publisher}*")
                    else:
                        st.info("Žádné aktuální zprávy nebyly nalezeny.")
                except Exception as err:
                    st.info(f"Nepodařilo se načíst zprávy: {err}")

    except Exception as e:
        st.error(f"Došlo k chybě při načítání dat: {e}")
