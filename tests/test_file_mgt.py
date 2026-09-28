import unittest
import os
import json
import file_mgt

class TestFileMgt(unittest.TestCase):
    # test if the class, variables and functions can be created successfully or not
    def test_class_functions(self):
        self.assertIsNotNone(file_mgt.FileMgt)

        fm = file_mgt.FileMgt()

        self.assertIsNotNone(fm.read_json)
        self.assertIsNotNone(fm.check_file_exist)
        self.assertIsNotNone(fm.write_dna_to_csv)
        self.assertIsNotNone(fm.write_to_json)
        self.assertIsNotNone(fm.list_files_in_directory)
        self.assertIsNotNone(fm.read_dna_list_from_csv)
        self.assertIsNotNone(fm.read_from_csv)
        self.assertIsNotNone(fm.write_csv)

    # test list_files_in_directory()
    def test_list_files_in_directory(self):
        fm=file_mgt.FileMgt()

        # try writing a new JSON file
        content = {'content': 'test content'}
        filepath = 'JSON/test/test.json'
        if not os.path.exists('JSON/test'):
            os.mkdir('JSON/test')
        fm.write_to_json(to_json_content=content, filename=filepath)

        # list and check the number of JSON file(s) is 1
        files = fm.list_files_in_directory('JSON/test')
        files = fm.list_files_in_directory('JSON/test')
        self.assertEqual(len(files), 1)
        read_file_content = fm.read_json(filename=filepath)
        self.assertEqual(read_file_content, content)

        # remove the test file
        os.remove(filepath)
        os.rmdir('JSON/test')

    # test write_to_json()
    def test_write_to_json(self):
        fm=file_mgt.FileMgt()
        to_json_content='test content'
        filename='JSON/test.json'

        fm.write_to_json(to_json_content=to_json_content, filename=filename)

        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            content=f.read()
            content=json.loads(content)
        self.assertEqual(content, to_json_content)

        # remove test file
        os.remove(filename)

    # test write_dna_to_csv()
    def test_write_dna_to_csv(self):
        fm=file_mgt.FileMgt()
        dna_list=[1.234, 2.345, 3.567]
        csv_file='CSV/test.csv'
        fm.write_dna_to_csv(list_content=dna_list, csv_file_path=csv_file)

        self.assertTrue(os.path.exists(csv_file))

        with open(csv_file) as f:
            csv_str = f.read()
            lines = csv_str[:-1]
            file_items = lines.split(',')
            items_from_file=[float(item) for item in file_items]
        self.assertEqual(items_from_file, dna_list)
        os.remove(csv_file)

    # test read_json()
    def test_read_json(self):
        fm=file_mgt.FileMgt()

        # write to a new JSON test file
        content = {'content': 'test content'}
        filepath = 'JSON/test.json'
        fm.write_to_json(to_json_content=content, filename=filepath)

        # check the JSON file created successfully or not
        self.assertTrue(os.path.exists(filepath))

        # read the JSON test file
        content2 = fm.read_json(filename=filepath)

        # assert the content was read
        self.assertIsNotNone(content2)

        # assert the content read from the test file is same as the content written to the test file
        self.assertEqual(content, content2)

        # remove the test file
        os.remove(filepath)

    # test check_file_exist()
    def test_check_file_exist(self):
        fm=file_mgt.FileMgt()

        test_content = 'test content'
        test_file_path = 'JSON/test.txt'

        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        self.assertFalse(fm.check_file_exist(test_file_path))

        with open(test_file_path, 'w') as f:
            f.write(test_content)

        self.assertTrue(fm.check_file_exist(test_file_path))
        os.remove(test_file_path)

    # test read_dna_list_from_csv()
    def test_read_dna_list_from_csv(self):
        fm=file_mgt.FileMgt()
        dna_list=[1.234, 2.345, 3.567]
        csv_file='CSV/test.csv'
        fm.write_dna_to_csv(list_content=dna_list, csv_file_path=csv_file)

        self.assertTrue(os.path.exists(csv_file))

        content_from_csv = fm.read_dna_list_from_csv(csv_file_path=csv_file)
        for c in range(len(content_from_csv)):
            content_from_csv[c] = float(content_from_csv[c])

        self.assertEqual(content_from_csv, dna_list)

        # remove test file
        os.remove(csv_file)

    # test read_from_csv()
    def test_read_from_csv(self):
        fm=file_mgt.FileMgt()

        # write to csv
        test_content='test content'
        csv_file='CSV/test.csv'
        with open(csv_file, 'w') as f:
            f.write(test_content)

        # read csv
        ## check file exists
        self.assertTrue(fm.check_file_exist(csv_file))
        content = fm.read_from_csv(csv_file_path=csv_file)

        ## check content exists
        self.assertIsNotNone(content)

        ## check content correct
        self.assertEqual(content[0], test_content)

        # remove test file
        os.remove(csv_file)

    # test write_csv()
    def test_write_csv(self):
        fm=file_mgt.FileMgt()

        csv_file_path = 'CSV/test.csv'
        csv_content = 'test content'

        # write to csv
        fm.write_csv(csv_file_path=csv_file_path,
                     to_csv_content=csv_content)

        self.assertTrue(fm.check_file_exist(csv_file_path))
        content_from_csv = fm.read_from_csv(csv_file_path=csv_file_path)
        self.assertIsNotNone(content_from_csv)
        self.assertEqual(content_from_csv[0], csv_content)
