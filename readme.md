# wikiscraperx

## Overview
This repository contains the wikiscraperx project, a Python script designed to scrape tables from HTML documents and save them as CSV files. The project consists of two main Python files:

1. `tableParser.py`:  logic for parsing HTML tables.
2. `mainCli.py`:  CLI interface for the application.

## Prerequisites

- Python 3.x
- Additional Python packages, as listed in `requirements.txt`.

## Installation
To install the latest version:
```bash
pip install wikiscraperx
```
Or install from source:
```bash
git clone https://github.com/Joseph-Press/wikiscraperx.git
cd wikiscraperx
pip install .
```

## Usage

### Command Line Interface

Scrape all tables from a Wikipedia page to a folder (default CSV):
```bash
wikiscraperx --url "https://en.wikipedia.org/wiki/Python_(programming_language)" --output-folder ./output
```

Scrape to JSON format:
```bash
wikiscraperx --url "https://en.wikipedia.org/wiki/Python_(programming_language)" --output-folder ./output --format json
```

Save a specific table by its header (to stdout):
```bash
wikiscraperx --url "https://en.wikipedia.org/wiki/Python_(programming_language)" --header "Summary of Python 3's built-in types"
```

Save as JSON to stdout:
```bash
wikiscraperx --url "https://en.wikipedia.org/wiki/Python_(programming_language)" --header "Summary of Python 3's built-in types" --format json
``` 