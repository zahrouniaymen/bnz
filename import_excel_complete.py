"""
Import Complet des Données Excel M54 & M77 (Version FINALE)
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import List, Optional
import re

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from backend.database import SessionLocal
import backend.models as models

class ExcelImporter:
    def __init__(self):
        self.db = SessionLocal()
        self.stats = {'clients_created': 0, 'offers_created': 0, 'orders_created': 0, 'errors': 0}
        self.client_cache = {}
        self.offer_cache = {}

    def parse_date(self, date_val):
        if pd.isna(date_val): return None
        if isinstance(date_val, datetime): return date_val
        try: return pd.to_datetime(date_val)
        except: return None

    def parse_float(self, val):
        if pd.isna(val): return 0.0
        try:
            if isinstance(val, str):
                val = re.sub(r'[^\d.,-]', '', val).replace(',', '.')
            return float(val)
        except: return 0.0

    def map_status(self, excel_status):
        if pd.isna(excel_status): return "PENDING_REGISTRATION"
        s = str(excel_status).upper().strip()
        if any(x in s for x in ["REGISTR", "DA REG", "DA INVIARE"]): return "PENDING_REGISTRATION"
        if any(x in s for x in ["WORK", "LAVORO"]): return "IN_LAVORO"
        if any(x in s for x in ["VERIF", "CHECK"]): return "CHECKS_IN_PROGRESS"
        if "PRONTA" in s: return "READY_TO_SEND"
        if any(x in s for x in ["INV", "SENT"]): return "SENT"
        if any(x in s for x in ["ACCETT", "VINTA", "ORDINE"]): return "ACCETTATA"
        if any(x in s for x in ["DECLIN", "PERSA", "NON ACCETT"]): return "DECLINATA"
        return "PENDING_REGISTRATION"

    def map_priority(self, excel_priority):
        if pd.isna(excel_priority): return "media"
        p = str(excel_priority).upper().strip()
        if "URG" in p: return "urgente"
        if "ALTA" in p: return "alta"
        if "BASSA" in p: return "bassa"
        return "media"

    def get_or_create_client(self, client_name):
        name = str(client_name).strip() if not pd.isna(client_name) else "Cliente Sconosciuto"
        if name in self.client_cache: return self.client_cache[name]
        
        client = self.db.query(models.Client).filter(models.Client.name == name).first()
        if not client:
            domain = name.lower().replace(' ', '').replace('.', '')[:50] + '.com'
            # Check if domain exists
            existing_domain = self.db.query(models.Client).filter(models.Client.email_domain == domain).first()
            if existing_domain:
                domain = f"manual_{datetime.now().microsecond}_{domain}"
            
            client = models.Client(name=name, email_domain=domain)
            self.db.add(client)
            try:
                self.db.commit()
            except Exception: # Catching any exception, typically IntegrityError
                self.db.rollback()
                # Attempt to retrieve the client again, in case it was created by another process
                client = self.db.query(models.Client).filter(models.Client.name == name).first()
            
            if client: # Ensure client is not None after potential rollback/re-query
                self.db.refresh(client)
                self.stats['clients_created'] += 1
        
        self.client_cache[name] = client
        return client

    def find_col(self, df, keywords):
        for col in df.columns:
            c_norm = str(col).upper().replace('\n', ' ').strip()
            if any(k.upper() in c_norm for k in keywords):
                return col
        return None

    def run_import(self):
        print("[INFO] Nettoyage et Import...")
        self.db.query(models.WorkflowStep).delete()
        self.db.query(models.Offer).delete()
        self.db.commit()

        m54_file = 'M54_REGISTRO OFFERTE_REV03 DEL 20_03_2024.xlsx'
        m77_file = 'M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx'
        
        # 1. Import M54 Offers
        df = pd.read_excel(m54_file, sheet_name='OFFERTA', header=1)
        
        # Identify columns
        c_nr = self.find_col(df, ['Nr.'])
        c_date = self.find_col(df, ['DATA MAIL'])
        c_client = self.find_col(df, ['CLIENTE'])
        c_status = self.find_col(df, ['STATO'])
        c_priority = self.find_col(df, ['PRIORIT'])
        c_item = self.find_col(df, ['ITEM']) # More specific
        c_amount = self.find_col(df, ['IMPORTO OFFERTA'])
        c_managed = self.find_col(df, ['GESTITA DA'])
        c_purchasing = self.find_col(df, ['GESTORE UFF.ACQ.'])
        c_subject = self.find_col(df, ['OGGETTO EMAIL'])
        c_type = self.find_col(df, ['TIPO'])

        admin = self.db.query(models.User).filter(models.User.username == 'admin').first()

        for idx, row in df.iterrows():
            try:
                raw_nr = row[c_nr]
                if pd.isna(raw_nr): continue
                
                # Handle 2500123.0 type floats from Excel
                if isinstance(raw_nr, float):
                    nr = str(int(raw_nr))
                else:
                    nr = str(raw_nr).strip().split('.')[0] # Remove potential .0 if it's a string

                if not nr or nr == 'nan': continue
                
                # Check for duplicates and append suffix
                base_nr = nr
                suffix = 0
                while nr in self.offer_cache:
                    nr = f"{base_nr}/{suffix}"
                    suffix += 1

                # Determine year from nr prefix (first 2 digits)
                year = 2000 + int(nr[:2]) if len(nr) >= 2 and nr[:2].isdigit() else 2024

                client = self.get_or_create_client(row[c_client]) if c_client else self.get_or_create_client(None)
                
                offer = models.Offer(
                    offer_number=nr,
                    mail_date=self.parse_date(row[c_date]) if c_date else None,
                    client_id=client.id,
                    managed_by_id=admin.id,
                    status=self.map_status(row[c_status]) if c_status else "PENDING_REGISTRATION",
                    priority=self.map_priority(row[c_priority]) if c_priority else "media",
                    item_name=str(row[c_item])[:500] if c_item and pd.notna(row[c_item]) else None,
                    email_subject=str(row[c_subject])[:1000] if c_subject and pd.notna(row[c_subject]) else None,
                    offer_type=str(row[c_type])[:100] if c_type and pd.notna(row[c_type]) else None,
                    offer_amount=self.parse_float(row[c_amount]) if c_amount else 0.0,
                    managed_by_name=str(row[c_managed]).strip() if c_managed and pd.notna(row[c_managed]) else None,
                    purchasing_manager_name=str(row[c_purchasing]).strip() if c_purchasing and pd.notna(row[c_purchasing]) else None,
                    year_stats=year,
                    created_at=datetime.utcnow()
                )
                self.db.add(offer)
                self.offer_cache[nr] = True
                self.stats['offers_created'] += 1
                if self.stats['offers_created'] % 100 == 0: self.db.commit()
            except Exception as e:
                self.stats['errors'] += 1
                print(f"Error row {idx}: {e}")
        
        self.db.commit()
        print(f"M54 Import SUCCESS: {self.stats['offers_created']} offers.")

        # 2. Import M77 Orders (Updating existing offers with order info)
        if os.path.exists(m77_file):
            print("[INFO] Importation des données M77 (Ordini)...")
            df77 = pd.read_excel(m77_file, sheet_name='ORDINE', header=1)
            
            c_nr77 = self.find_col(df77, ['Nr.'])
            c_order_date = self.find_col(df77, ['DATA ORDINE', 'DATA RICEZIONE'])
            c_order_amount = self.find_col(df77, ['IMPORTO', 'VALORE'])
            
            for idx, row in df77.iterrows():
                try:
                    raw_nr = row[c_nr77]
                    if pd.isna(raw_nr): continue
                    
                    nr = str(int(raw_nr)) if isinstance(raw_nr, float) else str(raw_nr).strip().split('.')[0]
                    if not nr or nr == 'nan': continue
                    
                    # Update existing offer with order info
                    offer = self.db.query(models.Offer).filter(models.Offer.offer_number.like(f"{nr}%")).first()
                    if offer:
                        offer.order_date = self.parse_date(row[c_order_date]) if c_order_date else offer.order_date
                        offer.order_amount = self.parse_float(row[c_order_amount]) if c_order_amount else offer.order_amount
                        if offer.order_date:
                            offer.status = "ACCETTATA"
                        self.stats['orders_created'] += 1
                except Exception as e:
                    print(f"Error M77 row {idx}: {e}")
            self.db.commit()
            print(f"M77 Update SUCCESS: {self.stats['orders_created']} orders linked.")

if __name__ == "__main__":
    importer = ExcelImporter()
    importer.run_import()
    importer.db.close()
