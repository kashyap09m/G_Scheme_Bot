import os
import pandas as pd
import re
import asyncio
import aiohttp
import json
from dotenv import load_dotenv
from tqdm.asyncio import tqdm_asyncio

# --- Helper Functions ---

def find_latest_file(folder_path: str) -> str | None:
    """Finds the most recently modified file in a directory."""
    if not os.path.exists(folder_path):
        print(f"Error: Input directory '{folder_path}' not found.")
        return None
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not files: return None
    return max(files, key=os.path.getmtime)

def load_processed_schemes(file_path: str) -> set:
    """Reads the master processed file to get a set of already processed scheme names."""
    if not os.path.exists(file_path):
        return set()
    try:
        df = pd.read_csv(file_path)
        if 'Scheme Name' in df.columns:
            return set(df['Scheme Name'].tolist())
    except pd.errors.EmptyDataError:
        return set()
    return set()

def expand_age_range(age_str: str) -> list:
    if not isinstance(age_str, str): return []
    try:
        if '-' in age_str:
            start, end = map(int, age_str.split('-'))
            return list(range(start, end + 1))
        return [int(age_str)]
    except (ValueError, TypeError):
        return []

def clean_and_listify(text: str) -> list:
    if not isinstance(text, str) or text == "Not Available": return []
    items = [re.sub(r'^[-\*]\s*', '', line).strip() for line in text.split('\n')]
    return [item for item in items if item]

def process_income_string(text: str) -> str:
    if not text or not isinstance(text, str): return ""
    text_lower = text.lower()
    numbers = re.findall(r'\d+\.?\d*', text_lower)
    if not numbers: return ""
    try:
        value = float(numbers[0])
        if 'lakh' in text_lower:
            value *= 100000
        return f"0-{int(value)}"
    except (ValueError, IndexError):
        return ""

# --- LLM and Main Processing Functions ---

def create_focused_llm_prompt(row_data: dict) -> str:
    context = f"DETAILS: {row_data.get('Details', '')}\nELIGIBILITY: {row_data.get('Eligibility', '')}"
    prompt = f"""
    Analyze the provided scheme context. Extract ONLY the following 5 fields.
    Your response MUST be only a valid JSON object with the following keys. If a value is not found, return null for that key.
    - "extracted_age": The required age range as a string (e.g., "18-60").
    - "extracted_gender": The applicable gender (e.g., "Female", "Male", "Any").
    - "extracted_occupation": A list of target occupations (e.g., ["Farmer", "Student"]).
    - "extracted_caste": A list of applicable social categories (e.g., ["SC", "ST"]).
    - "extracted_income": The family income requirement as a string (e.g., "up to 4 lakh per annum").
    CONTEXT:\n---\n{context}\n---
    """
    return prompt

async def query_llm_for_entities(session: aiohttp.ClientSession, row: dict, config: dict) -> dict:
    prompt = create_focused_llm_prompt(row)
    payload = {"model": config["llm_model"], "prompt": prompt, "format": "json", "stream": False}
    try:
        async with session.post(config["llm_url"], json=payload, timeout=180) as response:
            if response.status == 200:
                ollama_response = await response.json()
                return json.loads(ollama_response.get('response', '{}'))
            return {}
    except Exception:
        return {}

async def process_row_hybrid(session: aiohttp.ClientSession, row: pd.Series, config: dict) -> dict:
    llm_results = await query_llm_for_entities(session, row.to_dict(), config)
    processed_data = {
        'Scheme Name': row.get('Scheme Name'), 'URL': row.get('URL'),
        'Details': row.get('Details'), 'Benefits': clean_and_listify(row.get('Benefits')),
        'Eligibility': row.get('Eligibility'), 'Application Process': row.get('Application Process'),
        'Required Documents': clean_and_listify(row.get('Documents Required'))
    }
    age_from_llm = llm_results.get('extracted_age')
    processed_data['Age'] = expand_age_range(age_from_llm) if age_from_llm else "No age limit"
    occupation_from_llm = llm_results.get('extracted_occupation', [])
    processed_data['Occupation'] = occupation_from_llm if occupation_from_llm else "All"
    gender_from_llm = llm_results.get('extracted_gender')
    processed_data['Gender'] = gender_from_llm if gender_from_llm and str(gender_from_llm).lower() != 'any' else "Both"
    caste_from_llm = llm_results.get('extracted_caste', [])
    processed_data['caste'] = caste_from_llm if caste_from_llm else ["Not Specified"]
    income_from_llm = llm_results.get('extracted_income')
    processed_income = process_income_string(income_from_llm)
    processed_data['Income'] = processed_income if processed_income else "No income limit"
    context_lower = f"{row.get('Details', '')} {row.get('Eligibility', '')}".lower()
    ALL_STATES = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"]
    found_states = [state for state in ALL_STATES if state.lower() in context_lower]
    processed_data['Applicable State'] = found_states if found_states else ALL_STATES
    return processed_data

