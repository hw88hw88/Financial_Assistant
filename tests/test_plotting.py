from plotting import Plotting
import unittest
import file_mgt
import os

class TestPlotting(unittest.TestCase):
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(Plotting)
        self.assertIsNotNone(Plotting.plot_roi)
        self.assertIsNotNone(Plotting.plot_max_drawdown)
        self.assertIsNotNone(Plotting.plot_win_rate)
        self.assertIsNotNone(Plotting.plot_sharpe_ratio)

    # test the files can be created successfully
    def test_img_file(self):
        plot = Plotting()
        fm = file_mgt.FileMgt()

        # remove all existing files in plotting_img directory
        files = fm.list_files_in_directory('plotting_img')
        for f in files:
            os.remove(f)
            self.assertFalse(fm.check_file_exist(f))

        # assert no file in the directory
        files = fm.list_files_in_directory('plotting_img')
        self.assertEqual(len(files), 0)

        # get the run id
        file_path_run_id = 'CSV/run_id.csv'
        if fm.check_file_exist(file_path_run_id):
            run_id_file = fm.read_from_csv(
                csv_file_path=file_path_run_id
            )

        # start plotting
        plot.plot_roi()
        files = fm.list_files_in_directory('plotting_img')
        self.assertEqual(len(files), len(run_id_file))

        plot.plot_max_drawdown()
        files = fm.list_files_in_directory('plotting_img')
        self.assertEqual(len(files), len(run_id_file) * 2)

        plot.plot_win_rate()
        files = fm.list_files_in_directory('plotting_img')
        self.assertEqual(len(files), len(run_id_file) * 3)

        plot.plot_sharpe_ratio()
        files = fm.list_files_in_directory('plotting_img')
        self.assertEqual(len(files), len(run_id_file) * 4)

        for f in files:
            self.assertTrue(fm.check_file_exist(f))
