import mimetypes

def allowed_file(file):
    """
    Validates if the uploaded file is a valid PDF based on:
    - The file extension.
    - The MIME type (first guess).
    - The file header (magic number).
    - Attempts to open and parse the file as a valid PDF.
    """
    # 1. Check file extension
    filename = file.filename  # Extract the filename from the file object
    print(f"Validating file: {filename}")
    
    if not (filename and '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'):
        print(f"Invalid file extension for {filename}")
        return False

    # 2. Check MIME type (if available in the file object)
    if file.mimetype != 'application/pdf':
        print(f"Invalid MIME type for {filename}")
        return False

    # 3. Check the magic number (first few bytes of the file)
    file.seek(0)  # Ensure the file pointer is at the beginning
    file_header = file.read(4)  # Read the first 4 bytes to check the PDF signature
    if file_header != b'%PDF':
        print(f"Invalid file header for {filename}")
        return False

    file.seek(0)  # Reset the file pointer after reading the header

    # 4. Try to open and parse the file to ensure it's a valid PDF
    try:
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            pdf.pages  # Attempt to access the pages to ensure it's readable
    except Exception as e:
        print(f"File parsing error: {e}")
        return False

    return True
