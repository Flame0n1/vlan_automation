README
# 🔌 VLAN Count Automation Tool

This script automates connecting to switches (SSH), counting configured VLANs, and exporting results to a CSV file. It flags certain switch models if VLAN count exceeds a defined threshold.

## 📂 Setup Instructions

1. Clone or copy the script folder to your machine.  
2. Create a Python virtual environment and activate it:  

   cd vlan_automation
   python3 -m venv venv
   source venv/bin/activate

   Install requirements:
   pip install paramiko


🧾 How to Format switches.txt

Each line should be in the following format (with a trailing $ at end):

EXAMPLE: <HOSTNAME> - <IP ADDRESS> - <DESCRIPTION> $

The $ marker is required on each valid switch line. To add it automatically:
    macOS:  sed -i '' 's/$/ $/' switches.txt
    Linux: sed -i 's/$/ $/' switches.txt


Run the script:
python vlan_count.py

You will be prompted for your LDAP username and password. The script will read switches.txt, connect to each switch, retrieve VLAN count, flag models AR-720DP24S2F when VLAN count ≥ 509, and write results to vlan_count_flags.csv.

Built by Matthew Flame


