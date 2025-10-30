# 📁 Data ETL Pipeline

This folder contains the complete ETL (Extract, Transform, Load) pipeline for G Scheme Bot.

The `main.py` script in this directory is designed to be run as a single, orchestrated pipeline. It automatically fetches, cleans, processes, and loads all scheme data into the MongoDB database.

## Pipeline Workflow

The `main.py` script executes the following steps in order:

1.  **Extract:** Scrapes raw data (HTML, text) from target websites like `mygov.in` using **Playwright**.
2.  **Preprocess:** Cleans the raw scraped data. This step structures the data, removes junk HTML, and organizes it into a preliminary format using **Pandas**,**LLM**,**scpacy**.
3.  **Document Extract:** The pipeline identifies links to documents (like PDFs, DOCs).
4.  **Document Preprocess:** The raw text extracted from the documents is cleaned and formatted.
5.  **Translate:** (If necessary) Any text found in regional languages is translated to English using **googletrans** to ensure uniform data.
6.  **Load:** The final, clean, and processed data (a collection of JSON-like scheme objects) is loaded directly into the **MongoDB** `schemes` collection using **Pymongo**.

## How to Run

1.  Navigate to this directory:
    ```bash
    cd Data
    ```
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure your MongoDB server is running and you have a `MONGO_URI` (e.g., in a `.env` file).
4.  Run the main pipeline:
    ```bash
    python main.py
    ```
