#!/usr/bin/env python3
"""Owner-idle probe for the delegated "free bridge + 20 min idle" rule (owner card 2026-10-26 19:06,
delegation_policy.md 2.6, item BRIDGE_IDLE_BUILD_TWENTY_MINUTE_WATCH).

Reads, from WSL, seconds since the Windows session's last keyboard/mouse input (user32 GetLastInputInfo)
and whether RimWorld is the foreground window, via powershell.exe. ANY failure -> UNMEASURED; this module
never answers "idle" by default. Names no host or account. Read-only: touches nothing.

    python3 idle_probe.py          -> JSON reading on stdout
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys

IDLE_REQUIRED_SECONDS = 20 * 60
_PS = r'''
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public static class RmIdle {
  [StructLayout(LayoutKind.Sequential)] public struct LII { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LII p);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("kernel32.dll")] public static extern ulong GetTickCount64();
  public static long IdleMs() { LII l = new LII(); l.cbSize = (uint)Marshal.SizeOf(typeof(LII));
    if (!GetLastInputInfo(ref l)) return -1; return (long)(uint)(Environment.TickCount - (int)l.dwTime); }
  public static uint FgPid() { uint p; IntPtr h = GetForegroundWindow(); if (h == IntPtr.Zero) return 0;
    GetWindowThreadProcessId(h, out p); return p; }
}
"@
$ms = [RmIdle]::IdleMs(); $up = [RmIdle]::GetTickCount64(); $fp = [RmIdle]::FgPid(); $n = ''
if ($fp -ne 0) { try { $n = (Get-Process -Id $fp).ProcessName } catch { $n = '' } }
Write-Output ("RMIDLE|{0}|{1}|{2}|{3}" -f $ms, $up, $fp, $n)
'''


# 🔴 A session with NO input since boot is not "the owner went idle": powershell launched where no one ever
# typed (session 0, a service, an ssh-spawned interop) reports GetLastInputInfo's boot-time stamp, i.e. an idle
# as long as the uptime. That would read as "idle for days" and hand out the bridge, so it is UNMEASURED.
BOOT_SLACK_MS = 60 * 1000


def parse(out):
    """Parse the helper's single line `RMIDLE|idle_ms|uptime_ms|fg_pid|fg_name` -> reading dict. Pure (tested).
    Anything else, including the old 4-field line without the uptime, is UNMEASURED."""
    for line in (out or "").splitlines():
        if line.startswith("RMIDLE|"):
            parts = line.strip().split("|", 4)
            if len(parts) != 5:
                break
            try:
                ms, up = int(parts[1]), int(parts[2])
            except ValueError:
                break
            if ms < 0:
                return unmeasured("GetLastInputInfo failed")
            if up <= 0 or ms >= up - BOOT_SLACK_MS:
                return unmeasured("no input since boot (idle %d s of %d s uptime): not an interactive session"
                                  % (ms // 1000, up // 1000))
            fg = parts[4].strip()
            return {"state": "MEASURED", "idle_seconds": ms // 1000, "foreground": fg or None,
                    "rimworld_foreground": fg.lower().startswith("rimworld") if fg else False}
    return unmeasured("no RMIDLE line in helper output")


def unmeasured(why):
    return {"state": "UNMEASURED", "idle_seconds": None, "foreground": None,
            "rimworld_foreground": None, "why": why}


# A systemd user unit (the Dispatcher) gets no Windows PATH, so a bare "powershell.exe" is FileNotFoundError there
# and every reading went UNMEASURED: the bridge-ticket hold never lifted (2026-10-28, FOUNDRY idle 15+ min).
_PS_FALLBACK = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"


def _powershell():
    return shutil.which("powershell.exe") or (_PS_FALLBACK if os.path.exists(_PS_FALLBACK) else "powershell.exe")


def measure(timeout=30):
    exe = os.environ.get("RIMFLOW_POWERSHELL") or _powershell()
    try:
        p = subprocess.run([exe, "-NoProfile", "-NonInteractive", "-EncodedCommand",
                            base64.b64encode(_PS.encode("utf-16-le")).decode()],
                           capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001 - every failure is UNMEASURED
        return unmeasured("%s: %s" % (type(e).__name__, str(e)[:100]))
    if p.returncode:
        return unmeasured("powershell exit %d: %s" % (p.returncode, (p.stderr or "").strip()[:100]))
    return parse(p.stdout)


def idle_verdict(reading, need=IDLE_REQUIRED_SECONDS):
    """-> (ok, reason). ok only on a MEASURED idle >= need (input into RimWorld counts as input)."""
    if not reading or reading.get("state") != "MEASURED" or reading.get("idle_seconds") is None:
        return False, "owner idle UNMEASURED (%s) - not treated as idle" % ((reading or {}).get("why") or "no reading")
    s = reading["idle_seconds"]
    if s < need:
        return False, "owner touched the machine %d min %d s ago; need %d min idle" % (s // 60, s % 60, need // 60)
    return True, "owner idle %d min (need %d)" % (s // 60, need // 60)


# Self-declared and fail-safe: any form of fly/flies/flew/flown/flight/flyer (also inside "butterfly", which only
# costs a refusal), take off/takeoff, airborne, glide, soar, aloft, wingspan. Not "flow" (FlowWorks).
_FLIGHT_RE = re.compile(r"fl(?:y|ie|ew|own|ight)|take[-\s]*offs?|airborne|glid|soar|aloft|wingspan", re.I)


def flight_purpose(text):
    return bool(_FLIGHT_RE.search(text or ""))


def decide(reading, purpose, flyer=False, need=IDLE_REQUIRED_SECONDS):
    """The whole delegated rule minus bridge-holder state. -> (ok, reason)."""
    if flyer or flight_purpose(purpose):
        return False, "flyer flight is never delegated (needs a human present)"
    return idle_verdict(reading, need)


if __name__ == "__main__":
    r = measure()
    print(json.dumps(r))
    sys.exit(0 if r["state"] == "MEASURED" else 3)
