#!/bin/sh
# land.sh - publish ONE explicit commit (or explicit paths) onto origin/main by plumbing.
#   land.sh <sha> <path>...            replay <sha> onto origin/main; every path <sha> changes must be
#                                      one of (or under) the listed paths, else REFUSED
#   land.sh -m "<msg>" <path>...       build the commit itself from the working-tree content of the
#                                      paths, in a TEMP index seeded from origin/main (shared HEAD,
#                                      shared index and peers' unstaged edits are never read/touched)
# Refuses: no sha/paths, merge/root commits, a sha already in origin/main (ancestor or patch-equivalent
# per git cherry), paths outside the list. Push is fast-forward only. Prints PUBLISHED <sha>.
# After the push it records the new origin/main and runs seat_sync.py --no-fetch (beside this file), which
# realigns the clone's main with `git reset --keep` only when every local commit is already upstream, else
# says why not (stderr). LAND_SYNC=0 skips that. stdout stays the one PUBLISHED line.
# Env: LAND_REPO (default: the clone the cwd is in), LAND_REMOTE (origin), LAND_BRANCH (main), LAND_SYNC (1).
set -eu
die() { echo "REFUSED: $*" >&2; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=${LAND_REPO:-$(git rev-parse --show-toplevel 2>/dev/null)} || true
[ -n "$REPO" ] || die "not inside a git clone and LAND_REPO is unset"
REM=${LAND_REMOTE:-origin}; BR=${LAND_BRANCH:-main}
[ $# -ge 1 ] || die "no sha. usage: land.sh <sha> <path>...  |  land.sh -m <msg> <path>..."
cd "$REPO"
MODE=sha; MSG=
if [ "$1" = "-m" ]; then
  [ $# -ge 3 ] || die "-m needs a message and at least one path"
  MODE=paths; MSG=$2; shift 2
else
  SHA=$1; shift
  [ $# -ge 1 ] || die "no paths listed; list every path the commit may change"
  C=$(git rev-parse --verify -q "$SHA^{commit}") || die "'$SHA' is not a commit"
fi
covered() {
  p=$1; shift
  for a in "$@"; do
    a=${a%/}
    [ "$p" = "$a" ] && return 0
    case $p in "$a"/*) return 0;; esac
  done
  return 1
}

TMPB="${TMPDIR:-/tmp}/land.$$"; IDX="$TMPB.idx"
trap 'rm -f "$TMPB" "$TMPB.push" "$IDX"' EXIT

# fetch origin and build N on top of it (re-run when the push loses a race)
build() {
  git fetch -q "$REM" "$BR"
  UP=$(git rev-parse "$REM/$BR" 2>/dev/null || git rev-parse FETCH_HEAD)

  if [ "$MODE" = sha ]; then
    [ "$(git rev-list --parents -n1 "$C" | wc -w)" -eq 2 ] || die "$C is a root or merge commit"
    if git merge-base --is-ancestor "$C" "$UP"; then die "$C is already an ancestor of $REM/$BR"; fi
    git cherry "$UP" "$C" "$C^" 2>/dev/null | grep -q '^-' && die "$C is already on $REM/$BR (patch-equivalent)"
    git diff-tree --no-commit-id --name-only -r -z "$C^" "$C" | tr '\0' '\n' > "$TMPB"
    [ -s "$TMPB" ] || die "$C changes no paths"
    while IFS= read -r f; do
      covered "$f" "$@" || die "$C changes '$f', outside the listed paths"
    done < "$TMPB"
    T=$(git merge-tree --write-tree --merge-base="$C^" "$UP" "$C") || die "conflict replaying $C onto $UP"
    N=$(GIT_AUTHOR_NAME=$(git show -s --format=%an "$C") GIT_AUTHOR_EMAIL=$(git show -s --format=%ae "$C") \
        GIT_AUTHOR_DATE=$(git show -s --format=%aI "$C") \
        git show -s --format=%B "$C" | git commit-tree "$T" -p "$UP" -F -)
  else
    rm -f "$IDX"
    GIT_INDEX_FILE=$IDX git read-tree "$UP"
    for p in "$@"; do
      [ -e "$p" ] || [ -n "$(git ls-tree "$UP" -- "$p")" ] || die "path '$p' not in worktree or origin"
      if [ -e "$p" ]; then GIT_INDEX_FILE=$IDX git add -A -- "$p"; else GIT_INDEX_FILE=$IDX git rm -q -r --cached -- "$p"; fi
    done
    T=$(GIT_INDEX_FILE=$IDX git write-tree)
    [ "$T" != "$(git rev-parse "$UP^{tree}")" ] || die "nothing to land: paths already identical on $REM/$BR"
    N=$(printf '%s\n' "$MSG" | git commit-tree "$T" -p "$UP" -F -)
  fi
}

TRY=0
while :; do
  build "$@"
  git push -q "$REM" "$N:refs/heads/$BR" 2>"$TMPB.push" && break
  grep -q -e rejected -e non-fast-forward -e "fetch first" "$TMPB.push" || { cat "$TMPB.push" >&2; die "push failed"; }
  TRY=$((TRY + 1)); [ "$TRY" -lt 5 ] || { cat "$TMPB.push" >&2; die "push rejected $TRY times: origin keeps moving"; }
  echo "land.sh: origin moved during the push; rebuilding on the new tip (try $((TRY + 1)))" >&2; sleep "$TRY"
done
git update-ref "refs/remotes/$REM/$BR" "$N" 2>/dev/null || true
if [ "${LAND_SYNC:-1}" != 0 ] && [ "$REM" = origin ] && [ "$BR" = main ] && [ -f "$HERE/seat_sync.py" ]; then
  python3 "$HERE/seat_sync.py" --no-fetch --repo "$REPO" >&2 || echo "land.sh: clone left as is (see above); ./sync once it is safe" >&2
fi
echo "PUBLISHED $N"
