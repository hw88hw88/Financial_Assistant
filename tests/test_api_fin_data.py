# the code in this file is newly written to unit-test the code in 'fin_data.py'
# the whole coding process followed the three laws of test driven development

import unittest
import api_fin_data
import os
import datetime

class TestAPIFinData(unittest.TestCase):
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(api_fin_data.APIFinData)

        get_fin_data=api_fin_data.APIFinData()
        self.assertIsNotNone(get_fin_data.stock_symbol_file)
        self.assertIsNotNone(get_fin_data.get_symbol_from_csv)
        self.assertIsNotNone(get_fin_data.get_financial_data)
        self.assertIsNotNone(get_fin_data.append_to_json)
        self.assertIsNotNone(get_fin_data.read_from_pickle_binary_file)
        self.assertIsNotNone(get_fin_data.write_to_pickle_binary_file)
        self.assertIsNotNone(get_fin_data.get_nth_date)

    # test if functions return or output something
    def test_function_returns(self):
        get_fin_data=api_fin_data.APIFinData()

        # testing "get_symbol_from_csv()"
        self.assertIsNotNone(get_fin_data.get_symbol_from_csv('2023-01-01'))

        # testing "get_financial_data()"
        ## make request to external API
        symbol='MSFT'
        data_msft=get_fin_data.get_financial_data(symbol=symbol, period_end='2023-01-01')
        self.assertIsNotNone(data_msft)

        symbol='ABC'
        data=get_fin_data.get_financial_data(symbol=symbol, period_end='2023-01-01')
        self.assertIsNone(data)

        # testing "append_to_json()"
        test_json_path='JSON/test.json'
        get_fin_data.append_to_json({'content': 'test content'}, test_json_path)
        self.assertTrue(os.path.exists(test_json_path))
        os.remove(test_json_path)

        # testing "write_to_pickle_binary_file()"
        test_pickle_path='pickle/test.pickle'
        get_fin_data.write_to_pickle_binary_file(test_pickle_path, 'test data')
        self.assertTrue(os.path.exists(test_pickle_path))

        # testing "read_from_pickle_binary_file()"
        read_pickle=get_fin_data.read_from_pickle_binary_file(test_pickle_path)
        self.assertIsNotNone(read_pickle)
        self.assertEqual(str(read_pickle), 'test data')

        ## remove the test pickle file
        os.remove(test_pickle_path)

        # testing "get_nth_date()"
        self.assertIsNotNone(get_fin_data.get_nth_date(data_msft))
        self.assertIsNotNone(get_fin_data.get_nth_date(data_msft, n=0))

    # test if variables store correct type of data
    def test_var_type(self):
        get_fin_data=api_fin_data.APIFinData()
        self.assertEqual(str(type(get_fin_data.stock_symbol_file)), "<class 'str'>")

    # test if get_financial_data() works as expected
    def test_get_financial_data(self):
        get_fin_data=api_fin_data.APIFinData()
        # make request to external API
        # the symbol 'MSFT' was in the list of stock symbol
        symbol='MSFT'
        api_data=get_fin_data.get_financial_data(symbol=symbol, period_end='2023-01-01')
        self.assertIsNotNone(api_data)
        # test if a pickle file was saved successfully, and test if the pickle can be read
        data=get_fin_data.read_from_pickle_binary_file('pickle/stock_data/' + symbol + '_max.pkl')
        self.assertIsNotNone(data)
        self.assertEqual(str(type(data)), "<class 'pandas.DataFrame'>")

        # the symbol 'ABC' not in the list of stock symbol at the time of writing the code
        symbol='ABC'
        api_data=get_fin_data.get_financial_data(symbol=symbol, period_end='2023-01-01')
        self.assertIsNone(api_data)
        # test if a pickle file was saved successfully, and test if the pickle can be read
        file_path='pickle/stock_data/' + symbol + '_max.pkl'
        self.assertFalse(os.path.exists(file_path))

        # check last update file
        symbol_last_update_filename = 'JSON/symbol_update.json'
        if os.path.exists(symbol_last_update_filename):
            with open(symbol_last_update_filename) as f:
                symbol_last_update = f.read()
            self.assertTrue('MSFT' in symbol_last_update)
            # although the symbol 'ABC' was not downloadable from yfinance, the symbol should still be in the list of symbol_last_update
            self.assertTrue('ABC' in symbol_last_update)

    # test if all constituent stocks of S&P500 can be retrieved
    # the result will be stored to two csv files ('downloadable_stock_code.csv' and 'undownloadable_stock_code.csv')
    def test_all_sp500(self):
        get_fin_data=api_fin_data.APIFinData()
        # the beginning of financial period used in unittesting, and testing,
        ## and the beginning commonly used in training and validation
        fin_start = ['2023-01-01', '2023-12-01', '2024-01-01', '2024-07-01', '2025-01-01', '2026-01-01']

        # the 
        downloadable = []
        undownloadable = []
        
        # get all stock code
        for fin_s in fin_start:
            symbols = get_fin_data.get_symbol_from_csv(fin_s)

            today_date = datetime.datetime.now()
            today_date = today_date.strftime('%Y-%m-%d')

            for s in symbols:
                data=get_fin_data.get_financial_data(symbol=s, period_end=today_date)
                if data is None:
                    undownloadable.append(s)
                else:
                    downloadable.append(s)

            # at least the data from a stock of S&P500 can be downloaded
            self.assertGreater(len(downloadable), 0)

            # check if files created successfully
            downloadable_filename='CSV/downloadable_stock_code.csv'
            undownloadable_filename='CSV/undownloadable_stock_code.csv'

            self.assertTrue(os.path.exists(downloadable_filename))
            self.assertTrue(os.path.exists(undownloadable_filename))

            # check the list of downloadable and undownloadable symbols respectively

            with open(downloadable_filename) as f:
                csv_content = f.read()
            for i in range(len(downloadable)):
                # check if downloadable symbols are recorded in CSV file
                self.assertTrue(downloadable[i] in csv_content)

            with open(undownloadable_filename) as f:
                csv_content = f.read()
            for i in range(len(undownloadable)):
                # check if downloadable symbols are recorded in CSV file
                self.assertTrue(undownloadable[i] in csv_content)

    # test get_symbol_from_csv()
    def test_get_symbol_from_csv(self):
        get_fin_data=api_fin_data.APIFinData()

        trading_date = ['2023-01-01', '2026-01-29', '2026-06-30', '2026-07-01', '2026-08-01']

        for td in trading_date:

            symbols = get_fin_data.get_symbol_from_csv(
                trading_date=td
            )
            self.assertIsNotNone(symbols)
            self.assertGreater(len(symbols), 0)
            self.assertEqual(str(type(symbols)), "<class 'list'>")
            for s in symbols:
                self.assertEqual(str(type(s)), "<class 'str'>")

