import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Title and Setup
st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("My Stock Performance Tracker")

# 2. Define the stocks you want to track
# I've added a few major ones + ETFs to start
tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "XLK", "RSP"]

# 3. Helper function to calculate percentage change
def get_change(history, days):
    if len(history) < days: return 0.0
    start = history['Close'].iloc[-days]
    end = history['Close'].iloc[-1]
    return ((end - start) / start) * 100

def get_ytd(history):
    current_year = pd.Timestamp.now().year
    ytd_data = history[history.index.year == current_year]
    if ytd_data.empty: return 0.0
    return ((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0]) * 100

# 4. Fetch Data and Build Table
if st.button('Refresh Data'):
    data = []
    # Download 5 years of data for all tickers at once
    stock_data = yf.download(tickers, period="5y", group_by='ticker', progress=False)

    for t in tickers:
        # Extract the specific dataframe for this ticker
        df = stock_data if len(tickers) == 1 else stock_data[t]
        
        # Calculate metrics
        metrics = {
            "Ticker": t,
            "Price": f"${df['Close'].iloc[-1]:.2f}",
            "YTD": f"{get_ytd(df):.2f}%",
            "6-Month": f"{get_change(df, 126):.2f}%",
            "1-Year": f"{get_change(df, 252):.2f}%",
            "3-Year": f"{get_change(df, 756):.2f}%",
            "5-Year": f"{get_change(df, 1260):.2f}%"
        }
        data.append(metrics)

    # Display as a clean interactive dataframe
    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

else:
    st.write("Click 'Refresh Data' to load the latest market stats.")
