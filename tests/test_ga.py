import unittest
import ga
import os
import population
import file_mgt
import genome

class TestGA(unittest.TestCase):
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(ga.GA)
        self.assertIsNotNone(ga.GA.metrics)
        self.assertIsNotNone(ga.GA.elitism)
        self.assertIsNotNone(ga.GA.run_ga)
        self.assertIsNotNone(ga.GA.initialise_logs)
        self.assertIsNotNone(ga.GA.close_ga_performance_file)
        self.assertIsNotNone(ga.GA.import_elite_from_previous_run)

        the_ga=ga.GA(pool_size=1,
            start_up_cash=100000,
            trading_fee=0.01,
            pop_size=2,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
        )
        self.assertIsNotNone(the_ga.fin_start)
        self.assertIsNotNone(the_ga.fin_end)
        self.assertIsNotNone(the_ga.start_up_cash)
        self.assertIsNotNone(the_ga.trading_fee)
        self.assertIsNotNone(the_ga.gene_spec_filename)
        self.assertIsNotNone(the_ga.ga_performance_filename)
        self.assertIsNotNone(the_ga.hyper_parameter_filename)

        self.assertIsNotNone(the_ga.num_of_generations)
        self.assertIsNotNone(the_ga.point_mutate_rate)
        self.assertIsNotNone(the_ga.point_mutate_amt)

    # test files can be written successfully by __init__()
    def test_save_to_json_content(self):
        the_ga=ga.GA(pool_size=1, 
            start_up_cash=100000,
            trading_fee=0.01,
            pop_size=2,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
        )
        the_ga.initialise_logs()
        self.assertTrue(os.path.exists(the_ga.hyper_parameter_filename))
        self.assertTrue(os.path.exists(the_ga.gene_spec_filename))
        self.assertFalse(os.path.exists(the_ga.ga_performance_filename))

        os.remove(the_ga.hyper_parameter_filename)
        os.remove(the_ga.gene_spec_filename)

    # test metrics()
    def test_metrics(self):
        start_up_cash=100000
        pop_size=2

        the_ga=ga.GA(pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
        )

        the_ga.run_ga()

        self.assertIsNotNone(the_ga.ga_performance_file_content)
        self.assertEqual(str(type(the_ga.ga_performance_file_content)), "<class 'str'>")
        self.assertGreater(len(the_ga.ga_performance_file_content), 5)

    # test elitism()
    def test_elitism(self):
        start_up_cash = 100000
        pop_size = 4
        num_of_elite = 2

        num_of_generations=2

        # checking generation 0
        generation=0

        the_ga=ga.GA(pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=num_of_generations,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
            num_of_elite = num_of_elite,
        )
        the_ga.initialise_logs()
        pop = population.Population(start_up_cash=start_up_cash, pop_size=pop_size)

        top_n_st, rewards = the_ga.elitism(
            pop=pop,
            generation=generation
        )

        # check returned value
        self.assertIsNotNone(top_n_st)
        self.assertIsNotNone(rewards)

        self.assertEqual(str(type(top_n_st)), "<class 'list'>")
        self.assertEqual(len(top_n_st), num_of_elite)

        self.assertEqual(str(type(rewards)), "<class 'list'>")
        self.assertEqual(len(rewards), pop_size)

        # check saved files
        self.assertTrue(os.path.exists(the_ga.elite_csv_filepath + '/elite_gene_gen' + str(generation) + '_' + str(num_of_elite - 1) + '.csv'))

        self.assertTrue(os.path.exists(the_ga.elite_json_filepath + '/elite_gdict_gen' + str(generation) + '_' + str(num_of_elite - 1) + '.json'))

        # remove test files
        os.remove(the_ga.elite_csv_filepath + '/elite_gene_gen' + str(generation) + '_' + str(num_of_elite - 1) + '.csv')
        os.remove(the_ga.elite_json_filepath + '/elite_gdict_gen' + str(generation) + '_' + str(num_of_elite - 1) + '.json')

    # test run_ga()
    def test_run_ga(self):
        start_up_cash=100000
        pop_size=3

        the_ga=ga.GA(pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
        )

        the_ga.run_ga()

        self.assertIsNotNone(the_ga.ga_performance_filename)
        self.assertTrue(os.path.exists(the_ga.ga_performance_filename))
        self.assertTrue(os.path.exists(the_ga.hyper_parameter_filename))
        self.assertTrue(os.path.exists(the_ga.gene_spec_filename))

        os.remove(the_ga.ga_performance_filename)
        os.remove(the_ga.hyper_parameter_filename)
        os.remove(the_ga.gene_spec_filename)

    # test initialise_logs()
    def test_initialise_logs(self):
        test_content = {'test content': 'test content'}
        filepath = 'JSON/test.json'
        file_mgt.FileMgt.write_to_json(to_json_content=test_content, filename=filepath)

        start_up_cash=100000
        pop_size=3

        the_ga=ga.GA(pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
        )

        # run initialise_log()
        the_ga.initialise_logs()
        self.assertTrue(os.path.exists(the_ga.hyper_parameter_filename))
        self.assertTrue(os.path.exists(the_ga.gene_spec_filename))

        # remove test files
        os.remove(filepath)
        os.remove(the_ga.hyper_parameter_filename)
        os.remove(the_ga.gene_spec_filename)

    # test close_ga_performance_file()
    def test_close_ga_performance_file(self):
        # initialise the test
        the_ga=ga.GA(
            pool_size=1,
            start_up_cash=100000,
            trading_fee=0.01,
            pop_size=2,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
        )

        the_ga.close_ga_performance_file()

        self.assertTrue(os.path.exists(the_ga.ga_performance_filename))

        # remove test file
        os.remove(the_ga.ga_performance_filename)

    # test import_elite_from_previous_run()
    def test_import_elite_from_previous_run(self):
        run_id_filename='CSV/unittest_run_id.csv'
        the_ga=ga.GA(
            pool_size=1,
            start_up_cash=100000,
            trading_fee=0.01,
            pop_size=2,
            num_of_generations=2,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
            is_import_previous_strategy=True,
        )

        # test 1:
        ## create test run_id CSV file
        with open(run_id_filename, 'w') as f:
            f.write('')

        ## test the import of strategy
        st = the_ga.import_elite_from_previous_run(
            run_id_filename=run_id_filename
        )
        self.assertIsNone(st)

        # test 2:
        ## create test run_id CSV file
        with open(run_id_filename, 'w') as f:
            f.write('abc, def')

        ## test the import of strategy
        st = the_ga.import_elite_from_previous_run(
            run_id_filename=run_id_filename
        )
        self.assertIsNone(st)

        # test 3:
        ## create test run_id CSV file
        with open(run_id_filename, 'w') as f:
            f.write('abc, def, hij, klm')

        ## test the import of strategy
        st = the_ga.import_elite_from_previous_run(
            run_id_filename=run_id_filename
        )
        self.assertIsNone(st)

        # test 4:
        ## create test run_id with strategy
        run_id = 'unittest'
        with open(run_id_filename, 'w') as f:
            f.write(run_id)

        fm = file_mgt.FileMgt()
        # create a testing strategy
        g = genome.Genome()
        spec=g.get_gene_spec()
        
        test_gdict = g.get_gdict(
            gene=g.get_random_gene(gene_length=len(spec)),
            spec=spec
            )
        spec['run_id'] = str(run_id)
        test_gdict['run_id'] = str(run_id)

        # test file path
        test_hyper_params_file = f'JSON/{str(run_id)}/hyper_parameter.json'
        test_gdict_file = f'JSON/{str(run_id)}/fittest/elite_gdict_gen0_0.json'

        if not fm.check_file_exist(f'JSON/{str(run_id)}'):
            os.mkdir(f'JSON/{str(run_id)}')

        if not fm.check_file_exist(f'JSON/{str(run_id)}/fittest'):
            os.mkdir(f'JSON/{str(run_id)}/fittest')

        # create test files
        ## test_hyper-parameters file
        fm.write_to_json(
            to_json_content={'num_of_generations': 1},
            filename=test_hyper_params_file
        )



        ## test gdict file
        fm.write_to_json(
            to_json_content=test_gdict,
            filename=test_gdict_file,
        )

        # test if the strategy can be imported
        st = the_ga.import_elite_from_previous_run(
            run_id_filename = run_id_filename,
            )

        self.assertEqual(str(st.gdict['run_id']), str(test_gdict['run_id']))

        # remove test file
        os.remove(run_id_filename)
        os.remove(test_hyper_params_file)
        os.remove(test_gdict_file)

        files = file_mgt.FileMgt.list_files_in_directory(f'JSON/{str(run_id)}')
        for f in files:
            os.remove(f)
            self.assertFalse(os.path.exists(f))

    # tear down
    def test_tear_down(self):
        fm = file_mgt.FileMgt()
        files = []

        # remove files in 'JSON/unittest'
        if fm.check_file_exist('JSON/unittest'):
            files.extend(file_mgt.FileMgt.list_files_in_directory('JSON/unittest'))

        # remove files in 'CSV/unittest'
        if fm.check_file_exist('CSV/unittest'):
            files.extend(file_mgt.FileMgt.list_files_in_directory('CSV/unittest'))

        # remove files in 'JSON/unittest_fittest'
        if fm.check_file_exist('JSON/unittest_fittest'):
            files.extend(file_mgt.FileMgt.list_files_in_directory('JSON/unittest_fittest'))

        # remove files in 'CSV/unittest_fittest'
        if fm.check_file_exist('CSV/unittest_fittest'):
            files.extend(file_mgt.FileMgt.list_files_in_directory('CSV/unittest_fittest'))

        for f in files:
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        if fm.check_file_exist('JSON'):
            if fm.check_file_exist('JSON/unittest'):
                if fm.check_file_exist('JSON/unittest/fittest'):
                    os.rmdir('JSON/unittest/fittest')
                os.rmdir('JSON/unittest')
            if fm.check_file_exist('JSON/unittest_fittest'):
                os.rmdir('JSON/unittest_fittest')

        if fm.check_file_exist('CSV'):
            if fm.check_file_exist('CSV/unittest'):
                if fm.check_file_exist('CSV/unittest/fittest'):
                    os.rmdir('CSV/unittest/fittest')
                os.rmdir('CSV/unittest')
            if fm.check_file_exist('CSV/unittest_fittest'):
                os.rmdir('CSV/unittest_fittest')
