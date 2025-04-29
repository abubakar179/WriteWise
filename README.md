# 📝 WriteWise
*AI-enhanced notetaking for the masses*

WriteWise is a Flask-based web application that lets users create, edit, and organise rich-text documents in a simple, folder-based interface. Built with students and writers in mind, it also features image-to-text transcription (OCR) to bridge the gap between physical and digital notes.

This project was developed as part of my A-Level Computer Science course in early 2025.



## 🚀 Features

- 🔐 **User Authentication** – Secure registration and login with password hashing.
- 🗂️ **File Explorer** – Create, manage and organise documents in folders.
- 🖋️ **WYSIWYG Editor** – Rich-text editing with formatting tools (bold, italics, colour, lists, etc.).
- 📷 **Image Transcription** – Upload images of text to convert them to editable HTML (powered by Tesseract OCR).
- ⚠️ **XSS Protection** – Editor sanitises pasted content to prevent script injection.



## ❗ Missing or Planned Features

Some features were planned but not fully implemented:
- 🔒 Document encryption (files are currently stored as plaintext)
- 📤 Export to file (PDF/Word)
- 🧠 Improved handwritten text recognition via neural networks or better OCR models
- 🖨️ Print preview layout
- 🎨 CSS (to improve the overall aesthetics of the website)



## 🛠 Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/abubakar179/WriteWise.git
   cd writewise
   ```
2. **Create virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate # or `venv\Scripts\activate` on Windows
    ```
3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4. **Create SQLite database**
    ```bash
    python3 create.py
    ```
5. ** Start Flask web server** (By default, the app runs at http://0.0.0.0:5000/.)
    ```bash
    python3 app.py
    ```
