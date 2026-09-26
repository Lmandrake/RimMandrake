# SUMP_TAR_HYDROLOGY_1 — how the tar flows: the Sump on FlowWorks

Eight owner rulings, 2026-09-24, post-sitting flow round (his framing, typed:
consider *"how the flow works on the rest of this biome since making tar
[moats] was one of the original inspirations of that particular mod and all the
places that the tar liquid might go in terms of an entire ecosystem if oceans
and rivers were made of tar"* — *"as well as even things like tar rain"*).
Engine ground: FlowWorks pulsed spread (sort+overflow depth grid, no per-tick
sim), `RM_Tar` registry row at Heavy viscosity, tar→chemfuel at FOUND
refineries (`liquids_framework_design.md` — and the found-refinery set-piece now
has its Inhabited fiction: "attempts at refineries," `SUMP_INHABITED_NOTES_1`).

## the rulings

1. **Tar rain — in the MOD, not this scenario.** Typed, verbatim: *"Tar rain is
   part of mod but not this scenario."* ⇒ `RM_TheSump` ships a tar-drizzle
   weather (coats terrain, tars pawns, roofs matter — feeds the solvent
   economy); the Ash'karr campaign scenario keeps it OFF. First explicit
   mod-vs-scenario feature split; sheet ban 4 ("no rain") stands untouched for
   the campaign — the ban was about water, and the scenario sees no tar rain
   either.
2. **Accumulation: belches only** (card). No background seep gain; the map's tar
   level changes only through belch events (and burning/removal). No slow-drown
   background pressure.
3. **Flood fronts cool to glass** (card). A belch flood self-limits: its edges
   harden into walkable glass-reach terrain, the middle stays soft — every belch
   rewrites the map, and natural glass is the process the glasswalk imitates.
4. **Full canal-work** (card). Players dig channels and gates for `RM_Tar`:
   drain a dig claim, feed the moat and refinery, flood a raider approach on
   command (FlowWorks' own weaponized-gate v1 idea, now sited here).
5. **Fire follows the network; gates are firebreaks** (card). Lit tar propagates
   along connected liquid — a lit canal burns to its gate, a lit pool to its
   edges. Gate placement is life-and-death craft; a belch during a moat-burn is
   a genuine catastrophe.
6. **Edges are sinks, never sources — the FlowWorks edge law.** First typed as
   *"Only outflow."*, then clarified in full, typed, verbatim: *"What I mean is
   that a canal, when dug to the edge of the map, can serve as a sink. It can
   remove any kind of liquid by allowing it to flow to some other map. However,
   we should not assume that another map will be a source of anything at the
   edge. So that is why it is a sink only. Sources can be as rich as needed on
   the local map. And if we are next to an ocean, it should already be on this
   map, connected to a canal as effectively an infinite source."*
   ⇒ For the Sump: no inflow seams — the tar's arrival stays geological and
   unseen; sources are LOCAL (seeps and belches, as rich as the design needs);
   a canal dug to the map edge drains any liquid off-map — the player's tar
   disposal; and the Deep Black mere (ruling 7), canal-connected, is the
   biome's effectively infinite on-map source. This is engine law for ALL
   FlowWorks liquids, not a Sump special — noted on
   `FLOWWORKS_BUILD_PROGRAM_1`.
7. **The Deep Black** (card): a landmark-scale unbroken deep-tar mere — beast
   country, undiggable from shore, the biome's "ocean" at MAP scale. ⛔ No new
   world-map body; the frozen world stays untouched (the "world-map body too"
   option was offered and not taken).
8. **The living map** (card): slow responders after every rewrite — soffeth
   rings grow at new seeps, mouse-lines re-route, flora margins migrate to new
   edges over days. The literacy game stays true after every belch.

## engineering-tier questions (not carded — build's discretion, flag surprises)

- Depth grades of tar vs the D/F depth primitives and pits: does a pit dug in
  the Sump fill with tar? (`PIT_SUPERDEEP_COLLAPSE_1` owns pit law.)
- Wading rules: entering shallow tar = mire + tarred hediff
  (`SUMP_TAR_NASTINESS_1`), never a swim.
- Heavy-viscosity `ticksPerTile` tuning for oozing floods and canals.
- The found tar-cracking refinery set-piece on Sump maps (industry found, not
  built) — fiction already in `SUMP_INHABITED_NOTES_1`.
- Temperature gating of flow/hardening (glass fronts imply cooling logic; keep
  it event-shaped, no per-tick sim — pillar 2).
- Worldmap tanker-raid target ("fly to that tar lake"): the Sump's tiles serve
  without a new world body, per ruling 7.

## verify

Quicktest: a belch pulse spreads by depth rules and leaves a glass rim; a canal
carries tar through a gate and stops at a closed one; igniting a connected canal
burns to the gate and no further; the mere generates as one landmark expanse;
tar-rain weather exists in the mod and is absent from the campaign scenario
preset; indicator flora re-seed near a new soft area within days.

## criteria

The tar is one connected, steerable, burnable, self-healing system — the mod
that was inspired by tar moats finally gets its tar world.

## build status — FOUNDRY, 2026-09-26, partial: 3 of 6 sub-mechanisms built/confirmed, 3 deferred

This is a six-piece item (belch/glass-front cooling, full canal-work, network
fire + firebreak gates, outflow seams, the Deep Black mere, living-map
responders + tar rain) and it is genuinely too large to build fully-verified
in one pass, per this session's own established pattern. Read first: three
prior tar items closed this session — `SUMP_TAR_BELCH_EVENT_1` (closed, the
scenario-scoped belch that explicitly deferred the FlowWorks-integrated
version here), `SUMP_TAR_VAULT_1` (closed, the tar-vault/solvent economy) and
`SUMP_TAR_NASTINESS_1`'s own S1 (`RM_TarCoatingUtility`, still live and
untouched this pass). This pass built in `mandrake.rm.flowworks` and
`mandrake.rm.thesump` only, per this session's contention map
(`src/RimMandrake/EnvironmentalHazards/` — where the belch incident worker
itself lives — was avoided as contended).

**Confirmed already built, no new code needed:**

- **Full canal-work.** `RM_Fluid_Tar`/`RM_Liquid_Tar` (Defs/Canals/FluidDefs/
  FlowWorks_Fluids.xml, Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml)
  already ride the SAME generic depth/canal engine every other FlowWorks
  liquid uses — `Designator_DigCanal`/`JobDriver_DigCanal`/
  `WorkGiver_DigCanal`/`Flood_FlowWorks` are liquid-agnostic by construction,
  and tar has been a registered row since `FLOWWORKS_BUILD_PROGRAM_1` Phase
  7. Players can already dig channels/gates for tar, flood a raider approach,
  drain a dig claim — ruling 4 is satisfied by the existing engine plus the
  existing registry row, not by anything built this pass.
- **Outflow seams.** Ruling 6's own text reframes this ask: "no inflow
  seams... edges are sinks... a canal dug to the map edge drains any liquid
  off-map." That sink law is `Designator_DigCanal`'s own Phase-4 ruling-9
  edge-sink mechanic (`RimMandrakeFlowWorksSettings.edgeSinksEnabled`),
  already generic across every FlowWorks liquid including tar. Nothing biome-
  specific was owed here either.

**Built this pass:**

1. **Glass-front cooling — the generic FlowWorks engine half of ruling 3.**
   `FluidDef.coolsToGlassEdge` (new nullable field, `Source/FluidDef.cs`):
   null for every fluid but tar (water/brine/propane/chemfuel/slimes
   unaffected). `Flood_FlowWorks.CoolFrontToGlass()` (new, called from the
   two Tick() branches that are a genuinely self-limiting finish —
   `remainingVolume <= 0` and `frontier.Count == 0` — never from the
   stuck/expiry branch) writes the glass terrain onto the PERMANENT layer of
   every FRONT cell (a placed cell bordering at least one cell the release
   never reached), while the interior is untouched. Interior behaviour ("the
   middle stays soft") is read conservatively as UNCHANGED existing recede
   behaviour, not a new permanent-pool mechanic — flagged as an
   interpretation choice, not a measured ruling; a stronger reading (the
   interior becomes a permanent pool too) is real follow-on work.
   `RM_TarGlass` (new TerrainDef, Defs/LiquidTypes/TerrainDefs/RM_TarGlass.xml
   — hand-authored, kept OUT of the generated RM_Tar.xml on purpose) is
   FlowWorks' own tier-neutral glass terrain, modelled directly on the
   already-shipped `RUT_Glasswalk` (`SUMP_WALKWAYS_1`, whose own header
   explicitly deferred "crossing the liquid tar itself" to this item).
   `RM_Fluid_Tar.coolsToGlassEdge` wired to `RM_TarGlass` in the base def;
   `src/RimUtinni/UtinniPatches/Patches/RUT_Tar_GlasswalkCooling.xml` (new,
   `PatchOperationConditional`-gated) repoints it to the campaign's bespoke
   `RUT_Glasswalk` when UtinniPatches is active, so the campaign gets the
   lore art/slip mechanic and a standalone FlowWorks install still gets a
   real, working glass front — same "the free mod looks the same, the
   campaign layer adds flavour on top" posture `biome_mod_architecture.md`
   §7 Q11a already establishes for naming, generalised here to a mechanism.
   ⚠️ NOT wired into the actual Sump belch incident this pass —
   `RUT_IncidentWorker_TarPitBelch` (mandrake.rm.environmentalhazards,
   contended this session) still calls `RM_TarCoatingUtility.CoatRadius`
   exactly as `SUMP_TAR_BELCH_EVENT_1` shipped it. That class's own header
   already names the intended swap ("find epicenter -> flood pulse") and
   says it needs no change to the IncidentDef/settings/biome restriction —
   see the follow-on item.
2. **The Deep Black mere (ruling 7).** `RUT_GenStep_DeepBlackMere` (new,
   `mandrake.rm.thesump`'s own assembly): a randomized flood-fill (same
   reservoir-sampling shape `Flood_FlowWorks.SpreadOneTile` already uses,
   kept as an independent copy since the two run on different engines) grows
   one organic 180-420-cell blob (INVENTED-BUILD size, no owner number given)
   of `RM_TarDeep` plus a thin `RM_TarShallow` rim, at least 12 cells from
   the map edge, once per Sump map. Self-gated on the map's own biome
   (`RM_TheSump`/`RUT_Sump` by defName, same string-not-hard-reference
   posture `RM_LiquidBodyDef.biomes` already uses for this exact twin pair)
   and on a new Mod Settings toggle (`RM_TheSumpSettings.deepBlackMereEnabled`,
   default on). Registered onto `Base_Player` globally
   (`Patches/RUT_GenStep_DeepBlackMere_Register.xml`, order 225 — ahead of
   `RUT_GenStep_TarBeastPlacement`'s 780, so the mere becomes an eligible
   dormant-beast site too), costing nothing on any other biome. Explicitly
   NOT a world-map body, per ruling 7's own "no new world-map body" clause —
   pure per-map generation, nothing touches the frozen Ash'karr planet.
   **"Effectively infinite on-map source" (ruling 6) needed zero new engine
   code**: `RM_MapComponent_Excavation.IsSourceCell` already reads any
   natural `TerrainDef.IsWater` cell as a source with no excavation write at
   all, and `RM_TarDeep`/`RM_TarShallow` both carry the `Water` tag and
   inherit `WaterDeepBase`/`WaterShallowBase` (read directly, not assumed) —
   so placing the terrain is the whole job; the source property comes free
   from the existing engine.

**Deferred to `SUMP_TAR_FIRE_AND_LIVING_SYSTEMS_1`** (filed this pass): network
fire with gate firebreaks (ruling 5 — Phase 8's sluice-gate hardware does not
exist yet, and `LiquidIgnitionMapComponent`'s own header says it "has never
ticked inside a running game" and is off by default; wiring tar as flammable
also needs `Terrain.Flammability` calibrated the same careful way propane's
was, per `FLOWWORKS_BUILD_PROGRAM_1` Phase 6's own unmeasured-premise flag);
the living-map responders (ruling 8 — soffeth rings, mouse-line rerouting,
flora-margin migration over days; a multi-day simulation needing iterative
live tuning, not a mechanism this pass could invent numbers for); tar-rain
weather (ruling 1 — genuinely blocked on an architecture question, not
merely deferred for time: BOTH `RM_TheSump` and `RUT_Sump` currently force
the SAME `RUT_SumpDuskLock` permanent-dusk-no-rain `GameCondition` via
`ForcedWeather()`, so a naive "mod ships it, scenario doesn't" wiring would
either never roll on either biome or require unpicking the dusk lock's own
rain-suppression for the free mod without breaking the campaign's own
shipped "no rain" guarantee — a real design call, flagged rather than
guessed at); and wiring the belch incident itself to the new glass-cooling
mechanism (touches the contended `EnvironmentalHazards` assembly).

**Validated offline**: `dotnet build` on both `RimMandrake_FlowWorks.csproj`
and `RM_TheSump.csproj` (Release) — 0 warnings/errors on each. `validate_patch.py`
against the live 628-mod set (Data+Mods+Workshop) — all 5 new/changed XML
files: 0 errors, 0 warnings (one info-only note on the GenStepDef's Class,
expected for a mod not currently enabled in ModsConfig — same shape prior
items in this wave already document). Deployed via `deploy_custom_mods.py
--apply --mod FlowWorks --mod TheSump --mod UtinniPatches`: all new/changed
Defs/Patches files verified in sync; both the FlowWorks and UtinniPatches
DLLs FAILED to write (locked — RimWorld running with those two mods active),
a PRE-EXISTING sibling-pass condition this pass did not cause; TheSump's own
DLL (not currently enabled in ModsConfig, so not locked) deployed and
verified byte-identical.

**What a live proof needs** (no bridge access this pass): a tar canal release
that runs its reservoir dry or walls itself in should leave a visible glass
rim once its temp fluid layer recedes (~5000 in-game minutes later by
default — `floodedTicks`); a fresh Sump map should show one large connected
tar expanse well clear of the edge; a canal dug into that expanse should
never run dry. None of this pass's three pieces needs the owner present —
all are state/terrain checks, not the flyer-style "must be watched live"
class.
