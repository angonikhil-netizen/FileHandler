import streamlit as st
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

st.set_page_config(page_title="File Handler", layout="wide")

# Session state (replacement for Flask session)
if "matter" not in st.session_state:
    st.session_state.matter = ""

def extract_content(file):
    try:
        filename = file.name.lower()

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

# UI
st.title("📄 File Handler App")

# Load section
st.subheader("Load Text / File")

text_input = st.text_area("Enter text manually")

uploaded_file = st.file_uploader(
    "Upload file",
    type=["txt", "pdf", "jpg", "jpeg", "png"]
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Load"):
        if text_input.strip():
            st.session_state.matter = text_input
            st.success("Text loaded.")

        elif uploaded_file:
            res = extract_content(uploaded_file)
            if "ERROR" in res:
                st.error(res)
            else:
                st.session_state.matter = res
                st.success("File imported.")

        else:
            st.warning("Provide text or upload a file.")

with col2:
    if st.button("Reset"):
        st.session_state.matter = ""
        st.success("Reset done.")

# Replace section
st.subheader("Find & Replace")

search_word = st.text_input("Search word")
replace_word = st.text_input("Replace with")

if st.button("Replace"):
    if search_word and search_word in st.session_state.matter:
        st.session_state.matter = st.session_state.matter.replace(search_word, replace_word)
        st.success("Word replaced.")
    else:
        st.error(f"'{search_word}' not found.")

# Display content
st.subheader("Current Content")
st.text_area("Output", st.session_state.matter, height=300)

# Print / Download
st.subheader("Download")

st.download_button(
    label="Download Text File",
    data=st.session_state.matter,
    file_name="output.txt",
    mime="text/plain"
)