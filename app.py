from flask import Flask, render_template, request, session, redirect, url_for
import os
import PyPDF2
from PIL import Image
import numpy as np

# Safe import for EasyOCR
try:
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "clean_slate_key_2026"

def extract_content(file):
    try:
        filename = file.filename.lower()
        if filename.endswith('.txt'):
            return file.read().decode('utf-8')
        elif filename.endswith('.pdf'):
            reader_pdf = PyPDF2.PdfReader(file)
            return " ".join([p.extract_text() or "" for p in reader_pdf.pages])
        elif filename.endswith(('.jpg', '.jpeg', '.png')):
            if not OCR_AVAILABLE:
                return "ERROR: OCR Engine not found."
            img = Image.open(file).convert('RGB')
            results = reader.readtext(np.array(img), detail=0)
            return " ".join(results)
    except Exception as e:
        return f"ERROR: {str(e)}"
    return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'matter' not in session: session['matter'] = ""
    error, success = "", ""

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == "reset":
            session.clear()
            return redirect(url_for('index'))

        try:
            if action == "load":
                text = request.form.get('initial_text', '').strip()
                file = request.files.get('file_input')
                if text:
                    session['matter'] = text
                    success = "Text loaded."
                elif file and file.filename:
                    res = extract_content(file)
                    if "ERROR" in res: error = res
                    else:
                        session['matter'] = res
                        success = "File imported."
            
            elif action == "replace":
                s = request.form.get('search_word', '')
                r = request.form.get('replace_word', '')
                if s and s in session['matter']:
                    session['matter'] = session['matter'].replace(s, r)
                    success = "Word replaced."
                else: error = f"'{s}' not found."
            
            elif action == "print":
                return render_template('print.html', final_matter=session['matter'])
                
        except Exception:
            error = "System error occurred."

    return render_template('index.html', current_matter=session['matter'], error=error, success=success)

if __name__ == '__main__':
    app.run(debug=True)