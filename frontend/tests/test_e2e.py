import re
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8502"

def test_chat_interaction(page: Page):
    # Login first
    page.goto(BASE_URL)
    
    # Check if already logged in (cookies)
    # Use heading locator with regex for user info
    if not page.get_by_role("heading", name=re.compile("admin")).is_visible():
        page.get_by_label(re.compile("Usuario")).fill("admin")
        page.get_by_label(re.compile("Contraseña")).fill("admin123")
        page.get_by_role("button", name=re.compile("Iniciar")).click()
        expect(page.get_by_role("heading", name=re.compile("admin"))).to_be_visible(timeout=10000)

    # Now verify Chat Interface
    # Check title "Chat - Consultas Empresariales" matches partially
    expect(page.get_by_role("heading", name=re.compile("Chat"))).to_be_visible()
    
    # Send a message
    # Streamlit chat_input locator can be tricky. Usually it's a textarea.
    chat_input = page.get_by_placeholder("Escribe tu pregunta aquí...")
    expect(chat_input).to_be_visible()
    
    chat_input.fill("Hola, ¿qué documentos tienes?")
    page.keyboard.press("Enter")
    
    # Check for user message appearance
    expect(page.get_by_text("Hola, ¿qué documentos tienes?")).to_be_visible()
    
    # Check for a spinner or waiting state if possible?
    # Streamlit spinner usually has text "Pensando..." based on our code
    # We might miss it if it's too fast, so we check for Assistant response eventual appearance
    
    # Since we don't know exact response, we check if ANY assistant message appears with text
    # or just check that "Fuentes utilizadas" or generic text appears.
    # We can check for the Assistant icon or role
    
    # This might fail if RAG is broken, which is good testing.
    # We'll wait for a reasonable timeout
    expect(page.get_by_role("img", name="avatar")).to_have_count(2) # User + Assistant (at least) - might vary based on icon implementation
    
    # Alternatively, check for "Fuentes utilizadas" which logic says should appear if docs are found
    # accessing RAG results. Or just check that last message is not user's message.
