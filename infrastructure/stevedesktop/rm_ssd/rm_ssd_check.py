#!/usr/bin/env python3
"""rm_ssd_check.py - is SteveDesktop's ~/rm on the NVMe? (RIMMANDRAKE_MOVE_STEVEDESKTOP_CLONES_TO_SSD_LINUX_DRIVE_SITS_ON_HARD_DISK)

Run by rm-ssd-check.timer (systemd --user, every 10 min). Installed outside ~/rm (~/.local/bin), because it must
answer when ~/rm is not mounted. Writes ~/.local/state/rm-ssd/last.json on every run, with one verdict:
    ON_NVME        ~/rm is the SSD disk's ext4 (its UUID) and C:, which holds the vhdx, is on an NVMe bus
    NOT_MOUNTED    ~/rm is not a mount point
    WRONG_DISK     ~/rm is mounted from another filesystem
    NOT_NVME       C: reads a bus other than NVMe
    COULD_NOT_LOOK the Windows side could not be read (the cause is in `why`)
and writes reading.json ONLY on ON_NVME, so the live promise
`unit=rm-ssd-check.timer reading=/home/mandrake/.local/state/rm-ssd/reading.json max_age=1h host=stevedesktop`
goes stale, and breaks, as soon as ~/rm leaves the NVMe. Exit 0 ON_NVME, 1 a wrong place, 5 could not look.
"""
import json
import os
import subprocess
import sys
import time

UUID = "3bfbfd35-f6eb-41fe-a94d-10faf48fa360"
MP = "/home/mandrake/rm"
VHD = r"C:\WSL\rmssd\rm.vhdx"
STATE = os.path.expanduser("~/.local/state/rm-ssd")
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
PS_TIMEOUT_S = 60  # budget: danger=a powershell.exe that never returns holds the timer's oneshot unit active, so no later run fires; evidence=Windows calls from SteveDesktop have hung (RUNBOOK: scp past 120 s); longest=1.6s (three measured runs of the whole check, 2026-11-25)


def findmnt(field):
    r = subprocess.run(["findmnt", "-n", "-o", field, "--mountpoint", MP], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def windows_bus():
    """-> (bus, why): C:'s bus type, after checking the vhdx is there; bus None when it could not be read."""
    cmd = "Get-Item '%s' -ErrorAction Stop | Out-Null; (Get-Partition -DriveLetter C | Get-Disk).BusType" % VHD
    try:
        r = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True, text=True,
                           timeout=PS_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "powershell.exe: %s: %s" % (type(e).__name__, e)
    lines = [x.strip() for x in r.stdout.replace("\r", "").splitlines() if x.strip()]
    if r.returncode != 0 or not lines:
        return None, "powershell.exe rc=%d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:])
    return lines[-1], ""


def measure():
    rec = {"schema": "steve.rm_ssd/1", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "mount": MP,
           "uuid_want": UUID, "vhd": VHD}
    if subprocess.run(["mountpoint", "-q", MP]).returncode != 0:
        return dict(rec, verdict="NOT_MOUNTED", why="%s is not a mount point: the SSD disk is not mounted" % MP)
    rec.update(source=findmnt("SOURCE"), uuid=findmnt("UUID"))
    st = os.statvfs(MP)
    rec["free_gb"] = round(st.f_bavail * st.f_frsize / 1e9, 1)
    if rec["uuid"] != UUID:
        return dict(rec, verdict="WRONG_DISK", why="%s is mounted from %s (uuid %s), not the SSD disk's fs" %
                    (MP, rec["source"], rec["uuid"]))
    bus, why = windows_bus()
    rec["bus"] = bus
    if bus is None:
        return dict(rec, verdict="COULD_NOT_LOOK", why=why)
    if bus != "NVMe":
        return dict(rec, verdict="NOT_NVME", why="C:, which holds %s, is on bus %s" % (VHD, bus))
    return dict(rec, verdict="ON_NVME", why="%s is the SSD disk's fs, %s on C:, bus NVMe" % (MP, VHD))


def write(name, rec):
    os.makedirs(STATE, exist_ok=True)
    p = os.path.join(STATE, name)
    with open(p + ".tmp", "w") as f:
        f.write(json.dumps(rec) + "\n")
    os.replace(p + ".tmp", p)


def main():
    rec = measure()
    write("last.json", rec)
    if rec["verdict"] == "ON_NVME":
        write("reading.json", rec)
    print(json.dumps(rec))
    return {"ON_NVME": 0, "COULD_NOT_LOOK": 5}.get(rec["verdict"], 1)


if __name__ == "__main__":
    sys.exit(main())
