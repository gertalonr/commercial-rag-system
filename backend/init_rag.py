import argparse
import logging
import sys
import os

# Add parent directory to path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sqlalchemy.orm import Session

from backend.database import init_db, SessionLocal, User, UserRole
from backend.config import settings
from backend.rag_engine import ClaudeRAG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def init_database():
    logger.info("Initializing database tables...")
    try:
        init_db()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        sys.exit(1)

from backend.auth import create_initial_admin

def create_admin_user():
    logger.info("Checking admin user...")
    db = SessionLocal()
    try:
        create_initial_admin(db)
        
        print("\n" + "="*50)
        print("👤 Admin User Configured")
        print("="*50)
        print(f"Email:    {settings.ADMIN_EMAIL}")
        print(f"Username: {settings.ADMIN_USERNAME}")
        print(f"Password: {settings.ADMIN_PASSWORD}")
        print("\n⚠️  WARNING: SECURITY RISK")
        print("This is the default password from your configuration.")
        print("Please change it immediately after First Login!")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
    finally:
        db.close()

def index_documents():
    logger.info("Starting document indexing...")
    try:
        rag = ClaudeRAG()
        # Default path data/documents relative to project root
        doc_path = "data/documents"
        stats = rag.reindex_all(folder_path=doc_path)
        logger.info(f"Indexing complete. Stats: {stats}")
    except Exception as e:
        logger.error(f"Error indexing documents: {e}")

def run_test_query(query: str):
    logger.info(f"Running test query: '{query}'")
    try:
        rag = ClaudeRAG()
        result = rag.ask(query)
        
        print("\n" + "="*50)
        print("🤖 RAG Response")
        print("="*50)
        print(result.get('answer'))
        print("\n" + "-"*30)
        print(f"📚 Sources: {result.get('sources')}")
        print(f"💰 Cost: ${result.get('cost_usd')}")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Error running test query: {e}")

def main():
    parser = argparse.ArgumentParser(description="Commercial RAG System Initialization Tool")
    
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables")
    parser.add_argument("--create-admin", action="store_true", help="Create default admin user")
    parser.add_argument("--index-docs", action="store_true", help="Index documents from data/documents")
    parser.add_argument("--test-query", type=str, help="Run a test query")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
        
    if args.init_db:
        init_database()
        
    if args.create_admin:
        create_admin_user()
        
    if args.index_docs:
        index_documents()
        
    if args.test_query:
        run_test_query(args.test_query)

if __name__ == "__main__":
    main()
