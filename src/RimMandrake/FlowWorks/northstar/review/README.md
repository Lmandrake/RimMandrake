# FlowWorks capability review sheet

`FlowWorks_review.html` — one row per INTENDED FlowWorks capability (built or not), grouped by subsystem, with a
derived status: PROVEN-LIVE (a mapped mechanism row PASSed in the newest `../validation_v2_result_*.json`),
BUILT-UNPROVEN (every declared probe exists on disk), PARTIAL (some do), NOT BUILT (none). The brief lists what
remains to build, per open ledger item.

- Regenerate: `python3 src/RimMandrake/FlowWorks/human_review.py` (capability table is data at its top).
- Selftest: `python3 src/RimMandrake/FlowWorks/northstar/selftest_human_review.py`.
- `FlowWorks_review.decisions.json` is the owner's once it exists: the generator writes it only when absent.
- `shots/` = downscaled copies of the 2026-10-05 live-run screenshots + the Quarry reference (ruling 33).
- Lives under `northstar/` so it does not move modcheck's mod hash; held from deploy in `src/DEPLOY_HOLD.txt`.
