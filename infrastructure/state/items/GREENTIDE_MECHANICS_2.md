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
