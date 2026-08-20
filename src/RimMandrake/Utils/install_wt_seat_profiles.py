#!/usr/bin/env python3
"""install_wt_seat_profiles.py — give each seat its own Windows Terminal profile.

WHY THIS EXISTS RATHER THAN AN ESCAPE SEQUENCE
==============================================
`set_agent_window.sh` emits OSC 10/12 to tint the foreground. **Measured
2026-08-13: Windows Terminal ignores it** — the owner ran `--preview` and all
five lines rendered in the default colour. The escape is kept for other
terminals; it does nothing here.

Two things escapes could never do anyway:

  * **Font.** There is no way to READ the current font. A terminal's reply to a
    query goes to Claude Code's stdin, not to a script's, so "match this window"
    is unavailable by construction. `OSC 50` is also an xterm extension Windows
    Terminal does not implement.
  * **Tab colour.** The tab strip is what the owner actually scans with four
    seats open, and no escape sequence addresses it.

Profiles do all of it, before the shell even starts.

WHAT IT WRITES
==============
Four profiles named `AGENT DECIDE` … `AGENT REP`, each with

  * a colour scheme cloned from Campbell with the seat's foreground,
  * `tabColor`, so the tab strip is colour-coded,
  * a `commandline` that opens WSL in the repo, exports `AGENT_SEAT` and execs
    Claude Code — so **opening the tab is the whole startup**, nothing typed,
  * `suppressApplicationTitle` + `tabTitle`, so the tab keeps the seat name,
  * a fixed `guid`, derived from the seat name, so re-running UPDATES the
    profile instead of adding a duplicate.

WHY THE TAB USED TO SAY `wsl.exe`
=================================
`wsl.exe` sets its own window title, and Windows Terminal lets an application
win while `suppressApplicationTitle` is false — so the profile `name` was
overwritten within a second of the tab opening. `true` pins it; `tabTitle` is
set as well so the tab carries the seat name even if a future default overrides
`name`.

WHY THE COMMANDLINE LAUNCHES CLAUDE DIRECTLY
============================================
It used to run `set_agent_window.sh <SEAT>` in a bare shell, *before* Claude
Code existed. `CLAUDE_CODE_SESSION_ID` is unset there, so the script recorded no
role: the conversation was never named, the identity file never injected, and
peers could not address the seat. Only the window title worked — and that was
then lost to `wsl.exe` anyway.

Now the tab exports `AGENT_SEAT` and execs Claude Code. The SessionStart hook
(`.claude/hooks/set_session_title.py`) reads that variable, records the role
itself, and everything downstream follows. `set_agent_window.sh` remains the
manual path for a window opened without a profile, or a seat changing role.

Font is deliberately left inherited: the owner's `profiles.defaults` is empty,
so every window already shares one font, and pinning a face here would be the
first thing to go stale if they ever change it.

USAGE
=====
    python3 src/RimMandrake/Utils/install_wt_seat_profiles.py            # show the diff, write nothing
    python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --apply    # back up, then write

A SINGLE rolling backup (`settings.json.bak`) is written before any change and
overwritten each run. A malformed settings.json makes Windows Terminal fall back
to defaults silently, so that one file is the whole recovery path.
"""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import sys
import uuid

SETTINGS = ("/mnt/c/Users/Mandrake/AppData/Local/Packages/"
            "Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json")

REPO_WIN = r"D:\Luke\dev\Rimworld"
REPO_WSL = "/mnt/d/Luke/dev/Rimworld"
DISTRO = "Ubuntu"

