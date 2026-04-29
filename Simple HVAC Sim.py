#!/usr/bin/env python3
"""
============================================================
This script was vibe coded by Mike Holcomb of UtilSec, LLC.

Additional contribution by unknown individual.

LinkedIn : https://www.linkedin.com/in/mikeholcomb
Website  : https://mikeholcomb.com
============================================================
"""
import asyncio

import tkinter as tk

from tkinter import ttk

from threading import Thread

from datetime import datetime

from pymodbus.server.async_io import StartAsyncTcpServer

from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

from pymodbus.device import ModbusDeviceIdentification

from pymodbus.client import ModbusTcpClient

import time

import random

import logging

 

# Configure logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

 

# -------------------- Modbus Simulator Setup --------------------

 

# Extended register map to simulate Rockwell PLC data points

# Holding Registers (Read/Write)

# 1-10: Original AC control registers

# 11-20: CPU usage and performance metrics

# 21-30: Memory usage statistics

# 31-40: Security settings

# 41-50: Firmware and version information

# 51-60: Connection tracking

# 61-70: System status and diagnostics

 

# Coils (Read/Write)

# 1-10: Original AC control coils

# 11-20: Security mode indicators

# 21-30: Processor mode indicators

# 31-40: Force status indicators

# 41-50: Fault status indicators

 

slave_context = ModbusSlaveContext(

    co=ModbusSequentialDataBlock(1, [0] * 50),  # 50 coils

    hr=ModbusSequentialDataBlock(1, [0] * 70),  # 70 holding registers

)

context = ModbusServerContext(slaves=slave_context, single=True)

 

# Simulated PLC information

PLC_INFO = {

    "family": "ControlLogix",

    "model": "5570 (1756-L71)",

    "firmware": "v21.013",

    "serial": "1756L71BWA12345",

    "vendor": "Rockwell Automation",

    "security_features": "Standard"

}

 

# Initialize PLC data

def initialize_plc_data():

    # Original AC control registers

    registers = context[0].getValues(3, 1, count=70)

    registers[3] = 72  # Register #4 = AC setpoint (index 3)

    registers[5] = 74  # Register #6 = current temp (index 5)

   

    # CPU usage (register 11) - 0-100%

    registers[10] = 25  # 25% CPU usage

   

    # Memory usage (register 21) - percentage

    registers[20] = 40  # 40% memory usage

   

    # Security mode (register 31) - 0=disabled, 1=basic, 2=standard, 3=advanced

    registers[30] = 2  # Standard security

   

    # Failed login attempts (register 32)

    registers[31] = 0

   

    # Battery status (register 33) - percentage

    registers[32] = 95  # 95% battery

   

    # Firmware version major.minor.patch (registers 41-43)

    registers[40] = 21  # Major

    registers[41] = 0   # Minor

    registers[42] = 13  # Patch

   

    # Active connections (register 51)

    registers[50] = 1  # 1 active connection

   

    # System uptime in hours (register 61)

    registers[60] = 720  # 30 days uptime

   

    # Task scan time in ms (register 62)

    registers[61] = 12  # 12ms scan time

   

    # I/O scan time in ms (register 63)

    registers[62] = 8   # 8ms I/O scan time

   

    context[0].setValues(3, 1, registers)

   

    # Initialize coils

    coils = context[0].getValues(1, 1, count=50)

    coils[2] = 0  # AC status (off initially)

    coils[10] = 1  # Security enabled

    coils[20] = 1  # Processor in RUN mode (1=run, 0=program)

    coils[30] = 0  # No forces active

    coils[40] = 0  # No faults active

    coils[41] = 0  # No minor faults

    coils[42] = 0  # No major faults

    context[0].setValues(1, 1, coils)

 

# Simulate CPU fluctuation

async def fluctuate_cpu_usage():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        # Normal CPU usage between 20-40%

        registers[10] = random.randint(20, 40)

        context[0].setValues(3, 1, registers)

        await asyncio.sleep(10)

 

# Simulate memory usage changes

async def fluctuate_memory_usage():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        # Memory usage between 35-45%

        registers[20] = random.randint(35, 45)

        context[0].setValues(3, 1, registers)

        await asyncio.sleep(15)

 

# Simulate connection count changes

async def fluctuate_connections():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        # Between 1-3 connections

        registers[50] = random.randint(1, 3)

        context[0].setValues(3, 1, registers)

        await asyncio.sleep(30)

 

# Simulate scan time fluctuations

async def fluctuate_scan_times():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        # Task scan time between 10-15ms

        registers[61] = random.randint(10, 15)

        # I/O scan time between 6-10ms

        registers[62] = random.randint(6, 10)

        context[0].setValues(3, 1, registers)

        await asyncio.sleep(5)

 

# Simulate battery level decrease

async def update_battery():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        # Slowly decrease battery level

        if registers[32] > 0:

            registers[32] -= 1

        context[0].setValues(3, 1, registers)

        await asyncio.sleep(3600)  # Update every hour

 

# Simulate uptime counter

async def update_uptime():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        # Increment uptime by 1 hour

        registers[60] += 1

        context[0].setValues(3, 1, registers)

        await asyncio.sleep(3600)  # Update every hour

 

# Original AC temperature fluctuation

async def fluctuate_register_6():

    toggle = True

    while True:

        registers = context[0].getValues(3, 1, count=70)

        registers[5] = 74 if toggle else 75  # Register #6 = index 5

        context[0].setValues(3, 1, registers)

        toggle = not toggle

        await asyncio.sleep(5)

 

# Original AC logic

