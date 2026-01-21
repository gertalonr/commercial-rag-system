import requests
import json
import sys
import os
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDS = {"username": "admin", "password": "cambiar-en-produccion"}
TEST_USER = {"username": "testuser_api", "email": "test_api@example.com", "password": "testpassword123"}
TEST_ADMIN_USER = {"username": "new_admin_api", "email": "new_admin_api@example.com", "password": "adminpass123", "role": "admin"}
TEST_DOC_FILENAME = "test_upload_api.txt"

# State
tokens = {"user": None, "admin": None}
ids = {"user_id": None, "conversation_id": None, "new_user_id": None}
stats = {"total": 0, "passed": 0, "failed": 0}

def print_header(title):
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def log_result(test_name, success, detail=None):
    stats["total"] += 1
    if success:
        stats["passed"] += 1
        print(f"✅ PASS: {test_name}")
    else:
        stats["failed"] += 1
        print(f"❌ FAIL: {test_name}")
        if detail:
            print(f"   Error: {detail}")

def create_dummy_file():
    with open(TEST_DOC_FILENAME, "w") as f:
        f.write("This is a test document for the API upload endpoint.")

def cleanup_dummy_file():
    if os.path.exists(TEST_DOC_FILENAME):
        os.remove(TEST_DOC_FILENAME)

