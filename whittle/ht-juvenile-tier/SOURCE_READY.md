# Source ready — PARENT COMMIT requested

All production and focused-test build inputs are finished. No build has run. No test-race XML change is needed.

Rationale: fresh tools-disabled Opus keeps AdultTier lineage eligibility to preserve calf allowance even below supported T2 under custom ladders. Only spacing uses the largest supported stage, falling back conservatively on malformed stages. Existing gates and comp/runtime authorities remain unchanged (reproducible before-model identity checks retained).

Exact paths to commit:

- `src/RimMandrake/HugeThings/Source/Kernel/RM_TitanicKernel.cs`
- `src/RimMandrake/HugeThings/Source/Titanic/Tiering/TitanicTierUtility.cs`
- `src/RimMandrake/HugeThings/Source/Titanic/Events/TitanPassage.cs`
- `src/RimMandrake/HugeThings/Source/Titanic/Events/JuvenileTierValidationHooks.cs`
- `src/RimMandrake/HugeThings/Source/RM_HugeThings.csproj`
- `src/RimMandrake/HugeThings/Source/SelfTest/JuvenileTier/JuvenileTier.csproj`
- `src/RimMandrake/HugeThings/Source/SelfTest/JuvenileTier/Program.cs`
- `src/RimMandrake/HugeThings/Source/SelfTest/JuvenileTier/Stubs.cs`
- `src/RimMandrake/Utils/selftest_hugethings_juvenile_tier.py`
- `src/RimMandrake/HugeThings/northstar/juvenile_tier_live.py`
- `src/RimMandrake/HugeThings/TIERING.md`
- `design/RimMandrake/hugethings_codex_2026-11-09/JUVENILE_PASSAGE_CLASSIFICATION.md`
- `infrastructure/state/delegated/2026-11-11/RIMMANDRAKE_REVIEW_HUGETHINGS_JUVENILE_PASSAGE_CLASSIFICATION.json`

Exact ready hashes: `evidence/source-ready-hashes.json`.

After parent writes SOURCE_COMMITTED.json, NEXT: run only focused juvenile-tier and relevant passage tests through run_selftests.py --only ... --workers 1; build HugeThings using winbuild.py with SteveDesktop properties; verify DLL/stamp source identity; acquire fresh host lease only for deployment/live Entry-state proof and release immediately afterward. Parent retains commits/publication/ledger/CLEAN/final acceptance.
