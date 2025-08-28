# Google Chronicle Threat Detection Lab — Step‑by‑Step

## 0) Install dependencies
```bash
python3 -m pip install --upgrade google-auth requests
```

## 1) Configure environment

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json
export CHRONICLE_PROJECT_ID="your-project-id"
export CHRONICLE_LOCATION="us"            # e.g., us, europe, asia-southeast1
export CHRONICLE_INSTANCE_ID="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
```

> Tip: These values correspond to the instance your Google SecOps rep provisioned.
> You can use regional endpoints — this lab uses the **Dataplane Ingestion API** format:
> `https://chronicle.{region}.rep.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/instances/{INSTANCE_ID}/events:import`

## 2) Load the sample UDM data
```bash
python3 scripts/send_udm.py data/udm_scenarios.jsonl
```

Expected output: HTTP 200 with an ingestion batch id. Within a minute, you should see the events in **UDM Search**.

## 3) Import rules and run “Test rule”

Open **Detections → Rules → New** and paste one of the files from `detections/`:

- `bruteforce_ssh_success_after_fails.yaral`
- `suspicious_powershell_encodedcommand.yaral`
- `dns_exfil_long_label.yaral`

Click **Test rule**, verify matches, then **Save** (enable alerting if desired).

## 4) Verify in UDM Search (example queries)

- SSH failures and success:
```
metadata.event_type = "USER_LOGIN"
and target.application = "sshd"
and (security_result.action = "BLOCK" or security_result.action = "ALLOW")
```

- PowerShell EncodedCommand:
```
metadata.log_type = "POWERSHELL" or
re.regex(target.process.command_line, "(?i)-enc(odedcommand)?\s+[A-Za-z0-9+/=]{20,}")
```

- DNS long labels:
```
metadata.event_type = "NETWORK_DNS" and
strings.length(network.dns.questions.name) > 60
```

## 5) (Optional) Build a quick dashboard

Use the sidebar **Dashboards → Add → Import Dashboard** and start from the YAML in `dashboards/`.
Adjust the queries to your tenant’s field values.

## 6) Cleanup

- Disable the rules or switch them to “no alert” after the lab.
- Delete the test dataset with your standard retention controls (optional).

---

## Troubleshooting

- **401/403** from API: verify service account role *Chronicle API Editor* and the region/instance path.
- **No matches** in Test rule: paste a UDM Search query from above and confirm the dataset exists.
- **Regex fails**: in YARA‑L 2.0, `re.regex(field, "pattern")` returns true on substring matches; you do not need `.*` prefix/suffix.
