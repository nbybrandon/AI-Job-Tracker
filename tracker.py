# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
import pandas as pd
import requests

FILE_NAME = "my_applications.csv"
OLLAMA_URL = "http://localhost:11434/api/generate"

def run_aging_analysis():
    """
    Automated Application Aging Matrix Execution
    Calculates Δt = t_current - t_applied for pending statuses
    """
    if not os.path.exists(FILE_NAME):
        return

    try:
        df = pd.read_csv(FILE_NAME, on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        
        df['Date Applied'] = pd.to_datetime(df['Date Applied'], errors='coerce')
        today = pd.Timestamp(datetime.now().date())
        df['Days Elapsed'] = (today - df['Date Applied']).dt.days
        
        pending_statuses = ['Applied', 'Waiting on Reply']
        stagnant_apps = df[
            (df['Days Elapsed'] >= 7) & 
            (df['Status'].str.strip().isin(pending_statuses))
        ]
        
        if not stagnant_apps.empty:
            print("\n" + "!" * 60)
            print("🚨 PROACTIVE ALERT: STAGNANT APPLICATIONS DETECTED (>7 DAYS) 🚨")
            print("!" * 60)
            print(f"{'COMPANY':<40} | {'ROLE':<35} | {'DAYS ELAPSED':<12}")
            print("-" * 95)
            for _, row in stagnant_apps.iterrows():
                print(f"{str(row['Company'])[:38]:<40} | {str(row['Role'])[:33]:<35} | {int(row['Days Elapsed'])} days ago")
            print("-" * 95)
            print("💡 Action Recommendation: Prepare tactical follow-up sequences for these targets.\n")
        else:
            print("\n✅ Execution Check: All pending pipelines are fresh and within acceptable time horizons.")
            
    except Exception as e:
        print(f"\n⚠️ Analytics Warning: Could not execute aging check matrices: {e}")

def parse_email_with_llm(subject, email_text):
    """
    Sends both email subject line and raw body text to local Ollama inference engine
    to reliably extract structured JSON parameters without missing the company name.
    """
    prompt = f"""
    You are an expert HR data parsing engine. Analyze the provided email subject line and raw text body to extract the exact parameters.
    The company name or job title might be explicitly located inside the [SUBJECT LINE]. Look there carefully for reference context.
    
    You must output your response in strict valid JSON format with exactly these 5 keys:
    {{
        "Company": "Full corporate name (Clean up trailing descriptors like Limited or Ltd)",
        "Role": "Official job title or position name",
        "Status": "Applied",
        "Date Applied": "{datetime.now().strftime('%Y-%m-%d')}",
        "Notes": "Summarize the submission email used or key highlights from the text"
    }}
    
    Do not add any prose, markdown blocks, code blocks, or commentary outside the raw JSON object.
    
    Contextual Inputs:
    [SUBJECT LINE]: {subject}
    
    [EMAIL BODY TEXT]:
    {email_text}
    """
    
    print("\n🤖 Booting local inference engine... parsing unstructured metadata metrics...")
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        })
        parsed_json = json.loads(response.json()['response'])
        return parsed_json
    except Exception as e:
        print(f"❌ Structural Inference Failure: {e}")
        return None

def save_to_csv(data_dict):
    """
    Safely appends a flat data row into the standard database schema, wrapping fields in quotes.
    """
    new_row = pd.DataFrame([data_dict])
    if not os.path.exists(FILE_NAME):
        new_row.to_csv(FILE_NAME, index=False, encoding='utf-8')
    else:
        new_row.to_csv(FILE_NAME, mode='a', header=False, index=False, encoding='utf-8')
    print(f"📂 State Storage Synchronized! Added entry for: {data_dict['Company']}")

