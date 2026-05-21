import pandas as pd
import os
import json
import requests
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Load the variables from the .env file into Python's memory
load_dotenv()

FILE_NAME = "my_applications.csv"

def init_tracker():
    """Creates the CSV file if it doesn't exist yet."""
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["Company", "Role", "Status", "Date Applied", "Notes"])
        df.to_csv(FILE_NAME, index=False)
        print("✅ New tracker file created: my_applications.csv\n")

def check_follow_ups():
    """Scans the CSV and triggers an alert if an application is > 7 days old."""
    if not os.path.exists(FILE_NAME): return
    df = pd.read_csv(FILE_NAME)
    if df.empty: return
        
    df['Date Applied'] = pd.to_datetime(df['Date Applied'])
    today = datetime.now()
    needs_follow_up = df[(df['Status'] == 'Applied') & (today - df['Date Applied'] > timedelta(days=7))]
    
    if not needs_follow_up.empty:
        print("\n" + "!"*50)
        print(" ⚠️ ACTION REQUIRED: FOLLOW-UP ALERTS")
        print("!"*50)
        for index, row in needs_follow_up.iterrows():
            days_waiting = (today - row['Date Applied']).days
            print(f" -> {row['Company']} ({row['Role']}): Applied {days_waiting} days ago.")
        print("-" * 50 + "\n")

def add_job_manual():
    """Manually prompts user for job details."""
    company = input("Company Name: ")
    role = input("Role Applied For: ")
    status = "Applied"
    today = date.today().strftime("%Y-%m-%d")
    notes = input("Any Notes? (Hit enter to skip): ")
    
    save_to_csv(company, role, status, today, notes)
    print(f"\n🎉 Successfully added {company} to your tracker!\n")

def add_job_via_ai():
    """Takes a pasted email, uses local Ollama to extract details, and saves it."""
    
    print("\n📝 Paste your email draft below.")
    print("When you are finished pasting, type 'done' on a new line and press Enter:")
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'done':
            break
        lines.append(line)
    
    email_text = "\n".join(lines)
    
    if not email_text.strip():
        print("No text detected. Returning to menu.\n")
        return

    print("\n🧠 Local AI (Ollama) is analyzing your email...")
    
    prompt = f"""
    Analyze the following job application email.
    Extract the following information:
    1. The Company Name
    2. The Role Applied For
    3. Notes (A short 1-sentence summary of the main skills highlighted)

    Return the result STRICTLY as a valid JSON object with the exact keys: "Company", "Role", "Notes".
    
    Email Text:
    {email_text}
    """

    try:
        # Standard HTTP Request to your OWN computer (localhost)
        response = requests.post(
            url="http://localhost:11434/api/generate",
            json={
                "model": "llama3", # Change to "phi3" if you downloaded that one instead
                "prompt": prompt,
                "stream": False,
                "format": "json"   # Ollama natively forces JSON output here!
            }
        )
        
        response_data = response.json()
        
        # Ollama returns the text inside the 'response' key
        response_text = response_data.get('response', '{}')
        extracted_data = json.loads(response_text)
        
        company = extracted_data.get("Company", "Unknown")
        role = extracted_data.get("Role", "Unknown")
        notes = extracted_data.get("Notes", "")
        status = "Applied"
        today = date.today().strftime("%Y-%m-%d")
        
        save_to_csv(company, role, status, today, notes)
        
        print("\n✨ Extraction Complete! Here is what your Local AI found:")
        print(f"Company: {company}")
        print(f"Role:    {role}")
        print(f"Notes:   {notes}")
        print("✅ Automatically saved to your tracker!\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to Ollama. Make sure the Ollama app is running in the background!")
    except json.JSONDecodeError:
        print("\n❌ Failed to format the response properly. Please try again.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}\n")

def save_to_csv(company, role, status, date_applied, notes):
    """Helper function to append data to the CSV."""
    df = pd.read_csv(FILE_NAME)
    new_entry = pd.DataFrame([[company, role, status, date_applied, notes]], columns=df.columns)
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)

def view_jobs():
    """Displays all tracked jobs in a clean table format."""
    df = pd.read_csv(FILE_NAME)
    if df.empty:
        print("\nYour tracker is empty! Time to apply to some jobs.\n")
    else:
        print("\n" + "="*80)
        print(df.to_markdown(index=False))
        print("="*80 + "\n")

if __name__ == "__main__":
    init_tracker()
    check_follow_ups()
    
    while True:
        print("1. Add Application (Manual Entry)")
        print("2. Add Application (Paste Email & Auto-Extract)")
        print("3. View All Applications")
        print("4. Exit")
        
        choice = input("Choose an option (1-4): ")
        
        if choice == '1':
            add_job_manual()
        elif choice == '2':
            add_job_via_ai()
        elif choice == '3':
            view_jobs()
        elif choice == '4':
            print("Exiting Tracker. Good luck with your interviews!")
            break
        else:
            print("Invalid choice, please try again.\n")