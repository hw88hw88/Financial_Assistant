# import libraries
import os
import pickle
import time
import json
import file_mgt
import yfinance as yf
import pandas as pd

class APIFinData:
    # initialize the instance
    # input:
    # 1. stock_symbol_file: the file path of the file storing the stock symbols
    # 2. stock_symbol_downloadable_filename: the file path of the file storing downloadable symbols
    # 3. stock_symbol_undownloadable_filename: the file path of the file storing undownloadable symbols
    # 4. symbol_last_update_filename: the file path of the file storing the symbol last update
    def __init__(
            self,
            stock_symbol_file = 'CSV/S&P 500 Historical Components & Changes (Updated).csv',
            stock_symbol_downloadable_filename = 'CSV/downloadable_stock_code.csv',
            stock_symbol_undownloadable_filename = 'CSV/undownloadable_stock_code.csv',
            symbol_last_update_filename = 'JSON/symbol_update.json',
        ):
        # store the file path of stock code
        self.stock_symbol_file = stock_symbol_file
        # store the file path of the downloadable stock code
        self.stock_symbol_downloadable_filename = stock_symbol_downloadable_filename
        # store the file path of the undownloadable stock code
        self.stock_symbol_undownloadable_filename = stock_symbol_undownloadable_filename
        # store the date of last update of individual stock data
        self.symbol_last_update_filename = symbol_last_update_filename

    # this function retrieve the symbols of constituent stocks of the Standard & Poor’s 500 (S&P500) on a specified date from a csv file
    # input:
    # 1. trading_date: the trading date on which the list of S&P500 stocks were (This is the date to determine the list of S&P500 stocks. The list of symbols must be on or before <trading_date>)
    # output:
    # 1. a list of symbols
    def get_symbol_from_csv(
            self, 
            trading_date
        ):
        symbol=[]
        # using the list of symbols of S&P500 stocks from github
        ## Reference: <https://github.com/fja05680/sp500/blob/master/S%26P%20500%20Historical%20Components%20%26%20Changes%20(Updated).csv>
        with open(self.stock_symbol_file) as f:
            csv_str = f.read()
        lines = csv_str.split('\n')

        for line in range(len(lines)):
            # the first line is the heading
            if line == 0:
                continue
            # remove the character double quotation mark ' " '
            lines[line] = lines[line].replace('"', '')
            # remove the character space ' '
            lines[line] = lines[line].strip()
            # split the line of content
            tickers = lines[line].split(',')
            # tickers[0] is the date of the S&P500 components
            # skip the line of symbols before the start date of the financial period
            if (pd.Timestamp(tickers[0]) < pd.Timestamp(trading_date) and 
                line < len(lines) - 1):
                continue

            # split the line of content
            ## if the <trading_date> was the same as the trading date, use the trading date
            if pd.Timestamp(tickers[0]) == pd.Timestamp(trading_date):
                tickers = lines[line].split(',')
            else:
                ## the [line - 1] below means using the tickers before the <trading_date>, because there was no change to the list of S&P500 stocks
                tickers = lines[line - 1].split(',')
            # return the first line of raw data on or after financial period
            for ticker in range(len(tickers)):
                # skip the date element
                if ticker == 0:
                    continue
                if tickers[ticker] != '':
                    symbol.append(str(tickers[ticker]))
            # return the first line of raw data on or after financial period
            return symbol

    # get the financial data from external API
    # input:
    # 1. symbol: the stock code e.g. "MSFT", "MU"
    # 2. period_end: the end date of the period in string format 'yyyy-mm-dd' or pandas timestamp
    # output:
    # 1. raw_data: the dataframe from the external API
    def get_financial_data(
            self, 
            symbol, 
            period_end
        ):
        fm = file_mgt.FileMgt()
        # check the last update of the stock data
        if fm.check_file_exist(self.symbol_last_update_filename):
            symbol_last_update = fm.read_json(self.symbol_last_update_filename)
        else:
            symbol_last_update = {}

        is_force_download = True
        if symbol in symbol_last_update:
            # force to download if the period end is later than the last update
            if pd.Timestamp(symbol_last_update.get(symbol)) >= pd.Timestamp(period_end):
                is_force_download = False
        
        # check if the symbol has been tried but not downloadable
        ## reduce the number of requests made to the API
        if fm.check_file_exist(self.stock_symbol_undownloadable_filename) and not is_force_download:
            undownloadable_symbols = fm.read_from_csv(self.stock_symbol_undownloadable_filename)
            if symbol in undownloadable_symbols:
                # return None, if tried downloading but unsuccessful
                return None

        # store the raw data in pickle file for later retrieval
        pickle_filename='pickle/stock_data/'+symbol+'_max.pkl'
        # store the data frame of raw data in csv file, because this is human readable form
        df_csv_filename='CSV/stock_data/'+symbol+'_max.csv'

        # check if the folder exists for storing stock data in pickle
        if not fm.check_file_exist('pickle'):
            os.mkdir('pickle')
        if not fm.check_file_exist('pickle/stock_data'):
            os.mkdir('pickle/stock_data')

        # check if the folder exists for storing stock data in CSV
        if not fm.check_file_exist('CSV'):
            os.mkdir('CSV')
        if not fm.check_file_exist('CSV/stock_data'):
            os.mkdir('CSV/stock_data')

        # check if the folder exists for storing stock data in JSON
        if not fm.check_file_exist('JSON'):
            os.mkdir('JSON')

        ## check if the data was saved in files to reduce the number of requests made to API and save time
        if not fm.check_file_exist(pickle_filename) or is_force_download:
            # download the data from external source if not exist
            raw_data = yf.download(symbol, start='2022-01-01', auto_adjust=True)
            # update the last update to the time of downloading
            symbol_last_update[symbol] = str(pd.Timestamp.now())
            fm.write_to_json(
                to_json_content=symbol_last_update,
                filename=self.symbol_last_update_filename
            )
            # wait to avoid abuse the API
            time.sleep(0.001)

            # check if the raw data is empty
            # record downloadable and undownloadable symbols in CSV files for reference
            if raw_data is None or int(raw_data.size) < 1:
                if fm.check_file_exist(self.stock_symbol_undownloadable_filename):
                    undownloadable_symbols = fm.read_from_csv(self.stock_symbol_undownloadable_filename)
                else:
                    undownloadable_symbols = []
                if symbol not in undownloadable_symbols:
                    undownloadable_symbols.append(symbol)
                    to_csv_str = ''
                    for sym in undownloadable_symbols:
                        to_csv_str += str(sym) + ','
                    fm.write_csv(
                        csv_file_path=self.stock_symbol_undownloadable_filename,
                        to_csv_content=to_csv_str,
                    )
                return None
            if fm.check_file_exist(self.stock_symbol_downloadable_filename):
                downloadable_symbols = fm.read_from_csv(self.stock_symbol_downloadable_filename)
            else:
                downloadable_symbols = []
            if symbol not in downloadable_symbols:
                downloadable_symbols.append(symbol)
                to_csv_str = ''
                for sym in downloadable_symbols:
                    to_csv_str += str(sym) + ','
                fm.write_csv(
                    csv_file_path=self.stock_symbol_downloadable_filename,
                    to_csv_content=to_csv_str,
                )

            # convert the raw data to pickle format and
            # save to pickle file
            self.write_to_pickle_binary_file(filename=pickle_filename, data=raw_data)
            # save to human readable format, CSV file
            raw_data.to_csv(df_csv_filename)

        else:
            # load data from file
            raw_data=self.read_from_pickle_binary_file(filename=pickle_filename)
        return raw_data

    # finding the n (default: the first, if n is None) timestamp in the pandas frame from yfinance
    # input: 
    # 1. df: data frame storing a single stock
    # 2. n: (int) the Nth day in the data frame
    # output: 
    # 1. the n timestamp in the input data frame, in the format of pandas timestamp
    @staticmethod
    def get_nth_date(df, n=None):
        # finding the 1st day in the data frame
        df_dict=df.to_dict()
        ## the keys of the dict() are the name of columns
        df_dict_columns=list(df_dict.keys())
        ## the keys are the time stamp of each row
        df_dict_key_time=list(df_dict[df_dict_columns[0]].keys())
        if n is None:
            ## the first timestamp
            return pd.Timestamp(df_dict_key_time[0])
        else:
            ## the Nth timestamp
            if abs(n) < len(df_dict_key_time):
                return pd.Timestamp(df_dict_key_time[n])
            else:
                # if abs(n) is large than the number of rows in the data frame
                # return the last date in the data frame
                return pd.Timestamp(df_dict_key_time[-1])

    # converting data the json format and save to a file (append the content)
    # input:
    # 1. to_json_content: content in dict{}
    # 2. filename: the file path of the JSON file
    # output:
    # No return value
    # JSON file content was added
    @staticmethod
    def append_to_json(
            to_json_content, 
            filename
        ):
        content = json.dumps(to_json_content)
        with open(filename, 'a') as f:
            f.write(content)

    # reading pickle from binary file
    # input:
    # 1. filename: the file path of pickle file
    # output:
    # 1. the file content
    @staticmethod
    def read_from_pickle_binary_file(filename):
        with open(filename, 'rb') as f:
            data = f.read()
        return pickle.loads(data)

    # writing pickle to binary file
    # input:
    # 1. filename: file path
    # 2. data: the content to be written to the file
    # output:
    # No return value
    # content written to pickle file
    @staticmethod
    def write_to_pickle_binary_file(
            filename, 
            data
        ):
        pickled_data=pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        with open(filename, 'wb') as f:
            f.write(pickled_data)

