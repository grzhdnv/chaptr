import fitz

def create_dummy_pdf(filename="dummy_with_toc.pdf"):
    doc = fitz.open()
    
    # Create 10 pages
    for i in range(10):
        page = doc.new_page()
        page.insert_text((50, 50), f"This is page {i+1}", fontsize=20)
    
    # Define a Table of Contents
    # [level, title, page_num]
    # page_num is 1-based
    toc = [
        [1, "Chapter 1", 1],
        [2, "Section 1.1", 2],
        [1, "Chapter 2", 4],
        [1, "Chapter 3", 8],
    ]
    
    doc.set_toc(toc)
    doc.save(filename)
    print(f"Created {filename} with {len(toc)} ToC entries.")

if __name__ == "__main__":
    create_dummy_pdf()
