import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

# Fetch historical stock data
symbol = 'XU100.IS'
data = yf.download(symbol, start='2023-01-01', end='2024-03-08', interval='1d')

# Ensure the index is a DatetimeIndex and reset it for ohlc
data.reset_index(inplace=True)
data['Date'] = data['Date'].apply(mdates.date2num)

# Calculate VWMA
length = 10
fast = 2
slow = 30

data['hlc3'] = (data['High'] + data['Low'] + data['Close']) / 3
data['vwap'] = (data['hlc3'] * data['Volume']).rolling(window=length).sum() / data['Volume'].rolling(window=length).sum()

# Initialize columns for VW-KAMA
data['price_change'] = np.abs(data['vwap'] - data['vwap'].shift(length))
data['volatility'] = data['vwap'].diff().abs().rolling(window=length).sum()
data['ER'] = data['price_change'] / data['volatility'].replace(0, np.nan)
data['SC'] = ((data['ER'] * (2 / (fast + 1) - 2 / (slow + 1))) + 2 / (slow + 1)) ** 2
data['VW_KAMA'] = np.nan

for i in range(length, len(data)):
    if i == length or np.isnan(data.loc[i, 'VW_KAMA']):
        data.loc[i, 'VW_KAMA'] = data.loc[i, 'vwap']
    else:
        data.loc[i, 'VW_KAMA'] = data.loc[i - 1, 'VW_KAMA'] + data.loc[i, 'SC'] * (data.loc[i, 'vwap'] - data.loc[i - 1, 'VW_KAMA'])

# Calculate MACD
data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
data['Hist'] = data['MACD'] - data['Signal']

# Plotting with shared x-axis
fig, (ax1, ax2) = plt.subplots(2, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

# Plot Candlestick (Price)
candlestick_ohlc(ax1, data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.6, colorup='green', colordown='red', alpha=0.8)
ax1.xaxis_date()

# Plot VW-KAMA with dynamic color based on direction
for i in range(1, len(data)):
    if data['VW_KAMA'].iloc[i] > data['VW_KAMA'].iloc[i - 1]:
        ax1.plot(data['Date'].iloc[i - 1:i + 1], data['VW_KAMA'].iloc[i - 1:i + 1], color='green')
    elif data['VW_KAMA'].iloc[i] < data['VW_KAMA'].iloc[i - 1]:
        ax1.plot(data['Date'].iloc[i - 1:i + 1], data['VW_KAMA'].iloc[i - 1:i + 1], color='red')
    else:
        ax1.plot(data['Date'].iloc[i - 1:i + 1], data['VW_KAMA'].iloc[i - 1:i + 1], color='blue')

ax1.grid(True)

# Plot MACD
ax2.plot(data['Date'], data['MACD'], label='MACD', color='blue')
ax2.plot(data['Date'], data['Signal'], label='Signal', color='orange')

# Plot Histogram
colors = ['green' if val >= 0 else 'red' for val in data['Hist']]
ax2.bar(data['Date'], data['Hist'], color=colors, width=0.6)

ax2.xaxis_date()
ax2.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax2.grid(True)

# Rotate date labels for both plots
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Labels and Title for MACD
ax2.set_xlabel("Date")
ax2.set_ylabel("MACD")
ax1.set_title(f"{symbol} Stock Price and VW-KAMA Indicator with MACD")

plt.show()
