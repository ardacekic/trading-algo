import os
from binance.client import Client
import matplotlib.pyplot as plt

# Binance API credentials
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

# Initialize Binance client
client = Client(api_key, api_secret)

def fetch_historical_data(symbol, interval, limit):
    klines = client.get_historical_klines(symbol, interval, limit=limit)
    return klines

def plot_graph(data):
    timestamps = [entry[0] for entry in data]
    prices = [float(entry[4]) for entry in data]

    plt.plot(timestamps, prices)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Historical Price Data')
    plt.show()

if __name__ == "__main__":
    # Symbol: e.g., 'BTCUSDT', 'ETHUSDT'
    symbol = 'BTCUSDT'
    # Interval: e.g., '1h', '4h', '1d'
    interval = '1d'
    # Limit: Number of data points to fetch
    limit = 100

    # Fetch historical data
    historical_data = fetch_historical_data(symbol, interval, limit)

    # Plot graph
    plot_graph(historical_data)
