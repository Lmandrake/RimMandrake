# Parent source commit update required before retry

Fresh tools-disabled independent Opus Test Pilot complete: evidence/pilot_prompt.txt, pilot_raw.json, pilot_call.json (rc0). Three previous nonpasses retained. No game lease taken.

Concrete fixes, all finished:

- `src/RimMandrake/HugeThings/Source/Titanic/Events/JuvenileTierValidationHooks.cs`: actual engine API is pawn.ageTracker.CurLifeStage (confirmed by engine IL and compiler), not pawn.CurLifeStage.
- `src/RimMandrake/HugeThings/Source/SelfTest/JuvenileTier/Program.cs`: invariant-culture output avoids the Windows CP437 infinity byte0xEC that crashed the shared UTF8 runner; compare logged-error count relative to baseline.
- `src/RimMandrake/Utils/selftest_hugethings_juvenile_tier.py`: retain actual subprocess bytes/rc, render ASCII safely, fail on any non-ASCII output; no shared runner/workflow edit.
- `src/RimMandrake/HugeThings/northstar/juvenile_tier_live.py`: settings tool set returns valueAfter, get returns value; align helper with the actual tool contract before live use.

Production policy and all criteria unchanged. Please commit these four paths and update SOURCE_COMMITTED.json before retry. The required initial HugeThings build failed without replacing its DLL pair.

Additional host-tool issue identified before taking a lease: modset_builder.bridge_ok() calls ambient_bridge_host(), which returns None for the default game, so it checks Archmagi despite a fresh SteveDesktop lease. The prior passage16 round used --not-my-bridge with explicit actual-host proof, but this prompt says modset_builder --tier ... --apply --by ... only. Please authorize that same bounded host-mismatch override if needed, or supply an existing supported host selector. I will not patch shared workflows, take Archmagi, or hand-edit ModsConfig.

Parent inbound-reference review corrections are now finished too (Python/spec only):

- `src/RimMandrake/HugeThings/northstar/measure_reefback_calf.py`: current passage instrument has separate spacing tier, preserving lineage admission and habitat/pool/season negatives; existing-T3 reefback juvenile result now agrees with production policy.
- `src/RimMandrake/HugeThings/northstar/selftest_juvenile_policy_model.py`: exhaustive focused source-model truth-table controls plus supported-stage/custom/malformed cases.
- `design/RimMandrake/hugethings_codex_2026-11-09/REEFBACK_CALF_DECISION.md`: current paragraph corrected while preserving original L0/no-deployment history and historical raw evidence.
- `infrastructure/state/items/TITAN_CAMPS_SCAVENGERS_EVENTS_1.md`: spec-only lineage/spacing clarification; every criterion unchanged.

Please include these paths in the parent commit as well, or land them separately before final evidence. This adds no further C# changes.

Also corrected the current REVIEW.md compliance-table sentence to supported-stage spacing (same design directory). Exact nine updated path hashes: evidence/source-ready-update-hashes.json.