# How the owner launches Claude Code. There is no `claude` alias in ~/.zshrc —
# checked — so this is the bare binary plus the flag they always pass. Change it
# HERE if the launch line ever changes; four profiles read it.
#
# ⭐ `--name` IS WHAT MAKES A SEAT ADDRESSABLE. It is not decoration and it is not
# a duplicate of `tabTitle`. Measured 2026-08-13, three live seats at once: the
# SessionStart hook's `sessionTitle` sets the CONVERSATION title only, and the
# name peers address with `SendMessage` is a DIFFERENT field —
# `~/.claude/sessions/<pid>.json` `name`, which stayed `rimworld-1b` /
# `rimworld-64` / `rimworld-b8` with `nameSource: "derived"` while all three role
# files read `AGENT <retired seat>` / `AGENT <retired seat>` / `AGENT <retired seat>` correctly.
# In the 2.1.231 binary the hook path reaches `saveCustomTitle(title, "hook")`
# and never the pid-file writer; only `--name`, `/rename` and the agent-name
# setter reach it. So the flag is the ONLY zero-typing route to an addressable
# seat. Do not drop it to shorten the line.
#
# Single quotes, deliberately: this is interpolated into `bash -lc "…"` inside a
# JSON string, so a double-quoted argument would terminate the command early.
#
# 🔴 LAUNCHED THROUGH claude_bounded.sh, NOT bare `claude` — 2026-08-14.
# Bare `claude` under `wsl.exe -- bash -lc` lands every seat in ONE shared,
# unbounded cgroup (`/init.scope`, `memory.max=max`). On 2026-08-14 one seat
# reached 27.4 GB of the VM's 31.7 GB and the kernel logged
# `constraint=CONSTRAINT_NONE, global_oom` — a whole-VM kill, which takes init
# and therefore ALL FOUR SEATS. Twice in one day. The wrapper puts each seat in
# its own `systemd-run --user --scope` with MemoryMax/MemorySwapMax, which turns
# that into `constraint=CONSTRAINT_MEMCG`: the offending seat dies alone and the
# other three never notice. Full evidence: observed/2026-08-14_wsl_oom.md.
# Arguments pass through untouched, so `--name` still does its job below.
LAUNCH = ("/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils/claude_bounded.sh "
          "--dangerously-skip-permissions --name 'AGENT {seat}'")

# Hue-distinct and legible on Campbell's near-black background.
SEATS = {
    "DECIDE": ("#C08CE0", "violet — scope and spec"),
    "BUILD":  ("#7BC96F", "green  — artifacts and offline verification"),
    "CHECK":  ("#4EC9E0", "cyan   — the live game and the bridge"),
    "REP":    ("#E5A03C", "amber  — the human's interface"),
}

# Campbell, Windows Terminal's default scheme. Only `foreground` and
# `cursorColor` differ per seat; everything else is left identical so ordinary
# ANSI output looks exactly as it does now.
CAMPBELL = {
    "background": "#0C0C0C", "black": "#0C0C0C", "blue": "#0037DA",
    "brightBlack": "#767676", "brightBlue": "#3B78FF", "brightCyan": "#61D6D6",
    "brightGreen": "#16C60C", "brightPurple": "#B4009E", "brightRed": "#E74856",
    "brightWhite": "#F2F2F2", "brightYellow": "#F9F1A5", "cyan": "#3A96DD",
    "green": "#13A10E", "purple": "#881798", "red": "#C50F1F",
    "selectionBackground": "#FFFFFF", "white": "#CCCCCC", "yellow": "#C19C00",
}

# A fixed namespace so a seat's guid is stable across runs and machines.
NS = uuid.UUID("6ba7b812-9dad-11d1-80b4-00c04fd430c8")


def seat_guid(seat):
    return "{%s}" % uuid.uuid5(NS, "rimworld-seat-" + seat)


def build(seat):
    colour, _ = SEATS[seat]
    scheme = dict(CAMPBELL, name=f"Seat {seat}", foreground=colour,
                  cursorColor=colour)
    # A LOGIN shell, so the owner's PATH applies and `claude` resolves exactly as
    # when they type it (~/.local/bin/claude, verified present on a `bash -lc`).
    # AGENT_SEAT is exported before the exec, so Claude Code and every hook it
    # spawns inherit it — that variable is the whole zero-typing mechanism.
    # Claude Code is NOT exec'd into: when the owner quits it the tab drops to a
    # login shell that still carries AGENT_SEAT, rather than closing the window.
    inner = (f"cd {REPO_WSL} && export AGENT_SEAT={seat} && "
             f"{LAUNCH.format(seat=seat)}; exec $SHELL -l")
    profile = {
        "guid": seat_guid(seat),
        "name": f"AGENT {seat}",
        "tabTitle": f"AGENT {seat}",
        "commandline": f'wsl.exe -d {DISTRO} -- bash -lc "{inner}"',
        "startingDirectory": REPO_WIN,
        "colorScheme": f"Seat {seat}",
        "tabColor": colour,
        # false let `wsl.exe` overwrite the tab with its own path. See the
        # module docstring — this is the fix for "the tab says wsl.exe".
        "suppressApplicationTitle": True,
    }
    return profile, scheme


