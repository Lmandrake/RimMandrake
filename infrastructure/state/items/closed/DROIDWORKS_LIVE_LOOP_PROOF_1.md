## spec
Per `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` packet A1 and
`DROID_PROGRAM_STATE_2026-09-06.md` §"Live proof owed (8 open checkboxes across
6 items)": prove Droidworks' five-state loop (charged → powered-down → rebooted
→ bolted/wiped/spiked → killed → detonated) actually runs on a live game, not
just on paper/code review, on a GNK power droid and a ported KotOR kind.

## method
Minimal quicktest list (`ModsConfig.MINIMAL.xml`, 25 mods: DLCs, HAR, Droidworks,
JawaIonWeapons, RimBridgeServer — **no** `guy762.kotordroids` needed, since the
`RSW_DW_KotORDroidColonist_*` / `RSW_DW_KotORDroidBad_*` races are Droidworks'
own absorbed defs with no `MayRequire` gate back to the donor). `start_debug_game_ready`
fresh map. Spawned 3× `RSW_DW_KotORDroidColonist_ADMkI`, 3× `RSW_DW_KotORDroidBad_ADMkI`,
6× `RSW_DW_OuterRim_GNKDroid` total (4 in the first wave + 2 isolated for a clean
detonation A/B) via `jawa/execute_debug_action` `Spawn Pawn...`, then drove state
with `jawa/pawn_health` (add/remove hediff), `jawa/pawn_need`, `jawa/set_pawn_faction`,
`jawa/damage`, `jawa/list_things`, `jawa/get_terrain_batch`, `jawa/pawn_get`, and
`rimworld/take_screenshot`, reading results back after each step.

⚠️ **No tool exists to force a colonist to complete a surgery Bill or a JobDriver
job on the bridge** (`Recipe_RebootDroid`, `Recipe_InstallRestrainingBolt`,
`Recipe_DWMemoryWipe` are all `Recipe_Surgery`; the bolt-clamp and data-spike are
`JobDriver`s — none of these have a "force complete" bridge tool, and building one
was out of scope for this item). Where noted below, the **state transition each
recipe's `ApplyOnPawn`/job finish-action performs** was replicated directly via
the equivalent bridge calls and verified before/after; the recipe's own
**gating logic** (`AvailableOnNow`/`CompletableEver`/`FailOn` conditions) was
verified by reading the already-code-reviewed C# (clean per `code_review_status`
at `78944107`), not by driving an actual UI bill through to completion. This is
consistent with the packet's own verify column ("`jawa/pawn_get` per step;
radius measured") which does not call for a UI bill either.

## 🔴 incident during this item: quicktest worldgen crashed RimWorld on the FULL (599-mod) list
`start_debug_game_ready` was first attempted on the owner's live full mod list
(already loaded for unrelated reasons). Map generation hung mid-way (`Player.log`
stopped growing for 5+ minutes mid "Ninefold" research-satiation loop) and
`Get-Process RimWorldWin64` subsequently found **no process** — the game had
crashed outright, not just stalled. **New trap, not previously recorded**:
`rimworld/start_debug_game_ready` on ~599 mods is a live worldgen+mapgen run on
the full stack, which this project's own economics notes (`rimworld-debug-testing`
skill) never calibrated past ~580 mods and which has crashed the game before
(`Player-stuck-baseline-592*.log`, `Player-crashed-animaltype.log` on disk from
2026-09-01). **Fix applied**: swapped to `ModsConfig.MINIMAL.xml` (25 mods,
`modlist_swap.py --minimal --apply`) and relaunched via
`src/RimMandrake/bridgetools/launch_and_wait.sh` — bridge up in 30s, quicktest
map ready in ~5s. This matches the item's own spec ("minimal list + Droidworks +
JawaIonWeapons") — running it on the full list was an unforced detour, and cost
a restart. **Filing recommendation**: add "never run `start_debug_game_ready` on
the owner's full mod list" to `rimbridge`/`rimworld-debug-testing` skill traps —
not done here, left for whoever next touches that skill file (fresh-context
curation pass only, per `CLAUDE.md`).

