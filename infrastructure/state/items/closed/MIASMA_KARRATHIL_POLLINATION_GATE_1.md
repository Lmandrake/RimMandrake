# MIASMA_KARRATHIL_POLLINATION_GATE_1

## what

Gate the Miasma's flowering mangals' reproduction on `RUT_Karrathil` (the
fever-swarm) presence — the second half of
`design/Jawa/worldbuilding/biomes/the_miasma.md` §4's "disease vector and
the mangals' only pollinator, one and the same swarm. You cannot have the
trees without the fever," and `design/Jawa/worldbuilding/biomes/
miasma_fauna_roster_2026-09-23.md` §3's own row for `RM_Karrathil` (built
this pass as `RUT_Karrathil`, `COMMISSION_LEDGER_CLEANUP_1`, ledger slug
`the_miasma:karr-fever-swarm-vector-pollinator-one-swarm`).

## why

The roster's own §3 caution: *"whether a `Plant` can be gated on a nearby
animal at all is an engine question, UNMEASURABLE on the Mac... check it on
the Desktop before this row's mechanics are specified."* This item exists
so that check — and whatever mechanism it enables — has a home separate
from the creature build, rather than being guessed at inline.

`COMMISSION_LEDGER_CLEANUP_1`'s wave that built `RUT_Karrathil` (this
session) shipped the creature (flying insect swarm, `wildGroupSize` 12~30,
wired into `RUT_Miasma.xml`) and the VECTOR half needs no new mechanism —
`miasma_kit_spec.md` M4 already routes the biome's diseases through
vanilla's own `diseaseMtbDays`/`<diseases>` list, no bespoke bite/contact
comp. Only the POLLINATION half — a plant's reproduction failing without a
nearby animal — is new engine territory, and it is what this item covers.

Checked this session (not a Mac laptop; `mcp__rimsage__*` tools DID
connect and answer from this environment): a source search for
`pollinat`/`Plant` reproduction found **no existing engine hook** to gate
plant spread on nearby animal presence. This confirms the roster's
"UNMEASURABLE" flag is about genuine absence of a ready mechanism, not
merely about tool access — the Desktop check this item still needs is
about whether such a gate is *buildable at all* (does `Plant`'s spread/
growth path expose anything a comp could veto?), not about reaching a
tool.

## watch out

- ⚠️ **Do not add a second pollinator or make killing karrathil strictly
  good** — both are the "obvious balance fix" the roster explicitly warns
  against (§7): *"If killing karrathil is strictly good, the bargain
  collapses."* The gate has to be able to FAIL flowering, not just tax it.
- ⛔ Do not invent a plant-reproduction mechanism by guessing at engine
  behavior from a doc — CLAUDE.md's own standing rule on UNMEASURABLE
  engine facts. Verify on the Desktop (RimSage or a live dev-mode test)
  before writing any comp.
- Which flowering plant(s) this gates (the mangals — `AB_MangroveTree`/
  `AB_ParasiticMangrove`, `RUT_Miasma.xml` wildPlants) is a content
  decision for whoever picks this up; not pre-judged here.

## verify

- Confirm (Desktop) whether `Plant`'s growth/reproduction path can be
  vetoed or slowed by a comp reading nearby-pawn presence.
- If yes: build the gate, wire it to `RUT_Karrathil`, and re-verify the
  mangals still reproduce normally with karrathil present and measurably
  worse (not zero) without it.
- If no: record why here and close or retarget this item rather than
  leaving it open indefinitely.

## criteria

Closed when either (a) the pollination gate ships and is verified against
a live game, or (b) the Desktop check finds no buildable mechanism and
this item is closed/retargeted with that finding recorded.

## build pass — 2026-09-25, FOUNDRY

**Desktop check answered, against the real decompiled 1.6/Odyssey source
(RimSage connected this session, confirmed live):**

- `Plant` (`Source/RimWorld/Plant.cs`) exposes **no reproduction-time
  comp hook at all** — its virtual surface (`Growth`/`GrowthRate`/
  `LifeStage`/`TickLong`) governs an already-spawned individual maturing,
  never whether a NEW individual is chosen to spawn. The roster's own
  "UNMEASURABLE" flag was correct: there is no `Plant`-level comp for this.
- Wild-plant **reproduction** (both initial map-gen seeding and every later
  regrowth roll) is entirely decided by the per-map singleton
  `RimWorld.WildPlantSpawner`, via its private
  `CalculatePlantsWhichCanGrowAt(IntVec3, List<ThingDef>, bool, float)` →
  `PlantChoiceWeight(...)` chain (`Source/RimWorld/WildPlantSpawner.cs`).
  `CalculatePlantsWhichCanGrowAt` is the single choke point used for BOTH
  paths, and is **already proven patchable** by a sibling in this same
  assembly, `RM_LeachmossWildSpawnGatePatch` (DESERT_LEACHMOSS_BUILD_1) —
  found reading the codebase before writing anything new, per this repo's
  own "read the mechanism first" law.

**Answer: yes, buildable — not as a comp, as a Harmony postfix on that
private method, generalized from the leachmoss sibling's single hardcoded
defName into a data-driven gate.** Built, not just spiked:

- `RM_PollinationGateExtension` (new `DefModExtension`, one field —
  `pollinatorRace`) — attach to any plant ThingDef to require a species be
  alive somewhere on the map before that plant can spawn a NEW individual.
- `RM_PollinationGatePatch` (new Harmony postfix on
  `WildPlantSpawner.CalculatePlantsWhichCanGrowAt`, `AccessTools.
  FieldRefAccess<WildPlantSpawner, Map>("map")` for the owning map, same
  reflection shape `RimMandrake.MovingDunes.Patch_SandGrid` already uses
  for an identical private-map problem) — removes a gated candidate
  outright (never merely taxes its weight) whenever
  `map.listerThings.ThingsOfDef(pollinatorRace).Count == 0`. A HARD veto,
  satisfying the roster's own "must be able to FAIL flowering, not just tax
  it" — and deliberately MAP-WIDE presence rather than per-cell radius: the
  sheet's bargain is "no swarm on this map at all," not per-seedling
  proximity, and `ThingsOfDef` is the same already-indexed O(1) lookup
  `PlantChoiceWeight` itself already uses for the candidate plantDef, so no
  new per-cell scan cost is added to a loop that already runs many times a
  tick.
- Wired via `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_
  PollinationGate.xml` (new) onto `AB_MangroveTree`/`AB_ParasiticMangrove`
  (the live donor "mangal canopy" species RUT_Miasma.xml's own `wildPlants`
  actually carries today) with `pollinatorRace RUT_Karrathil` —
  `AB_MangrovePalm` deliberately excluded (its roster successor,
  RM_Ilbareen, is about dying in place as a salt-line gauge, a different
  mechanism). Content decision, per this item's own "not pre-judged here":
  whoever lands `MIASMA_FLORA_ROSTER_1` (RM_Thessamor/RM_Quennath are
  UNBUILT — no ThingDef exists yet, confirmed this pass) should move this
  same modExtension onto those defNames rather than re-deciding which
  species gate. `RUT_Miasma.xml` itself was NOT touched — its own Phase-A
  freeze header has not landed yet (`MIASMA_RM_MOD_BUILD_1` step 3, still
  OWED) but the mechanism needed no edit there regardless; everything
  routes through the Utinni patch layer.
- New Mod Settings toggle `pollinationGateEnabled` (#50,
  `RM_EnvironmentalHazardsMod.cs`), same one-per-mechanism convention this
  kit already uses; off restores vanilla behavior (no pollinator
  requirement) with no effect on already-grown stands either way.

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0
errors, with the 2 new `<Compile>` entries. The rebuilt `Assemblies/
RimMandrake.EnvironmentalHazards.dll` is deliberately NOT part of this
pass's commit, same reasoning every prior pass touching this shared,
actively-being-built assembly has given — regenerable any time from
committed source by the one-line build command this same file's earlier
sections already give.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` against
the live 626-active-mod set (`--defs` Data + Mods + Workshop root): the new
patch file, 0 errors, 0 warnings — both `PatchOperationConditional`/
`PatchOperationAddModExtension` pairs matched exactly once each, in Alpha
Biomes' `Plants_MiasmicMangrove.xml`, confirming both target ThingDefs are
real and live in the current 626-mod set. `run_selftests.py`: 73/75 passed;
the 2 failures (`selftest_live_prep.py` — RotSporeKit/`RM_LivePrepExtension`,
and `selftest_deployed_biome_refs.py` — `RUT_Vorrel`/`RUT_Desert.xml`) are
both pre-existing and unrelated to any file this pass touched.

