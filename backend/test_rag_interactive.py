import argparse
import sys
import os

# Add parent directory to path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_engine import ClaudeRAG

def main():
    parser = argparse.ArgumentParser(description="Interactive RAG Test Console")
    parser.add_argument("--verbose", action="store_true", help="Show context used")
    args = parser.parse_args()

    print("Initializing RAG Engine...")
    try:
        rag = ClaudeRAG()
        print("✅ RAG Engine Ready.")
    except Exception as e:
        print(f"❌ Error initializing RAG: {e}")
        return

    print("\nCommands: 'exit', 'quit', 'reindex'")
    print("-" * 50)

    while True:
        try:
            query = input("\n📝 Query > ").strip()
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if query.lower() == 'reindex':
                print("🔄 Re-indexing documents...")
                stats = rag.reindex_all()
                print(f"✅ Stats: {stats}")
                continue

            print("🤔 Thinking...")
            result = rag.ask(query)

            if "error" in result and result.get("error"):
                print(f"❌ Error: {result['error']}")
                continue

            print("\n🤖 Claude:")
            print(result['answer'])
            
            print("\n" + "-"*30)
            print(f"📚 Sources: {result['sources']}")
            print(f"💰 Cost: ${result['cost_usd']} (In: {result['tokens_input']}, Out: {result['tokens_output']})")
            
            if args.verbose and result.get('context_used'):
                print("\n🔍 Context Used:")
                for i, ctx in enumerate(result['context_used']):
                    print(f"[{i+1}] {ctx.get('source')} (Score: {ctx.get('similarity_score'):.4f})")
                    print(f"    Content: {ctx.get('content')[:200]}...")
                    print("-" * 10)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
