#!/usr/bin/env bash
# Run a PowerShell script (read from stdin) on SteveDesktop's Windows side over OpenSSH.
#
#   echo 'Get-Process steam | Select Id,SessionId' | infrastructure/stevedesktop/sps.sh
#   T=300 infrastructure/stevedesktop/sps.sh < script.ps1
#
# STEVEDESKTOP_PWSH_FIX_QUOTING_BY_ENCODING (2026-10-25). Windows OpenSSH hands the command to
# cmd.exe, so any quote, $, | or ; in an inline `powershell -Command "..."` is mangled
# ("The string is missing the terminator"). -EncodedCommand (base64 of UTF-16LE) carries the
# script through cmd untouched. Progress records are silenced so stdout is not CLIXML noise.
# NOTE: processes started this way run in session 0 (no desktop). To start the GAME use
# rw_game.sh from Steve's WSL, which lands in the logged-in session.
#
# Env: STEVE_WIN (default sjlewis@192.168.86.87), T (timeout seconds, default 120).
set -o pipefail
script="\$ProgressPreference='SilentlyContinue'
$(cat)"
enc=$(printf '%s' "$script" | iconv -f utf-8 -t utf-16le | base64 -w0)
# cmd.exe caps a command line at 8191 chars; base64 of UTF-16 is ~2.7x the script, so a script
# over ~2900 chars would be cut off. Refuse rather than run half a script.
[ ${#enc} -le 8000 ] || { echo "sps.sh: script too long for cmd.exe (${#enc} encoded chars > 8000); copy a .ps1 over and run it with -File" >&2; exit 2; }
exec timeout "${T:-120}" ssh -o BatchMode=yes -o ConnectTimeout=8 -o LogLevel=ERROR "${STEVE_WIN:-sjlewis@192.168.86.87}" \
    "powershell -NoProfile -NonInteractive -EncodedCommand $enc"