def load(path):
    raw = open(path, encoding="utf-8-sig").read()
    # Windows Terminal permits // comments; json does not.
    stripped = re.sub(r"^\s*//.*$", "", raw, flags=re.M)
    return json.loads(stripped)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the change (default: plan only)")
    ap.add_argument("--settings", default=SETTINGS)
    ap.add_argument("--font-size", type=float, default=12,
                    help="point size written to profiles.defaults, so it applies "
                         "to EVERY window, not just the seats. Default 12, which "
                         "is Windows Terminal's own default and what the owner "
                         "settled on after trying 6 and 18. Use 0 to leave the "
                         "font untouched.")
    args = ap.parse_args()

    if not os.path.exists(args.settings):
        sys.exit(f"settings.json not found: {args.settings}")

    d = load(args.settings)
    profiles = d.setdefault("profiles", {})
    plist = profiles.setdefault("list", [])
    schemes = d.setdefault("schemes", [])

    added = updated = 0
    for seat in SEATS:
        profile, scheme = build(seat)

        i = next((n for n, p in enumerate(plist)
                  if p.get("guid") == profile["guid"]), None)
        if i is None:
            plist.append(profile)
            added += 1
        else:
            plist[i].update(profile)
            updated += 1

        j = next((n for n, s in enumerate(schemes)
                  if s.get("name") == scheme["name"]), None)
        if j is None:
            schemes.append(scheme)
        else:
            schemes[j] = scheme

    # Font size goes in profiles.defaults, NOT in the seat profiles. The owner's
    # complaint is that windows start too big generally, and defaults is the one
    # place that fixes every profile at once — including the Ubuntu and
    # PowerShell tabs they open by hand. Seats then inherit it, so there is a
    # single value to change later instead of six.
    if args.font_size:
        font = profiles.setdefault("defaults", {}).setdefault("font", {})
        font["size"] = args.font_size

    print(f"{'APPLY' if args.apply else 'PLAN'}: {added} profile(s) to add, "
          f"{updated} to update, {len(SEATS)} scheme(s) synced")
    for seat, (colour, why) in SEATS.items():
        print(f"  AGENT {seat:<8} {colour}  tab+text  {why}")
    if args.font_size:
        print(f"  font size: {args.font_size:g} pt -> profiles.defaults, so EVERY "
              f"window, not just the seats")
        if args.font_size != 12:
            print(f"             (Windows Terminal's own default is 12, which is "
                  f"what the owner settled on)")
        if args.font_size <= 8:
            print(f"             ⚠️ {args.font_size:g} pt is small; 6 was rejected "
                  f"as unreadable on this display")
    else:
        print("  font: untouched")
    print("  font FACE: left inherited deliberately — pinning one here would be "
          "the first thing to go stale if you change it")

    if not args.apply:
        print("\nnothing written. re-run with --apply")
        return

    # One backup, not a pile. The owner tunes font size by re-running this, and
    # each run used to leave another .bak beside their settings — four after one
    # sizing session. A single rolling backup keeps the recovery path (a
    # malformed settings.json drops Windows Terminal to defaults silently)
    # without the litter.
    backup = f"{args.settings}.bak"
    shutil.copy2(args.settings, backup)
    for stale in glob.glob(f"{args.settings}.*-*.bak"):    # timestamped, pre-2026-08-13
        os.remove(stale)

    text = json.dumps(d, indent=4, ensure_ascii=False)
    json.loads(text)                       # never write what will not parse back
    with open(args.settings, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")

    print(f"\nwritten. backup: {backup}")
    print("Windows Terminal picks this up on save — open the tab dropdown.")
    print("⚠️ COMMENTS ARE STRIPPED: settings.json is rewritten as plain JSON.")


if __name__ == "__main__":
    main()
