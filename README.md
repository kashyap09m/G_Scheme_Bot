# G Scheme Bot 🤖

G Scheme Bot is a comprehensive web application designed to help Indian citizens find and understand government schemes they are eligible for. It features personalized recommendations, state-wise browsing, and an intelligent offline-first chatbot for answering specific queries.

## ✨ Features

* **Personalized Recommendations:** Users register with their profile (age, profession, state, income, etc.) to get a dashboard of recommended schemes.
* **Offline RAG Chatbot:** Ask complex questions (e.g., "What schemes are there for a 17-year-old student?") and get answers from an offline RAG pipeline.
* **Document Checklist:** When viewing a scheme, users see a personalized checklist of which required documents they have and which they are missing.


## 🛠️ Tech Stack & Architecture

This project has a multi-part architecture, separating the main app, the chatbot, and the data pipeline.

* **Frontend :**
    * **React**

* **Backend :**
    * **Node.js**
    * **Mongoose** (for MongoDB)

* **Chatbot :**
    * **Python**
    * **FastAPI** (to serve the RAG API)
    * **LangChain** (to build the RAG chain)
    * **Ollama `gemma3:4B`** (for offline LLM generation)
    * **FAISS** (for offline, in-memory vector storage)

* **Data Pipeline (ETL):**
    * **Python**
    * **Playwright** (for web scraping)
    * **Pandas & LLM** (for data processing)
    * **Pymongo** (for loading data to MongoDB)

## 📁 Data ETL Pipeline (My Task)

This project includes a complete ETL (Extract, Transform, Load) pipeline located in the `Data/` folder.

Its `main.py` script is designed to be run as a single, orchestrated pipeline. It automatically fetches, cleans, processes, and loads all scheme data into the MongoDB database.

### Pipeline Workflow

The script executes the following steps in order:

1.  **Extract:** Scrapes raw data (HTML, text) from target websites like `mygov.in` using **Playwright**.
2.  **Preprocess:** Cleans the raw scraped data, removes junk HTML, and organizes it into a preliminary format using **Pandas**.
3.  **Document Extract:** Downloads linked documents (like PDFs) and uses **Tika** to extract their text content.
4.  **Translate:** (If necessary) Any text found in regional languages is translated to English using **googletrans**.
5.  **Load:** The final, clean data is loaded directly into the **MongoDB** `schemes` collection using **Pymongo**.
