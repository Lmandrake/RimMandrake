On SteveDesktop the game environment (RM_STEAMAPPS, RM_DATA_ROOT, WSLENV /p entries, python.exe on PATH) comes only from ~/rm/runner/infrastructure/stevedesktop/testcentre_env.sh sourced by .bashrc; a systemd --user unit, cron or non-interactive ssh does not get it, so every unattended job must source it explicitly or it silently drives the wrong paths.

Pool reading instance: scratch_clone.py pool on SteveDesktop without testcentre_env.sh reads Archmagi's 210 GB floor (slot_rules.json) against the 79 GB /home/mandrake/rm disk, so it reports margin -188 GB and breach 1; with RM_POOL_FLOOR_GB=12 sourced the same pool reads margin 1.62 GB, breach 0 (2026-11-26).
home: infrastructure/stevedesktop/RUNBOOK.md
