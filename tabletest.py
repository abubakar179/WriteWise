import sqlite3
import datetime
 
def test_database():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    
    # Enable foreign keys in sqlite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("\n===== USERS TABLE TESTS =====")
    
    # 1. Insert valid user data
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", ("bob", "password", "bob@example.com"))
        print("✅ Inserted valid user data")
    except Exception as e:
        print("❌ Failed to insert valid user data", e)
    
    # 2a. Reject null emails 
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", ("alice", "password",None))
        print("❌ Failed to reject null email")
    except Exception:
        print("✅ Null email correctly rejected")
    
    # 2b. Reject null usernames
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", (None, "password", "alice@example.com"))
        print("❌ Failed to reject null username")
    except Exception:
        print("✅ Null username correctly rejected")

    # 2c. Reject null passwords
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", ("alice", None, "alice@example.com"))
        print("❌ Failed to reject null password")
    except Exception:
        print("✅ Null password correctly rejected")

    # 3a. Reject duplicate usernames
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", ("bob", "password", "bob1@example.com"))
        print("❌ Failed to reject duplicate username")
    except Exception:
        print("✅ Duplicate username correctly rejected")

    # 3b. Reject duplicate emails
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", ("bob1", "password", "bob@example.com"))
        print("❌ Failed to reject duplicate email")
    except Exception:
        print("✅ Duplicate email correctly rejected")


    print("\n===== FOLDERS TABLE TESTS =====")

    # 1. Insert valid folder data
    cursor.execute("SELECT user_id FROM users WHERE username = ?", ("bob",))
    row = cursor.fetchone()
    if row is None:
        print("❌ Could not find dummy user to insert folder. Perhaps a previous test has failed?")
        print("Breaking program...")
        return
    user_id = row[0]
    try:
        cursor.execute("INSERT INTO folders (user_id, folder_title) VALUES (?, ?)", (user_id, "maths notes"))
        print("✅ Inserted valid folder data")
    except Exception as e:
        print("❌ Failed to insert valid folder data", e)

    # 2. Reject null folder names
    try:
        cursor.execute("INSERT INTO folders (user_id, folder_title) VALUES (?, ?)", (user_id, None))
        print("❌ Failed to reject null folder name")
    except Exception:
        print("✅ Rejected null folder name")

    # 3. Invalid user id rejected
    try:
        cursor.execute("INSERT INTO folders (user_id, folder_title) VALUES (?, ?)", (99999, "computing notes"))
        print("❌ Failed to reject invalid user id")
    except:
        print("✅ Rejected invalid user id")
    

    print("\n===== DOCUMENTS TABLE TESTS =====")

    # 1. Valid document data can be inserted
    try:
        cursor.execute("INSERT INTO documents (folder_id, document_title, document_text, last_edited) VALUES (?, ?, ?, ?)", (1, "Using calculus in kinematics", "insert sample encrypted text", datetime.datetime.now()))
        print("✅ Inserted valid document data")
    except Exception as e:
        print("❌ Failed to insert valid document data", e)
    
    # 2. Null document titles are rejected
    try:
        cursor.execute("INSERT INTO documents (folder_id, document_title, document_text, last_edited) VALUES (?, ?, ?, ?)", (1, None, "text", datetime.datetime.now()))
        print("❌ Failed to reject null document title")
    except Exception:
        print("✅ Null document title correctly rejected")
    
    # 3. Invalid folder ID rejected
    try:
        cursor.execute("INSERT INTO documents (folder_id, document_title, document_text, last_edited) VALUES (?, ?, ?, ?)", (99999, "Orphan Document", "text", datetime.datetime.now()))
        print("❌ Failed to reject invalid folder ID")
    except Exception:
        print("✅ Invalid folder ID correctly rejected")


    print("\n===== SESSIONS TABLE TESTS =====")

    # 1. Valid session data can be inserted
    try:
        cursor.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", ("session123", user_id, datetime.datetime.now() + datetime.timedelta(days=1)))
        print("✅ Inserted valid session data")
    except Exception as e:
        print("❌ Failed to insert valid session data", e)
    
    # 2a. Null expiry dates rejected
    try:
        cursor.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", ("session124", user_id, None))
        print("❌ Failed to reject null expiry date")
    except Exception:
        print("✅ Null expiry date correctly rejected")

    # 2b. Null user id rejected
    try:
        cursor.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", ("session125", None, datetime.datetime.now() + datetime.timedelta(days=1)))
        print("❌ Failed to reject null user id")
    except Exception:
        print("✅ Null user id correctly rejected")

    # 3. Invalid user id rejected
    try:
        cursor.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)", ("session126", 99999, datetime.datetime.now() + datetime.timedelta(days=1)))
        print("❌ Failed to reject invalid user id")
    except Exception:
        print("✅ Invalid user id correctly rejected")


    print("\n===== SECURITY TABLE TESTS =====")

    # 1. Valid security data can be inserted
    cursor.execute("SELECT document_id FROM documents WHERE document_title = ?", ("Using calculus in kinematics",))
    document_row = cursor.fetchone()
    if document_row:
        document_id = document_row[0]
        try:
            cursor.execute("INSERT INTO security (document_id, encryption_key, checksum) VALUES (?, ?, ?)", (document_id, "key123", "checksum123"))
            print("✅ Inserted valid security data")
        except Exception as e:
            print("❌ Failed to insert valid security data", e)
        
        # 2a. Null encryption key rejected
        try:
            cursor.execute("INSERT INTO security (document_id, encryption_key, checksum) VALUES (?, ?, ?)", (document_id, None, "checksum124"))
            print("❌ Failed to reject null encryption key")
        except Exception:
            print("✅ Null encryption key correctly rejected")

        # 2b. Null checksum rejected
        try:
            cursor.execute("INSERT INTO security (document_id, encryption_key, checksum) VALUES (?, ?, ?)", (document_id, "key124", None))
            print("❌ Failed to reject null checksum")
        except Exception:
            print("✅ Null checksum correctly rejected")

        # 3. Invalid document id rejected
        try:
            cursor.execute("INSERT INTO security (document_id, encryption_key, checksum) VALUES (?, ?, ?)", (99999, "key999", "checksum999"))
            print("❌ Failed to reject invalid document id")
        except Exception:
            print("✅ Invalid document id correctly rejected")

    else:
        print("❌ Could not find document to insert security data. Document test might have failed earlier.")
    

    print("\n===== USERS CASCADE DELETE TEST =====")
    # Cascade delete test
    try:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        cursor.execute("SELECT * FROM folders WHERE user_id = ?", (user_id,))
        folders_left = cursor.fetchall()
        cursor.execute("SELECT * FROM documents WHERE folder_id = ?", (1,))
        documents_left = cursor.fetchall()
        cursor.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,))
        sessions_left = cursor.fetchall()

        if not folders_left and not documents_left and not sessions_left:
            print("✅ Cascade deletion worked (folders, documents, sessions removed)")
        else:
            print("❌ Cascade deletion did not clean up related data")
    except Exception as e:
        print("❌ Cascade delete test failed:", e)

    connection.commit()
    connection.close()
    print("\n🎉 ALL TESTS COMPLETED 🎉")

if __name__ == "__main__":
    test_database()