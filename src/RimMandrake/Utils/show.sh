#!/usr/bin/env bash
# show.sh — open a path in Windows File Explorer, from WSL.
#
#   ./src/RimMandrake/Utils/show.sh agents                          # repo-relative dir
#   ./src/RimMandrake/Utils/show.sh design/Jawa/worldbuilding/roster_v2.md      # repo-relative file
#   ./src/RimMandrake/Utils/show.sh /mnt/c/Users/Mandrake           # absolute WSL path
#   ./src/RimMandrake/Utils/show.sh 'file:///D:/Luke/dev/a%20b.md'  # file:/// URL, %20 decoded
#   ./src/RimMandrake/Utils/show.sh a b c                           # several, one window each
#
# FILE -> opens the containing folder with the file SELECTED.
# DIR  -> opens the folder itself.
#
# Terminal hyperlinks (OSC 8) and markdown links are inert in this setup, so a
# report cannot be clicked. Bare file:/// URLs stay the written convention —
# double-click copies them — and this is what runs when the owner says "show me".
#
# ⚠️ explorer.exe EXITS 1 ON SUCCESS. Never read its status as failure; this
# script reports on whether it was launched, and exits 0 when it was.
#
# A path that does not exist is refused by name. It never silently opens the
# parent — "here is the folder, your file is not in it" is the wrong answer to
# "show me the file".

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
    echo "usage: $0 <path> [path...]" >&2
    echo "  path: repo-relative | /mnt/... | C:\\... | file:///... (%20 ok)" >&2
    echo "  file -> folder opened with it selected;  dir -> opened directly" >&2
}

# --- %XX -> byte. Only real hex pairs; a bare % passes through untouched.
# printf -v, not a subshell, so a decoded newline is not eaten.
pct_decode() {
    local s=$1 out= hex
    while [[ $s == *%* ]]; do
        out+=${s%%\%*}; s=${s#*%}; hex=${s:0:2}
        if [[ $hex =~ ^[0-9A-Fa-f]{2}$ ]]; then
            printf -v hex '%b' "\\x$hex"; out+=$hex; s=${s:2}
        else
            out+='%'
        fi
    done
    printf '%s' "$out$s"
}

# --- anything -> WSL path. Existence is checked on this side.
to_wsl() {
    local p=$1
    case $p in
        file://*)
            p=$(pct_decode "${p#file://}")
            # file:///D:/x -> /D:/x ; drop the leading slash off the drive
            [[ $p =~ ^/[A-Za-z][:|] ]] && p=${p#/}
            ;;
    esac
    p=${p//|/:}                                  # legacy D|/ drive form
    case $p in
        /*) printf '%s' "$p"; return ;;          # already WSL-absolute
        [A-Za-z]:[/\\]*)                         # Windows path
            if command -v wslpath >/dev/null 2>&1; then
                wslpath -u "$p" 2>/dev/null && return
            fi
            local drive=${p:0:1}
            printf '/mnt/%s/%s' "${drive,,}" "$(printf '%s' "${p:3}" | tr '\\' '/')"
            return ;;
    esac
    printf '%s/%s' "$REPO_ROOT" "$p"             # repo-relative
}

# --- WSL path -> Windows path. wslpath when present, manual otherwise.
to_win() {
    local p=$1
    if command -v wslpath >/dev/null 2>&1; then
        wslpath -w "$p" 2>/dev/null && return
    fi
    # /mnt/d/a/b -> D:\a\b
    if [[ $p =~ ^/mnt/([A-Za-z])(/.*)?$ ]]; then
        local drive=${BASH_REMATCH[1]} rest=${BASH_REMATCH[2]:-/}
        printf '%s:%s' "${drive^^}" "$(printf '%s' "$rest" | tr '/' '\\')"
        return
    fi
    echo "$0: not reachable from Windows: $p" >&2
    return 1
}

case "${1:-}" in
    -h|--help) usage; exit 0 ;;
    "")        usage; exit 2 ;;
esac

rc=0
for arg in "$@"; do
    wsl=$(to_wsl "$arg")
    if [ ! -e "$wsl" ]; then
        echo "$0: no such path: $wsl" >&2
        rc=2
        continue
    fi
    win=$(to_win "$wsl") || { rc=2; continue; }

    if [ -d "$wsl" ]; then
        target="$win"
    else
        target="/select,$win"                    # folder opens, file highlighted
    fi

    # Run from a drive-backed cwd: explorer.exe warns and falls back to C:\ when
    # launched from a \\wsl$ path. Its exit 1 is success, so it is discarded.
    ( cd "$REPO_ROOT" && explorer.exe "$target" ) >/dev/null 2>&1 || true
    echo "opened: $win"
done
exit $rc
