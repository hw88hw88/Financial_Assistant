import unittest
import simulation
import strategy
import pandas as pd
import api_fin_data
import population

class TestSimulation(unittest.TestCase):
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(simulation.Simulation)

        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        self.assertIsNotNone(sim.api)
        self.assertIsNotNone(sim.calculate_fin_indicator_for_stock)
        self.assertIsNotNone(sim.sorting_stocks)
        self.assertIsNotNone(sim.get_stock_fin_indicator)
        self.assertIsNotNone(sim.run_strategy)
        self.assertIsNotNone(sim.find_first_last_trading_date)
        self.assertIsNotNone(sim.eval_population)
        self.assertIsNotNone(sim.find_nth_date_from_stocks)

    # test if functions return something
    # testing "calculate_fin_indicator_for_stock()"
    # testing "sorting_stocks()"
    def test_function_returns(self):
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        st=strategy.Strategy(start_up_cash=100000)

        # testing "calculate_fin_indicator_for_stock()"
        df_score=sim.calculate_fin_indicator_for_stock(st=st, symbol='MSFT')
        self.assertIsNotNone(df_score)
        df_score2=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        self.assertIsNotNone(df_score2)

        # testing "sorting_stocks()"
        stocks_df=[df_score, df_score2]
        ### finding the 1st day in the data frame
        first_date=api_fin_data.APIFinData.get_nth_date(df_score, n=1)

        sorting_stocks=sim.sorting_stocks(date_timestamp=first_date, stocks_df=stocks_df, st=st)
        self.assertIsNotNone(sorting_stocks)

    # test if the functions return correct data type
    # testing "calculate_fin_indicator_for_stock()"
    # testing "sorting_stocks()"
    def test_function_return_type(self):
        sim=simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        st=strategy.Strategy(start_up_cash=100000)

        # testing "calculate_fin_indicator_for_stock()"
        df_score=sim.calculate_fin_indicator_for_stock(st=st, symbol='MSFT')
        self.assertEqual(str(type(df_score)), "<class 'pandas.DataFrame'>")

        # testing "sorting_stocks()"
        df_score2=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        stocks_df=[df_score, df_score2]
        ### finding the 1st day in the data frame
        first_date=api_fin_data.APIFinData.get_nth_date(df_score)

        sorted_stocks=sim.sorting_stocks(date_timestamp=first_date, stocks_df=stocks_df, st=st)
        self.assertEqual(str(type(sorted_stocks)), "<class 'list'>")

    # test if the returned value is correct
    # testing "calculate_fin_indicator_for_stock()"
    # testing "sorting_stocks()"
    def test_function_return_value(self):
        fin_start='2023-01-01'
        fin_end='2023-01-31'
        sim=simulation.Simulation(fin_start=fin_start, fin_end=fin_end, trading_fee=0.01)
        st=strategy.Strategy(start_up_cash=100000)

        # testing "calculate_fin_indicator_for_stock()"
        df_score=sim.calculate_fin_indicator_for_stock(st=st, symbol='MSFT')
        df_score_dict=df_score.to_dict()
        columns=list(df_score_dict.keys())
        key_time=list(df_score_dict[columns[0]].keys())
        ## The returned data frame should be within the specified period
        self.assertGreaterEqual(pd.Timestamp(key_time[0]), pd.Timestamp(fin_start))
        self.assertLessEqual(pd.Timestamp(key_time[-1]), pd.Timestamp(fin_end))

        ## check existance of new columns
        self.assertIsNotNone(df_score['rsi'])
        self.assertIsNotNone(df_score['ma_short'])
        self.assertIsNotNone(df_score['ma_long'])
        self.assertIsNotNone(df_score['signal_score'])
        self.assertIsNotNone(df_score['daily_returns'])

        ## check data type of new columns
        self.assertEqual(str(type(df_score['rsi'])), "<class 'pandas.Series'>")
        self.assertEqual(str(type(df_score['ma_short'])), "<class 'pandas.Series'>")
        self.assertEqual(str(type(df_score['ma_long'])), "<class 'pandas.Series'>")
        self.assertEqual(str(type(df_score['signal_score'])), "<class 'pandas.Series'>")
        self.assertEqual(str(type(df_score['daily_returns'])), "<class 'pandas.Series'>")

        # testing "sorting_stocks()"
        df_score2=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        stocks_df=[df_score, df_score2]
        ## finding the 1st day in the data frame
        first_date=api_fin_data.APIFinData.get_nth_date(df_score)

        sorted_stocks=sim.sorting_stocks(date_timestamp=first_date, stocks_df=stocks_df, st=st)
        ## testing the length of the returned value
        ### the no. of stock in this testing should be 2. They are 'AAPL' & 'MSFT'. st.gdict['max_num_of_stock'] can be more than 2.
        self.assertLessEqual(len(sorted_stocks), st.gdict['max_num_of_stock'])

    # test run_strategy()
    def test_run_strategy(self):
        sim = simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash =100000
        st = strategy.Strategy(start_up_cash=start_up_cash)

        sim.run_strategy(st=st)
        self.assertEqual(len(list(st.stocks.keys())), 0)
        self.assertNotEqual(st.total_value, start_up_cash)

    # test eval_population()
    def test_eval_population(self):
        sim = simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        pop = population.Population(start_up_cash=100000, pop_size=1)
        sim.eval_population(pop)

        self.assertIsNotNone(pop.strategies[0].age)
        self.assertEqual(str(type(pop.strategies[0].age)), "<class 'int'>")
        self.assertGreater(pop.strategies[0].age, 0)

    # test get_stock_fin_indicator()
    def test_get_stock_fin_indicator(self):
        sim = simulation.Simulation(fin_start='2023-01-01', fin_end='2023-01-31', trading_fee=0.01)
        start_up_cash =100000
        st = strategy.Strategy(start_up_cash=start_up_cash)
        df = sim.get_stock_fin_indicator(
            st=st
        )
        self.assertIsNotNone(df)
        self.assertEqual(str(type(df)), "<class 'list'>")

    # test find_first_last_trading_date()
    def test_find_first_last_trading_date(self):
        fin_start='2023-01-01'
        fin_end='2023-01-31'
        sim=simulation.Simulation(fin_start=fin_start, fin_end=fin_end, trading_fee=0.01)
        st=strategy.Strategy(start_up_cash=100000)
        df_score=sim.calculate_fin_indicator_for_stock(st=st, symbol='MSFT')
        df_score2=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        stocks_df=[df_score, df_score2]

        first_trading_date, last_trading_date = sim.find_first_last_trading_date(
            stocks_df=stocks_df
        )

        self.assertIsNotNone(first_trading_date)
        self.assertIsNotNone(last_trading_date)
        self.assertEqual(str(type(first_trading_date)), "<class 'pandas.Timestamp'>")
        self.assertEqual(str(type(last_trading_date)), "<class 'pandas.Timestamp'>")
        self.assertLess(pd.Timestamp(first_trading_date), pd.Timestamp(last_trading_date))

    # test find_nth_date_from_stocks()
    def test_find_nth_date_from_stocks(self):
        fin_start='2023-01-01'
        fin_end='2023-01-31'
        sim=simulation.Simulation(fin_start=fin_start, fin_end=fin_end, trading_fee=0.01)
        st=strategy.Strategy(start_up_cash=100000)
        df_score=sim.calculate_fin_indicator_for_stock(st=st, symbol='MSFT')
        df_score2=sim.calculate_fin_indicator_for_stock(st=st, symbol='AAPL')
        stocks_df=[df_score, df_score2]

        trading_date, df = sim.find_nth_date_from_stocks(
            stocks_df=stocks_df,
            n=0
            )

        self.assertIsNotNone(trading_date)
        self.assertEqual(str(type(trading_date)), "<class 'pandas.Timestamp'>")
        self.assertGreaterEqual(pd.Timestamp(trading_date), pd.Timestamp(fin_start))

        trading_date, df = sim.find_nth_date_from_stocks(
            stocks_df=stocks_df,
            n=-1
            )
        self.assertIsNotNone(trading_date)
        self.assertEqual(str(type(trading_date)), "<class 'pandas.Timestamp'>")
        self.assertLessEqual(pd.Timestamp(trading_date), pd.Timestamp(fin_end))
