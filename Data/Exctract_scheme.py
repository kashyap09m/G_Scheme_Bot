import os
import time
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote
import random

# --- Configuration ---
BASE_URL = "https://www.myscheme.gov.in"
DATA_FOLDER = "data"
MASTER_CSV_FILE = os.path.join(DATA_FOLDER, "all_schemes.csv")
LOG_FILE = os.path.join(DATA_FOLDER, "scraper.log")
STATE_FILE = "state.txt" 

# --- New Randomized Scraping Rules ---
TOTAL_SCHEMES_GOAL = 20
NUM_RANDOM_STATES_TO_PICK = 10
MIN_SCHEMES_PER_STATE = 1
MAX_SCHEMES_PER_STATE = 5

# --- Selectors ---
SCHEME_CARD_SELECTOR = 'div[role="article"]'
SCHEME_NAME_IN_CARD_SELECTOR = '[id^="scheme-name-"]'
NEXT_PAGE_BUTTON_SELECTOR = 'li.next:not(.disabled) a'

def read_states_from_file(file_path: str) -> list[str]:
    """Reads a comma-separated, quoted list of states from a text file."""
    if not os.path.exists(file_path):
        print(f"Error: State file not found at '{file_path}'.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content: return []
            states = [state.strip() for state in content.replace('"', '').split(',')]
            return [state for state in states if state]
    except Exception as e:
        print(f"Error reading state file: {e}")
        return []

def load_scraped_schemes(master_file_path: str) -> set:
    """Reads the master CSV and returns a set of scraped scheme names."""
    if not os.path.exists(master_file_path): return set()
    try:
        df = pd.read_csv(master_file_path)
        if 'Scheme Name' in df.columns:
            return set(df['Scheme Name'].dropna().astype(str).tolist())
    except pd.errors.EmptyDataError:
        return set()
    return set()

def write_to_log(log_file_path, num_scraped):
    """Writes a timestamped log entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] - Scraped {num_scraped} new schemes.\n"
    with open(log_file_path, 'a', encoding='utf-8') as f: f.write(log_message)
    print(f"Log entry created in '{log_file_path}'")

def get_scheme_info(page, scheme_url: str) -> dict | None:
    """Navigates to a scheme's detail page and scrapes its information."""
    print(f"    -> Scraping details from: {scheme_url}...")
    try:
        page.goto(scheme_url, wait_until="networkidle", timeout=60000)
    except PlaywrightTimeoutError:
        print(f"      - Timeout error loading page. Skipping.")
        return None
    info = {}
    def extract_text(selector):
        try:
            page.wait_for_selector(selector, timeout=5000)
            text = page.locator(selector).first.inner_text().strip()
            return text.replace(',', '')
        except PlaywrightTimeoutError:
            return "Not Available"
    info['Scheme Name'] = extract_text("#scrollDiv h1")
    info['Details'] = extract_text("#details")
    info['Benefits'] = extract_text("#benefits")
    info['Eligibility'] = extract_text("#eligibility")
    info['Application Process'] = extract_text("#application-process")
    info['Documents Required'] = extract_text("#documents-required")
    info['URL'] = scheme_url
    print(f"      - Success: Scraped '{info['Scheme Name']}'")
    return info

def main():
    """Main function to run the randomized multi-state scraper."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    # --- SETUP ---
    all_states = read_states_from_file(STATE_FILE)
    if not all_states:
        print(f"No states found in '{STATE_FILE}'. Exiting.")
        return
    
    # Randomly select states for this run
    num_to_pick = min(NUM_RANDOM_STATES_TO_PICK, len(all_states))
    states_to_scrape = random.sample(all_states, k=num_to_pick)
    print(f"Randomly selected {len(states_to_scrape)} states for this run: {states_to_scrape}")

    print("\nLoading history from master CSV file...")
    scraped_scheme_names = load_scraped_schemes(MASTER_CSV_FILE)
    print(f"Found {len(scraped_scheme_names)} unique schemes in history.")

    all_newly_scraped_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for state in states_to_scrape:
            # Check if we have already reached our overall goal
            if len(all_newly_scraped_data) >= TOTAL_SCHEMES_GOAL:
                print("\nOverall goal of 20 schemes reached. Stopping.")
                break

            print(f"\n--- Scraping schemes for {state} ---")
            
            # Determine limits for this specific state
            schemes_still_needed = TOTAL_SCHEMES_GOAL - len(all_newly_scraped_data)
            limit_for_this_state = random.randint(MIN_SCHEMES_PER_STATE, MAX_SCHEMES_PER_STATE)
            schemes_to_find_in_state = min(schemes_still_needed, limit_for_this_state)
            
            print(f"  Target for this state: Find up to {schemes_to_find_in_state} new schemes.")

            state_url = f"https://www.myscheme.gov.in/search/state/{quote(state)}"
            try:
                page.goto(state_url, wait_until="domcontentloaded", timeout=60000)
            except PlaywrightTimeoutError:
                print(f"  Failed to load page for {state}. Skipping.")
                continue

            # --- PHASE 1: DISCOVERY (Across all pages for this state) ---
            new_schemes_found_for_state = []
            page_num = 1
            discovery_complete = False
            
            while not discovery_complete:
                print(f"\n  Scanning page {page_num} for {state}...")
                try:
                    page.wait_for_selector(SCHEME_CARD_SELECTOR, timeout=15000)
                except PlaywrightTimeoutError:
                    print(f"    No scheme cards found on this page. Ending search for {state}.")
                    break
                
                card_locators = page.locator(SCHEME_CARD_SELECTOR).all()
                for card in card_locators:
                    try:
                        scheme_name = card.locator(SCHEME_NAME_IN_CARD_SELECTOR).inner_text().strip()
                        if scheme_name and scheme_name not in scraped_scheme_names:
                            href = card.locator('a').first.get_attribute("href")
                            full_url = f"{BASE_URL}{href}" if href.startswith('/') else href
                            new_schemes_found_for_state.append({'name': scheme_name, 'url': full_url})
                            scraped_scheme_names.add(scheme_name)
                            # Check if we've found enough for this state
                            if len(new_schemes_found_for_state) >= schemes_to_find_in_state:
                                discovery_complete = True
                                break
                    except PlaywrightTimeoutError:
                        continue
                
                if discovery_complete:
                    break # Exit pagination loop if state limit is met

                next_button = page.locator(NEXT_PAGE_BUTTON_SELECTOR)
                if next_button.count() > 0:
                    print("    Navigating to next page...")
                    next_button.click()
                    page.wait_for_load_state('networkidle', timeout=30000)
                    page_num += 1
                else:
                    print(f"    Last page reached for {state}.")
                    break

            # --- PHASE 2: SCRAPING (Process the links we collected) ---
            if new_schemes_found_for_state:
                print(f"\n  Discovered {len(new_schemes_found_for_state)} new schemes for {state}. Scraping now...")
                for scheme_to_scrape in new_schemes_found_for_state:
                    scheme_data = get_scheme_info(page, scheme_to_scrape['url'])
                    if scheme_data:
                        all_newly_scraped_data.append(scheme_data)
                    time.sleep(1)
            else:
                print(f"\n  No new schemes discovered for {state}.")

        browser.close()
        print("\nBrowser closed.")
        
        if all_newly_scraped_data:
            print(f"\nWriting {len(all_newly_scraped_data)} new schemes to the master file: {MASTER_CSV_FILE}")
            new_df = pd.DataFrame(all_newly_scraped_data)
            file_exists = os.path.exists(MASTER_CSV_FILE)
            new_df.to_csv(MASTER_CSV_FILE, mode='a', header=not file_exists, index=False, encoding='utf-8')
            print("Successfully appended new data.")
        else:
            print("\nNo new schemes were found across the randomly selected states.")
        
        write_to_log(LOG_FILE, len(all_newly_scraped_data))

if __name__ == "__main__":
    main()