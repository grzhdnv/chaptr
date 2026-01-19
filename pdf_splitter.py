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

    total_pages = doc.page_count
    print(f"Total pages: {total_pages}")
    print(f"Found {len(toc)} sections in ToC.")

    # Calculate ranges first
    sections = []
    for i, entry in enumerate(toc):
        level, title, start_page = entry
        start_page_idx = start_page - 1
        
        if i < len(toc) - 1:
            end_page_idx = toc[i+1][2] - 2
        else:
            end_page_idx = total_pages - 1
            
        if start_page_idx > end_page_idx:
            # Skip invalid ranges or empty sections
            continue
            
        # Ensure bounds
        if start_page_idx < 0: start_page_idx = 0
        if end_page_idx >= total_pages: end_page_idx = total_pages - 1
        
        sections.append({
            "id": i + 1,
            "title": title,
            "start": start_page_idx,
            "end": end_page_idx
        })

    # Display sections to user
    print("\nAvailable Sections:")
    print(f"{'ID':<5} | {'Pages':<15} | {'Title'}")
    print("-" * 50)
    for section in sections:
        page_range = f"{section['start']+1}-{section['end']+1}"
        print(f"{section['id']:<5} | {page_range:<15} | {section['title']}")
    print("-" * 50)
    
    # Prompt for exclusions
    print("\nEnter the IDs of sections you want to EXCLUDE (comma-separated).")
    print("Press Enter to keep all sections.")
    
    user_input = input("Exclude IDs: ").strip()
    excluded_ids = set()
    
    if user_input:
        try:
            parts = user_input.split(',')
            for part in parts:
                if part.strip():
                    excluded_ids.add(int(part.strip()))
        except ValueError:
            print("Invalid input! Please enter numbers separated by commas.")
            doc.close()
            return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("\nProcessing...")
    
    count = 0
    for section in sections:
        if section["id"] in excluded_ids:
            print(f"Skipping (Excluded): {section['title']}")
            continue
            
        print(f"Extracting: '{section['title']}' (Pages {section['start']+1}-{section['end']+1})")
        
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=section['start'], to_page=section['end'])
        
        safe_title = sanitize_filename(section['title'])
        # Use simple counter for output filename order, or keep original ID?
        # Let's keep original ID to avoid confusion
        output_filename = f"{section['id']:03d}_{safe_title}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        new_doc.save(output_path)
        new_doc.close()
        count += 1

    doc.close()
    print(f"\nDone! Extracted {count} files.")

def main():
    parser = argparse.ArgumentParser(description="Split PDF by Table of Contents")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("--output", "-o", default="output", help="Output directory (default: output)")
    
    args = parser.parse_args()
    
    split_pdf_by_toc(args.input_pdf, args.output)

if __name__ == "__main__":
    main()
