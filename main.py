import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import datetime

# Fetch data from Yahoo Finance
ticker = "SOKM.IS"
start_date = "2022-3-01"
end_date = "2024-03-08"
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate multiple KAMA
data.ta.kama(close='Close', length=10, fast=1, slow=30, append=True)
data.ta.kama(close='Close', length=10, fast=2, slow=30, append=True)
data.ta.kama(close='Close', length=10, fast=5, slow=30, append=True)

# Convert index to matplotlib date format
data.reset_index(inplace=True)
data['Date'] = data['Date'].apply(mdates.date2num)

# Function to calculate buy and sell signals and capture the dates of those signals
def calculate_signals(data, kama_key, safety_threshold=0.88):
    last_signal = 'none'  # Possible values: 'buy', 'sell', 'none'
    last_buy_price = None
    buy_signal = []
    sell_signal = []
    buy_sell_pairs = []
    signal_dates = []

    for i in range(2, len(data)):
        current_price = data['Close'].iloc[i]
        current_date = data['Date'].iloc[i]
        if last_signal != 'buy' and data[kama_key].iloc[i] > data[kama_key].iloc[i - 1] and data[kama_key].iloc[i - 1] <= data[kama_key].iloc[i - 2]:
            buy_signal.append(True)
            sell_signal.append(False)
            last_signal = 'buy'
            last_buy_price = current_price
        elif last_signal == 'buy' and ((data[kama_key].iloc[i] < data[kama_key].iloc[i - 1] and data[kama_key].iloc[i - 1] >= data[kama_key].iloc[i - 2] and current_price > last_buy_price) or current_price < last_buy_price * safety_threshold):
            buy_signal.append(False)
            sell_signal.append(True)
            buy_sell_pairs.append((last_buy_price, current_price))
            signal_dates.append(current_date)
            last_signal = 'sell'
            last_buy_price = None
        else:
            buy_signal.append(False)
            sell_signal.append(False)

    buy_signal = [False, False] + buy_signal
    sell_signal = [False, False] + sell_signal

    return buy_signal, sell_signal, buy_sell_pairs, signal_dates

# Calculate signals, profits, and signal dates for each KAMA configuration
results = {}
for fast in [1, 2, 5]:
    kama_key = f'KAMA_10_{fast}_30'
    data[f'Buy_Signal_{fast}'], data[f'Sell_Signal_{fast}'], pairs, signal_dates = calculate_signals(data, kama_key)
    results[f'profits_{fast}'] = [(sell - buy) / buy * 100 for buy, sell in pairs]
    results[f'dates_{fast}'] = signal_dates

# Define figure and axes
fig, (ax_candle, ax_profit) = plt.subplots(2, 1, figsize=(18, 10), gridspec_kw={'height_ratios': [2, 1]})

# Plot candlesticks with KAMA and buy/sell signals
ax_candle.set_title(f'Candlestick Chart with KAMA Buy/Sell Signals for {ticker}')
candlestick_ohlc(ax_candle, data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.6, colorup='g', colordown='r', alpha=0.8)

colors = ['blue', 'orange', 'purple']
signal_colors = {
    1: {'buy': 'green', 'sell': 'red'},
    2: {'buy': 'lime', 'sell': 'maroon'},
    5: {'buy': 'black', 'sell': 'darkred'}
}

for i, fast in enumerate([1, 2, 5]):
    kama_key = f'KAMA_10_{fast}_30'
    ax_candle.plot(data['Date'], data[kama_key], label=f'KAMA (10, {fast}, 30)', color=colors[i])
    ax_candle.plot(data.loc[data[f'Buy_Signal_{fast}'], 'Date'], data.loc[data[f'Buy_Signal_{fast}'], kama_key], '^', color=signal_colors[fast]['buy'], markersize=10, label=f'Buy Signal {fast}')
    ax_candle.plot(data.loc[data[f'Sell_Signal_{fast}'], 'Date'], data.loc[data[f'Sell_Signal_{fast}'], kama_key], 'v', color=signal_colors[fast]['sell'], markersize=10, label=f'Sell Signal {fast}')

ax_candle.xaxis_date()
ax_candle.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax_candle.set_xlabel('Date')
ax_candle.set_ylabel('Price')
ax_candle.legend()
ax_candle.grid(True)

# Plot cumulative profit for all KAMA configurations, using dates for the x-axis
ax_profit.set_title('Cumulative Profit for KAMA Configurations')
for i, fast in enumerate([1, 2, 5]):
    profits = results[f'profits_{fast}']
    dates = results[f'dates_{fast}']
    cumulative_profits = [sum(profits[:i + 1]) for i in range(len(profits))]
    ax_profit.plot(mdates.num2date(dates), cumulative_profits, label=f'KAMA (10, {fast}, 30)', marker='o', linestyle='-', color=colors[i])

ax_profit.xaxis_date()
ax_profit.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax_profit.set_xlabel('Date')
ax_profit.set_ylabel('Cumulative Profit (%)')
ax_profit.legend()
ax_profit.grid(True)

plt.tight_layout()
plt.show()
