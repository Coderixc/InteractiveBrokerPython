from ib_insync import *
import datetime
import time
import threading


class AtmEngine:

    def __init__(self):
        print(F"Acess TIme : {datetime.datetime.today()}")
        self._interval = 5
        print(F"Setting interval to : {5}")
        self._underlyingprice = 0.0
        self.ATM = 0.0

    def getAtm(self, spotPrice):
        if spotPrice == 0.0:
            return -1
        atm_strike = -1
        rem = float(spotPrice) % self._interval
        adjusted = spotPrice - rem

        if rem > (self._interval / 2):
            atm_strike = adjusted + self._interval
        else:
            atm_strike = adjusted

        # validation
        if abs(spotPrice - atm_strike) <= self._interval:
            self.ATM = atm_strike  # store

        return atm_strike

    def getNextUpwardStrike(self, width: int):
        if width == 0.0:
            return self.ATM
        if width <= 0:
            return -1
            print("please pass correct +ve Width Value")

        atm_strike = -1
        if self.ATM <= 0:
            return -1  # error in Calculating next Upward Strike Price
        next_strike = self.ATM + self._interval * int(width)

        return next_strike

    def getNextDownStrike(self, width: int):
        if width == 0.0:
            return self.ATM
        if width <= 0:
            return -1
            print("please pass correct +ve Width Value")

        atm_strike = -1
        if self.ATM <= 0:
            return -1  # error in Calculating next Upward Strike Price
        next_strike = self.ATM - self._interval * int(width)

        return next_strike


