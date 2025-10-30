import os
import pandas as pd
import json
import requests
import re
import time
from dotenv import load_dotenv

# --- Step 1: Get Canonical Name (Single-purpose LLM call) ---
def get_canonical_document_name(doc_name: str, config: dict) -> str:
    """
    Uses an LLM to identify the canonical name for a given document.
    """
    prompt = f"""
    You are an expert on administrative and legal documents in India. Your task is to identify the most common and canonical document name for the term "{doc_name}".

    If the term is a general category (e.g., "Proof of Age" or "Marksheet"), return the name of a common specific document that fits this category (e.g., "Aadhaar Card" or "10th/12th Marks Sheet").

    If the term is already a specific document name, return it as-is. Do not provide any other text or conversational filler. Return only the canonical name.

    Example:
    Input: "Proof of Age" -> Output: "Aadhaar Card"
    Input: "Domicile Certificate" -> Output: "Domicile Certificate"
    Input: "Aadhar Card" -> Output: "Aadhaar Card"

    Return your response as a single, valid JSON object with one key: "canonical_name".
    """
    
    payload = {
        "model": config["llm_model"],
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.2}
    }
    
    try:
        response = requests.post(config["llm_url"], json=payload, timeout=300)
        if response.status_code == 200:
            ollama_response = response.json()
            json_match = re.search(r'\{.*\}', ollama_response.get('response', ''), re.DOTALL)
            if json_match:
                canonical_name = json.loads(json_match.group(0)).get('canonical_name')
                if canonical_name and isinstance(canonical_name, str):
                    return canonical_name
    except Exception as e:
        print(f"❌ Error getting canonical name for '{doc_name}': {e}")
        
    return doc_name

# --- Step 2: Get Details (Single-purpose LLM call) ---
def get_document_details(doc_name: str, config: dict) -> dict:
    """
    Uses an LLM to find and extract detailed information for a given canonical document name.
    """
    print(f"Extracting details for: {doc_name}...")
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        prompt = f"""
        You are an expert on administrative and legal documents in India. Your task is to provide detailed information about the official document titled "{doc_name}".

        Answer the following questions as a single, valid JSON object with the following keys. If a piece of information is not available or not applicable, state "N/A". DO NOT include any conversational text outside the JSON.

        1.  **document_name**: The title of the document.
        2.  **description**: A brief description of what the document is.
        3.  **purpose**: Where or why the document is typically used.
        4.  **how_to_obtain**: A step-by-step process to obtain the document.
        5.  **required_documents**: A list of other documents needed to apply for or get this document.
        6.  **approx_fees**: The approximate fee or cost to obtain the document.
        7.  **processing_time**: The approximate number of days to receive the document.
        """

        payload = {
            "model": config["llm_model"],
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.2}
        }
        
        try:
            response = requests.post(config["llm_url"], json=payload, timeout=600)
            if response.status_code == 200:
                ollama_response = response.json()
                response_text = ollama_response.get('response', '').strip()
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    details_json = json.loads(json_match.group(0))
                    return details_json
            else:
                print(f"❌ Attempt {attempt}/{max_retries} failed for {doc_name}: LLM API returned status {response.status_code}.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Attempt {attempt}/{max_retries} failed for {doc_name} due to parsing error: {e}")
        except Exception as e:
            print(f"❌ Attempt {attempt}/{max_retries} failed for {doc_name} due to a request exception: {e}")

        time.sleep(2)

    print(f"❌ All {max_retries} attempts failed for {doc_name}. Storing an error entry.")
    return {
        "document_name": doc_name,
        "description": "Error: Could not retrieve details.",
        "purpose": "N/A", "how_to_obtain": "N/A",
        "required_documents": "N/A", "approx_fees": "N/A",
        "processing_time": "N/A"
    }

# --- Main function to orchestrate the pipeline ---
def main():
    load_dotenv()
    config = {
        "llm_url": os.getenv("OLLAMA_API_URL",'http://192.168.0.109:11434/api/generate'),
        "llm_model": os.getenv("OLLAMA_MODEL_NAME",'gemma3:4b'),
        "input_csv": 'document_csv/cleaned_unique_document_list.csv',
        "output_csv": 'document_details_all.csv'
    }

    if not config["llm_url"] or not config["llm_model"]:
        print("Error: OLLAMA_API_URL and OLLAMA_MODEL_NAME must be set in your .env file.")
        return

    try:
        df_docs = pd.read_csv(config["input_csv"])
        if 'Cleaned Document Name' not in df_docs.columns:
            print(f"Error: 'Cleaned Document Name' column not found in '{config['input_csv']}'.")
            return
    except FileNotFoundError:
        print(f"Error: Input file '{config['input_csv']}' not found.")
        return

    all_docs = df_docs['Cleaned Document Name'].tolist()
    
    canonical_mapping = {}
    canonical_details_cache = {}
    final_output_list = []

    # Step 1: Create a mapping from original names to canonical names
    print("--- Step 1: Generating Canonical Names for all documents ---")
    for doc_name in all_docs:
        print(f"Finding canonical for: {doc_name}")
        canonical_name = get_canonical_document_name(doc_name, config)
        canonical_mapping[doc_name] = canonical_name

    # Step 2: Get details for each unique canonical name
    print("\n--- Step 2: Extracting Details for Unique Canonical Documents ---")
    unique_canonical_names = set(canonical_mapping.values())
    for canonical_name in unique_canonical_names:
        details = get_document_details(canonical_name, config)
        canonical_details_cache[canonical_name] = details

    # Step 3: Build the final output list, linking original names to details
    print("\n--- Step 3: Building Final Consolidated Output ---")
    for original_doc_name, canonical_name in canonical_mapping.items():
        details = canonical_details_cache.get(canonical_name, {})
        
        # New column with original and canonical name
        detailed_name_info = f"Original Name: {original_doc_name}, Canonical Name: {canonical_name}"
        
        # Create a new row for each original document
        new_row = {
            "original_document_name": original_doc_name,
            "canonical_document_name": canonical_name,
            "detailed_name_info": detailed_name_info,
            **details
        }
        final_output_list.append(new_row)

    if final_output_list:
        df_final = pd.DataFrame(final_output_list)
        df_final = df_final.fillna("N/A")
        
        try:
            df_final.to_csv(config["output_csv"], index=False, encoding='utf-8')
            print(f"\n✅ Successfully saved the complete, consolidated document details to '{config['output_csv']}'.")
        except Exception as e:
            print(f"An error occurred while saving the details file: {e}")
    else:
        print("\n❌ No document details could be processed.")

if __name__ == "__main__":
    main()