def main():
    print("=" * 60)
    print("     🤖 CORE SYSTEM INITIALIZED: APPLICATION DATA INGESTION CLI 🤖")
    print("=" * 60)
    
    run_aging_analysis()
    
    while True:
        print("\n" + "=" * 50)
        print("Select Operation Mode:")
        print("[1] Manual Structured Form Entry")
        print("[2] Local LLM Automated Email Parser (Subject + Body Context)")
        print("[3] Update Application Status (e.g., Follow Up)")
        print("[4] Exit System")
        print("=" * 50)
        choice = input("Enter execution mode index (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            print("\n--- Manual Structured Form Entry ---")
            company = input("Enter Company Name: ").strip()
            role = input("Enter Job Role: ").strip()
            status = input("Enter Status (e.g., Applied, Interviewing): ").strip()
            date_applied = input(f"Enter Date (YYYY-MM-DD) [Default: {datetime.now().strftime('%Y-%m-%d')}]: ").strip()
            if not date_applied:
                date_applied = datetime.now().strftime('%Y-%m-%d')
            notes = input("Enter Submission Notes: ").strip()
            
            payload = {
                "Company": company, "Role": role, "Status": status, 
                "Date Applied": date_applied, "Notes": notes
            }
            save_to_csv(payload)
            
        elif choice == "2":
            print("\n--- Local LLM Automated Email Parser ---")
            # Step 1: Capture the high-signal Subject Line metadata context
            subject_input = input("Step 1: Paste/Type Email Subject Line: ").strip()
            
            # Step 2: Capture the multi-line text body
            print("\nStep 2: Paste your email body below. Type 'done' on a blank new line and press Enter to process:\n")
            
            email_lines = []
            while True:
                try:
                    line = input()
                    if line.strip().lower() == "done":
                        break
                    email_lines.append(line)
                except (EOFError, KeyboardInterrupt):
                    break
            
            email_content = "\n".join(email_lines)
            
            if subject_input or email_content.strip():
                extracted_payload = parse_email_with_llm(subject_input, email_content)
                if extracted_payload:
                    print("\nExtracted Ingestion Struct:")
                    print(json.dumps(extracted_payload, indent=4))
                    confirm = input("\nCommit this data state to file database? (y/n): ").strip().lower()
                    if confirm == 'y':
                        save_to_csv(extracted_payload)
                    else:
                        print("⚠️ Ingestion stream aborted by operator.")
            else:
                print("❌ Input validation error: Empty payload detected.")
                
        elif choice == "3":
            print("\n--- Update Application Status ---")
            if not os.path.exists(FILE_NAME):
                print("❌ Database empty. No entries available to modify.")
                continue
                
            try:
                df = pd.read_csv(FILE_NAME, on_bad_lines='skip')
                df.columns = df.columns.str.strip()
                
                print("\nCurrent Applications Inventory:")
                print(f"{'INDEX':<6} | {'COMPANY':<35} | {'ROLE':<35} | {'STATUS':<20}")
                print("-" * 110)
                for idx, row in df.iterrows():
                    print(f"[{idx:<3}] | {str(row['Company'])[:33]:<35} | {str(row['Role'])[:33]:<35} | {str(row['Status']):<20}")
                print("-" * 110)
                
                selected_idx = input("\nEnter the number index of the application to update: ").strip()
                if selected_idx.isdigit() and int(selected_idx) in df.index:
                    idx = int(selected_idx)
                    old_status = df.at[idx, 'Status']
                    
                    print(f"\nSelected Target: {df.at[idx, 'Company']} ({df.at[idx, 'Role']})")
                    print("Select New Status:")
                    print("[1] Follow Up")
                    print("[2] Interview Scheduled")
                    print("[3] Waiting on Reply")
                    print("[4] No Response")
                    print("[5] Custom Status Entry")
                    status_choice = input("Enter choice (1-5) [Default: 1]: ").strip()
                    
                    new_status = "Follow Up"
                    if status_choice == "2":
                        new_status = "Interview Scheduled"
                    elif status_choice == "3":
                        new_status = "Waiting on Reply"
                    elif status_choice == "4":
                        new_status = "No Response"
                    elif status_choice == "5":
                        new_status = input("Enter custom status: ").strip()
                    
                    df.at[idx, 'Status'] = new_status
                    
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    current_notes = str(df.at[idx, 'Notes']) if pd.notna(df.at[idx, 'Notes']) else ""
                    df.at[idx, 'Notes'] = f"{current_notes} | Followed up on {today_str}".strip(" | ")
                    
                    df.to_csv(FILE_NAME, index=False, encoding='utf-8')
                    print(f"✅ Success! {df.at[idx, 'Company']} shifted from '{old_status}' to '{new_status}'.")
                else:
                    print("❌ Index processing boundary exception. Aborting update operation.")
            except Exception as e:
                print(f"❌ Status Pipeline Failure: {e}")
                
        elif choice == "4":
            print("\n👋 Terminating ingestion matrix interface. Core dataset changes saved. Goodbye!\n")
            break
            
        else:
            print("\n❌ Runtime Selection Error: Unrecognized index sequence. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()