#Trading Engine for Interactive Brokers
This Python script connects to the Interactive Brokers Trader Workstation (TWS) API to facilitate automated trading. It includes functionality for establishing a connection, retrieving market data, and executing a Butterfly Option Strategy on the SPX index.

#Features
Connection to TWS API: Establish a secure connection with Interactive Brokers to execute trades.
Market Data Retrieval: Access real-time and historical market data.
Trading Symbol Master: Retrieve master data for trading symbols.
Butterfly Option Strategy: Implement a basket-style Butterfly Option Strategy on SPX options with 0 days to expiry.
Order Execution: Automatically execute trades based on predefined signals

#Installation
git clone https://github.com/Coderixc/InteractiveBrokerPython.git
cd trading-engine

#Install dependencies:
Make sure you have Python installed on your machine. Then, install the necessary packages:
pip install ib_insync

#Setup Interactive Brokers:
Ensure that Interactive Brokers TWS or IB Gateway is running and API access is enabled.

#Usage
Trading Engine Class
The main class, TradingEngine, is responsible for connecting to the broker, retrieving data, and executing trades.
