import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("My Stock Performance Tracker")

tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "XLK", "RSP"]

# 1. Helper for Total Return (Absolute % change)
# Used for periods <= 1 Year
def get_total_return(history, days):
    if len(history) < days: return 0.0
    start = history['Close'].iloc[-days]
    end = history['Close'].iloc[-1]
    return ((end - start) / start) * 100

# 2. Helper for Annualized Return (CAGR)
# Used for periods > 1 Year
def get_cagr(history, days):
    if len(history) < days: return 0.0
    start = history['Close'].iloc[-days]
    end = history['Close'].iloc[-1]
    years = days / 252  # Approximate trading days in a year
    # CAGR Formula: (End/Start)^(1/n) - 1
    return ((end / start) ** (1 / years) - 1) * 100

def get_ytd(history):
    current_year = pd.Timestamp.now().year
    ytd_data = history[history.index.year == current_year]
    if ytd_data.empty: return 0.0
    return ((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0]) * 100

if st.button('Refresh Data'):
    data = []
    # Download 5 years of data
    stock_data = yf.download(tickers, period="5y", group_by='ticker', progress=False)

    for t in tickers:
        df = stock_data if len(tickers) == 1 else stock_data[t]
        
        metrics = {
            "Ticker": t,
            "Price": f"${df['Close'].iloc[-1]:.2f}",
            "YTD": f"{get_ytd(df):.2f}%",
            "6-Month": f"{get_total_return(df, 126):.2f}%",
            "1-Year": f"{get_total_return(df, 252):.2f}%",
            # Switch to Annualized (CAGR) for multi-year
            "3-Year (Ann)": f"{get_cagr(df, 756):.2f}%",
            "5-Year (Ann)": f"{get_cagr(df, 1260):.2f}%"
        }
        data.append(metrics)

    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

else:
    st.write("Click 'Refresh Data' to load the latest market stats.")
