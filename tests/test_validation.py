import unittest
import validation
import os
import file_mgt
import ga

class TestValidation(unittest.TestCase):        
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(validation.Validation)

        run_id = 'test'

        valid = validation.Validation(
            run_id=run_id,
            val_fin_start='2023-01-01',
            val_fin_end='2023-01-31',
            validation_hyper_parameter_filename = 'JSON/unittest_validation_hyper_parameter.json',
            )

        self.assertIsNotNone(valid.gene_spec_filename)
        self.assertIsNotNone(valid.validation_hyper_parameter_filename)

        self.assertIsNotNone(valid.run_validation)
        self.assertIsNotNone(valid.import_strategy)
        self.assertIsNotNone(valid.metrics)

    # test import_strategy()
    def test_import_strategy(self):
        # initialise the test
        start_up_cash=100000
        pop_size=1
        num_of_elite = 1
        num_of_generations=1
        run_id = 'unittest'

        the_ga=ga.GA(
            pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=num_of_generations,
            point_mutate_rate=0.0, 
            point_mutate_amt=0.25,

            fin_start='2023-12-01',
            fin_end='2023-12-31',

            num_of_elite = num_of_elite,
            run_id=run_id,
    
            # file path:
            ## mainly for ga
            gene_spec_filename = 'JSON/unittest_gene_spec.json',
            ga_performance_filename = 'JSON/unittest_ga_performance.json',
            hyper_parameter_filename = 'JSON/unittest_hyper_parameter.json',
    
            ## sharing from ga to validation
            elite_json_filepath = 'JSON/unittest_fittest',
            elite_csv_filepath = 'CSV/unittest_fittest',
        )

        the_ga.run_ga()

        valid = validation.Validation(
            run_id=run_id,
            val_fin_start='2023-01-01',
            val_fin_end='2023-01-31',
            validation_hyper_parameter_filename = 'JSON/unittest_validation_hyper_parameter.json',
            )

        # checking the consistency of file name
        self.assertEqual(valid.gene_spec_filename, the_ga.gene_spec_filename)

        # test importing the strategy
        st = valid.import_strategy(
            st_generation=num_of_generations - 1,
            st_num=num_of_elite - 1)

        # check the imported strategy
        self.assertIsNotNone(st)
        self.assertIsNotNone(st.total_value)

        # test importing the strategy without gdict JSON file
        fm = file_mgt.FileMgt()
        # remove gdict JSON files
        files = fm.list_files_in_directory(valid.elite_json_filepath)
        for f in files:
            os.remove(f)
            self.assertFalse(fm.check_file_exist(f))

        # test importing the strategy without gdict JSON file
        st = valid.import_strategy(
            st_generation=num_of_generations - 1,
            st_num=num_of_elite - 1)

        # check the imported strategy
        self.assertIsNotNone(st)
        self.assertIsNotNone(st.total_value)

        # remove test files
        os.remove(the_ga.gene_spec_filename)
        os.remove(the_ga.hyper_parameter_filename)
        os.remove(the_ga.ga_performance_filename)

        files = fm.list_files_in_directory(valid.elite_csv_filepath)
        for f in files:
            os.remove(f)
            self.assertFalse(fm.check_file_exist(f))

    # test run_validation()
    def test_run_validation(self):
        # initialise the test
        start_up_cash=100000
        pop_size=1
        num_of_elite = 1
        num_of_generations=1
        run_id = 'test'

        the_ga=ga.GA(
            pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=num_of_generations,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
            run_id=run_id,
            gene_spec_filename = 'JSON/unittest_gene_spec.json',
            ga_performance_filename = 'JSON/unittest_ga_performance.json',
            hyper_parameter_filename = 'JSON/unittest_hyper_parameter.json',
            elite_json_filepath = 'JSON/unittest_fittest',
            elite_csv_filepath = 'CSV/unittest_fittest',
            num_of_elite = num_of_elite,
        )

        # training, finding the fittest strategy
        the_ga.run_ga()

        # start validation
        valid = validation.Validation(
            # period:
            val_fin_start='2023-01-01',
            val_fin_end='2023-01-31',

            # other parameters
            run_id=run_id,
            trading_fee = 0.01,
            start_up_cash = 100000,

            # file path:
            ## sharing from ga to validation
            gene_spec_filename = 'JSON/unittest_gene_spec.json',
            elite_json_filepath = 'JSON/unittest_fittest',
            elite_csv_filepath = 'CSV/unittest_fittest',

            ## for validation
            validation_hyper_parameter_filename = 'JSON/unittest_validation_hyper_parameter.json',
            )

        # run validation
        validation_performance_filename = 'JSON/unittest_validation_performance.json'
        valid.run_validation(
            st_generation=(num_of_generations - 1), 
            st_num=(num_of_elite -1),
            validation_performance_filename = validation_performance_filename,
        )

        # checking the output file from run_validation()
        fm = file_mgt.FileMgt()
        self.assertTrue(fm.check_file_exist(validation_performance_filename))
        # remove test file
        os.remove(validation_performance_filename)

    # test metrics()
    def test_metrics(self):
        # initialise the test
        start_up_cash=100000
        pop_size=1
        num_of_elite = 1
        num_of_generations=1
        run_id = 'test'

        the_ga=ga.GA(pool_size=1,
            start_up_cash=start_up_cash,
            trading_fee=0.01,
            pop_size=pop_size,
            num_of_generations=num_of_generations,
            point_mutate_rate=0.1, 
            point_mutate_amt=0.25,
            fin_start='2023-12-01',
            fin_end='2023-12-31',
            run_id=run_id,
            num_of_elite = num_of_elite,
    
            # file path:
            ## mainly for ga
            gene_spec_filename = 'JSON/unittest_gene_spec.json',
            ga_performance_filename = 'JSON/unittest_ga_performance.json',
            hyper_parameter_filename = 'JSON/unittest_hyper_parameter.json',
    
            ## sharing from ga to validation
            elite_json_filepath = 'JSON/unittest_fittest',
            elite_csv_filepath = 'CSV/unittest_fittest',
        )

        # training, finding the fittest strategy
        the_ga.run_ga()

        validation_hyper_parameter_filename = 'JSON/unittest_validation_hyper_parameter.json'
        # start validation
        valid = validation.Validation(
            run_id=run_id,
            val_fin_start='2023-01-01',
            val_fin_end='2023-01-31',
            validation_hyper_parameter_filename = validation_hyper_parameter_filename,
            )

        # run validation
        # metrics() will be called by run_validation()

        validation_performance_filename = 'JSON/unittest_validation_performance.json'

        valid.run_validation(
            st_generation=(num_of_generations - 1), 
            st_num=(num_of_elite -1),
            validation_performance_filename = validation_performance_filename,
        )

        # checking the output file from run_validation()
        fm = file_mgt.FileMgt()
        self.assertTrue(fm.check_file_exist(validation_performance_filename))
        # remove test file
        os.remove(validation_performance_filename)
        os.remove(validation_hyper_parameter_filename)

    # tear down
    def test_tear_down(self):
        csv_folder = 'CSV/unittest_fittest'
        json_folder = 'JSON/unittest_fittest'
        
        # remove files in 'JSON/unittest_fittest'
        files = file_mgt.FileMgt.list_files_in_directory(json_folder)
        # remove files in 'CSV/unittest_fittest'
        files.extend(file_mgt.FileMgt.list_files_in_directory(csv_folder))
        for f in files:
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        
        os.rmdir(json_folder)
        os.rmdir(csv_folder)