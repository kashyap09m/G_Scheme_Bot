
import os
import pandas as pd
import ast
import json
import requests
import re
from dotenv import load_dotenv

def find_latest_file(folder_path: str) -> str | None:
    """Finds the most recently modified file in a directory."""
    if not os.path.exists(folder_path):
        print(f"Error: The directory '{folder_path}' was not found.")
        return None
    
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not files:
        return None
        
    return max(files, key=os.path.getmtime)

def extract_raw_documents(csv_path: str) -> list[str]:
    """
    Reads a CSV, extracts and cleans documents, handling slash-separated entries
    and performing minimal cleanup before passing to the LLM.
    """
    try:
        df = pd.read_csv(csv_path)
        if 'Required Documents' not in df.columns:
            print("Error: 'Required Documents' column not found in the CSV.")
            return []

        all_docs = set()
        for item in df['Required Documents'].dropna():
            try:
                doc_list = ast.literal_eval(item)
                if isinstance(doc_list, list):
                    for d in doc_list:
                        if isinstance(d, str):
                            sub_docs = [s.strip() for s in d.split('/')]
                            for doc_name in sub_docs:
                                clean_doc = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', doc_name.strip())
                                if clean_doc:
                                    all_docs.add(clean_doc)
            except (ValueError, SyntaxError):
                if isinstance(item, str) and item.strip():
                    sub_docs = [s.strip() for s in item.split('/')]
                    for doc_name in sub_docs:
                        clean_doc = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', doc_name.strip())
                        if clean_doc:
                            all_docs.add(clean_doc)
        
        return sorted(list(all_docs))
        
    except Exception as e:
        print(f"An error occurred while reading the CSV: {e}")
        return []

def get_clean_document_list_from_llm(messy_list: list, config: dict) -> list[str]:
    """Uses an LLM to intelligently filter and normalize a list of strings to get only document names."""
    print("Asking LLM to smartly select and consolidate document names from the list...")

    messy_list_str = "\n".join(f"- {item}" for item in messy_list)
    
    # Final, refined prompt for dynamic, semantic-based consolidation
    prompt = f"""
    You are an expert in legal and administrative documents. Your task is to analyze a list of strings and provide a single, clean list of official document names. Your response must follow these strict rules to be accurate:

1.  **Consolidate by Meaning:** Group documents that refer to the same concept into a single, canonical name.
    -   **Example:** "Age Proof", "Age Certificate", and "Proof of Age" should all be consolidated into **"Age Proof Certificate"**.
    -   **Example:** "Aadhaar Card" and "Aadhar Card" should be consolidated into **"Aadhaar Card"**.
    -   **Example:** "Domicile Certificate" and "Residential Certificate" should be consolidated into **"Domicile Certificate"**.

2.  **Handle Ambiguous Terms:** If a term like "Marksheet" is not clearly specified (e.g., "10th/12th Marks Sheet"), return it as-is without making an assumption.

3.  **Filter Irrelevant Text:** Ignore all strings that are not a document. This includes conditions, instructions, notes, and general descriptions. Also, ignore special characters, punctuation, and leading/trailing numbers.
    -   **Example:** "Applicant should not be a defaulter." -> Ignore.
    -   **Example:** "Death Certificate of the farmer" -> Return **"Death Certificate"**.
    -   **Example:** "noaminne has some symbol" -> Ignore.
    
4.  **Normalize Format:** Ensure the final output is capitalized consistently (e.g., "Bank Passbook" instead of "bank passbook").

Return your response as a single, valid JSON object with one key: "documents". This key should hold a list of the cleaned, unique document names.

Here is the list to process:
---
{messy_list_str}
---
    """
    
    payload = {
        "model": config["llm_model"],
        "prompt": prompt,
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(config["llm_url"], json=payload, timeout=300)
        if response.status_code == 200:
            ollama_response = response.json()
            cleaned_data = json.loads(ollama_response.get('response', '{}'))
            cleaned_list = cleaned_data.get('documents', [])
            
            if isinstance(cleaned_list, list):
                unique_cleaned_list = sorted(list(set(cleaned_list)))
                print(f"✅ LLM successfully identified {len(unique_cleaned_list)} unique documents.")
                return unique_cleaned_list
            else:
                print("❌ LLM did not return a list. Cleaning failed.")
                return []
        else:
            print(f"❌ Error: LLM API returned status {response.status_code}. Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ An exception occurred while communicating with the LLM: {e}")
        return []

def main():
    """Main function to run the smart document cleaning pipeline."""
    load_dotenv()
    config = {
        "llm_url": os.getenv("OLLAMA_API_URL",'http://192.168.0.109:11434/api/generate'),
        "llm_model": os.getenv("OLLAMA_MODEL_NAME",'gemma3:4b'),
    }
    
    if not config["llm_url"] or not config["llm_model"]:
        print("Error: OLLAMA_API_URL and OLLAMA_MODEL_NAME must be set in your .env file.")
        return

    input_folder = 'process_csv'
    output_folder = 'document_csv'
    output_path = os.path.join(output_folder, 'cleaned_unique_document_list.csv')

    os.makedirs(output_folder, exist_ok=True)

    latest_scheme_csv = find_latest_file(input_folder)
    if not latest_scheme_csv:
        latest_scheme_csv = 'processed_schemes.csv'
        if not os.path.exists(latest_scheme_csv):
            print(f"Error: The file '{latest_scheme_csv}' was not found.")
            return

    print(f"Reading from file: {os.path.basename(latest_scheme_csv)}")
    raw_docs = extract_raw_documents(latest_scheme_csv)

    if not raw_docs:
        print("No document data found to process.")
        return

    print(f"Found {len(raw_docs)} raw unique strings to clean.")
    
    clean_docs = get_clean_document_list_from_llm(raw_docs, config)

    if not clean_docs:
        print("No documents were selected by the LLM. Exiting.")
        return

    try:
        docs_df = pd.DataFrame(clean_docs, columns=['Cleaned Document Name'])
        docs_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nSuccessfully saved the clean list of {len(clean_docs)} documents to '{output_path}'.")
    except Exception as e:
        print(f"An error occurred while saving the final file: {e}")

if __name__ == "__main__":
    main()