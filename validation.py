import file_mgt
import simulation
import strategy
import numpy as np

# a classs to perform validation
class Validation:
    # input:
    # 1. val_fin_start: the start date of a financial period for validation
    # 2. val_fin_end: the end date of a financial period for validation
    # 3. run_id: the run id
    # 4. trading_fee: trading fee
    # 5. start_up_cash: start up capital
    # 6. gene_spec_filename: file path for gene specification
    # 7. elite_json_filepath: file path to store elite
    # 8. elite_csv_filepath: file path to store DNA
    # 9. validation_hyper_parameter_filename: to store the validation parameters
    # 10. is_testing: boolean (testing or validation)
    def __init__(
        self,

        # period:
        val_fin_start,
        val_fin_end,

        # other parameters
        run_id,
        trading_fee = 0.01,
        start_up_cash = 100000,

        # file path:
        ## mainly for ga
        gene_spec_filename = 'JSON/unittest_gene_spec.json',

        ## sharing from ga to validation
        elite_json_filepath = 'JSON/unittest_fittest',
        elite_csv_filepath = 'CSV/unittest_fittest',

        ## for validation
        validation_hyper_parameter_filename = 'JSON/unittest_validation_hyper_parameter.json',

        ## showing validation or testing on screen and in JSON file records
        ### Default: False
        is_testing = False
        ):

        # initialise file paths
        ## mainly for ga
        self.gene_spec_filename = gene_spec_filename

        ## sharing from ga to validation
        self.elite_json_filepath = elite_json_filepath
        self.elite_csv_filepath = elite_csv_filepath

        ## for validation
        self.validation_hyper_parameter_filename = validation_hyper_parameter_filename

        # initialise the period
        self.val_fin_start = val_fin_start
        self.val_fin_end = val_fin_end

        # initialise other parameters
        self.trading_fee = trading_fee
        self.start_up_cash = start_up_cash

        self.run_id = run_id

        self.is_testing = is_testing

    # import strategy
    # input:
    # 1. st_generation: a number of the generation of the strategy to be imported
    # 2. st_num: a number of the fittest strategy in a generation. For example, 0 means the fittest strategy, and 1 means the 2nd fittest strategy in the generation
    # output:
    # 1. an object of strategy
    # requirements during the process:
    # 1. gdict file
    # or the following:
    # 2. gene file, and
    # 3. gene spec file
    def import_strategy(
            self, 
            st_generation, 
            st_num
        ):
        fm = file_mgt.FileMgt()

        # initialise variables
        gdict = None
        spec = None
        gene = None
        
        # import gdict
        gdict_filename = self.elite_json_filepath + '/elite_gdict_gen' + str(st_generation) + '_' + str(st_num) + '.json'
        if fm.check_file_exist(filename=gdict_filename):
            gdict = fm.read_json(filename=gdict_filename)

            # check run_id
            if gdict['run_id'] != self.run_id:
                print('Warning: the <run_id> of gdict and the <run_id> for training mismatch!')

            # remove the run_id from gdict
            gdict.pop('run_id')
        else:
        # or import gene + spec, if gdict file is not found
            gene_filename = self.elite_csv_filepath + '/elite_gene_gen' + str(st_generation) + '_' + str(st_num) + '.csv'
            if fm.check_file_exist(filename=self.gene_spec_filename) and fm.check_file_exist(filename=gene_filename):
                spec = fm.read_json(self.gene_spec_filename)
                gene = fm.read_dna_list_from_csv(gene_filename)

                # check run_id of spec and gene
                if spec['run_id'] != gene[-1]:
                    # show warning to user
                    print('Warning: the <run_id> of the gene spec file and the gene file mismatch!')

                if spec['run_id'] != self.run_id:
                    # show warning
                    print('Warning: the <run_id> of gene spec and the <run_id> for training mismatch!')

                if gene[-1] != self.run_id:
                    # show warning
                    print('Warning: the <run_id> of gene and the <run_id> for training mismatch!')

                # remove run_id from gene spec and gene, after checking the run_id
                ## the removal restores data structure and data type of gene spec and gene
                spec.pop('run_id')
                gene = gene[:-1]

                # restoring the data type of DNA from CSV
                gene = [float(g) for g in gene]

            else:
                print('Error: gdict JSON file is missing.')
                print('Please provide both gene CSV and gene spec JSON files, if you don not have gdict JSON file.')
                return None

        return strategy.Strategy(
            start_up_cash=self.start_up_cash, 
            gene=gene, 
            spec=spec, 
            gdict=gdict)

    # run the simulation for validation
    # input parameters:
    # 1. st_generation: an integer indicator the generation in the training process. 
    #    For example, 0 means the 1st generation
    # 2. st_num: an integer indicator the number of the fittest in the generation. 
    #    For example, 0 means the fittest investment strategy
    # 3. validation_performance_filename:  a string of file name to store the performance record
    # output: no returned value
    # requirements to run: 
    # 1. a simulation object
    # 2. a strategy loaded from file(s)
    # changes:
    # 1. call metrics() to print & save results
    def run_validation(
        self, 
        st_generation, 
        st_num, 
        validation_performance_filename
    ):
        # create simulation environment
        sim = simulation.Simulation(
            fin_start=self.val_fin_start,
            fin_end=self.val_fin_end,
            trading_fee=self.trading_fee)

        # import strategy if strategy was None
        st = self.import_strategy(
            st_generation=st_generation,
            st_num=st_num)

        # run strategy in simulation environment
        sim.run_strategy(st)

        # print result & save it to performance JSON file
        self.metrics(
            st = st,
            validation_performance_filename = validation_performance_filename,
            st_generation=st_generation,
            st_num=st_num)

    # saving and printing the validation performance of the input strategy
    # input:
    # 1. st: strategy object
    # 2. validation_performance_filename:  a string of file name to store the performance record
    # 3. st_generation: an integer indicator the generation in the training process. For example, 0 means the 1st generation
    # 4. st_num: an integer indicator the number of the fittest in the generation. For example, 0 means the fittest investment strategy
    # output: None
    # change:
    # 1. print performance result on screen
    # 2. save the validation performance to a JSON file
    def metrics(
            self, 
            st, 
            validation_performance_filename, 
            st_generation, 
            st_num
        ):

        showing_task = 'validation'
        if self.is_testing:
            showing_task = 'testing'

        # prepare the information to be saved to JSON file
        validation_performance_log = {
            str(showing_task)+"_reward": np.round(float(st.rewards), 3),
            str(showing_task)+"_fin_start": self.val_fin_start,
            str(showing_task)+"_fin_end": self.val_fin_end,
            str(showing_task)+"_return": np.round(float(st.cumulative_return), 3),
            str(showing_task)+"_total_value": np.round(float(st.total_value), 3),
            str(showing_task)+"_max_drawdown": np.round(float(st.max_drawdown), 3),
            str(showing_task)+"_win_rate": float(np.round((st.num_of_increase_in_value / st.age), 3)),
            str(showing_task)+"_sharpe_ratio": float(np.round(st.sharpe_ratio, 3)),
            str(showing_task)+"_gdict": st.gdict,
            "strategy_generation": st_generation,
            "strategy_num": st_num,
            "run_id": self.run_id,
            str(showing_task)+"_portfolio_sequence": st.portfolio_sequence,
            str(showing_task)+"_total_value_sequence": st.total_value_sequence,
        }

        fm = file_mgt.FileMgt()
        # write performance to JSON
        fm.write_to_json(to_json_content=validation_performance_log, 
                         filename=validation_performance_filename)
        
        # print the performance
        print('\n', '-' * 10, ' ' * 5, ' ' + str(showing_task) + ' - generation: ', st_generation, ', fittest: ', st_num, ' ' * 5, '-' * 10)
        print(
            str(showing_task)+'_fin_start: ', self.val_fin_start,
            ', ' + str(showing_task) + '_fin_end: ', self.val_fin_end,
            ', ' + str(showing_task) + '_reward: ', np.round(float(st.rewards), 3),
            ', ' + str(showing_task) + '_return: ', np.round(float(st.cumulative_return), 3),
            ', ' + str(showing_task) + '_total_value: ', np.round(float(st.total_value),3),
            ', ' + str(showing_task) + '_max_drawdown: ', np.round(float(st.max_drawdown),3),
            ', ' + str(showing_task) + '_win_rate: ', float(np.round((st.num_of_increase_in_value / st.age), 3)),
            ', ' + str(showing_task) + '_sharpe_ratio: ', float(np.round(st.sharpe_ratio, 3)),
            )

        # saving the hyper-parameters of the validation
        validation_hyper_parameter = {
            "run_id": self.run_id,

            str(showing_task)+"_fin_start": self.val_fin_start,
            str(showing_task)+"_fin_end": self.val_fin_end,

            "start_up_cash": self.start_up_cash,
            "trading_fee": self.trading_fee,
        }

        # saving the hyper-parameters to JSON
        fm.write_to_json(
            to_json_content=validation_hyper_parameter, 
            filename=self.validation_hyper_parameter_filename
        )
