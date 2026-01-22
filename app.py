import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("Texas Investors Tracker")

tickers = ["BE","IREN","ONDS","SMR","AEM","TXN","GAME","NNOX","GOOG","JD","AMZN","ANET","SNTL","ALTO","NVDA","PLTR","MSFT","TSLA","NFLX","ORCL","TTD","SHOP","FROG","CEG","TEAM"]

# 1. Helpers return RAW FLOATS
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
    stock_data = yf.download(tickers, period="10y", group_by='ticker', progress=False)

    for t in tickers:
        df = stock_data if len(tickers) == 1 else stock_data[t]
        
        metrics = {
            "Ticker": t,
            "Price": df['Close'].iloc[-1],
            "YTD": get_ytd(df),
            "6-Month": get_total_return(df, 126),
            "1-Year": get_total_return(df, 252),
            "3-Year (Ann)": get_cagr(df, 756),
            "5-Year (Ann)": get_cagr(df, 1260)
        }
        data.append(metrics)

    df_display = pd.DataFrame(data)

    # Sort and Add Rank
    df_display = df_display.sort_values(by="YTD", ascending=False)
    df_display['Rank'] = range(1, len(df_display) + 1)

    # Reorder columns
    column_order = ['Rank', 'Ticker', 'Price', 'YTD', '6-Month', '1-Year', '3-Year (Ann)', '5-Year (Ann)']
    df_display = df_display[column_order]

    # Format numbers
    df_display["Price"] = df_display["Price"].apply(lambda x: f"${x:.2f}")
    cols_to_format = ['YTD', '6-Month', '1-Year', '3-Year (Ann)', '5-Year (Ann)']
    for col in cols_to_format:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%")

    # --- NEW: STYLE THE DATAFRAME ---
    # We use Pandas Styler to center the 'Rank' column
    styled_df = df_display.style.set_properties(subset=['Rank'], **{'text-align': 'center'})

    # Show the styled table
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

else:
    st.write("Click 'Refresh Data' to load the latest market stats.")
