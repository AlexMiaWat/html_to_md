# HTML to Markdown Converter

A collection of Python scripts for converting HTML content to Markdown format, with special handling for tables and structured text extraction.

**[Читать на русском](README_ru.md)**
## Features

- Convert HTML files, URLs, or strings to Markdown text
- Automatic table conversion to Markdown table format
- Hierarchical HTML parsing for structured text extraction
- Support for multiple input sources (files, URLs, stdin)
- UTF-8 encoding support
- Ignore technical tags (script, style, meta, etc.)
- Available in both English (grok_html2md.py) and Russian (html2md.py) versions

## Installation

1. Ensure you have Python 3.x installed
2. Install required dependencies:
   ```bash
   pip install requests
   ```
3. Clone or download the scripts to your local directory

## Usage

### grok_html2md.py (English version)

#### Convert HTML file:
```bash
python grok_html2md.py index.html
```

#### Convert from URL:
```bash
python grok_html2md.py -u https://example.com
```

#### Convert HTML string:
```bash
python grok_html2md.py -s "<h1>Title</h1><p>Content</p>"
```

#### Read from stdin:
```bash
cat index.html | python grok_html2md.py
```

### html2md.py (Russian version)

The Russian version has identical functionality and usage:

```bash
python html2md.py index.html
python html2md.py -u https://example.com
python html2md.py -s "<h1>Заголовок</h1><p>Содержимое</p>"
```

## Scripts Overview

### grok_html2md.py
- **Purpose**: Comprehensive HTML to Markdown converter with table support
- **Language**: English
- **Features**: 
  - Builds HTML element tree for structured parsing
  - Converts tables to Markdown format (| column1 | column2 |)
  - Handles horizontal rules as Markdown separators (---)
  - Includes debug output showing HTML tree structure
  - Ignores script, style, meta, link, and noscript tags

### html2md.py
- **Purpose**: Russian version of the HTML converter
- **Language**: Russian (comments and documentation)
- **Features**: Identical to grok_html2md.py but without debug output
- **Note**: Based on grok_html2md.py, provides cleaner output

## Input/Output Formats

### Input Formats
- **HTML files**: Local .html files
- **URLs**: Web pages (requires internet connection)
- **HTML strings**: Direct HTML content as command-line argument
- **Stdin**: Piped HTML content

### Output Format
- Plain text with Markdown table formatting
- Each HTML element on separate lines with empty line separators
- Tables formatted as:
  ```
  | Header 1 | Header 2 |
  |----------|----------|
  | Cell 1   | Cell 2   |
  ```
- UTF-8 encoded text output to stdout

## Dependencies

- `sys` - System-specific parameters and functions
- `argparse` - Command-line argument parsing
- `requests` - HTTP library for URL fetching
- `html.parser` - HTML parsing library (built-in)

## Testing

Run the test suite to verify functionality:

```bash
python test_html2md_scripts.py
```

The test suite will:
- Process multiple websites and local files
- Generate detailed reports in `test_results/test_report.md`
- Compare output between grok_html2md.py and html2md.py
- Verify table detection and line counts

## Examples

### Processing a local HTML file:
```bash
python grok_html2md.py index.html > output.md
```

### Converting a webpage:
```bash
python html2md.py -u https://habr.com/ru/articles/123456/ > article.md
```

### Batch processing multiple files:
```bash
for file in *.html; do
  python grok_html2md.py "$file" > "${file%.html}.md"
done
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check individual script headers for specific license information.