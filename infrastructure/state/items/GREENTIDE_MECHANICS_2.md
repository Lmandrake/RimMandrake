# GREENTIDE_MECHANICS_2 — the Greentide C# kit build

Successor to `GREENTIDE_MECHANICS_1` (filed 2026-09-07, closed 2026-09-11 at
`0167e7af` — spec-drafting only, no build). That ID is permanently closed
(append-only ledger — `rimflow why GREENTIDE_MECHANICS_1` confirms it will
never be offered again), so this item carries the kit's build/spike work
under a new ID rather than reopening it. `caused_by: GREENTIDE_MECHANICS_1`
on the filing event, and a note left on that item pointing here.

## spec

Per `design/Jawa/worldbuilding/biomes/the_greentide.md` (FROZEN, §4b, §4c,
§5, §7b, §8b): wet-bulb overwhelm + the gear tree · the dry-air blower ·
Scald damage + steam devils · the Roil (standing ground-fog) + Breaklight ·
three-feller tree fall · Lunger ambush · churnmud (swallow + mire) · root
causeways · grazing suppresses encroachment · the silence cue · the
Greatbole (mineable living tower).

**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/greentide_kit_spec.md` (2026-09-11)
— 12 mechanics (M1-M12), 4 ruled-comp reuses from `ALPHA_MECHANICS_KIT_1`,
9 new RM_ classes (1 L, 6 M, 2 S), hard-ban-adjacent owner rulings (churnmud
no-exemption, sealant recipe, no deferrals), build order, "Greentide is its
own RimMandrake-tier mod" ruling (→ `GREENTIDE_STANDALONE_MOD_1`).

**🔴 Load-bearing finding this pass: most of the kit isn't "unbuilt" — it's
scattered across two OTHER items that already closed, and the spec itself
hadn't caught up.** Before any spike work, this pass read every existing
def/class under the names the spec calls for and found:

- `GREENTIDE_STANDALONE_MOD_1` (closed 2026-09-11, sha `c71fb0fbf`,
  bridge-verified) already shipped, in `src/RimMandrake/Greentide/`
  (`mandrake.rm.greentide`) and the shared
  `src/RimMandrake/CreatureBehaviors/` assembly:
  - **M8 (churnmud: mire + swallow) — in full.**
    `RM_MapComponent_TerrainMire`/`RM_JobDriver_FreeMired`/
    `RM_WorkGiver_FreeMired` (mire) and `RM_MapComponent_MudSwallow`/
    `RM_JobDriver_DigOutBuried`/`RM_WorkGiver_DigOutBuried` (swallow, in the
    spec's own "minimal form": bury + dig, no decay while buried). Owner
    ruling (no stockpile exemption) enforced structurally.
  - **M11 (silence cue) — in full**, as `RM_MapComponent_SilenceCue` +
    `RM_SilenceAuraExtension`, shared `mandrake.rm.creaturebehaviors`.
  - **M5's seek-shade AI half** — `RM_JobGiver_SeekShade` +
    `RM_SeekShadeExtension`, same shared assembly, wired live onto
    Muffalo/Warg.
- `FORGE_MECHANICS_1`'s own F1 build pass (2026-09-13, today, earlier) shipped
  **M3's damage-type trio** (`RUT_Scald` DamageDef, `RM_ScaldArmor`
  DamageArmorCategoryDef, `RM_ArmorRating_Scald` StatDef) under its own
  spec's explicit cross-kit-reuse contingency ("if the greentide build
  slips, the def is XML and ships here first" — it slipped: this item
  wasn't even filed until today).

Both are reconciled in `greentide_kit_spec.md` itself this pass (see "files"
below) — each section now points at the real shipped location instead of
describing the mechanic as if unbuilt, and states plainly not to re-ship.

**What is genuinely still unbuilt, confirmed by grep (zero hits in `src/`)
and by the shipped mod's own About.xml, which already lists its own gaps**:
M1 (wet-bulb + gear), M2 (dry-air blower), M3's steam devil vortex, M4 (Roil
weather — mechanically; a compiling overlay class ships this pass, see
below), M5's Breaklight weather/light-snap half, M6 (tree fall), M7
(Lunger), M9 (root causeways), M10 (grazing suppression hook — blocked on
`EXPLOSIVE_PLANT_GROWTH_1`, still unfiled-to-build in `queue/BENCH.md`),
M12 (Greatbole).

## verify

- [x] Every ❓ engine claim the kit spec still carries (after the M3/M8/M11
      reconciliation removed the ones already settled by shipped code) is
      re-checked against the real 1.6/Odyssey decompile — **2026-09-13,
      6 resolved this pass, see "spike pass" below.**
- [ ] Build lands per the spec's build order, after `ALPHA_MECHANICS_KIT_1`
      (closed). **Not done this pass** — one compiling proof class (M4's
      overlay) shipped; the remaining ~9 mechanics are later, separate
      FOUNDRY work, same posture as every sibling kit's own spike pass.
- [ ] A quicktest map in the biome shows the remaining mechanics live.
      **Not done this pass** — no bridge/game access in this task, same as
      every sibling spike.

## spike pass — 2026-09-13, run per SCALD_MECHANICS_1's/MIASMA_MECHANICS_1's
own methodology

Sizing followed those items' own line: prove each risky/uncertain piece
minimally, offline, against real engine source, not the full 10-mechanic
remaining build. Decompile used throughout:
`/mnt/d/Luke/dev/reference/rimworld-decompiled` (confirmed 1.6/Odyssey by
the presence of Gravship-only classes, per MIASMA's own check).

### Engine ground-truth: 6 named claims resolved against the real decompile

1. **M2's "wild-animal avoid grid" — CONFIRMED ABSENT.**
   `Verse.AI/AvoidGrid.cs` read in full: built exclusively from
   `map.listerBuildings.allBuildingsColonist` + `ai_combatDangerous`
   turrets, then edifice-expanded — colonist-pathing/combat-danger only, no
   wild-fauna route. The spec's own fallback (periodic scan + flee hediff)
   is confirmed the only route.
2. **M6's "no falling-tree machinery" — re-verified against the REAL 1.6
   decompile (the spec's own citation was only the 1.5-era RimSage index).
   CONFIRMED ABSENT still.** Zero hits for `FallingTree|TreeFall`; only
   `MinifiedTree`/`Alert_MinifiedTreeAboutToDie` exist. `RM_TreeFallUtility`
   must be built from scratch exactly as assumed.
3. **M8's "rescue/carry crib" for the mire pull-free job — CONFIRMED the
   vanilla shape doesn't fit (moot for future work, since M8 already
   shipped custom, but recorded for the record).** `JobDefOf.Rescue` →
   `JobDriver_TakeToBed` (`RimWorld/WorkGiver_RescueDowned.cs`) is
   bed-reservation-specific, wrong shape for "free an adjacent pawn in
   place." The shipped `RM_JobDriver_FreeMired` built fresh — verified
   correct, not a missed crib.
4. **M8's "terrain-hazard hooks in 1.6" — CONFIRMED PRESENT, but wrong
   shape for mire (also moot for future work, same reason).**
   `Verse/HediffGiver_Terrain.cs` is real (`burnDamage`/`ignitePawnsIntervalTicks`
   off `TerrainDef`) but it's a `HediffGiver` — fires only for a pawn
   already carrying a qualifying Hediff, not an ambient per-pawn scan, and
   `TerrainDef` has no slow/immobilize field. The shipped
   `RM_MapComponent_TerrainMire`'s own interval scan (not hediff-gated) is
   confirmed the correct route.
5. **M10's grazing choke-point — CONFIRMED, resolves the spec's own named
   ❓.** `Plant.IngestedCalculateAmounts(Pawn ingester, float
   nutritionWanted, out int numTaken, out float nutritionIngested)`
   (`RimWorld/Plant.cs:603`, `protected override`) is the single seam every
   plant-eating pawn (grazer or player) passes through via the base
   `Thing.Ingested`. A Harmony postfix there is the entire mechanism — not
   built this pass (see "owed" below: the grid it must write into,
   `EXPLOSIVE_PLANT_GROWTH_1`, doesn't exist yet).
6. **M11's Sustainer-duck route — CONFIRMED a live volume-ramp route DOES
   exist** (better than what's shipped, though not a defect — see below).
   `Sustainer.externalParams` (`Verse.Sound/Sustainer.cs:22`) feeds every
   `SubSustainer`/sample update, and `SoundParamTarget_Volume`
   (`Verse.Sound/SoundParamTarget_Volume.cs`) maps a named external
   parameter onto sample volume when the target `SoundDef`'s subSounds
   declare a matching `paramTargets` entry. Live instances are reachable
   via `Find.SoundRoot.sustainerManager.AllSustainers` (public) — the
   shipped `RM_MapComponent_SilenceCue` already walks this exact list, just
   to call `.End()` rather than duck. Not reworked this pass: the shipped
   end-and-respawn is a real, owner-accepted v1 trade already live: reworking
   a working mechanic on an unrequested refinement is out of scope. Flagged
   in the kit spec as a future improvement, not a defect.
7. **M12's "large-graphic draw route" — RESOLVED: plain `drawSize`, no
   skyfaller overlay needed.** `GraphicData.drawSize`
   (`Verse/GraphicData.cs:29`) is independent of a `ThingDef`'s collision
   `size` — the standard vanilla route for any larger-than-footprint
   sprite. `Skyfaller` machinery (`RimWorld/Skyfaller.cs`) is
   time-of-flight-driven for descending/ascending things — read and
   confirmed the wrong fit for a static structure.

(Numbered 7 for the finding count; M8's two items (3,4) are moot-but-recorded
since that mechanic already shipped before this spike ran.)

### Built this pass (compiling proof)

- **`RM_WeatherOverlay_GreentideRoil : WeatherOverlayDualPanner`** (M4) —
  in `src/RimMandrake/Greentide/Source/` (`mandrake.rm.greentide`), NOT
  `src/RimMandrake/EnvironmentalHazards/` as the spec's stale text said.
  Correction found and recorded: the spec names a shared
  `RM_WeatherOverlay_GroundFog` class as if it already existed
  *(verified, greentide)* — checked this pass, it doesn't, and
  `SCALD_MECHANICS_1`'s own spike (2026-09-13, same repo) already proved a
  shared class is impossible (`WeatherOverlay_Fog`'s Material is hardcoded
  per-subclass in vanilla itself; `WeatherDef.overlayClasses` carries no
  per-instance texture config). Built Greentide's own one-off instead, in
  Greentide's own standalone mod — matching the real precedent
  `GREENTIDE_STANDALONE_MOD_1` already set for every other Greentide-specific
  class (they all live in `src/RimMandrake/Greentide/Source/`, not the
  shared EnvironmentalHazards home the spec's original placement plan
  named, which predates the owner's later own-mod ruling). Texture not
  shipped (owed to art, `MatLoader.LoadMat` degrades to a placeholder on a
  missing texture rather than throwing — does not block build/load).

### Not built this pass, explicitly

M1 (wet-bulb + gear, M-effort), M2 (dry-air blower, M-effort), M3's steam
devil vortex (M-effort — the damage-type half is done, see reconciliation),
M4's mechanical half (`RUT_RoilWeather` WeatherDef fields, the
`EnvironmentalWeather` condition lock — XML/reuse, low-risk, left for the
full build), M5's Breaklight weather/light-snap half (M6's seek-shade is
done), M6 (tree fall, M-effort — 3 fellers + utility), M7 (Lunger,
M-effort), M9 (root causeways, M-effort — also sites M12's boles, strict
order per the spec's own build order), M10's actual postfix (blocked on
`EXPLOSIVE_PLANT_GROWTH_1` not existing), M12 (Greatbole, L-effort,
deliberately out of spike scope per every sibling item's own precedent).
All are later, separate FOUNDRY build-pass work.

## verdict

7 named engine claims resolved with file:line citations against the real
1.6/Odyssey decompile — none left a guess standing (2 were moot-but-recorded
since the mechanic they'd have informed already shipped before this spike
ran). One compiling C# proof landed (M4's overlay), 0 warnings/0 errors. The
dominant finding this pass wasn't a new ❓ at all: it was that the kit's own
spec had gone stale against two OTHER items' closes
(`GREENTIDE_STANDALONE_MOD_1`, `FORGE_MECHANICS_1`) that had already shipped
roughly a third of the kit's v1 mechanic count (M3's damage half, M5's
seek-shade half, M8 in full, M11 in full) under different names, and was
still describing that work as unbuilt ❓s to resolve. `greentide_kit_spec.md`
is corrected at every one of those sections (M3, M4, M5, M8, M10, M11, M12,
plus M2's/M6's ❓ resolutions) so the next reader doesn't redo shipped work.
Remaining ~7 mechanics (M1, M2, M3-vortex, M4-mechanical, M5-weather, M6,
M7, M9, M10-postfix, M12) are honestly owed to later build passes — item
stays in `doing`.

## files

- `src/RimMandrake/Greentide/Source/RM_WeatherOverlay_GreentideRoil.cs` (new)
- `src/RimMandrake/Greentide/Source/RM_Greentide.csproj` (1 new `<Compile>` entry)
- `src/RimMandrake/Greentide/Assemblies/RimMandrake.Greentide.dll` (rebuilt, 0 warnings/errors)
- `design/Jawa/worldbuilding/biomes/kits/greentide_kit_spec.md` (M2/M3/M4/M5/M6/M8/M10/M11/M12 sections reconciled/resolved)

## M1/M2 build pass — 2026-09-14

Full build of M1 (wet-bulb overwhelm + the gear tree) and M2 (the dry-air
blower), per the kit spec's own build order (item 3, "one unit"). Built in
`src/RimMandrake/EnvironmentalHazards/` (the RM_ mechanism classes, per the
roster table's own "ruled kit's home" placement) and
`src/RimUtinni/UtinniPatches/` (the RUT_ content defs, matching the exact
precedent `RUT_ScaldSteamLock`/`RUT_Scald` already set for M3's damage
trio — mechanism in EnvironmentalHazards, content in UtinniPatches, wired
onto the frozen campaign biome `RUT_Greentide` via a MayRequire-gated
patch, never a direct BiomeDef edit).

## M9/M12 build pass — 2026-09-14

High-leverage build, run concurrently with the M1/M2 pass above in a
second window against the same shared `RM_EnvironmentalHazards.csproj` (no
file collision hit — see "concurrency" below) — `FEVER_WOOD_MECHANICS_1`'s
own item file names `RM_GenStep_RootCauseways` (M9) and
`RM_MapComponent_LivingRegrowth` (M12's core class) as the exact two
classes blocking its own F6/F7, so landing these unblocks a sibling kit,
not just this one.

Both mechanics built generic RM_-tier in
`src/RimMandrake/EnvironmentalHazards/Source/` (the shared kit home,
matching every other cross-kit-reused class in this assembly — F1-F9's own
RUT_ classes already live there too), gated onto biomes via two new
`DefModExtension`s (`RM_LivingBoleBiomeExtension`, `RM_RootCausewayBiomeExtension`)
following `RM_GradientAxisExtension`'s exact idiom: a no-op on any biome
that doesn't carry the extension, so registering both GenStepDefs globally
onto `Base_Player` (same pattern `RUT_Miasma_GradientAxis_Register.xml`
already set) is safe for every other biome too.

**M12 (the Greatbole).** `RUT_GreatboleHeartwood` (mineable ThingDef,
`ParentName="RockBase"`, `mineable=true`/`building.mineableThing=RUT_Hardwood`
— both fields the spike pass's own spike-7 already verified) spawns as a
blob via `RM_GenStep_LivingBoles`, which also paints `RoofDefOf.RoofRockThick`
over the whole footprint (the "natural-roof patch") and spawns
`RUT_GreatboleCore` (the marker, carrying the oversized `drawSize` the kit
spec's own RESOLVED ❓ calls for — no separate "Crown" defName; see that
def's own header) at the blob's center cell. `RUT_GreatboleCore`'s
`RM_CompLivingBoleMarker` flood-fills its own footprint from the heartwood
blob around it on first spawn and registers with
`RM_MapComponent_LivingRegrowth` — the reusable core loop: every
`TickInterval` (250 ticks, INVENTED), each registered bole's footprint is
scanned for empty/enclosed(roofed)/unsealed cells, which schedule a
regrow timer (3-6 days, INVENTED); landing on an occupied cell fires a
creak warning (message + sound, ~1 in-game hour ahead, per spec) then
periodic Blunt crush-and-eject (pawns pushed to the nearest open cell
outside the bole's own footprint, items destroyed, buildings damaged then
destroyed) until clear, then the tree regrows there. Sealing a cell at ANY
point (an ordinary construction job painting `RUT_ToxinSealant`) cancels
its timer outright, checked every pass, not just at schedule time — a real
bug found and fixed during this pass's own self-review (see "self-review
findings" below).

🔴 **Load-bearing correction found this pass, against the kit spec's own
"owed to the items pass" framing (card 2):** the sealant item and its
recipe chain are NOT owed — `RM_ToxinSealant`/`RM_SapResin` already shipped
in `src/RimMandrake/Greentide/Defs/ThingDefs/RM_Greentide_Items.xml`
(`GREENTIDE_STANDALONE_MOD_1`'s own M12 sealant half, that file's own
header: "owner ruling confirmed 2026-09-11: crafted from sap/resin; the
economic link is canon") and already seals M8's `RM_ChurnmudSealed`. This
pass's own `RUT_ToxinSealant` TerrainDef (the chamber-floor sealant, a
different def from the item of the same theme) simply consumes the
existing `RM_ToxinSealant` item via `costList`, same as `RM_ChurnmudSealed`
already does — no new economy invented. Same stale-spec pattern this
item's own spike pass already found three times over (M3/M5/M8/M11); kit
spec's M12 section corrected this pass to point at the real shipped item
instead of repeating "owed to items pass."

**M9 (root causeways).** `RM_GenStep_RootCauseways`, registered at
GenStepDef `order` 228 (after `RM_GenStep_LivingBoles`'s own 222, both
after vanilla `GenStep_Terrain`'s 210/`MutatorPostTerrain`'s 220 — the same
verified anchor `RUT_Miasma_GradientAxisGenStep.xml`'s own header cites).
Anchor selection is configurable, not hardcoded to the Greatbole, per the
build brief: reads `RM_MapComponent_LivingRegrowth.BoleCenters` when
non-empty (M9 paired with M12, guaranteed populated by the order value
above), else falls back to `RM_RootCausewayBiomeExtension`'s own scatter
fields (M9 running standalone). Traces 3-6 (INVENTED) wandering spline
paths per anchor in 1-2-wide lanes, restricted to `basinTerrains` when set;
`RUT_Greentide`'s own extension names `RM_Churnmud`
(`src/RimMandrake/Greentide/Defs/TerrainDefs/RM_Churnmud_Terrains.xml`,
`GREENTIDE_STANDALONE_MOD_1`'s already-shipped M8 basin — the real name,
checked, not guessed) as the basin to route over. Connects every anchor to
its own nearest neighbor (not a full minimum spanning tree, but enough for
"the network spans the map" per the spec's own text). "Roads slowly move
between visits" untouched, still correctly parked on
`EXPLOSIVE_PLANT_GROWTH_1`'s v2 list per the spec's own deferral.

**Self-review findings (M12's crush/eject logic touches player state
directly, reviewed carefully per the build brief).** One real bug found
and fixed before commit: `ProcessTimers` only checked for sealant at
schedule time, so sealing a cell already mid-`Scheduled`/`Warning`/
`Crushing` would NOT cancel its pending timer — a colonist could seal a
chamber and still have the tree crush it later. Fixed: the sealant check
now runs every pass, for every state, before the due-tick check. Two
accepted (not fixed) edge cases, both flagged rather than engineered
around: (1) a pawn crushed with genuinely no valid non-footprint escape
cell within radius 6 (e.g. deep in a large, fully-tunneled bole) takes
repeated Blunt pulses until it dies rather than stalling — matches the
spec's own intended lethality ("the tree crushes... whatever stands in the
way"), not treated as a bug, but real and worth the owner's awareness; (2)
`RM_GenStep_LivingBoles` does not individually validate each footprint
cell's terrain before placing heartwood there (only the blob's center site
is checked `Standable`), so a blob could in principle straddle water —
low-risk given the biome's own terrain table, not fixed this pass.

**Save-format note.** Unlike every other `RM_MapComponent_*` in this
assembly (which are deliberately NOT Scribed, being fully re-derivable
from currently-spawned things), `RM_MapComponent_LivingRegrowth` DOES
Scribe its full per-bole state (`BoleRecord`/`CellTimer`, both new
`IExposable` classes) — re-deriving a bole's footprint by flood-fill on
every load would silently shrink it once any chamber is mined out, so the
footprint and every pending timer are saved in full instead.
`RM_CompLivingBoleMarker` scribes its own `boleId` and skips
re-registering (re-flood-filling) on any load where that id is already
set.

**Mod Settings** (`MOD_OPTIONS_RETROFIT_1` pattern, `RM_EnvironmentalHazardsSettings`):
three new toggles — `livingBolesEnabled` (WORLDGEN-AFFECTING, gates
`RM_GenStep_LivingBoles`), `livingRegrowthEnabled` (gates
`RM_MapComponent_LivingRegrowth`'s tick — off freezes every registered bole
exactly where it is), `rootCausewaysEnabled` (WORLDGEN-AFFECTING, gates
`RM_GenStep_RootCauseways`). Landed in the same shared `RM_EnvironmentalHazardsMod.cs`
the concurrent M1/M2 pass was also editing — see "concurrency" below.

**Concurrency with the M1/M2 pass.** Both passes edited
`RM_EnvironmentalHazardsMod.cs` and `RM_EnvironmentalHazards.csproj`
concurrently in separate windows; both sets of edits were additive
(different toggle names, different `<Compile>` entries) and the M1/M2
window's own commit (`946fc0b04`) ended up capturing this pass's uncommitted
edits to those two shared files along with its own — verified afterward
(`git status`/`git show --stat`) that the committed content is byte-correct
for both passes' additions, not just claimed correct. No content was lost
or overwritten; this item's own commit below carries only the files that
commit did not already capture (the 6 new `.cs` files, the rebuilt `.dll`,
and everything under `src/RimUtinni/`).

**Confirms `FEVER_WOOD_MECHANICS_1`'s dependency is now satisfiable.**
`RM_GenStep_RootCauseways` and `RM_MapComponent_LivingRegrowth` both exist,
compile, and expose a generic public surface (footprint-registration API on
the MapComponent; a reusable marker `ThingComp` any future bole/dungeon
Thing can carry) — that item's own F6/F7 can now build against them without
inventing either class itself.

**Build/validate.** `RM_EnvironmentalHazards.csproj` rebuilds clean, 0
warnings/0 errors, including the concurrent M1/M2 files. All 11 new/changed
UtinniPatches XML files (2 ThingDefs, 2 TerrainDefs, 2 GenStepDefs, 2
registration patches, 1 BiomeDef edit, 1 translation file) validate 0
errors/0 warnings via `validate_patch.py` against the live 99-active-mod
installed set (one pre-existing, unrelated WARN: `mandrake.rut.vaultdungeons`
has no folder on disk). Two placeholder textures shipped (not held) because
`UtinniPatches` owns the `Things/` texture namespace itself — a vanilla-path
reuse like `RUT_MineableFungalGround`'s own would be a hard validate_patch
ERROR here, not the tolerable WARN a mod with no `Textures/` folder of its
own gets; genuine flat-color placeholder PNGs ship instead, both still
flagged `DEPLOY_HOLD` for real art.

**Owed**: wild-bole dungeon population (layout + occupant, explicitly
roster/template work per the build brief, capability-only this pass);
`RUT_ToxinSealant`/`RUT_RootCauseway`/`RUT_GreatboleHeartwood`/
`RUT_GreatboleCore` real art (`DEPLOY_HOLD`); the two accepted edge cases
above; no bridge/quicktest verification (none attempted, per scope — no
game access in this task).

**M1 — wet-bulb overwhelm.** `RM_GameCondition_WetBulb : GameCondition`
(new) + `RM_WetBulbExtension : DefModExtension` (new) ramp
`RUT_WetBulbOverwhelm` severity on an interval, cribbing
`HediffGiver_Heat.OnIntervalPassed`'s `HealthUtility.AdjustSeverity` shape
per the spec, with the three named gates: (1) gain scaled by
`max(0, 1 - protection/protectionHoldThreshold)` against the new
`RM_WetBulbProtection` StatDef, summed across worn apparel by the condition
itself (an "Apparel"-category stat has no vanilla pawn-level
auto-aggregation — `ArmorUtility` is the only vanilla reader, and it reads
per-apparel, not per-pawn); (2) zero gain while `pawn.GetRoom()` reads dry
in the new `RM_MapComponent_DryRooms` (M2's own registry); (3) species
exemption via the kit's existing shared `HazardTargeting.Affects`, not a
fourth bespoke gate. Attached to `RUT_Greentide` via
`RUT_GreentideWetBulbLock` (GameConditionDef) +
`RUT_GreentideWetBulbLock_BiomeWiring.xml` (patch). Ships
`RUT_WetBulbOverwhelm` (HediffDef, 4-stage escalation to collapse, stage
shape cribbed from vanilla `Heatstroke`), `RM_WetBulbProtection` (StatDef,
`ParentName="ArmorRatingBase"` crib, same shape `RM_ArmorRating_Scald`
already established in this mod), and three `RUT_` apparel defs
(`RUT_WickingWrap` 0.3, `RUT_SealedSuit` 0.6, `RUT_DryHood` 0.2 — stacking
any two of the heavier pieces already reaches the 0.8 hold threshold). All
three apparel defs reuse a real, already-shipping vanilla texPath verbatim
(`Apparel_TribalA`/`Apparel_Vacsuit`/`Apparel_HatHood`, confirmed via
RimSage raw fetch) — real art on day one, no DEPLOY_HOLD entry needed, 0
validate_patch.py errors on all three (only the expected "cannot verify a
packed vanilla texture from here" WARN, not an ERROR).

**M2 — the dry-air blower.** `RUT_DryAirBlower` ThingDef (new building)
composed of vanilla `CompPowerTrader`/`CompRefuelable`(Chemfuel)/
`CompFlickable`/`CompHeatPusher`, plus one new comp,
`RM_CompDryFieldEmitter : ThingComp` (+ its `CompProperties_DryFieldEmitter`),
on `CompTickRare` (vanilla's own 250-tick cadence, matching the spec's own
named animal-scan interval exactly):

1. **Dries the room** — registers `parent.GetRoom()` into
   `RM_MapComponent_DryRooms` every active tick rather than once at spawn,
   because a `Room` object is not durable (vanilla regenerates it on any
   wall/door change); re-registering on a cadence is self-healing across a
   geometry change with no spawn/despawn bookkeeping. Dryness is a decaying
   grant (`dryUntilTick`), not a boolean, so a fuel-starved blower simply
   stops refreshing it and the room reverts on its own — "the green notices
   within hours" for free, no explicit stop path.
2. **Repels encroachment — FLAGGED, not built, exactly as the calling
   brief specified.** Confirmed by grep before this pass started
   (`grep -r "PlantSuppression\|ExplosivePlantGrowth" src/`, zero hits):
   `EXPLOSIVE_PLANT_GROWTH_1`'s suppression grid does not exist anywhere in
   `src/` yet. `RM_CompDryFieldEmitter.SuppressPlantGrowth()` is a
   documented no-op method with a `TODO(EXPLOSIVE_PLANT_GROWTH_1)` comment
   naming exactly what it should call once that engine ships — building the
   grid itself here would be doing a different item's whole job.
3. **Repels animals — built for real**, per the spike pass's own
   resolution (`AvoidGrid` confirmed absent as a route; the fallback scan
   is the only one). A 90°-arc, radius-3 scan (both **INVENTED** per the
   spec) applies the new short `RUT_DryAirAversion` hediff (a
   `HediffCompProperties_Disappears` marker, 2500–3500 ticks — doubles as
   the re-trigger cooldown) to non-immune wild animals and starts vanilla
   `MentalStateDefOf.PanicFlee` on them in the same call.

Two new Mod Settings toggles (`wetBulbOverwhelmEnabled`,
`dryAirBlowerEnabled`), following this mod's existing one-master-switch-
per-mechanism convention — added as entries 20/21 after the M9/M12 build
pass's own 17–19, which landed in this same file concurrently (another
window, same repo, no file collision: confirmed by reading the live file
before editing rather than assuming the numbering this item's own spike
pass left off at).

**Build/validate**: `RimMandrake.EnvironmentalHazards.dll` rebuilt, 0
warnings/0 errors (`RM_EnvironmentalHazards.csproj`, 4 new `<Compile>`
entries appended after the M9/M12 pass's own). `validate_patch.py` against
the live 99-mod list: 0 errors on 8 of 9 new/changed def files; the ninth
(`RUT_DryAirBlower.xml`) carries the one expected error — its own new
texPath has no art yet — held in `DEPLOY_HOLD.txt` exactly like every
sibling kit's own missing-building-art entries (Scald/Sump/Forge).

**Owed**: M2's plant-suppression write (blocked on `EXPLOSIVE_PLANT_GROWTH_1`
existing at all — not this item's job to unblock); `RUT_DryAirBlower`'s own
sprite; M1's `immunePawnKinds`/`immuneThingDefs` lists (empty this pass —
Greentide's own fauna roster, including which species count as
"elevated-thirst" or "native", is a follow-on item, same gap M5/M7 already
carry). No bridge/game access this pass, same posture as the spike.

## files (M1/M2 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_WetBulbExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_WetBulb.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_DryRooms.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompDryFieldEmitter.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (2 new settings toggles)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (4 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimMandrake/EnvironmentalHazards/Defs/StatDefs/RM_WetBulbProtection.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_WetBulbOverwhelm.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_DryAirAversion.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_GreentideWetBulbLock.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_GreentideWetBulbLock_BiomeWiring.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Apparel/RUT_WickingWrap.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Apparel/RUT_SealedSuit.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Apparel/RUT_DryHood.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_DryAirBlower.xml` (new, held — no art)
- `src/DEPLOY_HOLD.txt` (1 new entry, `RUT_DryAirBlower.xml`)

