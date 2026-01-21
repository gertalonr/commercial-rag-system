import re
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8502"

def test_app_loads(page: Page):
    try:
        page.goto(BASE_URL)
    except Exception:
        # Retry once if connection fails immediately (sometimes local server needs warm up)
        page.wait_for_timeout(1000)
        page.goto(BASE_URL)
        
    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Commercial RAG System"))
    
    # Check if we are either at login or main app
    # Since we are not authenticated initially, we expect Login page elements
    # Using a generic selector that should exist in Login Page
    expect(page.get_by_role("heading", name="Iniciar Sesión")).to_be_visible()
