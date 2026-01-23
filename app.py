import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("Texas Investors")

# 1. Define the full dataset with Owners and Company Names
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

# Extract just the symbols list for the API download
tickers = [item["Ticker"] for item in portfolio_data]

# 2. Performance Calculation Helpers
def get_total_return(history, days):
    if len(history) < days: return 0.0
    start = history['Close'].iloc[-days]
    end = history['Close'].iloc[-1]
    return ((end - start) / start) * 100

def get_cagr(history, days):
    if len(history) < days: return 0.0
    start = history['Close'].iloc[-days]
    end = history['Close'].iloc[-1]
    years = days / 252
    return ((end / start) ** (1 / years) - 1) * 100

def get_ytd(history):
    current_year = pd.Timestamp.now().year
    ytd_data = history[history.index.year == current_year]
    if ytd_data.empty: return 0.0
    return ((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0]) * 100

if st.button('Refresh Data'):
    data = []
    # Download 10 years of data
    stock_data = yf.download(tickers, period="10y", group_by='ticker', progress=False)

    # Loop through our portfolio dictionary so we can keep track of names
    for item in portfolio_data:
        t = item["Ticker"]
        
        # Handle case where download might fail or return empty for a specific ticker
        try:
            df = stock_data if len(tickers) == 1 else stock_data[t]
            
            # If the dataframe is empty (e.g. invalid ticker), skip or fill zeros
            if df.empty:
                continue

            metrics = {
                "Rank": 0, # Placeholder, we fill this after sorting
                "Owner": item["Owner"],     # NEW COLUMN
                "Company": item["Company"], # NEW COLUMN
                "Ticker": t,
                "Price": df['Close'].iloc[-1],
                "YTD": get_ytd(df),
                "6-Month": get_total_return(df, 126),
                "1-Year": get_total_return(df, 252),
                "3-Year (Ann)": get_cagr(df, 756),
                "5-Year (Ann)": get_cagr(df, 1260)
            }
            data.append(metrics)
        except Exception as e:
            # If a ticker fails, we just skip it so the app doesn't crash
            pass

    df_display = pd.DataFrame(data)

    # 1. SORT by YTD first (Highest return at top)
    df_display = df_display.sort_values(by="YTD", ascending=False)

    # 2. ADD RANK (1 to N)
    df_display['Rank'] = range(1, len(df_display) + 1)

    # 3. REORDER columns
    # We put Rank, Owner, and Company at the start
    column_order = ['Rank', 'Owner', 'Company', 'Ticker', 'Price', 'YTD', '6-Month', '1-Year', '3-Year (Ann)', '5-Year (Ann)']
    df_display = df_display[column_order]

    # 4. Format numbers
    df_display["Price"] = df_display["Price"].apply(lambda x: f"${x:.2f}")
    
    cols_to_format = ['YTD', '6-Month', '1-Year', '3-Year (Ann)', '5-Year (Ann)']
    for col in cols_to_format:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%")

    # 5. STYLE the table
    # Center the Rank and Ticker, Left Align the Names
    styled_df = df_display.style.set_properties(subset=['Rank', 'Ticker', 'YTD'], **{'text-align': 'center'})
    
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

else:
    st.write("Click 'Refresh Data' to load the latest market stats.")
