# SteveDesktop test-centre environment, sourced at the TOP of ~/.bashrc in SteveDesktop's WSL
# (before the "not interactive -> return" line, so ssh commands get it too):
#
#     [ -f ~/rm/runner/infrastructure/stevedesktop/testcentre_env.sh ] && . ~/rm/runner/infrastructure/stevedesktop/testcentre_env.sh
#
# GAME_PATHS_REWIRE_ONE_ENV_PER_MACHINE (2026-10-25). game_paths.py reads these, so every tool
# in the runner clone resolves SteveDesktop's install (D:\SteamLibrary) and the Windows user
# sjlewis's LocalLow instead of Archmagi's C:\ paths. The game there is ours outright (owner,
# 2026-10-25: "this game is ours to play with"): it runs with its normal save-data folder, and the
# runner owns ModsConfig.xml, Prefs.xml and Saves in it. Player.log is written to the same folder.
#
# WSLENV /p hands Windows python.exe (the only process that reaches the bridge on Windows
# loopback) the D:\ form of each path, and hands it back to `wsl.exe python3` children.

export RM_STEAMAPPS=/mnt/d/SteamLibrary/steamapps
export RM_GAME_USERDATA="/mnt/c/Users/sjlewis/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
export RM_GAME_LOGDIR="$RM_GAME_USERDATA"
export RM_DATA_ROOT=/mnt/d/RimTest/data
export RM_INSTANCES_ROOT=/mnt/d/ClaudeWork/rimmandrake/instances   # game_instance.py: where game b's data folder lives

for _v in RM_STEAMAPPS/p RM_GAME_USERDATA/p RM_GAME_LOGDIR/p RM_DATA_ROOT/p RM_INSTANCES_ROOT/p; do
    case ":${WSLENV:-}:" in *":$_v:"*) ;; *) WSLENV=${WSLENV:+$WSLENV:}$_v ;; esac
done
export WSLENV
unset _v

# A Tailscale SSH session has no Windows dirs on PATH (interop works, lookup does not).
for _d in /mnt/c/Windows/System32 /mnt/c/Windows /mnt/c/Windows/System32/WindowsPowerShell/v1.0 \
          "/mnt/c/Program Files/Python313"; do
    case ":$PATH:" in *":$_d:"*) ;; *) [ -d "$_d" ] && PATH=$PATH:$_d ;; esac
done
export PATH
unset _d

# RIMMANDRAKE_MOVE_STEVEDESKTOP_CLONES_TO_SSD_LINUX_DRIVE_SITS_ON_HARD_DISK (2026-11-25): ~/rm here is its own 80 GiB disk on
# the NVMe (infrastructure/stevedesktop/rm_ssd/), not the WSL volume. The pool's disk floor in slot_rules.json
# (ops.disk_brake_free_gb, 210 GB: one worst day of scratch growth on Archmagi's volume) is larger than this whole disk and
# would refuse every new pool clone. The danger here is the ~/rm disk filling mid-run, which breaks every run on it, so the
# floor keeps one run's worst growth free beyond the largest clone: a 4.7 GB fresh check tree (publish makes one when both
# of the machine's kept trees in ~/rm/treecheck-kept are held) plus a 7 GB Saves backup seen in one pool clone
# (2026-11-22). The machine's two kept trees (9.4 GB) are made once and stay; rm-pool-room.timer reads the room each hour.
export RM_POOL_FLOOR_GB=12
