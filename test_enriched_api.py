"""
Test complet de l'API après enrichissement
"""
import requests

print("=" * 80)
print("TEST API M54 - APRÈS ENRICHISSEMENT")
print("=" * 80)
print()

# Test 1: Backend accessible?
try:
    r = requests.get("http://localhost:8000/health", timeout=2)
    print(f"[OK] Backend accessible: {r.json()}")
except Exception as e:
    print(f"[ERREUR] Backend non accessible: {e}")
    print("Assurez-vous que start_app.bat est lancé!")
    exit(1)

# Test 2: Login
try:
    r = requests.post(
        "http://localhost:8000/auth/login",
        data={"username": "admin", "password": "123"},
        timeout=5
    )
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("[OK] Login réussi")
    else:
        print(f"[ERREUR] Login échoué: {r.status_code} - {r.text}")
        exit(1)
except Exception as e:
    print(f"[ERREUR] Login impossible: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test 3: Dashboard stats
print("\n--- TEST DASHBOARD ---")
try:
    r = requests.get("http://localhost:8000/dashboard/stats", headers=headers, timeout=5)
    if r.status_code == 200:
        stats = r.json()
        print(f"[OK] Total offres: {stats.get('total_offers', 0)}")
        print(f"[OK] Acceptées: {stats.get('accepted', 0)}")
        print(f"[OK] Déclinées: {stats.get('declined', 0)}")
    else:
        print(f"[ERREUR] Dashboard: {r.status_code}")
        print(f"Réponse: {r.text[:200]}")
except Exception as e:
    print(f"[ERREUR] Dashboard: {e}")

# Test 4: New analytics endpoints
print("\n--- TEST NOUVEAUX ENDPOINTS ---")

# Team performance
try:
    r = requests.get("http://localhost:8000/analytics/team-performance?period=2026-01", headers=headers, timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"[OK] Team Performance: {len(data)} utilisateurs")
    else:
        print(f"[ERREUR] Team Performance: {r.status_code}")
except Exception as e:
    print(f"[ERREUR] Team Performance: {e}")

# Workflow timing
try:
    r = requests.get("http://localhost:8000/analytics/workflow-timing/2024", headers=headers, timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"[OK] Workflow Timing: {len(data)} phases")
    else:
        print(f"[ERREUR] Workflow Timing: {r.status_code}")
except Exception as e:
    print(f"[ERREUR] Workflow Timing: {e}")

# Client loyalty
try:
    r = requests.get("http://localhost:8000/analytics/client-loyalty/2024", headers=headers, timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"[OK] Client Loyalty: {len(data)} clients")
    else:
        print(f"[ERREUR] Client Loyalty: {r.status_code}")
except Exception as e:
    print(f"[ERREUR] Client Loyalty: {e}")

# Test 5: Offers list
print("\n--- TEST LISTE OFFRES ---")
try:
    r = requests.get("http://localhost:8000/offers?skip=0&limit=10", headers=headers, timeout=5)
    if r.status_code == 200:
        offers = r.json()
        print(f"[OK] Offres récupérées: {len(offers)}")
        if offers:
            print(f"[OK] Première offre: ID={offers[0].get('id')}, Client={offers[0].get('client_name', 'N/A')}")
    else:
        print(f"[ERREUR] Offers: {r.status_code}")
        print(f"Réponse: {r.text[:200]}")
except Exception as e:
    print(f"[ERREUR] Offers: {e}")

print("\n" + "=" * 80)
print("FIN DU TEST")
print("=" * 80)
