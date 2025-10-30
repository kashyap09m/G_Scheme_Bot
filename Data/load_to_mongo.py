import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import ast
from datetime import datetime

# --- Helper Functions ---

def get_unprocessed_files(folder_path: str, log_file_path: str) -> list[str]:
    """Finds all CSV files in a directory that are NOT listed in the log file."""
    if not os.path.exists(folder_path):
        print(f"  - ❗️ Warning: Directory '{folder_path}' not found. Skipping.")
        return []
    
    processed_files = set()
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as f:
            processed_files = set(line.strip() for line in f)
            
    all_csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    unprocessed_files = [os.path.join(folder_path, f) for f in all_csv_files if f not in processed_files]
    return unprocessed_files

def mark_file_as_processed(log_file_path: str, filename: str):
    """Appends a filename to the log file."""
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')

def safe_eval_list(s):
    """Safely evaluates a string that looks like a list."""
    if isinstance(s, str) and s.startswith('[') and s.endswith(']'):
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return s
    return s

def process_folder(folder_path: str, db: MongoClient):
    """
    Finds and processes all new CSV files within a given folder.
    """
    print(f"\n===== PROCESSING FOLDER: '{folder_path}' =====")
    log_file = os.path.join(folder_path, 'processed_files.log')
    
    files_to_process = get_unprocessed_files(folder_path, log_file)

    if not files_to_process:
        print("  - ✅ No new CSV files to process in this folder.")
        return

    print(f"  - Found {len(files_to_process)} new CSV files to load.")

    for csv_path in files_to_process:
        filename = os.path.basename(csv_path)
        collection_name = os.path.splitext(filename)[0]
        
        print(f"\n  --- Processing '{filename}' ---")
        print(f"  Target collection: '{collection_name}'")

        try:
            df = pd.read_csv(csv_path)
            df['timestamp'] = datetime.now()
            
            for col in df.columns:
                if df[col].astype(str).str.startswith('[').any():
                    df[col] = df[col].apply(safe_eval_list)
            
            records = df.to_dict('records')
            print(f"    - Read and prepared {len(records)} records.")

            collection = db[collection_name]
            if len(records) > 0:
                collection.insert_many(records)
                print(f"    - ✅ Successfully inserted {len(records)} documents.")
            else:
                print("    - ❕ CSV is empty. No documents inserted.")

            mark_file_as_processed(log_file, filename)
            print(f"    - ✅ Logged '{filename}' as processed.")

            os.remove(csv_path)
            print(f"    - ✅ Deleted source file '{filename}'.")

        except Exception as e:
            print(f"    - ❌ An error occurred while processing '{filename}': {e}")
            print("    - ❗️ This file will be skipped and retried on the next run.")
            continue

def main():
    """
    Main function to orchestrate loading CSVs from multiple folders to MongoDB.
    """
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    if not all([mongo_uri, db_name]):
        print("❌ Error: Missing MONGO_URI or MONGO_DB_NAME in .env file.")
        return

    # --- List of folders to process in order ---
    folders_to_process = ['translate_csv', 'final_document_csv']

    try:
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        db = client[db_name]
        print("✅ Successfully connected to MongoDB server.")
    except ConnectionFailure as e:
        print(f"❌ Error: Could not connect to MongoDB. Details: {e}")
        return

    for folder in folders_to_process:
        process_folder(folder, db)

    print("\n--- All new files from specified folders have been processed. ---")
    client.close()

if __name__ == "__main__":
    main()