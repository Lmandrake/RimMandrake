# RIMMANDRAKE_FIX_STEVE_CPU_SWEEP_CODEX_REVIEW_FINDINGS

## spec
Codex full-file review 2026-11-17. (1) med l.164: os.makedirs(os.path.dirname(out)) with a bare filename (--out sweep.json) raises FileNotFoundError before preflight [measured by reading: dirname('sweep.json')==''] . (2) low l.249: --cpus 5-3 gives an empty CPU list, writes PASS_UNMEASURED_HEAT with zero tests.
Raw review: /mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_sw.txt. Not fixed at filing.

## refs
file: src/RimMandrake/Utils/steve_cpu_retest/steve_cpu_sweep.py

## criteria
- Each finding has a case that failed on base and passes after, or is ruled not-a-bug.

## verify
python3 -c "import os;os.makedirs(os.path.dirname('sweep.json'))" fails on base; re-check after fix
