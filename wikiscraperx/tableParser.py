import csv
import logging
import os
import re
import sys

import bs4
from bs4 import BeautifulSoup as bs

LOG = logging.getLogger(__name__)

MAX_FILE_LEN = os.getenv("MAX_FILE_LEN", 250)

class CustomError(Exception):
    pass

class RowCounter:
    def __init__(self, tag):
        self.remaining_rows = int(tag["rowspan"]) - 1
        del tag["rowspan"]
        self.tag_value = tag

    def get_value(self):
        self.remaining_rows -= 1
        return self.tag_value

class HtmlToTable:
    def __init__(self, table_tag):
        self.table_tag = table_tag

    def extract_header(self):
        caption = self.table_tag.find("caption")
        if caption:
            return sanitize_cell(caption)
        return None

    def extract_rows(self):
        saved_row_data = []
        for row in self.table_tag.find_all("tr"):
            cells = row.find_all(["th", "td"])

            # handle colspan attributes
            for idx, cell in reversed(list(enumerate(cells))):
                if cell.has_attr("colspan"):
                    for _ in range(int(cell["colspan"]) - 1):
                        cells.insert(idx, cell)

            # initialize saved_row_data for the first row
            if not saved_row_data:
                saved_row_data = [None for _ in cells]

            # handle rowspan
            elif len(cells) != len(saved_row_data):
                for idx, row_data in enumerate(saved_row_data):
                    if row_data and row_data.remaining_rows:
                        cells.insert(idx, row_data.get_value())

            # save rowspan for future rows
            for idx, cell in enumerate(cells):
                if cell.has_attr("rowspan"):
                    saved_row_data[idx] = RowCounter(cell)

            cleaned = [sanitize_cell(cell) for cell in cells]

            # fill in missing col with empty strings
            missing_cols = len(saved_row_data) - len(cleaned)
            if missing_cols:
                cleaned += [""] * missing_cols

            yield cleaned

    # save table to a CSV file
    def save_to_file(self, path):
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            self.save(f)

    # write table to a CSV
    def save(self, output=sys.stdout):
        csv_writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator="\n")
        for row in self.extract_rows():
            csv_writer.writerow(row)

    # save table to a JSON file
    def save_to_json(self, path):
        import json
        rows = list(self.extract_rows())
        data = []
        if not rows:
            return

        # assuming first row is header
        headers = rows[0]
        for row in rows[1:]:
             # zip headers with row data
             entry = {}
             for i, cell in enumerate(row):
                 if i < len(headers):
                     entry[headers[i]] = cell
                 else:
                     entry[f"col_{i}"] = cell
             data.append(entry)
        
        with open(path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

class TableParser:
    def __init__(self, html_text):
        self.html_tables = [HtmlToTable(tag) for tag in extract_tables_from_html(html_text, min_columns=2)]

    # save all tables to a directory as separate CSV files
    def save_to_folder(self, folder_path, format="csv"):
        os.makedirs(folder_path, exist_ok=True)
        for idx, table in enumerate(self.html_tables):
            file_name = f"table_{idx + 1}"
            header = table.extract_header()
            if header:
                file_name += "_" + header
            
            if format == "json":
                file_path = os.path.join(folder_path, generate_csv_filename(file_name).replace(".csv", ".json"))
                LOG.info(f"Saving table {idx + 1} to {file_path}")
                table.save_to_json(file_path)
            else:
                file_path = os.path.join(folder_path, generate_csv_filename(file_name))
                LOG.info(f"Saving table {idx + 1} to {file_path}")
                table.save_to_file(file_path)

    # save a single table to CSV file based on its index
    def save_single_table(self, index, folder_path, format="csv"):
        if index < len(self.html_tables):
            table = self.html_tables[index]
            file_name = f"table_{index + 1}"
            header = table.extract_header()
            if header:
                file_name += "_" + header
            
            if format == "json":
                file_path = os.path.join(folder_path, generate_csv_filename(file_name).replace(".csv", ".json"))
                LOG.info(f"Saving table {index + 1} to {file_path}")
                table.save_to_json(file_path)
            else:
                file_path = os.path.join(folder_path, generate_csv_filename(file_name))
                LOG.info(f"Saving table {index + 1} to {file_path}")
                table.save_to_file(file_path)
        else:
            LOG.error(f"Table index {index} out of range")

def extract_tables_from_html(html_text, min_columns=2):
    soup = bs(html_text, "lxml")
    tables = soup.find_all("table")
    return [table for table in tables if len(table.find_all("tr")) > 1 and len(table.find_all("tr")[0].find_all(["th", "td"])) >= min_columns]

# sanitize cell data by removing extra tags
def sanitize_cell(cell):
    to_remove = (
        {"name": "sup", "class": "reference"},
        {"name": "sup", "class": "sortkey"},
        {"name": "span", "class": "mw-editsection"},
    )

    for tag in to_remove:
        for match in cell.find_all(**tag):
            match.extract()

    # replace <br> tags with spaces
    line_breaks = cell.find_all("br")
    for br in line_breaks:
        br.replace_with(new_span(" "))

    # handle cells that contain only an image
    tags = cell.find_all()
    if len(tags) == 1 and tags[0].name == "img":
        return clean_spaces(tags[0]["alt"])

    # remove footnotes and other bracketed text
    tags = [t for t in cell.find_all(string=True) if not t.startswith("[")]

    return clean_spaces("".join(tags))

# remove extra whitespace from text
def clean_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

# create a new <span> tag
def new_span(text_value):
    return bs(f"<span>{text_value}</span>", "lxml").html.body.span

# generate a CSV file name from text
def generate_csv_filename(text):
    text = text.lower()
    text = re.sub(r"[,|'|\"/]", "", text)
    text = re.sub(r"[\(|\)|-]", " ", text)
    joined = "_".join(text.split())
    if len(joined) > MAX_FILE_LEN:
        joined = joined[: joined.rindex("_", 0, MAX_FILE_LEN)]
    return joined + ".csv"
