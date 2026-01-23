import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("Texas Investors")

# 1. Define the full dataset
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
    {"Owner": "Tom McCarthy", "Company": "SENTINEL HOLDINGS LTD.", "Ticker": "SNTL"},
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
    ytd_data = history[history.index.year == current_year]
    if ytd_data.empty: return 0.0
    return ((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0]) * 100

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

    # Sort, Rank, and Reorder
    df_display = df_display.sort_values(by="YTD", ascending=False)
    df_display['Rank'] = range(1, len(df_display) + 1)
    df_display = df_display[['Rank', 'Owner', 'Company', 'Ticker', 'Price', 'YTD']]

    # Formatting
    df_display["Price"] = df_display["Price"].apply(lambda x: f"${x:.2f}")
    df_display["YTD"] = df_display["YTD"].apply(lambda x: f"{x:.2f}%")

    # --- STYLING LOGIC START ---
    
    # 1. Define highlight function
    def highlight_msft(row):
        # Apply 'font-weight: bold' if the ticker is MSFT, otherwise nothing
        return ['font-weight: bold' if row['Ticker'] == 'MSFT' else '' for _ in row]

    # 2. Apply the highlight function AND the centering at the same time
    styled_df = df_display.style.apply(highlight_msft, axis=1)\
                                .set_properties(subset=['Rank', 'Ticker', 'YTD'], **{'text-align': 'center'})

    st.dataframe(styled_df, hide_index=True, use_container_width=True)
    # --- STYLING LOGIC END ---

else:
    st.write("Click 'Refresh Data' to load the latest market stats.")
