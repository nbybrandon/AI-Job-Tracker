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

Managing a high volume of internship applications (60+) across multiple tech stacks introduces a substantial data tracking bottleneck. Manual data logging is inefficient, while traditional cloud-based LLM APIs (like OpenAI or Groq) present data privacy concerns, rate limits, and structural geoblocking within the Hong Kong region. 

To circumvent these friction points, this architecture is decoupled into a **Local AI Ingestion Engine** and an **Interactive Analytics Frontend**, operating completely offline on localized hardware.

```text
   [Unstructured Text Ingestion]
                │
                ▼
      ┌───────────────────┐
      │    tracker.py     │ (CLI Client)
      └─────────┬─────────┘
                │ (POST Request / localhost:11434)
                ▼
      ┌───────────────────┐
      │  Ollama Engine    │ (Local Inference: Llama 3 / Phi-3)
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

### 1. Localized NLP Parsing Strategy
The application utilizes a local HTTP pipeline connecting to **Ollama**. Through structural prompt engineering constraints (`format="json"` API payload optimization), a local LLM instances (Llama 3 or Phi-3 mini) parses unformatted, raw text email drafts. It programmatically extracts key enterprise profiles, targeted engineering roles, and main skills summaries into clean, structured JSON data states.

### 2. Automated Application Aging Matrix
To eliminate stagnation in the application cycle, the backend script runs an automated time-delta execution check upon boot. Utilizing Python's native `datetime` libraries, it maps the temporal vector:
$$\Delta t = t_{\text{current}} - t_{\text{applied}}$$
If $\Delta t > 7\text{ days}$ and the state remains marked as `Applied`, the system flags the row and triggers a proactive terminal alert notifying the user to follow up with the target company.

### 3. Interactive Web UI Dashboard
Built using **Streamlit**, the application reads the flat-file CSV repository into a Pandas DataFrame and serves a live browser dashboard. It displays real-time key performance indicators (KPIs) tracking aggregate metrics (Total Applications, Pending Responses, Scheduled Interviews) alongside an interactive, scrollable data table with built-in multi-column sorting and natural text filtering capabilities.

---

## 🛠️ Tech Stack & Dependencies
* **Core Language:** Python 3
* **Data Processing:** Pandas, JSON, Datetime
* **Local Inference Client:** Ollama (Llama 3 / Phi-3 mini)
* **Frontend Web Framework:** Streamlit
* **Database Engine:** Local Flat-File CSV Matrix

---

## 📁 Repository Structure
```text
ai-job-tracker/
│
├── tracker.py          # CLI Data Entry Client & Ollama AI Ingestion Engine
├── dashboard.py        # Streamlit Web Application Code (KPIs & Data Grid)
├── .gitignore          # Environment & Personal Data Protection Rules
└── README.md           # Technical Documentation & System Blueprint

```
---

## 🚀 Step-by-Step Execution Guide

### 1. Initialize the Local AI Server

Ensure you have downloaded [Ollama](https://ollama.com/) onto your machine. Launch your terminal and boot up the local LLM model instance:

```bash
ollama run phi3

```

*(Leave this terminal window running in the background as your local AI inference server).*

### 2. Install Python Packages

Open a separate terminal window inside the project directory and install the necessary data libraries:

```bash
pip install pandas streamlit requests

```

### 3. Execute the Ingestion CLI

Run the ingestion program to add a manual entry or paste an email draft for automatic AI extraction:

```bash
python tracker.py

```

### 4. Boot the Analytics Dashboard

Launch the interactive browser application to visually analyze, filter, and track your ongoing application cycles:

```bash
streamlit run dashboard.py

```

This will automatically initialize a local web server and open the UI dashboard inside your web browser at `http://localhost:8501`.

```

```