# SUMP_TAR_NASTINESS_1 — the Sump is nasty, and the tar gets on everything

Owner ruling 2026-09-24 (typed in chat, quoted in full on
`BIOME_NUISANCE_NORMALIZATION_1`): the Sump must be many kinds of nasty — stinky,
sticky, messy, little way to keep clean. This item is the Sump-NOW slice of that
principle; the planet-wide normalization is gated to the end
(`BIOME_NUISANCE_NORMALIZATION_1`).

## spec

Four mechanics, all RM-tier (`RM_TheSump` / its kit), feature-gated per the Mod
Settings law:

1. **Sticky tar onto any terrain surface** — an overlay/coating a source can apply
   to arbitrary terrain (belch events, beast surfacing, tracking). 🔑 Check what is
   already built before writing anything: the Fever Wood's `RM_ToxinSealant`
   (item + terrain, `RM_MapComponent_LivingRegrowth` gating on it) is the shipped
   terrain-coating precedent; also weigh filth-based vs TerrainDef-swap approaches
   against `RM_CompTimedTerrainBurn` (Sump kit) and the FlowWorks/liquids layer.
   `SUMP_TAR_BELCH_EVENT_1` consumes this mechanism — build them coherently.
2. **Tarred-pawn hediffs** — tar on yourself: move/work penalties, mood, hygiene-
   flavored stink, spreads filth, maybe flammability. Severity from exposure;
   removal is not free.
