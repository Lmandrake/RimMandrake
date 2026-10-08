# DivingInteraction offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (7.9k lines, 47 files)
Chosen kernels, and why:
1. **Brine Elder novelty economy** (RM_ElderTradeUtility + RM_GameComponent_BrineElders): a per-tile seen-ledger, a world-wide
   "one of each" treasure claim list, silver arithmetic, all Scribed. Dense state across save/load and mod add/remove: live
   chains can reach one trade at a time.
2. **Chill garden defense** (RM_MapComponent_ChillGardenDefense): two score pools, three cooldowns, trail-density discounted
   thresholds, a design promise ("drilling can never wake the Tarnn"). Pure scoring state machine, ideal for sequence fuzz.
Rejected as kernels:
- Layer swap / descent / ship-or-nothing (RM_SeabedLayer, RM_SeabedSiteParent, RM_SeaDiveHatch, PlaceWorker_NeedsGravEngine):
  almost entirely engine calls (PlanetTile, WorldGrid, MapPortal). The only logic is tile arithmetic (tile N <-> tile N) and
  "hatch needs a GravEngine"; pawn/ship accounting during the swap is the ENGINE's, this mod holds no pawn list or counter, so
  there is nothing to extract and an invariant would test a mock. Stays with the live chains (validation.py).
- Heated suit battery, Scald vent forecast (phase 0/1/2), aurora surge hysteresis: pure-able and next in line (small), not done.

## 2. Kernels + fuzz
Extracted (behaviour preserving, call sites call the kernels, Scribe names unchanged):
- `src/RimMandrake/DivingInteraction/Source/RM_GardenDefenseKernel.cs` (enum RM_GardenOffenseKind moved here, same type name):
  State struct + Offense() + Agitation(); component copies its 5 Scribed fields in/out and plays the returned Outcome.
- `src/RimMandrake/DivingInteraction/Source/RM_ElderEconomyKernel.cs`: HasSeen/MarkSeen/TryClaim/ChooseTreasure/SilverFor/Decide;
  RM_ElderTileRecord implements IElderTileRecord, GameComponent + Offer() call it.
Two real defects found by the extraction and now guarded by the fuzz (both FIXED in the kernel, small behaviour change):
- **Burned treasure**: the old code claimed a unique treasure (written to the save's granted list) BEFORE looking up the def; if
  the def does not resolve (a Utinni-patch-added treasure with its mod absent) the claim is burned for the world, nothing is
  paid as treasure. Now only resolvable candidates are chosen.
- **Silver overflow**: `RoundToInt(value*8)` for value*8 > 2^31 yields int.MinValue, so the huge trade paid the 50 floor
  instead of a fortune (also non-monotone payouts). Now saturates at `MaxSilver` (1,000,000).
Fuzz: `src/RimMandrake/DivingInteraction/Source/SelfTest/{DivingFuzz.cs,Program.cs,RimMandrakeDiving.SelfTest.csproj}`,
wrapper `src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py` (families garden | elder | units; knobs --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- garden: fires exactly when score and cooldown say so (oracle on floats); firing zeroes score and arms the tier-1 cooldown;
  arcs never closer than 2500 ticks to the last arc or wake; wakes never closer than 60000; agitation arcs >= 2500 apart;
  an offense never touches the drill pool, drilling never touches the offense pool or tier cooldowns (cannot wake Tarnn);
  scores >= 0 and finite; cooldowns never move backwards; Scribe text round trip of scores is exact.
- elder: novel <=> tile>=0 and not seen; a tile-less offer writes nothing; a stale offer never gets a treasure; the ledger equals
  an independent reference across save/load deep copies; no duplicate tile/key; each treasure delivered at most once, only if
  its def resolves, and granted list == delivered set (nothing burned); treasure => silver 0; silver within floor..cap and equal
  to an independent rounding; pick/roll only consumed on a novel winning roll; payout monotone in value over 1e-2..1e12.
- units: threshold falls with trail density and stays > 0 at density 1; Drill kind weight 0; design numbers (8 harvests to Tier1,
  one kill or one heat hit arcs).
Seeds: 8,302 cases / 794k steps at default scale in 1.3 s; `--fuzz-scale 25`: 207,502 cases / 19.85M steps in 20 s, all green.
Mutation (each planted, caught, reverted; file compared byte-identical afterwards):
- M1 claim without resolvable check (the original bug): elder FAIL seed 1 "treasure ... claimed although its def cannot be made".
- M2 unsaturated int cast (the original bug): elder FAIL "silver 14000000 above the cap" + units "silver fell from 2009509120 to 50".
- M3 wake does not arm tier-1 cooldown: garden FAIL on 5 seeds, shrunk to 4-5 actions.
- M4 agitation ignores its cooldown: garden FAIL "agitation arc fired but score 3 ..." shrunk to 6-7 actions.
Trap: the wrapper stages with rsync `--modify-window=2`; after editing a kernel and re-running within ~2 s a stale staged copy
can be built. Wait a few seconds between a mutation and its run.

## 3. Lint
`src/RimMandrake/Utils/selftest_divinginteraction_lint.py` (named selftest*, so run_selftests.py runs it): 36 XML class refs
resolve to public classes; 28 XML field children are public fields of their extension/comp class; 47 .cs files == csproj Compile
list (a missing <Compile> compiles into nothing); 122 RM_/RUT_/RSW_ string literals resolve to a defName or `<li>` tag under src/
or a translation key; 34 Translate() calls have Keyed entries; kernel State fields match the Scribe names. Count 0 on any check
fails the run. Mutation: misspelling `floorBiome` in Patches/RM_SeabedFloorBiomeWiring.xml was caught, file restored. One initial
false positive (terrain tag RM_GreyBrinePool lives in TerminalBiomes as a `<li>`) fixed by accepting tags.

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/DivingInteraction/Source/RM_DivingInteraction.csproj`: 0 warnings, 0 errors,
two `<Compile Include>` lines added. DLL + .srchash rewritten in the working tree, NOT committed (source stamp is +dirty until
the source is committed and the DLL rebuilt).

## Run
- `python3 src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py [--fuzz-scale 25] [--fuzz-seed N] [--fuzz-only garden|elder|units]`
- `python3 src/RimMandrake/Utils/selftest_divinginteraction_lint.py`
