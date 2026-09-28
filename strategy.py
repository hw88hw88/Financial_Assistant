import genome
import numpy as np
import pandas as pd

class Strategy:
    # initialise the instance
    # input:
    # 1. start_up_cash: the start up amount of capital
    # 2. (optional) gene: the gene of a strategy
    # 3. (optional) spec: the spec of a strategy
    # 4. (optional) gdict: the gdict of a strategy
    def __init__(
        self, 
        start_up_cash=100000, 
        gene=None, 
        spec=None, 
        gdict=None
        ):
        # the configuration or structure of the strategy
        if spec is None:
            spec=genome.Genome.get_gene_spec()
        self.spec=spec

        if gene is None:
            gene=genome.Genome.get_random_gene(len(spec))
        self.gene=gene

        if gdict is None:
            gdict=genome.Genome.get_gdict(
                gene=gene,
                spec=spec
            )
        self.gdict = gdict

        self.reset(start_up_cash=start_up_cash)

    # reset the parameters of the strategy
    # input:
    # 1. start_up_cash: the start up amount of capital
    def reset(self, start_up_cash):
        # record the performance
        self.rewards=0
        self.cumulative_return=0
        # the structure of <self.stocks{}> :
        # stocks[symbol]['cost'], stocks[symbol]['volume'], stocks[symbol]['date']
        ## <symbol> can be 'MSFT', 'AAPL' and so on.
        self.stocks={}
        # the structure of <self.stock_cumulative_return{}>:
        # self.stock_cumulative_return{symbol: return}
        ## For example, self.stock_cumulative_return{'MSFT': 10,000}
        self.stock_cumulative_return={}
        # the structure of <self.stock_roi}>:
        # self.stock_roi{symbol: return}
        ## For example, self.stock_roi{'MSFT': 0.1}
        self.stock_roi={}
        self.max_drawdown=0
        self.num_of_increase_in_value=0
        self.age=0
        self.num_of_trade=0
        self.cash=start_up_cash
        self.start_up_cash=start_up_cash

        # the value of the portfolio
        self.total_value=self.cash
        self.high_value=self.cash
        self.low_value=self.cash
        self.total_value_sequence=[]

        # portfolio
        self.portfolio_sequence={}

        self.sharpe_ratio=0

    # retrieve the market price and volume from the input data
    # input:
    # 1. current_trading_date: pandas timestamp of the date of the trading date
    # 2. stock_df: pandas data frame of a stock
    # 3. symbol: the symbol of the stock, such as 'MSFT' or 'AAPL'
    # output:
    # 1. current price of the share
    # 2. the market volume on the current trading day
    def get_market_info(
            self, 
            current_trading_date, 
            stock_df, 
            symbol
        ):
        ## get the current information of the stock on the market
        ### get the data on the current date
        current_this_stock = stock_df.loc[stock_df.index == current_trading_date]
        ### convert to dict{}
        current_this_stock_dict = current_this_stock.to_dict()

        ## finding the price & volume of the stock
        current_price=current_this_stock_dict['Close', symbol][current_trading_date]
        market_volume=current_this_stock_dict['Volume', symbol][current_trading_date]

        return {'current_price': current_price, 'market_volume': market_volume}

    # a function to add a stock to the portfolio
    # input:
    # 1. current_trading_date: pandas timestamp of the date of the trading date
    # 2. stock_df: pandas data frame of a stock to be bought
    # 3. current_target_portfolio: a list of symbols of target stocks of a new portfolio
    # 4. symbol: the symbol of the stock to be bought, such as 'MSFT' or 'AAPL'
    # 5. trading_fee: the fee for trading the stocks in percentage of the stock price
    # change: (the change it makes, not the return value)
    # 1. deduct self.cash to buy shares
    # 2. add to self.stocks{} the volume, date, cost of the newly bought shares
    # 3. add self.num_of_trade by 1
    # 4. add the symbol to self.stock_cumulative_return[symbol]
    # 5. add the symbol to self.stock_roi[symbol]
    def buy_stock(
            self, 
            current_trading_date, 
            stock_df, 
            current_target_portfolio, 
            symbol,
            trading_fee
        ):
        # get market information
        mkt_info=self.get_market_info(current_trading_date=current_trading_date,
                                      stock_df=stock_df,
                                      symbol=symbol)
        current_price = mkt_info['current_price']
        market_volume = mkt_info['market_volume']

        ## the value and volume to be bought
        ### the less of available stocks and maximum number of stocks allowed by the gdict of the strategy
        target_num_of_stocks = min(len(current_target_portfolio), self.gdict['max_num_of_stock'])
        
        # check if the target number of stocks is 0
        if target_num_of_stocks <= 0:
            return

        target_value = int(np.floor(self.cash / target_num_of_stocks))
        # target volume must be an integer
        # buyers cannot buy less than 1 share, and sellers cannot sell less than 1 share
        target_volume = int(np.floor(target_value / (current_price + trading_fee)))

        ### check if the volume is larger than market volume (very rarely)
        target_volume = min(target_volume, market_volume)

        # check if the volume is > 0 to avoid error from division by 0
        if target_volume <= 0:
            print('target volume <= 0: ', target_volume,', symbol:', symbol, ', date=', current_trading_date)
            return
        elif target_value <= 0:
            # stop buying if target value is 0 or below 0
            print('target value <= 0: ', target_value, ', symbol:', symbol, ', date=', current_trading_date)
            return

        ## reduce cash
        buying_cost = target_volume * (current_price + trading_fee)
        self.cash -= buying_cost

        ## get the shares
        self.stocks[symbol]={
            'volume': target_volume, 
            'date': current_trading_date, 
            'cost': buying_cost,
            }

        ## add number of trade
        self.num_of_trade+=1
        ## add the cumulative return for each stock
        self.stock_cumulative_return[symbol]=0.0
        ## add the roi for each stock
        self.stock_roi[symbol]=0.0

    # a function to remove a stock from the portfolio
    # input:
    # 1. current_trading_date: pandas timestamp of the date of the trading date
    # 2. stock_df: pandas data frame of a stock to be sold
    # 3. symbol: the symbol of the stock to be sold, such as 'MSFT' or 'AAPL'
    # 4. trading_fee: the fee for trading the stocks in percentage of the stock price
    # change:
    # 1. add the cash (receiving money by selling the stock)
    # 2. remove the stock from portfolio
    # 3. add number of trades
    def sell_stock(
            self,
            current_trading_date,
            stock_df,
            symbol,
            trading_fee
        ):

        # get market information
        mkt_info=self.get_market_info(current_trading_date=current_trading_date,
                                      stock_df=stock_df,
                                      symbol=symbol)
        current_price = mkt_info['current_price']
        market_volume = mkt_info['market_volume']

        # calculate the volume of the shares to be sold
        volume_to_sell = self.stocks[symbol]['volume']
        ### check if the volume is larger than market volume (very rarely)
        volume_to_sell = min(market_volume, volume_to_sell)

        # check if volume > 0
        if volume_to_sell <= 0:
            # stop selling if volume is 0 or below 0
            return

        # receiving cash
        self.cash += volume_to_sell * (current_price - trading_fee)

        # deducting the stock from the portfolio
        if volume_to_sell == self.stocks[symbol]['volume']:
            self.stocks.pop(symbol)
            self.stock_cumulative_return.pop(symbol)
            self.stock_roi.pop(symbol)
        else:
            # the cost of the stock will be deducted from the returns from the sales
            # but the cost must be at least 0, it cannot be negative
            self.stocks[symbol]['cost'] = max(0, volume_to_sell * (current_price - trading_fee))
            self.stocks[symbol]['volume'] -= volume_to_sell

        self.num_of_trade+=1

    # calculate the maximum drawdown
    # input: value_sequence: a list of value, such as <self.total_value_sequence>
    # output: return the maximum drawdown
    @staticmethod
    def calculate_max_drawdown(value_sequence):
        max_peak = float('-inf')
        max_drawdown = 0.0
        
        for price in value_sequence:
            # the record high
            max_peak = max(price, max_peak)

            # the maximum drawdown up to the current element in <self.total_value_sequence>
            drawdown = (price - max_peak) / max_peak
            
            # the maximum drawdown of the drawdown up to current element in <self.total_value_sequence
            max_drawdown = min(drawdown, max_drawdown)
                
        return max_drawdown

    # calculate the Sharpe ratio of the portfolio 
    # (not to calculate the Sharpe ratio of individual stocks)
    # (for evaluating the performance, not for selecting stocks in portfolio)
    # input:
    # 1. value_list: a list of the total value sequence of the portfolio
    # 2. risk_free_interest_rate: the risk free interest rate
    # output:
    # 1. Sharpe ratio
    @staticmethod
    def calculate_sharpe_ratio(
        value_list, 
        risk_free_interest_rate = 0.03
        ):

        # using pandas series
        series = pd.Series(value_list)

        # calculating the daily returns
        daily_return = series.pct_change().dropna()

        # the number of trading days in a year is about 252 days
        ## Reference: https://www.stockgro.club/blogs/trading/how-many-trading-days-in-a-year/
        annualized_return = daily_return.mean() * 252
        annualized_volatility = daily_return.std() * np.sqrt(252)

        # avoid division by 0
        if annualized_volatility == 0:
            if annualized_return - risk_free_interest_rate <= 0:
                return 0
            else:
                # this should be very rare
                # having high return but zero volatility actually means running very fast without moving 
                print('annualized_return - risk_free_interest_rate= ', annualized_return - risk_free_interest_rate)
                print('annualized_volatility= ', annualized_volatility)
                return np.inf

        # calculating sharpe ratio
        sharpe_ratio = (annualized_return - risk_free_interest_rate) / annualized_volatility

        return sharpe_ratio

    # update the value of the stock and portfolio
    # input:
    # 1. stocks_df[]: a list of the pandas dataframe of all available stocks
    # 2. current_trading_date: pandas timestamp of the date of the trading date
    # 3. trading_fee: the fee for trading the stocks in percentage of the stock price
    # changes:
    # 1. update self.stock_cumulative_return[symbol], if the stock is in the portfolio
    # 2. update self.high_value, which stores the highest value of the total value of the portfolio
    # 3. update self.low_value, which stores the lowest value of the total value of the portfolio
    # 4. update self.cumulative_return, which is the cumulative return of the portfolio
    # 5. update self.total_value, which is the total value of the portfolio
    # 6. update self.num_of_increase_in_value, which is the number of times the value of the portfolio increase
    # 7. update self.max_drawdown, which is the highest
    # 8. update self.stock_roi[symbol], if the stock is in the portfolio
    def daily_update(
            self, 
            stocks_df,
            current_trading_date,
            trading_fee
        ):
        # initialise the new total value of portfolio
        new_portfolio_value = 0

        # iterate the stocks on the market
        for s in stocks_df.copy():
            # select the current trading date
            stock_df=s.loc[(s.index == current_trading_date)]

            # convert to python dict{}
            stock_dict=stock_df.to_dict()

            ## find the current stock symbol
            symbol=(list(stock_dict.keys())[0][1])

            ## if the stock is in the portfolio
            if symbol in list(self.stocks.keys()):
                # volume and cost of the stock in portfolio
                cost = self.stocks[symbol]['cost']
                volume = self.stocks[symbol]['volume']

                # if the volume of a stock in portfolio <= 0, the stock is not in the portfolio
                if volume <= 0:
                    print('Error: volume of ', symbol, ' <= 0')

                    # remove the stock
                    self.stocks.pop(symbol)
                    self.stock_cumulative_return.pop(symbol)
                    self.stock_roi.pop(symbol)

                    # stop processing the stock, and go to the next stock
                    continue

                # get market information
                mkt_info=self.get_market_info(
                    current_trading_date=current_trading_date,
                    stock_df=stock_df,
                    symbol=symbol
                )

                current_price = mkt_info['current_price']

                # check the stop-loss strategy
                ## cost / volume = cost per the share in the portfolio
                if current_price < cost / volume * (1 + self.gdict['stop_loss']):
                    # sell the stock
                    self.sell_stock(
                        current_trading_date=current_trading_date,
                        stock_df=stock_df,
                        symbol=symbol,
                        trading_fee=trading_fee
                    )
                    # the stock was sold and removed from portfolio
                    continue

                # check the take-profit strategy
                if current_price > cost / volume * (1 + self.gdict['take_profit']):
                    # sell the stock
                    self.sell_stock(
                                current_trading_date=current_trading_date,
                                stock_df=stock_df,
                                symbol=symbol,
                                trading_fee=trading_fee)
                    # the stock was sold and removed from portfolio
                    continue

                # update the stock_cumulative_return
                self.stock_cumulative_return[symbol] = float((volume * current_price) - cost)

                # update the stock ROI
                self.stock_roi[symbol] = float(((volume * current_price) - cost) / cost)

                # adding to portfolio value
                new_portfolio_value += volume * current_price

        # calculate the portfolio value, by adding the value of all stocks and cash in the portfolio
        new_portfolio_value += self.cash

        # update the portfolio value, high, low
        if new_portfolio_value >= self.total_value:
            self.num_of_increase_in_value += 1

        self.high_value = max(new_portfolio_value, self.high_value)
        self.low_value = min(new_portfolio_value, self.low_value)

        self.total_value = new_portfolio_value
        self.total_value_sequence.append(self.total_value)

        # update maximum drawdown of the portfolio
        self.max_drawdown = self.calculate_max_drawdown(self.total_value_sequence)

        # update the cumulative return of the portfolio
        self.cumulative_return = self.total_value - self.start_up_cash

        # calculate Sharpe ratio of the portfolio
        self.sharpe_ratio = self.calculate_sharpe_ratio(
            value_list=self.total_value_sequence
            )

        # update the age of the portfolio
        self.age += 1

        # update reward
        self.fitness()

    # this function perform the rebalancing of portfolio. The rebalancing will reset the portfolio to the target stocks
    # input:
    # 1. current_target_portfolio[]: numpy array storing the symbol of the target selected stocks
    # 2. stocks_df[]: the market data and the calculation of the financial indicators of each stock. 
    #                 The financial indicators were calculated based on the parameters in the strategy
    # 3. current_trading_date: the current trading date in the format of pandas timestamp
    # 4. trading_fee: 
    # change:
    # 1. the stocks of the portfolio will become the target stocks
    def rebalance(self, 
                  current_target_portfolio, 
                  stocks_df, 
                  current_trading_date,
                  trading_fee):
        # record the target portfolio on the trading day
        self.portfolio_sequence[str(current_trading_date)]=current_target_portfolio
        
        ## if no stock in the portfolio
        if len(list(self.stocks.keys())) == 0:
            for symbol in current_target_portfolio:
                for stock_df in stocks_df:
                    ## find the stock from data
                    stock_dict=stock_df.to_dict()
                    s_df_symbol=(list(stock_dict.keys())[0][1])

                    # if the stock was found
                    if s_df_symbol == symbol:
                        # buy the stocks
                        self.buy_stock(
                            current_trading_date=current_trading_date, 
                            stock_df=stock_df, 
                            current_target_portfolio=current_target_portfolio, 
                            symbol=symbol,
                            trading_fee=trading_fee,
                            )
                        break
        else:
            # there are stocks in the portfolio
            ## matching the current portfolio with target portfolio
            symbols_in_portfolio=list(self.stocks.keys())
            matched_stock_in_portfolio_index=[]
            for s_in_portfolio in symbols_in_portfolio:
                for s_target_portfolio in current_target_portfolio:
                    if s_in_portfolio == s_target_portfolio:
                        matched_stock_in_portfolio_index.append(s_in_portfolio)
                        break

            ## selling the unmatched stocks in the portfolio
            for s_in_p in symbols_in_portfolio:
                if s_in_p not in matched_stock_in_portfolio_index:
                    ### for all stocks in portfolio not in the matched list, which is a list of stocks to be held
                    for stock_df in stocks_df:
                        ### find the stock from data, then sell it
                        stock_dict=stock_df.to_dict()
                        s_df_symbol=(list(stock_dict.keys())[0][1])

                        #### if the stock was found, sell it
                        if s_df_symbol == s_in_p:
                            self.sell_stock(
                                current_trading_date=current_trading_date,
                                stock_df=stock_df,
                                symbol=s_in_p,
                                trading_fee=trading_fee,
                                )

            ## adding the target stocks to the portfolio if the stock not in the portfolio
            for target_stock in current_target_portfolio:
                if target_stock not in symbols_in_portfolio:
                    ### find the stock data
                    for stock_df in stocks_df:
                        ### find the stock from data, then buy it
                        stock_dict=stock_df.to_dict()
                        s_df_symbol=(list(stock_dict.keys())[0][1])

                        if s_df_symbol == target_stock:
                            self.buy_stock(
                                current_trading_date=current_trading_date, 
                                stock_df=stock_df, 
                                current_target_portfolio=current_target_portfolio, 
                                symbol=s_df_symbol,
                                trading_fee=trading_fee,
                            )

    # fitness function: this function calculates the total reward of the portfolio managed with the strategy
    # change:
    # 1. self.rewards: update the total rewards of the portfolio managed with the strategy
    def fitness(self):
        # reward 1:
        # cumulative return
        reward_cum_return = self.cumulative_return / self.start_up_cash

        # reward 2:
        # num_of_increase_in_value (number of having gains in a trading day) / age (number of trading days)
        reward_win_rate = self.num_of_increase_in_value / self.age

        # reward 3:
        # Sharpe ratio
        reward_sharpe_ratio = self.sharpe_ratio

        # penalty 1:
        # the range of maximum drawdown <self.max_drawdown> is [-1, 0]
        penalty_max_drawdown = self.max_drawdown * (-1)

        # penalty 2:
        # no. of trade <= self.age
        penalty_num_of_trade = self.num_of_trade / self.age

        # rewards
        self.rewards = float(
            max(
                0,
                0.25 * reward_cum_return
                + 0.05 * reward_win_rate
                + 0.7 * reward_sharpe_ratio
                - 0.05 * penalty_num_of_trade
                - 0.5 * penalty_max_drawdown
                )
            )

        # heavy penalty:
        # penalty 3:
        ## rewards would be 0 if the portfolio made a loss
        if self.cumulative_return < 0:
            self.rewards = 0

        # penalty 4:
        ## Sharpe ratio below 1 means poor performance, and the strategy is likely bad
        if self.sharpe_ratio < 1:
            self.rewards = 0

