# AI Log Monitoring Agent

A lightweight, config-driven network log monitoring agent built in Python.

## How to Run

Ensure you have Python 3 installed.

```bash
py agent.py
```

Make sure `logs.txt` and `rules.json` are in the same directory as `agent.py`.

## Overview
This project is a Python-based log monitoring agent that detects network interface state changes from Cisco IOS logs. It identifies critical failures and flapping behavior, and records structured audit logs for analysis.

## Features
- Parses Cisco IOS log files
- Detects interface up/down events using regex
- Classifies severity (INFO, WARNING, CRITICAL)
- Identifies flapping interfaces based on configurable thresholds
- Outputs structured JSON audit logs
- Config-driven design using external rules.json

## How It Works
1. Reads log data from `logs.txt`
2. Matches interface state changes using regex
3. Tracks event history per interface
4. Determines severity based on:
   - Interface importance
   - Event frequency (flapping detection)
5. Prints alerts to console
6. Writes structured events to `audit_log.txt`

## Configuration
Edit `rules.json` to control behavior:

```json
{
  "critical_interfaces": ["GigabitEthernet0/1"],
  "flap_threshold": 3
}
```

## Example Output

```text
CRITICAL: GigabitEthernet0/1 is DOWN (events=1)
INFO: GigabitEthernet0/1 is UP (events=2)
CRITICAL (FLAPPING): GigabitEthernet0/1 is DOWN (events=3)
CRITICAL (FLAPPING): GigabitEthernet0/1 is UP (events=4)
```

## Technologies Used

- Python
- Regex
- JSON logging

## Future Improvements

- Time-based flapping detection
- Real-time log streaming
- Alert integrations (Slack, email)
- Web dashboard

## Author

Stephanie Grogan