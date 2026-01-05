import requests
import json

print("=== TEST COMPLET DE L'API M54 ===\n")

# Test 1: Backend is running?
try:
    r = requests.get("http://localhost:8000/docs", timeout=2)
    print("[OK] Backend est accessible sur localhost:8000")
except:
    print("[ERREUR] Backend n'est PAS accessible sur localhost:8000")
    print("Verifiez que start_app.bat est bien lance!")
    exit(1)

# Test 2: Can we login?
try:
    r = requests.post(
        "http://localhost:8000/auth/login",
        data={"username": "admin", "password": "123"},
        timeout=5
    )
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("[OK] Login reussi")
    else:
        print(f"[ERREUR] Login echoue: {r.status_code} - {r.text}")
        exit(1)
except Exception as e:
    print(f"[ERREUR] Impossible de se connecter: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test 3: Dashboard stats
try:
    r = requests.get("http://localhost:8000/dashboard/stats", headers=headers, timeout=5)
    if r.status_code == 200:
        stats = r.json()
        print(f"\n[DASHBOARD]")
        print(f"  Total offres: {stats.get('total_offers', 0)}")
        print(f"  Acceptees: {stats.get('accepted', 0)}")
        print(f"  Declinees: {stats.get('declined', 0)}")
    else:
        print(f"[ERREUR] Dashboard: {r.status_code} - {r.text}")
except Exception as e:
    print(f"[ERREUR] Dashboard: {e}")

# Test 4: Analytics reasons
try:
    r = requests.get("http://localhost:8000/analytics/reasons/2024", headers=headers, timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"\n[ANALYTICS REASONS 2024]")
        print(f"  Declined reasons: {len(data.get('declined_reasons', []))}")
        print(f"  Not accepted reasons: {len(data.get('not_accepted_reasons', []))}")
        if data.get('declined_reasons'):
            print(f"  Premier motif decline: {data['declined_reasons'][0]}")
    else:
        print(f"[ERREUR] Analytics: {r.status_code} - {r.text}")
except Exception as e:
    print(f"[ERREUR] Analytics: {e}")

print("\n=== FIN DU TEST ===")
