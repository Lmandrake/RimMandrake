#!/usr/bin/env bash
# findings_judge.sh - the daily findings judge (and Friday memory sweep) that replaced FOUNDRY's window duty.
# Owner by card 2026-11-02: "What should happen to FOUNDRY? -> Retire it (Recommended)" ("the daily findings read
# becomes a scheduled job"). Run by rm-findings-judge.timer on BENCH's clone. Model: opus (Agent_Policy.md: its
# decisions become recorded facts other work cites). Reading: $OUT/last.json, written on every run, ok or not.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUT="${FINDINGS_JUDGE_OUT:-/mnt/d/ClaudeWork/rimmandrake/findings_judge}"
MODEL="${FINDINGS_JUDGE_MODEL:-opus}"
mkdir -p "$OUT"
cd "$ROOT" || exit 2
export AGENT_SEAT=BENCH RIMFLOW_SEAT=BENCH
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
./sync >"$OUT/sync.last" 2>&1 || true
prompt="$(cat src/RimMandrake/Utils/findings_judge_prompt.md)"
friday=false
if [ "$(date +%u)" = 5 ] || [ "${FINDINGS_JUDGE_FRIDAY:-}" = 1 ]; then
  friday=true
  prompt="$prompt
$(cat src/RimMandrake/Utils/findings_judge_friday.md)"
fi
src/RimMandrake/Utils/claude_bounded.sh -p "$prompt" --model "$MODEL" --name "FINDINGS JUDGE $started" \
  --output-format json --dangerously-skip-permissions >"$OUT/run.json" 2>"$OUT/run.err"
rc=$?
python3 - "$OUT" "$started" "$rc" "$friday" "$MODEL" <<'PY'
import json, sys, time
out, started, rc, friday, model = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4] == "true", sys.argv[5]
try:
    res = json.load(open(out + "/run.json"))
    text = str(res.get("result") or "")
    cost = res.get("total_cost_usd")
except (OSError, ValueError):
    text, cost = "", None
line = next((ln for ln in reversed(text.splitlines()) if ln.startswith("JUDGED ")), None)
rec = {"started": started, "ended": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rc": rc, "friday": friday,
       "model": model, "ok": rc == 0 and line is not None, "judged": line, "cost_usd": cost}
json.dump(rec, open(out + "/last.json", "w"), indent=1)
with open(out + "/history.jsonl", "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
PY
st=failed; [ "$rc" = 0 ] && st=ok
python3 src/RimMandrake/Utils/pulse/pulse.py report findings_judge:daily "$st" --cause "findings judge exit $rc" \
  --link "$OUT/last.json" >/dev/null 2>&1 || true
exit "$rc"
