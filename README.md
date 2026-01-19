# PDF Splitter based on Table of Contents

This is a simple automated tool to split large PDF files into smaller PDF files based on their Table of Contents (ToC).

## Features

-   **Automatic Splitting**: detailed parsing of the PDF's Table of Contents.
-   **Interactive Mode**: Lists all found sections and lets you choose which ones to exclude before processing.
-   **Sanitized Filenames**: Automatically cleans up section titles to use as valid filenames.

## Prerequisites

-   Python 3.x
-   `pymupdf` library

## Installation

1.  Clone the repository or download the files.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from the command line, providing the path to your input PDF file:

```bash
python pdf_splitter.py <input_pdf_path>
```

### Optional Arguments

-   `-o` or `--output`: Specify the output directory (default is `output`).

### Example

```bash
python pdf_splitter.py my_large_book.pdf -o chapters
```

When you run the command, the script will:
1.  Read the PDF and extract the Table of Contents.
2.  Display a list of all sections with their page ranges.
3.  Prompt you to enter the IDs of any sections you want to **exclude** (comma-separated).
4.  Process the remaining sections and save them as individual PDF files in the specified output directory.
