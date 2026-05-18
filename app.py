import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("Texas Investors")

portfolio_data = [
    {"Owner": "Bart McCollum", "Company": "BLOOM ENERGY CORPORATION", "Ticker": "BE"},
    {"Owner": "Derek Long", "Company": "IREN LIMITED", "Ticker": "IREN"},
    {"Owner": "William Sleeper", "Company": "ONDAS HOLDINGS INC.", "Ticker": "ONDS"},
    {"Owner": "Richard Scherer", "Company": "NUSCALE POWER CORPORATION", "Ticker": "SMR"},
    {"Owner": "Marc Bateman", "Company": "AGNICO EAGLE MINES LIMITED", "Ticker": "AEM"},
    {"Owner": "Jay Settle", "Company": "TEXAS INSTRUMENTS INC.", "Ticker": "TXN"},
    {"Owner": "Richard Irwin", "Company": "GAMESQUARE HOLDINGS, INC.", "Ticker": "GAME"},
    {"Owner": "Robert Elder", "Company": "NANO-X IMAGING LTD", "Ticker": "NNOX"},
    {"Owner": "Bill Searight", "Company": "ALPHABET INC.", "Ticker": "GOOG"},
    {"Owner": "Collin Comer", "Company": "JD.COM, INC.", "Ticker": "JD"},
    {"Owner": "George Gibson", "Company": "AMAZON.COM, INC.", "Ticker": "AMZN"},
    {"Owner": "Don Gaskins", "Company": "ARISTA NETWORKS, INC.", "Ticker": "ANET"},
    {"Owner": "Tom McCarthy", "Company": "SENTINELONE", "Ticker": "S"},
    {"Owner": "John Peavy", "Company": "ALTO INGREDIENTS, INC.", "Ticker": "ALTO"},
    {"Owner": "Craig Penfold", "Company": "NVIDIA CORPORATION", "Ticker": "NVDA"},
    {"Owner": "Phillip Bankhead", "Company": "PALANTIR TECHNOLOGIES INC.", "Ticker": "PLTR"},
    {"Owner": "Jimmy Perryman", "Company": "MICROSOFT CORPORATION", "Ticker": "MSFT"},
    {"Owner": "Griffin Collie", "Company": "TESLA, INC.", "Ticker": "TSLA"},
    {"Owner": "Bill Perryman", "Company": "NETFLIX, INC.", "Ticker": "NFLX"},
    {"Owner": "Greg Pape", "Company": "ORACLE CORPORATION", "Ticker": "ORCL"},
    {"Owner": "Rod Hays", "Company": "THE TRADE DESK, INC.", "Ticker": "TTD"},
    {"Owner": "Kent Comer", "Company": "SHOPIFY INC.", "Ticker": "SHOP"},
    {"Owner": "Dan Shimer", "Company": "JFROG LTD", "Ticker": "FROG"},
    {"Owner": "Matt Gaskins", "Company": "CONSTELLATION ENERGY CORP.", "Ticker": "CEG"},
    {"Owner": "Chris Jaquez", "Company": "ATLASSIAN CORPORATION", "Ticker": "TEAM"},
]

tickers = [item["Ticker"] for item in portfolio_data]

def get_ytd(history):
    current_year = pd.Timestamp.now().year
    prev_year = current_year - 1
    prev_year_data = history[history.index.year == prev_year]
    if not prev_year_data.empty:
        start_price = prev_year_data['Close'].iloc[-1]
    else:
        ytd_data = history[history.index.year == current_year]
        if ytd_data.empty: return 0.0
        start_price = ytd_data['Close'].iloc[0]
    end_price = history['Close'].iloc[-1]
    return ((end_price - start_price) / start_price) * 100

if st.button('Refresh Data'):
    data = []
    stock_data = yf.download(tickers, period="2y", group_by='ticker', progress=False)

    for item in portfolio_data:
        t = item["Ticker"]
        try:
            df = stock_data if len(tickers) == 1 else stock_data[t]
            if df.empty: continue
            metrics = {
                "Rank": 0,
                "Owner": item["Owner"],
                "Company": item["Company"],
                "Ticker": t,
                "Price": df['Close'].iloc[-1],
                "YTD": get_ytd(df)
            }
            data.append(metrics)
        except Exception:
            pass

    df_display = pd.DataFrame(data)
    df_display = df_display.sort_values(by="YTD", ascending=False)
    df_display['Rank'] = range(1, len(df_display) + 1)
    df_display = df_display[['Rank', 'Owner', 'Company', 'Ticker', 'Price', 'YTD']]

    # --- AVERAGE RETURN METRICS ---
    avg_return = df_display["YTD"].mean()
    best = df_display.iloc[0]
    worst = df_display.iloc[-1]
    pct_positive = (df_display["YTD"] > 0).sum() / len(df_display) * 100
    positive_count = (df_display["YTD"] > 0).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Group Average Return", f"{avg_return:.2f}%")
    col2.metric("🥇 Leader", f"{best['Owner']} ({best['Ticker']})", f"{best['YTD']:.2f}%")
    col3.metric("📉 Trailing", f"{worst['Owner']} ({worst['Ticker']})", f"{worst['YTD']:.2f}%")
    col4.metric("✅ In Positive Territory", f"{pct_positive:.0f}%", f"{positive_count} of {len(df_display)} picks")

    st.divider()
    # --- END METRICS ---

    # Formatting
    df_display["Price"] = df_display["Price"].apply(lambda x: f"${x:.2f}")
    df_display["YTD"] = df_display["YTD"].apply(lambda x: f"{x:.2f}%")

    def highlight_msft(row):
        return ['font-weight: bold' if row['Ticker'] == 'MSFT' else '' for _ in row]

    styled_df = df_display.style.apply(highlight_msft, axis=1)\
                                .set_properties(subset=['Rank', 'Ticker', 'YTD'], **{'text-align': 'center'})

    st.dataframe(styled_df, hide_index=True, use_container_width=True)

else:
    st.write("Click 'Refresh Data' to load the latest market stats.")
