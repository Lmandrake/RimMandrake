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
  # git quotes a path holding a newline, tab, quote or backslash: that line is not the path, so it can match no
  # listed path (a caller listing the quoted spelling would otherwise pass it); such a path is refused by name
  case $p in \"*) die "'$p' holds a character git quotes; land.sh cannot check it against the list: use ./publish";; esac
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
  # a peer's fetch in the same clone can win the ref update ("incorrect old value provided"): that fetch is tried
  # again; three failures in a row are a real fetch fault
  git fetch -q "$REM" "$BR" || { sleep 1; git fetch -q "$REM" "$BR"; } || { sleep 2; git fetch -q "$REM" "$BR"; } \
    || die "git fetch $REM $BR failed three times"
  # --verify -q: a failed bare rev-parse echoes its argument to stdout, which then sat in UP above the real sha
  UP=$(git rev-parse --verify -q "$REM/$BR^{commit}" || git rev-parse --verify -q "FETCH_HEAD^{commit}") \
    || die "cannot read $REM/$BR after the fetch"

  if [ "$MODE" = sha ]; then
    [ "$(git rev-list --parents -n1 "$C" | wc -w)" -eq 2 ] || die "$C is a root or merge commit"
    if git merge-base --is-ancestor "$C" "$UP"; then die "$C is already an ancestor of $REM/$BR"; fi
    git cherry "$UP" "$C" "$C^" 2>/dev/null | grep -q '^-' && die "$C is already on $REM/$BR (patch-equivalent)"
    # one path per line: git quotes a path holding a newline (or a quote or backslash), so it never reads as a
    # listed one; never -z through tr, which split such a path into two listed-looking names
    git -c core.quotePath=false diff-tree --no-commit-id --name-only -r "$C^" "$C" > "$TMPB"
    [ -s "$TMPB" ] || die "$C changes no paths"
    while IFS= read -r f; do
      covered "$f" "$@" || die "$C changes '$f', outside the listed paths"
    done < "$TMPB"
    T=$(git merge-tree --write-tree --merge-base="$C^" "$UP" "$C") || die "conflict replaying $C onto $UP"
    # the merge detects renames: our edit to a listed path can land on upstream's new, unlisted name; check what
    # the published commit itself changes, not only what $C changed
    git -c core.quotePath=false diff-tree --no-commit-id --name-only -r "$UP" "$T" > "$TMPB"
    while IFS= read -r f; do
      covered "$f" "$@" || die "replaying $C onto $UP changes '$f', outside the listed paths (an upstream rename?)"
    done < "$TMPB"
    # the GIT_AUTHOR_* prefixes belong on commit-tree: on the left of the pipe they reached only git show
    AN=$(git show -s --format=%an "$C"); AE=$(git show -s --format=%ae "$C"); AD=$(git show -s --format=%aI "$C")
    N=$(git show -s --format=%B "$C" | GIT_AUTHOR_NAME=$AN GIT_AUTHOR_EMAIL=$AE GIT_AUTHOR_DATE=$AD \
        git commit-tree "$T" -p "$UP" -F -)
  else
    rm -f "$IDX"
    GIT_INDEX_FILE=$IDX git read-tree "$UP"
    for p in "$@"; do
      # --literal-pathspecs: a listed path is that path, never a glob ('a[1].txt' also matched a1.txt)
      [ -e "$p" ] || [ -n "$(git --literal-pathspecs ls-tree "$UP" -- "$p")" ] || die "path '$p' not in worktree or origin"
      if [ -e "$p" ]; then GIT_INDEX_FILE=$IDX git --literal-pathspecs add -A -- "$p"
      else GIT_INDEX_FILE=$IDX git --literal-pathspecs rm -q -r --cached -- "$p"; fi
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
  # the race also comes in a pre-push hook's words (the ledger lint's NOT_APPEND against the newer tip): any refusal
  # while origin moved off UP is the race, whatever it says; a refusal with origin standing still is a verdict
  NOW=$(git ls-remote "$REM" "refs/heads/$BR" 2>/dev/null | cut -f1)
  if ! grep -q -e rejected -e non-fast-forward -e "fetch first" "$TMPB.push" && { [ -z "$NOW" ] || [ "$NOW" = "$UP" ]; }; then
    cat "$TMPB.push" >&2; die "push failed"
  fi
  TRY=$((TRY + 1)); [ "$TRY" -lt 5 ] || { cat "$TMPB.push" >&2; die "push rejected $TRY times: origin keeps moving"; }
  echo "land.sh: origin moved during the push; rebuilding on the new tip (try $((TRY + 1)))" >&2; sleep "$TRY"
done
git update-ref "refs/remotes/$REM/$BR" "$N" 2>/dev/null || true
if [ "${LAND_SYNC:-1}" != 0 ] && [ "$REM" = origin ] && [ "$BR" = main ] && [ -f "$HERE/seat_sync.py" ]; then
  # sha mode: $C is the commit this run just published as $N, a proof seat_sync's landed_twin cannot always rebuild (a
  # union shard plus a file origin changed since: RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS)
  SUP=; [ "$MODE" = sha ] && SUP="--superseded $C"
  # shellcheck disable=SC2086
  python3 "$HERE/seat_sync.py" --no-fetch --repo "$REPO" $SUP >&2 || echo "land.sh: clone left as is (see above); ./sync once it is safe" >&2
fi
echo "PUBLISHED $N"