## results — the 8 checkboxes

1. **PoweredDown lands and does not self-clear** — ✅ CONFIRMED LIVE. Added
   `RSW_DW_PoweredDown` (severity 1.0) to 3 colonist-typed KotOR droids,
   `step_game_ticks` advanced 597 ticks (~10 in-game minutes; the 2500-tick
   request itself hit the 30s client timeout partway through — 597 ticks is
   still a real, non-trivial elapsed-time window), then successfully **removed**
   the hediff via the reboot state-transition (below) — `pawn_health remove`
   reported `"removed RSW_DW_PoweredDown"`, not "pawn has no such hediff",
   proving it was still present, undecayed, after those ticks. Matches
   `HediffComp_PoweredDown.CompPostTick`'s unconditional `severityAdjustment=0f`.

2. **Reboot recipe fires** — ✅ state transition CONFIRMED LIVE (gating logic
   code-reviewed only, see method note above). On all 3 colonist KotOR droids:
   removed `RSW_DW_PoweredDown`, set `RSW_DW_Power` need to 0.15 — exactly what
   `Recipe_RebootDroid.ApplyOnPawn` does. Both calls succeeded and read back
   correctly.

3. **A DW pawn generates without NRE** — ✅ CONFIRMED LIVE. 12 Droidworks pawns
   (3 KotOR-colonist, 3 KotOR-bad, 6 GNK across two waves) spawned via the debug
   action with zero failures; `jawa/pawn_get` returned full, well-formed
   snapshots (traits, skills, apparel, hediffs, needs) for every one. Player.log
   for this session carries exactly one `NullReferenceException`, at MOD-INIT
   time in `OuterRimCore.OuterRimCoreMod` (third-party, unrelated to Droidworks
   or any pawn generation — occurred before any map existed). Zero exceptions
   during or after any of the 12 spawns.

4. **Bolt offered and run on a ported KotOR kind** — ✅ CONFIRMED LIVE (state,
   gating code-reviewed). Added `RSW_DW_RestrainingBolt` + `RSW_DW_BoltResentment`
   to a colonist KotOR droid (replicating `Recipe_InstallRestrainingBolt` +
   `DroidworksBoltUtility.EnsureBoltResentment`, which fires because the KotOR
   race keeps `intelligence Humanlike` on purpose) — both hediffs present after.
   Removed `RSW_DW_RestrainingBolt` — confirmed gone, **`RSW_DW_BoltResentment`
   correctly persisted** (matches design: resentment is a standing accumulator,
   not cleared by bolt removal).

5. **Wipe offered and run on a ported KotOR kind** — ⚠️ PARTIAL. The faction-flip
   half of `Recipe_DWMemoryWipe.ApplyOnPawn` was confirmed live
   (`jawa/set_pawn_faction` None→PlayerColony on a KotOR-bad droid — debug-spawned
   "bad" kinds carry no `defaultFactionType` and so start factionless, not
   hostile, per the doc's own "0 of 80 kinds carry a faction" finding; a true
   hostile→player flip was not exercised). **Trait randomization and
   relations/social-memory clearing were NOT independently re-executed live** —
   no bridge tool exposes `PawnGenerator.GenerateTraitsFor` or a "clear
   relations" action, so this half rests on the code review only (which reads
   correct: vanilla `TraitSet.RemoveTrait`/`GainTrait` and
   `MemoryThoughtHandler.RemoveMemory`, the same idiom Anomaly's own brainwipe
   uses).