## M6 build pass — 2026-09-14

Full build of M6 (three-feller tree fall), per the kit spec's own M6
section, resolved 2026-09-13 by this item's own spike pass ("no falling-
tree machinery exists ... `RM_TreeFallUtility` must be built from scratch
exactly as this section already assumed" — re-cited, not re-verified).

**`RM_TreeFallUtility.FellTree(Plant tree, Rot4 dir, FallCause cause)`**
(`src/RimMandrake/EnvironmentalHazards/Source/RM_TreeFallUtility.cs`, new,
generic RM_-tier — not Greentide-hardcoded, matches this assembly's own
"build once, pay three times" kit-home posture every prior M-pass in this
item used). Walks `ext.fellLength` cells from the trunk in `dir` (an
`RM_FellableTreeExtension` on the Plant def supplies every number below;
an untagged Plant falls back to a conservative built-in default so the
utility never throws on an arbitrary vanilla tree): each cell takes one
Blunt hit (`ext.fallDamageRange.RandomInRange`, **INVENTED** 30-120 per the
spec's own range, tiered by `isGiantClass` — placeholder giant ships
70-120, the utility's own untagged fallback is 20-40) against every Thing
there except the tree itself; the first `heartRadius` cells roll one
`hardwoodDef` drop total (giants only); every cell independently rolls a
`greenwoodDef` drop at `greenwoodDropChancePerCell` (**INVENTED** 0.5,
stack 5-15, giant placeholder overrides to 0.6/10-25); a dust puff throws
at every cell. `SoundDefOf.Roof_Collapse` (a real vanilla crash cue) plays
once at the trunk unless `ext.crashSound` overrides it — no new SoundDef
authored, matching M9/M12's own "reuse before invent" precedent for
cues. Distant-crash ambience is free from that alone, per the spec — a
plain map-volume `PlayOneShot` needs no falloff/sustainer work. The tree
is then `Destroy(DestroyMode.Vanish)`d explicitly, not killed by its own
swath. Gated by one new settings toggle, `treeFallEnabled` (#22) — the
single choke point all three fellers route through, so turning it off
mid-game freezes a cracking/mid-chew tree exactly where it is rather than
forcing anything back upright.

**`RM_FellableTreeExtension`** (new, same file's sibling
`RM_FellableTreeExtension.cs`) — the opt-in tag `FellTree`, feller 1's own
comp, feller 2's hook and feller 3's JobGiver all key off. Carries
`isGiantClass`, `fellLength`, `fallDamageRange`, `heartRadius`,
`hardwoodDropRange`, `greenwoodDef`/`hardwoodDef` (generic `ThingDef`
fields, same idiom `RM_LivingBoleBiomeExtension`'s own
heartwoodThing/coreMarkerThing already set in this assembly — a different
biome's giant tree names its own resource defs, not a hardcoded
RUT_Greenwood/RUT_Hardwood lookup), `greenwoodStackRange`/
`greenwoodDropChancePerCell`, `crashSound`, `dustPuffScale`.

**Feller 1 — cracked from within.** `RM_CompCrackFall : ThingComp` +
`CompProperties_CrackFall` (new, same file). `CompTickRare` (250-tick
cadence, matching every other interval roll in this assembly). Below
`minGrowthFraction` (**INVENTED** 0.9 — "past a growth/age threshold" per
the spec) the tree never rolls at all; at/above it, MTB scales linearly
from `mtbDaysAtFullGrowth * 2` at the threshold down to
`mtbDaysAtFullGrowth` (**INVENTED** 8 days, the spec's own named figure) at
full growth — "scaling down at lower growth if that reads better
mechanically" per the build brief's own discretion, recorded here as the
exact formula (`RM_CompCrackFall.EffectiveMtbDays`) rather than left
implicit. On a hit: creak sound (`Props.creakSound` or
`SoundDefOf.Building_Complete` — the same fallback
`RM_MapComponent_LivingRegrowth`'s own creak cue already uses in this
assembly) + a `RM_TreeFallCreak` message, then `FellTree` after
`fallDelayTicksRange` (**INVENTED** 300-900 ticks, "a few hundred" per the
spec).

**Feller 2 — shattered from the side.** Build-time decision the spec left
open ("a damage-watcher on tagged tree defs, or the comp exposes an
on-kill callback — decide at build against the comp's final shape"):
**chose the callback, as a Props field, not a watcher.** Added
`fellsTreesBelowHealthFraction` (float, default 0 = off) to
`HediffCompProperties_PeriodicAreaAttack`, and a `TryFellTree` check inside
`HediffComp_PeriodicAreaAttack.DamageCell`, called right after its existing
`t.TakeDamage` for every Thing the burst touches. Read the comp's real
current shape before deciding (its `DamageCell` already snapshots the cell,
already computes a per-category multiplier including `plantMultiplier`,
already TakeDamages each Thing individually) — a watcher would stand up a
second scanning system (a Harmony patch or a MapComponent tick) duplicating
work this method already does every burst; the Props field is zero-cost
when unset (every other consumer of this ruled comp — SUMP_MECHANICS_1,
MIASMA, FORGE etc. — is unaffected, since the default is 0) and generic
(any `RM_FellableTreeExtension`-tagged Plant this comp damages below the
fraction falls, not a Greentide-specific subclass). `TryFellTree` fires
`RM_TreeFallUtility.FellTree` with `Rot4.FromAngleFlat((plant.Position -
carrier.Position).AngleFlat)` (away from the carrier) once a tagged
Plant's `HitPoints` drops to/below `fellsTreesBelowHealthFraction *
MaxHitPoints`; untagged plants are never affected by this hook regardless
of the fraction. Not wired onto a live Shatterer HediffDef this pass — no
such HediffDef exists yet in `src/` (the Shatterer itself is roster/design
content, out of this item's scope) — the field and hook are proven to
compile and are ready for that def to set
`<fellsTreesBelowHealthFraction>` whenever it ships.

**Feller 3 — gnawed from below.** `RM_JobGiver_GnawTreeBase` +
`RM_JobDriver_GnawTreeBase` (new, `EnvironmentalHazards/Source/`, not
`CreatureBehaviors` — it calls `RM_TreeFallUtility`/
`RM_FellableTreeExtension` directly, so it lives in the same assembly as
what it drives rather than adding a new cross-project reference). Written
directly for this one job, not through the generic `RM_JobGiver_
GnawTargets` extension-scanner already in `CreatureBehaviors` — same
posture `RM_JobGiver_ChewAnchors` already set in this repo for
`JobGiver_Mine`-shaped work ("write it directly per creature", per that
item's own review note the spec's M6 text explicitly points back to). The
JobGiver (~30 lines) finds the nearest `RM_FellableTreeExtension`-tagged
Plant within `RM_GnawTreeBaseExtension.searchRadius` (**INVENTED** 40) via
`GenClosest.ClosestThingReachable`; the driver walks to it and runs one
toil that counts down `chewTicksToFell` (**INVENTED** 2400 ticks — no
figure named in the spec's own text for this duration) with a progress
bar, then calls `FellTree(tree, Rot4.Random, FallCause.Gnawed)`. Cribbed
structurally from `RM_JobDriver_Gnaw` (SHIP_VERMIN_MOD_1, same assembly
family) but ends in a real fall rather than a generic bite-kill, per the
spec's own explicit distinction.

**Gnawer PawnKindDef — confirmed absent, placeholder shipped.** Grep
before this pass started (`grep -rn "Gnawer" src/`) found none. Per the
build brief's own fallback: `RUT_Placeholder_GreentideGnawerRace.xml` +
`RUT_Placeholder_GreentideGnawer.xml` (new, `UtinniPatches/`) — a
recolored Squirrel, the exact same placeholder shape
`RUT_Placeholder_SumpMouseRace`/`RUT_Placeholder_SumpMouse`
(SUMP_MECHANICS_1) already established in this repo for the identical
situation, read in full before writing these. Carries the marker/tuning
extension `RM_GnawTreeBaseExtension` (new). Wired via
`RUT_ThinkTree_GreentideGnawerFell.xml` (new) — the same globally-inserted,
marker-gated `insertTag="Animal_PreMain"` idiom
`RUT_ThinkTree_SumpMouseWander.xml` already set, safe-by-construction for
every other animal (the JobGiver's own first real check returns null for
any race without the extension). Neither def is added to `RUT_Greentide`'s
own `wildAnimals` list or any GenStep — proving the mechanism compiles and
is reachable, not populating the biome, same posture the SumpMouse
precedent itself used.

**Content.** `RUT_Greenwood.xml` (new item, `ParentName="ResourceBase"`,
same shape `RUT_Hardwood.xml` already set — MarketValue 1.8, Mass 1.5,
**INVENTED** both) and `RUT_Placeholder_GreentideGiantTree.xml` (new Plant,
`ParentName="TreeBase"`, MaxHitPoints 900/visualSizeRange 3.5-5.0/drawSize
(6,6), all **INVENTED**, sized for the spec's own "a giant comes down
across ten tiles" line — matches `fellLength` exactly). Both new files —
placeholder giant tree + Greenwood item — ship genuine flat-color
placeholder PNGs (64×64/128×128 RGBA, same discipline `RUT_Hardwood.png`
already set), **not** a real donor texPath: `Textures/Things/Plants/
AB_JungleTree` and its siblings already sit in this repo as real, unused
art, but `infrastructure/artpipe/done/jungletree_v1.json` and the flora
roster docs already track them for the real roster pass's own giant —
poaching that file here risked a defName/asset collision with that future
real def, so a fresh placeholder was authored instead. Real bespoke art
for both is owed, same posture as every sibling placeholder this session.

**Self-review (build brief's own instruction: the fall-damage swath
directly damages player structures/pawns — review the targeting logic
carefully).** `RM_TreeFallUtility.DamageCell` snapshots each cell's Thing
list before damaging (`new List<Thing>(cell.GetThingList(map))`), same
defensive shape `HediffComp_PeriodicAreaAttack.DamageCell` already uses,
so destroying a Thing mid-loop cannot corrupt the live list — and skips
only the falling tree itself (`t == tree`), meaning every pawn, building
and item in the swath, including the player's own, takes the hit, which is
the spec's own explicit intent ("crushing what it lands on"), not an
oversight. Two accepted (not fixed) simplifications, both flagged rather
than engineered around, matching this item's own M12 self-review posture:
(1) no `sparedNaturalRock`/`sparedUnderThickRoof` check — a swath that
runs into a mountain edifice can chip it once; low risk relative to
M12's own concern (that hazard is a long-lived repeating aura, this is a
single one-time pass); (2) feller 2's `TryFellTree` hook is called from
inside the ruled comp's own per-Thing loop, but `RM_TreeFallUtility.
DamageCell`'s own internal swath damage does **not** itself call
`TryFellTree` — confirmed deliberately non-recursive: a Shatterer's aura
felling one tagged tree cannot chain-trigger a second fell even if that
tree's own swath crosses another tagged tree, which would otherwise be a
real chain-reaction risk in a dense stand.

**Mod Settings.** One new toggle, `treeFallEnabled` (entry #22,
`RM_EnvironmentalHazardsMod.cs`) — the single master switch for all three
fellers, per this mod's established one-master-switch-per-mechanism
convention.

**Build/validate.** `RimMandrake.EnvironmentalHazards.dll` rebuilt, 0
warnings/0 errors (6 new `<Compile>` entries; `HediffCompProperties_
PeriodicAreaAttack.cs`/`HediffComp_PeriodicAreaAttack.cs`/`RM_
CompStationEater.cs` edited in place for the feller-2 hook and the shared
`RM_EnvironmentalHazardsJobDefOf` class). `validate_patch.py` against the
live 99-active-mod installed set: 0 errors on all 6 new/changed def files
(the usual "no def in the load set uses that class" info-lines for brand-
new C# classes, and the usual "cannot verify a packed vanilla texture"
WARNs on the Squirrel-reuse texPaths — both the same expected shape every
prior placeholder in this repo produces, not a real error).

**Owed.** Real bespoke art for `RUT_Placeholder_GreentideGiantTree`/
`RUT_Greenwood` (flat-color placeholders ship, not held from deploy — they
compile and validate clean, same as `RUT_Hardwood`'s own precedent); the
real Shatterer HediffDef to actually set
`fellsTreesBelowHealthFraction` (feller 2's hook is proven, unwired to
live content); the real Gnawer/giant-tree roster content (both
placeholders explicitly out of scope, same as every prior placeholder this
item shipped); no bridge/quicktest verification (no game access in this
task, same posture as every build pass in this item).

## files (M6 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_FellableTreeExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_TreeFallUtility.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompCrackFall.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GnawTreeBaseExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_JobGiver_GnawTreeBase.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_JobDriver_GnawTreeBase.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/HediffCompProperties_PeriodicAreaAttack.cs` (feller 2 hook field)
- `src/RimMandrake/EnvironmentalHazards/Source/HediffComp_PeriodicAreaAttack.cs` (feller 2 hook call)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompStationEater.cs` (shared JobDefOf class, 1 new entry)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (1 new settings toggle, #22)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (6 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimMandrake/EnvironmentalHazards/Defs/JobDefs/RM_JobDefs_TreeFall.xml` (new)
- `src/RimMandrake/EnvironmentalHazards/Languages/English/Keyed/RM_EnvironmentalHazards_Keys.xml` (2 new keys)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_Greenwood.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_Placeholder_GreentideGiantTree.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Placeholder_GreentideGnawerRace.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/RUT_Placeholder_GreentideGnawer.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThinkTreeDefs/RUT_ThinkTree_GreentideGnawerFell.xml` (new)
- `src/RimUtinni/UtinniPatches/Textures/Things/Plant/GreentideGiantTree/RUT_Placeholder_GreentideGiantTree.png` (new, placeholder)
- `src/RimUtinni/UtinniPatches/Textures/Things/Item/Resource/RUT_Greenwood.png` (new, placeholder)

## M4/M5 build pass — 2026-09-14

Full build of the remaining M4 (the Roil weather) and M5 (Breaklight)
pieces per this item's own spike-pass reconciliation of both sections
(above): M4's overlay class (`RM_WeatherOverlay_GreentideRoil`) and M5's
seek-shade AI (`RM_JobGiver_SeekShade`) were already shipped before this
pass; everything else in both sections lands here — almost entirely XML
wiring onto already-compiling ruled classes
(`GameCondition_EnvironmentalWeather`/`EnvironmentalWeatherExtension`,
`BiomeGlowPatches`), plus one small new generic C# class and one small new
gate on an existing one.

**M4 — the Roil.** `RUT_RoilWeather.xml` (WeatherDef, accuracy 0.7/move
0.95, both the spec's own INVENTED figures, overlayClasses pointing at the
already-shipped `RM_WeatherOverlay_GreentideRoil`) forced permanently via
`RUT_RoilLock.xml` (GameConditionDef, `conditionClass` =
`GameCondition_EnvironmentalWeather`, no damage/hediff/rot/density fields
set — pure weather force, same shape `RUT_ScaldSteamLock`/
`RUT_MiasmaWeatherLock` already established for their own sibling biomes),
wired onto `RUT_Greentide` via `RUT_RoilLock_BiomeWiring.xml`. "The steam
deflects the sun": `BiomeGlowMultiplierExtension{glowMultiplier: 0.75}`
(the spec's own INVENTED value) added directly to `RUT_Greentide.xml`'s
`modExtensions` — zero new code, the ruled `BiomeGlowPatches` Harmony patch
already reads it. "Underlight rain": `Ambient_Rain` (real, already-shipping
vanilla SoundDef, confirmed via `mcp__rimsage__search_defs`) added to
`RUT_Greentide.xml`'s `soundsAmbient` — cosmetic, no mechanic, no C#, per
the spec's own explicit minimal-content license. The biome's own stale
header note ("no dedicated Roil/Breaklight WeatherDefs exist yet") is
corrected in place per the repo's "inaccurate material is deleted, not
superseded-in-place" rule — it named a real gap this pass closes.

**M5 — Breaklight.** `RUT_BreaklightClear.xml` (WeatherDef, clear/harsh —
accuracy/move left at their 1.0 defaults rather than repeated, no
overlayClasses, bright near-white sky colours, all INVENTED-BUILD tuning
since the spec names no figures) fired by `RUT_Breaklight.xml` (IncidentDef,
category Misc, `workerClass` = a new one-line subclass
`RUT_IncidentWorker_Breaklight` rather than bare vanilla
`IncidentWorker_MakeGameCondition` — see below for why; `durationDays`
0.125~0.3333 = 3-8 hours, the spec's own INVENTED figure; `baseChance`
1/`minRefireDays` 6, both this pass's own INVENTED since the spec gives no
refire cadence; `allowedBiomes: [RUT_Greentide]`), which registers
`RUT_BreaklightCondition.xml` (GameConditionDef, `conditionClass` =
`GameCondition_EnvironmentalWeather`, `tempOffset` 12 — confirmed a real,
already-shipped `EnvironmentalWeatherExtension` field before use, not
guessed — `temperatureTransitionTicks` 2500 INVENTED for a fast ramp-in,
`allowUnderground` false since a cave has no sun to snap clear).

Confirmed against the live def dump (`mcp__rimsage__get_def_details
HeatWave`) that vanilla's own weather-event incidents (HeatWave, ColdSnap)
use the identical category-Misc/`baseChance`/`minRefireDays` shape with no
bespoke StorytellerComp — Breaklight rides the Storyteller's ordinary
periodic Misc-incident roll, not a hand-rolled `MapComponent` timer (unlike
`RUT_Surge`, whose sibling biome carries an explicit "no clockwork tide"
ban this kit's own M5 section never states).

Two small hookups, both additive to already-shipped shared classes rather
than new comps, per the spec's own framing of each as a small extension:

- **Glow override** (new class `RM_GlowMultiplierOverrideExtension`,
  `src/RimMandrake/EnvironmentalHazards/Source/`): a `DefModExtension` for a
  `GameConditionDef` (not a `BiomeDef`, unlike `BiomeGlowMultiplierExtension`).
  `BiomeGlowPatches.CurCelestialSunGlow_Postfix` now checks
  `EnvironmentalHazardsMod.ActiveGlowOverrideFor(map)` first — a scan of
  `map.gameConditionManager.ActiveConditions` for one whose `def` carries the
  new extension, gated behind a load-order-computed `anyGlowOverrideOptsIn`
  flag so every install that never uses the feature pays only a bool read,
  same hot-path posture `anyBiomeOptsIn` already established for the
  biome-side check. When found, its `glowMultiplier` (1.0 on
  `RUT_BreaklightCondition`) is applied INSTEAD of the biome's own 0.75, not
  stacked with it. Deliberately generic — nothing in the new class names
  Greentide or Breaklight — so any future dark-biome "clearing event"
  reuses it without new C#, exactly the spec's own "benefits every future
  dark biome with a clearing event" framing.
- **Wet-bulb pause**: `RM_WetBulbExtension` gained one new field,
  `pausedByConditions` (`List<GameConditionDef>`, empty/no-op by default) —
  `RM_GameCondition_WetBulb.RampMap` now checks it before gate 2's per-room
  dried-room check and idles the WHOLE map's ramp for the tick if any named
  condition is active (`GameConditionManager.ConditionIsActive`), a genuine
  gate-4 addition, not a reduced rate. `RUT_GreentideWetBulbLock.xml` is the
  only config naming `RUT_BreaklightCondition` here — the C# class itself
  stays kit-agnostic, matching M1's existing data-driven shape rather than
  hardcoding Breaklight's defName in `RM_GameCondition_WetBulb.cs`.

`RUT_IncidentWorker_Breaklight` (new class, same RUT_-prefixed-content-in-
`mandrake.rm.environmentalhazards` precedent `RUT_WeatherOverlay_ScaldSteam`
already set): a one-line `IncidentWorker_MakeGameCondition` subclass adding
only the `breaklightEnabled` mod-setting gate — no firing logic of its own.
Needed because, unlike a permanent `biomeMapConditions` lock (which has no
individual toggle in this kit's existing convention — Scald/Miasma/this
pass's own Roil lock are all ungated), a rare incident-fired event has no
other on/off hook to retrofit `MOD_OPTIONS_RETROFIT_1`'s "master switch per
mechanism" rule onto.

**Patch-order bug found and fixed in self-review, before commit.**
`RUT_RoilLock_BiomeWiring.xml` is the SECOND patch to touch
`RUT_Greentide.xml`'s `biomeMapConditions` node (M1's
`RUT_GreentideWetBulbLock_BiomeWiring.xml` was first) — PatchOperation order
between two same-mod files is not something either file controls. The
existing M1 patch used a bare `PatchOperationConditional` with only a
`<nomatch>` branch (add-the-whole-node); if this pass's own Roil patch had
happened to run first, the WetBulb patch's `<nomatch>` branch would have
silently done nothing on its own turn (node already exists, no `<match>`
branch to fire), permanently dropping `RUT_GreentideWetBulbLock` from the
biome with no error and no log. Fixed by adding the symmetric `<match>`
branch (append-`<li>`) to `RUT_GreentideWetBulbLock_BiomeWiring.xml` itself,
and writing `RUT_RoilLock_BiomeWiring.xml` with both branches from the
start — both patches are now correct regardless of load order.
`validate_patch.py` confirms both files' `<nomatch>` branch is the one that
actually fires against the live 99-mod load order (alphabetical: M1's file
sorts before M4's), so this was a latent bug, not a live one — worth fixing
anyway since load order is not a contract.

**Owed** (explicitly deferred per this item's own scope, not silently
dropped): M5's "everything scrambles for shade" visible animal AI — a
seek-shade JobGiver keyed to Breaklight specifically — is flavor-only and
was NOT built this pass, per the calling brief's own instruction; M1's
`immunePawnKinds`/`immuneThingDefs` lists remain empty (Greentide's own
fauna roster, a follow-on item, unchanged by this pass); no art held —
neither new WeatherDef carries a texPath validate_patch.py can flag, and the
Roil overlay's own missing texture was already flagged (no DEPLOY_HOLD.txt
entry needed either way, matching `RUT_WeatherOverlay_ScaldSteam`'s own
precedent: a weather overlay's `MatLoader.LoadMat` call is invisible to that
tool); no bridge/quicktest verification (no game access in this task, same
posture as every build pass in this item).

**Build/validate.** `RM_EnvironmentalHazards.csproj` rebuilds clean, 0
warnings/0 errors (2 new `<Compile>` entries:
`RM_GlowMultiplierOverrideExtension.cs`, `RUT_IncidentWorker_Breaklight.cs`;
4 files edited: `BiomeGlowPatches.cs`, `RM_WetBulbExtension.cs`,
`RM_GameCondition_WetBulb.cs`, `RM_EnvironmentalHazardsMod.cs` — the last
gaining settings toggle #23, `breaklightEnabled`). `validate_patch.py`
against the live 99-active-mod installed set: 0 errors across all 9
new/changed def/patch files; 2 advisory WARNs, both the expected
"add-if-missing `<nomatch>` shape" info the two biome-wiring patches always
carry (confirmed intentional, same as every sibling lock-wiring patch in
this item); several `info` lines noting the new/edited C# classes aren't
resolvable from the undeployed Mods folder, expected pre-deploy and matching
every prior build pass in this item.

## files (M4/M5 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_GlowMultiplierOverrideExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_IncidentWorker_Breaklight.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/BiomeGlowPatches.cs` (glow-override lookup, wired into the postfix)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_WetBulbExtension.cs` (1 new field, `pausedByConditions`)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_WetBulb.cs` (gate 4, the dry-air pause)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (1 new settings toggle, #23)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_RoilWeather.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_RoilLock.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_RoilLock_BiomeWiring.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_GreentideWetBulbLock_BiomeWiring.xml` (patch-order bug fix, `<match>` branch added)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml` (M4's `BiomeGlowMultiplierExtension`/`soundsAmbient`; stale header note corrected)
- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_BreaklightClear.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_BreaklightCondition.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_Breaklight.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_GreentideWetBulbLock.xml` (M5's `pausedByConditions` wiring)

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values.
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanisms `RM_` in Greentide's
  own standalone mod (`mandrake.rm.greentide`) or the shared
  `mandrake.rm.creaturebehaviors`/`mandrake.rm.environmentalhazards`
  assemblies as appropriate; "Jawa" is lore text only.
- No duplicate defs against what `FORGE_MECHANICS_1` and
  `GREENTIDE_STANDALONE_MOD_1` already shipped — enforced by this pass's own
  spec reconciliation, to be checked again at the next build pass.

## M3/M7 build pass — 2026-09-14

M3's remainder (the steam devil vortex — the Scald damage-type trio stays
FORGE_MECHANICS_1's, not re-shipped) and M7 (Lunger ambush) in full, per
`greentide_kit_spec.md`. Concurrent with another window's M4/M5 pass
(`6f7f5ff61`, landed mid-way through this one) — different files, no
collision on the source it touched; the shared `RM_EnvironmentalHazards.csproj`
and `RM_EnvironmentalHazardsMod.cs` were both mid-edit by that window at the
same time and got clobbered back to pre-my-edit state once (csproj) — caught
by a stale-file notification, re-applied on top of the current disk content
rather than reverting theirs.

**M3 — the steam devil.** `RUT_SteamDevil` ThingDef (`ParentName=
"EtherealThingBase"`, category Ethereal/no hit points — def shape cribbed
from the real vanilla Tornado def, read directly off the live install's
`Data/Core/Defs/ThingDefs_Misc/Ethereal_Various.xml`) + new
`RM_WanderingVortex : ThingWithComps`
(`src/RimMandrake/EnvironmentalHazards/Source/`), structurally cribbed from
`Source/RimWorld/Tornado.cs` (read in full) and reimplemented in this
repo's own words: a bounded-drift wander (plain `Rand.Range` heading nudge
on a fixed interval, not Tornado's own private-static Perlin field — a
documented, deliberate simplification), a close-radius damage sweep on an
interval, a rare far hit, and a lifetime countdown to dissipation.
Parameterized via new `RM_WanderingVortexExtension` (DefModExtension):
`damageDef` points at the already-shipped `RUT_Scald`; wander speed,
lifetime, both damage radii/intervals, damage amount range and armor
penetration are all **INVENTED** (recorded in that class's own field
comments — no figures named in the spec's own text for any of them).
Fells trees it crosses via `RM_TreeFallUtility.FellTree` (M6's shared
routine, unmodified except one additive change: a new
`FallCause.WindThrown` enum value, since none of the three existing causes
fit and `FellTree` doesn't branch on the value today) —
**INVENTED** per the spec's own explicit rule: a giant-tagged tree only
falls below `giantTreeFellHealthFraction` (0.5) of its max HP, a non-giant
or untagged tree falls unconditionally once in the swath.

Spawned by `RUT_SteamDevilAppears` IncidentDef (new
`RUT_IncidentWorker_SteamDevil`, weighted into `RM_Greentide` only,
**INVENTED** baseChance 2 / minRefireDays 5). The Roil-condition rare-spawn
hook (spec: "and, rarely, by the Roil condition itself") is **NOT wired**
— checked before build: `RUT_RoilLock.xml`/`RUT_RoilWeather.xml` existed on
disk but uncommitted at check time, another window's own M4/M5 pass still
in flight, so M4 counted as not-yet-landed per the build brief's own
explicit fallback for this exact race ("if M4 hasn't landed yet when you
check, wire the plain IncidentDef route only... don't wait on it"). M4 has
since landed and committed (`6f7f5ff61`) — re-checked after the fact,
purely for this note: `RUT_RoilLock`'s `conditionClass` is the shared,
already-ruled `GameCondition_EnvironmentalWeather` (also the Wet Bulb/
Scald Steam/Miasma locks' own conditionClass), which has no per-tick
arbitrary-Thing-spawn hook at all — wiring a rare vortex spawn into it
would mean extending a widely-reused shared class, not a small addition,
so it stays owed rather than retrofitted under this pass.

**Self-review** (build brief's own instruction — this directly damages
pawns/structures/trees): `DamageCloseThings`/`DamageFarThing`/`FellTreesNearby`
all snapshot their own cell's Thing list before iterating (same defensive
shape `RM_TreeFallUtility.DamageCell`/`HediffComp_PeriodicAreaAttack.DamageCell`
already use), so a Thing destroyed mid-sweep cannot corrupt the loop.
`CellImmuneToDamage` excludes natural rock and un-owned (Faction-null)
walls exactly like Tornado's own exclusion — a colonist's OWN built wall
IS hit, the spec's own intent. One real catch this review found and fixed
before shipping: the ThingDef initially cribbed Tornado's `drawerType
RealtimeOnly` without cribbing its ~180-line custom `DrawAt` mesh code —
with no `graphicData` and no draw override, that combination risked an
engine draw call against a null `Graphic` every frame. Fixed by leaving
`drawerType` at `EtherealThingBase`'s own inherited `None` — the vortex is
now represented only by its own `FleckMaker.ThrowSmoke` column, no drawn
sprite. Flagged, not silently accepted: this means the spec's own "visible
from far off" is **not actually met** by flecks alone (they render only
near the vortex's current cell) — real custom draw code, or at minimum
`graphicData` once art exists, is owed to a later rendering pass.

**M7 — Lunger ambush.** New `RM_CompAquaticAmbusher : ThingComp` +
`CompProperties_AquaticAmbusher` (`src/RimMandrake/CreatureBehaviors/Source/`,
generic RM_-tier — any future aquatic ambush creature can reuse it, not
Greentide-hardcoded). Reads "no melee target" / "target acquired" as one
operation: while the carrying pawn stands on deep water (**INVENTED**
reading of "deep water" — the three vanilla-named DEEP water TerrainDefOf
entries: `WaterDeep`/`WaterOceanDeep`/`WaterMovingChestDeep`, distinct from
their Shallow counterparts) with no hostile pawn within `lungeRangeCells`
(5, spec's own figure), it grants `RM_AquaticAmbushInvisibility` (stock
`HediffComp_Invisibility`, the Revenant/Sightstealer machinery, per the
spec's own "reuse vanilla invisibility wholesale"); a hostile pawn found
within range removes that hediff (`BecomeVisible(instant: true)` then
`RemoveHediff`, an intentionally sudden reveal — an ambush snapping visible
reads right, not a graceful fade) and force-starts `RM_LungeAttack`
(new JobDef, driven by new `RM_JobDriver_LungeAttack`): a fast approach
(an optional short `RM_LungeSpeedBurst` self-expiring MoveSpeed hediff,
**INVENTED** +2.5 c/s for 240 ticks) ending in ONE manually-dealt
`DamageDefOf.Bite` hit at `baseLungeDamageRange` (**INVENTED**, 12-20)
`× firstStrikeDamageMultiplier` (1.5, spec's own figure). The opener is
dealt via direct `TakeDamage`, not the pawn's normal melee-verb pipeline —
deliberately, to avoid a Harmony patch on `Verb_MeleeAttackDamage`'s own
private damage-resolution method for what the spec itself frames as
"a small comp"; ongoing combat after the opener is 100% vanilla predator
ThinkTree, exactly the spec's own stated boundary. Self-review catch: the
comp now also treats a `Downed` pawn as a no-op (vanilla's own
`HediffComp_Invisibility.ForcedVisible` already forces a downed pawn
visible regardless, but nothing previously stopped a fresh lunge job from
being force-started on one).

**DLC-gate finding**: `HediffComp_Invisibility`'s own `UpdateTarget` calls
`ModLister.CheckRoyaltyOrAnomaly` — confirmed via decompile, matches the
spec's own note. Checked against the owner's live `ModsConfig.xml`
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon
Studios\Config\ModsConfig.xml`) this pass: both `ludeon.rimworld.royalty`
and `ludeon.rimworld.anomaly` are active — the gate is satisfied on the
owner's own install, nothing here would silently fail to compile or work
for him.

**Placeholder finding**: the spec's M7 section never states outright
whether the Lunger PawnKindDef is roster content (unlike some sibling kit
pieces, which say so explicitly) — read as ambiguous, so treated the same
as every other kit's creature-content boundary this session. Vanilla Core
`Alligator` (predator, water-seeker, real swimming graphic — confirmed via
RimSage) is aquatic-ambush-shaped enough to need **no art recolor at all**,
unlike M6's Gnawer placeholder (a tinted Squirrel). New
`RUT_Placeholder_GreentideLungerRace`/`RUT_Placeholder_GreentideLunger`
(ThingDef+PawnKindDef, `UtinniPatches/`) copy Alligator's own real
statBases/tools/race/lifeStages/graphics fields down directly —
`ParentName="Alligator"` does **not** work (`validate_patch.py` caught it
live: Alligator carries no `Name="..."` attribute, the same trap the
Gnawer placeholder's own header already recorded for Squirrel) — and add
only the one new comp. Neither def is added to `RM_Greentide`'s own
`wildAnimals` list or any GenStep, same "compiles now, first live spawn
later" posture as every prior placeholder this item shipped. §6.6's "no
safe standing water" spawn-density rule: **INVENTED** reference figure
recorded in the PawnKindDef's own header (ecoSystemWeight 1.2-1.5 vs.
vanilla's 0.5, once a real roster pass actually wires this into a biome) —
not set on the placeholder itself, since it is deliberately unwired.

**Build/validate.** Both assemblies rebuilt, 0 warnings/0 errors
(`RimMandrake.EnvironmentalHazards.dll`: 3 new `<Compile>` entries plus one
additive enum value in `RM_TreeFallUtility.cs`;
`RimMandrake.CreatureBehaviors.dll`: 3 new `<Compile>` entries).
`validate_patch.py` against the live 99-active-mod installed set: 0 errors
on all 7 new/changed def files (the usual info-line for a brand-new C#
class no def yet resolves against by name across the load set, and the
usual "cannot verify a packed vanilla texture" WARNs on the Alligator-reuse
texPaths — both the same expected shape every prior placeholder in this
repo produces).

**Owed.** The Roil rare-spawn hook for M3 (see above — needs the shared
`GameCondition_EnvironmentalWeather` class extended, or a side
`MapComponent`, not a small addition); real custom draw/art for the steam
devil (currently flecks-only, does not meet "visible from far off"); real
bespoke art for the Lunger placeholder pair; the real Lunger roster content
(placeholder explicitly out of scope); no bridge/quicktest verification (no
game access in this task, same posture as every build pass in this item).

## files (M3/M7 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_WanderingVortexExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_WanderingVortex.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_IncidentWorker_SteamDevil.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_TreeFallUtility.cs` (additive `FallCause.WindThrown` enum value)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (1 new settings toggle, #24 `steamDevilEnabled`)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (3 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Misc/RUT_SteamDevil.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_SteamDevilAppears.xml` (new)
- `src/RimUtinni/UtinniPatches/Languages/English/Keyed/RUT_Greentide_SteamDevil.xml` (new)
- `src/RimMandrake/CreatureBehaviors/Source/CompProperties_AquaticAmbusher.cs` (new)
- `src/RimMandrake/CreatureBehaviors/Source/RM_CompAquaticAmbusher.cs` (new)
- `src/RimMandrake/CreatureBehaviors/Source/RM_JobDriver_LungeAttack.cs` (new)
- `src/RimMandrake/CreatureBehaviors/Source/RM_JobDefOf.cs` (1 new JobDef entry)
- `src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs` (1 new settings toggle, #11 `aquaticAmbushEnabled`)
- `src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviors.csproj` (3 new `<Compile>` entries)
- `src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll` (rebuilt, 0 warnings/errors)
- `src/RimMandrake/CreatureBehaviors/Defs/JobDefs/RM_JobDefs.xml` (new `RM_LungeAttack` JobDef)
- `src/RimMandrake/CreatureBehaviors/Defs/HediffDefs/RM_AquaticAmbush_Hediffs.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Placeholder_GreentideLungerRace.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/RUT_Placeholder_GreentideLunger.xml` (new)
