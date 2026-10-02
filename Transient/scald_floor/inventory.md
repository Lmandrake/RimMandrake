# The Scald — sea floor / underwater inventory (2026-09-25)

Read-only survey so a design session on the Scald's sea floor / underwater experience
doesn't reinvent what already exists or is already ruled. BUILT = shipped code/XML.
SPECCED = written design, nothing built. IDEA = mentioned, not designed.

## Cast (creatures)

**BUILT, wired on `RM_TheScald` (franchise-free, RM_ tier):**
- `RM_Noohm` ("noohm") — bubble-sailor jelly-analog. Rides bubble-lines like a solar sail,
  harmless, never attacks, not catchable. `wildAnimals` commonality 0.4. Has real art
  (Graphic_Multi, artpipe-delivered 2026-09-25). Immune to terrain burn via
  `RM_OrganicScaldNative` hediffGiverSet.
- `RM_Shulla` ("shulla") — silver shoal fish-analog, herd animal (group 5-15), dung-fall
  feeder. `wildAnimals` 0.9, ALSO catchable as `RM_ShullaCatch` in `fishTypes` (the sea-floor
  law's "two defs per species": one floor resident, one catch item). Real art shipped.
  Also immune via `RM_OrganicScaldNative`.

**BUILT, Utinni-patched in (Star Wars IP, `mandrake.rsw.swbestiary`-gated), via
`WildAnimals_TheScald.xml`:** `RSW_SandoAquaMonster` (0.03), `RSW_ElderSando` (0.005, both
de-predatored per owner ruling — "armored, slow, pastoral" mat-mowers), `RSW_Faa` (0.5),
`RSW_Mee` (0.5). Kept OFF the franchise-free `RM_TheScald` def itself per Q11a tier rule.

**SPECCED, not built — bottom-walkers.** The_scald.md's "huge creatures walking the crater
floor, mowing the mats, submerged herds" — v1 design (`scald_kit_spec.md` S5) makes them a
**surfacing incident**, NOT a spawned pawn: `RUT_WalkerSurfacing` IncidentDef +
`RUT_IncidentWorker_WalkerSurfacing` — BUILT AND COMPILING (samples deep boil cells, fires a
Message, no pawn). Whether walkers ever become real huntable pawnkinds at depth was
**owner card 3** (open in the kit spec). `sea_dive_maps_spec.md` does NOT list a walker in
its per-sea cast table — an open gap between the two specs.

**Fish/catch roster (8 pre-existing + shulla = 9), all `MayRequire="Ludeon.RimWorld.Odyssey"`,
`fishTypes` on `RM_TheScald`:** freshwater_Common: `RM_Eesh`, `RM_Muddal`, `RM_Doss`,
`RM_Thuum`, `RM_ShullaCatch`; freshwater_Uncommon: `RM_Karrash`, `RM_Saal` (item-face of the
noohm/bubble-sailor concept — NOT the living noohm), `RM_BladderboilCatch`, `RM_Ekkel`;
`rareCatchesSetMaker RM_RareScaldCatches`. Salinity ruled **FRESHWATER** (rivers flow OUT of
the Scald — `RM_liquid_types_mod.md` §9 CARD-1), overriding the sheet's "eight rivers in,
none out" reading (superseded).

## Flora

- **BUILT** `RM_WelcomeBlanket` — the rainbow thermophile mat (the_scald.md §4's "welcome
  blankets"). Wild-spawns only on the `RUT_ScaldMarginMat` terrain tag (never open boil water
  — Ban 4). `maxGrowthTemperature 90` (overridden up from engine default 58 to survive the
  Scald's own ambient). Harvests to `RM_RainbowPigment` (yield 4, work 120). Placeholder art
  (vanilla Ambrosia texPath) — real art still owed.
- No kelp/other Scald-specific floor flora built. (Kelp is a Twilight Sea feature, not Scald,
  per `sea_dive_maps_spec.md`'s per-sea table.)

## Terrain / features / wrecks

- **BUILT** six `RUT_ScaldWater*` terrains (shallow/deep/moving variants): cyan glow
  (2,154,229), `HotSpring` comfort thought, `avoidWander`, burn damage — engine floors
  `burnDamage` at 3 regardless of the authored 1/2 (`Mathf.Max(burnDamage,3)` in
  `HediffGiver_Terrain`, MEASURED). Ruled 2026-09-25: relabel shallow to `burnDamage 3`
  (honest), deep to `burnDamage 4` (owner: "deep water should burn harder") — **ruled, not
  yet built into XML** per the steam spec's build order step 2.
- **BUILT** `RUT_ScaldMargin` — the one non-burning cool ring ("the baths"), sole `dbh_water`
  drink source, swimmable via vanilla `JoyGiver_GoSwimming`. NOT yet placed on the actual map
  (def ships, map-authoring is a separate bridge step). Header flags an UNFIXABLE engine gap:
  `KnownDangerAt` is edifice-only, so nothing stops a swim path crossing open boil water to
  reach the margin — it must be sited as a geometrically isolated cove, never an open-shore
  strip.
- **BUILT** `RUT_ScaldVent` — shore vent building, `RM_Building_ScaldVent` (thin
  `Building_SteamGeyser` subclass), gated `Scald.S4`, feeds `RUT_SteamCatch` condensers
  (`RM_CompResourceCondenser`, generic vent-locked resource comp, built+compiling). Real
  placement on the actual map is a bridge/world-authoring step, not done.
- **BUILT** three `RUT_ScaldWreck{Hull,Tank,Frame}` — `ParentName="ShipChunkBase"` salvage
  buildings (deconstruct-only, vanilla costList/killedLeavings, no loot comp). Real art
  shipped 2026-09-25, shadow volumes hand-calibrated against sprite alpha bbox. Scatter
  mechanism resolved as **zero new C#** — stock `GenStep_ScatterThings` reads
  `terrainValidationAllowed` tags; a shared shallow-tag is owed but not yet added.
- **BUILT** `RUT_ScaldSteamLock` — `RM_GameCondition_WeatherPulse`: forces `RUT_ScaldSteam`,
  MTB 96h clear-spell (12-24h "still day," the window for salvage/vent work without the
  clock running). Gate `Scald.S1`.
- **BUILT** `RUT_SteamDevil` — wandering vortex, deals `RUT_Scald` damage, currently has **no
  species-immunity gate** (ruled fix: C# step 3, small change to
  `RM_WanderingVortexExtension`/`DamageCell`, not yet built).
- **SPECCED, not built** — the Rakatan dark tower dungeon in the crater lake
  (`SCALD_DARK_TOWER_1`), a different item from `sea_dive_maps_spec.md`'s dive floors; sits
  IN the lake, doesn't touch the boil/roster/two-faith shore.

## Mechanics built (diving, dive maps, burns, steam, protections)

**Diving TODAY (shore-only, shipped, `mandrake.rm.divinginteraction`):** float-menu options
"Dive to hunt" / "Dive to commune" on `RM_DiveEligible`-tagged shallow terrain (tagged via
`RM_ScaldDiveEligibleTerrain.xml` — excludes deep/impassable water by construction, so the
boiling surface stays structurally no-swim). `RM_JobDriver_DiveHunt`/`DiveCommune` job
drivers. **This is the ONLY reachable diving today — the sea floor's `wildAnimals` cast is
NOT currently reachable in play** (engine fact, MEASURED: wild-animal spawn never reads
`impassable`, so it's inert until a walkable floor map exists).

**SPECCED (RULED design, nothing built) — `sea_dive_maps_spec.md`, `SEA_DIVE_MAPS_BUILD_1`:**
real underwater pocket maps via `PocketMapUtility.GeneratePocketMap` (the exact mechanism
`src/RimUtinni/LanternDeeps/` already proves live). Right-click "Dive down" on shallow water
generates a persistent 100×100 floor map per sea; a `RM_SurfaceLine : MapPortal` (no building
needed) is the up/down transfer; the floor's biome IS the sea BiomeDef so its `wildAnimals`
finally spawn (needs a new `RM_SeaFloorHabitat` TileMutatorDef to raise animalDensityFactor
~30x and set `allowRoofedEdgeWalkIn`). Scald-specific floor per its table: dark mat-floored
basin, vents with tethered noohm, shulla shoals, wrecks in the deep; clock = 55°C heatstroke +
vent-adjacent `burnDamage 1` floor cells; bans honoured structurally. 8-step build order, step
2 (bare Scald floor) is the falsification test. Two MEASURED pocket-map crash fixes already
paid for by LanternDeeps (plant growth-rate on tile-less map; `WildPlantSpawner` ignoring
biome wildPlants under roof) are reusable as-is. **No open questions remain** — ruled
2026-09-25, ready to build.

**SPECCED (RULED design, step 1 partially built) — `scald_steam_and_hazards_spec.md`,
`SCALD_STEAM_WEATHER_DESIGN_1`:**
- Native immunity to water burn: **BUILT 2026-09-25** (`2f223f825`) — `RM_OrganicScaldNative`
  HediffGiverSetDef (OrganicStandard minus `HediffGiver_Terrain`), applied to both
  `RM_Noohm`/`RM_Shulla`. Deploy+quicktest proof still owed.
- Steam exposure clock (`RUT_ScaldExposure` hediff via existing
  `HediffCompProperties_EnvironmentalExposure`, new `RM_ScaldProtection` stat): **specced,
  not built.** Unprotected = dead under two days.
- Protection ladder RULED: roof (free) → `RM_Apparel_ScaldWrap` (Neolithic, tailoring only) →
  **Royal Rind gear** (Neolithic, from greatbole fruit — no def exists anywhere yet, waits on
  Greentide's fruit item) → `RM_Apparel_BoilSuit` (Industrial research `RM_ScaldWorking`) →
  Odyssey vacsuit (patched). None reach immunity (floor 8%, Ban 3).
- Wading burns stay ordinary vanilla `Burn`/Heat (ruled — NOT retyped to the custom
  `RUT_Scald` damage type, which stays the steam-devil's own).
- Steam overlay art: `RUT_WeatherOverlay_ScaldSteam` currently borrows vanilla's fog material
  wholesale (a real crash — `MatLoader.LoadMat` only reads Unity Resources, mod texture paths
  null-throw — was FIXED live 2026-09-25 at `70607e667` by falling back to vanilla fog).
  Genuine custom look (copy-material-and-swap-textures route) is specced but the two textures
  are still owed art.
- Mod Settings gates specced: `Scald.S1/.S1a/.S1b/.S7/.S8` (steam sky / custom art / vent-
  flash / exposure / lake-burn-toggle-default-ON).

**DEEPFIRE (`LuminousPigment`, `DEEPFIRE_PIGMENT_MOD_1`) — rulings only, spec still a
skeleton (all 11 sections `(pending)`).** Its own item is required content FOR the Scald mod:
glowing pigment harvested from "rare ocean bacterial mats" — **Utinni places the rare-mat
source specifically in the Scald** (dovetails with `RM_WelcomeBlanket`/`RM_RainbowPigment`,
though the item talks about pigment as a *separate, new, more valuable* glow-pigment, not
simply a rename of the existing rainbow pigment — relationship between the two not yet
reconciled). Ruled: name Deepfire; colour comes from normal dye, pigment supplies glow; +1
quality (art items, once) / +beauty (other items, first coat only); paints walls/floors/
furniture; personal items = light sphere + easier to target in dark; GlowTank (hydroponics-
like, low yield); fresh mat decays ~1 day (dies if refrigerated); press bench "looks like a
press and an alchemical setup welded together," default-unlockable via research on first
seeing a mat; status = sumptuary reactions (nobles pleased, low-status disapproval); gods:
trade/craft trio adore, Ishko dislikes; RimCuisine glow-effect-family eating mechanic (body
part/eyes/cranial/neural/mouth/products glow, good+bad per family, chef-skill-steered).
Nothing built — this is a brand-new mod, not started.

## Owner rulings verbatim, with dates

- 2026-09-07 (the_scald.md freeze): sheet FROZEN under `BIOME_FREEZE_FABLE_REVIEW_1` —
  amendments add detail, never change a ruling.
- 2026-09-25 (question card, `SEA_DIVE_MAPS_BUILD_1`): **"Build dive maps"** — chosen over
  "surface in shallows" and "decide later."
- 2026-09-25, typed: *"It's worth talking about how we can make the Scald steam weather really
  beautiful and interesting (and deadly without protective gear)."* And: *"Everything appears
  to be burning. Is that the boiling water? Likely should make its own creatures immune to
  that. Do we already have the water's dangerous nature (and the protections available to the
  player) wired in?"*
- 2026-09-25, typed (protection ladder): *"Industrial research for a boil-suit, but advanced
  vacsuit-types should be able to handle it too. And then there's the Royal Rind from the
  fruit of the great Bole."*
- 2026-09-25, typed (Royal Rind + burn tuning): *"To make clothing out of the Royal Rind
  would render you immune to heat and cold to extreme levels, yes. Neolithic, yes. Yes, deep
  water should burn harder. Yes, a native would need a gene, but we don't have any plans for
  that at this time."*
- 2026-09-25 (Deepfire, typed): *"It's its own RimMandrake mod: LuminousPigment. Required by
  the Scald mod."* ... *"Curing sounds good but I'm not sure how to achieve that since it can
  be used on so many item types, so best to drop it."* ... *"And it should look like a press
  and an alchemical setup welded together."* ... *"They do NOT all need to have 'equal good
  and bad.'"*
- 2026-09-25 (art, ledger note quoting owner card): *"the art looks very simple compared to
  our other lucious high-res art. We should improve it. It would be superb for everything to
  have a few variants where possible too..."* → filed `SCALD_ART_UPGRADE_WAVE_1` (high-res
  restyle, 2-3 stack variants, shulla catch as a fish pile, landspeeder-style wreck redo,
  steam-catch machinery de-blue-tinted, vent visibly CAPPED). Not built.
- 2026-09-12 (scald_kit_spec.md owner cards): diving ships as v1 content, verbatim: *"Diving
  interaction, and make the diving mod v1 content now!!"* Item water is the steam-catch
  default output, `dbh_water` pipe-network behind a Mod Settings toggle.
- 2026-09-25 (SCALD_FLOOR_PASS_1 note): owner asked for a rainbow-pigment brainstorm **beyond
  dye** — halos, shimmer, effects — recorded as **open, unresolved**.

## "bedazzle" / owed-but-unfiled

"Bedazzle" appears only as BENCH's own shorthand for **the live review/beautification sitting
with the owner**, not a mechanic or a filed item name:
- `SCALD_FLOOR_PASS_1` note (06:30): "...then live half: vent placement, dive proof,
  **bedazzle sitting with owner**." Also its 14:32 idle note: "...then bedazzle sitting."
- `BLUEDESERT_DESIGN_SITTING_1` (different biome, same usage): "bedazzle pass to full-mod
  status — rule the sheet's Owed list."
⇒ For the Scald, the bedazzle sitting is the **live review still owed** — SCALD_REVIEW.rws
was staged and saved 2026-09-25 (16:16 note) precisely for this: cast renders read tiny
(drawSize 0.25-0.45), wreck shadows were large dark boxes (fixed via the hand-measured
shadowData above), 6 fish still on borrowed placeholder sprites, margin terrain reads
identical to shallows visually. **This sitting has not yet happened** — it is the natural
next live step, not a design gap.

Other owed-but-unfiled threads found in ledger notes, not yet items:
- Rainbow pigment uses beyond dye (halos/shimmer/effects) — explicitly "open" in the ledger,
  no item filed.
- Relationship between `RM_RainbowPigment` (existing, from `RM_WelcomeBlanket`) and the new
  Deepfire `LuminousPigment` mod's own glow pigment — not reconciled in any doc read.
- Standalone load-proof for the Scald pass — flagged "still owed" as of the 16:16 note.
- A shared shallow-water tag for `RUT_ScaldWreck*` scatter placement (`terrainValidationAllowed`)
  — resolved as needing zero C#, but the tag itself isn't shown as added yet.

## Gaps

- **Sea-floor cast is currently unreachable in play.** `wildAnimals` on `RM_TheScald` never
  spawns until `SEA_DIVE_MAPS_BUILD_1` lands (ruled, unbuilt) — today's diving is shore-job
  only (hunt/commune), not a floor visit.
- **Bottom-walkers** (the_scald.md's signature "huge creatures walking the crater floor") have
  no pawn presence anywhere — only a Message-only surfacing incident. `sea_dive_maps_spec.md`'s
  own Scald floor-cast table lists only noohm + shulla, omitting a walker resident entirely —
  worth flagging explicitly if a design session assumes walkers will be encounterable on the
  dive floor.
- **Steam exposure clock, protection apparel, Royal Rind def, boil-suit + research, vacsuit
  patch** — all ruled, none built (`scald_steam_and_hazards_spec.md` build steps 4-8 pending).
- **Deepfire mod** — rulings only; spec sections all `(pending)`; nothing built; its relation
  to the existing `RM_RainbowPigment` is an open reconciliation question.
- **Burn number fix** (shallow 3 / deep 4, honest relabel) — ruled, not yet in XML.
- **Steam-devil species immunity** — ruled fix, not yet built (small C# change).
- **Custom steam-overlay art** (two tileable textures) — specced route, art not delivered;
  current look is vanilla fog material as a graceful fallback.
- **Margin cove placement, vent placement, geyser density mutator** on the actual live map —
  all explicitly deferred to bridge/world-authoring steps, not done.
- **The live review ("bedazzle") sitting** — staged (SCALD_REVIEW.rws exists) but not yet
  walked with the owner.
