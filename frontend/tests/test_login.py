import re
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8502"

def test_login_failure(page: Page):
    page.goto(BASE_URL)
    
    # Fill invalid credentials using generic selectors (avoiding emoji issues)
    # Streamlit inputs usually have aria-label
    page.get_by_label(re.compile("Usuario")).fill("wronguser")
    page.get_by_label(re.compile("Contraseña")).fill("wrongpass")
    
    # Click button containing text "Iniciar"
    page.get_by_role("button", name=re.compile("Iniciar")).click()
    
    # Expect error message
    expect(page.get_by_text(re.compile("incorrectos"))).to_be_visible()

def test_login_success(page: Page):
    page.goto(BASE_URL)
    
    page.get_by_label(re.compile("Usuario")).fill("admin")
    page.get_by_label(re.compile("Contraseña")).fill("admin123")
    
    page.get_by_role("button", name=re.compile("Iniciar")).click()
    
    # Expect to see Chat interface or Sidebar
    # Sidebar should contain user info "👤 admin"
    # Using regex to match "admin" inside a heading
    expect(page.get_by_role("heading", name=re.compile("admin"))).to_be_visible(timeout=15000)
    
    # Logout for cleanup
    page.get_by_role("button", name="🚪 Cerrar Sesión").click()
    expect(page.get_by_role("heading", name=re.compile("Commercial RAG"))).to_be_visible()
