# BOUNDARY: every Claude session is launched with permissions skipped, Design Version 0.1.0

Code: `src/RimMandrake/Utils/launch_permissions.py`; `skip_args` in `src/RimMandrake/Utils/claude_bounded.sh`; the settings
default that `infrastructure/stevedesktop/bootstrap_wsl.sh` writes; `rm-launch-permissions.timer`.
Item: `RIMMANDRAKE_SKIP_PERMISSIONS_EVERYWHERE_AUTO_MODE_BLOCKED_HIM`.
Each promise has a check in `src/RimMandrake/Utils/selftest_launch_permissions.py`.

The owner, 2026-11-20: "those Claude's were on Auto mode and thus required continual allow buttons to the point I could
not use them. Please ensure all Claude sessions everywhere have dangerously skip permissions in their launch
specifications from now on."

What happened (measured 2026-11-20). The two seat lines of `C:\SteveDesktop\claude_fleet.ps1` had no permission flag, and
SteveDesktop's `~/.claude/settings.json` had no default mode. The CLI then started the Runner in auto mode and the
sessions of the Server in default mode. Nothing read launch lines. On 2026-11-23, 10 launches in this repo still lacked
the flag.

## ACCEPTS (the only inputs this is built for)

- **a-tracked-file.** A Python, shell, PowerShell, unit, JSON or C# file that git tracks. It is not a selftest, an
  acceptance case, a design record or a skill.
- **a-machine.** Archmagi (this WSL) and SteveDesktop (`stevedesktop-wsl` over ssh): the settings file, the fleet file,
  the Windows Terminal profiles and the running sessions.

## DOES NOT SURVIVE (not promised)

- **a-command-in-prose.** A Markdown file that tells an agent to run `claude` is not read.
- **a-program-named-at-run-time.** A launch that gets the program's name from an environment variable with no mention of
  Claude in its file is not seen. `claude_bounded.sh` adds the flag if the launch goes through it.
- **the-Macs-and-the-Windows-side.** They read NOT CHECKED. There is no route from Archmagi to the Macs.
- **a-folder-trust-question.** A first session in a folder under a new login asks once if the folder is trusted. That
  question is not a permission mode.

- **an-unreadable-schedule.** `install_wt_seat_profiles.py` reads `dispatcher_schedule.json`. If that tracked file cannot
  be read, the installer writes the plain launch line. The plain launch line also skips permissions.

## PROMISES (each one is owed a check)

- **a-launch-without-the-flag-is-red.** An argv, a command line or a command in a brief that starts a session and is not
  sure to carry the flag (on every branch) reads LACKS, exit 1. The lines that blocked him are planted and read LACKS.
- **a-closed-tool-list-is-its-own-answer.** A headless call with `--tools` reads WALLED. It is a blind judge, it can show
  no prompt, and the flag would open the wall. `--allowed-tools` is not a wall.
- **a-route-it-cannot-read-is-named.** A file that names the Claude program with no readable launch, a file that does not
  parse, and a machine that does not answer read COULD NOT LOOK (exit 3), never clean.
- **an-exception-carries-its-reason.** An exception is a line in `EXCEPTIONS`. An exception that excuses nothing is red.
- **installed-and-running.** `live` judges the settings default, the deployed fleet file, the Terminal profiles and each
  running session of both machines. Its reading moves only on a whole clean look. Another look is written beside it.
- **the-one-launcher-adds-a-forgotten-flag.** `claude_bounded.sh` adds the flag when its caller names no permission mode
  and no closed tool list. It adds nothing to `auth`, `update` and the like.
- **every-launch-specification-in-this-tree.** The selftest reads this tree at `./publish` and is red on a LACKS or a
  COULD NOT LOOK. A reader that no longer sees a route known on 2026-11-23 is also red.

## LIMITS

- The ssh probe and the git call have a 60 s and a 120 s hang guard. An ssh to a machine that is down does not return.
- The timer runs every 2 hours. The promise dies at 30 hours, because SteveDesktop restarts and can be off for hours.
