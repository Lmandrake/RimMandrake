# LANE_TIER_WIRE_A_WHOLE_LIST_LOAD

Relentless staging can only ENABLE mods onto the live list (`modlist_swap --enable`), so a proof that needs an exact
tier never gets one: VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL A1 (ratchet_pilot, 20..26 running mods) reads WRONG_TIER
forever, and GIZKA_STOWAWAY_UNMEASURED_ROWS_1 A2's judge (`a2_live_proof.py`) demands the running load equal the
`gizkastowaway` tier as a set, which an enable-only Archmagi load can never be. Expedited by the Conductor on the
owner's word 2026-11-05.

## Owner ruling — SteveDesktop is the exact-tier host (by card, 2026-11-05)

"What should SteveDesktop spend its time on now? → Exact-mod-list tests". SteveDesktop (testq lane, `lane=stevedesktop`)
becomes the machine that loads a mod's own tier and runs its suite there; Archmagi keeps its full list and never pays
a ~15-minute swap for an exact-tier proof.

## spec

1. A proof declares its tier (`live-tier: <name>`, resolved by `modset_builder.resolve_tier`). Relentless routes every
   live clause with a `live-tier:` to SteveDesktop through testq (`testq.py submit`, profile = that tier), instead of
   Archmagi's live game; results come back through testq ingest to the item's clause verdict.
2. On Steve, the run loads exactly the tier (whole-list swap, plus all five DLC), and the run row records the actual
   running packageIds; a run whose load is not the tier is UNMEASURED, never a verdict.
3. Batching: riders are batched only within one tier; Steve stays on a tier while jobs for it are queued.
4. Steve's fault monitor still gates: a result inside a fault window is quarantined, never counted
   (`fault_monitor.gate`).
5. Leaves Archmagi staging enable-only; `live-without:` (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT) on an Archmagi proof
   may route that proof to Steve with an explicit tier when the running Archmagi load holds the excluded mod.
6. Then add `live-tier: gizkastowaway` to GIZKA_STOWAWAY_UNMEASURED_ROWS_1's live proof and `live-tier: ratchet_pilot`
   to VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL's, and let both run.

## verify

- Selftests for routing (tier proof → testq job, non-tier proof → Archmagi), tier-exact load check, batching by tier,
  fault-window quarantine.
- Live: one Steve run of the GizkaStowaway tier whose recorded running set equals `resolve_tier("gizkastowaway")`.

## criteria

- GIZKA_STOWAWAY_UNMEASURED_ROWS_1 A2 and VITALS A1 each get a real verdict (PASS or FAIL, not WRONG_TIER/UNMEASURED)
  from a Steve run.
- No exact-tier proof triggers an Archmagi mod-list swap.