def request(method, endpoint, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        return response
    except Exception as e:
        return None

# ==========================================
# TESTS
# ==========================================

def run_tests():
    create_dummy_file()
    print_header("AUTENTICACIÓN")

    # 1. Register User
    res = request("POST", "/auth/register", json=TEST_USER)
    if res and res.status_code == 201:
        log_result("1. Register User", True)
        ids["user_id"] = res.json()["id"]
    elif res and res.status_code == 400 and "already registered" in res.text:
         # If already exists, we login to get the ID later
         log_result("1. Register User (User exists, proceeding)", True)
    else:
        log_result("1. Register User", False, res.text if res else "Connection Error")

    # 2. Login User
    res = request("POST", "/auth/login", json={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    if res and res.status_code == 200:
        tokens["user"] = res.json()["access_token"]
        log_result("2. Login User", True)
    else:
        log_result("2. Login User", False, res.text if res else "Connection Error")

    # 3. Login Admin
    # Note: Assuming Admin already exists from init_rag system
    res = request("POST", "/auth/login", json=ADMIN_CREDS)
    if res and res.status_code == 200:
        tokens["admin"] = res.json()["access_token"]
        log_result("3. Login Admin", True)
    else:
        log_result("3. Login Admin", False, res.text if res else "Connection Error")

    # 4. Verify Token (Me) - User context
    if tokens["user"]:
        res = request("GET", "/auth/me", token=tokens["user"])
        if res and res.status_code == 200:
            log_result("4. Verify Token (Me)", True)
            if not ids["user_id"]: # Capture if we missed it in register
                 ids["user_id"] = res.json()["id"]
        else:
            log_result("4. Verify Token (Me)", False, res.text if res else "Connection Error")
    else:
        log_result("4. Verify Token (Me)", False, "Skipped (No Token)")

    # ---------------------------------------------------------
    print_header("CONVERSACIONES")

    # 5. Create Conversation
    if tokens["user"]:
        res = request("POST", "/conversations/create", token=tokens["user"], json={"title": "Test Chat API"})
        if res and res.status_code == 201:
            log_result("5. Create Conversation", True)
            ids["conversation_id"] = res.json()["id"]
        else:
            log_result("5. Create Conversation", False, res.text if res else "Connection Error")
    else:
        log_result("5. Create Conversation", False, "Skipped")

    # 6. List Conversations
    if tokens["user"]:
        res = request("GET", "/conversations", token=tokens["user"])
        if res and res.status_code == 200 and isinstance(res.json(), list):
            log_result("6. List Conversations", True)
        else:
             log_result("6. List Conversations", False, res.text if res else "Connection Error")
    else:
        log_result("6. List Conversations", False, "Skipped")

    # 7. Get Conversation
    if tokens["user"] and ids["conversation_id"]:
        res = request("GET", f"/conversations/{ids['conversation_id']}", token=tokens["user"])
        if res and res.status_code == 200:
             log_result("7. Get Conversation", True)
        else:
             log_result("7. Get Conversation", False, res.text if res else "Connection Error")
    else:
        log_result("7. Get Conversation", False, "Skipped")

    # 8. Update Title
    if tokens["user"] and ids["conversation_id"]:
        res = request("PUT", f"/conversations/{ids['conversation_id']}/title", token=tokens["user"], json={"title": "Updated Title API"})
        if res and res.status_code == 200 and res.json()["title"] == "Updated Title API":
             log_result("8. Update Conversation Title", True)
        else:
             log_result("8. Update Conversation Title", False, res.text if res else "Connection Error")
    else:
        log_result("8. Update Conversation Title", False, "Skipped")

    # 9. RAG Query (Auto Create)
    # Using a simple query
    if tokens["user"]:
        print("   Sending Query 1 (wait)...")
        res = request("POST", "/query", token=tokens["user"], json={"question": "Hola, ¿quién eres?"})
        if res and res.status_code == 200:
             log_result("9. RAG Query (Auto-Create)", True)
             # This created a new conversation, we can optionally track it but we have one already
        else:
             log_result("9. RAG Query (Auto-Create)", False, res.text if res else "Connection Error")
    else:
        log_result("9. RAG Query", False, "Skipped")

    # 10. RAG Query (Existing ID)
    if tokens["user"] and ids["conversation_id"]:
        print("   Sending Query 2 (wait)...")
        res = request("POST", "/query", token=tokens["user"], json={"question": "Dime un resumen muy breve.", "conversation_id": ids["conversation_id"]})
        if res and res.status_code == 200:
             log_result("10. RAG Query (Existing ID)", True)
        else:
             log_result("10. RAG Query (Existing ID)", False, res.text if res else "Connection Error")
    else:
        log_result("10. RAG Query (Existing ID)", False, "Skipped")

    # 11. Verify Messages Saved
    if tokens["user"] and ids["conversation_id"]:
        res = request("GET", f"/conversations/{ids['conversation_id']}", token=tokens["user"])
        if res and res.status_code == 200:
            msgs = res.json().get("messages", [])
            # Should have at least User msg + Assistant msg
            if len(msgs) >= 2:
                log_result("11. Verify Messages Saved", True)
            else:
                 log_result("11. Verify Messages Saved", False, f"Not enough messages found: {len(msgs)}")
        else:
             log_result("11. Verify Messages Saved", False, res.text if res else "Connection Error")
    else:
        log_result("11. Verify Messages Saved", False, "Skipped")

    # ---------------------------------------------------------
    print_header("ADMIN - USUARIOS")

    # 12. List Users
    if tokens["admin"]:
        res = request("GET", "/admin/users", token=tokens["admin"])
        if res and res.status_code == 200:
            log_result("12. List Users (Admin)", True)
        else:
             log_result("12. List Users (Admin)", False, res.text if res else "Connection Error")
    else:
         log_result("12. List Users", False, "Skipped")

    # 13. Create New User (Admin)
    if tokens["admin"]:
        res = request("POST", "/admin/users/create", token=tokens["admin"], json=TEST_ADMIN_USER)
        if res and res.status_code == 201:
             log_result("13. Create User (Admin)", True)
             ids["new_user_id"] = res.json()["id"]
        elif res and res.status_code == 400: # Already exists
             log_result("13. Create User (Admin) - Exists", True)
             # Try to find ID from list
             res_list = request("GET", "/admin/users", token=tokens["admin"])
             for u in res_list.json():
                 if u["username"] == TEST_ADMIN_USER["username"]:
                     ids["new_user_id"] = u["id"]
                     break
        else:
             log_result("13. Create User (Admin)", False, res.text if res else "Connection Error")
    else:
         log_result("13. Create User", False, "Skipped")

    # 14. Update Password
    if tokens["admin"] and ids["new_user_id"]:
        res = request("PUT", f"/admin/users/{ids['new_user_id']}/password", token=tokens["admin"], json={"new_password": "newpassword123"})
        if res and res.status_code == 200:
            log_result("14. Update Password (Admin)", True)
        else:
            log_result("14. Update Password (Admin)", False, res.text if res else "Connection Error")
    else:
         log_result("14. Update Password", False, "Skipped")

    # 15. Toggle Active
    if tokens["admin"] and ids["new_user_id"]:
        res = request("PUT", f"/admin/users/{ids['new_user_id']}/toggle-active", token=tokens["admin"])
        if res and res.status_code == 200:
            log_result("15. Toggle Active (Admin)", True)
        else:
            log_result("15. Toggle Active (Admin)", False, res.text if res else "Connection Error")
    else:
         log_result("15. Toggle Active", False, "Skipped")

    # 16. Delete User
    if tokens["admin"] and ids["new_user_id"]:
        res = request("DELETE", f"/admin/users/{ids['new_user_id']}", token=tokens["admin"])
        if res and res.status_code == 204:
            log_result("16. Delete User (Admin)", True)
        else:
            log_result("16. Delete User (Admin)", False, res.text if res else "Connection Error")
    else:
         log_result("16. Delete User", False, "Skipped")

    # ---------------------------------------------------------
    print_header("ADMIN - DOCUMENTOS")

    # 17. Upload Document
    if tokens["admin"]:
        with open(TEST_DOC_FILENAME, "rb") as f:
            files = {"files": (TEST_DOC_FILENAME, f, "text/plain")}
            res = request("POST", "/admin/documents/upload", token=tokens["admin"], files=files)
        
        if res and res.status_code == 201:
            log_result("17. Upload Document", True)
        else:
            log_result("17. Upload Document", False, res.text if res else "Connection Error")
    else:
        log_result("17. Upload Document", False, "Skipped")

    # 18. List Documents
    if tokens["admin"]:
        res = request("GET", "/admin/documents", token=tokens["admin"])
        if res and res.status_code == 200:
            docs = res.json()
            found = any(d['filename'] == TEST_DOC_FILENAME for d in docs)
            if found:
                log_result("18. List Documents", True)
            else:
                 log_result("18. List Documents", False, "Uploaded file not found in list")
        else:
             log_result("18. List Documents", False, res.text if res else "Connection Error")
    else:
        log_result("18. List Documents", False, "Skipped")

    # 19. Reindex
    if tokens["admin"]:
        print("   Reindexing (wait)...")
        res = request("POST", "/admin/documents/reindex", token=tokens["admin"])
        if res and res.status_code == 200:
             log_result("19. Reindex Documents", True)
        else:
             log_result("19. Reindex Documents", False, res.text if res else "Connection Error")
    else:
        log_result("19. Reindex Documents", False, "Skipped")

    # 20. Delete Document
    if tokens["admin"]:
        res = request("DELETE", f"/admin/documents/{TEST_DOC_FILENAME}", token=tokens["admin"])
        if res and res.status_code == 204:
             log_result("20. Delete Document", True)
        else:
             log_result("20. Delete Document", False, res.text if res else "Connection Error")
    else:
        log_result("20. Delete Document", False, "Skipped")

    # ---------------------------------------------------------
    print_header("ADMIN - ESTADÍSTICAS")

    # 21. User Usage
    if tokens["admin"] and ids["user_id"]:
        res = request("GET", f"/admin/usage/user/{ids['user_id']}", token=tokens["admin"])
        if res and res.status_code == 200:
             log_result("21. User Usage Stats", True)
        else:
             log_result("21. User Usage Stats", False, res.text if res else "Connection Error")
    else:
        log_result("21. User Usage Stats", False, "Skipped")

    # 22. Global Usage
    if tokens["admin"]:
        res = request("GET", "/admin/usage/global", token=tokens["admin"])
        if res and res.status_code == 200:
             log_result("22. Global Usage Stats", True)
        else:
             log_result("22. Global Usage Stats", False, res.text if res else "Connection Error")
    else:
        log_result("22. Global Usage Stats", False, "Skipped")

    # 23. Realtime Usage
    if tokens["admin"]:
        res = request("GET", "/admin/usage/realtime", token=tokens["admin"])
        if res and res.status_code == 200:
             log_result("23. Realtime Usage Stats", True)
        else:
             log_result("23. Realtime Usage Stats", False, res.text if res else "Connection Error")
    else:
        log_result("23. Realtime Usage Stats", False, "Skipped")

    # ---------------------------------------------------------
    cleanup_dummy_file()
    
    success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    
    print("\n" + "┌" + "─"*28 + "┐")
    print("│ TEST RESULTS               │")
    print("├" + "─"*28 + "┤")
    print(f"│ Total: {stats['total']:<19} │")
    print(f"│ Passed: {stats['passed']:<10} ✅       │")
    print(f"│ Failed: {stats['failed']:<10} ❌       │")
    print(f"│ Success Rate: {success_rate:>5.1f}%        │")
    print("└" + "─"*28 + "┘")

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        cleanup_dummy_file()
        print("\nTests interrupted.")
