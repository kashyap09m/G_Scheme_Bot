import os
import pandas as pd
from googletrans import Translator
import time
import ast
from tqdm import tqdm
import shutil

# --- Configuration ---
TARGET_LANGUAGES = {
    'hi': 'hindi',
    'mr': 'marathi',
    'te': 'telugu'
}

# --- Helper Functions ---

def find_latest_file(folder_path: str) -> str | None:
    """Finds the most recently modified file in a directory."""
    if not os.path.exists(folder_path):
        print(f"Error: Input directory '{folder_path}' not found.")
        return None
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    if not files: return None
    return max(files, key=os.path.getmtime)

def safe_literal_eval(val):
    """Safely evaluates a string that looks like a list or other literal."""
    try:
        if isinstance(val, str) and ('[' in val or '{' in val):
            return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        pass
    return val

def translate_text_robust(translator, text, dest_language, retries=3):
    """Translates text with a retry mechanism."""
    if not text:
        return text
    
    for attempt in range(retries):
        try:
            time.sleep(1)
            if isinstance(text, list):
                if not all(isinstance(item, str) for item in text): return text
                return [translator.translate(item, dest=dest_language).text for item in text]
            elif isinstance(text, str):
                return translator.translate(text, dest=dest_language).text
            else:
                return text
        except Exception as e:
            print(f"\n  - Attempt {attempt + 1}/{retries} failed for '{dest_language}'. Error: {e}")
            if attempt < retries - 1:
                print("  - Waiting for 5 seconds...")
                time.sleep(5)
            else:
                print(f"  - All attempts failed for '{dest_language}'.")
                return f"Translation Error: {text}"

def main():
    """Reads, translates, and saves CSVs with a robust, resumable append-based method."""
    
    input_folder = 'process_csv'
    output_folder = 'translate_csv'
    os.makedirs(output_folder, exist_ok=True)
    
    latest_input_csv = find_latest_file(input_folder)
    if not latest_input_csv:
        print(f"No CSV files found in '{input_folder}'. Exiting.")
        return
        
    print(f"Reading from latest file: {os.path.basename(latest_input_csv)}")
    df_original = pd.read_csv(latest_input_csv)
    
    base_name = os.path.splitext(os.path.basename(latest_input_csv))[0]
    
    # --- NEW: Resume Logic ---
    start_row = 0
    # Use the Hindi file as the reference for checking progress
    hindi_output_path = os.path.join(output_folder, f"{base_name}_hindi.csv")
    if os.path.exists(hindi_output_path):
        try:
            df_progress = pd.read_csv(hindi_output_path)
            start_row = len(df_progress)
            print(f"Resuming translation from row {start_row + 1}...")
        except pd.errors.EmptyDataError:
            print("Found empty progress file. Starting from scratch.")
            start_row = 0
        except Exception as e:
            print(f"Could not read progress file. Starting from scratch. Error: {e}")
            start_row = 0
    else:
        print("No existing progress found. Starting new translation.")

    if start_row >= len(df_original):
        print("All rows have already been translated. Exiting.")
        return
        
    translator = Translator()
    
    try:
        # Loop through only the untranslated rows
        for index, row in tqdm(df_original.iloc[start_row:].iterrows(), 
                               total=len(df_original) - start_row, 
                               desc="Translating Rows"):
            
            # This dictionary will hold the translated data for this single row
            translated_row_for_all_langs = {lang: {} for lang in TARGET_LANGUAGES.keys()}

            for col in df_original.columns:
                value = safe_literal_eval(row[col])
                
                is_translatable = (isinstance(value, str) and value and not value.startswith('http')) or \
                                  (isinstance(value, list) and value and all(isinstance(item, str) for item in value))

                if is_translatable:
                    for lang_code in TARGET_LANGUAGES.keys():
                        translated_value = translate_text_robust(translator, value, lang_code)
                        translated_row_for_all_langs[lang_code][col] = translated_value
                else:
                    # If not translatable, copy the original value to all language versions
                    for lang_code in TARGET_LANGUAGES.keys():
                        translated_row_for_all_langs[lang_code][col] = value
            
            # --- NEW: Append the single processed row to each file ---
            for lang_code, lang_suffix in TARGET_LANGUAGES.items():
                output_path = os.path.join(output_folder, f"{base_name}_{lang_suffix}.csv")
                # Create a single-row DataFrame
                new_row_df = pd.DataFrame([translated_row_for_all_langs[lang_code]])
                # Append to the CSV, writing the header only if the file doesn't exist
                header = not os.path.exists(output_path)
                new_row_df.to_csv(output_path, mode='a', header=header, index=False, encoding='utf-8')

    except (KeyboardInterrupt, Exception) as e:
        print(f"\n⚠️ Process interrupted: {e}. Progress has been saved up to the last completed row.")
        return # Exit gracefully
        
    print("\n✅ Translation complete.")
        
    # Copy the original source file to the output folder at the very end
    try:
        source_file_path = latest_input_csv
        dest_file_path = os.path.join(output_folder, os.path.basename(latest_input_csv))
        if not os.path.exists(dest_file_path): # Avoid re-copying if it's already there
            shutil.copy(source_file_path, dest_file_path)
            print(f"✅ Successfully copied original file to '{dest_file_path}'")
    except Exception as e:
        print(f"❌ Error copying original file: {e}")

if __name__ == "__main__":
    main()