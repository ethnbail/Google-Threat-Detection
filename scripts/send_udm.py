#!/usr/bin/env python3
"""
Send UDM events to Google SecOps (Chronicle) via the Dataplane Ingestion API.

Env vars:
  GOOGLE_APPLICATION_CREDENTIALS : path to service account JSON
  CHRONICLE_PROJECT_ID           : GCP project id bound to your SecOps instance
  CHRONICLE_LOCATION             : region short name (e.g., "us", "europe")
  CHRONICLE_INSTANCE_ID          : SecOps instance id (UUID)

Usage:
  python3 scripts/send_udm.py data/udm_scenarios.jsonl
"""
import os, sys, json, time
from typing import List
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

SCOPE = ["https://www.googleapis.com/auth/cloud-platform"]

def load_events(path: str) -> List[dict]:
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append({"udm": json.loads(line)})
    return events

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/send_udm.py <path-to-jsonl>", file=sys.stderr)
        sys.exit(1)

    project_id = os.environ.get("CHRONICLE_PROJECT_ID")
    location   = os.environ.get("CHRONICLE_LOCATION", "us")
    instance   = os.environ.get("CHRONICLE_INSTANCE_ID")
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not all([project_id, location, instance, creds_path]):
        print("Missing one or more env vars: CHRONICLE_PROJECT_ID, CHRONICLE_LOCATION, CHRONICLE_INSTANCE_ID, GOOGLE_APPLICATION_CREDENTIALS", file=sys.stderr)
        sys.exit(2)

    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPE)
    authed = AuthorizedSession(credentials)

    parent = f"projects/{project_id}/locations/{location}/instances/{instance}"
    url = f"https://chronicle.{location}.rep.googleapis.com/v1alpha/{parent}/events:import"

    events = load_events(sys.argv[1])
    # Send in small batches (<= 100 events per best practice)
    batch_size = 50
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        body = {"inlineSource": {"events": batch}}
        r = authed.post(url, json=body, timeout=60)
        if r.status_code != 200:
            print(f"[!] Error {r.status_code}: {r.text}", file=sys.stderr)
            sys.exit(3)
        print(f"[+] Imported {len(batch)} events: {r.text}")

if __name__ == "__main__":
    main()
