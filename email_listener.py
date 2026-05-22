import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# 1. Load your Burner Email credentials from .env
load_dotenv()
EMAIL = os.getenv("BURNER_EMAIL_ADDRESS")
PASSWORD = os.getenv("BURNER_APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def check_burner_inbox():
    try:
        print("Connecting to Burner Inbox...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        
        mail.select('INBOX')
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        if not email_ids:
            print("No new applications found.")
            return []
            
        extracted_emails = []
        
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # --- NEW: Extract and safely decode the Subject Line ---
                    subject_header = msg.get("Subject", "No Subject")
                    decoded_subject = decode_header(subject_header)[0]
                    subject = decoded_subject[0]
                    if isinstance(subject, bytes):
                        # Decode bytes to a standard string
                        encoding = decoded_subject[1] if decoded_subject[1] else 'utf-8'
                        try:
                            subject = subject.decode(encoding)
                        except:
                            subject = subject.decode('utf-8', errors='ignore')
                    # -------------------------------------------------------
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break # Stop after finding the first plain-text body
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        
                    # Bundle the extracted subject and body together into a dictionary
                    if body:
                        extracted_emails.append({
                            "subject": subject, 
                            "body": body
                        })
            
            mail.store(e_id, '+FLAGS', r'\Seen')
            
        return extracted_emails
                    
    except Exception as e:
        print(f"Error fetching email: {e}")
        return []

from tracker import parse_email_with_llm, save_to_csv

if __name__ == "__main__":
    new_emails = check_burner_inbox()
    
    target_keywords = ["applied", "application", "internship", "resume", "position", "role"]
    
    if not new_emails:
        print("Waiting for new applications...")
    else:
        # Now we iterate through our list of dictionaries
        for email_data in new_emails:
            print("-" * 50)
            
            # Unpack the subject and body from the dictionary
            subject = email_data["subject"]
            body = email_data["body"]
            
            text_lower = body.lower()
            is_application = any(keyword in text_lower for keyword in target_keywords)
            
            if is_application:
                print(f"📬 Found a valid application! Subject: '{subject}'")
                print("Sending to local Ollama...")
                
                # Pass BOTH the dynamic subject and the body exactly as tracker.py expects
                extracted_json = parse_email_with_llm(subject, body) 
                
                if extracted_json:
                    save_to_csv(extracted_json) 
                    print("✅ Successfully added to dashboard!")
                else:
                    print("⚠️ Failed to extract JSON from this email.")
            else:
                print("⏭️ Filter triggered: Skipping non-application email.")
                
    print("🏁 Inbox check complete!")