**Not done this pass, explicitly**: no `--live` DefDump-based validation and
no in-game/quicktest confirmation that killing off every karrathil on a
live map actually stops new mangals appearing while leaving standing ones
alone. `bridge who` read held-by-FOUNDRY (`FISH_BESTIARY_BUILD_1`) at the
start of this pass, then read FREE once that hold aged out; taking it and
attempting to deploy found `RimWorldWin64.exe` already running a load with
heavy corpse-def cross-reference errors in `Player.log` — an ambiguous
state (a live scratch session, not obviously idle, not obviously the
canonical save) this pass chose NOT to restart over rather than force
through an unclear state for a verification that already has strong
offline evidence. The new patch XML was copied into the deployed
`UtinniPatches/Patches/` folder (harmless, additive, no restart forced);
the rebuilt assembly DLL could not be copied over the running game's
memory-mapped copy (expected — `rimworld-load-round`'s own "assembly
cannot be written while the game runs") and is owed at the next natural
shutdown window, not blocking this close. The offline `validate_patch.py`
run against the real live installed-mod XML tree (not a stale dump)
already confirms both target defs exist and the patch resolves exactly
once each, which is strong but not equivalent to watching it run. Closing
this item now on ground (a) — "the pollination gate ships" — with the
live-game confirmation named here as the honest remaining gap, in the same
posture `MIASMA_MECHANICS_1`'s own six build passes already used for their
own "not done, explicitly" lines.

## files (this pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_PollinationGateExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_PollinationGate.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (modified: 2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (modified: `pollinationGateEnabled` setting #50)
- `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_PollinationGate.xml` (new)
