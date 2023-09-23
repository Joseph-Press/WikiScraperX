
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

    # Extract table header if available
    def extract_header(self):
        caption = self.table_tag.find("caption")
        if caption:
            return sanitize_cell(caption)
        return None

    # Extract rows from the table
    def extract_rows(self):
        saved_row_data = []
        for row in self.table_tag.findAll("tr"):
            cells = row.findAll(["th", "td"])

            # Handle colspan attributes
            for idx, cell in reversed(list(enumerate(cells))):
                if cell.has_attr("colspan"):
                    for _ in range(int(cell["colspan"]) - 1):
                        cells.insert(idx, cell)

            # Initialize saved_row_data for the first row
            if not saved_row_data:
                saved_row_data = [None for _ in cells]

            # Handle rowspan attributes
            elif len(cells) != len(saved_row_data):
                for idx, row_data in enumerate(saved_row_data):
                    if row_data and row_data.remaining_rows:
                        cells.insert(idx, row_data.get_value())

            # Save rowspan data for future rows
            for idx, cell in enumerate(cells):
                if cell.has_attr("rowspan"):
                    saved_row_data[idx] = RowCounter(cell)

            # Sanitize cell data
            cleaned = [sanitize_cell(cell) for cell in cells]

            # Fill in missing columns with empty strings
            missing_cols = len(saved_row_data) - len(cleaned)
            if missing_cols:
                cleaned += [""] * missing_cols

            yield cleaned

    # Save table to a CSV file
    def save_to_file(self, path):
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            self.save(f)

    # Write table to a CSV output (can be a file or stdout)
    def save(self, output=sys.stdout):
        csv_writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator="\n")
        for row in self.extract_rows():
            csv_writer.writerow(row)

# Class to parse multiple HTML tables
class TableParser:
    def __init__(self, html_text):
        self.html_tables = [HtmlToTable(tag) for tag in extract_tables_from_html(html_text, min_columns=2)]

    # Save all tables to a directory as separate CSV files
    def save_to_folder(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        for idx, table in enumerate(self.html_tables):
            file_name = f"table_{idx + 1}"
            header = table.extract_header()
            if header:
                file_name += "_" + header
            file_path = os.path.join(folder_path, generate_csv_filename(file_name))
            LOG.info(f"Saving table {idx + 1} to {file_path}")
            table.save_to_file(file_path)

    # Save a single table to a CSV file based on its index
    def save_single_table(self, index, folder_path):
        if index < len(self.html_tables):
            table = self.html_tables[index]
            file_name = f"table_{index + 1}"
            header = table.extract_header()
            if header:
                file_name += "_" + header
            file_path = os.path.join(folder_path, generate_csv_filename(file_name))
            LOG.info(f"Saving table {index + 1} to {file_path}")
            table.save_to_file(file_path)
        else:
            LOG.error(f"Table index {index} out of range")

# Extract tables from HTML text with at least min_columns
def extract_tables_from_html(html_text, min_columns=2):
    soup = bs(html_text, "lxml")
    tables = soup.findAll("table")
    return [table for table in tables if len(table.findAll("tr")) > 1 and len(table.findAll("tr")[0].findAll(["th", "td"])) >= min_columns]

# Sanitize cell data by removing unnecessary tags
def sanitize_cell(cell):
    to_remove = (
        {"name": "sup", "class": "reference"},
        {"name": "sup", "class": "sortkey"},
        {"name": "span", "class": "mw-editsection"},
    )

    for tag in to_remove:
        for match in cell.findAll(**tag):
            match.extract()

    # Replace <br> tags with spaces
    line_breaks = cell.findAll("br")
    for br in line_breaks:
        br.replace_with(new_span(" "))

    # Handle cells that contain only an image
    tags = cell.findAll()
    if len(tags) == 1 and tags[0].name == "img":
        return clean_spaces(tags[0]["alt"])

    # Remove footnotes and other bracketed text
    tags = [t for t in cell.findAll(text=True) if not t.startswith("[")]

    return clean_spaces("".join(tags))

# Remove extra whitespace from text
def clean_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

# Create a new <span> tag
def new_span(text_value):
    return bs(f"<span>{text_value}</span>", "lxml").html.body.span

# Generate a CSV file name from text
def generate_csv_filename(text):
    text = text.lower()
    text = re.sub(r"[,|'|\"/]", "", text)
    text = re.sub(r"[\(|\)|-]", " ", text)
    joined = "_".join(text.split())
    if len(joined) > MAX_FILE_LEN:
        joined = joined[: joined.rindex("_", 0, MAX_FILE_LEN)]
    return joined + ".csv"
