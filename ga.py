import genome
import os
import json
import numpy as np
import population
import simulation
import strategy
import copy
import file_mgt
import api_fin_data
from chatbot import Chatbot
from inputimeout import inputimeout, TimeoutOccurred

class GA:
    '''
    # the parameters of the GA, and their default values
        def __init__(self,
                    cr_start_pos,
                    cr_start_ori,
                    pool_size,
                    pop_size=200, 
                    gene_count=3,
                    min_gene=1,
                    cr_lifetime=2400, 
                    num_of_generations=1000, 
                    point_mutate_rate=0.1, 
                    point_mutate_amt=0.25,
                    shrink_mutate_rate=0.25, 
                    grow_mutate_rate=0.1, 
                    is_grow_legs_only=False, 
                    max_gene_to_grow=300,
                    is_handcrafted_urdf=False):
            # user input pool size
            self.pool_size=pool_size
            self.pop_size=pop_size
            # make sure the gene_count is at least 4 for the 4 wheels of the handcrafted robot
            if gene_count < min_gene:
                self.gene_count=min_gene
            else:
                self.gene_count=gene_count
            self.min_gene=min_gene
            self.JSON_filename='JSON/genome_spec.json'
            self.log_filename='JSON/log_ga.json'
            # the lifetime of creature(s) in number of frames
            self.cr_lifetime=cr_lifetime
            # the number of generations
            self.num_of_generations=num_of_generations
            self.point_mutate_rate=point_mutate_rate
            self.point_mutate_amt=point_mutate_amt
            self.shrink_mutate_rate=shrink_mutate_rate
            self.grow_mutate_rate=grow_mutate_rate
            self.is_grow_legs_only=is_grow_legs_only
            self.max_gene_to_grow=max_gene_to_grow
            self.cr_start_pos=cr_start_pos
            self.cr_start_ori=cr_start_ori
            self.is_handcrafted_urdf=is_handcrafted_urdf

            # save the parameters to JSON
            to_json_content = {
                'cr_start_pos': self.cr_start_pos,
                'cr_start_ori': self.cr_start_ori,
                'pop_size': self.pop_size,
                'gene_count': self.gene_count,
                'cr_lifetime': self.cr_lifetime,
                'num_of_generations': self.cr_lifetime,
                'point_mutate_rate': self.point_mutate_rate,
                'point_mutate_amt': self.point_mutate_amt,
                'shrink_mutate_rate': self.shrink_mutate_rate,
                'grow_mutate_rate': self.grow_mutate_rate,
                'is_grow_legs_only': self.is_grow_legs_only,
                'max_gene_to_grow': self.max_gene_to_grow,
                "is_handcrafted_urdf": self.is_handcrafted_urdf,
            }
            genome.Genome.to_json(to_json_content, 'JSON/config.json')

            # save the genome spec to JSON
            genome.Genome.to_json(genome.Genome.get_gene_spec(), self.JSON_filename)

            # remove the old log file
            if os.path.exists(self.log_filename):
                os.remove(self.log_filename)

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # initialise the parameters of the GA, and their default values
    # input:
    # 1. pool size: the number of threads
    # 2. start_up_cash: the start up capital
    # 3. trading_fee: trading fee
    # 4. fin_start: the start date of the financial period
    # 5. fin_end: the end date of the financial period
    # 6. run_id: run id for the running round
    # 7. pop_size: the population size
    # 8. num_of_generations: total number of generations
    # 9. point_mutate_rate: the chance to trigger point mutation
    # 10. point_mutate_amt: the amount to mutate
    # 11. gene_spec_filename: gene specification file path
    # 12. ga_performance_filename: file path to store ga performance
    # 13. hyper_parameter_filename: file path to store hyper-parameters
    # 14. run_id_filename: file path to store run id
    # 15. elite_json_filepath: file path to store gdict and performance of the elite
    # 16. elite_csv_filepath: file path to store DNA
    # 17. num_of_elite: number of elites to be selected in each generation
    # 18. is_import_previous_strategy: boolean, true to select elite in previous run
    def __init__(
        self,
        pool_size,
        start_up_cash,
        trading_fee,
        fin_start,
        fin_end,
        run_id = str(0),
        pop_size = 50,
        num_of_generations = 50,
        point_mutate_rate = 0.1, 
        point_mutate_amt = 0.25,

        # file path:
        ## mainly for ga
        gene_spec_filename = 'JSON/unittest_gene_spec.json',
        ga_performance_filename = 'JSON/unittest_ga_performance.json',
        hyper_parameter_filename = 'JSON/unittest_hyper_parameter.json',
        run_id_filename = 'CSV/run_id.csv',

        ## sharing from ga to validation
        elite_json_filepath = 'JSON/unittest_fittest',
        elite_csv_filepath = 'CSV/unittest_fittest',
        
        num_of_elite = 1,

        is_import_previous_strategy = False,
    ):
        self.pool_size = pool_size
        self.fin_start = fin_start
        self.fin_end = fin_end
        self.start_up_cash = start_up_cash
        self.trading_fee = trading_fee
        # pop size should be larger than no. of elites to be selected, when no. of generations is larger than 1.
        # Otherwise, the results from 2nd generations will be the same as the 1st generation
        if pop_size <= num_of_elite and num_of_generations > 1:
            self.pop_size = num_of_elite + 1
        else:
            self.pop_size = pop_size

        self.gene_spec_filename = gene_spec_filename
        self.ga_performance_filename = ga_performance_filename
        self.hyper_parameter_filename = hyper_parameter_filename
        self.run_id_filename = run_id_filename

        self.elite_json_filepath = elite_json_filepath
        self.elite_csv_filepath = elite_csv_filepath

        # the number of generations
        self.num_of_generations = num_of_generations
        self.point_mutate_rate = point_mutate_rate
        self.point_mutate_amt = point_mutate_amt

        # number of fittest strategies to be selected to the next generation
        ## e.g. 3 means the 3 fittest strategies of the current and previous generations will be saved 
        ### to JSON file(s), 
        ### to CSV file(s), and
        ### to next generation
        self.num_of_elite = num_of_elite

        # run id
        ## to identify the files generated this time
        self.run_id = str(run_id)
        self.run_id = self.run_id.strip()

        # initialise ga performance file content
        # preparing the JSON log file at the beginning
        self.ga_performance_file_content = '{"run_id": "' + str(self.run_id) + '",\n "result":[\n'

        # initialize the api and file management
        self.my_api = api_fin_data.APIFinData()
        self.fm = file_mgt.FileMgt()

        self.is_import_previous_strategy = is_import_previous_strategy

    # initialise the running of ga
    ## the initialisation process that the developer does not want it to run when creating the ga instances, but run at the start of ga process
    # cleaning the old logs and record in JSON folder, and the old elite CSV files
    # saving the hyper-parameters, gene spec to JSON files
    # input: None
    # output: no returned value
    # changes:
    # 1. save hyper-parameter to JSON
    # 2. save gene spec to JSON
    def initialise_logs(self):
        # check if file path exists for saving JSON and CSV
        if not self.fm.check_file_exist(self.elite_csv_filepath):
            os.mkdir(self.elite_csv_filepath)

        if not self.fm.check_file_exist(self.elite_json_filepath):
            os.mkdir(self.elite_json_filepath)

        # save the hyper-parameters to JSON
        save_hyper_parameter_to_json_content = {
            'run_id': self.run_id,
            'pop_size': self.pop_size,
            'num_of_generations': self.num_of_generations,
            'num_of_elite': self.num_of_elite,
            'point_mutate_rate': self.point_mutate_rate,
            'point_mutate_amt': self.point_mutate_amt,
            'start_up_cash': self.start_up_cash,
            'fin_start': self.fin_start,
            'fin_end': self.fin_end,
            'trading_fee': self.trading_fee,
            'pool_size': self.pool_size,
            'gene_spec_filename': self.gene_spec_filename,
            'ga_performance_filename': self.ga_performance_filename,
            'hyper_parameter_filename': self.hyper_parameter_filename,
            'elite_csv_filepath': self.elite_csv_filepath,
            'elite_json_filepath': self.elite_json_filepath,
        }
        self.fm.write_to_json(
            to_json_content=save_hyper_parameter_to_json_content, 
            filename=self.hyper_parameter_filename)

        # save the genome spec to JSON
        gene_spec = genome.Genome.get_gene_spec()
        gene_spec['run_id'] = str(self.run_id)
        self.fm.write_to_json(
            to_json_content=gene_spec, 
            filename=self.gene_spec_filename)

    '''
    # calculating and printing the metrics
    def metrics(self, pop, generation):
        # the performance of creatures
        max_closeness = []
        links = []
        distance_travelled = []
        total_movement = []
        rewards = []
        for cr in pop.creatures:
            max_closeness.append(cr.get_max_closeness())
            links.append(len(cr.get_expanded_links()))
            distance_travelled.append(cr.get_distance_travelled())
            total_movement.append(cr.get_total_movement())
            rewards.append(cr.get_reward())

        # for the fittest creature
        fittest_reward = np.max(rewards)
        for cr in pop.creatures:
            if cr.get_reward() == fittest_reward:
                # get the max closeness of the fittest creature
                fittest_closeness = cr.get_max_closeness()
                fittest_links = len(cr.get_expanded_links())
                fittest_travelled = cr.get_distance_travelled()
                fittest_total_movement = cr.get_total_movement()
                break

        # prepare the information to be printed and returned
        log = {
            # the shortest distance of max closeness among creatures
            'max_closeness': str(np.round(np.min(max_closeness), 3)),
            # the mean distance of max closeness among creatures
            'mean_closeness': str(np.round(np.mean(max_closeness), 3)),
            # the longest distance of max closeness among creatures
            'min_closeness':str(np.round(np.max(max_closeness), 3)), 
            'mean_links':str(np.round(np.mean(links))),
            'max_links':str(np.round(np.max(links))),
            'min_links':str(np.round(np.min(links))),
            'pop_size':str(len(pop.creatures)),
            'max_dist_travelled':str(np.round(np.max(distance_travelled), 3)),
            'min_dist_travelled':str(np.round(np.min(distance_travelled), 3)),
            'max_total_movement':str(np.round(np.max(total_movement), 3)),
            'min_total_movement':str(np.round(np.min(total_movement), 3)),
            'max_reward':str(np.round(np.max(rewards), 3)),
            'min_reward':str(np.round(np.min(rewards), 3)),
            # the max closeness of the fittest creature (the creature with highest reward)
            'fittest_closeness':str(np.round(fittest_closeness, 3)),
            'fittest_links':str(np.round(fittest_links, 3)),
            'fittest_travelled':str(np.round(fittest_travelled, 3)),
            'fittest_total_movement':str(np.round(fittest_total_movement, 3)),
        }

        print(generation,
            "max closeness:", log['max_closeness'], 
            ", mean:", log['mean_closeness'], 
            ", mean links:", log['mean_links'], 
            ", max links:", log['max_links'],
            ", pop size:", log['pop_size'],
            ", dist travelled (max):", log['max_dist_travelled'],
            ", (min):", log['min_dist_travelled'],
            ", total dist (max):", log['max_total_movement'],
            ", (min):", log['min_total_movement'],
            ", reward (max):", log['max_reward'],
            ", (min):", log['min_reward'],
            ", fittest closeness:", np.round(fittest_closeness, 3))
        
        # saving the above information to csv log file
        with open(self.log_filename, "a") as f:
            f.write(json.dumps(log))
            f.write(',\n')
            
        return rewards
    
    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # calculating and printing the metrics
    # input:
    # 1. generation: number of generations. 1 stands for the first generation
    # 2. top_n_strategies: a list of the <self.num_of_elite> fittest strategies. This is the output of elitism()
    # 3. the list of rewards of all strategies in a generation
    # output: no returned value
    # change:
    # 1. add performance metrics to <ga_performance_file_content> JSON
    # 2. print the metrics and performance
    def metrics(
            self, 
            generation, 
            top_n_strategies, 
            all_rewards
        ):
        # prepare the information to be logged to file
        log = {
            "generation": str(generation),
            "max_reward": str(float(np.round(np.max(all_rewards), 3))),
            "min_reward": str(float(np.round(np.min(all_rewards), 3))),
            # the highest reward strategy
            "fittest_gdict": top_n_strategies[-1].gdict,
            "fin_start": self.fin_start,
            "fin_end": self.fin_end,
            "fittest_rewards_0": float(np.round(top_n_strategies[-1].rewards, 3)),
            "fittest_return_0": float(np.round(top_n_strategies[-1].cumulative_return, 3)),
            "fittest_value_0": float(np.round(top_n_strategies[-1].total_value, 3)),
            "fittest_max_drawdown_0": float(np.round(top_n_strategies[-1].max_drawdown, 3)),
            "fittest_win_rate_0": float(np.round((top_n_strategies[-1].num_of_increase_in_value / 
                                                  top_n_strategies[-1].age), 3)),
            "fittest_sharpe_ratio": float(np.round(top_n_strategies[-1].sharpe_ratio, 3)),
        }

        # print the performance
        print('\n', '-' * 20, ' ' * 3, ' Training - Generation:', generation, ' ' * 3, '-' * 20)
        print(
            str(generation), 
            'max_reward:', float(np.round(np.max(all_rewards), 3)), 
            ', min_reward:', float(np.round(np.min(all_rewards), 3)),
            ', pop_size:', self.pop_size,
            ', fin_start:', self.fin_start,
            ', fin_end:', self.fin_end,
        )
        print('\n', '-' * 20, ' ' * 3, ' Training - Generation:', generation, ', fittest: 0', ' ' * 3, '-' * 20)
        print(
            'fittest_rewards_0:', float(np.round(top_n_strategies[-1].rewards, 3)),
            ', fittest_return_0:', float(np.round(top_n_strategies[-1].cumulative_return, 3)), 
            ', fittest_value_0:', float(np.round(top_n_strategies[-1].total_value, 3)),
            ', fittest_max_drawdown_0:', float(np.round(top_n_strategies[-1].max_drawdown, 3)),
            ', fittest_win_rate_0:', float(np.round(top_n_strategies[-1].num_of_increase_in_value / 
                                                  top_n_strategies[-1].age, 3)),
            ', fittest_sharpe_rate_0:', float(np.round(top_n_strategies[-1].sharpe_ratio, 3)),
            )

        # record all top n fittest strategies to JSON performance file, and print
        counter = 2
        while counter <= len(top_n_strategies):
            print('\n', '-' * 20, ' ' * 3, ' Training - Generation:', generation, ', fittest: ', counter - 1, ' ' * 3, '-' * 20)
            log['fittest_rewards_' + str(counter - 1)] = float(np.round(top_n_strategies[-counter].rewards, 3))
            log['fittest_return_' + str(counter - 1)] = float(np.round(top_n_strategies[-counter].cumulative_return, 3))
            log['fittest_value_' + str(counter - 1)] = float(np.round(top_n_strategies[-counter].total_value, 3))
            log['fittest_max_drawdown_' + str(counter - 1)] = float(np.round(top_n_strategies[-counter].max_drawdown, 3))
            log['fittest_win_rate_' + str(counter - 1)] = float(
                np.round((top_n_strategies[-counter].num_of_increase_in_value / 
                          top_n_strategies[-counter].age), 3))
            log['fittest_sharpe_ratio_' + str(counter - 1)] = float(np.round(top_n_strategies[-counter].sharpe_ratio, 3))

            print(
                'fittest_rewards_' + str(counter - 1) + ':', 
                float(np.round(top_n_strategies[-counter].rewards, 3)),
                ', fittest_return_' + str(counter - 1) + ':', 
                float(np.round(top_n_strategies[-counter].cumulative_return, 3)),
                ', fittest_value_' + str(counter - 1) + ':', 
                float(np.round(top_n_strategies[-counter].total_value, 3)),
                ', fittest_max_drawdown_' + str(counter - 1) + ':', 
                float(np.round(top_n_strategies[-counter].max_drawdown, 3)),
                ', fittest_win_rate_' + str(counter - 1) + ':', 
                float(np.round((top_n_strategies[-counter].num_of_increase_in_value / 
                                top_n_strategies[-counter].age), 3)),
                ', fittest_sharpe_ratio_' + str(counter - 1) + ':', 
                float(np.round(top_n_strategies[-counter].sharpe_ratio, 3)),
                )

            counter += 1

        # saving the above information to JSON file
        self.ga_performance_file_content += json.dumps(log) + ',\n'

    '''
    # passing the fittest creature on to the next generation
    @staticmethod
    def elitism(reward, pop, new_creatures, generation):
        # elitism
        best_fit_reward = np.max(reward)
        for c_in_pop in pop.creatures:
            if c_in_pop.get_reward() == best_fit_reward:
                # deepcopy to copy the fittest creature
                fittest = copy.deepcopy(c_in_pop)
                # Reset all parameters, but leaving the DNA unchanged
                fittest.reset()
                # I appended the fittest creature to new_creatures, instead of assign it to the first element of new_creatures. This can keep both the fittest creature and all newly breeded creatures for the next generation
                new_creatures.append(fittest)

                # saving the fittest to CSV file
                filename = "CSV/elite_"+str(generation)+".csv"
                genome.Genome.to_csv(c_in_pop.dna, filename)
                # stop iteration after the fittest was found
                break
        return new_creatures

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # saving the <self.num_of_elite> fittest strategies to CSV and JSON files, and return
    # input:
    # 1. pop: the population instances of current generation
    # 2. genereation: the generation number, such as 1 stands for the first generation
    # output: 
    # 1. top_n_st: a list of the instances of the <self.num_of_elite> fittest strategies
    #    top_n_st is in descending order of the rewards of the strategy
    # 2. rewards: a list of rewards of the strategies in the population of current generation
    # change:
    # 1. JSON file(s) storing gdict of the <self.num_of_elite> fittest
    # 2. CSV file(s) storing the genome of the <self.num_of_elite> fittest
    def elitism(
            self, 
            pop, 
            generation
        ):
        # the performance of strategies in current generation
        all_rewards = [st.rewards for st in pop.strategies]

        np_rewards = np.array(copy.deepcopy(all_rewards))
        np_st = np.array(copy.deepcopy(pop.strategies))

        # sorting the strategy array in descending order of the strategy rewards
        top_n_st = np_st[np.argsort(a=np_rewards)[-self.num_of_elite:]]
        top_n_st = top_n_st.tolist()

        # saving the fittest to files
        counter = len(top_n_st)
        while counter > 0:
            # saving the fittest DNA to CSV file
            dna_filename = self.elite_csv_filepath + '/elite_gene_gen' + str(generation) + '_' + str(counter - 1) + '.csv'
            gene=copy.deepcopy(top_n_st[-counter].gene)
            gene=np.append(gene, self.run_id)
            self.fm.write_dna_to_csv(list_content=gene, csv_file_path=dna_filename)

            # saving the fittest gdict to JSON file
            gdict_filename = self.elite_json_filepath + '/elite_gdict_gen' + str(generation) + '_' + str(counter - 1) + '.json'
            gdict=copy.deepcopy(top_n_st[-counter].gdict)
            gdict['run_id'] = self.run_id
            gdict['training_rewards'] = top_n_st[-counter].rewards
            gdict['fin_start'] = self.fin_start
            gdict['fin_end'] = self.fin_end
            # although gdict should not include the following, they were added for saving to JSON only.
            # If they were saved to 'ga_performance.json', the file would be very long.
            ## the following are not gdict items:
            gdict['portfolio_sequence'] = top_n_st[-counter].portfolio_sequence
            gdict['total_value_sequence'] = top_n_st[-counter].total_value_sequence
            self.fm.write_to_json(to_json_content=gdict, filename=gdict_filename)

            counter -= 1

        return top_n_st, all_rewards

    # check any available previous elite strategy
    # ask for importing the previous elite, if found
    # input:
    # 1. run_id_filename: file path of file of run id
    # output:
    # 1. st: the elite strategy
    def import_elite_from_previous_run(
            self, 
            run_id_filename = 'CSV/run_id.csv'
        ):
        # check for any old elite
        if not self.fm.check_file_exist(run_id_filename):
            return None

        run_id_record = self.fm.read_from_csv(run_id_filename)

        if run_id_record is None or len(run_id_record) < 1:
            return None

        if len(run_id_record) == 1 and run_id_record[0].strip() == self.run_id.strip():
            # if only 1 run_id was found, the run_id is the current run_id
            return None
        
        if len(run_id_record) > 2:
            for id in range(len(run_id_record)):
                if run_id_record[id] != self.run_id:
                    print('id: ', id, ', run_id: ', run_id_record[id].strip())
            try:
                # wait 60 seconds for the user to enter which strategy to import
                print('You can type "Enter" to skip this step.')
                user_input = inputimeout(prompt='Enter the <id> or <run_id> to import the previous strategy: (<id>, <run_id> or Nothing to import) \n(60 seconds) >>\n', timeout=60)
            except TimeoutOccurred:
                print('Time is up. No strategy is imported')
                return None
            if user_input in range(len(run_id_record)):
                import_run_id = run_id_record[user_input]
            elif user_input in run_id_record:
                for run in run_id_record:
                    if user_input == run:
                        import_run_id = run
                        break
            else:
                print('Invalid id or strategy. No elite strategy is imported.\n')
                return None
        elif run_id_record[0].strip() is not None and run_id_record[0].strip() != self.run_id.strip():
            import_run_id = run_id_record[0]
        else:
            # Elite strategy not found
            return None

        # import strategy
        st, gdict = Chatbot.get_strategy(
            run_id=import_run_id.strip()
        )
        if st:
            print('The elite from: ', import_run_id.strip(), ' was imported.\n')
            return st
        print('No elite strategy is imported.\n')
        return None

    '''
    # the main body and workflow of GA
    def run_ga(self):
        # checking user input: pool size
        if self.pool_size is None or type(self.pool_size) is not int:
            # prompt users to input number of thread(s)
            self.user_input()

        pop = population.Population(pop_size=self.pop_size, 
                                    gene_count=self.gene_count)

        # determine the number of threads based on user input
        if self.pool_size > 1:
            sim = simulation.ThreadedSim(pool_size=self.pool_size, cr_start_pos=self.cr_start_pos, cr_start_ori=self.cr_start_ori, is_handcrafted_urdf=self.is_handcrafted_urdf)
            print('Multi-threads:', self.pool_size)
        else:
            sim = simulation.Simulation(cr_start_pos=self.cr_start_pos, cr_start_ori=self.cr_start_ori, is_handcrafted_urdf=self.is_handcrafted_urdf)
            print('Single thread')

        # preparing the JSON log file at the beginning
        with open(self.log_filename, "w") as f:
            f.write('{"result":[')

        for generation in range(self.num_of_generations):
            if self.pool_size > 1:
                # multi-threads version
                sim.eval_population(pop, self.cr_lifetime)
            else:
                # single-thread version 
                # where we just call run_creature instead
                # of eval_population
                for cr in pop.creatures:
                    sim.run_creature(cr=cr, cr_lifetime=self.cr_lifetime)

            rewards = self.metrics(pop=pop, generation=generation)

            fit_map = population.Population.get_fitness_map(reward=rewards)
            new_creatures = []
            # I changed the number of newly breeded creatures to existing number minus 1, because the current fittest creature will be appended. The population size remains unchanged.
            # breeding new creatures
            for i in range(len(pop.creatures) - 1):
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                # now we have the parents!

                dna = genome.Genome.crossover(g1=p1.dna, g2=p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=self.point_mutate_rate, amount=self.point_mutate_amt)
                dna = genome.Genome.shrink_mutate(dna, rate=self.shrink_mutate_rate)
                # The if-statement here was added after the experiments to fix the bug of the failed sim because of too many links
                # limit the number of links to grow
                if len(p1.get_expanded_links()) <= self.max_gene_to_grow and len(p2.get_expanded_links()) <= self.max_gene_to_grow:
                    # I added the parameter 'max_gene' to grow_mutate(). Genome will not grow, once the max number of genes has been reached.
                    while True:
                        # keep growing, until the number of genes reaches the minimum number
                        ## avoid error(s) for handcrafted robot(s)
                        if len(dna) >= self.min_gene:
                            break
                        dna = genome.Genome.grow_mutate(dna, rate=1.0, max_gene_to_grow=self.max_gene_to_grow)
                    dna = genome.Genome.grow_mutate(dna, rate=self.grow_mutate_rate, max_gene_to_grow=self.max_gene_to_grow)
                new_cr = creature.Creature(gene_count=self.gene_count, dna=dna, is_grow_legs_only = self.is_grow_legs_only)
                new_creatures.append(new_cr)
                # I added the assertion to assert at least 1 creature in new_creatures
                assert len(new_creatures) >= 1
            
            # elitism
            new_creatures = self.elitism(reward=rewards, pop=pop, new_creatures=new_creatures, generation=generation)
            # Assigning the new creatures and the fittest to the population for the next generation
            pop.creatures = new_creatures

        # closing the JSON log file at the end
        with open(self.log_filename, "a") as f:
            f.write(']}')

    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project.
    
    The code of the mid-term coursework was written with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # the main body and workflow of GA
    # input: None
    # Output: No returned value
    # Changes:
    # 1. write the log of strategy performance to self.ga_performance_filename
    # 2. run simulation
    # 3. call fitmap
    # 4. breed new strategies
    def run_ga(self):
        # initialise the running
        ## the initialisation process that the developer does not want it to run when creating the ga instances, but run at the start of ga process
        self.initialise_logs()

        # import previous strategy
        if self.is_import_previous_strategy:
            imported_st = self.import_elite_from_previous_run(
                run_id_filename = self.run_id_filename
            )
            pop = population.Population(
                pop_size=self.pop_size, 
                start_up_cash=self.start_up_cash,
                st=imported_st,
                )
        else:
            pop = population.Population(
                pop_size=self.pop_size, 
                start_up_cash=self.start_up_cash
                )

        # determine the number of threads based on user input
        if self.pool_size > 1:
            sim_t = simulation.ThreadedSim(
                pool_size=self.pool_size, 
                fin_start=self.fin_start,
                fin_end=self.fin_end,
                trading_fee=self.trading_fee)
            print('Multi-threads:', self.pool_size)

            # initialise the financial data for multi-threads environment
            symbols = self.my_api.get_symbol_from_csv(trading_date=self.fin_start)

            # pre-downloading any missing financial data for the running of simulations
            ## this helps prevent the error(s) of concurrent downloading of financial data in multi-threads environment
            for s in symbols:
                self.my_api.get_financial_data(symbol=s, period_end=self.fin_end)
        else:
            sim = simulation.Simulation(
                fin_start=self.fin_start,
                fin_end=self.fin_end,
                trading_fee=self.trading_fee)
            print('Single thread')

        for generation in range(self.num_of_generations):
            if self.pool_size > 1:
                # multi-threads version
                sim_t.eval_population(pop=pop)
            else:
                # single-thread version 
                for st in pop.strategies:
                    sim.run_strategy(st=st)

            # elitism
            ## finds the <self.num_of_elite> fittest
            top_n_strategies, all_rewards = self.elitism(
                pop=pop, 
                generation=generation)

            # calculating, logging and printing metrics of the fittest strategy
            ## it must be called after the elitism, because the self.elitism finds the fittest from current and previous generations
            self.metrics(
                generation=generation, 
                top_n_strategies=top_n_strategies, 
                all_rewards=all_rewards
                )

            # getting the fitmap for breeding
            fit_map = population.Population.get_fitness_map(reward=all_rewards)

            # the number of newly breeded strategies is the existing number of strategies minus <len(top_n_strategies)>, because the <len(top_n_strategies)> fittest strategies will be added to the population. The population size remains unchanged.
            # breeding new strategies
            new_strategies = []
            for i in range(len(pop.strategies) - len(top_n_strategies)):
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.strategies[p1_ind]
                p2 = pop.strategies[p2_ind]

                dna = genome.Genome.crossover(g1=p1.gene, g2=p2.gene)
                dna = genome.Genome.point_mutate(dna, rate=self.point_mutate_rate, amount=self.point_mutate_amt)
                new_st = strategy.Strategy(start_up_cash=self.start_up_cash, gene=dna)

                new_strategies.append(new_st)

            # adding the top n fittest strategies to the population for the next generation
            for st in top_n_strategies:
                st.reset(start_up_cash=self.start_up_cash)
                new_strategies.append(st)

            # Assigning the new strategies to the population for the next generation
            pop.strategies = new_strategies

        # close the ga performance JSON file
        self.close_ga_performance_file()

    # closing the JSON file of the ga performance
    # input: None
    # output: None
    # change: saving content to the JSON file of ga performance, and closing it
    def close_ga_performance_file(self):
        # saving log content to the JSON log file at the end
        self.ga_performance_file_content = self.ga_performance_file_content[:-2]
        self.ga_performance_file_content += '\n]}'
        with open(self.ga_performance_filename, "w") as f:
            f.write(self.ga_performance_file_content)


