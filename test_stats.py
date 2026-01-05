import sys
import os
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from backend.database import SessionLocal
import backend.crud as crud
import backend.models as models

db = SessionLocal()

print("--- Testing get_dashboard_stats ---")
try:
    # 1. Test as Admin, no year filter
    print("\n[Admin, All Years]")
    stats = crud.get_dashboard_stats(db, user_role="admin", user_id=1, year=None)
    print(f"Total Offers: {stats['total_offers']}")
    print(f"Pending: {stats['pending_registration']}")
    print(f"Accepted: {stats['accepted']}")
    
    # 2. Test as Admin, year 2024
    print("\n[Admin, 2024]")
    stats_2024 = crud.get_dashboard_stats(db, user_role="admin", user_id=1, year=2024)
    print(f"Total Offers: {stats_2024['total_offers']}")

    # 3. Test as Admin, year 2025
    print("\n[Admin, 2025]")
    stats_2025 = crud.get_dashboard_stats(db, user_role="admin", user_id=1, year=2025)
    print(f"Total Offers: {stats_2025['total_offers']}")

    # 4. Check actual years in DB
    print("\n[DB Years Distribution]")
    from sqlalchemy import func
    years = db.query(models.Offer.year_stats, func.count(models.Offer.id)).group_by(models.Offer.year_stats).all()
    for year, count in years:
        print(f"Year {year}: {count}")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    db.close()
