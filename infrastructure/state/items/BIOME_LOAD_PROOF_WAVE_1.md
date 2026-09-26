# BIOME_LOAD_PROOF_WAVE_1 — prove every biome mod loads clean, standalone

## the ruling

Owner, at the bench 2026-09-26, on what PROVEN has to mean here — typed into a
question-card free-text answer, verbatim:

> *"(1) because here PROVEN doesn't mean fully functional, it means PROVEN for donor
> retirement purposes"*

And on where this sits in the order of work:

> *"(3) should go to Foundry ASAP at high priority. Then Bench and I work on (1) as well
> as finishing the Bedazzle passes for each biome"*

⇒ **This item is BENCH's, worked with the owner present.** The three cheap donor
retirements (`THEY_MOD_REPLICATION_1`, `CRYPTOFORGE_HARVEST_RETIRE_1`,
`RUT_SCAVENGEREVENTS_BUILD_1`) run in parallel at FOUNDRY, high priority.

## 🔴 PROVEN is deliberately NARROW here

**PROVEN = the mod loads clean, by itself, on a minimal list.** Its defs resolve, its
biome exists, nothing red in the log. That is all.

⛔ **PROVEN does NOT mean:** the biome plays well · its cast is complete · its art is
final · its mechanics fire · anyone has looked at it. Those belong to the per-biome
**bedazzle sitting** (`<BIOME>_DESIGN_SITTING_1`), which is a different, slower thing
held with the owner.

🔑 **Why the narrow sense is the right one:** the whole point is donor retirement. A
donor mod can only come off the list once our replacement is known to load without it.
That is a load question, not a quality question, and answering the quality question
first would stall every retirement behind 23 design sittings.

## the subjects — 23 biome mods

All 23 `*_RM_MOD_BUILD_1` items exist; **22 are CLOSED on authoring**, and
`LONGSHADE_RM_MOD_BUILD_1` is the one still open (its own steps 3 freeze-twin and
4 retarget are owed and offline; its step 5 *prove it loads* is this wave's work).

BlueDesert · Contagion · FeverWood · FloodedCanyon · ForsakenCrags · GelatinousSlime ·
Greentide · LanternDeeps · LeaningScrub · LongShade · Miasma · NightsideIce ·
PoisonForest · Pyrelands · RustCathedral · Stillsand · TerminalBiomes · TheForge ·
TheRot · TheSump · Wasteland · Webwork · WeepingStones

⚠️ **Not one of them has ever been load-proven.** `BIOME_KITS_PUSH_TO_TEST_1` says so in
its own title — the kits were pushed toward readiness **offline only**. Every one of
those 22 closures was an authoring closure.

## method

Existing tooling, not new tooling:

- `src/RimMandrake/Utils/modset_builder.py` already carries per-subject tiers and
  resolves `<modDependencies>` transitively, so a tier is always complete. It already
  has `leaningscrub`, `slime`, `weepingstones`, `desertplants`, `diving` and others —
  **a biome tier per mod is an addition to an existing pattern, not a new harness.**
- 🔴 **Every tier sets `dlc: True`** (owner ruling 2026-09-19: all test mod lists include
  all five expansions, no exceptions). A tier's `want` may narrow which MODS load; it
  may not narrow which DLC loads.
- `src/RimMandrake/Utils/modlist_swap.py` does the swap and the restore.
- ⛔ **Never `modcheck run <Mod>`** — it calls `modlist_swap` and rewrites the live
  `ModsConfig.xml` to MINIMAL despite reading like a query verb.
- Back up the live `ModsConfig.xml` to `infrastructure/state/modlists/` before the wave
  and restore it at the end.

## pass criteria — write them BEFORE launching

Per the `rimworld-load-round` skill: arrive already confident. For each mod, the
decision is made by named strings in `Player.log`, not by "it looked fine":

- FAIL on any `Could not resolve cross-reference`, `XML error`, `Could not load
  reference to`, or a `PatchOperation` reporting no match, attributable to this mod.
- FAIL if the mod's own BiomeDef is absent from the loaded def set.
- ⚠️ A patch that matches nothing **logs nothing** (`PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match), so silence is not a pass —
  the BiomeDef presence check is what makes a pass positive rather than merely quiet.
- PASS is recorded with `rimflow verify <ID> --result pass --config <tier>`.

## criteria
- [ ] A tier in `modset_builder.py` per biome mod, `dlc: True`, dependency-complete.
- [ ] Live `ModsConfig.xml` backed up to `infrastructure/state/modlists/` first.
- [ ] Each of the 23 loaded standalone; verdict decided by log strings written in
      advance, plus a positive check that its BiomeDef is in the loaded def set.
- [ ] Every result recorded on the ledger — a FAIL is immutable and stands.
- [ ] Live `ModsConfig.xml` restored to the full list at the end of the wave.
- [ ] Failures filed as their own items against the owning biome, not fixed inline.

## what this does NOT do
- It does not paint tiles. The planet is painted ONCE at the end
  (`BIOME_PAINT_ONCE_AT_THE_END_1`), and **a biome of ours carrying 0 tiles is the
  expected mid-migration state** — never a finding, never a reason to act.
- It does not retire any donor mod. It removes the load-risk objection to retiring one;
  the retirement items own the rest.
- It does not judge any biome's content. That is the bedazzle sitting.
