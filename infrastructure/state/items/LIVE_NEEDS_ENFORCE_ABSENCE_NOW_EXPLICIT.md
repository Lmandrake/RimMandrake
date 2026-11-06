# LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT

Owner, 2026-11-05: *"The stronger version was rejected because some tests might be specifically intending to not
include all the mods to see what happens. I would have preferred if that would have been an explicit tag/option in the
specification to say "ignore this MOD's lack of presence" rather than weakening the entire concept. Please evaluate the
stronger version again other than this complaint, and if it's superior, let's implement the stronger version with this
new capability for the unusual test of "intentionally don't include a needed mod." That's quite an edge case to cater
to."*

Conductor's evaluation, 2026-11-05: the stronger version is superior. It aims at R1 and R2 of the census in
`design/RimMandrake/live_mods_filing_check_2026-11-05.md` §2 (20 items, most of the lost item-games); the minimal scope
built by LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING (ae868f1adb) refuses only R4 (5 items) and *warns* on the rest, and
a warning in an unattended pipeline changes nothing. The costs are lopsided: a false positive loads one extra mod
(seconds); a false negative wastes a ~15-minute cold load and a hand repair. The blind review's other objections are
answered below, not by cutting scope.

## spec

Build on `src/RimMandrake/rimflow/relentless_needs.py` (the resolver already shipped). Design of record: the doc's §5
and its §7 replay table, changed as follows.

1. **Enforce, don't warn.** A `sure` need (fixture save `<modIds>`, script path incl. folded source → composed mod,
   CLI `--mod`/scenario JSON, single-owner type/namespace or defName, hard `modDependencies` closure) is ADDED to the
   planned load by `mod_gap`/`batch_gap` before the slot. Soft/ambiguous needs (multi-owner, MayRequire only) still
   only warn.
2. **Derive at the gate; never write into the proof file.** This answers the review's finding 2 (no mutation
   protocol, concurrent edits, decision provenance, `# auto:` parse trap): nothing is persisted in the proof. Each
   run row in `runs.jsonl` records the effective mod list and every inferred addition with its evidence, so a verdict
   always says what environment produced it. The filing/proof-write check prints the same inferred list as
   information.
3. **The opt-out is explicit: `live-without: <mods>`** — the proof intends to run without these mods. Effect:
   inference never adds a listed mod; the gate refuses (holds before the slot, never after) a rider whose planned load
   contains a listed mod, and `batch_gap` never batches a rider needing X with one that is `live-without: X`. Names
   resolve through the same resolver; an unknown name is refused. Staging still only enables (whole-list swaps stay
   with LANE_TIER_WIRE_A_WHOLE_LIST_LOAD; `live-tier:` stays out of scope).
4. **Absence assertions are not needs.** A defName reached only inside an absence check (`--absent X`, an
   `assert_absent`/"not present" probe) gives no need, even unflagged (the review's `--absent RUT_PaleMoss` case).
5. **One-time migration.** Run the resolver over every live proof in `infrastructure/state/live_proofs/`; list every
   addition it would make. Where an addition contradicts the proof's intent (it measures a mod's absence), add
   `live-without:` to that proof. Commit the list as evidence.
6. Stale index (DLL/def dump older than the deploy fingerprint) degrades `sure` to warn, never to a refusal.

## verify

- Selftests under `run_selftests.py --only relentless_needs` plus the touched live_round/game tests: each source
  yields its need; `live-without` blocks inference and refuses a conflicting load; mixed batch (needs X / without X)
  splits; absence-assertion defName gives zero; stale index warns only; resolver idempotent.
- Historical replay per design §7.2, using proof text AND scripts at the historical sha.

## criteria

- Replay: at least 17 of the 20 R1/R2 items get the right mod added before repair; zero wrong additions.
- Negative control: zero additions on the last 50 PASS proofs, after the migration's `live-without:` lines.
- One week after landing: runs failing on a mod-list cause in `runs.jsonl`, against a baseline recounted first.
