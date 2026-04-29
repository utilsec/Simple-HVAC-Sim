# Simple HVAC Simulator

A self-contained, single-file simulator that mimics a **Rockwell ControlLogix 5570 (1756-L71)** PLC over Modbus TCP, paired with a Tkinter HMI. Built for hands-on OT/ICS cybersecurity training, Modbus tool exercises, and offensive/defensive technique practice — no real iron required.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Protocol](https://img.shields.io/badge/protocol-Modbus%20TCP-green)
![Use](https://img.shields.io/badge/use-training%20%2F%20lab-orange)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## Overview

This lab spins up two things in a single Python process:

1. **A Modbus TCP server** that impersonates a Rockwell ControlLogix 5570 PLC, complete with a realistic register/coil map covering process control, performance metrics, security state, firmware info, and fault status.
2. **An HMI client** (Tkinter) that connects to the simulated PLC and provides a six-tab operator interface: AC Control, PLC Status, Performance, Security, Diagnostics, and Event Logs.

Background tasks continuously fluctuate CPU usage, memory usage, scan times, battery level, uptime, and active connections. Random security events (failed logins, mode changes, faults) fire on intervals — giving learners a realistic moving target to enumerate, query, attack, defend, and monitor.

Use it to practice Modbus reconnaissance, register/coil enumeration, value tampering, denial-of-control scenarios, and detection engineering — all on your own machine, on your own time, without touching production gear.

---

## What Gets Simulated

**PLC identity (returned via Modbus device identification):**

- Vendor: Rockwell Automation
- Product code: 1756-L71
- Product name: ControlLogix 5570
- Firmware: v21.013
- Serial: 1756L71BWA12345

**Process scenario:** A simple AC control loop. Holding register 4 is the temperature setpoint, register 6 is the current temperature, and coil 3 is the AC unit's on/off state. Logic toggles the AC based on whether current > setpoint.

**Live-fluctuating telemetry:** CPU usage (20–40%), memory usage (35–45%), task scan time (10–15 ms), I/O scan time (6–10 ms), connection counter, battery, uptime, and randomized security events.

---

## Modbus Register & Coil Map

The PLC exposes 70 holding registers and 50 coils. This map is your cheat sheet for crafting Modbus requests against the simulator.

### Holding Registers (Function Code 3 / 6 / 16)

| Register | Purpose | Notes |
|----------|---------|-------|
| 4 | AC setpoint (°F) | Writable; default 72 |
| 6 | Current temperature (°F) | Fluctuates 74–75 |
| 11 | CPU usage (%) | 20–40 normal range |
| 21 | Memory usage (%) | 35–45 normal range |
| 31 | Security mode | 0=Disabled, 1=Basic, 2=Standard, 3=Advanced |
| 32 | Failed login counter | Increments on simulated failed logins |
| 33 | Battery level (%) | Decrements over time |
| 41–43 | Firmware version | Major / Minor / Patch |
| 51 | Active connections | 1–3 typical |
| 61 | Uptime (hours) | Increments hourly |
| 62 | Task scan time (ms) | 10–15 typical |
| 63 | I/O scan time (ms) | 6–10 typical |

### Coils (Function Code 1 / 5 / 15)

| Coil | Purpose | Notes |
|------|---------|-------|
| 3 | AC unit state | 1=On, 0=Off (driven by control logic) |
| 11 | Security enabled | 1=Enabled |
| 21 | Processor mode | 1=RUN, 0=PROGRAM |
| 31 | Force active | 1=Forces enabled on outputs |
| 41 | Minor fault | 1=Minor fault present |
| 42 | Major fault | 1=Major fault present |

---

## Prerequisites

- Python 3.8 or newer
- `pymodbus` (3.x branch — the script uses `pymodbus.server.async_io` and the 3.x client API)
- `tkinter` — bundled with most Python distributions; on some Linux installs you may need `sudo apt install python3-tk`

The remaining imports (`asyncio`, `threading`, `datetime`, `time`, `random`, `logging`) are all standard library.

---

## Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/simple-hvac-simulator.git
cd simple-hvac-simulator

# (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows

# Install dependencies
pip install pymodbus
```

---

## Usage

### Default (port 502)

Modbus TCP runs on TCP/502, which is a privileged port on Linux and macOS. Either launch with elevated privileges:

```bash
sudo python OT_Pentest_Sim_Lab_1_1.py        # Linux/macOS
python OT_Pentest_Sim_Lab_1_1.py             # Windows (run terminal as Admin)
```

### Non-privileged alternative

If you'd rather not run as root/admin, change both occurrences of `502` in the source to `15020` (one in `StartAsyncTcpServer`, one in `ModbusTcpClient`) and run as a regular user. Any external Modbus client will need to target the same port.

When the script starts:
1. The Modbus TCP server boots in a background thread and begins listening on `0.0.0.0:502`.
2. Background simulation tasks start fluctuating telemetry and firing random events.
3. The Tkinter HMI window opens and connects to `127.0.0.1:502`.

Close the HMI window to shut everything down cleanly.

---

## Lab Exercise Ideas

A few things to try once it's running. The point is to practice tradecraft, build muscle memory, and validate detections against a target you fully control.

**Reconnaissance**
- `nmap -sV -p 502 <ip>` — confirm Modbus TCP is open and grab service info
- `nmap --script modbus-discover -p 502 <ip>` — pull device identification fields
- Run `plcscan` and compare what it sees against the ground truth in this README

**Enumeration**
- Use `mbtget`, `modbus-cli`, or `pymodbus` REPL to read the full register and coil ranges
- Map out which addresses respond and which return errors
- Watch which values change over time (CPU, memory, scan times) vs. which stay static (firmware version)

**Manipulation**
- Write to the AC setpoint (register 4) and observe the AC coil flip
- Flip the processor mode coil (21) from RUN to PROGRAM — a real-world high-impact action
- Toggle force status (coil 31) and clear/set fault coils (41, 42)
- Reset the failed login counter (register 32)

**Detection & monitoring**
- Point Wireshark at loopback or your VM interface and capture Modbus traffic
- Build Snort/Suricata or Zeek rules for unauthorized writes to processor mode or security mode registers
- Tune SIEM correlations for the warning-level log lines this script emits (`SECURITY_ALERT`, `CONFIG_CHANGE`, `FAULT_ALERT`)

**Defensive engineering**
- Practice baselining "normal" register behavior so anomalies stand out
- Write a script that polls register 32 and alerts on any non-zero value
- Capture a clean PCAP and a tampered PCAP for training datasets

---

## HMI Tabs

The operator interface mirrors what you'd expect to see in a real ICS environment:

- **AC Control** — setpoint entry, current temperature, AC status indicator
- **PLC Status** — processor mode, force status, fault indicators, uptime, active connections
- **Performance** — CPU and memory progress bars, task and I/O scan times
- **Security** — security mode selector, failed login counter, login reset
- **Diagnostics** — battery level, system diagnostics runner, counter reset
- **Event Logs** — categorized event stream (Security, Configuration, Faults, Connections, System) with filtering, clear, and export

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Python Process                     │
│                                                     │
│  ┌────────────────────┐    ┌─────────────────────┐  │
│  │  Modbus TCP Server │    │   Tkinter HMI       │  │
│  │  (asyncio thread)  │◄──►│   (main thread)     │  │
│  │  port 502          │    │   ModbusTcpClient   │  │
│  └─────────┬──────────┘    └─────────────────────┘  │
│            │                                        │
│  ┌─────────▼──────────┐                             │
│  │  Background tasks  │                             │
│  │  - CPU/memory sim  │                             │
│  │  - Scan times      │                             │
│  │  - Battery/uptime  │                             │
│  │  - Security events │                             │
│  │  - AC control loop │                             │
│  └────────────────────┘                             │
└─────────────────────────────────────────────────────┘
              ▲
              │ Modbus TCP / 502
              │
         External tools
   (nmap, plcscan, mbtget, custom)
```

External Modbus clients connect to the same port the HMI uses — both speak vanilla Modbus TCP, so anything that talks Modbus will work.

---

## Disclaimer

This project is for **educational and authorized testing purposes only**. It is intentionally insecure, and is meant to be run on isolated lab machines or VMs that you own.

Do not point real-world Modbus tools at devices, networks, or systems you do not own or have explicit written authorization to test. Pentesting against production OT/ICS environments without authorization is illegal in most jurisdictions and can have serious safety consequences for the physical processes those systems control.

You are solely responsible for how you use this code.

---

## Contributing

Issues, PRs, and exercise contributions are welcome. Some ideas worth adding:

- Additional protocols (EtherNet/IP CIP, S7comm, DNP3) on the same simulated device
- Configurable register map via JSON/YAML
- Replay-able attack scenarios (`--scenario fault-injection`, `--scenario credential-spray`)
- Detection rule starter packs (Suricata, Zeek, Snort)

---

## License

Add a license file (MIT, Apache 2.0, or similar) to declare reuse terms. Until then, all rights reserved by default.

---

## Author

Built for hands-on OT/ICS cybersecurity training and content. If this saves you from spinning up a physical PLC for a Modbus exercise, mission accomplished.
