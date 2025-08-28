# Google Chronicle (Google SecOps) Threat Detection Lab

Hands-on lab you can run in your own Google Security Operations (Chronicle SIEM) tenant. You will:

- **Ingest** synthetic **UDM** events via the **Dataplane Ingestion API**.
- **Deploy** several **YARA‑L 2.0** detection rules (multi-event and single-event).
- **Test** and **tune** detections using the Rules Editor.
- **Hunt** the injected activity with UDM Search.

> Works with Google Security Operations (Chronicle SIEM) as of 2025-08-28.
>
> This repo does **not** depend on any third‑party datasets and is safe to run in a test tenant.

## Repo layout

```
data/        # UDM sample events (JSONL)
detections/  # YARA-L 2.0 rules (*.yaral)
scripts/     # Helper scripts to send UDM to the Dataplane API
dashboards/  # (optional) dashboard starter YAML
LAB.md       # Step-by-step lab guide
README.md    # You are here
```

## Prereqs

- Access to a Google SecOps (Chronicle SIEM) instance.
- A **service account** with the **Chronicle API Editor** role and JSON key.
- Your instance coordinates: **PROJECT_ID**, **LOCATION** (e.g., `us`, `europe`), **INSTANCE_ID** (UUID).
- Python 3.9+ on a workstation with `requests` and `google-auth` packages.

## Quick start

1) Authenticate and set environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json
export CHRONICLE_PROJECT_ID="your-project-id"
export CHRONICLE_LOCATION="us"            # or your regional code
export CHRONICLE_INSTANCE_ID="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
```

2) Send the included UDM sample events:

```bash
python3 scripts/send_udm.py data/udm_scenarios.jsonl
```

3) In the Google SecOps UI → **Detections → Rules** → **New**, paste any file from `detections/*.yaral`, then **Test rule** and **Save**.

4) Use **UDM Search** to verify hits. The rule headers in `LAB.md` include example UDM searches.

## What you’ll detect

- **SSH brute force** that ends in a success
- **Encoded PowerShell** execution (Windows)
- **Suspicious DNS** queries with very long labels (exfil behavior)

## MITRE ATT&CK (example mappings)

- Brute Force: **T1110**
- Command & Scripting Interpreter: **T1059** (PowerShell: **T1059.001**)
- Exfiltration Over Unencrypted/Unusual Protocol (DNS): **T1048 / T1041**

## Notes

- The synthetic logs are already in **UDM**. You can also adapt the sender to wrap non‑UDM logs via `events:import` or `logs:import` endpoints.
- Use the **Rules Editor → Test rule** to validate and tune before enabling alerting.
- Prefer **data tables** for large allow/deny lists; reference lists are being phased out in 2025.

---

Happy hunting!
