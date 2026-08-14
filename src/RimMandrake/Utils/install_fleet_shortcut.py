#!/usr/bin/env python3
"""install_fleet_shortcut.py — one double-click opens the whole fleet.

Windows Terminal takes a chain of sub-commands in a single invocation, so all
five seats are ONE process launch:

    wt.exe -w _new new-tab -p "AGENT BRIDGE" ; new-tab -p "AGENT OPS" ; ...

Each `-p` picks the seat profile written by `install_wt_seat_profiles.py`, which
already carries the colour, the tab title, `AGENT_SEAT`, and the
`claude_bounded.sh --name 'AGENT <SEAT>'` launch line. So this script adds no
launch logic of its own — it only chains the profiles that exist, in seat order,
and that is deliberate: one place defines how a seat starts.

WHY A .lnk AND NOT A .bat
=========================
A batch file goes through cmd, where `;` is a token delimiter and has to be
escaped `^;` — and it flashes a console window on every click. A shortcut runs
`wt.exe` directly: no shell, no escaping, no flash. The Explorer properties
dialog caps the Target field at 260 characters, but the .lnk format itself does
not, and WScript.Shell writes the field directly — which is why this is a script
rather than "make a shortcut by hand".

`-w _new` forces a NEW window every time. Without it a second click appends five
more tabs to the window that is already open, which is exactly the accident this
is meant to prevent.

USAGE
=====
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py            # print the plan
    python3 src/RimMandrake/Utils/install_fleet_shortcut.py --apply    # write the .lnk

The shortcut is also the thing to pin: right-click it → Pin to Start / Taskbar.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from install_wt_seat_profiles import SEATS  # noqa: E402  single source of seat order

WT = r"C:\Users\Mandrake\AppData\Local\Microsoft\WindowsApps\wt.exe"
DESKTOPS = (r"C:\Users\Mandrake\OneDrive\Desktop", r"C:\Users\Mandrake\Desktop")
NAME = "Start Agent Fleet.lnk"


def wt_args():
    parts = ["-w", "_new"]
    for n, seat in enumerate(SEATS):
        if n:
            parts.append(";")
        parts += ["new-tab", "-p", f'"AGENT {seat}"']
    parts += [";", "focus-tab", "-t", "0"]
    return " ".join(parts)


def win_to_wsl(p):
    return "/mnt/" + p[0].lower() + p[2:].replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the shortcut (default: plan only)")
    ap.add_argument("--desktop", help="override the Desktop folder (Windows path)")
    args = ap.parse_args()

    desktop = args.desktop
    if not desktop:
        desktop = next((d for d in DESKTOPS if os.path.isdir(win_to_wsl(d))), None)
    if not desktop:
        sys.exit("no Desktop folder found; pass --desktop")

    lnk = desktop + "\\" + NAME
    arguments = wt_args()

    print(f"{'APPLY' if args.apply else 'PLAN'}: {lnk}")
    print(f"  target : {WT}")
    print(f"  args   : {arguments}")
    print(f"  seats  : {', '.join(SEATS)}")
    if not args.apply:
        print("\nRe-run with --apply to write it.")
        return

    ps = (
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%s');"
        "$s.TargetPath = '%s';"
        "$s.Arguments = '%s';"
        "$s.WorkingDirectory = 'D:\\Luke\\dev\\Rimworld';"
        "$s.IconLocation = '%s,0';"
        "$s.Description = 'Open all five RimWorld agent seats in one Windows "
        "Terminal window';"
        "$s.Save()"
    ) % (lnk, WT, arguments.replace("'", "''"), WT)

    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip() or "powershell failed")
    print("written.")


if __name__ == "__main__":
    main()
