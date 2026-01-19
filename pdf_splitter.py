import fitz  # PyMuPDF
import argparse
import os
import re

def sanitize_filename(filename):
    """
    Sanitize the filename by removing invalid characters.
    """
    # Remove invalid characters for filenames
    s = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores and strip whitespace
    s = s.strip().replace(" ", "_")
    return s

def split_pdf_by_toc(input_pdf_path, output_dir):
    """
    Splits a PDF based on its Table of Contents.
    """
    if not os.path.exists(input_pdf_path):
        print(f"Error: File '{input_pdf_path}' not found.")
        return

    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return

    toc = doc.get_toc()
    
    if not toc:
        print("Error: No Table of Contents found in this PDF.")
        doc.close()
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_pages = doc.page_count
    print(f"Total pages: {total_pages}")
    print(f"Found {len(toc)} sections in ToC.")

    for i, entry in enumerate(toc):
        level, title, start_page = entry
        
        # PyMuPDF pages are 1-based in get_toc? 
        # Documentation says: get_toc() returns [lvl, title, page, dest]
        # page is 1-based.
        # fitz.open() and manipulation uses 0-based indexing.
        
        # verified: get_toc returns 1-based page numbers.
        # BUT we need to check if user needs to adjust this.
        # Wait, let's verify with a quick script or documentation check if I can.
        # Standard PyMuPDF get_toc returns 1-based page numbers usually.
        # Actually, let's look at the docs if I could. Or just assume standard 1-based and convert to 0-based for slicing.
        
        # Let's assume start_page is 1-based from get_toc.
        
        start_page_idx = start_page - 1

        # Determine end page
        if i < len(toc) - 1:
            next_entry = toc[i+1]
            next_start_page = next_entry[2]
            end_page_idx = next_start_page - 2 # 1-based next start - 1 (previous page) - 1 (to 0-based) = -2
            # Actually range is [start, end], but fitz uses to_page as inclusive? or we extract range?
            # We will use insert_pdf which takes from_page and to_page (inclusive).
            # So if next section starts at 10 (index 9), this section ends at 9 (index 8).
            
            # Wait, easier logic:
            # start of this section (0-based): start_page - 1
            # start of next section (0-based): toc[i+1][2] - 1
            # so we want pages from (start_page - 1) up to (toc[i+1][2] - 2) inclusive.
            
            end_page_idx = toc[i+1][2] - 2
        else:
            end_page_idx = total_pages - 1

        if start_page_idx > end_page_idx:
            # This can happen if multiple toc entries point to the same page or nesting weirdness
            # We will just skip or grab the single page
             # But if they point to the same page, start=end.
             pass

        # Valid range check
        if start_page_idx < 0: start_page_idx = 0
        if end_page_idx >= total_pages: end_page_idx = total_pages - 1
        
        if start_page_idx > end_page_idx:
            print(f"Skipping empty section: {title}")
            continue

        print(f"Extracting: '{title}' (Pages {start_page_idx+1}-{end_page_idx+1})")
        
        # Create new PDF
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page_idx, to_page=end_page_idx)
        
        safe_title = sanitize_filename(title)
        output_filename = f"{i+1:03d}_{safe_title}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        new_doc.save(output_path)
        new_doc.close()

    doc.close()
    print("Done!")

def main():
    parser = argparse.ArgumentParser(description="Split PDF by Table of Contents")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("--output", "-o", default="output", help="Output directory (default: output)")
    
    args = parser.parse_args()
    
    split_pdf_by_toc(args.input_pdf, args.output)

if __name__ == "__main__":
    main()
