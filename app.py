import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
import bcrypt
from datetime import datetime, timedelta, timezone
import uuid
import pytesseract
from PIL import Image
import os
if not os.path.exists("/app/database/database.db"):
    from create import create_tables
    create_tables()

app = Flask(__name__)
app.secret_key = "INSERT KEY HERE"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class UserAuth:

    def __init__(self, db_path="/app/database/database.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def validate_user(self, username, password):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("SELECT user_id, password_hash FROM users WHERE username=?", (username,))
            
            row = cursor.fetchone()

            if row is None:
                return "Account not found"
            user_id, stored_hash = row # cursor.fetchone always returns a tuple so only get index 0 item (hash)
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                cursor.execute("SELECT session_id, expires_at FROM sessions WHERE user_id=?", (user_id,))
                row = cursor.fetchone()

                if row is None:
                    session_id = str(uuid.uuid4())
                    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                    cursor.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", (session_id, user_id, expires_at))
                    conn.commit()
                    session["user_id"] = user_id
                    session["session_id"] = session_id
                    return redirect(url_for("dashboard"))
                
                else:
                    session_id, expires_at = row
                    expires_at = datetime.fromisoformat(expires_at)
                    if expires_at <= datetime.now(timezone.utc):
                        session_id = str(uuid.uuid4())
                        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                        cursor.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", (session_id, user_id, expires_at))
                        conn.commit()
                        session["user_id"] = user_id
                        session["session_id"] = session_id
                        return redirect(url_for("dashboard"))
                    else:
                        session_id, expires_at = row
                        session["user_id"] = user_id
                        session["session_id"] = session_id
                        return redirect(url_for("dashboard"))
    
            else:
                return "Invalid password"

    def register_user(self, username, password, email):
        if not username or not password or not email:
            return "All fields are required"
        
        hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("SELECT email FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return "Email already taken."
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                return "Username already taken."
            try:
                cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", (username, hashpass, email))
                conn.commit()
                return f"{username} registered successfully"
            except sqlite3.IntegrityError:
                return "An error occurred while registering an account. Please try again."
    
class Documents:
    
    def __init__(self, db_path="/app/database/database.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def fetchDocs(self, user_id):
        # fetch recent documents from user
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("""
                SELECT d.document_id, d.document_title, d.last_edited
                FROM documents d
                JOIN folders f ON d.folder_id = f.folder_id
                WHERE f.user_id = ?
                ORDER BY d.last_edited DESC
                LIMIT 5
            """, (user_id,))
            recent_documents = cursor.fetchall()
        return recent_documents
    
    def createDoc(self, user_id, document_title, folder_id, new_folder_name):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            if folder_id == "new" and new_folder_name:
                cursor.execute("INSERT INTO folders (user_id, folder_title) VALUES (?, ?)", (user_id, new_folder_name))
                cursor.execute("SELECT folder_id FROM folders WHERE folder_title = ?", (new_folder_name,))
                folder_id = cursor.lastrowid
            cursor.execute("INSERT INTO documents (folder_id, document_title, document_text, last_edited) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",(folder_id, document_title, "",))
            conn.commit()

    def viewDoc(self, document_id, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("""SELECT * 
                            FROM documents d
                            JOIN folders f ON d.folder_id = f.folder_id
                            WHERE document_id=? AND f.user_id=? 
                            """, (document_id, user_id))
            document = cursor.fetchone()
            return document
    
    def saveDoc(self, document_text, document_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("""
                UPDATE documents
                SET document_text = ?, last_edited = ?
                WHERE document_id = ?
            """, (document_text, datetime.now(), document_id))
            conn.commit()

class Folders:
    def __init__(self, db_path="/app/database/database.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def fetchFolders(self, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("SELECT folder_id, folder_title FROM folders WHERE user_id = ?", (user_id,))
            user_folders = cursor.fetchall()
            return user_folders
        
    def getFolder(self, user_id, folder_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("SELECT * FROM folders WHERE user_id = ? AND folder_id = ?", (user_id, folder_id))
            folder_data = cursor.fetchone()
            return folder_data

auth = UserAuth()
doc = Documents()
folder = Folders()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
       username = request.form["username"]
       password = request.form["password"]
       return auth.validate_user(username, password)
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        return auth.register_user(username, password, email)
    return render_template("register.html")

@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    if "user_id" not in session: #safeguard route from not signed in users
        return redirect(url_for("login"))
    
    with sqlite3.connect("/app/database/database.db") as conn:
        cursor = conn.cursor() 
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute("SELECT username FROM users WHERE user_id=?", (session["user_id"],))
        user = cursor.fetchone()

        if user is None:
            return "User not found. Please log in again.", 404
            
        username = user[0]
    user_id = session["user_id"]
    return render_template("dashboard.html", username=username, recent_documents=doc.fetchDocs(user_id), user_folders = folder.fetchFolders(user_id))

@app.route("/logout")
def logout():
    user_id = session["user_id"]
    session.clear()  # Remove session from browser
    with sqlite3.connect("/app/database/database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        conn.commit()
    return redirect(url_for("home"))

@app.route("/get_folder_contents/<int:folder_id>")
def get_folder_contents(folder_id):
   if "user_id" not in session: #safeguard route from not signed in users
        return jsonify({"error": "Unauthorized"}), 401

   user_id = session["user_id"]
   folder_data = folder.getFolder(user_id, folder_id)

   if folder_data: # safeguard route from unauthorised users
        try:
            conn = sqlite3.connect("/app/database/database.db")
            cursor = conn.cursor()
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute("SELECT document_id, document_title FROM documents WHERE folder_id = ?", (folder_id,))
            documents = cursor.fetchall()
            conn.close()   
            return jsonify(documents)
        except Exception as e:
            print("ERROR in /get_folder_contents:", e)
            return jsonify({"error": str(e)}), 500
   else:
       return jsonify({"error": "Folder not found or unauthorized"}), 404

@app.route("/delete_document/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):

    # see if user is signed in
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    # check document belongs to user
    user_id = session["user_id"]
    with sqlite3.connect("/app/database/database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute("""
            SELECT  *
            FROM documents d
            JOIN folders f ON d.folder_id = f.folder_id
            WHERE f.user_id = ? AND d.document_id = ?
        """, (user_id, document_id))
        docu = cursor.fetchone()

        if not docu:
            return "Unauthorised", 403
        
        # delete document from database and return success
        cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
        conn.commit()
    return '', 204

@app.route("/delete_folder/<int:folder_id>", methods=["DELETE"])
def delete_folder(folder_id):
    # see if user is signed in
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    # check folder belongs to user
    user_id = session["user_id"]
    with sqlite3.connect("/app/database/database.db") as conn:
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM folders WHERE folder_id = ? and user_id = ?", (folder_id, user_id))
        fold = cursor.fetchone()

        if not fold:
            return "Unauthorised", 403
        
        cursor.execute("DELETE FROM folders WHERE folder_id = ?", (folder_id,))
        conn.commit()
    return '', 204

@app.route("/recent_documents/", methods=["GET"])
def recent_documents():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    recent_docs = doc.fetchDocs(user_id)
    # convert recent_docs into a serialisable dictionary

    recent_docs_serialisable = [
        {
            "document_id": doc[0],
            "document_title": doc[1],
            "last_edited": doc[2]
        }
        for doc in recent_docs
    ]

    return jsonify(recent_docs_serialisable)

@app.route("/create_document", methods=["POST"])
def create_document():
    if "user_id" not in session: #safeguard route from not signed in users
        return redirect(url_for("login"))
    user_id = session["user_id"]
    document_title = request.form["document_title"]
    folder_id = request.form["folder_id"]
    new_folder_name = request.form["new_folder_name"].strip()
    if not document_title:
        return "Document title is required", 400
    if folder_id == "new":
        if not new_folder_name.strip():
            return "New folder name is required", 400
    doc.createDoc(user_id, document_title, folder_id, new_folder_name)
    return redirect(url_for("dashboard"))

@app.route("/view_document/<int:document_id>")
def view_document(document_id):
   if "user_id" not in session: #safeguard route from not signed in users
        return redirect(url_for("login"))
   user_id = session["user_id"]
   document = doc.viewDoc(document_id, user_id)
   if document: # safeguard document from unauthorised users
        return render_template("view_document.html", document=document)
   else:
       return "Unauthorised or document not found", 404

@app.route("/save_document", methods=["POST"])
def save_document():
    data = request.get_json()
    document_id = data.get("document_id")
    document_text = data.get("document_text")

    if not document_id or document_text is None:
        return jsonify({"success": False, "error": "Invalid data"}), 404
    
    try:
        doc.saveDoc(document_text, document_id)
        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Error while saving document: {e}")
        return jsonify({"success": False, "message": str(e)})
    
@app.route("/extract_text", methods=["POST"])
def extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        image = Image.open(file)
        extracted_text = pytesseract.image_to_string(image)
        return jsonify({"text": extracted_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Current directory contents:", os.listdir("."))
    if not os.path.exists("/app/database/database.db"):
        print("⚠️ database.db NOT FOUND in current directory.")
    else:
        print("✅ database.db found.")
    app.run(host="0.0.0.0", port=5000, debug=True)

