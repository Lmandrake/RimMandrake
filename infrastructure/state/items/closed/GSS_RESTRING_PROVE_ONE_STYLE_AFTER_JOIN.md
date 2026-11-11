## spec
found-by: BENCH helper (2026-11-05), writing live proofs for GSS_RESTRING_FIX_STYLES_UNRECONCILED. Its A1 L2 ("cut the only span joining two runs, restyle sides differently, re-string: the joined run carries one style") has no live row: M15b_restring_rejoins only checks that the nets rejoin (validation_aerial.py ~line 340), M15e checks the colonist job; nothing reads the style of either side after the join.
## criteria
- A1 L0: a row in validation_aerial.py (aerial block, after M15e): cut the only joining span, set a different style on each side via the probe, run the restring job, read both sides' style; PASS = one style on the joined run
- A2 L0: add `live-proof A1:` for it to infrastructure/state/live_proofs/GSS_RESTRING_FIX_STYLES_UNRECONCILED.txt
