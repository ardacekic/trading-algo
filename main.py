import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import datetime

# Fetch data from Yahoo Finance
ticker = "REEDR.IS"  # Example ticker symbol (you can change it)
start_date = "2020-01-01"
end_date = "2024-03-06"
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate KAMA
# data.ta.kama(close='Close', drift=1, append=True)
data.ta.kama(close='Close', length=10, fast=1, slow=30, drift=1, append=True)

# Convert index to matplotlib date format
data.reset_index(inplace=True)
data['Date'] = data['Date'].apply(mdates.date2num)

# Detecting Buy and Sell signals
buy_signal = (data['KAMA_10_1_30'] > data['KAMA_10_1_30'].shift(1)) & (
        data['KAMA_10_1_30'].shift(1) <= data['KAMA_10_1_30'].shift(2))
sell_signal = (data['KAMA_10_1_30'] < data['KAMA_10_1_30'].shift(1)) & (
        data['KAMA_10_1_30'].shift(1) >= data['KAMA_10_1_30'].shift(2))

# Initialize variables for profit calculation
last_10_profit = []
last_10_buy_dates = []
last_10_sell_dates = []

# Extract last 10 buy and sell dates
last_10_buy_dates = data.loc[buy_signal, 'Date'].iloc[-10:].apply(mdates.num2date)
last_10_sell_dates = data.loc[sell_signal, 'Date'].iloc[-10:].apply(mdates.num2date)

# Iterate through last 10 buy and sell signals
for buy_date, sell_date in zip(last_10_buy_dates, last_10_sell_dates):
    # Extracting high and low prices for the buy and sell dates
    buy_price = data.loc[data['Date'] == mdates.date2num(buy_date), 'High'].values[0]
    sell_price = data.loc[data['Date'] == mdates.date2num(sell_date), 'Low'].values[0]

    # Calculate profit or loss percentage
    profit_loss_percentage = ((sell_price - buy_price) / buy_price) * 100

    # Store profit and buy/sell dates for last 10 pairs
    last_10_profit.append(profit_loss_percentage)

# Calculate cumulative profit
cumulative_profit = [sum(last_10_profit[:i+1]) for i in range(len(last_10_profit))]

# Plotting
fig, axs = plt.subplots(1, 2, figsize=(16, 6))

# Plotting candlesticks with KAMA and buy/sell signals
axs[0].set_title('Candlestick Chart with KAMA Buy/Sell Signals for {}'.format(ticker))
candlestick_ohlc(axs[0], data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.6, colorup='g', colordown='r', alpha=0.8)
axs[0].plot(data['Date'], data['KAMA_10_1_30'], label='KAMA (10, 2, 30)', color='blue')
axs[0].plot(data.loc[buy_signal, 'Date'], data.loc[buy_signal, 'KAMA_10_1_30'], '^', color='g', markersize=10, label='Buy Signal')
axs[0].plot(data.loc[sell_signal, 'Date'], data.loc[sell_signal, 'KAMA_10_1_30'], 'v', color='r', markersize=10, label='Sell Signal')
axs[0].xaxis_date()
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d-%h'))
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Price')
axs[0].legend()
axs[0].grid(True)
axs[0].tick_params(rotation=45)

# Plotting cumulative profit for last 10 buy-sell pairs
axs[1].set_title('Cumulative Profit/Loss for Last 10 Buy-Sell Pairs for {}'.format(ticker))
axs[1].plot_date(last_10_sell_dates, cumulative_profit, linestyle='-', marker='o', color='g', label='Cumulative Profit/Loss (%)')
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Cumulative Profit/Loss (%)')
axs[1].legend()
axs[1].grid(True)
axs[1].tick_params(rotation=45)

plt.tight_layout()
plt.show()
