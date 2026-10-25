# SteveDesktop test-centre environment, sourced at the TOP of ~/.bashrc in Steve's WSL
# (before the "not interactive -> return" line, so ssh commands get it too):
#
#     [ -f ~/rm/runner/infrastructure/stevedesktop/testcentre_env.sh ] && . ~/rm/runner/infrastructure/stevedesktop/testcentre_env.sh
#
# STEVEDESKTOP_USERDATA_FIX_STEVE_UNTOUCHED / GAME_PATHS_REWIRE_ONE_ENV_PER_MACHINE (2026-10-25).
# game_paths.py reads these, so every tool in the runner clone resolves Steve's install and the
# test-only save-data folder instead of Archmagi's C:\ paths. The game is launched with
# -savedatafolder=D:\RimTest\userdata (rw_game.sh), so Steve's own ModsConfig and saves in his
# LocalLow are never read or written. Unity still writes Player.log to his LocalLow.
#
# WSLENV /p hands Windows python.exe (the only process that reaches the bridge on Windows
# loopback) the D:\ form of each path, and hands it back to `wsl.exe python3` children.

export RM_STEAMAPPS=/mnt/d/SteamLibrary/steamapps
export RM_GAME_USERDATA=/mnt/d/RimTest/userdata
export RM_GAME_LOGDIR="/mnt/c/Users/sjlewis/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
export RM_DATA_ROOT=/mnt/d/RimTest/data

for _v in RM_STEAMAPPS/p RM_GAME_USERDATA/p RM_GAME_LOGDIR/p RM_DATA_ROOT/p; do
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