async def main():
    """Finds latest scraped data, processes new schemes, appends to master file, and cleans up."""
    load_dotenv()
    config = {
        "llm_url": os.getenv("OLLAMA_API_URL"),
        "llm_model": os.getenv("OLLAMA_MODEL_NAME"),
        "concurrency": int(os.getenv("CONCURRENT_REQUESTS", 4))
    }
    input_folder = 'data'
    output_folder = 'process_csv'
    master_output_file = os.path.join(output_folder, 'processed_schemes.csv')
    os.makedirs(output_folder, exist_ok=True)

    processed_scheme_names = load_processed_schemes(master_output_file)
    print(f"Found {len(processed_scheme_names)} schemes that have already been processed.")

    latest_input_csv = find_latest_file(input_folder)
    if not latest_input_csv:
        print("No scraped data files found in the 'data' folder. Exiting.")
        return
    print(f"Found latest scraped file: {os.path.basename(latest_input_csv)}")

    try:
        df = pd.read_csv(latest_input_csv)
        unprocessed_df = df[~df['Scheme Name'].isin(processed_scheme_names)]
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"Error reading input file: {e}")
        return

    if unprocessed_df.empty:
        print("No new schemes to process from the latest file. All data is up to date.")
        # NEW: Delete the redundant raw file even if there's no new data
        try:
            print(f"\nCleanup: Deleting the redundant raw data file: {os.path.basename(latest_input_csv)}")
            os.remove(latest_input_csv)
            print("✅ Raw data file deleted successfully.")
        except OSError as e:
            print(f"❌ Error deleting raw data file: {e}")
        return
    
    print(f"Found {len(unprocessed_df)} new schemes to process.")

    tasks = []
    semaphore = asyncio.Semaphore(config["concurrency"])
    async with aiohttp.ClientSession() as session:
        for _, row in unprocessed_df.iterrows():
            async def task_wrapper(row_dict):
                async with semaphore:
                    return await process_row_hybrid(session, pd.Series(row_dict), config)
            tasks.append(task_wrapper(row.to_dict()))
        
        print(f"Processing new schemes with hybrid approach (concurrency: {config['concurrency']})...")
        results = await tqdm_asyncio.gather(*tasks)

    successful_docs = [doc for doc in results if doc is not None]
    print(f"\nProcessing complete. {len(successful_docs)} new schemes processed successfully.")
    
    if successful_docs:
        column_order = [
            'Scheme Name', 'URL', 'Details', 'Benefits', 'Eligibility', 'Application Process',
            'Required Documents', 'Age', 'caste', 'Applicable State', 'Occupation', 'Gender', 'Income'
        ]
        new_processed_df = pd.DataFrame(successful_docs, columns=column_order)
        
        file_exists = os.path.exists(master_output_file)
        new_processed_df.to_csv(master_output_file, mode='a', header=not file_exists, index=False, encoding='utf-8')
        
        print(f"Successfully appended {len(successful_docs)} new records to '{master_output_file}'.")

        # --- NEW: Delete the processed raw data file ---
        try:
            print(f"\nCleanup: Deleting the processed raw data file: {os.path.basename(latest_input_csv)}")
            os.remove(latest_input_csv)
            print("✅ Raw data file deleted successfully.")
        except OSError as e:
            print(f"❌ Error deleting raw data file: {e}")

if __name__ == "__main__":
    asyncio.run(main())