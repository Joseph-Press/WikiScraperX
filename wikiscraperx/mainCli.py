import argparse
import logging
from tableParser import TableParser  

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    cli = argparse.ArgumentParser(description='Parse HTML tables and save them as CSV files.')
    
    cli.add_argument('--debug', help='Enable debug-level logging', default=False, action='store_true')
    cli.add_argument('--html-file', help='Path to the HTML file containing tables', required=True)
    cli.add_argument('--output-folder', help='Directory where CSV files will be saved', required=True)
    cli.add_argument('--table-index', type=int, default=None, help='Index of single table to save (Optional)')
    
    args = cli.parse_args()
    
    # enables debug-level logging if --debug is set
    if args.debug:
        LOGGER.setLevel(logging.DEBUG)
    
    # reads the HTML file
    with open(args.html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # initialize the table parser
    table_parser = TableParser(html_content)  # Using the TableParser class from table_parser.py
    
    # log the operation
    LOGGER.info(f"Parsing tables from '{args.html_file}' into '{args.output_folder}'")
    
    # check if a single table index is specified
    if args.table_index is not None:
        LOGGER.debug(f"Parsing table at index {args.table_index} from '{args.html_file}'")
        table_parser.save_single_table(args.table_index, args.output_folder)
    else:
        table_parser.save_to_folder(args.output_folder)

if __name__ == "__main__":
    main()
