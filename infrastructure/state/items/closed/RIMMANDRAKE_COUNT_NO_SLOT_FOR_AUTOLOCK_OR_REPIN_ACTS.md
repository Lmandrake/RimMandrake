## spec
resolve adds an autolock or autorepin act to launches, and every later gate counts len(launches) as occupancy, so at max_live 1 with nothing live a steward behind an autolock reads slots_full (item 8), though both acts are documented as taking no slot. Fix: the gate counts planned runs, not acts.
Pre-existing, found by the Codex full-file review of the split fixes (D:\ClaudeWork\rimmandrake\conductor\cr\r_ma_split_fixes.txt). Minimal diff inside maturation_autonomy.py.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py --all (section acts_take_no_slot, red on 260b1dc67a, watched).

## refs
file: src/RimMandrake/rimflow/maturation_autonomy.py

## criteria
- Its section fails on base and passes after; selftest_maturation_autonomy stays green.

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_autonomy_review_findings.py
