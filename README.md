# Trading Engine for Interactive Brokers
This Python script connects to the Interactive Brokers Trader Workstation (TWS) API to facilitate automated trading. It includes functionality for establishing a connection, retrieving market data, and executing a Butterfly Option Strategy on the SPX index.

# Features
📌Connection to TWS API: Establish a secure connection with Interactive Brokers to execute trades.

📌Market Data Retrieval: Access real-time and historical market data.

📌Trading Symbol Master: Retrieve master data for trading symbols.

📌Butterfly Option Strategy: Implement a basket-style Butterfly Option Strategy on SPX options with 0 days to expiry.

📌Order Execution: Automatically execute trades based on predefined signals

# Installation
git clone https://github.com/Coderixc/InteractiveBrokerPython.git

cd trading-engine

# Install dependencies:
Make sure you have Python installed on your machine. Then, install the necessary packages:
pip install ib_insync

# Setup Interactive Brokers:
Ensure that Interactive Brokers TWS or IB Gateway is running and API access is enabled.

# Usage
Trading Engine Class
The main class, TradingEngine, is responsible for connecting to the broker, retrieving data, and executing trades.

# Key Methods
📍ConnectionEstablishment() : This method connects the engine to the TWS API, enabling communication with Interactive Brokers.

📍getMaster() : Retrieves the trading symbol master list to identify available trading symbols.

📍GetMarketData() : Fetches live market data for selected trading symbols or make simulation to get price.

📍GetHistoricalData_Index() : Acquires historical data for stocks to support backtesting and analysis.

📍StartTrading(): Starts the trading process, executing orders based on generated signals.

📍ButterFlyOptionStrategyBasketStyle() : This method implements the butterfly strategy by dynamically selecting the ATM, ITM, and OTM strikes based on the latest market prices.

## Butterfly Option Strategy
This project includes a butterfly option strategy for SPX with DTE "0" expiry. The strategy involves creating a balanced spread using at-the-money (ATM), in-the-money (ITM), and out-of-the-money (OTM) options.

This README provides a structured overview of your project, making it easier for others to understand and contribute to your work
