from flask import Flask, request, render_template, send_file
import os
import shutil  # Import shutil for file copy
from comparator import (
    read_names_from_excel, highlight_custom_words_in_pdf,
    create_matching_string_excel_file, highlight_names_in_excel_in_pdf
)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        pdf_file = request.files['pdf']
        excel_file = request.files['excel']
        custom_string = request.form['match_string']

        if pdf_file and excel_file:
            pdf_path = os.path.join('uploads', pdf_file.filename)
            interim_pdf_path = os.path.join('uploads', 'interim_' + pdf_file.filename)
            final_pdf_path = os.path.join('uploads', 'final_' + pdf_file.filename)
            original_excel_path = os.path.join('uploads', excel_file.filename)
            comp_excel_path = os.path.join('uploads', 'comp.xlsx')  # Path for comp.xlsx
            comp_copy_path = os.path.join('uploads', 'comp_copy.xlsx')  # Path for comp_copy.xlsx

            # Save the PDF and Excel files
            pdf_file.save(pdf_path)
            excel_file.save(original_excel_path)

            # Create a copy of the comp.xlsx file if it doesn't exist
            if not os.path.exists(comp_copy_path):
                shutil.copyfile(comp_excel_path, comp_copy_path)

            # First pass: Highlight words in PDF using the custom string
            highlight_custom_words_in_pdf(pdf_path, interim_pdf_path, original_excel_path, custom_string)

            # Create a new Excel file containing matching words from the PDF and custom string
            matching_excel_path = os.path.join('uploads', 'matching_words.xlsx')
            create_matching_string_excel_file(original_excel_path, matching_excel_path, custom_string)

            # Second pass: Highlight names in the interim PDF using the comp_copy.xlsx file
            names_to_match = read_names_from_excel(comp_copy_path)
            highlight_names_in_excel_in_pdf(interim_pdf_path, final_pdf_path, names_to_match)

            # Send the final processed PDF to the user
            return send_file(final_pdf_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
