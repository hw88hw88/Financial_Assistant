
'''
        import ga
        import sys

        # start running the genetic algorithm here to start selecting the fittest creatures
        # input: 
        ## 1. number of threads of the running environment
        # output: printing some metrics of the creatures for each generation
        try:
                assert len(sys.argv) == 2, "Usage: python run_ga_find_fittest.py [number of threads] \n For example (2 threads): python run_ga_find_fittest.py 2"

                # change the parameters here, if needed
                g = ga.GA(
                        cr_start_pos=[6, 6, 10],
                        cr_start_ori=[0, 0, 0, 1],
                        pool_size = sys.argv[1], 
                        pop_size=100,
                        gene_count=3,
                        min_gene=1,
                        # if is_handcrafted_urdf = True, gene_count >= 6 for:
                        ## 1. the root link, 
                        ## 2. the top link and 
                        ## 3. the 4 wheels
                        is_handcrafted_urdf=False,
                        cr_lifetime=2400, 
                        num_of_generations=200,
                        point_mutate_rate=0.1, 
                        point_mutate_amt=0.25, 
                        shrink_mutate_rate=0.25, 
                        grow_mutate_rate=0.1,
                        is_grow_legs_only=False,
                        max_gene_to_grow=100)
                # run the genetic algorithm
                g.run_ga()

        except Exception as e:
        print(e)

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

''' 
        The running environment:
        Host OS: WSL2.0 on Windows 11
        Guest OS: Ubuntu 24.04

        Python 3.12.3

'''
# run the training of GA and validation
try:
        import ga
        import validation
        import sys
        import datetime
        import os
        import file_mgt

        # initialise variable(s)
        run_id = str(datetime.datetime.now())
        run_id = run_id.replace(' ', '_')
        run_id = run_id.replace(':', '-')
        run_id = 'run_id' + str(run_id)

        fm = file_mgt.FileMgt()

        ## training with data in the period
        fin_start = '2023-01-01'
        fin_end = '2023-12-31'

        ## validation with data in the period
        val_fin_start = '2024-01-01'
        val_fin_end = '2024-12-31'

        ## import previous strategy or not
        ### set to True to import generated strategy
        ### useful to test the strategy across period, such as walk-forward test
        # the fittest strategy of the last generation of the run would be imported
        is_import_previous_strategy = False

        trading_fee = 0.01
        start_up_cash = 100000

        num_of_generations = 50
        num_of_elite = 1
        pop_size = 50
        point_mutate_rate = 0.1
        point_mutate_amt = 0.2

        # initialise file paths
        json_parent_path = 'JSON/'
        csv_parent_path = 'CSV/'

        json_file_path = json_parent_path + run_id
        csv_file_path = csv_parent_path + run_id

        gene_spec_filename = json_file_path + '/gene_spec.json'
        ga_performance_filename = json_file_path + '/ga_performance.json'
        hyper_parameter_filename = json_file_path + '/hyper_parameter.json'
        elite_json_filepath = json_file_path + '/fittest'
        elite_csv_filepath = csv_file_path + '/fittest'
        validation_filepath = json_file_path + '/validation'

        # create folder(s) for saving the JSON and CSV files
        if not fm.check_file_exist(json_parent_path):
                os.mkdir(json_parent_path)

        if not fm.check_file_exist(csv_parent_path):
                os.mkdir(csv_parent_path)

        if not fm.check_file_exist(json_file_path):
                os.mkdir(json_file_path)

        if not fm.check_file_exist(elite_json_filepath):
                os.mkdir(elite_json_filepath)

        if not fm.check_file_exist(csv_file_path):
                os.mkdir(csv_file_path)

        if not fm.check_file_exist(elite_csv_filepath):
                os.mkdir(elite_csv_filepath)

        if not fm.check_file_exist(validation_filepath):
                os.mkdir(validation_filepath)

        ## saving run_id to CSV file
        with open (csv_parent_path + '/run_id.csv', 'a') as f:
                f.write(run_id + ',')

        validation_performance_filename = json_file_path + '/validation_performance.json'
        validation_hyper_parameter_filename = json_file_path + '/validation_hyper_parameter.json'

        # start running the genetic algorithm here to start selecting the fittest creatures
        # input: 
        # 1. number of threads of the running environment
        # output: 
        # 1. printing some metrics of the creatures for each generation
        # 2. saving the results, metrics, performance etc. to CSV and JSON files
        if len(sys.argv) == 2 and type(int(sys.argv[1])) is int:
                pool_size = sys.argv[1]
        else:
                pool_size = 1
                print("Usage: python run_ga_find_fittest.py [number of threads] \n For example (2 threads): python run_ga_find_fittest.py 2")

        g = ga.GA(
                pool_size = int(pool_size),
                # pop_size should be larger than num_of_elite
                pop_size = pop_size,
                num_of_generations = num_of_generations,
                point_mutate_rate = point_mutate_rate, 
                point_mutate_amt = point_mutate_amt,

                fin_start = fin_start,
                fin_end = fin_end,

                start_up_cash = start_up_cash,
                # trading fee includes commission fee, trading platform fee, and other fee for each transaction of stocks
                # trading fee is per order fee (e.g. 0.01 means US$0.01 per share in the order)
                trading_fee = trading_fee,

                num_of_elite = num_of_elite,
                run_id = run_id,

                # file path:
                ## mainly for ga
                gene_spec_filename = gene_spec_filename,
                ga_performance_filename = ga_performance_filename,
                hyper_parameter_filename = hyper_parameter_filename,
                run_id_filename = str(csv_parent_path) + '/run_id.csv',

                ## sharing from ga to validation
                elite_json_filepath = elite_json_filepath,
                elite_csv_filepath = elite_csv_filepath,

                is_import_previous_strategy = is_import_previous_strategy,
        )
        # run the genetic algorithm
        g.run_ga()

        # run validation
        valid = validation.Validation(
                val_fin_start = val_fin_start,
                val_fin_end = val_fin_end,

                # other parameters
                run_id = run_id,
                trading_fee = trading_fee,
                start_up_cash = start_up_cash,

                # file path:
                ## mainly for ga
                gene_spec_filename = gene_spec_filename,

                ## sharing from ga to validation
                elite_json_filepath = elite_json_filepath,
                elite_csv_filepath = elite_csv_filepath,

                ## for validation
                validation_hyper_parameter_filename = validation_hyper_parameter_filename,
        )

        # run validation for the fittest strategy in each generation
        for gen in range(num_of_generations):
                for num_e in range(num_of_elite):
                        # run validation for the input strategy
                        valid.run_validation(
                                st_generation=gen, 
                                st_num=num_e, 
                                validation_performance_filename = validation_filepath + '/validation_performance_gen' + str(gen) + '_elite' + str(num_e) + '.json'
                        )
except Exception as e:
        print('Error(run_ga_find_fittest.py): ', e)
