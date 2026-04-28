import re
import json
from collections import defaultdict
from datetime import datetime

with open("rules.json", "r") as config_file:
    config = json.load(config_file)

critical_interfaces = config["critical_interfaces"]
flap_threshold = config["flap_threshold"]

pattern = r"Interface\s+([\w\/\.\-]+),\s+changed state to\s+(up|down)"

history = defaultdict(list)

with open("logs.txt", "r") as file:
    for line in file:
        line = line.strip()
        match = re.search(pattern, line)

        if match:
            interface = match.group(1)
            state = match.group(2)

            history[interface].append(state)
            change_count = len(history[interface])

            if change_count >= flap_threshold:
                severity = "CRITICAL (FLAPPING)"
            elif state == "down":
                if interface in critical_interfaces:
                    severity = "CRITICAL"
                else:
                    severity = "WARNING"
            else:
                severity = "INFO"

            message = f"{severity}: {interface} is {state.upper()} (events={change_count})"

            print(message)
            print("-" * 40)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "interface": interface,
                "state": state,
                "severity": severity,
                "event_count": change_count
            }

            with open("audit_log.txt", "a") as audit:
                audit.write(json.dumps(log_entry) + "\n")