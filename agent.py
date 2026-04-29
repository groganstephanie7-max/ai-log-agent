import re
import json
from collections import defaultdict
from datetime import datetime
import time   # ← ADD THIS LINE

pattern = r"Interface\s+([\w\/\.\-]+),\s+changed state to\s+(up|down)"

with open("rules.json", "r") as config_file:
    config = json.load(config_file)

critical_interfaces = config["critical_interfaces"]
flap_threshold = config["flap_threshold"]

with open("topology.json", "r") as topo_file:
    topology = json.load(topo_file)

history = defaultdict(list)

interface_map = {
    "GigabitEthernet0/1": "Firewall-1"
}

backup_map = {
    "Firewall-1": ["Backup-WAN", "LTE-Failover"]
}

backup_status = {
    "Backup-WAN": "DOWN",
    "LTE-Failover": "UP"
}

with open("logs.txt", "r") as file:
    for line in file:
        line = line.strip()
        match = re.search(pattern, line)

        if match:
            interface = match.group(1)
            state = match.group(2)

            node = interface_map.get(interface, "Unknown")
            neighbors = topology.get(node, {}).get("neighbors", [])

           
            time.sleep(0)
            history[interface].append((state, datetime.now()))
            change_count = len(history[interface])

            prediction = None
            selected_backup = None

            recent = history[interface][-5:]

            changes = 0
            for i in range(1, len(recent)):
                if recent[i][0] != recent[i - 1][0]:
                     changes += 1
            time_diffs = []

            for i in range(1, len(recent)):
                diff = (recent[i][1] - recent[i - 1][1]).total_seconds()
                time_diffs.append(diff)

            avg_time = sum(time_diffs) / len(time_diffs) if time_diffs else 999
            instability_score = changes / max(len(recent) - 1, 1)

            if len(recent) >= 4 and instability_score >= 0.75 and avg_time < 5:
                prediction = "flapping"
            elif len(recent) >= 4 and instability_score >= 0.5:
                prediction = "unstable" 

            if change_count >= flap_threshold:
                severity = "CRITICAL (FLAPPING)"
            elif state == "down":
                if interface in critical_interfaces:
                    severity = "CRITICAL"
                else:
                    severity = "WARNING"
            else:
                severity = "INFO"

            if state == "down" and interface in critical_interfaces:
                risk = "HIGH"
                reason = f"{node} is unstable and may impact {', '.join(neighbors)}"
            elif prediction == "unstable":
                risk = "MEDIUM"
                reason = "Interface is showing signs of instability"
            else:
                risk = "LOW"
                reason = "Interface is currently stable"

            print(f"{severity}: {interface} ({node}) is {state.upper()} (events={change_count})")
            print(f"Risk Level: {risk}")
            print(f"Reason: {reason}")
            print(f"Avg Time Between Events: {avg_time:.2f}s")

            if risk == "HIGH":
                backups = backup_map.get(node, [])

                for backup in backups:
                    status = backup_status.get(backup, "UNKNOWN")
                    print(f"Backup Status: {backup} is {status}")

                    if status == "UP":
                        selected_backup = backup
                        break

                if selected_backup:
                    print(f"Recommended Action: Prepare failover to {selected_backup}")

                    if prediction == "flapping":
                        print(f"ACTION: FAILOVER TRIGGERED → {selected_backup}")
                    else:
                        print(f"Action: Simulating failover readiness for {selected_backup}")
                else:
                    print("Recommended Action: DO NOT FAILOVER - no backup path is available")

            elif risk == "MEDIUM":
                print("Recommended Action: Monitor interface and verify configuration")

            else:
                print("Recommended Action: No action needed")

            if prediction == "flapping":
                print("Prediction: HIGH instability — likely outage soon")
            elif prediction == "unstable":
                print("Warning: Interface becoming unstable")

            if state == "down" and neighbors:
                print(f"Possible impact: {', '.join(neighbors)} may be at risk")

            print("-" * 40)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_entry = {
                "timestamp": timestamp,
                "interface": interface,
                "node": node,
                "state": state,
                "severity": severity,
                "event_count": change_count,
                "possible_impact": neighbors,
                "risk": risk,
                "selected_backup": selected_backup,
                "prediction": prediction
            }

            with open("audit_log.txt", "a") as audit:
                audit.write(json.dumps(log_entry) + "\n")