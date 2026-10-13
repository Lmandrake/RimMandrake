# TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO

## spec
Owner, 2026-10-13 (corrected scope): *"for all PAWNS on the map, record their vitals as a function of time. Alive, hurt, hostile, dead, mood. Motivated because so many validation runs fail because a mech cluster lands and mecs wipe out the colony, while a tester waits for a colonist to come and do a job. We asked that many such telemetry channels be hypothosized that would detect when conditions were "far from bland" for testing purposes, but that this would be useful at other times."*

- Per map, sampled on a tick cadence: every spawned pawn's alive / hurt (health %, downed, bleeding) / hostile-to-player / dead / mood, rolled up by faction class (colonist, hostile, neutral, animal, mech) and kept per pawn where cheap.
- "Far from bland" detectors: hostiles present, colonists downed/dead/mental-break, alive colonists = 0, a colonist turned hostile, mood collapse, mech cluster / raid arrival. Alarm into RimPulse and mark a validation run INDETERMINATE/DISRUPTED.
- Ingest as rm_game_pawns_* series in the telemetry stack (skills/telemetry).

## prior work (read first)
- Owner's original question and the GPT review: `Transient/foundry_map_awareness_gpt_prompt_20261010.md`, `Transient/foundry_map_awareness_review_gpt_20261010.md` (GPT kept on-demand `scene_report` primary and deferred any cadence recorder to "Phase 3 only after a measured gap" — that is where the time series dropped).
- Built 2026-10-10: `Transient/foundry_map_awareness_build_20261010.md` (scene_report, CLEAN/DISRUPTED/INDETERMINATE verdict, origin recorder in JawaBenchAwareness.cs).
- Metrics GPT review: `Transient/foundry_metrics_review_gpt_20261010.md:332` ("Pawn workload composition").
- Measured gap: pass 7 (2026-10-13) — the test colony died after a ~10-day clock jump; no instrument noticed; the owner saw the game-over letter on screen.
