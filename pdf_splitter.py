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

def split_pdf_by_toc(input_pdf_path, output_dir, deep=False):
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
    
    # Filter ToC based on mode
    if not deep:
        # Find the top-most level (usually 1, but could be different)
        min_level = min(entry[0] for entry in toc)
        print(f"Default mode: Splitting by top-level sections (Level {min_level}).")
        print("Use --deep to split by all subsections.")
        toc = [entry for entry in toc if entry[0] == min_level]
    else:
        print("Deep mode: Splitting by all sections.")

    # Calculate ranges first
    sections = []
    for i, entry in enumerate(toc):
        level, title, start_page = entry
        start_page_idx = start_page - 1
        
        if i < len(toc) - 1:
            end_page_idx = toc[i+1][2] - 2
        else:
            end_page_idx = total_pages - 1
            
        # For deep usage, sometimes parent and child start on same page.
        # e.g. Ch1 (p1), Sect1.1 (p1).
        # In this case range for Ch1 is 1-0 -> invalid.
        # We will keep it in the list for display, but mark as "Container" if range is invalid?
        # OR just skip it as before.
        # If we skip it, the user doesn't see "Chapter 1" in the list, just 1.1.
        # While technically correct for splitting, it might be confusing visually.
        # Let's keep it but mark it as skipped/zero-length? 
        # No, existing logic skips. Let's stick with that for now unless user complains.
        
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
            "end": end_page_idx,
            "level": level
        })

    # Display sections to user
    print("\nAvailable Sections:")
    print(f"{'ID':<5} | {'Pages':<15} | {'Title'}")
    print("-" * 60)
    for section in sections:
        page_range = f"{section['start']+1}-{section['end']+1}"
        # Indent title based on level. min_level might be 1.
        # We want relative indentation.
        # Let's assume level 1 has 0 indent.
        indent = "    " * (section['level'] - 1)
        title_display = f"{indent}{section['title']}"
        print(f"{section['id']:<5} | {page_range:<15} | {title_display}")
    print("-" * 60)
    
    # Prompt for exclusions
    print("\nEnter the IDs of sections you want to EXCLUDE (comma-separated).")
    print("Press Enter to keep all sections.")
    
    try:
        user_input = input("Exclude IDs: ").strip()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        doc.close()
        return

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
            print(f"Skipping (Excluded): {section['title'].strip()}")
            continue
            
        print(f"Extracting: '{section['title'].strip()}' (Pages {section['start']+1}-{section['end']+1})")
        
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=section['start'], to_page=section['end'])
        
        safe_title = sanitize_filename(section['title'])
        # Use simple counter for output filename order
        # Using section['id'] might preserve gaps if excluded, which is fine.
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
    parser.add_argument("--deep", action="store_true", help="Split by all sections (recursive), not just top-level chapters.")
    
    args = parser.parse_args()
    
    split_pdf_by_toc(args.input_pdf, args.output, deep=args.deep)

if __name__ == "__main__":
    main()
