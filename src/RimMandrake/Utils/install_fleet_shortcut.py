#!/usr/bin/env python3
"""install_fleet_shortcut.py — one double-click opens the whole fleet, tiled.

Writes a Desktop shortcut that runs `launch_fleet.ps1`, which opens one Windows
Terminal window per agent and places them at their fixed positions:

    TOP-LEFT HESTIA   BOTTOM-LEFT AGENT BENCH   BOTTOM-RIGHT AGENT FOUNDRY

All launch behaviour lives in the .ps1 — the AGENT BENCH/AGENT FOUNDRY profiles
it names are the ones `install_wt_seat_profiles.py` writes, which already carry
the colour, tab title, `AGENT_SEAT` and the `claude_bounded.sh --name 'AGENT
<SEAT>'` line; HESTIA is a separate project's own profile (D:/Luke/dev/Hestia),
not something this repo's tooling writes. This script only writes the shortcut.

WHY A .lnk AND NOT A .bat
=========================
A batch file goes through cmd and flashes a console window on every click. The
shortcut runs `powershell.exe` directly with `-WindowStyle Hidden`, so the only
windows that appear are the three seats.

The Explorer properties dialog caps the Target field at 260 characters, but the
.lnk format does not and WScript.Shell writes the field directly — which is why
this is a script rather than "make a shortcut by hand".

AUTOSTART ON REBOOT
===================
`--startup` writes a SECOND copy of the same shortcut into the per-user Startup
folder, so the fleet opens on every sign-in without a double-click. That copy
passes `-DelaySec` (default 45) to the launcher, because at logon the desktop is
ready long before WSL2 and the network are and every seat is a WSL session.

It runs at LOGON, not at power-on: a machine sitting at the lock screen has not
run it yet. `--startup --remove` takes it out again; the Desktop shortcut is
never touched by either.

USAGE
=====
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py            # print the plan
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py --apply    # write the .lnk
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py --startup --apply
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py --startup --remove --apply

The shortcut is also the thing to pin: right-click it -> Pin to Start / Taskbar.
Tune the layout in `launch_fleet.ps1` (`-Gap`), not here.
"""
import argparse
import os
import subprocess
import sys

WT = r"C:\Users\Mandrake\AppData\Local\Microsoft\WindowsApps\wt.exe"
PS = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
SCRIPT = r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils\launch_fleet.ps1"
REPO_WIN = r"D:\Luke\dev\Rimworld"
DESKTOPS = (r"C:\Users\Mandrake\OneDrive\Desktop", r"C:\Users\Mandrake\Desktop")
STARTUP = (r"C:\Users\Mandrake\AppData\Roaming\Microsoft\Windows"
           r"\Start Menu\Programs\Startup")
NAME = "Start Agent Fleet.lnk"


def win_to_wsl(p):
    return "/mnt/" + p[0].lower() + p[2:].replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the shortcut (default: plan only)")
    ap.add_argument("--desktop", help="override the Desktop folder (Windows path)")
    ap.add_argument("--startup", action="store_true",
                    help="write into the Startup folder instead of the Desktop, "
                         "so the fleet opens on every sign-in")
    ap.add_argument("--delay", type=int, default=45, metavar="SEC",
                    help="seconds the Startup copy waits for WSL and the network "
                         "before launching (default 45; --startup only)")
    ap.add_argument("--remove", action="store_true",
                    help="delete the Startup copy instead of writing it")
    args = ap.parse_args()

    if args.remove and not args.startup:
        sys.exit("--remove only applies to --startup; the Desktop shortcut stays")

    if not os.path.exists(win_to_wsl(SCRIPT)):
        sys.exit(f"launcher missing: {SCRIPT}")

    if args.startup:
        folder = args.desktop or STARTUP
        if not os.path.isdir(win_to_wsl(folder)):
            sys.exit(f"Startup folder missing: {folder}")
    else:
        folder = args.desktop
        if not folder:
            folder = next((d for d in DESKTOPS if os.path.isdir(win_to_wsl(d))), None)
        if not folder:
            sys.exit("no Desktop folder found; pass --desktop")

    lnk = folder + "\\" + NAME
    delay = f" -DelaySec {args.delay}" if args.startup else ""
    arguments = ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden '
                 f'-File "{SCRIPT}"{delay}')

    verb = "REMOVE" if args.remove else "APPLY"
    print(f"{verb if args.apply else 'PLAN ' + verb}: {lnk}")
    if not args.remove:
        print(f"  target : {PS}")
        print(f"  args   : {arguments}")
    if not args.apply:
        print("\nRe-run with --apply to write it.")
        return

    if args.remove:
        path = win_to_wsl(lnk)
        if os.path.exists(path):
            os.remove(path)
            print("removed.")
        else:
            print("nothing there already.")
        return

    desc = ("Open the fleet at sign-in: HESTIA + the RimWorld agent windows, tiled"
            if args.startup else
            "Open the fleet: HESTIA + the two RimWorld agent windows, tiled")
    ps = (
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%s');"
        "$s.TargetPath = '%s';"
        "$s.Arguments = '%s';"
        "$s.WorkingDirectory = '%s';"
        # The icon is Windows Terminal's, not PowerShell's: what the shortcut
        # opens is three terminals, and the icon is how it is found on a busy
        # Desktop.
        "$s.IconLocation = '%s,0';"
        "$s.Description = '%s';"
        "$s.Save()"
    ) % (lnk, PS, arguments.replace("'", "''"), REPO_WIN, WT, desc)

    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip() or "powershell failed")
    print("written.")


if __name__ == "__main__":
    main()
