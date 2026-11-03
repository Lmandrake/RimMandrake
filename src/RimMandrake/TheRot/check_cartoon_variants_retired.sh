#!/usr/bin/env bash
# ROT_CARTOON_VARIANT_REPAINT_1 proof: no cartoon Rot plant variant retired in a8367a60de /
# 1ac6e93480 is live again (by blob, under any name), and the art ledger guard is clean.
# Exit 0 = holds, 1 = a retired picture is back or the guard found unledgered changes.
set -o pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
live=$(git ls-tree -r HEAD -- src/RimMandrake/TheRot/Textures)
[ -n "$live" ] || { echo "UNMEASURED: no Rot textures in HEAD"; exit 1; }
bad=0; n=0
for c in a8367a60de 1ac6e93480; do
  while read -r f; do
    n=$((n+1)); old=$(git rev-parse "$c^:$f")
    hit=$(awk -v o="$old" '$3==o{print $4}' <<<"$live")
    [ -n "$hit" ] && { echo "CARTOON LIVE: $f -> $hit"; bad=1; }
  done < <(git diff --name-only --diff-filter=D "$c^" "$c" -- '*.png')
done
[ "$n" -eq 23 ] || { echo "expected 23 retired files, saw $n"; exit 1; }
python3 src/RimMandrake/Utils/art/art.py guard worktree src/RimMandrake/TheRot/Textures || bad=1
echo "checked $n retired cartoon files; bad=$bad"; exit $bad
