import argparse
import logging
import requests
import sys

from .tableParser import TableParser

LOGGER = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    cli = argparse.ArgumentParser(
        description="Scrape tables from Wikipedia pages into CSVs"
    )
    cli.add_argument("--debug", help="Enable debug-level logging", default=False, action='store_true')
    cli.add_argument("--url", help="URL of the Wikipedia page to scrape", required=True)
    cli.add_argument("--output-folder", help="Folder to write all tables from a url")
    cli.add_argument("--format", help="Output format (csv or json)", default="csv", choices=["csv", "json"])
    cli.add_argument("--header", help="Write a single HTML table by header to stdout")

    args = cli.parse_args()

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    try:
        headers = {
            'User-Agent': 'WikiScraperX/1.0 (https://github.com/Joseph-Press/wikiscraperx; joepress101@gmail.com)'
        }
        resp = requests.get(args.url, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Failed to fetch URL: {e}")
        sys.exit(1)

    parser = TableParser(resp.text)

    if args.output_folder:
        LOGGER.info(f"Parsing all tables from '{args.url}' into '{args.output_folder}'")
        parser.save_to_folder(args.output_folder, format=args.format)
        return

    if args.header:
        LOGGER.debug(f"Parsing table '{args.header}' from '{args.url}'")
        
        found = False
        for table in parser.html_tables:
            header = table.extract_header()
            if header and args.header.lower() in header.lower():
                 # Write to stdout
                 if args.format == "json":
                     import json
                     rows = list(table.extract_rows())
                     data = []
                     if rows:
                         headers = rows[0]
                         for row in rows[1:]:
                             entry = {}
                             for i, cell in enumerate(row):
                                 if i < len(headers):
                                     entry[headers[i]] = cell
                                 else:
                                     entry[f"col_{i}"] = cell
                             data.append(entry)
                     print(json.dumps(data, indent=4, ensure_ascii=False))
                 else:
                     table.save(sys.stdout)
                 found = True
                 break
        if not found:
            LOGGER.error(f"No table found with header containing '{args.header}'")
            sys.exit(1)
        return

    LOGGER.error("Must provide either an `--output-folder` or `--header`")
    sys.exit(1)

if __name__ == "__main__":
    main()