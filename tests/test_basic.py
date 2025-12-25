import unittest
from wikiscraperx.tableParser import TableParser, extract_tables_from_html

class TestTableParser(unittest.TestCase):
    def setUp(self):
        self.html = """
        <html>
        <body>
            <table>
                <caption>Test Table</caption>
                <tr><th>Col1</th><th>Col2</th></tr>
                <tr><td>Val1</td><td>Val2</td></tr>
            </table>
            <table>
                <tr><td>SingleRow</td></tr>
            </table>
        </body>
        </html>
        """

    def test_extract_tables(self):
        tables = extract_tables_from_html(self.html, min_columns=2)
        self.assertEqual(len(tables), 1)

    def test_parser_init(self):
        parser = TableParser(self.html)
        self.assertEqual(len(parser.html_tables), 1)
        
    def test_extract_header(self):
        parser = TableParser(self.html)
        table = parser.html_tables[0]
        self.assertEqual(table.extract_header(), "Test Table")

    def test_extract_rows(self):
        parser = TableParser(self.html)
        table = parser.html_tables[0]
        rows = list(table.extract_rows())
        self.assertEqual(len(rows), 2) # Header + 1 data row
        self.assertEqual(rows[0], ['Col1', 'Col2'])
        self.assertEqual(rows[1], ['Val1', 'Val2'])

    def test_json_output(self):
        import json
        import os
        parser = TableParser(self.html)
        table = parser.html_tables[0]
        
        test_file = "test_output.json"
        table.save_to_json(test_file)
        
        try:
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['Col1'], 'Val1')
            self.assertEqual(data[0]['Col2'], 'Val2')
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
