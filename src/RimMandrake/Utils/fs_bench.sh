#!/usr/bin/env bash
# fs_bench.sh - same workload, four access paths, so "WSL is slow" becomes a number.
#
# The question this answers: if Claude Code ran natively on Windows instead of
# under WSL, how much faster would file work actually be? That decision has been
# argued from folklore ("9P is slow") without a measurement of the thing that
# matters - the agent's real workload, which is many small files, tree walks,
# content search, and git.
#
# THE COMPARISON THAT DECIDES IT is row 2 vs row 3: the SAME physical disk (D:),
# reached through the 9P bridge from inside WSL, versus reached natively by Git
# Bash on Windows. Git Bash is what a native-Windows Claude Code would use for
# its Bash tool, so that pair isolates the bridge from everything else.
#
# Row 1 (ext4) is the ceiling - what you would get by moving the repo inside WSL.
# Row 4 (PowerShell/.NET) shows how much of any Windows-side number is the shell
# rather than the filesystem; PowerShell cmdlets have famously high per-call cost,
# so a slow PowerShell result must not be read as a slow filesystem.
#
# Usage: ./fs_bench.sh [file_count]     (default 500)

set -uo pipefail
N="${1:-500}"
GITBASH="/mnt/c/Program Files/Git/bin/bash.exe"
PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
OUT="/mnt/d/Luke/dev/Rimworld/observed/resource_watch/fs_bench_$(date +%Y%m%d_%H%M%S).txt"

# The workload. Written once, run verbatim by both bash environments so the only
# variable is the path to the disk. $1 = a scratch directory.
WORKLOAD='
d="$1/bench_$$"; mkdir -p "$d" || { echo "SKIP cannot write"; exit 1; }
t(){ python3 -c "import time;print(time.time())" 2>/dev/null || date +%s.%N; }
el(){ awk -v a="$1" -v b="$2" "BEGIN{printf \"%.3f\", b-a}"; }
a=$(t); i=0; while [ $i -lt '"$N"' ]; do printf "line %d padding content here for grep\n" $i > "$d/f$i.txt"; i=$((i+1)); done; b=$(t); W=$(el $a $b)
a=$(t); ls -la "$d" >/dev/null; find "$d" -type f >/dev/null; b=$(t); S=$(el $a $b)
a=$(t); cat "$d"/*.txt >/dev/null 2>&1; b=$(t); R=$(el $a $b)
a=$(t); grep -rl "padding" "$d" >/dev/null 2>&1; b=$(t); G=$(el $a $b)
a=$(t); rm -rf "$d"; b=$(t); D=$(el $a $b)
echo "$W $S $R $G $D"
'

run_bash() {  # $1=label  $2=bash binary  $3=scratch dir
  local r
  r=$("$2" -c "$WORKLOAD" _ "$3" 2>/dev/null | tail -1)
  [ -z "$r" ] && r="- - - - -"
  printf "%-26s %8s %8s %8s %8s %8s\n" "$1" $r
}

{
echo "fs_bench  $(date -Iseconds)   N=$N small files, identical workload"
echo "host: $(uname -r)   git-bash: $([ -x "$GITBASH" ] && echo present || echo MISSING)"
echo
printf "%-26s %8s %8s %8s %8s %8s\n" "access path" "write" "stat" "read" "grep" "delete"
printf "%-26s %8s %8s %8s %8s %8s\n" "--------------------------" "-------" "-------" "-------" "-------" "-------"

run_bash "1 WSL bash -> ext4 (~)"     /bin/bash "$HOME"
run_bash "2 WSL bash -> /mnt/d (9P)"  /bin/bash "/mnt/d/Luke"
if [ -x "$GITBASH" ]; then
  # Git Bash cannot see /mnt/d; it takes the Windows path for the same disk.
  run_bash "3 Git Bash -> D:\\ (NTFS)" "$GITBASH" "D:/Luke"
else
  printf "%-26s %s\n" "3 Git Bash -> D:\\ (NTFS)" "MISSING"
fi

# PowerShell using .NET IO directly, not cmdlets - measuring the filesystem,
# not Get-ChildItem's object pipeline.
PSRES=$("$PS" -NoProfile -Command '
$d = "D:\Luke\bench_ps_" + $PID; New-Item -ItemType Directory -Path $d -Force | Out-Null
function el($sb){ $s=[Diagnostics.Stopwatch]::StartNew(); & $sb; $s.Stop(); "{0:N3}" -f $s.Elapsed.TotalSeconds }
$w = el { 0..('"$N"'-1) | ForEach-Object { [IO.File]::WriteAllText("$d\f$_.txt","line $_ padding content here for grep`n") } }
$s = el { [IO.Directory]::GetFiles($d) | Out-Null; [IO.Directory]::EnumerateFiles($d,"*",[IO.SearchOption]::AllDirectories) | Measure-Object | Out-Null }
$r = el { foreach($f in [IO.Directory]::GetFiles($d)){ [IO.File]::ReadAllText($f) | Out-Null } }
$g = el { foreach($f in [IO.Directory]::GetFiles($d)){ if([IO.File]::ReadAllText($f) -match "padding"){} } }
$x = el { [IO.Directory]::Delete($d,$true) }
"$w $s $r $g $x"' 2>/dev/null | tr -d '\r' | tail -1)
[ -z "$PSRES" ] && PSRES="- - - - -"
printf "%-26s %8s %8s %8s %8s %8s\n" "4 PowerShell/.NET -> D:\\" $PSRES

echo
echo "--- the composite real-world case: git status on the actual repo ---"
for pair in "WSL bash:/bin/bash:/mnt/d/Luke/dev/Rimworld" "Git Bash:$GITBASH:D:/Luke/dev/Rimworld"; do
  lbl="${pair%%:*}"; rest="${pair#*:}"; bin="${rest%%:*}"; dir="${rest#*:}"
  if [ -x "$bin" ]; then
    v=$("$bin" -c 'cd "$1" || exit; s=$(date +%s%N); git status --porcelain >/dev/null 2>&1; e=$(date +%s%N); awk -v a=$s -v b=$e "BEGIN{printf \"%.2f\", (b-a)/1000000000}"' _ "$dir" 2>/dev/null | tail -1)
    printf "  %-12s git status  %ss\n" "$lbl" "${v:-?}"
  fi
done
echo
echo "Read row 2 vs row 3. That difference IS the 9P bridge; everything else is noise."
} | tee "$OUT"
echo
echo "saved: $OUT"
