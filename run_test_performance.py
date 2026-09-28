# run the testing or validation

try:
    import validation
    import os
    import file_mgt
    from chatbot import Chatbot

    # initialise hyper-parameters

    ## the number of run_id in the CSV file
    ### 0 means the first run_id, 1 means the second
    num_of_run = 4

    ## the testing period
    testing_fin_start = '2025-01-01'
    testing_fin_end = '2025-12-31'

    run_id = Chatbot.get_run_id(num_of_run=num_of_run)

    if run_id is not None:
        # import training hyper-parameters
        hyper_parameter_file_name = 'JSON/' + str(run_id) + '/hyper_parameter.json'

        fm = file_mgt.FileMgt()

        hyper_parameter = fm.read_json(filename=hyper_parameter_file_name)
        if hyper_parameter['run_id'] != run_id:
            print('<run_id> of hyper-parameter does not match!')

        # setting up hyper-parameters    
        trading_fee = hyper_parameter['trading_fee']
        start_up_cash = hyper_parameter['start_up_cash']

        num_of_generations = hyper_parameter['num_of_generations']
        num_of_elite = hyper_parameter['num_of_elite']
        pop_size = hyper_parameter['pop_size']
        point_mutate_rate = hyper_parameter['point_mutate_rate']
        point_mutate_amt = hyper_parameter['point_mutate_amt']

        # check file path availability of writing performance to JSON
        test_file_path = 'JSON/' + str(run_id) + '/testing_' + str(testing_fin_start) + '_' + str(testing_fin_end)
        if not fm.check_file_exist(test_file_path):
            os.mkdir(test_file_path)

        # run testing or validation
        # validation
        valid = validation.Validation(
                val_fin_start = testing_fin_start,
                val_fin_end = testing_fin_end,

                # other parameters
                run_id = run_id,
                trading_fee = trading_fee,
                start_up_cash = start_up_cash,

                # file path:
                ## mainly for ga
                gene_spec_filename = hyper_parameter['gene_spec_filename'],

                ## sharing from ga to validation (for testing)
                elite_json_filepath = hyper_parameter['elite_json_filepath'],
                elite_csv_filepath = hyper_parameter['elite_csv_filepath'],

                ## for testing
                validation_hyper_parameter_filename = test_file_path + '/testing_hyper_parameter.json',
                is_testing=True
        )

        # run validation/ testing for the fittest strategy in each generation
        for gen in range(num_of_generations):
            # run for each elite in the generation
            for num_e in range(num_of_elite):
                # run validation for the input strategy
                valid.run_validation(
                    st_generation=gen, 
                    st_num=num_e, 
                    validation_performance_filename = test_file_path + '/testing_performance_gen' + str(gen) + '_elite' + str(num_e) + '.json'
                )
    else:
        print('<run_id> file not found')
except Exception as e:
    print('Error(run_test_performance.py): ', e)
