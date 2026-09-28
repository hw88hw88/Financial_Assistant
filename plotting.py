import matplotlib.pyplot as plt
import file_mgt

# The code in this class plot the charts of trained, validated and tested strategies with a set of complete record in JSON and the run_id must be stored in the run_id.csv properly. Otherwise, error(s) might occur.
# The code in this file runs only if user runs this file or the 'tests/test_plotting.py' file or both.
class Plotting:
    # plotting the ROI of evolved strategies and S&P 500 Index
    # output:
    # 1. images in the folder 'plotting_img'
    @staticmethod
    def plot_roi():
        fm = file_mgt.FileMgt()

        # get the run id
        file_path_run_id = 'CSV/run_id.csv'
        if fm.check_file_exist(file_path_run_id):
            run_id_file = fm.read_from_csv(
                csv_file_path=file_path_run_id
            )
            # iterate all run IDs
            for num_run_id in range(len(run_id_file)):
                # get the run id
                run_id = run_id_file[num_run_id]

                # get hyper-parameters
                file_path_hyper_parameter = f'JSON/{run_id}/hyper_parameter.json'
                if fm.check_file_exist(file_path_hyper_parameter):
                    hyper_parameter = fm.read_json(
                        filename=file_path_hyper_parameter
                    )
                    start_up_cash = hyper_parameter.get('start_up_cash')
                else:
                    print('file_path_hyper_parameter not exist: run_id= ', run_id)
                    continue

                # Training performance
                file_path_ga_performance = f'JSON/{run_id}/ga_performance.json'
                if fm.check_file_exist(file_path_ga_performance):
                    ga_performance = fm.read_json(
                        filename=file_path_ga_performance
                    )
                    ga_performance = ga_performance.get('result')

                    training_roi = []
                    for i in range(len(ga_performance)):
                        roi = ga_performance[i].get('fittest_return_0') / start_up_cash
                        training_roi.append(roi)

                    plt.plot(
                        range(len(training_roi)), 
                        training_roi,
                        'ro',
                        label = 'ROI (Training) in 2023'
                        )
                else:
                    print('file_path_ga_performance not exist: run_id= ', run_id)
                    continue

                # Validation performance
                folder_path = f'JSON/{run_id}/validation'
                validation_roi = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    validation_performance_file_path = folder_path + '/validation_performance_gen' + str(i) + '_elite0.json'
                    if fm.check_file_exist(validation_performance_file_path):
                        content = fm.read_json(filename=validation_performance_file_path)
                        validation_roi.append(content.get('validation_return') / start_up_cash)
                    else:
                        print(validation_performance_file_path, ' not exist')

                plt.plot(
                    range(len(validation_roi)), 
                    validation_roi,
                    'b+',
                    label = 'ROI (Validation) in 2024'
                    )

                # Testing performance
                folder_path = f'JSON/{run_id}/testing_2025-01-01_2025-12-31'

                testing_roi = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    file_path_testing_performance = folder_path + '/testing_performance_gen' + str(i) + '_elite0.json'

                    if fm.check_file_exist(file_path_testing_performance):
                        content = fm.read_json(filename=file_path_testing_performance)

                        testing_roi.append(content.get('testing_return') / start_up_cash)
                    else:
                        print('file_path_testing_performance not exist')
                        return

                plt.plot(
                    range(len(testing_roi)), 
                    testing_roi,
                    'g*',
                    label = 'ROI (Testing) in 2025'
                    )

                # ROI of S&P 500 Index
                sp500 = [float(0.175) for i in range(50)]
                plt.plot(
                    range(len(testing_roi)), 
                    sp500,
                    'm.',
                    label = 'ROI of S&P 500 Index in 2025'
                    )
                    

                plt.xlabel('Generation')
                plt.ylabel('ROI')
                plt.title('ROI of Evolved strategies and S&P 500 Index')
                plt.legend()
                plt.savefig('plotting_img/' + str(run_id) + '_roi.png')
                plt.clf()

    # plotting the Maximum Drawdown of evolved strategies
    # output:
    # 1. images in the folder 'plotting_img'
    @staticmethod
    def plot_max_drawdown():
        fm = file_mgt.FileMgt()
        
        # get the run id
        file_path_run_id = 'CSV/run_id.csv'
        if fm.check_file_exist(file_path_run_id):
            run_id_file = fm.read_from_csv(
                csv_file_path=file_path_run_id
            )
            # iterate all run IDs
            for num_run_id in range(len(run_id_file)):
                # get the run id
                run_id = run_id_file[num_run_id]

                # Training performance
                file_path_ga_performance = f'JSON/{run_id}/ga_performance.json'
                if fm.check_file_exist(file_path_ga_performance):
                    ga_performance = fm.read_json(
                        filename=file_path_ga_performance
                    )
                    ga_performance = ga_performance.get('result')

                    training_max_drawdown = []
                    for i in range(len(ga_performance)):
                        max_drawdown = ga_performance[i].get('fittest_max_drawdown_0')
                        training_max_drawdown.append(max_drawdown)

                    plt.plot(
                        range(len(training_max_drawdown)), 
                        training_max_drawdown,
                        'ro',
                        label = 'Max Drawdown (Training) in 2023'
                        )
                else:
                    print('file_path_ga_performance not exist: run_id= ', run_id)
                    continue

                # Validation performance
                folder_path = f'JSON/{run_id}/validation'
                validation_max_drawdown = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    validation_performance_file_path = folder_path + '/validation_performance_gen' + str(i) + '_elite0.json'
                    if fm.check_file_exist(validation_performance_file_path):
                        content = fm.read_json(filename=validation_performance_file_path)
                        validation_max_drawdown.append(content.get('validation_max_drawdown'))
                    else:
                        print(validation_performance_file_path, ' not exist')

                plt.plot(
                    range(len(validation_max_drawdown)), 
                    validation_max_drawdown,
                    'b+',
                    label = 'Max Drawdown (Validation) in 2024'
                    )

                # Testing performance
                folder_path = f'JSON/{run_id}/testing_2025-01-01_2025-12-31'

                testing_max_drawdown = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    file_path_testing_performance = folder_path + '/testing_performance_gen' + str(i) + '_elite0.json'

                    if fm.check_file_exist(file_path_testing_performance):
                        content = fm.read_json(filename=file_path_testing_performance)

                        testing_max_drawdown.append(content.get('testing_max_drawdown'))
                    else:
                        print('file_path_testing_performance not exist')
                        return

                plt.plot(
                    range(len(testing_max_drawdown)), 
                    testing_max_drawdown,
                    'g*',
                    label = 'Max Drawdown (Testing) in 2025'
                    )                

                plt.xlabel('Generation')
                plt.ylabel('Max Drawdown')
                plt.title('Max Drawdown of Evolved strategies')
                plt.legend()
                plt.savefig('plotting_img/' + str(run_id) + '_max_drawdown.png')
                plt.clf()

    # plotting the Win rate of evolved strategies
    # output:
    # 1. images in the folder 'plotting_img'
    @staticmethod
    def plot_win_rate():
        fm = file_mgt.FileMgt()
        
        # get the run id
        file_path_run_id = 'CSV/run_id.csv'
        if fm.check_file_exist(file_path_run_id):
            run_id_file = fm.read_from_csv(
                csv_file_path=file_path_run_id
            )
            # iterate all run IDs
            for num_run_id in range(len(run_id_file)):
                # get the run id
                run_id = run_id_file[num_run_id]

                # Training performance
                file_path_ga_performance = f'JSON/{run_id}/ga_performance.json'
                if fm.check_file_exist(file_path_ga_performance):
                    ga_performance = fm.read_json(
                        filename=file_path_ga_performance
                    )
                    ga_performance = ga_performance.get('result')

                    training_win_rate = []
                    for i in range(len(ga_performance)):
                        win_rate = ga_performance[i].get('fittest_win_rate_0')
                        training_win_rate.append(win_rate)

                    plt.plot(
                        range(len(training_win_rate)), 
                        training_win_rate,
                        'ro',
                        label = 'Win Rate (Training) in 2023'
                        )
                else:
                    print('file_path_ga_performance not exist: run_id= ', run_id)
                    continue

                # Validation performance
                folder_path = f'JSON/{run_id}/validation'
                validation_win_rate = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    validation_performance_file_path = folder_path + '/validation_performance_gen' + str(i) + '_elite0.json'
                    if fm.check_file_exist(validation_performance_file_path):
                        content = fm.read_json(filename=validation_performance_file_path)
                        validation_win_rate.append(content.get('validation_win_rate'))
                    else:
                        print(validation_performance_file_path, ' not exist')

                plt.plot(
                    range(len(validation_win_rate)), 
                    validation_win_rate,
                    'b+',
                    label = 'Win Rate (Validation) in 2024'
                    )

                # Testing performance
                folder_path = f'JSON/{run_id}/testing_2025-01-01_2025-12-31'

                testing_win_rate = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    file_path_testing_performance = folder_path + '/testing_performance_gen' + str(i) + '_elite0.json'

                    if fm.check_file_exist(file_path_testing_performance):
                        content = fm.read_json(filename=file_path_testing_performance)

                        testing_win_rate.append(content.get('testing_win_rate'))
                    else:
                        print('file_path_testing_performance not exist')
                        return

                plt.plot(
                    range(len(testing_win_rate)), 
                    testing_win_rate,
                    'g*',
                    label = 'Win Rate (Testing) in 2025'
                    )                

                plt.xlabel('Generation')
                plt.ylabel('Win Rate')
                plt.title('Win Rate of Evolved strategies')
                plt.legend()
                plt.savefig('plotting_img/' + str(run_id) + '_win_rate.png')
                plt.clf()

    # plotting the Sharpe Ratio of evolved strategies
    # output:
    # 1. images in the folder 'plotting_img'
    @staticmethod
    def plot_sharpe_ratio():
        fm = file_mgt.FileMgt()
        
        # get the run id
        file_path_run_id = 'CSV/run_id.csv'
        if fm.check_file_exist(file_path_run_id):
            run_id_file = fm.read_from_csv(
                csv_file_path=file_path_run_id
            )
            # iterate all run IDs
            for num_run_id in range(len(run_id_file)):
                # get the run id
                run_id = run_id_file[num_run_id]

                # Training performance
                file_path_ga_performance = f'JSON/{run_id}/ga_performance.json'
                if fm.check_file_exist(file_path_ga_performance):
                    ga_performance = fm.read_json(
                        filename=file_path_ga_performance
                    )
                    ga_performance = ga_performance.get('result')

                    training_sharpe_ratio = []
                    for i in range(len(ga_performance)):
                        sharpe_ratio = ga_performance[i].get('fittest_sharpe_ratio')
                        training_sharpe_ratio.append(sharpe_ratio)

                    plt.plot(
                        range(len(training_sharpe_ratio)), 
                        training_sharpe_ratio,
                        'ro',
                        label = 'Sharpe Ratio (Training) in 2023'
                        )
                else:
                    print('file_path_ga_performance not exist: run_id= ', run_id)
                    continue

                # Validation performance
                folder_path = f'JSON/{run_id}/validation'
                validation_sharpe_ratio = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    validation_performance_file_path = folder_path + '/validation_performance_gen' + str(i) + '_elite0.json'
                    if fm.check_file_exist(validation_performance_file_path):
                        content = fm.read_json(filename=validation_performance_file_path)
                        validation_sharpe_ratio.append(content.get('validation_sharpe_ratio'))
                    else:
                        print(validation_performance_file_path, ' not exist')

                plt.plot(
                    range(len(validation_sharpe_ratio)), 
                    validation_sharpe_ratio,
                    'b+',
                    label = 'Sharpe Ratio (Validation) in 2024'
                    )

                # Testing performance
                folder_path = f'JSON/{run_id}/testing_2025-01-01_2025-12-31'

                testing_sharpe_ratio = []

                # iterate all generations, because one file is for one generation
                for i in range(len(ga_performance)):
                    file_path_testing_performance = folder_path + '/testing_performance_gen' + str(i) + '_elite0.json'

                    if fm.check_file_exist(file_path_testing_performance):
                        content = fm.read_json(filename=file_path_testing_performance)

                        testing_sharpe_ratio.append(content.get('testing_sharpe_ratio'))
                    else:
                        print('file_path_testing_performance not exist')
                        return

                plt.plot(
                    range(len(testing_sharpe_ratio)), 
                    testing_sharpe_ratio,
                    'g*',
                    label = 'Sharpe Ratio (Testing) in 2025'
                    )                

                plt.xlabel('Generation')
                plt.ylabel('Sharpe Ratio')
                plt.title('Sharpe Ratio of Evolved strategies')
                plt.legend()
                plt.savefig('plotting_img/' + str(run_id) + '_sharpe_ratio.png')
                plt.clf()

# plotting the ROI of evolved strategies and S&P 500 Index
Plotting.plot_roi()
# plotting the Maximum Drawdown of evolved strategies
Plotting.plot_max_drawdown()
# plotting the Win Rate of evolved strategies
Plotting.plot_win_rate()
# plotting the Sharpe Ratio of evolved strategies
Plotting.plot_sharpe_ratio()