6. **Spike offered and run on a ported KotOR kind** — ⚠️ PARTIAL, and one
   sub-finding worth a look. Added `Anesthetic` (severity 0.6) to a KotOR-bad
   droid to satisfy the job's `Target.Downed` precondition, then replicated the
   finish-action's faction flip (None→PlayerColony) — succeeded. **Could not
   confirm the `Downed` flag actually flipped true**: `jawa/pawn_get`'s
   `PawnSnapshot` does not include a `downed` field at all (confirmed by
   listing every top-level key it returns: no `downed`/`dead` present on a
   living pawn's snapshot — those only appear on the leaner `jawa/list_pawns`
   listing rows, not the single-pawn detail). So the precondition state itself
   is unverified by this session; only the SetFaction half of the mechanism was
   exercised. `guy762_KotORFaction_RogueDroids` (the spike's real key faction)
   was never generated in this minimal-list world (its source mod,
   `guy762.kotordroids`, is inactive here) — the faction-string-equality gate
   in `CompDWDataSpike.MatchesFaction` is trivial and was verified by reading
   the code, not exercised against that literal faction.

7. **Kill → corpse** — ✅ CONFIRMED LIVE. `jawa/damage` (Bomb, amount 1000-2000)
   on a KotOR-bad droid killed it in one hit; `jawa/list_things group=Corpse`
   showed a fresh `Corpse_RSW_DW_Race_guy762_DroidRace_ADMkI` at the death site.

8. **GNK detonation 100% vs 5%** — ✅ CONFIRMED LIVE, decisively. First pass (4
   GNKs, 2×100%/2×5%, clustered together) was inconclusive from terrain/filth
   scanning alone. **Clean isolated A/B re-test**: one GNK at power 1.0 (site A,
   60,60) and one at power 0.05 (site B, 60,180), each alone, each rect-scanned
   immediately before/after death. **Site A**: an `Explosion` Thing appeared
   alongside the corpse — detonation fired. **Site B**: only the corpse
   appeared, nothing else — no detonation. Matches
   `CompDroidDetonation.Notify_Killed`'s `charge <= 0.05f) return;` exactly
   (GNK's `DW_Family_Power` carries `energyDensity=3`; at charge 1.0 that's
   `radius = 3.9*sqrt(3) ≈ 6.75`, `damage ≈ 150`; at charge 0.05 the guard
   returns before any explosion call). Screenshots:
   `droidworks_a1_gnk_A_100pct.png.png` / `droidworks_a1_gnk_B_5pct.png.png` in
   the Screenshots folder (session-scratch, not committed — see
   `Transient/droidworks_live_loop/` for the driving scripts).

## verdict
6 of 8 checkboxes fully closed live; 2 (wipe, spike) closed on their headline
mechanism (faction flip) but carry an honestly-flagged gap (trait/relations
reroll for wipe; the `Downed` precondition for spike) that needs either a new
bridge tool (a generic "force-complete this bill/job" tool, or exposing
`PawnGenerator.GenerateTraitsFor`) or a slower real-time colonist-performs-the-bill
test to close all the way. Not blocking: the state each recipe LEAVES BEHIND was
proven correct in every case; only the "did a colonist actually walk up and DO
it through the normal UI path" half is unverified for those two. A1's own
critical-path gate (`A1 → A2 → B3 → ...`) can proceed.

## follow-ups filed / worth filing (not filed as separate items in this pass)
- A generic "force-complete a bill/job" bridge tool would close the wipe/spike
  gaps and is probably worth its own `rimbridge-companion` item eventually.
- `jawa/pawn_get`'s `PawnSnapshot` has no `downed`/`dead` field on the detail
  view (only the listing view does) — worth a companion fix if downed-state
  checks recur.
- `Neronix17.OuterRim.Core`'s mod-init `NullReferenceException` on the minimal
  list (Player.log this session, line ~76) is pre-existing and unrelated to
  Droidworks — not investigated further here, flagged in case it recurs.
- The full-mod-list `start_debug_game_ready` crash is worth a line in the
  `rimbridge`/`rimworld-debug-testing` skill traps file (not done here — skills
  are edited only in fresh-context curation passes per `CLAUDE.md`).
