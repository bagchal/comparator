import fitz  # PyMuPDF
import pandas as pd
import re

def read_names_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    names = [(name, False) for name in df.iloc[:, 0].dropna()]  # False indicates 'not found'
    return names

def highlight_custom_words_in_pdf(pdf_path, interim_pdf_path, excel_path, custom_string):
    words_found = set()
    doc = fitz.open(pdf_path)
    
    # Regex pattern to find words containing the custom string, case-insensitive
    pattern = re.compile(r'\b\w*' + re.escape(custom_string) + r'\w*\b', re.IGNORECASE)

    for page in doc:
        text = page.get_text("text")
        words = pattern.finditer(text)
        for word in words:
            word_text = word.group()
            words_found.add(word_text)
            word_bbox = page.search_for(word_text)
            for rect in word_bbox:
                annot = page.add_highlight_annot(rect)
                annot.set_colors(stroke=(0, 0, 1))  # Blue color for highlighting
                annot.update()
                annot.set_opacity(0.3)  # Set opacity to 30%

    # Save the words to an Excel file
    df = pd.DataFrame(list(words_found), columns=["Words Containing '" + custom_string + "'"])
    df.to_excel(excel_path, index=False)
    
    # Save the interim PDF after first pass
    doc.save(interim_pdf_path)
    doc.close()

def highlight_names_in_excel_in_pdf(interim_pdf_path, final_pdf_path, names):
    doc = fitz.open(interim_pdf_path)
    for page in doc:
        text = page.get_text("text").lower()
        for idx, (name, found) in enumerate(names):
            if not found:
                name_lower = name.lower()
                if name_lower in text:
                    names[idx] = (name, True)
                    text_instances = page.search_for(name)
                    for inst in text_instances:
                        annot = page.add_highlight_annot(inst)
                        annot.set_colors(stroke=(0, 1, 0))
                        annot.update()
                        annot.set_opacity(0.3)
    doc.save(final_pdf_path)
    doc.close()
    return names

def create_flagged_excel_file(original_excel_path, flagged_excel_path, names_to_match):
    # Read the original Excel file
    df = pd.read_excel(original_excel_path)
    
    # Create a dictionary from names_to_match for easy lookup
    names_dict = {name: found for name, found in names_to_match}

    # Add a new column for the flag
    df['Flag'] = df.iloc[:, 0].apply(lambda name: 'AP not Found In Drawing' if not names_dict.get(name, False) else '')

    # Save to a new flagged Excel file
    df.to_excel(flagged_excel_path, index=False)

def create_matching_string_excel_file(original_excel_path, matching_excel_path, custom_string):
    df = pd.read_excel(original_excel_path)
    
    # Filter rows containing the custom string (case-insensitive)
    matching_df = df[df.iloc[:, 0].str.contains(custom_string, case=False, na=False)]

    # Save to a new Excel file
    matching_df.to_excel(matching_excel_path, index=False)


# In your main function or wherever you call these functions
def main():
    # ... your existing code ...
    names_to_match = read_names_from_excel(excel_path)
    names_to_match = highlight_names_in_excel_in_pdf(interim_pdf_path, final_pdf_path, names_to_match)
    update_excel_file(excel_path, names_to_match)
    names_to_match = read_names_from_excel(excel_path)
    names_to_match = highlight_names_in_excel_in_pdf(interim_pdf_path, final_pdf_path, names_to_match)
    update_excel_file(excel_path, names_to_match)

if __name__ == "__main__":
    main()



def main():
    pdf_path = 'C:\\web\\pdf_excel_comparator\\Dev.pdf'
    interim_pdf_path = 'C:\\web\\pdf_excel_comparator\\interim_highlighted.pdf'
    final_pdf_path = 'C:\\web\\pdf_excel_comparator\\final_highlighted.pdf'
    excel_path = 'C:\\web\\pdf_excel_comparator\\words_list.xlsx'  # Ensure this is not the original file if you're testing
    match_string = 'YourCustomString'  # Replace with the string to match
    
        # Read names and highlight them in the PDF
    names_to_match = read_names_from_excel(excel_path)
    highlight_names_in_excel_in_pdf(interim_pdf_path, final_pdf_path, names_to_match)

    # Any other operations that do not involve writing to the original Excel file

if __name__ == "__main__":
    main()
