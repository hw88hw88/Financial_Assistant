import os
import json

class FileMgt:
    # initialise the folders
    def __init__(self):
        if not os.path.exists('JSON'):
            os.mkdir('JSON')

        if not os.path.exists('CSV'):
            os.mkdir('CSV')
    # find all files in a directory, including all files in all sub-directories
    # input:
    # 1. directory: a string storing the file path
    # output:
    # 1. a list to store the file paths of all files in the directory, or
    # 2. return empty list [], if there is no file in the directory
    @staticmethod
    def list_files_in_directory(directory):
        files = []
        if os.path.exists(directory):
            def list_files(directory):
                for f in os.listdir(directory):
                    if os.path.isfile(os.path.join(directory, f)):
                        files.append(os.path.join(directory, f))
                    else:
                        list_files(os.path.join(directory, f))
            list_files(directory)
        return files

    '''
    @staticmethod
    def to_json(to_json_content, filename):
        content = json.dumps(to_json_content)
        with open(filename, 'w') as f:
            f.write(content)
    
    Title: CM3020 Artificial Intelligence, Week 10 Mid-term coursework
    Author: The author of this project (Anonoymous submission of assignment)
    Date: 2026
    Code version: N/A
    Availability: Submitted Assignment (Not published)
    (Week 10 Mid-term coursework of CM3020 Artificial Intelligence, 2026)

    The code in this function was adapted from the mid-term coursework in the week 10 of "CM3020 Artificial Intelligence" by the author of this project
    All the code was written and prepared by the author of this project, with reference to the starter code from the mid-term coursework of "CM3020 Artificial Intelligence" (Yee-King, no date)

    Reference:
    Yee-King, M., (no date) CM3020 Artificial Intelligence, Week 10 Mid-term coursework starter code [online] Available from: https://www.coursera.org/learn/uol-cm3020-artificial-intelligence/assignment-submission/6JASg/mid-term-coursework [8 December 2025]
    '''
    # write content, such as gene spec, to JSON file(s)
    # input:
    # 1. to_json_content: JSON content in a python dict
    # 2. filename: file path
    # output: (return nothing)
    # 1. JSON file
    @staticmethod
    def write_to_json(to_json_content, filename):
        content = json.dumps(to_json_content)
        with open(filename, 'w') as f:
            f.write(content)

    '''
    @staticmethod
    def to_csv(dna, csv_file):
        csv_str = ""
        for gene in dna:
            for val in gene:
                csv_str = csv_str + str(val) + ","
            csv_str = csv_str + '\n'

        with open(csv_file, 'w') as f:
            f.write(csv_str)

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
    # Write a list of content, such as DNA, to CSV file(s)
    # input: 
    ## 1. list_content: a single dimension list
    ## 2. csv file path
    # output: (return nothing)
    ## 1. write CSV file to disk
    @staticmethod
    def write_dna_to_csv(list_content, csv_file_path):
        csv_str = ""
        for element in list_content:
            csv_str = csv_str + str(element) + ","
        csv_str = csv_str[:-1] + '\n'

        with open(csv_file_path, 'w') as f:
            f.write(csv_str)

    # read content, such as gdict, from JSON file
    # input:
    # 1. filename: a string of file path of a JSON file
    # output:
    # 1. return the content from the JSON file in a python dict{}
    @staticmethod
    def read_json(filename):
        with open(filename) as f:
            content = f.read()
            return json.loads(content)

    # check if a file exists and is not empty
    # input:
    # 1. filename
    # output:
    # 1. boolean: True when the file exists and is not empty, or false
    @staticmethod
    def check_file_exist(filename):
        if os.path.exists(filename):
            if os.path.getsize(filename) > 0:
                return True
        return False

    # reading DNA or gene
    # input:
    # 1. CSV file path
    # output:
    # 1. the elements in CSV
    @staticmethod
    def read_dna_list_from_csv(csv_file_path):
        if not os.path.exists(csv_file_path):
            return None
        with open(csv_file_path) as f:
            csv_content = f.read()

        # separate each element
        csv_content = csv_content.split(',')
        # remove the '\n' end line symbol at the end of file
        csv_content[-1] = csv_content[-1][:-1]
        
        return csv_content

    # read CSV file (not for DNA)
    # input:
    # 1. csv_file_path: file path
    # output:
    # 1. a list of elements in the CSV file
    @staticmethod
    def read_from_csv(csv_file_path):
        if not os.path.exists(csv_file_path):
            return []
        with open(csv_file_path) as f:
            csv_content = f.read()
        lines = csv_content.split('\n')
        csv_list = []
        for line in range(len(lines)):
            # separate each element
            lines[line] = csv_content.split(',')
            for ind in range(len(lines[line])):
                if lines[line][ind] != '':
                    csv_list.append(lines[line][ind])        
        return csv_list

    # write content to CSV file
    # input:
    # 1. csv_file_path: file path
    # 2. to_csv_content: content to be written to CSV file
    # output: (return nothing)
    # write content to CSV file
    @staticmethod
    def write_csv(csv_file_path, to_csv_content):
        with open(csv_file_path, 'w') as f:
            f.write(to_csv_content)