class TradingEngine:

    def __init__(self):
        print("Connecting to TWS API framework...")
        self.INIT()

    def INIT(self):
        try:

            print("     ******  INIT PROCES  *****   ")

            self.ConnectionEsablishment()
            self.getMaster()
            self.prepareContract()
            self.GetMarketData()
            self.GetHistoricalData_Index()
            self.MarketData()

            print(" *****************  Request LTP ******************")
            contract = Index('SPX', 'CBOE')
            ltp_index = self.GetLTP(contract)
            print(F"LTP is  {contract.symbol} : ${ltp_index}")

            stock_contract = Stock('AAPL', 'NASDAQ')
            ltp_stk = self.GetLTP(stock_contract)
            print(F"LTP is  {stock_contract.symbol} : ${ltp_stk}")

            self.ListExpiryDate = []  # string
            self.ListStrikePrice = []  # float
            self.List_Open_trades = []
            # List for Only Executed Trades..
            self.List_Executed_trades = []

            # self.DefineALlEvent()

            print("  -------------------------  Variables ----------------")
            self._atmEngine = AtmEngine()

        except Exception as e:
            print(F"Failed to initialize Variables : {e}")

    def ConnectionEsablishment(self):
        print("Establishing Connection gateway..")
        port_no = 7497
        self.ib = IB()
        self.ib.connect('127.0.0.1', port_no, 123)

    def prepareContract(self):
        self.contract_index = Index(symbol='SPX', exchange='CBOE')

    def MarketData(self):
        print("Market Data Auto Function")
        [ticker] = self.ib.reqTickers(self.contract_index)
        print(F"Print Ticker is {ticker}")

    def GetContractMarketData(self, contract: Contract):
        try:
            print("Market Data Auto Function")
            [ticker] = self.ib.reqTickers(self.contractdex)
            print(F"Contract Ticker  {ticker}")
            return ticker.marketPrice()
        except Exception as e:
            print(F"Failed to get Contract File   .... {e}")
            return -1

    def getMaster(self):
        try:
            print("*************** Downlaoding Master File **********************")
            # https://www.interactivebrokers.com/en/trading/products-exchanges.php#/
            contract = Contract()
            contract.symbol = "SPX"
            contract.exchange = 'CBOE'
            contract.secType = "IND"  # Set security type to 'IND' for index
            master = self.ib.reqContractDetails(contract)
            # Display contract details

            option_symbols = []
            for contract_detail in master:
                print("\nContract Details:")
                optioncontract = contract_detail.contract
                print(contract_detail.contract)

                # Additional information available in contract_detail object
                print("Trading Hours:", contract_detail.tradingHours)
                print("Valid Exchanges:", contract_detail.validExchanges)
                print("Currency:", contract_detail.contract.currency)
                print("Primary Exchange:", contract_detail.contract.primaryExchange)
                if optioncontract.secType == "OPT":  # Filter for options contracts
                    option_symbols.append(optioncontract.localSymbol)
            # Print the list of option symbols
            print("Option Trading Symbols under SPX on CBOE:")
            for symbol in option_symbols:
                print(symbol)

            print("*************** End here (Downlaoding Master) **********************")
        except Exception as e:
            print("*************** Failed to process (Downlaoding Master) **********************")
            print(F"Error Occured while Downloading Master : {e}")

    def GetMarketData(self):
        response = self.ib.reqMktData(self.contract_index, '', False, True)
        self.ib.sleep(2)  # Allow time for market data to be fetched
        print(F" Requested Market Data is  : {response}")

    def StartTrading(self):
        print("Place Trades ----")
        self.GetHistoricalData_Index()

    def GetHistoricalData_Index(self):
        try:
            # Request historical data
            end_datetime = datetime.datetime.now()
            self.bars = self.ib.reqHistoricalData(
                self.contract_index,
                endDateTime=end_datetime,
                durationStr='1 D',
                barSizeSetting='1 min',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1,
                keepUpToDate=False
            )
            if len(self.bars) != 0:
                print(F"Response : Historicla Data  {self.bars[-1]}")
        except Exception as e:
            print("Error Occured ... while requesting historical Data")

    def GetLTP(self, contract_index):
        ltp = -1
        try:
            bars = self.ib.reqHistoricalData(
                contract_index,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting='1 min',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )

            if bars:
                last_bar = bars[-1]
                ltp = last_bar.close  # Last traded price (close price of the most recent bar)
                print(f"Last Traded Price for {contract_index}: {ltp}")
            else:
                print(f"No historical data available for {contract_index.symbol}")
                if contract_index.symbol == 'SPX':
                    ltp = 5580  # Forcefully By Passing LTP Mechanism

            return ltp
        except Exception as e:
            print(F"Failed to get LTP : {e}")
            return ltp

    def OnOrder(self, trade):
        if trade.orderStatus.status == 'Filled':
            fill = trade.fills[-1]

            print(
                f'{fill.time} - {fill.execution.side} {fill.contract.symbol} {fill.execution.shares} @ {fill.execution.avgPrice}')
        else:
            # print(F"Trade Event Handler : {trade}")
            pass

    def AutoPlaceOrderSystem(self):
        try:
            # Check if historical data is available
            if self.bars:
                """ self.contract_index =  Index(symbol='SPX',exchange=  'CBOE') """

                last_price = self.bars[-1].close
                contract_stock = Stock('NFLX', 'SMART', 'USD')

                # lest Place New Trades -- AAPL (APPLE)  on MARKET ORDER
                contract_aapl = Stock('AAPL', 'SMART', 'USD')

                verify_stk = self.ib.qualifyContracts(contract_stock)
                print(F"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ {verify_stk}")
                print(f"Last historical price for {contract_stock.symbol} is {last_price}")

                # Place an order
                order = MarketOrder('BUY', 1)
                trade = self.ib.placeOrder(contract_stock, order)
                self.OnOrder(trade)

                # Place an order  #500 Quantity of APPLE
                order = MarketOrder('BUY', 500)
                print("APPLE TRADE Executing....")
                trade = self.ib.placeOrder(contract_aapl, order)
                self.OnOrder(trade)

                # Wait for order to fill
                self.ib.sleep(2)
                print(trade)
            else:
                print("Historical market data not available for the specified contract.")
        except Exception as e:
            print(F"Failed to Place Trade ... {e}")

    def AutoPlaceOrderSystemSTOCKS(self):
        try:
            # Check if historical data is available
            if self.bars:
                """ self.contract_index =  Index(symbol='SPX',exchange=  'CBOE') """

                last_price = self.bars[-1].close
                contract_stock = Stock('NFLX', 'SMART', 'USD')

                verify_stk = self.ib.qualifyContracts(contract_stock)
                print(F"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ {verify_stk}")
                print(f"Last historical price for {contract_stock.symbol} is {last_price}")

                # Place an order
                order = MarketOrder('BUY', 1)
                trade = self.ib.placeOrder(contract_stock, order)
                self.ib.orderStatusEvent += self.OnOrder(trade)

                # Wait for order to fill
                self.ib.sleep(2)
                print(trade)
            else:
                print("Historical market data not available for the specified contract.")
        except Exception as e:
            print(F"Failed to Place Trade ... {e}")

    def RequestStockOptionChain(self):
        try:
            response = self.ib.reqSecDefOptParams(0, "IBM", "", "STK", 8314)
            print(F"Response of STK : {response}")
        except Exception as e:
            print(F"Error Ocuured while Requesting option Chain {e}")

    def CreateStructure(self, ListExpiryDtae: list, listStrikePrice: list):
        try:
            print()
            print("------------------- Expiry Date ---------")
            print(ListExpiryDtae)
            if len(ListExpiryDtae) > 0:
                count = 0
                for exp in ListExpiryDtae:
                    try:
                        if count > 3:
                            break

                        self.ListExpiryDate.append(int(exp))
                        count += 1
                    except Exception as e:
                        print(F"Failed to Convert Exact Expiry Conversion : {e}")

            if len(listStrikePrice) > 0:
                for st in listStrikePrice:
                    try:
                        self.ListStrikePrice.append(float(st))
                    except Exception as e:
                        print(F"Failed to Convert Exact StrikePrice Conversion : {e}")
            self.ListStrikePrice.sort()
            self.ListExpiryDate.sort()
            print()
            print()

        except Exception as e:
            print(F"Failed to provide Structure to : {e}")

    def RequestOptionChain(self):
        try:

            underlying = Index('SPX', 'CBOE')
            print("        ********  OPTION CHAIN *********")
            print(F"Requesting Option chain for {underlying.symbol}")
            # request_option_chain = self.ib.reqSecDefOptParams(underlying.symbol, '', underlying.secType, underlying.conId)
            contract_details = self.ib.reqContractDetails(underlying)

            if contract_details:
                conId = contract_details[0].contract.conId
                print(f"ConId for SPX: {conId}")

                # Request option chain using the fetched conId

                count_allowed_strikeprice = 0

                option_chain = self.ib.reqSecDefOptParams(underlying.symbol, '', underlying.secType, conId)

                strikeprice = []
                expiryDate = []
                for chain in option_chain:
                    if count_allowed_strikeprice >= 10:
                        break

                        # print(f"Exchange: {chain.exchange}")
                    # print(f"Underlying ConId: {chain.underlyingConId}")
                    # print(f"Trading Class: {chain.tradingClass}")
                    # print(f"Multiplier: {chain.multiplier}")
                    # print(f"Expirations: {chain.expirations}")
                    # print(f"Strikes: {chain.strikes}")
                    # print('-' * 50)

                    strikeprice = chain.strikes
                    expiryDate = chain.expirations
                    count_allowed_strikeprice += 1

            self.CreateStructure(expiryDate, expiryDate)

            # print("Requested : Option Chain : {request_option_chain}")
            # # Print the option chain
            # for chain in request_option_chain:
            #     print(f"Exchange: {chain.exchange}")
            #     print(f"Underlying ConId: {chain.underlyingConId}")
            #     print(f"Trading Class: {chain.tradingClass}")
            #     print(f"Multiplier: {chain.multiplier}")
            #     print(f"Expirations: {chain.expirations}")
            #     print(f"Strikes: {chain.strikes}")
            #     print('-' * 50)
            print("        ********  END Here (Requesting option Chain) *********")
        except Exception as e:
            print(F"failed to get Option Chain Response : {e}")

    def StartTrading(self):
        try:

            # self.Start_Timer()
            symbol = 'SPX'
            expiry = '20240730'  # Expiration date format: YYYYMMDD
            strike = 4000
            exchange = "CBOE"
            callput = "C"

            ltp = self.GetLTP(self.contract_index)
            print(F"LTP of Spot is  {ltp}")

            if ltp > 0:
                self.ButterFlyOptionStrategy(ltp)
                # self.ButterFlyOptionStrategyParentChild(ltp)
                self.OpenTrades()

            # option_contract = Option(symbol, expiry, strike, callput,exchange )

            # ltp = self.GetLTP(option_contract)
            # print(f"LTP for {symbol} {expiry} {strike}: {ltp}")


        except Exception as e:
            print(F"Error Occured while Trading Started .... {e}")

    def ButterFlyOptionStrategyBasketStyle(self, ltp: float):
        try:
            print("Strategy Creation [Butterfly option Strategy] using Basket Styler")

            # Need to Call this Inside this method
            if ltp > 0:
                # Allow Entry if we have LTP
                atmSPX = self._atmEngine.getAtm(ltp)
                StrikeOTM = self._atmEngine.getNextUpwardStrike(1)
                STRIKEITM = self._atmEngine.getNextDownStrike(1)
                print(F"ATM Strike Price ltp {ltp} : {atmSPX}")
                print(F"ITM Strike Price ltp {ltp} : {STRIKEITM}")
                print(F"OTM Strike Price ltp {ltp} : {StrikeOTM}")

                """  Create Option Contract """
                if len(self.ListExpiryDate) > 0:
                    nearest_expiry_date = str(int(self.ListExpiryDate[0]))
                    print(F"Contract Date of Option Trades is  : {nearest_expiry_date}")
                    # https://finance.yahoo.com/quote/%5ESPX/options/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuYmluZy5jb20v&guce_referrer_sig=AQAAAIiZgZbikl_N7xfig4mlyVc-N8C2w-gm5guo20cdwyDKANxBmVfSnydqUlZGFosMOTCsyCdg6Lnl-Zub_GrShDrNFgurKB37rLz9gZVTXUjpZ-vTOGNZyXBLwM2OdCTLSoQhGAPuHMa6gl0NGYkABRLmm3knsqIw1JXYWJJCvZlH

                    #         Option('SPY', '20170721', 240, 'C', 'SMART')  contract.primaryExchange = "ARCA
                    optionatm = Option(symbol='SPX', lastTradeDateOrContractMonth=str(nearest_expiry_date),
                                       strike=atmSPX,
                                       right='C',

                                       exchange='CBOE',
                                       currency="USD",
                                       tradingClass='SPX'
                                       )

                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionatm}")
                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionatm)}")

                    optionItm = Option(symbol='SPX', lastTradeDateOrContractMonth=nearest_expiry_date,
                                       strike=float(STRIKEITM),
                                       right='C',
                                       exchange='CBOE',
                                       currency="USD",
                                       # multiplier="5",           # Specify the multiplier

                                       tradingClass="SPX",

                                       )
                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionItm}")

                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionItm)}")

                    optionOTM = Option(symbol='SPX', lastTradeDateOrContractMonth=nearest_expiry_date,
                                       strike=float(StrikeOTM),
                                       right='C',
                                       exchange='CBOE',
                                       currency="USD",
                                       tradingClass='SPX')
                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionOTM}")
                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionOTM)}")

                    print("sending trades to auto system.....")
                    # Buy 1 In-The-Money (ITM) option
                    print('\n\n')
                    contracts = self.ib.qualifyContracts(optionItm, optionatm, optionOTM)

                    leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='BUY', exchange=contracts[0].exchange)
                    leg2 = ComboLeg(conId=contracts[1].conId, ratio=2, action='SELL', exchange=contracts[1].exchange)
                    leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='BUY', exchange=contracts[2].exchange)

                    bulk_order = Contract()
                    bulk_order.symbol = 'SPX'
                    # bulk_order.secIdType = 'Option'
                    bulk_order.exchange = 'CBOE'
                    bulk_order.currency = 'USD'
                    bulk_order.comboLegs = [leg1, leg2, leg3]

                    order = MarketOrder('BUY', 1)

                    self.ib.placeOrder(bulk_order, order)

                    # self.PlaceOrder(OptionContrat= optionItm , Quantity= 1, BuySell= "BUY")
                    # self.PlaceOrder(OptionContrat= optionatm , Quantity= 2,BuySell= "SELL")
                    # self.PlaceOrder(OptionContrat= optionOTM , Quantity= 1 ,  BuySell= "BUY")

            self.GetPendingOrder()


        except Exception as e:
            print(F"Error generated in Butterfly func : {e}")

    def ButterFlyOptionStrategyParentChild(self, ltp: float):
        try:
            print("Strategy Creation [Butterfly option Strategy] using ParentChild")
            # https://interactivebrokers.github.io/tws-api/bracket_order.html

            # Need to Call this Inside this method
            if ltp > 0:
                # Allow Entry if we have LTP
                atmSPX = self._atmEngine.getAtm(ltp)
                StrikeOTM = self._atmEngine.getNextUpwardStrike(1)
                STRIKEITM = self._atmEngine.getNextDownStrike(1)
                print(F"ATM Strike Price ltp {ltp} : {atmSPX}")
                print(F"ITM Strike Price ltp {ltp} : {STRIKEITM}")
                print(F"OTM Strike Price ltp {ltp} : {StrikeOTM}")

                """  Create Option Contract """
                if len(self.ListExpiryDate) > 0:
                    nearest_expiry_date = str(int(self.ListExpiryDate[0]))
                    print(F"Contract Date of Option Trades is  : {nearest_expiry_date}")
                    # https://finance.yahoo.com/quote/%5ESPX/options/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuYmluZy5jb20v&guce_referrer_sig=AQAAAIiZgZbikl_N7xfig4mlyVc-N8C2w-gm5guo20cdwyDKANxBmVfSnydqUlZGFosMOTCsyCdg6Lnl-Zub_GrShDrNFgurKB37rLz9gZVTXUjpZ-vTOGNZyXBLwM2OdCTLSoQhGAPuHMa6gl0NGYkABRLmm3knsqIw1JXYWJJCvZlH

                    #         Option('SPY', '20170721', 240, 'C', 'SMART')  contract.primaryExchange = "ARCA
                    optionatm = Option(symbol='SPX', lastTradeDateOrContractMonth=str(nearest_expiry_date),
                                       strike=atmSPX,
                                       right='C',

                                       exchange='CBOE',
                                       currency="USD",
                                       tradingClass='SPX'
                                       )

                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionatm}")
                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionatm)}")

                    optionItm = Option(symbol='SPX', lastTradeDateOrContractMonth=nearest_expiry_date,
                                       strike=float(STRIKEITM),
                                       right='C',
                                       exchange='CBOE',
                                       currency="USD",
                                       # multiplier="5",           # Specify the multiplier

                                       tradingClass="SPX",

                                       )
                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionItm}")

                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionItm)}")

                    optionOTM = Option(symbol='SPX', lastTradeDateOrContractMonth=nearest_expiry_date,
                                       strike=float(StrikeOTM),
                                       right='C',
                                       exchange='CBOE',
                                       currency="USD",
                                       tradingClass='SPX')
                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionOTM}")
                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionOTM)}")

                    print("sending trades to auto system.....")
                    # Buy 1 In-The-Money (ITM) option
                    print('\n\n')
                    contracts = self.ib.qualifyContracts(optionItm, optionatm, optionOTM)

                    leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='BUY', exchange=contracts[0].exchange)
                    leg2 = ComboLeg(conId=contracts[1].conId, ratio=2, action='SELL', exchange=contracts[1].exchange)
                    leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='BUY', exchange=contracts[2].exchange)

                    mutiple_trades = Bag('SPX', ComboLeg=[leg1, leg2, leg3], exchange='CBOE', currency='USD')

                    parent = Order(orderId=self.ib.client.getReqId(), action="BUY", orderType='MKT', totalQuantity=1)
                    takeprofit = Order()
                    takeprofit.orderId = parent.orderId + 1
                    takeprofit.action = "SELL"
                    takeprofit.orderType = 'LMT'
                    takeprofit.lmtPrice = 2
                    takeprofit.parentId = parent.orderId
                    takeprofit.totalQuantity = 1
                    takeprofit.transmit = True

                    ords = [parent, takeprofit]
                    for o in ords:
                        trade = self.ib.placeOrder(mutiple_trades, o)
                        print(trade)

            self.GetPendingOrder()


        except Exception as e:
            print(F"Error generated in Butterfly func : {e}")

    def ButterFlyOptionStrategy(self, ltp: float):
        try:
            print("Strategy Creation [Butterfly option Strategy]")

            # Need to Call this Inside this method
            if ltp > 0:
                # Allow Entry if we have LTP
                atmSPX = self._atmEngine.getAtm(ltp)
                StrikeOTM = self._atmEngine.getNextUpwardStrike(1)
                STRIKEITM = self._atmEngine.getNextDownStrike(1)
                print(F"ATM Strike Price ltp {ltp} : {atmSPX}")
                print(F"ITM Strike Price ltp {ltp} : {STRIKEITM}")
                print(F"OTM Strike Price ltp {ltp} : {StrikeOTM}")

                """  Create Option Contract """
                if len(self.ListExpiryDate) > 0:
                    nearest_expiry_date = str(int(self.ListExpiryDate[0]))
                    print(F"Contract Date of Option Trades is  : {nearest_expiry_date}")
                    # https://finance.yahoo.com/quote/%5ESPX/options/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuYmluZy5jb20v&guce_referrer_sig=AQAAAIiZgZbikl_N7xfig4mlyVc-N8C2w-gm5guo20cdwyDKANxBmVfSnydqUlZGFosMOTCsyCdg6Lnl-Zub_GrShDrNFgurKB37rLz9gZVTXUjpZ-vTOGNZyXBLwM2OdCTLSoQhGAPuHMa6gl0NGYkABRLmm3knsqIw1JXYWJJCvZlH

                    #         Option('SPY', '20170721', 240, 'C', 'SMART')  contract.primaryExchange = "ARCA
                    optionatm = Option(symbol='SPX', lastTradeDateOrContractMonth=str(nearest_expiry_date),
                                       strike=atmSPX,
                                       right='C',

                                       exchange='CBOE',
                                       currency="USD",
                                       tradingClass='SPX'
                                       )

                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionatm}")
                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionatm)}")

                    optionItm = Option(symbol='SPX', lastTradeDateOrContractMonth=nearest_expiry_date,
                                       strike=float(STRIKEITM),
                                       right='C',
                                       exchange='CBOE',
                                       currency="USD",
                                       # multiplier="5",           # Specify the multiplier

                                       tradingClass="SPX",

                                       )
                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionItm}")

                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionItm)}")

                    optionOTM = Option(symbol='SPX', lastTradeDateOrContractMonth=nearest_expiry_date,
                                       strike=float(StrikeOTM),
                                       right='C',
                                       exchange='CBOE',
                                       currency="USD",
                                       tradingClass='SPX')
                    print(F"VERIFY OPTION TRADES >>>>>>>>>>>>>>>>>>>>>>>> : {optionOTM}")
                    # print(F"Verify Contract Details : {self.ib.reqContractDetails(optionOTM)}")

                    print("sending trades to auto system.....")
                    # Buy 1 In-The-Money (ITM) option
                    self.PlaceOrder(OptionContrat=optionItm, Quantity=1, BuySell="BUY")
                    self.PlaceOrder(OptionContrat=optionatm, Quantity=2, BuySell="SELL")
                    self.PlaceOrder(OptionContrat=optionOTM, Quantity=1, BuySell="BUY")

            self.GetPendingOrder()


        except Exception as e:
            print(F"Error generated in Butterfly func : {e}")

    def CalculatePnl(self):
        try:
            # THis Pnl part can be done at Local Computation, if we have subscribe to Token...
            list_pnl = self.ib.pnl()
            if len(list_pnl) == 0:
                return
            self.List_Pnl_trades = list_pnl
            for trade in self.List_Pnl_trades:
                print(F"Pnl Trades is : {trade}")
        except Exception as e:
            print(F"Error Occured while Calculating Pnl :{e}")

    def UpdatePnl(self):
        try:
            print("*************")

            self.OpenTrades()
            self.CalculatePnl()

            if len(self.List_Executed_trades) == 0:
                print("No Open Trades Found in Executed System")
                return

            for trd in self.List_Executed_trades:
                print(F"Trades :{trd.execId}|Qty {trd.cumQty} BuySell:{trd.side} |Avg Price={trd.avgPrice} ")


        except Exception as e:
            print(" Failed to Update Pnl.. {e}")

    def DefineALlEvent(self):
        pass
        # self._timer_update = threading.Thread(target=self.UpdatePnl, daemon=True)
        # self._timer_update = threading.Timer(5.0, self.UpdatePnl).start()
        self._timer_update = threading.Thread(target=self.UpdatePnl)
        self._timer_update.daemon = True

    def Start_Timer(self):
        print()
        print()
        print("----------------------------------  Timer Event Call Back---------------------")
        self._timer_update.start()

    def OpenTrades(self):
        try:
            print()
            print()
            print()
            print(" -----------------   ALl Open Trades------")
            executedTrades = self.ib.executions()  # Get Executed Trades...

            # avoid Duplicate Entry .... self.List_Executed_trades
            for trade in executedTrades:
                """Add Trades one By One """

                """  Key to avoid Duplicate Entry is  : {execId='00012ec5.668fdb45.01.01'}"""
                if len(self.List_Executed_trades) == 0:

                    self.List_Executed_trades.append(trade)
                else:

                    if not any(x.execId == trade.execId for x in self.List_Executed_trades):
                        self.List_Executed_trades.append(trade)
                        # print(F'Avoided Duplicate Entry : {trade.execId}')

            print(F"Executed trades is : {self.List_Executed_trades}")
        except Exception as e:
            print("Failed to Execute Open Standing  Trades : {e}")

    def PlaceOrder(self, OptionContrat: Option, Quantity: int, BuySell: str):
        try:
            print("Activating Sytem.. new trades")
            # Request market data to get the current price (not mandatory for placing order)
            # market_data = self.ib.reqTickers(OptionContrat)
            market_data = True

            """
            tickers = ib.reqTickers(*contracts)



            """
            if market_data:
                # current_price = market_data[0].marketPrice()

                # Define the order
                order = MarketOrder(BuySell, Quantity)

                """ Helper
                 order = MarketOrder('BUY', 1)
                trade = self.ib.placeOrder(self.contract_index, order)

                # Wait for order to fill
                self.ib.sleep(2)
                   """
                # Place the order
                trade = self.ib.placeOrder(OptionContrat, order)

                # Print confirmation
                print("Trade placed successfully:")
                print(trade)

                time.sleep(10)

            else:
                print("Error: Market data not available for contract.")
        except Exception as e:
            print("Faield to Execute Trades")

    def GetPendingOrder(self):
        try:
            print(F"******************ALl Open Order***********************")

            list_ = self.ib.openOrders()
            for trd in list_:
                print(F"Open Trade is : {trd}")
        except Exception as e:
            print("Error Ocucred while requesting Pendiang Trades")

    def CloseAPI(self):
        print("Closing/ Disconenct Interactive Broker API session..")
        self.ib.disconnect()

    # Task 1 :  Setting up Loggin and Connect To TWS interactive Broker


