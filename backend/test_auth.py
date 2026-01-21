import argparse
import requests
import subprocess
import time
import sys
import os
import signal
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, User

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser_automated",
    "email": "test_automated@example.com",
    "password": "securepassword123",
    "role": "user"
}

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_result(step: str, success: bool, details: str = ""):
    icon = "✅" if success else "❌"
    color = GREEN if success else RED
    print(f"{icon} {step}: {color}{'PASS' if success else 'FAIL'}{RESET} {details}")

def wait_for_server(max_retries=30):
    print(f"{CYAN}Waiting for server to start...{RESET}")
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print(f"{GREEN}Server is ready!{RESET}")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
        print(f".", end="", flush=True)
    print(f"\n{RED}Server failed to start.{RESET}")
    return False

def cleanup_user(username: str):
    print(f"{YELLOW}Cleaning up test user '{username}'...{RESET}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            db.delete(user)
            db.commit()
            print(f"{GREEN}User deleted.{RESET}")
        else:
            print(f"{CYAN}User not found (already clean).{RESET}")
    except Exception as e:
        print(f"{RED}Error cleanup: {e}{RESET}")
    finally:
        db.close()

def run_tests():
    session = requests.Session()
    results = {"passed": 0, "failed": 0}
    
    # 1. Health Check
    print(f"\n{CYAN}--- 1. Health Check ---{RESET}")
    try:
        res = session.get(f"{BASE_URL}/health")
        if res.status_code == 200:
            print_result("GET /health", True)
            results["passed"] += 1
        else:
            print_result("GET /health", False, f"Status: {res.status_code}")
            results["failed"] += 1
    except Exception as e:
        print_result("GET /health", False, str(e))
        results["failed"] += 1

    # 2. Register
    print(f"\n{CYAN}--- 2. Registration ---{RESET}")
    # Ensure clean state first
    cleanup_user(TEST_USER["username"])
    
    try:
        res = session.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if res.status_code == 201:
            data = res.json()
            if data["username"] == TEST_USER["username"]:
                print_result("POST /auth/register", True, f"ID: {data['id']}")
                results["passed"] += 1
            else:
                print_result("POST /auth/register", False, "Username mismatch")
                results["failed"] += 1
        else:
            print_result("POST /auth/register", False, f"Status: {res.status_code} - {res.text}")
            results["failed"] += 1
    except Exception as e:
        print_result("Register", False, str(e))
        results["failed"] += 1

    # 3. Login
    print(f"\n{CYAN}--- 3. Login ---{RESET}")
    access_token = None
    try:
        res = session.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        if res.status_code == 200:
            data = res.json()
            access_token = data.get("access_token")
            if access_token:
                print_result("POST /auth/login", True, "Token acquired")
                results["passed"] += 1
            else:
                print_result("POST /auth/login", False, "No access_token in response")
                results["failed"] += 1
        else:
            print_result("POST /auth/login", False, f"Status: {res.status_code} - {res.text}")
            results["failed"] += 1
    except Exception as e:
        print_result("Login", False, str(e))
        results["failed"] += 1

    # 4. Get Profile (Me)
    print(f"\n{CYAN}--- 4. Profile (Me) ---{RESET}")
    if access_token:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = session.get(f"{BASE_URL}/auth/me", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data["email"] == TEST_USER["email"]:
                    print_result("GET /auth/me", True, f"Verified as {data['username']}")
                    results["passed"] += 1
                else:
                    print_result("GET /auth/me", False, "Email mismatch")
                    results["failed"] += 1
            else:
                print_result("GET /auth/me", False, f"Status: {res.status_code}")
                results["failed"] += 1
        except Exception as e:
            print_result("Profile", False, str(e))
            results["failed"] += 1
    else:
        print_result("GET /auth/me", False, "Skipped (No token)")
        results["failed"] += 1

    # 5. Refresh Token
    print(f"\n{CYAN}--- 5. Refresh Token ---{RESET}")
    if access_token:
        # Wait to ensure token exp changes (JWT exp is in seconds)
        time.sleep(2)
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            res = session.post(f"{BASE_URL}/auth/refresh", headers=headers)
            if res.status_code == 200:
                data = res.json()
                new_token = data.get("access_token")
                if new_token and new_token != access_token:
                    print_result("POST /auth/refresh", True, "New token received")
                    results["passed"] += 1
                else:
                    print_result("POST /auth/refresh", False, "Invalid token response")
                    results["failed"] += 1
            else:
                print_result("POST /auth/refresh", False, f"Status: {res.status_code}")
                results["failed"] += 1
        except Exception as e:
            print_result("Refresh", False, str(e))
            results["failed"] += 1
    else:
        print_result("POST /auth/refresh", False, "Skipped (No token)")
        results["failed"] += 1

    # Summary
    print(f"\n{CYAN}=================================={RESET}")
    print(f"SUMMARY: {GREEN}{results['passed']} Passed{RESET}, {RED}{results['failed']} Failed{RESET}")
    print(f"{CYAN}=================================={RESET}")
    
    return results["failed"] == 0

def main():
    parser = argparse.ArgumentParser(description="Run API Authentication Tests")
    parser.add_argument("--cleanup", action="store_true", help="Delete test user after run")
    args = parser.parse_args()

    # Start Server
    print(f"{CYAN}Starting FastAPI server subprocess...{RESET}")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        if wait_for_server():
            success = run_tests()
        else:
            success = False
    finally:
        print(f"\n{CYAN}Stopping server...{RESET}")
        proc.terminate()
        proc.wait()
    
    if args.cleanup:
        cleanup_user(TEST_USER["username"])

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
