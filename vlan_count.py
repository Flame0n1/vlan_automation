#!/usr/bin/env python3
"""
vlan_count.py — SSH into switches, run 'show vlan brief count', save CSV, flag high-VLAN AR-720DP24S2F.
"""

import re
import sys
import csv
import getpass
import paramiko
from pathlib import Path

# Base models to flag when VLAN count ≥ threshold
FLAG_MODELS = ["AR-720DP24S2F"]
FLAG_THRESHOLD = 509

def parse_host_line(line: str):
    """
    Given a line like:
      AR-720DP24S2F-I-1-ATP02-US - 10.64.116.48 - Workshop ...
    return (hostname, ip).
    """
    m = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', line)
    if not m:
        return None, None
    ip = m.group(1)
    # hostname is everything before the IP (strip trailing separators)
    hostname = line[:m.start()].rstrip(" -")
    return hostname, ip

def run_command(ip, username, password, command="show vlan brief count"):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode(errors='ignore')
        err = stderr.read().decode(errors='ignore')
        return out.strip(), err.strip()
    except Exception as e:
        return "", str(e)
    finally:
        client.close()

def extract_vlan_count(text: str):
    """
    From:
      "Number of existing VLANs           : 529"
    return integer 529, or None if not found.
    """
    m = re.search(r'Number of existing VLANs\s*:\s*(\d+)', text)
    return int(m.group(1)) if m else None

def should_flag(hostname: str, count: int):
    """
    True if hostname matches a flagged model prefix
    AND count ≥ FLAG_THRESHOLD.
    """
    if count is None:
        return False
    for model in FLAG_MODELS:
        if hostname.startswith(model) and count >= FLAG_THRESHOLD:
            return True
    return False

def main():
    print("\n=== VLAN Count & Flag Automation ===\n")
    username = input("LDAP Username: ").strip()
    password = getpass.getpass("LDAP Password: ")

    path = input("Path to switches file: ").strip()
    file = Path(path)
    if not file.is_file():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    # build list of {hostname, ip}
    entries = []
    for raw in file.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        hostname, ip = parse_host_line(line)
        if not ip:
            # skip any header or comment lines
            continue
        entries.append((hostname, ip))

    if not entries:
        print("ERROR: No valid switch entries found.")
        sys.exit(1)

    results = []
    for hostname, ip in entries:
        print(f"[*] Connecting to {hostname} ({ip}) ... ", end="", flush=True)
        out, err = run_command(ip, username, password)
        if err:
            print("FAIL")
            count = None
            error = err
        else:
            print("OK")
            count = extract_vlan_count(out)
            error = ""
        flag = should_flag(hostname, count)
        results.append({
            "hostname": hostname,
            "ip": ip,
            "count": count if count is not None else "",
            "error": error,
            "flagged": "⚠️" if flag else ""
        })

    csv_file = "vlan_count_flags.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["hostname","ip","count","error","flagged"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Results written to {csv_file}\n")

if __name__ == "__main__":
    main()