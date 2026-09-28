import file_mgt
import strategy
import simulation
import pandas as pd
import datetime
import re
import json
import numpy as np
from llama_cpp import Llama

class Chatbot:
    # initialize the chatbot
    # the function runs after being called, not run automatically at the start
    # input:
    # 1. model_path: the file path of the LLM gguf file
    def initialize_chatbot(
            self,
            model_path = "LLM/gemma-4-E2B-it-qat-q4_0-gguf/gemma-4-E2B_q4_0-it.gguf"
        ):
        self.max_token=4096
        ## loading the LLM
        self.llm = Llama(
            model_path=model_path, 
            n_gpu_layers=-1,
            n_ctx=4096,
        )
    # get the run_id from CSV file
    # input:
    # 1. num_of_run: the number of run_id in the CSV file.
    # 2. run_id_file_path: the file path of CSV file storing the run_id
    ## For example, 0 means the first run_id in the CSV
    # output:
    # 1. run_id
    # 2. None, if run_id cannot be retrieved
    @staticmethod
    def get_run_id(
            num_of_run = 0, 
            run_id_file_path = 'CSV/run_id.csv',
        ):
        fm = file_mgt.FileMgt()

        # import <run_id> from a list
        if fm.check_file_exist(run_id_file_path):
            with open (run_id_file_path) as f:
                csv_content = f.read()
                # separate each element
                csv_content = csv_content.split(',')

            # remove space ' ' from <csv_content>
            i = len(csv_content) - 1
            while i >= 0:
                csv_content[i] = csv_content[i].strip()
                if len(csv_content[i]) < 1:
                    csv_content.pop(i)
                i -= 1

            # determine the <run_id> from the list from file
            if len(csv_content) > 0:
                if num_of_run < len(csv_content):
                    run_id = csv_content[num_of_run]
                else:
                    print('<num_of_run> out of range. It has been set to the last one.')
                    run_id = csv_content[-1]
                return run_id
            else:
                print('There is no <run_id>. Please run the training first.')
        return None

    # read the trained strategy amd return
    # input:
    # 1. run_id: <run_id>
    # 2. hyper_params_file_path (optional): file path for training hyper parameters
    # 3. gdict_file_path (optional): file path for gdict
    # output:
    # 1. trained strategy: investment strategy
    # 2. gdict: the gene dictionary of strategy
    # 3. None, if either hyper-parameters of the training or gdict cannot be retrieved
    @staticmethod
    def get_strategy(
            run_id,
            hyper_params_file_path=None,
            gdict_file_path=None
        ):
        fm = file_mgt.FileMgt()
        # get training hyper-parameters
        ## (the file path depends on the run_id, so it is assigned here, rather than the input parameters)
        if hyper_params_file_path is None:
            hyper_params_file_path = 'JSON/' + str(run_id) + '/hyper_parameter.json'

        if fm.check_file_exist(hyper_params_file_path):
            hyper_params = fm.read_json(filename=hyper_params_file_path)
            num_of_gen = hyper_params.get('num_of_generations')

            # get gdict
            ## (the file path depends on the run_id, so it is assigned here, rather than the input parameters)
            if gdict_file_path is None:
                gdict_file_path = 'JSON/' + str(run_id) + '/fittest/elite_gdict_gen' + str(num_of_gen - 1) + '_0.json'

            if fm.check_file_exist(gdict_file_path):
                gdict = fm.read_json(
                    filename=gdict_file_path
                )

                # get gene for storing the gene in strategy instance
                gene_file_path = 'CSV/' + str(run_id) + '/fittest/elite_gene_gen' + str(num_of_gen - 1) + '_0.csv'

                gene = None

                if fm.check_file_exist(gene_file_path):
                    gene = fm.read_from_csv(
                        csv_file_path=gene_file_path
                    )

                stgy = strategy.Strategy(
                    start_up_cash=100000, 
                    gdict=gdict,
                    gene=gene
                    )
                return stgy, gdict
        return None, None

    # load data and financial indicators
    # input:
    # 1. trading_date: the trading date
    # 2. st: investment strategy instance
    # 3. trading_fee: e.g. 0.01 means 1% of the trading amount
    # output:
    # 1. stocks_df: a list of data frame of all stocks
    @staticmethod
    def get_data(
            trading_date,
            st,
            trading_fee=0.01
        ):

        # setting the start and end the same date to get the financial data on the trading day
        sim = simulation.Simulation(
            fin_start = trading_date,
            fin_end = trading_date,
            trading_fee = trading_fee
            )

        # getting the data frame of all stocks
        stocks_df = sim.get_stock_fin_indicator(
            st = st
            )
        return stocks_df

    # generating the target portfolio
    # input:
    # 1. st: investment strategy
    # 2. stocks_df: the data frame of all available stocks of S&P500
    # 3. trading_date: (str) the trading date in the format 'yyyy-mm-dd'
    # 4. trading_fee: the trading fee. E.g. 0.01 means 1% of the transaction amount
    # output:
    # 1. current_target_portfolio: a list of symbols of the target stocks
    @staticmethod
    def get_investment_portfolio(
            st,
            stocks_df,
            trading_date,
            trading_fee=0.01
        ):
        # setting the start and end the same date to get the financial data on the trading day
        sim = simulation.Simulation(
            fin_start = trading_date,
            fin_end = trading_date,
            trading_fee = trading_fee
            )

        current_target_portfolio = sim.sorting_stocks(
            date_timestamp=pd.Timestamp(trading_date), 
            stocks_df=stocks_df.copy(), 
            st=st)

        return current_target_portfolio

    # retrieving the financial information and the calculated financial indicators of the target portfolio for the chatbot
    # input:
    # 1. trading_date: (str) the trading date in the format 'yyyy-mm-dd'
    # 2. num_of_run: (int) the run id number. E.g. 0 means the first run_id in the CSV file
    # 3. trading_fee: (float) the trading fee. E.g. 0.01 means 1% of the trading amount
    # 4. run_id_file_path: (string) the file path of the run id CSV file
    # 5. hyper_params_file_path: (string) the file path of the hyper-parameter file
    # 6. gdict_file_path: (string) the file path of the gdict file
    # output:
    # 1. portfolio: a list of stock symbols
    # 2. portfolio_dict: a dictionary of information of stocks in portfolio
    # 3. st: an investment strategy
    # 4. gdict: dictionary of gene of strategy
    def apply_strategy(
            self,
            trading_date,
            num_of_run = 0,
            trading_fee = 0.01,
            run_id_file_path = 'CSV/run_id.csv',
            hyper_params_file_path=None,
            gdict_file_path=None
        ):
        # get run id
        run_id = self.get_run_id(
            num_of_run = num_of_run,
            run_id_file_path = run_id_file_path,
        )
        # get the strategy and gdict
        st, gdict = self.get_strategy(
            run_id = run_id,
            hyper_params_file_path=hyper_params_file_path,
            gdict_file_path=gdict_file_path,
        )
        # strategy should not be None
        if st is None:
            print('st is None')
            return None

        # the pandas data frame of all stocks
        stocks_df = self.get_data(
            trading_date = trading_date,
            st = st,
            trading_fee = trading_fee)

        # get a list of symbols of the stocks in portfolio
        portfolio = self.get_investment_portfolio(
            st = st,
            stocks_df = stocks_df,
            trading_date = trading_date,
            trading_fee=trading_fee
        )

        # store the portfolio stock data in dict{}
        portfolio_dict = {}

        # process each stock one by one
        for stock_df in stocks_df:
            # convert to python dict{}
            stock_dict = stock_df.to_dict()

            ## current stock symbol
            symbol=(list(stock_dict.keys())[0][1])

            # create the portfolio dict{}
            if symbol in portfolio:
                portfolio_dict[symbol] = {
                    'symbol': symbol,
                    'price': list(stock_dict['Close', str(symbol)].values())[0],
                    'ma_short': list(stock_dict['ma_short', ''].values())[0],
                    'ma_long': list(stock_dict['ma_long', ''].values())[0],
                    'rsi': list(stock_dict['rsi', ''].values())[0],
                    'daily_return': list(stock_dict['daily_returns', ''].values())[0],
                    'annualized_return': list(stock_dict['annualized_return', ''].values())[0],
                    'sharpe_ratio': list(stock_dict['sharpe_ratio', ''].values())[0],
                    'annualized_volatility': list(stock_dict['annualized_volatility', ''].values())[0],
                }

            # store investment strategy in portfolio
            portfolio_dict['stgy'] = {
                'stop_loss': gdict.get('stop_loss'),
                'take_profit': gdict.get('take_profit'),
                'num_of_day_rebalance': gdict.get('num_of_day_rebalance'),
                'buy_rsi': gdict.get('buy_rsi'),
                'sell_rsi': gdict.get('sell_rsi'),
            }

        return portfolio, portfolio_dict, st, gdict

    # classify the user input with the LLM
    # input:
    # 1. user_prompt: (str) user prompt
    # output:
    # 1. a dict of result
    def identify_user_input(
            self, 
            user_prompt
        ):
        # initialize the chatbot at the first time of running
        if getattr(self, 'llm', None) is None:
            self.initialize_chatbot()

        # prepare the prompt
        today_date = datetime.datetime.now()
        day_of_week = today_date.strftime("%A")
        today_date = today_date.strftime('%Y-%m-%d')        

        prompt = f"""You are a professional financial advisor. Your task is to classify user input into a JSON object.
        Today: {today_date} ({day_of_week})

        Rules:
        1. investment: boolean (true if the user expresses intent to invest)
        2. investment_explanation: boolean (true if the user ask for explanation of recommendations)
        3. risk_tolerance: string (high or low or medium, null if not mentioned)
        4. investment_date: string ('yyyy-mm-dd' or 'yy-m-d' or null).
            - If no date is mentioned: null;
            - If today is mentioned: {today_date};

        Example Output Format:
        {{"investment": true, "investment_explanation": false, "risk_tolerance": null, "investment_date": null}}

        User Input: "{user_prompt}"

        Please return valid JSON only."""

        try:
            # initialize the variable
            raw_response = None
            # call the LLM
            output = self.llm(
                'User: ' + prompt + '. Assistant: ',
                max_tokens=self.max_token,
                stop=["User:"],
                echo=False,
                temperature=0,
            )
            # get the response in text
            raw_response = output.get('choices', [])
            if not raw_response:
                raise ValueError
            raw_response = raw_response[0].get('text', '')
            response = re.search('{.*}', raw_response, re.S)
            if response:
                return json.loads(response.group())
            return {"investment": False, "investment_explanation": False, "risk_tolerance": None, "investment_date": None, "error": "Invalid response", "raw_response": raw_response}
        except Exception as e:
            print('Error: ', e)
            return {"investment": False, "investment_explanation": False, "risk_tolerance": None, "investment_date": None, "error": str(e), "raw_response": raw_response}

    # classify the types of response to be generated
    # input:
    # 1. user_prompt_dict: a dict generated with identify_user_input()
    # 2. run_id_file_path: the file path of run_id CSV
    # 3. hyper_params_file_path: the file path of hyper-parameters
    # 4. gdict_file_path: the file path of the gdict file
    # output:
    # 1. chatbot_response: (str) chatbot response
    def classify_response(
        self, 
        user_prompt_dict,
        run_id_file_path = 'CSV/run_id.csv',
        hyper_params_file_path = None,
        gdict_file_path = None,
        ):
        # default: medium profile
        num_of_run = 0
        
        # determining the strategy based on the risk level
        if user_prompt_dict.get('risk_tolerance') == 'low':
            # low risk profile
            num_of_run = 2
        elif user_prompt_dict.get('risk_tolerance') == 'high':
            # high return and high risk profile
            num_of_run = 1

        # get investment date
        investment_date = None
        today_date = datetime.datetime.now()
        if user_prompt_dict.get('investment_date'):
            # check the range of the investment date
            start_date = datetime.datetime(2024, 1, 1)

            user_input_date = str(user_prompt_dict.get('investment_date'))
            user_input_date = user_input_date.split('-')
            user_input_date = datetime.datetime(
                int(user_input_date[0]), 
                int(user_input_date[1]), 
                int(user_input_date[2])
                )

            if start_date <= user_input_date and user_input_date <= today_date:
                investment_date = user_input_date.strftime('%Y-%m-%d')
            elif start_date > user_input_date:
                investment_date = start_date.strftime('%Y-%m-%d')
            else:
                investment_date = today_date.strftime('%Y-%m-%d')

        # initialize the variable response_type
        response_type = 4
        # type 1 response:
        # identify if user mentioned investment
        if user_prompt_dict.get('investment_explanation'):
            # if no date is provided, the chatbot assume 'today' to generate investment explanation
            if not user_prompt_dict.get('investment_date'):
                investment_date = today_date.strftime('%Y-%m-%d')
            # get investment portfolio with detailed explanation
            portfolio, portfolio_dict, st, gdict = self.apply_strategy(
                trading_date = investment_date,
                num_of_run = num_of_run,
                trading_fee = 0.01,
                run_id_file_path = run_id_file_path,
                hyper_params_file_path=hyper_params_file_path,
                gdict_file_path=gdict_file_path,
            )
            response_type = 1
            chatbot_response = self.generate_response(
                response_type = response_type, 
                portfolio = portfolio, 
                portfolio_dict = portfolio_dict, 
                trading_date = investment_date,
                gdict = gdict,
                risk_tolerance=user_prompt_dict.get('risk_tolerance'),
            )
        # type 2 response:
        elif user_prompt_dict.get('investment'):
            # if no date is provided, the chatbot assume 'today' to generate investment explanation
            if not user_prompt_dict.get('investment_date'):
                investment_date = today_date.strftime('%Y-%m-%d')
            # get investment portfolio
            portfolio, portfolio_dict, st, gdict = self.apply_strategy(
                trading_date = investment_date,
                num_of_run = num_of_run,
                trading_fee = 0.01,
                run_id_file_path = run_id_file_path,
                hyper_params_file_path = hyper_params_file_path,
                gdict_file_path = gdict_file_path,
            )
            response_type = 2
            chatbot_response = self.generate_response(
                response_type = response_type, 
                portfolio = portfolio, 
                portfolio_dict = portfolio_dict, 
                trading_date = investment_date,
                gdict = gdict,
                risk_tolerance=user_prompt_dict.get('risk_tolerance'),
            )
        # type 3 response:
        elif investment_date is not None:
            response_type = 3
            chatbot_response = self.generate_response(
                response_type = response_type,
                portfolio = None,
                portfolio_dict = None,
                trading_date = investment_date,
                gdict = None,
                risk_tolerance=user_prompt_dict.get('risk_tolerance'),
            )

        # type 4 response:
        # greeting and introduce the financial advisor services to the user
        else:
            response_type = 4
            chatbot_response = self.generate_response(
                response_type = response_type,
                portfolio = None,
                portfolio_dict = None,
                trading_date = None,
                gdict = None,
                risk_tolerance=user_prompt_dict.get('risk_tolerance'),
            )
            
        return chatbot_response, response_type

    # generate the response based on the classified response type
    # input:
    # 1. response_type: the type of response (e.g. about investment, or about investment explanation)
    # 2. portfolio: a list of stock symbols
    # 3. portfolio_dict: a dictionary of information of stocks in portfolio from apply_strategy()
    # 4. trading_date: the date of trading day
    # 5. gdict: gdict of the strategy
    # output:
    # 1. response in a string
    def generate_response(
            self,
            response_type=None, 
            portfolio=None, 
            portfolio_dict=None, 
            trading_date=None,
            gdict=None,
            risk_tolerance=None
            ):

        # response type 1:
        # explain the investment portfolio and strategy clearly
        if (
                response_type == 1 and 
                portfolio is not None and 
                portfolio_dict is not None and 
                trading_date is not None and 
                gdict is not None
            ):
            date = str(trading_date)
            date = date.split('-')
            date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
            day_of_week = date.strftime("%A")

            next_rebalance_date = date + datetime.timedelta(days=portfolio_dict.get('stgy').get('num_of_day_rebalance'))
            day_of_week_next_rebal = next_rebalance_date.strftime("%A")
            next_rebalance_date = next_rebalance_date.strftime('%Y-%m-%d')

            if risk_tolerance is None:
                risk_tolerance = 'medium'
            chatbot_response = f"""
            <p>
                The explanation of the investment portfolio for {trading_date} ({day_of_week}) is as follows:
            </p>
            <p>
                The risk tolerance is {risk_tolerance}.
            </p>
            <ul>
            """
            for p in portfolio:
                chatbot_response += f"""
                    <li>
                        {p}
                        <ul>
                            <li>
                                Price: {np.round(portfolio_dict.get(p).get('price'), 2)}
                            </li>               
                            <li>
                                Simple Moving Average (SMA) Short: {np.round(portfolio_dict.get(p).get('ma_short'), 2)} ({gdict.get('ma_short')} days);
                            </li>
                            <li>
                                Simple Moving Average (SMA) Long: {np.round(portfolio_dict.get(p).get('ma_long'), 2)} ({gdict.get('ma_long')} days);
                            </li>
                            <li>
                                Relative Strength Index (RSI): {np.round(portfolio_dict.get(p).get('rsi'), 2)} ({gdict.get('rsi_period')} day(s));
                            </li>
                            <li>
                                Sharpe Ratio: {np.round(portfolio_dict.get(p).get('sharpe_ratio'), 2)};
                            </li>
                            <li>
                                Annualized Return: {np.round(portfolio_dict.get(p).get('annualized_return'), 2)};
                            </li>
                            <li>
                                Annualized Volatility: {np.round(portfolio_dict.get(p).get('annualized_volatility'), 2)}.
                            </li>
                        </ul>
                    </li>
                    <br>
                """
                # Comment on SMA
                if np.round(portfolio_dict.get(p).get('ma_short'), 2) > np.round(portfolio_dict.get(p).get('ma_long'), 2):
                    chatbot_response += f'<p>The SMA Short ({np.round(portfolio_dict.get(p).get('ma_short'), 2)}) is higher than SMA Long ({np.round(portfolio_dict.get(p).get('ma_long'), 2)}). This is a signal of short-term bullish trend for the stock {p}.</p>'

                # comment on RSI
                if np.round(portfolio_dict.get(p).get('rsi'), 2) < portfolio_dict.get('stgy').get('buy_rsi'):
                    chatbot_response += f'<p>The RSI {np.round(portfolio_dict.get(p).get('rsi'), 2)} of the stock {p} is low. The price for the stock is attractive, and the stock {p} is highly recommended to put in the portfolio.</p>'
                elif np.round(portfolio_dict.get(p).get('rsi'), 2) < portfolio_dict.get('stgy').get('sell_rsi'):
                    chatbot_response += f'<p>The RSI {np.round(portfolio_dict.get(p).get('rsi'), 2)} of the stock {p} is in the normal range, neither too high nor too low.</p>'

                # comment on Sharpe ratio
                if np.round(portfolio_dict.get(p).get('sharpe_ratio'), 2) > 2:
                    chatbot_response += f'<p>The sharpe ratio {np.round(portfolio_dict.get(p).get('sharpe_ratio'), 2)} of the stock {p} is greater than 2. The stock is highly recommended.</p>'
                elif np.round(portfolio_dict.get(p).get('sharpe_ratio'), 2) > 1:
                    chatbot_response += f'<p>The sharpe ratio {np.round(portfolio_dict.get(p).get('sharpe_ratio'), 2)} of the stock {p} is greater than 1. The stock is recommended.</p>'

                # comment on annualized_return
                if np.round(portfolio_dict.get(p).get('annualized_return'), 2) > 1:
                    chatbot_response += f'<p>The high annualized return of the stock {p} made the stock be put in the portfolio. The higher the annualized return, the more profitable the stock is.</p>'

                # commnet on annualized volatility
                if np.round(portfolio_dict.get(p).get('annualized_volatility'), 2) < 0.5:
                    chatbot_response += f'<p>The annualized volatility reflects the risk of the stock. The lower the volatility, the lower the risk. {np.round(portfolio_dict.get(p).get('annualized_volatility'), 2)} is very low.</p>'
                elif np.round(portfolio_dict.get(p).get('annualized_volatility'), 2) < 1:
                    chatbot_response += f'<p>The annualized volatility reflects the risk of the stock. The lower the volatility, the lower the risk. {np.round(portfolio_dict.get(p).get('annualized_volatility'), 2)} is low.</p>'
            # investment strategy
            chatbot_response += f"""
            </ul>
                <p>
                    The investment strategy:
                </p>
                <ul>
                    <li>
                        Your capital should equally allocated to the stocks. About {1/len(portfolio) * 100}% of your capital should be allocated to each stock.
                    </li>
                    <li>
                        Stop Loss: {np.round(portfolio_dict.get('stgy').get('stop_loss'), 2) * 100}%
                    </li>
                    <li>
                        Take Profit: {np.round(portfolio_dict.get('stgy').get('take_profit'), 2) * 100}%
                    </li>
                    <li>
                        Number of days to rebalance: {portfolio_dict.get('stgy').get('num_of_day_rebalance')} day(s)
                    </li>
                    <li>
                        Relative Strength Index (RSI) is high: > {portfolio_dict.get('stgy').get('sell_rsi')}
                    </li>
                    <li>
                        Relative Strength Index (RSI) is low: < {portfolio_dict.get('stgy').get('buy_rsi')}
                    </li>
                    <li>
                        Relative Strength Index (RSI) is normal: > {portfolio_dict.get('stgy').get('buy_rsi')} and < {portfolio_dict.get('stgy').get('sell_rsi')}
                    </li>
                </ul>
                <br>
                <p>How to implement the strategy:</p>
                <ul>
                    <li>
                        Stop Loss:
                        <br>
                        The negative sign means a loss. 
                        <br>
                        You should sell the stock when the loss of the stock is more than {-np.round(portfolio_dict.get('stgy').get('stop_loss'), 2) * 100}%. 
                        <br>
                        After selling it, you should hold the cash until the next rebalance day, which is {next_rebalance_date} ({day_of_week_next_rebal}).
                    </li>
                    <li>
                        Take Profit: 
                        <br>
                        You should sell the stock when the return on the stock is more than {np.round(portfolio_dict.get('stgy').get('take_profit'), 2) * 100}%. 
                        <br>
                        After selling it, you should hold the cash until the next rebalance day, which is {next_rebalance_date} ({day_of_week_next_rebal}).
                    </li>
                    <li>
                        Number of days to rebalance: 
                        <br>
                        You should ask me the recommended investment portfolio on {next_rebalance_date} ({day_of_week_next_rebal}), because the next rebalance day is {portfolio_dict.get('stgy').get('num_of_day_rebalance')} day(s) after {trading_date} ({day_of_week}).
                        <br>
                        You are reminded to tell me your risk tolerance is {risk_tolerance} on that day, because your data is not saved in the chatbot, and your queries are annonymous.
                    </li>
                </ul>
            """

        # response type 2:
        elif (
                response_type == 2 and 
                portfolio is not None and 
                portfolio_dict is not None and 
                trading_date is not None and 
                gdict is not None
            ):
            # prepare the prompt
            date = str(trading_date)
            date = date.split('-')
            date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
            day_of_week = date.strftime("%A")

            if risk_tolerance is None:
                risk_tolerance='medium'
        
            chatbot_response = f"""
            <p>
                I recommend the following investment portfolio for {trading_date} ({day_of_week}) to you:
            </p>
            <p>
                The risk tolerance is {risk_tolerance}.
            </p>
            <ul>
            """
            for p in portfolio:
                chatbot_response += f"""
                    <li>
                        {p}
                        <ul>
                            <li>
                                Price: {np.round(portfolio_dict.get(p).get('price'), 2)}
                            </li>               
                            <li>
                                Simple Moving Average (SMA) Short: {np.round(portfolio_dict.get(p).get('ma_short'), 2)} ({gdict.get('ma_short')} days);
                            </li>
                            <li>
                                Simple Moving Average (SMA) Long: {np.round(portfolio_dict.get(p).get('ma_long'), 2)} ({gdict.get('ma_long')} days);
                            </li>
                            <li>
                                Relative Strength Index (RSI): {np.round(portfolio_dict.get(p).get('rsi'), 2)} ({gdict.get('rsi_period')} day(s));
                            </li>
                            <li>
                                Sharpe Ratio: {np.round(portfolio_dict.get(p).get('sharpe_ratio'), 2)};
                            </li>
                            <li>
                                Annualized Return: {np.round(portfolio_dict.get(p).get('annualized_return'), 2)};
                            </li>
                            <li>
                                Annualized Volatility: {np.round(portfolio_dict.get(p).get('annualized_volatility'), 2)}.
                            </li>
                        </ul>
                    </li>
                """
            chatbot_response += f"""
            </ul>
                <p>
                    The investment strategy:
                </p>
                <ul>
                    <li>
                        Your capital should equally allocated to the stocks. About {1/len(portfolio) * 100}% of your capital should be allocated to each stock.
                    </li>
                    <li>
                        Stop Loss: {np.round(portfolio_dict.get('stgy').get('stop_loss'), 2) * 100}%
                    </li>
                    <li>
                        Take Profit: {np.round(portfolio_dict.get('stgy').get('take_profit'), 2) * 100}%
                    </li>
                    <li>
                        Number of days to rebalance: {portfolio_dict.get('stgy').get('num_of_day_rebalance')} day(s)
                    </li>
                    <li>
                        Relative Strength Index (RSI) is high: > {portfolio_dict.get('stgy').get('sell_rsi')}
                    </li>
                    <li>
                        Relative Strength Index (RSI) is low: < {portfolio_dict.get('stgy').get('buy_rsi')}
                    </li>
                    <li>
                        Relative Strength Index (RSI) is normal: > {portfolio_dict.get('stgy').get('buy_rsi')} and < {portfolio_dict.get('stgy').get('sell_rsi')}
                    </li>
                </ul>
                <p>
                    You can ask for an explanation for the portfolio and strategy.
                </p>
            """
        # response type 3:
        elif (
                response_type == 3 and
                trading_date is not None
            ):
            # prepare the chatbot_response
            date = str(trading_date)
            date = date.split('-')
            date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
            day_of_week = date.strftime("%A")
        
            chatbot_response = f"""<div>
                Hello! I am your financial assistant. My goal is to build an investment portfolio for you.
                <br>
                To help me create the most suitable portfolio for your needs, please provide the following information:
                <br>
                <ul>
                    <li>
                        <b>Risk Tolerance Level:</b> Please specify if your risk tolerance is High, Low, or Medium.
                    </li>
                </ul>
                You have provided the <b>Date of Investment: {trading_date} ({day_of_week})</b> (The format of date: yyyy-mm-dd).
            </div>"""
        # response type 4:
        else:
            # prepare the chatbot_response
            chatbot_response = """<div>
                Hello! I am your financial assistant. My goal is to build an investment portfolio for you.
                <br>
                To help me create the most suitable portfolio for your needs, please provide the following information:
                <br>
                <ul>
                    <li>
                        <b>Risk Tolerance Level:</b> Please specify if your risk tolerance is High, Low, or Medium.
                    </li>
                    <li>
                        <b>Date of Investment:</b> Please provide a specific date between 2024-01-01 and today (The format of date: yyyy-mm-dd).
                    </li>
                </ul>
                <p>
                    Note: You can change your preferences any time. If no date is provided, I will assume today.
                </p>
            </div>"""

        return chatbot_response