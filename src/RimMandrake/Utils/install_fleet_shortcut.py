#!/usr/bin/env python3
"""install_fleet_shortcut.py — one double-click opens the whole fleet, tiled.

Writes a Desktop shortcut that runs `launch_fleet.ps1`, which opens one Windows
Terminal window per agent and places them side by side:

    LEFT  AGENT BENCH        RIGHT  AGENT FOUNDRY

All launch behaviour lives in the .ps1 — the profiles it names are the ones
`install_wt_seat_profiles.py` writes, which already carry the colour, tab title,
`AGENT_SEAT` and the `claude_bounded.sh --name 'AGENT <SEAT>'` line. This script
only writes the shortcut.

WHY A .lnk AND NOT A .bat
=========================
A batch file goes through cmd and flashes a console window on every click. The
shortcut runs `powershell.exe` directly with `-WindowStyle Hidden`, so the only
windows that appear are the four seats.

The Explorer properties dialog caps the Target field at 260 characters, but the
.lnk format does not and WScript.Shell writes the field directly — which is why
this is a script rather than "make a shortcut by hand".

USAGE
=====
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py            # print the plan
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py --apply    # write the .lnk

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
NAME = "Start Agent Fleet.lnk"


def win_to_wsl(p):
    return "/mnt/" + p[0].lower() + p[2:].replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the shortcut (default: plan only)")
    ap.add_argument("--desktop", help="override the Desktop folder (Windows path)")
    args = ap.parse_args()

    if not os.path.exists(win_to_wsl(SCRIPT)):
        sys.exit(f"launcher missing: {SCRIPT}")

    desktop = args.desktop
    if not desktop:
        desktop = next((d for d in DESKTOPS if os.path.isdir(win_to_wsl(d))), None)
    if not desktop:
        sys.exit("no Desktop folder found; pass --desktop")

    lnk = desktop + "\\" + NAME
    arguments = ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden '
                 f'-File "{SCRIPT}"')

    print(f"{'APPLY' if args.apply else 'PLAN'}: {lnk}")
    print(f"  target : {PS}")
    print(f"  args   : {arguments}")
    if not args.apply:
        print("\nRe-run with --apply to write it.")
        return

    ps = (
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%s');"
        "$s.TargetPath = '%s';"
        "$s.Arguments = '%s';"
        "$s.WorkingDirectory = '%s';"
        # The icon is Windows Terminal's, not PowerShell's: what the shortcut
        # opens is four terminals, and the icon is how it is found on a busy
        # Desktop.
        "$s.IconLocation = '%s,0';"
        "$s.Description = 'Open the two RimWorld agent windows, tiled';"
        "$s.Save()"
    ) % (lnk, PS, arguments.replace("'", "''"), REPO_WIN, WT)

    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip() or "powershell failed")
    print("written.")


if __name__ == "__main__":
    main()