class StartTask2:

    def init(self):
        update_thread = threading.Thread(target=self._tradingEngine.UpdatePnl)
        update_thread.daemon = True  # . Daemonize thread to ensure it exits when the main program does
        update_thread.start()

    def run(self):
        self._tradingEngine = TradingEngine()

        # Template to Request option chain
        # _tradingEngine.RequestStockOptionChain()
        self._tradingEngine.RequestOptionChain()

        self._tradingEngine.StartTrading()
        self.init()

        self._tradingEngine.AutoPlaceOrderSystem()

    def TimerEvent(self):
        while True:
            self._tradingEngine.UpdatePnl()
            time.sleep(60)  # 5 second Delay

    def CloseTradingAPI(self):
        self._tradingEngine.CloseAPI()


class netPosition:

    def __init__(self):
        self.List_netPosition = []
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, 0)

        self.NetPositionOrder()

    def NetPositionOrder(self):
        try:
            print("*************************  Net postion************************")
            while 5 > 0:
                list_open_posion = self.ib.positions()
                for pos in list_open_posion:
                    print(F"net position Trades : {list_open_posion}")
                    symbol = pos.symbol
                    strike = pos.strike
                    expiry = pos.lastTradeDateOrContractMonth
                    option = pos.right
                    entryprice = pos.avgCost
                    trdsym = pos.localSymbol
                    qty = pos.position
                    messgae = F"Pos :{symbol} {strike} {expiry} {option}| Qty :{qty}, Avg Price {entryprice}"
                self.ib.sleep(5)
        except Exception as e:
            print("Failed to get Net Position")


# t = netPosition()


s = StartTask2()
s.run()
s.TimerEvent()
# s.CloseTradingAPI()

# t = netPosition()
