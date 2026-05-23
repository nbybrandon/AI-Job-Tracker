# 🚀 Local LLM-Powered Job Application Tracker & Analytics Dashboard

A private, entirely offline Full-Stack Python application that leverages localized Large Language Models (LLMs) to automatically parse job application details from email drafts and track internship application cycles via an interactive Streamlit analytics dashboard.

---

## 👨‍💻 Developed By
* **Name:** Nicholas Brandon Yang  
* **Institution:** City University of Hong Kong (CityU)  
* **Major:** BSc Data Science
* **Core Skills:** Python, Machine Learning Pipelines, Local LLM Orchestration, Streamlit Ecosystems

---

## 💡 System Architecture & Design Choices

Managing a high volume of internship applications (60+) across multiple tech stacks introduces a substantial data tracking bottleneck. Manual data logging is inefficient, while traditional cloud-based LLM APIs (like OpenAI) present data privacy concerns and rate limits.

This architecture is decoupled into a **Local AI Ingestion Engine** and an **Interactive Analytics Frontend**, operating completely offline.

```text
   [Manual Input]      [Email Drafts/Burner Inbox]
          │                     │
          ▼                     ▼
   ┌────────────┐        ┌──────────────────┐
   │ tracker.py │        │email_listener.py │
   └──────┬─────┘        └────────┬─────────┘
          │                       │
          └───────────┬───────────┘
                      │ (POST Request / localhost:11434)
                      ▼
            ┌───────────────────┐
            │    Ollama Engine  │ (Local Inference: Llama 3 / Phi-3)
            └─────────┬─────────┘
                      │ (Strict Structural JSON Payload)
                      ▼
            ┌───────────────────┐
            │my_applications.csv│ (Flat-File Storage State)
            └─────────┬─────────┘
                      │ (Pandas Dataframe Query)
                      ▼
            ┌───────────────────┐
            │   dashboard.py    │ (Streamlit Web Dashboard)
            └───────────────────┘
```

---

## ✨ Core Engineering Features

### 1. Multi-Channel Data Ingestion
*   **CLI Tracker:** Direct text entry or manual logging via `tracker.py`.
*   **Automated Email Listener:** Connects to a dedicated "burner" inbox via IMAP to automatically fetch and parse application confirmation emails.

### 2. Localized NLP Parsing Strategy
The application utilizes a local HTTP pipeline connecting to **Ollama**. Using structural prompt engineering, local LLM instances (Llama 3 or Phi-3) parse unformatted, raw text. It programmatically extracts company names, roles, and key details into clean, structured JSON.

### 3. 🎯 AI Interview Prep Guide
Integrated directly into the dashboard, this feature uses the local LLM to generate tailored interview questions and preparation guides based on the specific company, role, and application notes stored in the database.

### 4. Automated Application Aging Matrix
To eliminate stagnation, the system calculates the time elapsed since each application:
$$\Delta t = t_{\text{current}} - t_{\text{applied}}$$
If $\Delta t > 7\text{ days}$ and the state is `Applied`, the system triggers a proactive alert in both the CLI and the Dashboard to prompt follow-up action.

### 5. Interactive Web UI Dashboard
Built using **Streamlit**, the dashboard provides:
*   **Real-time KPIs:** Total applications, active pipelines, and interview counts.
*   **Interactive Data Editor:** Edit application statuses or notes directly in the browser and save back to the CSV.
*   **Stagnant App Alerts:** Visual warnings for applications requiring immediate touchpoints.

---

## 🛠️ Tech Stack & Dependencies
* **Core Language:** Python 3
* **Data Processing:** Pandas, JSON, Datetime
* **Local Inference Client:** Ollama (Llama 3 / Phi-3)
* **Frontend Web Framework:** Streamlit
* **Database Engine:** Local Flat-File CSV Matrix
* **Email Protocols:** IMAP (via `imaplib`)

---

## 📁 Repository Structure
```text
Application-Tracker/
│
├── tracker.py          # CLI Data Entry Client & Ollama AI Ingestion Engine
├── dashboard.py        # Streamlit Web Application (KPIs, Data Editor, AI Prep)
├── email_listener.py   # Automated IMAP monitor for fetching email applications
├── repair_csv.py       # Data integrity utility for fixing malformed CSV rows
├── my_applications.csv # Local CSV database (Git-ignored)
├── .env                # Private email credentials (Git-ignored)
└── README.md           # Technical Documentation
```

---

## 🚀 Step-by-Step Execution Guide

### 1. Initialize the Local AI Server
Download [Ollama](https://ollama.com/) and boot up your preferred model:
```bash
ollama run llama3
```

### 2. Environment Setup
Install the necessary Python packages:
```bash
pip install pandas streamlit requests python-dotenv
```

For the **Email Listener**, create a `.env` file in the root directory:
```env
BURNER_EMAIL_ADDRESS="your-email@gmail.com"
BURNER_APP_PASSWORD="your-app-specific-password"
```

### 3. Usage Workflows

**Option A: Manual/Text Ingestion**
Run the ingestion program to add a manual entry or paste an email body for extraction:
```bash
python tracker.py
```

**Option B: Automated Email Fetching**
Listen for new application emails in your burner inbox:
```bash
python email_listener.py
```

**Option C: Launch the Dashboard**
Analyze your progress and generate interview prep guides:
```bash
streamlit run dashboard.py
```

### 4. Data Maintenance
If your CSV becomes malformed due to manual edits or parsing edge cases, run the repair utility:
```bash
python repair_csv.py
```
