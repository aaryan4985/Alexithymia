import sys
import os
import argparse
import subprocess

from query_engine import AlexiEngine
from memory import Memory
from ingest_json import ingest

def main():
    parser = argparse.ArgumentParser(description="Alexi Vale - RAG CLI")
    parser.add_argument("--volume", type=int, help="Filter by volume number")
    parser.add_argument("--chapter", type=str, help="Filter by chapter number/name")
    parser.add_argument("--novel", type=str, help="Filter by novel name")
    
    args = parser.parse_args()
    
    filters_dict = {}
    if args.volume is not None:
        filters_dict["volume"] = args.volume
    if args.chapter is not None:
        filters_dict["chapter"] = args.chapter
    if args.novel is not None:
        filters_dict["novel"] = args.novel

    print("Welcome to the Alexi Vale System.")
    print("---------------------------------")
    choice = input("Do you want to (1) Scrape and ingest a new novel, or (2) Skip to Chat? [1/2]: ").strip()
    
    if choice == '1':
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scraper_script = os.path.join(parent_dir, "webscrapper.py")
        
        if os.path.exists(scraper_script):
            print("\nLaunching Web Scraper...")
            # Run the scraper natively and let the user interact with its inputs
            subprocess.run([sys.executable, scraper_script], cwd=parent_dir)
            print("\nScraping finished. Ingesting data into ChromaDB...")
            ingest()
        else:
            print("Scraper not found at parent directory. Skipping to chat...")
    
    print("\nInitializing Alexi Vale Query Engine...")
    try:
        engine = AlexiEngine()
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return

    memory = Memory()
    
    print("\nAlexi Vale is ready. Type 'quit' to exit.")
    if filters_dict:
        print(f"Active Filters: {filters_dict}")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ['quit', 'exit']:
                print("Alexi: Goodbye.")
                break
                
            if not user_input.strip():
                continue
                
            history_str = memory.get_history_string()
            
            response = engine.query(
                user_query=user_input, 
                history_context=history_str,
                filters_dict=filters_dict
            )
            
            if "not present in the retrieved material" not in response:
                 memory.add_interaction(user_input, response)
            
            print(f"Alexi: {response}")
            
        except KeyboardInterrupt:
            print("\nAlexi: Goodbye.")
            break
        except Exception as e:
            print(f"Alexi: An error occurred: {e}")

if __name__ == "__main__":
    main()