async def update_ac_logic():

    while True:

        registers = context[0].getValues(3, 1, count=70)

        setpoint = registers[3]

        current_temp = registers[5]

        coils = context[0].getValues(1, 1, count=50)

        coils[2] = 1 if current_temp > setpoint else 0  # Coil #3 = index 2

        context[0].setValues(1, 1, coils)

        await asyncio.sleep(1)

 

# Simulate security events (login attempts, mode changes)

async def simulate_security_events():

    while True:

        # Wait a random time between 60-300 seconds

        await asyncio.sleep(random.randint(60, 300))

       

        # 10% chance of a security event

        if random.random() < 0.1:

            event_type = random.choice(["login_attempt", "security_mode", "processor_mode", "fault"])

           

            if event_type == "login_attempt":

                # Simulate failed login attempt

                logger.warning("SECURITY_ALERT: Failed login attempt detected")

                # Increment failed login counter (register 32)

                registers = context[0].getValues(3, 1, count=70)

                registers[31] = registers[31] + 1 if registers[31] < 255 else 255

                context[0].setValues(3, 1, registers)

               

            elif event_type == "security_mode":

                # Simulate security mode change

                registers = context[0].getValues(3, 1, count=70)

                old_mode = registers[30]

                new_mode = random.randint(0, 3)

                registers[30] = new_mode

                context[0].setValues(3, 1, registers)

                logger.warning(f"CONFIG_CHANGE: Security mode changed from {old_mode} to {new_mode}")

               

            elif event_type == "processor_mode":

                # Simulate processor mode change (RUN/PROGRAM)

                coils = context[0].getValues(1, 1, count=50)

                old_mode = "RUN" if coils[20] else "PROGRAM"

                coils[20] = not coils[20]

                new_mode = "RUN" if coils[20] else "PROGRAM"

                context[0].setValues(1, 1, coils)

                logger.warning(f"CONFIG_CHANGE: Processor mode changed from {old_mode} to {new_mode}")

               

            elif event_type == "fault":

                # Simulate a fault condition

                coils = context[0].getValues(1, 1, count=50)

                fault_type = random.choice(["minor", "major", "none"])

               

                if fault_type == "minor":

                    coils[41] = 1  # Set minor fault

                    coils[42] = 0  # Clear major fault

                    logger.warning("FAULT_ALERT: Minor fault detected")

                elif fault_type == "major":

                    coils[41] = 0  # Clear minor fault

                    coils[42] = 1  # Set major fault

                    logger.warning("FAULT_ALERT: Major fault detected")

                else:

                    coils[41] = 0  # Clear minor fault

                    coils[42] = 0  # Clear major fault

                    logger.info("FAULT_CLEAR: All faults cleared")

                   

                context[0].setValues(1, 1, coils)

 

# Log access to the PLC

async def log_plc_access():

    last_connection_count = 1

    while True:

        await asyncio.sleep(5)

        registers = context[0].getValues(3, 1, count=70)

        current_connections = registers[50]

       

        if current_connections > last_connection_count:

            logger.info(f"CONNECTION_ALERT: New connection established. Total connections: {current_connections}")

        elif current_connections < last_connection_count:

            logger.info(f"CONNECTION_ALERT: Connection closed. Total connections: {current_connections}")

           

        last_connection_count = current_connections

 

async def start_modbus_server():

    # Initialize PLC data

    initialize_plc_data()

 

    identity = ModbusDeviceIdentification()

    identity.VendorName = "Rockwell Automation"

    identity.ProductCode = "1756-L71"

    identity.ProductName = "ControlLogix 5570"

    identity.MajorMinorRevision = "v21.013"

 

    await asyncio.gather(

        fluctuate_register_6(),

        update_ac_logic(),

        fluctuate_cpu_usage(),

        fluctuate_memory_usage(),

        fluctuate_connections(),

        fluctuate_scan_times(),

        update_battery(),

        update_uptime(),

        simulate_security_events(),

        log_plc_access(),

        StartAsyncTcpServer(

            context=context,

            identity=identity,

            address=("0.0.0.0", 502),  # Change to 15020 if running without admin

        )

    )

 

# -------------------- HMI UI Definition --------------------

 

