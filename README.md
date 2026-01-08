# G Scheme Bot – Government Scheme Assistant

🔗 **GitHub Repository:**  
https://github.com/kashyap09m/G_Scheme_Bot

---

## 📌 Project Overview
**G Scheme Bot** is a full-stack web application designed to simplify access to Indian Government Schemes.  
It aggregates scheme data from official sources, structures it using an ETL pipeline, and enables users to explore schemes through a modern web interface and an AI-powered chatbot.

The project includes:
- A **React frontend** for user interaction
- A **Node.js backend** for APIs and business logic
- A **FastAPI-based chatbot microservice** using **RAG (Retrieval-Augmented Generation)**
- A complete **ETL pipeline** to scrape, process, and store scheme data

---

## 🚀 Key Features
- • Centralized access to **3,500+ government schemes**
- • Personalized scheme recommendations
- • AI-powered chatbot for scheme-related queries
- • Document checklist assistance

---

## 🧠 Architecture & Tech Stack

### Frontend
- • React
- • HTML, CSS, JavaScript

### Backend
- • Node.js
- • Mongoose (MongoDB ORM)

### Chatbot Service
- • Python
- • FastAPI
- • LangChain
- • FAISS (Vector Store)
- • Ollama (gemma3:4B – Offline LLM)

### Data Pipeline (ETL)
- • Python
- • Playwright (Web Scraping)
- • Pandas (Data Processing)
- • googletrans (Optional Translation)
- • PyMongo (Database Loading)

### Database
- • MongoDB

---

## 📂 Project Structure
```text
G_Scheme_Bot/
│── Chatbot/            # Chatbot
│── Data/               # ETL pipeline scripts
│── Frontend/           # React frontend
│── backend/            # Node.js backend 
│── README.md
│── .gitignore
│── Screenshot 