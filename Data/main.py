import subprocess
import sys
import os
import time
from datetime import datetime

# --- Configuration ---
# Define the sequence of scripts to be executed
PIPELINE_SCRIPTS = [
    "Extract_scheme.py",
    "preprocess.py",
    "Document_extract.py",
    "Document_preprocess.py",
    "translate.py",
    "load_to_mongo.py"
]

def run_script(script_name):
    """
    Executes a given Python script, checks for errors, and prints its output.
    """
    print("─" * 60)
    print(f"▶️  Running script: {script_name}...")
    start_time = time.time()
    
    # Check if the script file exists before trying to run it
    if not os.path.exists(script_name):
        print(f"❌ FATAL ERROR: Script '{script_name}' not found. Aborting pipeline.")
        sys.exit(1)
        
    try:
        # Use sys.executable to ensure we use the same Python interpreter and environment
        process = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True  # This will raise a CalledProcessError if the script fails (returns a non-zero exit code)
        )
        
        # Print the standard output from the script
        if process.stdout:
            print("   --- Script Output ---")
            print(process.stdout)
        
        duration = time.time() - start_time
        print(f"✅ SUCCESS: '{script_name}' finished in {duration:.2f} seconds.")
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ ERROR: '{script_name}' failed after {duration:.2f} seconds.")
        
        # Print the detailed error message from the script
        if e.stdout:
            print("   --- Output ---")
            print(e.stdout)
        if e.stderr:
            print("   --- Error Details ---")
            print(e.stderr)
            
        # Stop the entire pipeline
        print("\nPipeline aborted due to an error.")
        sys.exit(1)

def main():
    """
    Main function to run the entire data pipeline in the specified sequence.
    """
    pipeline_start_time = time.time()
    print("🚀 Starting the full data processing pipeline...")
    
    for script in PIPELINE_SCRIPTS:
        run_script(script)
        
    total_duration = time.time() - pipeline_start_time
    
    print("─" * 60)
    print(f"🎉 Pipeline completed successfully in {total_duration:.2f} seconds.")
    print(f"   Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("─" * 60)

if __name__ == "__main__":
    main()