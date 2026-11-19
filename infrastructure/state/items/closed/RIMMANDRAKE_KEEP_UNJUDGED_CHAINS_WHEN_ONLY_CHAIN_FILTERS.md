# RIMMANDRAKE_KEEP_UNJUDGED_CHAINS_WHEN_ONLY_CHAIN_FILTERS

## spec
`python3 src/RimMandrake/Utils/northstar_driver/judge_cli.py <results.json> --only-chain A` (default: rewrite in place) deletes every other chain's components from the saved results file, and every other chain's visual bars turn UNMEASURED ("judge: no component claim to judge"), although they were never selected for judging. Found by Codex (2026-11-18) reviewing judge_cli.py on RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS; reproduced by the filer [measured]. Cause: main() replaces doc["components"] with the filtered list, and apply_verdicts rewrites every visual bar row.

Smallest fix (suggested): judge a filtered copy of the components; keep the saved list whole; apply verdicts only to the bars the selected components claim.

## verify
Acceptance test: `python3 src/RimMandrake/Utils/northstar_driver/case_only_chain_keeps_other_chains.py` — 2 cases, exit 0 when right; watched failing on 86d35cdec8+ (2 wrong: chain B deleted, bar_B rewritten to UNMEASURED). Mock judge, no model.

## criteria
- The case exits 0; selftest_judge_open_look.py and selftest_judge_refusal_records.py stay green.

## refs
file: src/RimMandrake/Utils/northstar_driver/judge_cli.py
file: src/RimMandrake/Utils/northstar_driver/case_only_chain_keeps_other_chains.py
