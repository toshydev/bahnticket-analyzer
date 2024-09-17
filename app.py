import os
from flask import Flask, session, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from helpers.pdf_utils import parse_pdf
from helpers.validation import allowed_file
from helpers.csv_output import create_csv
from helpers.excel_output import create_excel

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'


UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_files_and_parse():
    parsed_results = session.get('parsed_results')
    if not parsed_results:
        session['parsed_results'] = []

    print(f"Request: {request.files.keys()}")

    uploaded_file = request.files['files']
    file_bytes = uploaded_file.read()

    with open(os.path.join(UPLOAD_FOLDER, uploaded_file.filename), 'wb') as f:
        f.write(file_bytes)
        # check if the newwly created file is a valid PDF
        if allowed_file(uploaded_file):
            return jsonify({'message': 'File uploaded successfully'}), 200

    os.remove(os.path.join(UPLOAD_FOLDER, uploaded_file.filename))
    print(f"Deleted {os.path.join(UPLOAD_FOLDER, uploaded_file.filename)}")
    return jsonify({'error': 'Invalid file format. Only PDF allowed'}), 400


@app.route('/generate-output', methods=['POST'])
def generate_output():
    output_type = request.json.get('output_type', 'csv')
    parsed_results = []

    files = [file for file in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, file))]
    print(f"Files in upload folder: {files}")
    if not files:
        return jsonify({'error': 'No files found in upload folder'}), 400

    for file in files:
        # Ensure the file is a valid PDF based on the file name, mimetype, and magic number
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file)
            try:
                # Parse the PDF using your parsing logic
                with open(file_path, 'rb') as pdf_file:
                    print(f"Processing file: {pdf_file}")
                    if allowed_file(pdf_file):
                        parsed_data = parse_pdf(pdf_file)
                        print(f"Parsed data: {parsed_data}")

                    else:
                        return jsonify({'error': f'Invalid file format for {file_path}. Only PDF allowed'}), 400

                # Append parsed data to results
                if isinstance(parsed_data, dict):
                    parsed_results.append({
                        'filename': file,
                        'parsed_data': parsed_data
                    })
                else:
                    parsed_results.append({
                        'filename': file + "-1",
                        'parsed_data': parsed_data[0]
                    })
                    parsed_results.append({
                        'filename': file + "-2",
                        'parsed_data': parsed_data[1]
                    })
                
                os.remove(file_path)
                print(f"Deleted {file_path}")

            except Exception as e:
                return jsonify({'error': f"Error parsing {file_path}: {str(e)}"}), 500

    # Generate the output file based on requested format
    if output_type == 'csv':
        output_file = 'parsed_output.csv'
        create_csv(parsed_results, output_file)
    elif output_type == 'excel':
        output_file = 'parsed_output.xlsx'
        create_excel(parsed_results, output_file)
    else:
        return jsonify({'error': 'Invalid output type specified'}), 400

    # Return the file for download
    return send_file(output_file, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
