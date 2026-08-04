"""
===========================================================
LIVE SYSTEM DATA COLLECTOR
Version 3
===========================================================
"""

import os
import time
import socket
import psutil
import pandas as pd

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

OUTPUT_FILE = "../../data/live_data.csv"

INTERVAL = 10          # seconds
SESSION_ID = 1

# -------------------------------------------------------
# Create data folder if needed
# -------------------------------------------------------

os.makedirs("../../data", exist_ok=True)

# -------------------------------------------------------
# System Name
# -------------------------------------------------------

SYSTEM_NAME = socket.gethostname()

print("=" * 60)
print("LIVE DATA COLLECTION")
print("=" * 60)

print(f"System : {SYSTEM_NAME}")
print(f"Saving : {OUTPUT_FILE}")
print(f"Interval : {INTERVAL} seconds")

# -------------------------------------------------------
# Initialize disk counters
# -------------------------------------------------------

previous_disk = psutil.disk_io_counters()
previous_time = time.time()

# -------------------------------------------------------
# Main Loop
# -------------------------------------------------------

while True:

    current_time = time.time()

    cpu = psutil.cpu_percent()

    memory = psutil.virtual_memory()

    process_count = len(psutil.pids())

    disk = psutil.disk_io_counters()

    elapsed = current_time - previous_time

    # ----------------------------------------------
    # Disk write speed (MB/s)
    # ----------------------------------------------

    bytes_written = (
        disk.write_bytes -
        previous_disk.write_bytes
    )

    disk_write_mbps = (
        bytes_written /
        (1024 * 1024)
    ) / max(elapsed, 1e-6)

    previous_disk = disk
    previous_time = current_time

    row = {

        "timestamp": pd.Timestamp.now(),

        "system_id": SYSTEM_NAME,

        "session_id": SESSION_ID,

        "cpu_percent": cpu,

        "memory_percent": memory.percent,

        "memory_available_mb":
            round(memory.available / (1024 * 1024), 2),

        "disk_write_mbps":
            round(disk_write_mbps, 4),

        "process_count":
            process_count,

        "disk_percent": psutil.disk_usage("/").percent,

        "cpu_frequency": psutil.cpu_freq().current,

        "memory_used_mb":
            round(memory.used/(1024*1024),2)
    }

    df = pd.DataFrame([row])

    if os.path.exists(OUTPUT_FILE):

        df.to_csv(
            OUTPUT_FILE,
            mode="a",
            header=False,
            index=False
        )

    else:

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )

    print(
        f"[{row['timestamp']}] "
        f"CPU={cpu:.1f}% | "
        f"MEM={memory.percent:.1f}% | "
        f"Avail={row['memory_available_mb']} MB | "
        f"Disk={disk_write_mbps:.2f} MB/s"
    )

    time.sleep(INTERVAL)