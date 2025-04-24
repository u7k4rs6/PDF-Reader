import os
from flask import Flask, request, render_template
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def allowed_file(filename):
    """Check if the file extension is allowed (PDF only)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def check_file_size(file):
    """Check if the file size exceeds the maximum allowed size."""
    if file and allowed_file(file.filename):
        if len(file.read()) > MAX_CONTENT_LENGTH:
            return False
        file.seek(0)  
    return True
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'pdfFile' not in request.files:
        return render_template('error.html', message="No file selected."), 400

    file = request.files['pdfFile']

    if not check_file_size(file):
        return render_template('error.html', message=f"File exceeds the maximum allowed size of {MAX_CONTENT_LENGTH // (1024 * 1024)} MB."), 400
    if file.filename == '':
        return render_template('error.html', message="No file selected."), 400
    if not allowed_file(file.filename):
        return render_template('error.html', message="Invalid file type. Please upload a PDF."), 400
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    extracted_text = extract_text_from_pdf(file_path)
    return render_template('extracted_text.html', extracted_text=extracted_text)
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    import pdfplumber
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")
    return extracted_text

if __name__ == '__main__':
    app.run(debug=True)