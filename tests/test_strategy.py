import unittest
import strategy
import numpy as np
import simulation
import api_fin_data

class TestStrategy(unittest.TestCase):
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(strategy.Strategy)

        s=strategy.Strategy(start_up_cash=100000)
        self.assertIsNotNone(s.reset)
        self.assertIsNotNone(s.rewards)
        self.assertIsNotNone(s.cumulative_return)
        self.assertIsNotNone(s.stock_cumulative_return)
        self.assertIsNotNone(s.stock_roi)
        self.assertIsNotNone(s.stocks)
        # self.assertIsNotNone(s.annual_return)
        self.assertIsNotNone(s.max_drawdown)
        self.assertIsNotNone(s.num_of_trade)
        self.assertIsNotNone(s.cash)
        self.assertIsNotNone(s.total_value)
        self.assertIsNotNone(s.high_value)
        self.assertIsNotNone(s.low_value)
        self.assertIsNotNone(s.total_value_sequence)
        self.assertIsNotNone(s.age)
        self.assertIsNotNone(s.num_of_increase_in_value)
        self.assertIsNotNone(s.start_up_cash)

        self.assertIsNotNone(s.gdict)
        self.assertIsNotNone(s.gene)
        self.assertIsNotNone(s.spec)

        self.assertIsNotNone(s.rebalance)
        self.assertIsNotNone(s.buy_stock)
        self.assertIsNotNone(s.sell_stock)
        self.assertIsNotNone(s.daily_update)
        self.assertIsNotNone(s.fitness)
        self.assertIsNotNone(s.calculate_max_drawdown)
        self.assertIsNotNone(s.calculate_sharpe_ratio)

    # test get_market_info() output
    def test_mkt_info(self):
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        st=strategy.Strategy(start_up_cash=100000)
        api= api_fin_data.APIFinData()

        s_df=sim.calculate_fin_indicator_for_stock(st=st, symbol='MSFT')

        current_trading_date=api.get_nth_date(df=s_df, n=1)
        
        # select the current trading date
        stock_df=s_df.loc[(s_df.index == current_trading_date)]

        # convert to python dict{}
        stock_dict=stock_df.to_dict()

        ## find the current stock symbol
        symbol=(list(stock_dict.keys())[0][1])

        result=st.get_market_info(current_trading_date, s_df, symbol)

        self.assertIsNotNone(result['current_price'])
        self.assertIsNotNone(result['market_volume'])

        self.assertEqual(str(type(result['current_price'])), "<class 'float'>")
        self.assertEqual(str(type(result['market_volume'])), "<class 'int'>")

    # test the change of buy_stock() made
    def test_buy_stock(self):
        # initialize the test
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash=100000
        st=strategy.Strategy(start_up_cash=start_up_cash)
        api= api_fin_data.APIFinData()

        s_df=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')

        current_trading_date=api.get_nth_date(df=s_df, n=1)

        ## select the current trading date
        stock_df=s_df.loc[(s_df.index == current_trading_date)]

        ## convert to python dict{}
        stock_dict=stock_df.to_dict()

        ## find the current stock symbol
        symbol=(list(stock_dict.keys())[0][1])

        current_target_portfolio=['AAPL', 'MSFT']

        # no stock in portfolio
        self.assertEqual(len(list(st.stocks.keys())), 0)

        trading_fee=0.01

        st.buy_stock(
                  current_trading_date=current_trading_date, 
                  stock_df=stock_df, 
                  current_target_portfolio=current_target_portfolio, 
                  symbol=symbol,
                  trading_fee=trading_fee)

        # the stock of AAPL was bought
        self.assertIsNotNone(st.stocks[symbol])
        
        # on correct date
        self.assertEqual(st.stocks[symbol]['date'], current_trading_date)
        
        # the amount is less than the cash distributed to the stock, because of trading fee
        self.assertLess(st.stocks[symbol]['cost'], start_up_cash)
        
        # check: volume * (price + trading fee) = purchasing cost
        self.assertEqual(st.stocks[symbol]['volume'] * (stock_df['Close', symbol][current_trading_date] + trading_fee), st.stocks[symbol]['cost'])
        
        # check cash balance
        ## cash allocated to the current stock
        cash_allocated = start_up_cash / len(current_target_portfolio)
        self.assertEqual(st.cash, (cash_allocated - st.stocks[symbol]['cost'] + cash_allocated))
        
        # check num_of_trade
        self.assertGreaterEqual(st.num_of_trade, 1)

        # check stock_cumulative_return[symbol]
        self.assertIsNotNone(st.stock_cumulative_return[symbol])
        self.assertEqual(st.stock_cumulative_return[symbol], 0)

        # check stock_roi[symbol]
        self.assertIsNotNone(st.stock_roi[symbol])
        self.assertEqual(st.stock_roi[symbol], 0)

    # check sell_stock()
    def test_sell_stock(self):
        # initialize the test
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash=100000
        st=strategy.Strategy(start_up_cash=start_up_cash)
        api= api_fin_data.APIFinData()

        s_df=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')

        current_trading_date=api.get_nth_date(df=s_df, n=1)

        ## select the current trading date
        stock_df=s_df.loc[(s_df.index == current_trading_date)]

        ## convert to python dict{}
        stock_dict=stock_df.to_dict()

        ## find the current stock symbol
        symbol=(list(stock_dict.keys())[0][1])

        current_target_portfolio=['AAPL', 'MSFT']

        trading_fee=0.01

        st.buy_stock(
                  current_trading_date=current_trading_date, 
                  stock_df=stock_df, 
                  current_target_portfolio=current_target_portfolio, 
                  symbol=symbol,
                  trading_fee=trading_fee)

        # the stock of AAPL was bought
        self.assertIsNotNone(st.stocks[symbol])

        # sell the stock of AAPL
        st.sell_stock(
                  current_trading_date=current_trading_date,
                  stock_df=stock_df,
                  symbol=symbol,
                  trading_fee=trading_fee)

        # the stock of AAPL was sold
        self.assertFalse(symbol in st.stocks)
        self.assertFalse(symbol in st.stock_cumulative_return)
        self.assertFalse(symbol in st.stock_roi)

        # check cash balance
        ## the loss was due to the trading fee
        self.assertLess(st.cash, start_up_cash)

        # check num_of_trade
        self.assertEqual(st.num_of_trade, 2)

    # check daily_update()
    def test_daily_update(self):
        # initialize the test
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash=100000
        st=strategy.Strategy(start_up_cash=start_up_cash)
        api= api_fin_data.APIFinData()

        symbol='MSFT'
        s_df_aapl=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        s_df_msft=sim.calculate_fin_indicator_for_stock(st=st, symbol=symbol)

        current_trading_date=api.get_nth_date(df=s_df_aapl, n=1)
        trading_fee=0.01

        stocks_df=[s_df_aapl, s_df_msft]

        current_target_portfolio=['AAPL', 'MSFT']

        st.buy_stock(
                  current_trading_date=current_trading_date,
                  stock_df=s_df_msft,
                  current_target_portfolio=current_target_portfolio,
                  symbol=symbol,
                  trading_fee=trading_fee)
        
        # check the cumulative returns and ROI
        self.assertIsNotNone(st.stocks[symbol])
        self.assertIsNotNone(st.stock_cumulative_return[symbol])
        self.assertIsNotNone(st.stock_roi[symbol])
        self.assertEqual(st.cumulative_return, st.stock_cumulative_return[symbol])
        self.assertEqual(float(st.stock_cumulative_return[symbol] / st.stocks[symbol]['cost']), st.stock_roi[symbol])

        st.daily_update(
                     stocks_df=stocks_df,
                     current_trading_date=current_trading_date,
                     trading_fee=trading_fee)

        # check the daily_update()
        self.assertGreater(start_up_cash, st.total_value)
        self.assertEqual(st.age, 1)
        self.assertIsNotNone(st.max_drawdown)

        self.assertIsNotNone(st.stocks[symbol])
        self.assertIsNotNone(st.stock_cumulative_return[symbol])
        self.assertIsNotNone(st.stock_roi[symbol])
        self.assertAlmostEqual(st.cumulative_return, st.stock_cumulative_return[symbol])
        self.assertEqual(float(st.stock_cumulative_return[symbol] / st.stocks[symbol]['cost']), st.stock_roi[symbol])

    # check rebalance()
    def test_rebalancing(self):
        # initialize the test
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash=100000
        st=strategy.Strategy(start_up_cash=start_up_cash)
        api= api_fin_data.APIFinData()

        symbol='MSFT'
        s_df_aapl=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        s_df_msft=sim.calculate_fin_indicator_for_stock(st=st, symbol=symbol)

        current_trading_date=api.get_nth_date(df=s_df_aapl, n=1)
        next_trading_date=api.get_nth_date(df=s_df_aapl, n=2)
        trading_fee=0.01

        stocks_df=[s_df_aapl, s_df_msft]

        current_target_portfolio=['AAPL']

        st.rebalance(
            current_target_portfolio=current_target_portfolio, 
            stocks_df=stocks_df,
            current_trading_date=current_trading_date,
            trading_fee=trading_fee)
        
        # check if the target stocks were bought
        self.assertIsNotNone(st.stocks['AAPL'])

        # check cash balance after the trade
        self.assertLess(st.cash, start_up_cash)

        # daily update
        st.daily_update(
            stocks_df=stocks_df,
            current_trading_date=current_trading_date,
            trading_fee=trading_fee)
        
        # check total value
        self.assertLess(st.total_value, start_up_cash)

        # next day
        current_target_portfolio=[]

        st.rebalance(
            current_target_portfolio=current_target_portfolio, 
            stocks_df=stocks_df,
            current_trading_date=next_trading_date,
            trading_fee=trading_fee)

        # check if the target stocks were being held and sold
        self.assertFalse('AAPL' in list(st.stocks.keys()))

    # check fitness()
    def test_fitness(self):
        # initialize the test
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash=100000
        st=strategy.Strategy(start_up_cash=start_up_cash)
        api= api_fin_data.APIFinData()

        symbol='MSFT'
        s_df_aapl=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        s_df_msft=sim.calculate_fin_indicator_for_stock(st=st, symbol=symbol)

        current_trading_date=api.get_nth_date(df=s_df_aapl, n=1)
        next_trading_date=api.get_nth_date(df=s_df_aapl, n=2)
        trading_fee=0.01

        stocks_df=[s_df_aapl, s_df_msft]

        current_target_portfolio=['AAPL', 'MSFT']

        st.rebalance(
            current_target_portfolio=current_target_portfolio, 
            stocks_df=stocks_df,
            current_trading_date=current_trading_date,
            trading_fee=trading_fee)
        
        st.daily_update(
            stocks_df=stocks_df,
            current_trading_date=current_trading_date,
            trading_fee=trading_fee)
        
        self.assertFalse(0, st.rewards)

    def test_calculate_max_drawdown(self):
        st = strategy.Strategy(start_up_cash=100000)
        data = [100, 120, 30, 90, 85, 110, 130, 40, 120, 50, 100, 10000]

        self.assertEqual(-0.75, st.calculate_max_drawdown(data))

    def test_calculate_sharpe_ratio(self):
        st = strategy.Strategy(start_up_cash=100000)

        value_list = [100, 102, 105, 140, 166, 105, 180, 110, 109, 112]

        sharpe_ratio = st.calculate_sharpe_ratio(value_list=value_list, risk_free_interest_rate = 0.03)

        self.assertIsNotNone(sharpe_ratio)
        self.assertEqual(np.round(sharpe_ratio, 2), 2.84)