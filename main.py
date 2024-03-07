import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import datetime

# Fetch data from Yahoo Finance
ticker = "TUPRS.IS"  # Example ticker symbol (you can change it)
start_date = "2020-01-01"
end_date = "2024-03-06"
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate KAMA
#data.ta.kama(close='Close', drift=1, append=True)
data.ta.kama(close='Close', length=10, fast=1, slow=30, drift=1, append=True)

# Convert index to matplotlib date format
data.reset_index(inplace=True)
data['Date'] = data['Date'].apply(mdates.date2num)

# Plotting candlesticks
fig, ax = plt.subplots(figsize=(12, 6))
candlestick_ohlc(ax, data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.6, colorup='g', colordown='r', alpha=0.8)

# Plotting KAMA
plt.plot(data['Date'], data['KAMA_10_1_30'], label='KAMA (10, 2, 30)', color='blue')

# Detecting Buy and Sell signals
buy_signal = (data['KAMA_10_1_30'] > data['KAMA_10_1_30'].shift(1)) & (
        data['KAMA_10_1_30'].shift(1) <= data['KAMA_10_1_30'].shift(2))
sell_signal = (data['KAMA_10_1_30'] < data['KAMA_10_1_30'].shift(1)) & (
        data['KAMA_10_1_30'].shift(1) >= data['KAMA_10_1_30'].shift(2))

# Plotting Buy and Sell arrows
plt.plot(data.loc[buy_signal, 'Date'], data.loc[buy_signal, 'KAMA_10_1_30'], '^', color='g', markersize=10,
         label='Buy Signal')
plt.plot(data.loc[sell_signal, 'Date'], data.loc[sell_signal, 'KAMA_10_1_30'], 'v', color='r', markersize=10,
         label='Sell Signal')

# Formatting
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d-%h'))
plt.xticks(rotation=45)
plt.title('Candlestick Chart with KAMA Buy/Sell Signals for {}'.format(ticker))
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)

# Reporting the last buy and sell signals
last_buy_date = data.loc[buy_signal, 'Date'].iloc[-1] if len(data.loc[buy_signal, 'Date']) > 0 else None
last_sell_date = data.loc[sell_signal, 'Date'].iloc[-1] if len(data.loc[sell_signal, 'Date']) > 0 else None

if last_buy_date:
    last_buy_date = mdates.num2date(last_buy_date)
    last_buy_date = datetime.datetime.strftime(last_buy_date, '%Y-%m-%d %H:%M:%S')
else:
    last_buy_date = "No recent buy signal"

if last_sell_date:
    last_sell_date = mdates.num2date(last_sell_date)
    last_sell_date = datetime.datetime.strftime(last_sell_date, '%Y-%m-%d %H:%M:%S')
else:
    last_sell_date = "No recent sell signal"

print("Last Buy Signal:", last_buy_date)
print("Last Sell Signal:", last_sell_date)

# Extract last 10 buy and sell dates
last_10_buy_dates = data.loc[buy_signal, 'Date'].iloc[-10:].apply(mdates.num2date)
last_10_sell_dates = data.loc[sell_signal, 'Date'].iloc[-10:].apply(mdates.num2date)

# Report the date of the first buy and sell signals within the last 10 buy-sell pairs
first_buy_within_last_10 = last_10_buy_dates.min() if not last_10_buy_dates.empty else "No buy signal within last 10 buy-sell pairs"
first_sell_within_last_10 = last_10_sell_dates.min() if not last_10_sell_dates.empty else "No sell signal within last 10 buy-sell pairs"

print("First Buy Signal within Last 10 Buy-Sell Pairs:", first_buy_within_last_10)
print("First Sell Signal within Last 10 Buy-Sell Pairs:", first_sell_within_last_10)

print("\n")
print("-------------------------------------------------------------------------------------------------")
print("\n")

# Iterate through buy and sell signals
for buy_date, sell_date in zip(last_10_buy_dates, last_10_sell_dates):
    # Extracting high and low prices for the buy and sell dates
    buy_price = data.loc[data['Date'] == mdates.date2num(buy_date), 'High'].values[0]
    sell_price = data.loc[data['Date'] == mdates.date2num(sell_date), 'Low'].values[0]

    # Calculate profit or loss percentage
    profit_loss_percentage = ((sell_price - buy_price) / buy_price) * 100

    # Report buy-sell pair details
    print("Buy Date:", buy_date.strftime('%Y-%m-%d'), "Sell Date:", sell_date.strftime('%Y-%m-%d'))
    print("Buy Price (Highest of the Day):", buy_price, "Sell Price (Lowest of the Day):", sell_price)
    print("Profit/Loss Percentage: {:.2f}%".format(profit_loss_percentage))
    print()  # Empty line for readability


plt.show()