3. **Solvents** — cleaning items that remove tar from pawns (and coated terrain).
   A WEAK solvent is craftable in-biome from local materials; the STRONG solvent is
   deliberately NOT craftable here (the Poison Forest's acid line is the owner's
   example source — arrives by trade). Do not build the foreign side; leave the
   item hook (trade tag / def placeholder) for the normalization pass.
   ✅ REFINED same sitting (`SUMP_GASLIGHT_1` holds the verbatim rulings): the
   cleaner is an ACID and cleaning works BY the tar→green-gas reaction; the weak
   local acid renders from thrummel seepwax, ruled generous ("one raid should
   give you a lot. Not meant as a starvation mechanism"); the same acid gates
   vault extraction (`SUMP_TAR_VAULT_1`) and fuels the warbling lamp.
4. **The tar's own reward** — annoying materials pay: the sheet already calls the
   tar biologically rich; pick the reward with the roster docs (fuel/chemistry/
   preservation are the obvious axes) and make gathering it want the coping gear.

## verify

On a quicktest map: tar can be applied to a non-tar terrain and cleaned off it; a
pawn crossing gets the hediff and a weak solvent removes it; the weak solvent is
craftable from in-biome materials only; the reward loop yields something a colony
wants. All four toggleable in Mod Settings.

## criteria

A Sump colony is a constant, legible fight against the tar — losable by neglect,
priced in solvent, and worth it because the tar itself pays.

🔑 **Tuning law** (owner, 2026-09-24, typed; full quote on `SUMP_INHABITED_NOTES_1`):
the biome *rewards* players who enjoy their colony being dirty, messy,
idiosyncratic, and *frustrates* players who want neat, tidy, controlled. Tune every
knob here toward that — coping must be viable and characterful; full cleanliness
should be a losing fight, not an achievable state.

## build status — FOUNDRY, 2026-09-24, offline-complete on all 4 pieces, needs live proof

All four mechanics built and deployed this pass, extending `SUMP_WALKWAYS_1`'s
already-shipped `RM_Filth_Tar`/`Pawn_FilthTracker` foundation rather than inventing a
second tar representation, per this session's own brief. Content still lands as
`RUT_`-tier under `UtinniPatches` (same convention `RUT_TarMoat`/`RUT_BeastBulge`
already use) since `RM_TheSump` (`THESUMP_RM_MOD_BUILD_1`) does not exist yet; generic
mechanisms are `RM_`-tier C# in `mandrake.rm.environmentalhazards`, matching every
other Sump-kit mechanism in this repo.

**1. Terrain coating** — `RM_TarCoatingUtility.cs` (static: `CoatCells`/`CoatRadius`,
wraps `FilthMaker.TryMakeFilth`, RimWorld/FilthMaker.cs, read in full) +
`RM_Comp_TarCoatingSource.cs` (`CompProperties_TarCoatingSource`/
`RM_Comp_TarCoatingSource`: a generic ThingComp any Thing can carry to splash a filth
coating on spawn and/or on a tick interval). **Compiles now, no XML consumer wired
this pass** — `SUMP_TAR_BELCH_EVENT_1` (named by this item's own spec as the intended
first consumer) is not a filed item as of this build; same "mechanism now, content
later" posture `RM_CompFloodIgniter` used before its own S1 build pass wired it.
Gated by `RM_EnvironmentalHazardsSettings.tarCoatingEnabled`.

**2. Tarred-pawn hediff** — `RM_HediffComp_CarriedFilthExposure.cs` (severity accrues
while `Pawn_FilthTracker.CarriedFilthListForReading` contains the configured
filthDef, decays when clean — sibling to `HediffCompProperties_EnvironmentalExposure`
but keyed on carried filth instead of weather) + `RM_CarriedFilthHediffExtension.cs`
(BiomeDef ModExtension, presence-is-opt-in idiom) + `RM_MapComponent_
CarriedFilthHediffLink.cs` (per-map scanner that actually hands a newly-tarred pawn
the hediff). Content: `RUT_Tarred_Hediffs.xml` (3 stages, move penalty via `capMods`
Moving, work penalty via `statFactors` WorkSpeedGlobal, `Flammability` statOffset from
stage 2 — "maybe flammability" from the spec, all fields verified against the live
1.6 decompile) + `RUT_Tarred_Thoughts.xml` (`ThoughtWorker_Hediff`, 3 stages matching
the hediff's own, same pattern `RUT_VorrelEuphoriaThought` already uses in this repo)
+ `RUT_Sump.xml`'s own `<modExtensions>` wiring the two together. "Spreads filth"
(spec's own line) needs no new code — `Pawn_FilthTracker.Notify_EnteredNewCell`
already does it, purely from carrying `RM_Filth_Tar` at all. Gated by
`RM_EnvironmentalHazardsSettings.tarredHediffEnabled`.

**3. Solvents** — `RUT_ThrummelSeepwax` (raw feedstock, roster-named, no recipeMaker
yet — the thrummel hive/creature does not exist, so "raid a mound" has no job to
attach to; tradeable/debug-spawnable meanwhile) → `RUT_WeakTarSolvent` (crafted at
TableMachining, 1 seepwax → 4 solvent, deliberately generous per the ruling) via the
short vanilla `recipeMaker` route (no separate RecipeDef, same shape
`RM_SapResin`→`RM_ToxinSealant` already uses in Greentide). `RUT_StrongTarSolvent`
built as the explicitly-instructed HOOK ONLY — no recipeMaker, a `tradeTags` marker
(`RM_ForeignSolventTrade`) for `BIOME_NUISANCE_NORMALIZATION_1` to wire later, never
built as a working trade path this pass. The actual cure:
`RUT_Tarred_Surgery.xml` (`RUT_ScrubTarred`, vanilla `Recipe_RemoveHediff`, zero new
C#, same shape `RSW_RemoveBrainWorm` already ships in this repo) +
`RUT_TarredSurgery_RecipeUsers.xml` (patch attaching it to every race that already
lists `ExciseCarcinoma`, identical xpath to `BrainWormSurgery_RecipeUsers.xml`).
Accepts either solvent. 🔴 **NOT BUILT**: the tar→green-gas reaction chemistry itself
(`SUMP_GASLIGHT_1`'s own scope — "cleaning works BY the reaction" is that item's full
mechanism; this pass's cure is a direct hediff removal with no gas byproduct, honest
partial coverage of this item's own §3, flagged rather than duplicated).

**4. The tar's own reward** — `RUT_Bitumen` (fuel/chemistry axis: waterproofing,
adhesive, torch-fuel, asphalt — the_sump.md §7's own naming, independently confirmed
OWED by `sump_flora_roster_2026-09-24.md` row 4 as the korveth plant's harvest
output). No recipeMaker/harvest job yet (the korveth plant and the dig-barrel economy
are both separately unbuilt) — real and immediately spendable as a COST, not yet
producible. **Correction landed the same pass**: `RUT_Glasswalk`'s own costList
(`SUMP_WALKWAYS_1`, this same session) was a flagged Chemfuel placeholder for exactly
this def — repointed to `RUT_Bitumen`×6 in this commit, both item files updated.
"Make gathering it want the coping gear" (spec's closing line): noted as a design
requirement on whichever pass builds the harvest job (tar exposure risk without
solvent on hand); not implemented, since no harvest job exists to attach it to.

**Validated offline**: `dotnet build RM_EnvironmentalHazards.csproj -c Release` — 0
warnings/errors (5 new `.cs` files + `.csproj` entries + 2 new Mod Settings toggles,
checkboxes, `ExposeData` lines, view-height bump). `validate_patch.py` against the
live 621-mod set (Data+Mods+Workshop) on all 10 touched/new XML files: 0 errors after
one fix-forward round — three new resource ThingDefs (`RUT_ThrummelSeepwax`,
`RUT_WeakTarSolvent`, `RUT_StrongTarSolvent`) and `RUT_Bitumen` first reused vanilla
texPaths as placeholders (matching `RUT_TarMoat`/`RUT_WickStem` precedent) but hit the
SAME hard-ERROR trap `RM_Filth_Tar.xml` already documented — `UtinniPatches` already
claims `Textures/Things/Item/Resource/` as its own namespace
(`RUT_Greenwood.png`/`RUT_Hardwood.png`) — repointed to four new `RUT_`-named folders
with simple procedurally-drawn placeholder icons; re-validated clean. Deployed via
`deploy_custom_mods.py --apply --mod EnvironmentalHazards --mod FlowWorks --mod
UtinniPatches` — plan matched exactly (17 files: `+`/`~`, pre-existing holds
untouched), `-> VERIFIED in sync`.

**DEPLOY_HOLD status**: `RM_Filth_Tar.xml` and `RUT_TarShallow_GeneratedFilth.xml`
(`SUMP_WALKWAYS_1`'s own holds) are **LIFTED** this pass — three procedurally-drawn
placeholder blob sprites now ship at
`FlowWorks/Textures/Things/Filth/RM_FilthTar/RM_FilthTar_{a,b,c}.png`
(`Graphic_Cluster` reads texPath as a FOLDER, confirmed against
`Verse/Graphic_Collection.cs`, not guessed). `src/DEPLOY_HOLD.txt` updated to record
both lifts. No new holds added this pass — every new def resolved a real texPath
after the fix-forward round above.

**What a live proof needs** (no bridge access this pass):

1. Quicktest map with `RM_TarShallow`/`RUT_Duckboards`: confirm a pawn standing in
   tar actually picks up `RM_Filth_Tar`, that `RUT_Tarred` is then GIVEN to them
   (`RM_MapComponent_CarriedFilthHediffLink`'s own scan, 250-tick interval — not yet
   confirmed to fire in a live game), and that its 3 stages/mood/stat effects read
   correctly as severity climbs.
2. Confirm `RUT_ScrubTarred` actually appears on a tarred pawn's health-tab
   operations list, consumes `RUT_WeakTarSolvent`/`RUT_StrongTarSolvent`, and removes
   `RUT_Tarred` on completion.
3. Confirm `RUT_WeakTarSolvent`'s bench recipe actually appears at `TableMachining`
   once `RUT_ThrummelSeepwax` exists in inventory (debug-spawn it — no live source
   yet).
4. `RM_Comp_TarCoatingSource` (piece 1) has NO live consumer to test yet — its own
   correctness (does a Thing carrying it actually splash filth on spawn/tick) is
   checkable in isolation once any def wires it, but nothing does this pass.
5. Confirm the two BiomeDef `<modExtensions>` entries on `RUT_Sump` both resolve
   (info-level "no def uses that class" lines in validate_patch.py are expected —
   the assembly ships both classes, confirmed public/correctly namespaced by
   `dotnet build`, but only a live load proves the loader actually resolves them).
6. `RUT_ThrummelSeepwax`'s real source (raiding a thrummel mound) and `RUT_Bitumen`'s
   real source (korveth plant harvest / dig-barrel economy) are both unbuilt — flagged
   on their own def headers, owed to the fauna/flora roster and dig-economy passes
   respectively, not this one.
7. The tar→green-gas reaction (`SUMP_GASLIGHT_1`) is explicitly NOT built here —
   `RUT_ScrubTarred` cures the hediff with no gas byproduct; wiring the reaction is
   that item's own scope, not a gap in this one.

Item stays in `doing` — all 4 pieces have real, deployed, offline-validated content,
but "done" per this item's own `verify` section needs the live checks above, which
this pass had no bridge access to run.

## Reconciliation pass — FOUNDRY, 2026-09-26

Closes owed line 6 (`RUT_ThrummelSeepwax`'s real source) in part. Since the pass
above, `SUMP_FAUNA_ROSTER_1` (closed) shipped the real thrummel family
(`RM_Thrummel`/`RM_ThrummelWarden`/`RM_ThrummelBroodmother`, `RM_TheSump`) with
their own butcher product `RM_Seepwax` — a separate RM-tier def from this item's
own `RUT_ThrummelSeepwax`, by necessity (RM tier may not depend on RUT tier,
Q11a), and that roster item's own header explicitly named reconciling the two as
follow-on work for "whoever next picks up `SUMP_TAR_NASTINESS_1`."

New patch `src/RimUtinni/UtinniPatches/Patches/RUT_ThrummelSeepwax_RosterSource.xml`
(`PatchOperationConditional MayRequire="mandrake.rm.thesump"`, `RUT_Tarred_
Solvents.xml` itself left untouched): gives `RUT_ThrummelSeepwax` a real
recipeMaker, 1:1 off `RM_Seepwax`, `WorkToMake 60` (a cheap render, not a
refinement — the two goods' own descriptions read as the same substance under
two names). `RUT_WeakTarSolvent`'s own crafting chain (seepwax -> solvent) is
now reachable from ordinary wildlife butchering, not only debug-spawn/trade, for
a colony with `RM_TheSump` active. **Still not built**: the actual "hive raid"
source (`SUMP_FAUNA_ROSTER_1`'s own deferred item — mound + defend-radius comp,
UNMEASURED engine feasibility) and the tar->green-gas reaction chemistry
(`SUMP_GASLIGHT_1`'s own scope, untouched). `validate_patch.py` against the live
628-active-mod set: 0 errors, 0 warnings. Full account and the sibling bitumen
reconciliation: `SUMP_MECHANICS_1.md`'s own "Owner card 2 build pass" section,
same commit. Item stays in `doing` — every live-verification line from the
2026-09-24 pass above still stands.
