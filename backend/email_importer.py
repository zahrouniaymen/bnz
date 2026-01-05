"""
Email Importer for M54 Offer Management System
Adapté du script Download_mail_Commerciale_per_articolo.py
Import des offres depuis commerciale@benozzi.com
"""

import os
import sys
import base64
import re
from datetime import datetime
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️  Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import SessionLocal
import backend.models as models

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class EmailImporter:
    """Import offers from Gmail commerciale@benozzi.com"""
    
    def __init__(self):
        self.service = None
        self.db = SessionLocal()
        self.stats = {
            'processed': 0,
            'created': 0,
            'errors': 0,
            'error_messages': []
        }
    
    def init_gmail_service(self):
        """Initialize Gmail API service"""
        creds = None
        token_path = 'credentials/gmail_token.json'
        creds_path = 'credentials/gmail_credentials.json'
        
        # Check if credentials exist
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                f"Gmail credentials not found at {creds_path}\n"
                "Please download credentials from Google Cloud Console"
            )
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Refresh or create new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            os.makedirs('credentials', exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def search_messages_with_label(self, label_name='1-RICHIESTA_D\'OFFERTA'):
        """Search for messages with specific label"""
        try:
            # Get label ID
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            if not label_id:
                print(f"⚠️  Label '{label_name}' not found")
                return []
            
            # Search messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[label_id],
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            print(f"📧 Found {len(messages)} emails with label '{label_name}'")
            
            return messages
            
        except HttpError as error:
            print(f'❌ Gmail API error: {error}')
            return []
    
    def get_message_details(self, msg_id):
        """Get full message details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            return message
        except HttpError as error:
            print(f'❌ Error getting message {msg_id}: {error}')
            return None
    
    def extract_email_data(self, message):
        """Extract offer data from email"""
        headers = message['payload']['headers']
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Parse date
        try:
            mail_date = datetime.strptime(date_str.split(' (')[0], '%a, %d %b %Y %H:%M:%S %z')
        except:
            mail_date = datetime.now()
        
        # Extract client from email
        client_email = re.search(r'<(.+?)>', from_email)
        if client_email:
            email_domain = client_email.group(1).split('@')[1]
        else:
            email_domain = from_email.split('@')[1] if '@' in from_email else 'unknown.com'
        
        # Extract body
        body = self.get_email_body(message)
        
        # Extract item name from subject or body
        item_name = self.extract_item_name(subject, body)
        
        return {
            'subject': subject,
            'from_email': from_email,
            'email_domain': email_domain,
            'mail_date': mail_date,
            'body': body,
            'item_name': item_name,
            'message_id': message['id']
        }
    
    def get_email_body(self, message):
        """Extract email body (text or HTML)"""
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        data = part['body'].get('data', '')
                        if data:
                            html = base64.urlsafe_b64decode(data).decode('utf-8')
                            soup = BeautifulSoup(html, 'html.parser')
                            return soup.get_text()
            else:
                data = message['payload']['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            print(f"⚠️  Error extracting body: {e}")
        
        return ""
    
    def extract_item_name(self, subject, body):
        """Extract item/article name from subject or body"""
        # Try to find patterns like "RDO:", "Richiesta:", etc.
        patterns = [
            r'RDO[:\s]+(.+?)(?:\n|$)',
            r'Richiesta[:\s]+(.+?)(?:\n|$)',
            r'Offerta[:\s]+(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to subject
        return subject[:100] if subject else "Articolo da email"
    
    def get_or_create_client(self, email_domain, from_email):
        """Get existing client or create new one"""
        # Try to find by email domain
        client = self.db.query(models.Client).filter(
            models.Client.email_domain == email_domain
        ).first()
        
        if not client:
            # Extract company name from email
            company_name = email_domain.split('.')[0].capitalize()
            
            client = models.Client(
                name=f"Cliente {company_name}",
                email_domain=email_domain,
                strategic=False,
                notes=f"Creato automaticamente da email: {from_email}"
            )
            self.db.add(client)
            self.db.commit()
            self.db.refresh(client)
            print(f"   ✅ Nuovo cliente creato: {client.name}")
        
        return client
    
    def create_offer_from_email(self, email_data):
        """Create offer in database from email data"""
        try:
            # Get or create client
            client = self.get_or_create_client(
                email_data['email_domain'],
                email_data['from_email']
            )
            
            # Get admin user (default manager)
            admin = self.db.query(models.User).filter(
                models.User.username == 'admin'
            ).first()
            
            if not admin:
                raise Exception("Admin user not found")
            
            # Generate offer number
            year = email_data['mail_date'].year
            count = self.db.query(models.Offer).filter(
                models.Offer.offer_number.like(f'{year}-%')
            ).count()
            offer_number = f"{year}-{count + 1:04d}"
            
            # Create offer
            offer = models.Offer(
                offer_number=offer_number,
                client_id=client.id,
                managed_by_id=admin.id,
                mail_date=email_data['mail_date'],
                status=models.OfferStatus.PENDING_REGISTRATION,
                priority=models.Priority.MEDIA,
                check_feasibility=models.CheckStatus.DA_ESAMINARE,
                check_technical=models.CheckStatus.DA_ESAMINARE,
                check_purchasing=models.CheckStatus.DA_ESAMINARE,
                check_planning=models.CheckStatus.DA_ESAMINARE,
                item_name=email_data['item_name'],
                email_subject=email_data['subject'],
                offer_amount=0.0
            )
            
            self.db.add(offer)
            self.db.commit()
            self.db.refresh(offer)
            
            print(f"   ✅ Offerta creata: {offer.offer_number} - {client.name}")
            return offer
            
        except Exception as e:
            self.db.rollback()
            print(f"   ❌ Errore creazione offerta: {e}")
            raise
    
    def change_message_label(self, msg_id, remove_label, add_label):
        """Change email label after processing"""
        try:
            # Get label IDs
            labels = self.service.users().labels().list(userId='me').execute()
            
            remove_label_id = None
            add_label_id = None
            
            for label in labels.get('labels', []):
                if label['name'] == remove_label:
                    remove_label_id = label['id']
                if label['name'] == add_label:
                    add_label_id = label['id']
            
            if remove_label_id and add_label_id:
                self.service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={
                        'removeLabelIds': [remove_label_id],
                        'addLabelIds': [add_label_id]
                    }
                ).execute()
                print(f"   📝 Label cambiato: {remove_label} → {add_label}")
        
        except HttpError as error:
            print(f'   ⚠️  Errore cambio label: {error}')
    
    def import_offers(self):
        """Main import process"""
        print("\n" + "="*80)
        print("📧 IMPORT OFFERTE DA EMAIL")
        print("="*80 + "\n")
        
        try:
            # Initialize Gmail service
            print("🔐 Connessione a Gmail...")
            self.init_gmail_service()
            print("✅ Connesso a Gmail\n")
            
            # Search for emails
            messages = self.search_messages_with_label('1-RICHIESTA_D\'OFFERTA')
            
            if not messages:
                print("ℹ️  Nessun email da processare")
                return self.stats
            
            # Process each message
            for i, msg in enumerate(messages, 1):
                print(f"\n📨 Processando email {i}/{len(messages)}...")
                self.stats['processed'] += 1
                
                try:
                    # Get message details
                    message = self.get_message_details(msg['id'])
                    if not message:
                        continue
                    
                    # Extract data
                    email_data = self.extract_email_data(message)
                    print(f"   Oggetto: {email_data['subject'][:50]}...")
                    
                    # Create offer
                    offer = self.create_offer_from_email(email_data)
                    self.stats['created'] += 1
                    
                    # Change label
                    self.change_message_label(
                        msg['id'],
                        '1-RICHIESTA_D\'OFFERTA',
                        '2-OFFERTE_DA_GESTIRE'
                    )
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    error_msg = f"Email {i}: {str(e)}"
                    self.stats['error_messages'].append(error_msg)
                    print(f"   ❌ Errore: {e}")
            
            # Summary
            print("\n" + "="*80)
            print("✅ IMPORT COMPLETATO")
            print("="*80)
            print(f"📊 Statistiche:")
            print(f"   - Email processate: {self.stats['processed']}")
            print(f"   - Offerte create: {self.stats['created']}")
            print(f"   - Errori: {self.stats['errors']}")
            print("="*80 + "\n")
            
            return self.stats
            
        except Exception as e:
            print(f"\n❌ Errore fatale: {e}")
            self.stats['errors'] += 1
            self.stats['error_messages'].append(str(e))
            return self.stats
        
        finally:
            self.db.close()


def main():
    """Run email import"""
    importer = EmailImporter()
    stats = importer.import_offers()
    return stats


if __name__ == "__main__":
    main()
