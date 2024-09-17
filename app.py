import os
from flask import Flask, session, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from helpers.pdf_utils import parse_pdf
from helpers.validation import allowed_file
from helpers.csv_output import create_csv
from helpers.excel_output import create_excel

# Initialize Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
CORS(app)

# Directory to temporarily save uploaded files
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_files_and_parse():
    # Get the list of uploaded files
    files = request.files.getlist('files')
    print(f"Received {len(files)} files")
    print(f"Files: {files}")

    if not files:
        return jsonify({'error': 'No files uploaded'}), 400

    parsed_results = []

    for file in files:
        # Ensure the file is a valid PDF based on the file name, mimetype, and magic number
        if file and allowed_file(file):
            print(f"Processing file: {file.filename}")
            try:
                # Save the file temporarily
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                print(f"Saved file to: {file_path}")

                # Parse the PDF using your parsing logic
                with open(file_path, 'rb') as pdf_file:
                    print(f"Parsing {filename}")
                    parsed_data = parse_pdf(pdf_file)
                    print(f"Parsed data: {parsed_data}")

                # Append parsed data to results
                if isinstance(parsed_data, dict):
                    parsed_results.append({
                        'filename': filename,
                        'parsed_data': parsed_data
                    })
                else:
                    parsed_results.append({
                        'filename': filename + "-1",
                        'parsed_data': parsed_data[0]
                    })
                    parsed_results.append({
                        'filename': filename + "-2",
                        'parsed_data': parsed_data[1]
                    })

                # Remove the file after processing
                #os.remove(file_path)
                #print(f"Deleted {file_path}")

            except Exception as e:
                return jsonify({'error': f"Error parsing {filename}: {str(e)}"}), 500
        else:
            return jsonify({'error': f'Invalid file format for {file.filename}. Only PDF allowed'}), 400

    # Store parsed results in the session
    session['parsed_results'] = parsed_results

    return jsonify({'parsed_results': parsed_results})


@app.route('/generate-output', methods=['POST'])
def generate_output():
    output_type = request.json.get('output_type', 'csv')
    parsed_results = session.get('parsed_results')

    if not parsed_results:
        return jsonify({'error': 'No parsed results found in session'}), 400

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
