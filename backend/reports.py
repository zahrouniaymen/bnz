import pandas as pd
from sqlalchemy.orm import Session
from backend import models, analytics_crud
import io
from fpdf import FPDF
from datetime import datetime

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db

    def generate_excel_analytics(self, year: int) -> io.BytesIO:
        """Generate a multi-sheet Excel report with detailed analytics"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 1. Monthly Evolution
            evolution = analytics_crud.get_monthly_evolution(self.db, year)
            df_evo = pd.DataFrame([e.model_dump() for e in evolution])
            df_evo.to_excel(writer, sheet_name='Evoluzione Mensile', index=False)

            # 2. Client Ranking
            ranking = analytics_crud.get_client_ranking(self.db, year)
            df_rank = pd.DataFrame([r.model_dump() for r in ranking])
            df_rank.to_excel(writer, sheet_name='Ranking Clienti', index=False)

            # 3. Sector Distribution
            sectors = analytics_crud.get_sector_distribution(self.db, year)
            df_sector = pd.DataFrame(sectors)
            df_sector.to_excel(writer, sheet_name='Distribuzione Settori', index=False)

        output.seek(0)
        return output

    def generate_pdf_summary(self, year: int) -> io.BytesIO:
        """Generate a PDF summary report"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, f"Rapporto Statistico M54 - Anno {year}", 0, 1, 'C')
        pdf.ln(10)

        # Basic Stats
        evolution = analytics_crud.get_monthly_evolution(self.db, year)
        total_requests = sum(e.requests for e in evolution)
        total_accepted = sum(e.accepted for e in evolution)
        total_value = sum(e.order_value for e in evolution)

        pdf.set_font("Arial", '', 12)
        pdf.cell(100, 10, f"Totale Richieste: {total_requests}", 0, 1)
        pdf.cell(100, 10, f"Offerte Accettate: {total_accepted}", 0, 1)
        pdf.cell(100, 10, f"Valore Totale Ordini: {total_value:,.2f} EUR", 0, 1)
        pdf.ln(10)

        # Monthly Table
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(40, 10, "Mese", 1)
        pdf.cell(30, 10, "Richieste", 1)
        pdf.cell(30, 10, "Accettate", 1)
        pdf.cell(40, 10, "Valore (EUR)", 1)
        pdf.ln()

        pdf.set_font("Arial", '', 9)
        for e in evolution:
            pdf.cell(40, 8, e.month, 1)
            pdf.cell(30, 8, str(e.requests), 1)
            pdf.cell(30, 8, str(e.accepted), 1)
            pdf.cell(40, 8, f"{e.order_value:,.2f}", 1)
            pdf.ln()

        output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        output.write(pdf_content)
        output.seek(0)
        return output