class ACHMI:

    def __init__(self, root):

        self.root = root

        self.root.title("Industrial Control System HMI")

        self.root.geometry("800x600")  # Larger window for more information

        self.polling = True

 

        # Create tabs for different views

        self.create_tabs()

       

        # Start polling

        self.client = ModbusTcpClient('127.0.0.1', port=502)  # Change to 15020 if needed

        self.connected = self.client.connect()

        self.update_connection_status(self.connected)

 

        self.thread = Thread(target=self.poll_data, daemon=True)

        self.thread.start()

 

    def create_tabs(self):

        # Create notebook for tabs

        self.notebook = ttk.Notebook(self.root)

        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

       

        # AC Control Tab

        self.ac_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.ac_tab, text="AC Control")

        self.setup_ac_tab()

       

        # PLC Status Tab

        self.plc_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.plc_tab, text="PLC Status")

        self.setup_plc_tab()

       

        # Performance Tab

        self.perf_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.perf_tab, text="Performance")

        self.setup_performance_tab()

       

        # Security Tab

        self.security_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.security_tab, text="Security")

        self.setup_security_tab()

       

        # Diagnostics Tab

        self.diag_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.diag_tab, text="Diagnostics")

        self.setup_diagnostics_tab()

       

        # Logs Tab

        self.logs_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.logs_tab, text="Event Logs")

        self.setup_logs_tab()

 

    def setup_ac_tab(self):

    # Create a main frame to center everything

        main_frame = ttk.Frame(self.ac_tab)

        main_frame.pack(expand=True, fill=tk.BOTH)

   

    # Create a centered content frame

        content_frame = ttk.Frame(main_frame)

        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

   

    # Connection status at the top

        self.connection_label = ttk.Label(content_frame, text="Disconnected", foreground="red",

                                     font=("Arial", 12, "bold"))

        self.connection_label.pack(pady=10, anchor=tk.CENTER)

   

    # AC Status display with larger font

        self.status_label = ttk.Label(content_frame, text="AC Unit: Unknown",

                                 font=("Arial", 16, "bold"))

        self.status_label.pack(pady=15, anchor=tk.CENTER)

   

    # Temperature information in a frame

        temp_frame = ttk.Frame(content_frame)

        temp_frame.pack(pady=10, anchor=tk.CENTER)

   

    # Setpoint temperature

        self.setpoint_label = ttk.Label(temp_frame, text="Setpoint Temp: -- °F",

                                   font=("Arial", 14))

        self.setpoint_label.pack(pady=8, anchor=tk.CENTER)

   

    # Current temperature

        self.current_label = ttk.Label(temp_frame, text="Current Temp: -- °F",

                                  font=("Arial", 14))

        self.current_label.pack(pady=8, anchor=tk.CENTER)

   

    # Visual AC status indicator

        indicator_frame = ttk.Frame(content_frame)

        indicator_frame.pack(pady=15, anchor=tk.CENTER)

   

        self.ac_canvas = tk.Canvas(indicator_frame, width=150, height=80, highlightthickness=0)

        self.ac_canvas.pack()

   

    # Larger status box with rounded corners

        self.ac_box = self.ac_canvas.create_rectangle(25, 10, 125, 60, fill="gray", width=2, outline="black")

        self.ac_canvas.create_text(75, 35, text="AC", font=("Arial", 16, "bold"), fill="white")

        self.ac_canvas.create_text(75, 70, text="AC Unit Status", font=("Arial", 10))

   

    # Controls in a frame with better spacing

        control_frame = ttk.LabelFrame(content_frame, text="Temperature Control")

        control_frame.pack(pady=15, anchor=tk.CENTER, ipadx=10, ipady=10)

   

    # Control elements in a grid

        control_grid = ttk.Frame(control_frame)

        control_grid.pack(padx=20, pady=10)

   

        ttk.Label(control_grid, text="Set Setpoint:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)

   

        self.setpoint_input = ttk.Spinbox(control_grid, from_=60, to=85, width=5, font=("Arial", 12))

        self.setpoint_input.grid(row=0, column=1, padx=10, pady=5)

        self.setpoint_input.delete(0, tk.END)

        self.setpoint_input.insert(0, "72")

   

        apply_button = ttk.Button(control_grid, text="Apply", command=self.set_setpoint)

        apply_button.grid(row=0, column=2, padx=10, pady=5)

   

    # Status message and timestamp at the bottom

        status_frame = ttk.Frame(content_frame)

        status_frame.pack(pady=10, anchor=tk.CENTER)

   

        self.setpoint_status = ttk.Label(status_frame, text="", font=("Arial", 10, "italic"), foreground="blue")

        self.setpoint_status.pack(pady=5, anchor=tk.CENTER)

   

        self.timestamp_label = ttk.Label(status_frame, text="Last Updated: --", font=("Arial", 10, "italic"))

        self.timestamp_label.pack(pady=5, anchor=tk.CENTER)


 

    def setup_plc_tab(self):

        # PLC information and status

        frame = ttk.LabelFrame(self.plc_tab, text="PLC Information")

        frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

       

        # Create a two-column layout

        info_frame = ttk.Frame(frame)

        info_frame.pack(fill=tk.X, padx=10, pady=10)

       

        # Left column - PLC model info

        left_frame = ttk.Frame(info_frame)

        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

       

        row = 0

        for label, key in [("Family:", "family"), ("Model:", "model"), ("Firmware:", "firmware"),

                          ("Serial:", "serial"), ("Vendor:", "vendor")]:

            ttk.Label(left_frame, text=label, font=("Arial", 11)).grid(row=row, column=0, sticky="w", pady=2)

            lbl = ttk.Label(left_frame, text=PLC_INFO[key], font=("Arial", 11))

            lbl.grid(row=row, column=1, sticky="w", pady=2)

            setattr(self, f"{key}_label", lbl)

            row += 1

       

        # Right column - Status indicators

        right_frame = ttk.Frame(info_frame)

        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

       

        # Status indicators with colored indicators

        self.create_status_indicator(right_frame, "Processor Status:", "processor_status", 0)

        self.create_status_indicator(right_frame, "Force Status:", "force_status", 1)

        self.create_status_indicator(right_frame, "Fault Status:", "fault_status", 2)

        self.create_status_indicator(right_frame, "Battery Status:", "battery_status", 3)

       

        # System uptime

        ttk.Label(right_frame, text="System Uptime:", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=2)

        self.uptime_label = ttk.Label(right_frame, text="-- hours", font=("Arial", 11))

        self.uptime_label.grid(row=4, column=1, sticky="w", pady=2)

       

        # Active connections

        ttk.Label(right_frame, text="Active Connections:", font=("Arial", 11)).grid(row=5, column=0, sticky="w", pady=2)

        self.connections_label = ttk.Label(right_frame, text="--", font=("Arial", 11))

        self.connections_label.grid(row=5, column=1, sticky="w", pady=2)

       

        # PLC Controls

        controls_frame = ttk.LabelFrame(self.plc_tab, text="PLC Controls")

        controls_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

       

        # Processor mode control

        proc_frame = ttk.Frame(controls_frame)

        proc_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(proc_frame, text="Processor Mode:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.processor_mode_var = tk.StringVar(value="RUN")

        ttk.Radiobutton(proc_frame, text="RUN", variable=self.processor_mode_var, value="RUN").pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(proc_frame, text="PROGRAM", variable=self.processor_mode_var, value="PROGRAM").pack(side=tk.LEFT, padx=5)

        ttk.Button(proc_frame, text="Apply", command=self.set_processor_mode).pack(side=tk.LEFT, padx=5)

       

        # Force control

        force_frame = ttk.Frame(controls_frame)

        force_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(force_frame, text="I/O Force:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.force_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(force_frame, text="Enable Forces", variable=self.force_var).pack(side=tk.LEFT, padx=5)

        ttk.Button(force_frame, text="Apply", command=self.set_force_status).pack(side=tk.LEFT, padx=5)

       

        # Fault control

        fault_frame = ttk.Frame(controls_frame)

        fault_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(fault_frame, text="Fault Control:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        ttk.Button(fault_frame, text="Clear Faults", command=self.clear_faults).pack(side=tk.LEFT, padx=5)

 

    def create_status_indicator(self, parent, text, name, row):

        ttk.Label(parent, text=text, font=("Arial", 11)).grid(row=row, column=0, sticky="w", pady=2)

       

        frame = ttk.Frame(parent)

        frame.grid(row=row, column=1, sticky="w", pady=2)

       

        canvas = tk.Canvas(frame, width=15, height=15)

        canvas.pack(side=tk.LEFT)

        indicator = canvas.create_oval(2, 2, 13, 13, fill="gray")

       

        label = ttk.Label(frame, text="Unknown", font=("Arial", 11))

        label.pack(side=tk.LEFT, padx=5)

       

        setattr(self, f"{name}_indicator", indicator)

        setattr(self, f"{name}_canvas", canvas)

        setattr(self, f"{name}_label", label)

 

    def setup_performance_tab(self):

        # Performance metrics

        frame = ttk.LabelFrame(self.perf_tab, text="Performance Metrics")

        frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

       

        # CPU Usage

        cpu_frame = ttk.Frame(frame)

        cpu_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(cpu_frame, text="CPU Usage:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.cpu_progress = ttk.Progressbar(cpu_frame, length=300, mode="determinate", maximum=100)

        self.cpu_progress.pack(side=tk.LEFT, padx=5)

        self.cpu_value = ttk.Label(cpu_frame, text="0%", font=("Arial", 11))

        self.cpu_value.pack(side=tk.LEFT, padx=5)

       

        # Memory Usage

        mem_frame = ttk.Frame(frame)

        mem_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(mem_frame, text="Memory Usage:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.mem_progress = ttk.Progressbar(mem_frame, length=300, mode="determinate", maximum=100)

        self.mem_progress.pack(side=tk.LEFT, padx=5)

        self.mem_value = ttk.Label(mem_frame, text="0%", font=("Arial", 11))

        self.mem_value.pack(side=tk.LEFT, padx=5)

       

        # Scan Times

        scan_frame = ttk.LabelFrame(self.perf_tab, text="Scan Times")

        scan_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

       

        # Task Scan Time

        ttk.Label(scan_frame, text="Task Scan Time:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.task_scan_label = ttk.Label(scan_frame, text="-- ms", font=("Arial", 11))

        self.task_scan_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

       

        # I/O Scan Time

        ttk.Label(scan_frame, text="I/O Scan Time:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.io_scan_label = ttk.Label(scan_frame, text="-- ms", font=("Arial", 11))

        self.io_scan_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

       

        # Connection Statistics

        conn_frame = ttk.LabelFrame(self.perf_tab, text="Connection Statistics")

        conn_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

       

        # Current Connections

        ttk.Label(conn_frame, text="Current Connections:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.current_conn_label = ttk.Label(conn_frame, text="--", font=("Arial", 11))

        self.current_conn_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

       

        # Max Connections

        ttk.Label(conn_frame, text="Maximum Connections:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.max_conn_label = ttk.Label(conn_frame, text="32", font=("Arial", 11))

        self.max_conn_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

 

    def setup_security_tab(self):

        # Security settings and status

        frame = ttk.LabelFrame(self.security_tab, text="Security Status")

        frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

       

        # Security Mode

        sec_frame = ttk.Frame(frame)

        sec_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(sec_frame, text="Security Mode:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.security_mode_label = ttk.Label(sec_frame, text="--", font=("Arial", 11, "bold"))

        self.security_mode_label.pack(side=tk.LEFT, padx=5)

       

        # Failed Login Attempts

        login_frame = ttk.Frame(frame)

        login_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(login_frame, text="Failed Login Attempts:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.login_failures_label = ttk.Label(login_frame, text="--", font=("Arial", 11))

        self.login_failures_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(login_frame, text="Reset Counter", command=self.reset_login_failures).pack(side=tk.LEFT, padx=20)

       

        # Security Controls

        controls_frame = ttk.LabelFrame(self.security_tab, text="Security Controls")

        controls_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)

       

        # Security mode selector

        mode_frame = ttk.Frame(controls_frame)

        mode_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(mode_frame, text="Set Security Mode:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.security_mode_var = tk.StringVar(value="Standard")

        mode_options = ["Disabled", "Basic", "Standard", "Advanced"]

        self.security_mode_dropdown = ttk.OptionMenu(mode_frame, self.security_mode_var, *mode_options)

        self.security_mode_dropdown.pack(side=tk.LEFT, padx=5)

        ttk.Button(mode_frame, text="Apply", command=self.set_security_mode).pack(side=tk.LEFT, padx=5)

       

        # Security Features

        features_frame = ttk.LabelFrame(self.security_tab, text="Security Features")

        features_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

       

        # Create a grid of security features with checkboxes

        features = [

            ("User Authentication", True),

            ("Connection Encryption", True),

            ("Access Control Lists", True),

            ("Audit Logging", True),

            ("Change Detection", True),

            ("Intrusion Detection", False)

        ]

       

        for i, (feature, enabled) in enumerate(features):

            var = tk.BooleanVar(value=enabled)

            cb = ttk.Checkbutton(features_frame, text=feature, variable=var, state="disabled")

            cb.grid(row=i//2, column=i%2, sticky="w", padx=20, pady=5)

            setattr(self, f"{feature.lower().replace(' ', '_')}_var", var)

 

    def setup_diagnostics_tab(self):

        # Diagnostics information

        frame = ttk.LabelFrame(self.diag_tab, text="System Diagnostics")

        frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

       

        # Battery Status

        battery_frame = ttk.Frame(frame)

        battery_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(battery_frame, text="Battery Level:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.battery_progress = ttk.Progressbar(battery_frame, length=200, mode="determinate", maximum=100)

        self.battery_progress.pack(side=tk.LEFT, padx=5)

        self.battery_value = ttk.Label(battery_frame, text="0%", font=("Arial", 11))

        #self.battery_value.pack(side=tk.LEFT, padx-2)

        # Battery Status

        battery_frame = ttk.Frame(frame)

        battery_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Label(battery_frame, text="Battery Level:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.battery_progress = ttk.Progressbar(battery_frame, length=200, mode="determinate", maximum=100)

        self.battery_progress.pack(side=tk.LEFT, padx=5)

        self.battery_value = ttk.Label(battery_frame, text="0%", font=("Arial", 11))

        self.battery_value.pack(side=tk.LEFT, padx=5)

       

        # Fault Status

        fault_frame = ttk.LabelFrame(frame, text="Fault Status")

        fault_frame.pack(fill=tk.X, padx=10, pady=10)

       

        # Minor Faults

        minor_frame = ttk.Frame(fault_frame)

        minor_frame.pack(fill=tk.X, padx=10, pady=5)

       

        self.minor_fault_var = tk.BooleanVar(value=False)

        self.minor_fault_indicator = ttk.Checkbutton(minor_frame, text="Minor Fault", variable=self.minor_fault_var, state="disabled")

        self.minor_fault_indicator.pack(side=tk.LEFT, padx=5)

       

        # Major Faults

        major_frame = ttk.Frame(fault_frame)

        major_frame.pack(fill=tk.X, padx=10, pady=5)

       

        self.major_fault_var = tk.BooleanVar(value=False)

        self.major_fault_indicator = ttk.Checkbutton(major_frame, text="Major Fault", variable=self.major_fault_var, state="disabled")

        self.major_fault_indicator.pack(side=tk.LEFT, padx=5)

       

        # I/O Status

        io_frame = ttk.LabelFrame(self.diag_tab, text="I/O Status")

        io_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

       

        # Create a grid of I/O points with status indicators

        io_points = [

            ("Digital Input 0", False),

            ("Digital Input 1", True),

            ("Digital Input 2", False),

            ("Digital Input 3", True),

            ("Digital Output 0", True),

            ("Digital Output 1", False),

            ("Digital Output 2", True),

            ("Digital Output 3", False),

        ]

       

        self.io_vars = []

        for i, (io_name, state) in enumerate(io_points):

            var = tk.BooleanVar(value=state)

            self.io_vars.append(var)

           

            row, col = i // 4, i % 4

            frame = ttk.Frame(io_frame)

            frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")

           

            canvas = tk.Canvas(frame, width=15, height=15)

            canvas.pack(side=tk.LEFT)

            color = "green" if state else "red"

            indicator = canvas.create_oval(2, 2, 13, 13, fill=color)

           

            ttk.Label(frame, text=io_name, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

           

            setattr(self, f"io_{i}_indicator", indicator)

            setattr(self, f"io_{i}_canvas", canvas)

       

        # Diagnostics Controls

        controls_frame = ttk.LabelFrame(self.diag_tab, text="Diagnostic Controls")

        controls_frame.pack(fill=tk.X, padx=10, pady=10)

       

        ttk.Button(controls_frame, text="Run Diagnostics", command=self.run_diagnostics).pack(side=tk.LEFT, padx=10, pady=10)

        ttk.Button(controls_frame, text="Reset Counters", command=self.reset_counters).pack(side=tk.LEFT, padx=10, pady=10)

        ttk.Button(controls_frame, text="Clear Faults", command=self.clear_faults).pack(side=tk.LEFT, padx=10, pady=10)

 

    def setup_logs_tab(self):

        # Event logs display

        frame = ttk.Frame(self.logs_tab)

        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

       

        # Filter controls

        filter_frame = ttk.Frame(frame)

        filter_frame.pack(fill=tk.X, pady=5)

       

        ttk.Label(filter_frame, text="Filter:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        self.filter_var = tk.StringVar(value="All")

        filter_options = ["All", "Security", "Configuration", "Faults", "Connections"]

        ttk.OptionMenu(filter_frame, self.filter_var, *filter_options, command=self.apply_filter).pack(side=tk.LEFT, padx=5)

       

        # Scrollable text area for logs

        log_frame = ttk.Frame(frame)

        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

       

        scrollbar = ttk.Scrollbar(log_frame)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

       

        self.log_text = tk.Text(log_frame, height=20, width=80, yscrollcommand=scrollbar.set)

        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.log_text.yview)

       

        # Add initial log entry

        self.add_log_entry("System initialized", "System")

       

        # Control buttons

        button_frame = ttk.Frame(frame)

        button_frame.pack(fill=tk.X, pady=5)

       

        ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Generate Test Event", command=self.generate_test_event).pack(side=tk.LEFT, padx=5)

 

    def add_log_entry(self, message, category="System"):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.log_text.insert(tk.END, f"[{timestamp}] [{category}] {message}\n")

        self.log_text.see(tk.END)  # Scroll to the end

       

        # Apply tag for color coding based on category

        line_count = int(self.log_text.index('end-1c').split('.')[0])

        line_start = f"{line_count}.0"

        line_end = f"{line_count}.end"

       

        # Create tags if they don't exist

        try:

            self.log_text.tag_configure("Security", foreground="red")

            self.log_text.tag_configure("Configuration", foreground="blue")

            self.log_text.tag_configure("Faults", foreground="orange")

            self.log_text.tag_configure("Connections", foreground="green")

            self.log_text.tag_configure("System", foreground="black")

        except:

            pass

       

        # Apply tag

        self.log_text.tag_add(category, line_start, line_end)

 

    def apply_filter(self, selection):

        # Show all lines

        self.log_text.tag_remove("hidden", "1.0", tk.END)

       

        if selection == "All":

            return

           

        # Hide lines that don't match the filter

        line_count = int(self.log_text.index('end-1c').split('.')[0])

        for i in range(1, line_count + 1):

            line_text = self.log_text.get(f"{i}.0", f"{i}.end")

            if f"[{selection}]" not in line_text:

                self.log_text.tag_add("hidden", f"{i}.0", f"{i}.end+1c")

       

        # Configure hidden tag

        self.log_text.tag_configure("hidden", elide=True)

 

    def clear_logs(self):

        self.log_text.delete(1.0, tk.END)

        self.add_log_entry("Logs cleared", "System")

 

    def export_logs(self):

        # In a real application, this would save to a file

        self.add_log_entry("Logs exported to file", "System")

 

    def generate_test_event(self):

        event_types = [

            ("Failed login attempt detected", "Security"),

            ("Security mode changed to Advanced", "Configuration"),

            ("Minor fault detected in module", "Faults"),

            ("New connection established from 192.168.1.100", "Connections"),

            ("Processor mode changed to PROGRAM", "Configuration"),

            ("Battery level warning", "System"),

            ("Force enabled on output", "Configuration")

        ]

        event, category = random.choice(event_types)

        self.add_log_entry(event, category)

 

    def poll_data(self):

        while self.polling:

            if not self.connected:

                self.update_labels("Disconnected", "--", "--", "--", "gray")

                try:

                    self.connected = self.client.connect()

                    if self.connected:

                        self.update_connection_status(self.connected)

                        self.add_log_entry("Connection established to PLC", "Connections")

                except Exception as e:

                    pass

                time.sleep(2)

                continue

 

            try:

                # Poll AC control data

                coil_result = self.client.read_coils(3, 1)

                ac_on = coil_result.bits[0] if coil_result and not coil_result.isError() else None

 

                reg_result = self.client.read_holding_registers(4, 3)

                if reg_result and not reg_result.isError():

                    setpoint = reg_result.registers[0]

                    current_temp = reg_result.registers[2]

                else:

                    setpoint = current_temp = None

 

                if ac_on is True:

                    ac_status = "On"

                    color = "green"

                elif ac_on is False:

                    ac_status = "Off"

                    color = "red"

                else:

                    ac_status = "Unknown"

                    color = "gray"

 

                timestamp = datetime.now().strftime("%H:%M:%S")

                self.update_labels(ac_status, str(setpoint), str(current_temp), timestamp, color)

                self.update_ac_box(color)

 

                # Poll PLC status data

                self.poll_plc_status()

                self.poll_performance_data()

                self.poll_security_status()

                self.poll_diagnostics_data()

 

            except Exception as e:

                print(f"[ERROR] Polling failed: {e}")

                self.update_labels("Error", "--", "--", "--", "gray")

                self.update_ac_box("gray")

                self.connected = False

                self.update_connection_status(self.connected)

                self.add_log_entry(f"Connection lost: {e}", "Connections")

 

            time.sleep(1)

 

    def poll_plc_status(self):

        try:

            # Read processor mode (coil 21)

            proc_result = self.client.read_coils(21, 1)

            if proc_result and not proc_result.isError():

                processor_mode = "RUN" if proc_result.bits[0] else "PROGRAM"

                self.update_status_indicator("processor_status",

                                            "green" if processor_mode == "RUN" else "yellow",

                                            processor_mode)

               

                # Log processor mode changes

                if hasattr(self, 'last_processor_mode') and self.last_processor_mode != processor_mode:

                    self.add_log_entry(f"Processor mode changed from {self.last_processor_mode} to {processor_mode}", "Configuration")

               

                self.last_processor_mode = processor_mode

           

            # Read force status (coil 31)

            force_result = self.client.read_coils(31, 1)

            if force_result and not force_result.isError():

                force_status = "Active" if force_result.bits[0] else "Inactive"

                self.update_status_indicator("force_status",

                                           "yellow" if force_status == "Active" else "green",

                                           force_status)

               

                # Log force status changes

                if hasattr(self, 'last_force_status') and self.last_force_status != force_status:

                    self.add_log_entry(f"Force status changed to {force_status}", "Configuration")

               

                self.last_force_status = force_status

           

            # Read fault status (coils 41-42)

            fault_result = self.client.read_coils(41, 2)

            if fault_result and not fault_result.isError():

                minor_fault = fault_result.bits[0]

                major_fault = fault_result.bits[1]

               

                if major_fault:

                    fault_status = "Major Fault"

                    fault_color = "red"

                elif minor_fault:

                    fault_status = "Minor Fault"

                    fault_color = "orange"

                else:

                    fault_status = "No Faults"

                    fault_color = "green"

               

                self.update_status_indicator("fault_status", fault_color, fault_status)

               

                # Log fault status changes

                if hasattr(self, 'last_fault_status') and self.last_fault_status != fault_status:

                    self.add_log_entry(f"Fault status changed to {fault_status}", "Faults")

               

                self.last_fault_status = fault_status

           

            # Read uptime (register 61)

            uptime_result = self.client.read_holding_registers(61, 1)

            if uptime_result and not uptime_result.isError():

                uptime = uptime_result.registers[0]

                self.uptime_label.config(text=f"{uptime} hours")

           

            # Read connections (register 51)

            conn_result = self.client.read_holding_registers(51, 1)

            if conn_result and not conn_result.isError():

                connections = conn_result.registers[0]

                self.connections_label.config(text=str(connections))

               

        except Exception as e:

            print(f"[ERROR] PLC status polling failed: {e}")

 

    def poll_performance_data(self):

        try:

            # Read CPU usage (register 11)

            cpu_result = self.client.read_holding_registers(11, 1)

            if cpu_result and not cpu_result.isError():

                cpu_usage = cpu_result.registers[0]

                self.cpu_progress["value"] = cpu_usage

                self.cpu_value.config(text=f"{cpu_usage}%")

               

                # Log high CPU usage

                if cpu_usage > 80:

                    self.add_log_entry(f"High CPU usage detected: {cpu_usage}%", "System")

           

            # Read memory usage (register 21)

            mem_result = self.client.read_holding_registers(21, 1)

            if mem_result and not mem_result.isError():

                mem_usage = mem_result.registers[0]

                self.mem_progress["value"] = mem_usage

                self.mem_value.config(text=f"{mem_usage}%")

           

            # Read scan times (registers 62-63)

            scan_result = self.client.read_holding_registers(62, 2)

            if scan_result and not scan_result.isError():

                task_scan = scan_result.registers[0]

                io_scan = scan_result.registers[1]

                self.task_scan_label.config(text=f"{task_scan} ms")

                self.io_scan_label.config(text=f"{io_scan} ms")

           

            # Read connections (register 51)

            conn_result = self.client.read_holding_registers(51, 1)

            if conn_result and not conn_result.isError():

                connections = conn_result.registers[0]

                self.current_conn_label.config(text=str(connections))

               

        except Exception as e:

            print(f"[ERROR] Performance data polling failed: {e}")

 

    def poll_security_status(self):

        try:

            # Read security mode (register 31)

            sec_result = self.client.read_holding_registers(31, 2)

            if sec_result and not sec_result.isError():

                security_mode = sec_result.registers[0]

                login_failures = sec_result.registers[1]

               

                mode_text = ["Disabled", "Basic", "Standard", "Advanced"][security_mode] if 0 <= security_mode <= 3 else "Unknown"

                self.security_mode_label.config(text=mode_text)

               

                # Set color based on security mode

                if mode_text == "Disabled":

                    self.security_mode_label.config(foreground="red")

                elif mode_text == "Basic":

                    self.security_mode_label.config(foreground="orange")

                elif mode_text == "Standard":

                    self.security_mode_label.config(foreground="blue")

                elif mode_text == "Advanced":

                    self.security_mode_label.config(foreground="green")

               

                self.login_failures_label.config(text=str(login_failures))

               

                # Log security mode changes

                if hasattr(self, 'last_security_mode') and self.last_security_mode != security_mode:

                    self.add_log_entry(f"Security mode changed from {['Disabled', 'Basic', 'Standard', 'Advanced'][self.last_security_mode]} to {mode_text}", "Security")

               

                self.last_security_mode = security_mode

               

        except Exception as e:

            print(f"[ERROR] Security status polling failed: {e}")

 

    def poll_diagnostics_data(self):

        try:

            # Read battery level (register 33)

            battery_result = self.client.read_holding_registers(33, 1)

            if battery_result and not battery_result.isError():

                battery_level = battery_result.registers[0]

                self.battery_progress["value"] = battery_level

                self.battery_value.config(text=f"{battery_level}%")

               

                # Update battery status indicator

                if battery_level > 75:

                    battery_status = "Good"

                    battery_color = "green"

                elif battery_level > 25:

                    battery_status = "Fair"

                    battery_color = "yellow"

                else:

                    battery_status = "Low"

                    battery_color = "red"

                   

                    # Log low battery

                    if battery_level <= 20 and (not hasattr(self, 'last_battery_level') or self.last_battery_level > 20):

                        self.add_log_entry(f"Low battery warning: {battery_level}%", "System")

               

                self.update_status_indicator("battery_status", battery_color, battery_status)

                self.last_battery_level = battery_level

           

            # Read fault status (coils 41-42)

            fault_result = self.client.read_coils(41, 2)

            if fault_result and not fault_result.isError():

                minor_fault = fault_result.bits[0]

                major_fault = fault_result.bits[1]

               

                self.minor_fault_var.set(minor_fault)

                self.major_fault_var.set(major_fault)

               

        except Exception as e:

            print(f"[ERROR] Diagnostics data polling failed: {e}")

 

    def update_status_indicator(self, name, color, text):

        canvas = getattr(self, f"{name}_canvas")

        indicator = getattr(self, f"{name}_indicator")

        label = getattr(self, f"{name}_label")

       

        canvas.itemconfig(indicator, fill=color)

        label.config(text=text)

 

    def update_ac_box(self, color):

        self.ac_canvas.itemconfig(self.ac_box, fill=color)

 

    def set_setpoint(self):

        if not self.connected:

            self.setpoint_status.config(text="Not connected", fg="red")

            return

 

        try:

            value = int(self.setpoint_input.get())

            result = self.client.write_register(4, value)

           

            if result and not result.isError():

                self.setpoint_status.config(text=f"Setpoint updated to {value} °F", foreground="blue")

                self.add_log_entry(f"Setpoint changed to {value} °F", "Configuration")

            else:

                self.setpoint_status.config(text="Failed to write setpoint", foreground="red")

       

        except Exception as e:

       

            self.setpoint_status.config(text=f"Error: {e}", foreground="red")


 

    def set_security_mode(self):

        if not self.connected:

            self.add_log_entry("Cannot change security mode: Not connected", "Security")

            return

 

        try:

            mode_text = self.security_mode_var.get()

            mode_value = {"Disabled": 0, "Basic": 1, "Standard": 2, "Advanced": 3}[mode_text]

           

            result = self.client.write_register(31, mode_value)

            if result and not result.isError():

                self.add_log_entry(f"Security mode changed to {mode_text}", "Security")

            else:

                self.add_log_entry("Failed to change security mode", "Security")

        except Exception as e:

            self.add_log_entry(f"Error changing security mode: {e}", "Security")

 

    def set_processor_mode(self):

        if not self.connected:

            self.add_log_entry("Cannot change processor mode: Not connected", "Configuration")

            return

 

        try:

            mode = 1 if self.processor_mode_var.get() == "RUN" else 0

           

            result = self.client.write_coil(21, mode)

            if result and not result.isError():

                self.add_log_entry(f"Processor mode changed to {self.processor_mode_var.get()}", "Configuration")

            else:

                self.add_log_entry("Failed to change processor mode", "Configuration")

        except Exception as e:

            self.add_log_entry(f"Error changing processor mode: {e}", "Configuration")

 

    def set_force_status(self):

        if not self.connected:

            self.add_log_entry("Cannot change force status: Not connected", "Configuration")

            return

 

        try:

            force = self.force_var.get()

           

            result = self.client.write_coil(31, force)

            if result and not result.isError():

                status = "enabled" if force else "disabled"

                self.add_log_entry(f"Force {status}", "Configuration")

            else:

                self.add_log_entry("Failed to change force status", "Configuration")

        except Exception as e:

            self.add_log_entry(f"Error changing force status: {e}", "Configuration")

 

    def clear_faults(self):

        if not self.connected:

            self.add_log_entry("Cannot clear faults: Not connected", "Faults")

            return

 

        try:

            # Clear minor and major faults

            result1 = self.client.write_coil(41, False)

            result2 = self.client.write_coil(42, False)

           

            if result1 and not result1.isError() and result2 and not result2.isError():

                self.add_log_entry("All faults cleared", "Faults")

            else:

                self.add_log_entry("Failed to clear faults", "Faults")

        except Exception as e:

            self.add_log_entry(f"Error clearing faults: {e}", "Faults")

 

    def reset_login_failures(self):

        if not self.connected:

            self.add_log_entry("Cannot reset login failures: Not connected", "Security")

            return

 

        try:

            result = self.client.write_register(32, 0)

           

            if result and not result.isError():

                self.add_log_entry("Login failure counter reset", "Security")

            else:

                self.add_log_entry("Failed to reset login failures", "Security")

        except Exception as e:

            self.add_log_entry(f"Error resetting login failures: {e}", "Security")

 

    def run_diagnostics(self):

        if not self.connected:

            self.add_log_entry("Cannot run diagnostics: Not connected", "System")

            return

 

        self.add_log_entry("Running system diagnostics...", "System")

       

        # Simulate diagnostic process

        self.root.after(1000, lambda: self.add_log_entry("Checking processor status...", "System"))

        self.root.after(2000, lambda: self.add_log_entry("Checking memory allocation...", "System"))

        self.root.after(3000, lambda: self.add_log_entry("Checking I/O modules...", "System"))

        self.root.after(4000, lambda: self.add_log_entry("Checking communication interfaces...", "System"))

        self.root.after(5000, lambda: self.add_log_entry("Diagnostics complete. No issues found.", "System"))

 

    def reset_counters(self):

        if not self.connected:

            self.add_log_entry("Cannot reset counters: Not connected", "System")

            return

 

        self.add_log_entry("System counters reset", "System")

 

    def update_labels(self, ac_status, setpoint, current, timestamp, color):

        self.status_label.config(text=f"AC Unit: {ac_status}", foreground=color)

        self.setpoint_label.config(text=f"Setpoint Temp: {setpoint} °F")

        self.current_label.config(text=f"Current Temp: {current} °F")

        self.timestamp_label.config(text=f"Last Updated: {timestamp}")


 

    def update_connection_status(self, connected):

     if connected:

        self.connection_label.config(text="Connected", foreground="green")

     else:

        self.connection_label.config(text="Disconnected", foreground="red")


 

    def stop_polling(self):

        self.polling = False

        self.client.close()

        self.root.destroy()

 

# -------------------- Launch Modbus Server in Background --------------------

 

def start_asyncio_loop():

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(start_modbus_server())

 

def launch():

    server_thread = Thread(target=start_asyncio_loop, daemon=True)

    server_thread.start()

 

    root = tk.Tk()

    app = ACHMI(root)

    root.protocol("WM_DELETE_WINDOW", app.stop_polling)

    root.mainloop()

 

if __name__ == "__main__":

    launch()
