import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

# Where is Grafana?
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")

# Admin creds (from .env or defaults)
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD", "admin")

# Postgres (inside Docker network)
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB", "Bhramana")
PG_USER = os.getenv("POSTGRES_USER", "admin")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

# Path to dashboard.json
DASHBOARD_PATH = os.getenv(
    "GRAFANA_DASHBOARD_PATH",
    str(Path(__file__).with_name("dashboard.json"))
)

auth = HTTPBasicAuth(GRAFANA_USER, GRAFANA_PASSWORD)
headers = {"Content-Type": "application/json"}

def wait_for_grafana(timeout=120):
    """Wait until Grafana API is healthy before provisioning."""
    deadline = time.time() + timeout
    health_url = f"{GRAFANA_URL}/api/health"
    while time.time() < deadline:
        try:
            r = requests.get(health_url, auth=auth, timeout=5)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(2)
    return False

def create_or_update_datasource():
    """Create/update the 'PostgreSQL' datasource pointing to postgres:5432."""
    payload = {
        "name": "PostgreSQL",
        "type": "postgres",
        "url": f"{PG_HOST}:{PG_PORT}",
        "access": "proxy",
        "user": PG_USER,
        "database": PG_DB,
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {
            "sslmode": "disable",
            "postgresVersion": 1300
        },
        "secureJsonData": {"password": PG_PASSWORD},
    }

    # Update if exists, else create
    getr = requests.get(f"{GRAFANA_URL}/api/datasources/name/{payload['name']}",
                        auth=auth)
    if getr.status_code == 200:
        ds_id = getr.json()["id"]
        print(f"Updating existing datasource (id={ds_id})")
        upr = requests.put(f"{GRAFANA_URL}/api/datasources/{ds_id}",
                           headers=headers, json=payload, auth=auth)
        if upr.status_code not in (200, 202):
            raise RuntimeError(f"Update datasource failed: {upr.status_code} {upr.text}")
        return upr.json().get("datasource", {}).get("uid") or upr.json().get("uid")

    print("Creating new datasource")
    cr = requests.post(f"{GRAFANA_URL}/api/datasources",
                       headers=headers, json=payload, auth=auth)
    if cr.status_code not in (200, 201):
        raise RuntimeError(f"Create datasource failed: {cr.status_code} {cr.text}")
    return cr.json().get("datasource", {}).get("uid") or cr.json().get("uid")

def create_dashboard(datasource_uid):
    """Import dashboard.json and rewrite datasource UID references."""
    dash_path = Path(DASHBOARD_PATH)
    if not dash_path.exists():
        raise FileNotFoundError(f"Dashboard file not found at: {dash_path}")
    with dash_path.open("r", encoding="utf-8") as f:
        dashboard_json = json.load(f)

    # Remove problematic keys
    for k in ("id", "uid", "version"):
        dashboard_json.pop(k, None)

    # Rewrite datasource UID
    panels_updated = 0
    for panel in dashboard_json.get("panels", []):
        if isinstance(panel.get("datasource"), dict):
            panel["datasource"]["uid"] = datasource_uid
            panels_updated += 1
        for tgt in panel.get("targets", []) or []:
            if isinstance(tgt.get("datasource"), dict):
                tgt["datasource"]["uid"] = datasource_uid
                panels_updated += 1

    payload = {"dashboard": dashboard_json, "overwrite": True,
               "message": "Provisioned by init.py"}

    r = requests.post(f"{GRAFANA_URL}/api/dashboards/db",
                      headers=headers, json=payload, auth=auth)
    if r.status_code != 200:
        raise RuntimeError(f"Create dashboard failed: {r.status_code} {r.text}")

    print(f"Dashboard created/updated. Panels updated: {panels_updated}")
    return r.json().get("uid")

def main():
    print(f"Waiting for Grafana at {GRAFANA_URL} ...")
    if not wait_for_grafana():
        raise RuntimeError("Grafana API did not become ready in time.")

    ds_uid = create_or_update_datasource()
    dash_uid = create_dashboard(ds_uid)
    print(f"Done. Dashboard UID: {dash_uid}")

if __name__ == "__main__":
    main()
