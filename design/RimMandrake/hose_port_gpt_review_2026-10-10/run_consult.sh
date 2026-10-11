#!/bin/sh
# Re-run one consult: sh design/RimMandrake/hose_port_gpt_review_2026-10-10/run_consult.sh C1_flow_and_hose
# (from the repo root). Model gpt-6.1-sol, effort high. Output: gpt_<key>.md beside this script.
D=design/RimMandrake/hose_port_gpt_review_2026-10-10
K="$1"
set --
while IFS= read -r f; do [ -n "$f" ] && set -- "$@" -f "$f"; done < "$D/$K.files.txt"
exec python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file "$D/prompt_$K.md" -m gpt-6.1-sol --effort high \
  --timeout 3000 --out "$D/gpt_$K.md" "$@"
