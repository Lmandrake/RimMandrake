# CHECK inbox.

> 🔴 **W1–W9 BELOW ARE THE IMMEDIATE NEXT STEPS — owner's order, 2026-08-19.**
> *"Plan out a rather complete expansion of our live bridge capabilities centered around
> the worldmap… read/write/validate capabilities for all of them… implement them in a
> sensible grouping."* Nothing supersedes these. Work them in order; each is a shippable
> slice that leaves the bridge more capable than it found it.
>
> The element census and every API signature is
> `design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md` — read from 1.6 source through
> RimSage, NOT from memory. **Do not re-derive it and do not guess a signature.**
>
> 🔑 **CHECK holds the game.** The owner has granted start/stop/modify authority outright.
> No seat is asked before a reload. The game is DOWN as of 2026-08-19 20:15.

## W1 The minimal mod list, proven and timed
row:      bridge-1
spec:     578 mods is a ~25 min cold load and this work needs many. The 13-mod list is
          BUILT at `infrastructure/state/modlists/ModsConfig.MINIMAL.xml` and the swap
          tool is `src/RimMandrake/Utils/modlist_swap.py` (--status / --minimal / --restore,
          plan-only unless --apply; it archives the live file before every write).
          Contents and WHY each one is in it:
            harmony · core + all 5 expansions · VEF (Alpha Biomes' hard dep) ·
            brrainz.rimbridgeserver (THE BRIDGE - without it there is no bridge) ·
            7f.alienworlds + 7f.alienworlds.tidallylocked (the preset) ·
            sarg.alphabiomes (modded terrain under test) · oblitus.mylittleplanet.
          🔴 ODYSSEY IS NOT OPTIONAL: `Tile.Landmark` returns null when
          `!ModsConfig.OdysseyActive`, and PlanetLayer/Orbit are Odyssey types. A list
          without it silently has no landmarks and a different layer set.
          🔴 MLP AT SUBCOUNT 7 IS NOT OPTIONAL: it is what makes 21,872 tiles. Any other
          subcount shifts every tile ID and paints the wrong planet.
verify:   `modlist_swap.py --status` shows MINIMAL live; the game reaches the main menu;
          `Player.log` carries no missing-dependency error; `rimbridge/list_tools` answers.
criteria: the minimal list loads clean AND the wall-clock load time is MEASURED and
          written here. That number is what justifies the whole regime - if it is not
          dramatically under 25 min, say so and rethink rather than pressing on.
          🔴 `modlist_swap.py --restore --apply` before the owner plays. Leaving his
          machine on 13 mods is the one unacceptable outcome of this item.
state:    ready

## W2 Scaffold: split the tool file, prove build → deploy → load
row:      bridge-2
spec:     `JawaBenchTerrainTools.cs` is ONE flat class, 6,199 lines, 32 tools, and world
          tools are already scattered across three non-adjacent regions of it. Adding ~20
          more into that file makes it unmanageable.
          Add `partial` to the class at line 49 and put every new world tool in a sibling
          `JawaBenchWorldTools.cs`. ✅ The .csproj is `<Project Sdk="Microsoft.NET.Sdk">`
          with no explicit `<Compile>` items, so default globbing picks the new file up -
          VERIFIED, no csproj edit needed.
          Ship ONE trivial tool in it (`jawa/world_layers`: enumerate PlanetLayers, their
          defs and TilesCount) purely to prove the path end to end.
          Build: `python.exe src/RimMandrake/bridgetools/build.py --apply`
          ⚠️ hard-exits under WSL python3 - must be Windows `python.exe`.
          Deploys to `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\`
          - NOT under Mods\, not in ModsConfig. Needs the game DOWN (OS locks the assembly).
verify:   the deployed DLL's md5 differs from the pre-build one, and `rimbridge/list_tools`
          counts 33 `jawa/` names with `world_layers` among them.
criteria: `jawa/world_layers` RETURNS on a live world - 3 layers, surface TilesCount 21872
          on an MLP-7 world. Read the value back; a method returning is not evidence.
state:    ready

## W3 G1 + G7 — tile scalars, and the commit that makes any write visible
row:      bridge-3
spec:     The first complete vertical slice and the pattern every later group copies.
          TOOLS: `world_tile_get` (read scalars for a tile / range / list)
                 `world_tile_set` (batch write over ranges, ops-string convention)
                 `world_tile_import` (⭐ read a CSV FROM DISK by path - see below)
                 `world_tile_validate` (compare live grid against a CSV, report diffs)
                 `world_commit` (the invalidation recipe - G7)
          Fields: PrimaryBiome (property, get/set) · elevation · hilliness (ENUM, not a
          def) · temperature · rainfall · swampiness · pollution · feature.
          🔑 `world_commit` carries the recipe read out of vanilla's OWN debug tools:
            GetLayer<WorldDrawLayer_Terrain>(layer).RegenerateNow()
            GetLayer<WorldDrawLayer_Hills>(Surface).RegenerateNow()
            GetLayer<WorldDrawLayer_Landmarks>(Surface).RegenerateNow()
            layer.FastTileFinder.DirtyCache()
            Find.WorldPathGrid.RecalculateLayerPerceivedPathCosts(layer)
          It is SEPARATE from every writer on purpose: regenerating a draw layer per
          write would be pathological over 21,872 tiles, and this way the recipe lives
          in one place.
          ⭐ IMPORT TAKES A FILE PATH, NOT AN OPS STRING. The existing batch convention
          is a semicolon-separated `string ops` capped at MaxOps=4096; 21,872 tiles would
          be ~6 calls and a multi-megabyte socket payload. ⚠️ There is NO CSV-reading code
          anywhere in the companion today (no File.ReadAllLines, no StreamReader) - this
          is new capability, deliberately, and symmetric with `world_tile_export` which
          already writes one.
verify:   set a known tile's biome and elevation, then read them back RAW; screenshot the
          world map before and after `world_commit` and confirm the colour changed.
criteria: a scalar written through the tool is read back correctly from the RAW FIELD, AND
          the change is VISIBLE on the world map after `world_commit`. Both halves, or the
          item has not passed. 🔴 VALIDATORS MUST READ RAW FIELDS, never the cached
          properties - `HillinessLabel`, `MinTemperature`, `MaxTemperature` and `Biomes`
          are lazily cached with NO reset method anywhere in the codebase, so a validator
          built on them would confirm its own writes while the planet stayed wrong.
state:    ready

## W4 G2 — rivers and roads, including the removal vanilla cannot do
row:      bridge-4
spec:     TOOLS: `world_links_get` · `world_links_set` · `world_links_clear` ·
                 `world_links_import` · `world_links_validate`
          Links live on `SurfaceTile`, not `Tile`:
            struct RoadLink  { PlanetTile neighbor; RoadDef road; }
            struct RiverLink { PlanetTile neighbor; RiverDef river; }
            List<RoadLink> potentialRoads;  List<RiverLink> potentialRivers;  int riverDist;
          ADD via `WorldGrid.OverlayRoad(from,to,def)` / `OverlayRiver(from,to,def)` -
          they write BOTH endpoints symmetrically and no-op silently if either tile is
          not a SurfaceTile. `OverlayRiver` maintains riverDist = max(d, other.d + 1).
          Rivers MUST be laid mouth-first, then upstream.
          🔴 `world_links_clear` IS CAPABILITY VANILLA LACKS. Overlay* with null only
          logs ErrorOnce; lower-priority overlays are silently refused (road.priority,
          river.degradeThreshold). Removal and downgrade need direct edits to
          potentialRoads/potentialRivers on BOTH endpoints. Ours to build.
          🔴 `Roads` and `Rivers` are FILTERED VIEWS: `PrimaryBiome.allowRoads ?
          potentialRoads : null`. A biome with allowRoads=false HIDES links without
          deleting them. ⇒ validate against `potentialRivers`/`potentialRoads`; read
          `Rivers`/`Roads` only to answer "what does the player see". Both questions
          matter and the tools must answer them separately.
verify:   lay a 3-tile river, read both endpoints of each link, clear the middle segment,
          read back that it is gone from BOTH tiles.
criteria: add, downgrade and REMOVE all three demonstrated with read-back, and a river
          laid under a biome with allowRivers=false is proven present in potentialRivers
          while absent from Rivers. That asymmetry is the whole point of the item.
state:    ready

## W5 G3 — tile mutators and landmarks
row:      bridge-5
spec:     TOOLS: `world_mutators_get/set` · `world_landmarks_get/set`
          336 TileMutatorDef, 113 LandmarkDef.
          Mutators: use `Tile.AddMutator(def)` / `RemoveMutator(def)` and NEVER write
          `mutatorsNullable` directly - AddMutator resolves category conflicts, sorts by
          genOrder and calls `def.Worker?.OnAddedToTile(tile)`, which is where the side
          effects live.
          Landmarks: `Find.World.landmarks` is `Dictionary<PlanetTile, Landmark>` with
          `AddLandmark(def, tile, layer, forced)` / `RemoveLandmark(tile)`.
          `Landmark { LandmarkDef def; string name; bool isComboLandmark; }`.
          ⚠️ AddLandmark ALSO rolls the def's mutatorChances / comboLandmarkMutators onto
          the tile - adding a landmark is also a mutator write, and the tools must report it.
          🔴 ORDERING: `LandmarkDef.IsValidTile` REJECTS any tile that already holds a
          settlement (also impassable biome/hilliness, an existing landmark, and any
          TileMutatorDef with preventsLandmarks). ⇒ landmarks BEFORE settlements, always.
          This is also the route to the map-quality item's mutator defect: 4,831 `Coast`
          on non-water tiles, 2,116 of them deep inland, and 4 marine reefs incl. one on
          the nightside - all placed for the ORIGINAL sea layout.
verify:   add and remove a landmark on a known tile; confirm the rolled mutators appear
          and disappear with it.
criteria: mutators and landmarks both round-trip, AND the landmark-after-settlement
          rejection is OBSERVED rather than assumed - place a settlement, try to add a
          landmark on it, confirm the refusal.
state:    ready

## W6 G4 + G5 — named regions, and the world objects that carry our 72 holdings
row:      bridge-6
spec:     TOOLS: `world_features_get/set` · `world_objects_get/set` ·
                 `world_objects_add/remove` · `world_settlements_import`
          FEATURES (the named regions, 24 of ours): `Find.World.features.features` is
          `List<WorldFeature>`; a feature carries uniqueID, def, layer, name, drawCenter,
          drawAngle, maxDrawSizeInTiles.
          🔑 Tile membership is stored ON THE TILE (`Tile.feature`), not in the feature -
          assigning a region means writing `feature` on each member tile. ⚠️
          `WorldFeature.Tiles` is a FULL-GRID SCAN; do not call it in a loop over 24 regions.
          ⭐ `drawAngle` is never set by vanilla's generator - it stays 0. We get label
          placement control the base game does not use.
          WORLD OBJECTS: create is two steps -
            var wo = WorldObjectMaker.MakeWorldObject(def);   // def, ID, ticks, PostMake
            wo.Tile = tile; wo.SetFaction(f); ((Settlement)wo).Name = "...";
            Find.WorldObjects.Add(wo);                        // placement is separate
          🔴 A Settlement whose faction is NULL on load is DESTROYED with a warning. All
          72 holdings must carry a live faction before the owner saves or they vanish on
          his next load - and he would not find out until then.
          §12 rules these as OVERWRITE: re-`Tile` the objects vanilla already placed
          rather than deleting and remaking them.
verify:   rename a region and move its label; re-Tile one settlement and read back its
          tile, faction and name.
criteria: a region renamed and repositioned is VISIBLE on the world map, and a re-sited
          settlement survives a save→load round trip with its faction intact. The
          save→load half is not optional - it is the only thing that proves the null-faction
          trap was avoided.
state:    ready

## W7 G6 — world info and layers
row:      bridge-7
spec:     TOOLS: `world_info_get/set` (`world_layers` already shipped in W2).
          `Find.World.info`: name · planetCoverage · seedString · persistentRandomValue ·
          overallRainfall · overallTemperature · overallPopulation · landmarkDensity ·
          initialMapSize · List<FactionDef> factions · pollution.
          🔴 `overallPopulation` and `landmarkDensity` are NOT SCRIBED - they do not
          survive save/load. The tool must REFUSE to write them, or say plainly in its
          result that the value is session-only. Do not build a capability that quietly
          depends on them persisting.
          ⚠️ Planet layers come from the SCENARIO (`ScenPart_PlanetLayer` via
          `Find.Scenario.AllParts`), not from worldgen parameters. Read-only from us.
verify:   rename the planet, read it back, save, reload, read it back again.
criteria: the persistent fields survive a save→load and the two non-persistent ones are
          either refused or flagged. Both.
state:    ready

## W8 G8 — the in-engine sanity linter
row:      bridge-8
spec:     TOOL: `world_lint`. The owner's own sanity list, run IN the engine against the
          live grid rather than offline against arrays, so it sees what the game sees.
          Checks, from `ashkarr-map-quality-second-pass-8c31f7` item 8:
            stranded coasts · biomes without their climate · rivers that reach no sea ·
            single-tile islands · settlements unreachable by road · lush terrain off-river ·
            marine mutators on inland tiles · geometric shapes (perfect circles).
          🔑 The owner's RIVER MOUTHS ruling makes "reaches no sea" conditional: HIGH
          -accumulation trunks MUST reach a sea; low-accumulation rivers MAY die in
          playas or salt pans. The linter must know which is which or it will cry wolf
          on 44 legitimate rivers.
verify:   run it against the CURRENT unpainted world and confirm it reports the defects
          we already know are there - that is the calibration.
criteria: the linter finds the KNOWN defects on a world we have already diagnosed. A
          linter that passes a world we know is broken is the linter being wrong. Run it
          against the known-bad state FIRST; a clean sheet on the first run is a red flag,
          not a result.
state:    ready

## W9 The full 21,872-tile import, and the owner looks at his planet
row:      bridge-9
spec:     Everything above, used in anger, in the order §12 fixes:
            biome/scalars -> links (rivers mouth-first) -> mutators -> landmarks ->
            settlements -> features -> world_commit -> world_lint -> the owner LOOKS.
          Then he places the gravship and the six founders and SAVES. That save is v1's
          campaign start.
          🔴 PRECONDITIONS, folded in from the retired pin item - assert and REFUSE loudly:
            * `Find.WorldGrid.TilesCount == 21872`. MLP must be ACTIVE at subcount 7 with
              planetCoverage 1. Any other subcount shifts EVERY tile id and silently
              paints the wrong planet.
            * `Find.CurrentMap == null`. No map may be instantiated - repainting a planet
              underneath a live map is what killed two saves and ~2 cold loads on 2026-08-18.
            * the faction roster was hand-ticked per `WORLDGEN_FACTION_CHECKLIST.md`
              BEFORE the world was created. That pass is one-shot and unfixable afterwards.
          ⚠️ RESTORE THE FULL 578-MOD LIST FIRST. The frozen world the owner keeps must be
          built on his real stack, not the 13-mod test list. W1's minimal regime is for
          DEVELOPING the tools, never for building the shipped planet.
verify:   `world_lint` clean, then five tile IDs drawn from the CSV spot-checked against
          the biome the CSV claims.
criteria: the owner looks at the planet and does not immediately name a defect. NOT "the
          tool returned success". 🔑 Then compare it against
          `world/view/ASHKARR_WORLDMAP.biome.equirect.png` - every defect that has mattered
          in this work passed its numeric check while the picture was obviously wrong.
state:    ready

## C-V2 Park any v2 idea in design/V2_DREAMS.md yourself — no permission needed
row:      doctrine
spec:     Any idea for new content that is not v1 — including one a live session
          suggests — is appended to the END of `design/V2_DREAMS.md`. You have a
          standing right to append there directly: no permission, no routing through
          DECIDE, no queue item asking for it, no format and no field contract.
          Never queue v2 work.
verify:   read the header of `design/V2_DREAMS.md` once; it says the same thing.
criteria: EMPTY — that file is not a queue and nothing in it is scheduled.
state:    ready


## C17 At worldgen, untick the 21 factions that break the fiction
row:      10
spec:     `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` (`c269c6a`) — 21 untick / 6 keep, ratified, committed and UNSPENT. Executed by unticking factions on vanilla's Configure Factions page DURING the worldgen run; that page is seen ONCE and there is no fixing it afterwards without regenerating the world. Four rulings ride in the file header: R1 dangling refs, R2 Rebel Alliance stays suppressed, R3 vanilla `Empire` is a KEEP, R4 rough-outlander floor. There is no file we can write to suppress a faction — Faction Control's `density` is a CLUMPING RADIUS (`__result = dist < fd.Density;`), not a count, and the English key "setting to 0 disables the faction" is a pre-1.3 leftover. Before calling any missing faction a defect, grep `Jawa_Patches/` for its defName.
verify:   EMPTY
criteria: the generated world's faction roster matches the keep list. A quicktest map's roster PROVES NOTHING — a debug quicktest never visits the Configure Factions page, so every faction is present by default. State which map any census came from. Prior scale, from the deleted world: 53 factions across 107 settlements, of which the fiction-breakers held ~34.
state:    ⭐ v1 — and RESHAPED 2026-08-15 by the owner's worldgen ruling.
🔴 ruling: *"There is no auto worldgen we are building. The world will be user-made and
          frozen... True worldgen is OUT of any version, even v2."* Plus: *"(but designing
          worldgen by hand and design documents to guide that are in)"*.
          ⇒ **This item is NOT an automated worldgen task and must never be read as one.**
          It is the owner ticking boxes by hand, ONCE, on his single build. Nothing here
          is to be automated, and it must NOT be moved to v2 if it slips — v2 is not a
          parking space for worldgen.
⇒ MY HALF IS NOW A SAVE READ, NOT A LIVE RUN. The deliverable is a frozen savegame, so
          the roster can be verified **from the `.rws` after the fact** — no bridge, no
          second worldgen, no live window. That removes the one-shot pressure from MY
          side of it: if I miss the moment, the save still answers.
          ⛔ What is still one-shot is the OWNER's tick pass at the Configure Factions
          page. There is no second chance at that, and no file we can write to fix it.
          ⚠️ A quicktest map proves defs LOAD; it never proves which factions a generated
          world HOLDS. Do not let a quicktest roster stand in for this.
          One of only three items left in v1.
          🔴 Seen ONCE at the Configure Factions page and unfixable afterwards without
          regenerating. ⚠️ Only `Jawa_IndigenousTribes` carries `requiredCountAtGameStart`
          — the other seven default to 0, so a world generated without hand-ticking them
          contains NONE of them (BUILD, `seven-factions-have-no-required-count-9c4e17`).
          ✅ FIXED 2026-08-19 by BUILD (`7aa0543`): all seven now carry
          `requiredCountAtGameStart 1` and are deployed. See the
          `seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8` item below — it
          is MY confirmation half, and it is checked at the owner's worldgen run, which
          W9 gates on.


## C34 You hold the live bridge at all times — standing rule
row:      doctrine
spec:     Owner ruling 2026-08-14. `infrastructure/agents/CHECK.md` updated: the
          Live Bridge is yours with no window in which another seat holds it, and
          `infrastructure/state/status/game.json` is yours to keep true. Stamp it
          on every transition — game up, state change, game down. Fields:
          state (PLAYABLE|LOADING|DOWN) · by: CHECK · at: epoch · note · left · lease.
          Its stale `by: BRIDGE` is already corrected to CHECK; `at` is still
          1786744923 and the note still reads "BRIDGE idle" — restamp it yourself.
verify:   `python3 -c "import json;d=json.load(open('infrastructure/state/status/game.json'));print(d['by'],d['state'],d['at'])"`
          shows CHECK, a current state, and an `at` you wrote.
criteria: The board's GAME panel matches the real game across one up→down
          transition, and does not flag STALE while the process is resident.
state:    ✅ DONE — CLOSED 2026-08-19. The DOWN half finally had its chance: the owner took
          the game down, `tasklist.exe` confirmed no RimWorldWin64.exe resident, and I
          stamped `game.json` DOWN against that. That completes the one up→down transition
          the criterion asked for; it had never closed only because the game was up at the
          end of every prior session.
          ⚠️ Honest limit: I confirmed the state file and the process, not the rendered
          GAME panel — the board serves its state client-side and I could not read the
          panel text over curl. If the owner wants the panel itself witnessed, that is one
          screenshot on the next launch, not a reopened item.
          📌 Corrected on the way past: the note claimed 583 active mods. `activeMods` is
          **578**; the extra 5 were `<knownExpansions>` counted by a naive `grep -c '<li>'`
          — the documented overcount trap, hit by our own docs. So the JawaSeaShaper
          removal was 579 → 578.
resume:   The DOWN half is still unproven - the game was still up when this session
          ended. game.json currently reads LOADING from the 07:56 launch. Next seat:
          stamp it DOWN at shutdown and confirm the board's GAME panel follows, which
          is the whole remaining criterion. Everything else in this item is done: the
          file is mine, `by: CHECK`, and I restamped it through DOWN/LOADING/PLAYABLE
          transitions all session.

note:     2026-08-14 CHECK. Restamped: `by CHECK`, `at 1786770877` (was BRIDGE's
          1786744923), note no longer "BRIDGE idle", and `left` refreshed — the old
          one claimed "0 pawns" when the map now has Alex (PlayerColony), plus the
          moved thruster bank and the rewired power net. `verify:` PASSES
          (`CHECK PLAYABLE 1786770877`). **Not done:** the criteria needs one
          up→down transition and the game is still up, so the DOWN half is unproven.
          Stays `doing` until I stamp it down and the panel agrees.

## C40 Three Jawa fixes that only a load can prove
row:      9
spec:     Deployed but unproven, all needing a fresh load:
          (a) `291aebf` `MandrakeJawa` `canGenerateAsCombatant` false -> true.
              It was invented when the def was written and is not in the owner's
              .xtp. A Jawa faction could not generate a fighter.
          (b) `6ed888e` `JawaGeonosianFoundryHive` — its xenotype entry was gated
              on `btd.xenotyperemix.starwars`, which is now OFF, so the node was
              dropped and the faction's `xenotypeChances` was empty.
          (c) `5bb9f5c` B58 — starting gear and every JawaVoice rule named
              `OuterRim_Jawa`, a defName that stopped existing when Galactic
              Diversity was switched off.
verify:   PREDICTIONS, each a positive observation:
          (a) spawn `Jawa_Tribal_Scavenger` ×6 — all six are MandrakeJawa AND
              are armed fighters, not civilians.
          (b) spawn a Geonosian Foundry Hive pawn — it is a Geonosian, NOT a
              plain baseliner. An empty `xenotypeChances` yields baseliners and
              looks like a content gap rather than a dropped node.
          (c) a Jawa spawns WEARING the robe and hood (`guy762_Robes_jawa`,
              `guy762_JawaHood` — both from KotOR Weapons, which stays active),
              and a Jawa social interaction produces a Jawa voice line rather
              than a vanilla one.
          HOW IT LIES: (c)'s gear defs live in a mod we KEPT, so their presence
          in the dump proves nothing about whether our patch found its target —
          the pawn wearing them is the only evidence.
criteria: six armed Jawa; a Geonosian that is not a baseliner; a robed Jawa ~~that
          speaks in its own voice~~.
          ⛔ **THE VOICE CLAUSE IS STRUCK — owner, 2026-08-16.** *"Deprecate all future
          Jawa Voice checking. Those items are no longer to be tracked or pursued unless
          bugs are seen in game."* Not passed and not failed: **not graded**. C40 is
          scored on the armed-Jawa and Geonosian clauses and on the APPAREL half of (c)
          alone. The robe and hood still count; the voice line does not.
state:    🔴 COLLECTED 2026-08-15 — **(b) PASSES, (a) AND (c) FAIL.** Still v1.
result:   Collected live on the quicktest map. Evidence is the SAVE, not a screenshot.
          ✅ **(b) PASSES.** 4/4 pawns spawned into `Jawa_GeonosianFoundryHive` come out
             `RimMandrakeGeonosianVariants` / "Geonosian" — NOT baseliners. The dropped
             `btd.xenotyperemix.starwars`-gated node is fixed.
          ⚠️ **(a) HALF.** Xenotype is right: `Jawa_Tribal_Scavenger` ×6 in
             `Jawa_IndigenousTribes` came out **6/6 MandrakeJawa**.
             🔴 But they are **UNARMED** — `<equipment>` is EMPTY on all six in the
             parsed save. The criterion was "six ARMED Jawa"; the armed half fails.
             ⚠️ `canGenerateAsCombatant` and carrying a weapon are two different things —
             the flag can be true while the kind has no weaponTags. Do not assume
             `291aebf` failed; assume the kind arms nobody and check weaponTags.
             📌 Test setup matters: spawned into `faction=hostile` the same kind resolves
             to **Empire** and 2 of 6 came out `HBX_Highborn`/`Hussar`. That is the
             faction's own xenotypeSet doing its job, NOT a defect. Always name a Jawa
             faction when testing a Jawa kind.
          🔴 **(c) FAILS.** The six wear **generic tribal gear** — `Apparel_TribalA`,
             `VAE_Apparel_TribalPoncho`, `VFET_Apparel_TribalLight`, `Apparel_WarVeil` —
             and **NOT** `guy762_Robes_jawa` / `guy762_JawaHood`. B58's starting-gear
             rename did not take.
             ⚠️ **THE ITEM'S OWN "HOW IT LIES" WARNING FIRED, EXACTLY AS WRITTEN.** On
             screen they look robed and hooded and I nearly passed it — that is the
             XENOTYPE's body graphic, not apparel. Only the save settles it.
             The JawaVoice half of (c) is UNTESTED: it needs unpaused play, and SpeakUp
             does not fire at TPS 0.
          ⛔ **DEPRECATED 2026-08-16, owner. Do not chase this and do not re-open it.**
             Jawa Voice is no longer verified by anybody: no queue item, no load-round
             slot, no prediction owed. The ONLY route back in is a bug seen in normal
             play — a wrong or missing line the owner notices himself. Nobody goes
             looking. ⚠️ It is deprecated as a CHECK subject, not deleted as content:
             the mod stays deployed and active.
          🔑 2026-08-16 CHECK, game-down deploy window: **the JawaVoice patches were never
             in the game folder.** All 10 `Patches/JawaVoice_*.xml` read as drift against
             the deployed copy though the repo tree was clean at `5bb9f5c` (B58 itself).
             Deployed now. ⇒ the voice half of (c) was not failing, it was UNTESTABLE.
             Kept because it explains why the rules were absent, NOT as a reason to test
             them — the deprecation above outranks it. Says nothing about the apparel
             half, which lives in a mod that was already in sync and is still graded.
          📌 Bonus, and it contradicts C31: `Jawa_Tribal_Scavenger` is **NOT** discarded
             at load. It spawned 6/6 every time. C31's premise needs re-checking before
             anyone works it in v2.


## ashkarr-map-quality-second-pass-8c31f7
row:      2
spec:     ⛔ 2026-08-19 — SAVEGAME WRITING IS OUT. Every "run X" in this item names a
          script that has been DELETED; the map reaches the game over the live bridge
          (design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md §12). The DIAGNOSES and
          the owner's ORDER below are still the work; the tooling named is not. The
          current painter is `src/RimMandrake/Utils/ashkarr_paint.py` -> a CSV.

          Ash'karr is BUILT and committed (`world/WORLDMAP_gen.rws`, seed `pumpkin`,
          21,872 tiles, 12 factions all ours). This item is the owner's review list
          from 2026-08-17, in HIS order. Everything below is diagnosed, not guessed.

          🔑 THE TOOL THAT MAKES ALL OF IT POSSIBLE: `src/RimMandrake/Utils/world_graph.py`
          builds the tile adjacency graph (cached `world/world_graph.npz`, verified by
          the 12-pentagon test). Before it existed the painter could only make per-tile
          decisions, which is why the map looked like confetti. `world_shape.py` has
          despeckle / components / coastal / grow / roughen on top of it.

          THE PIPELINE (⛔ DELETED 2026-08-19 - savegame writing is out; the map reaches
          the game over the live bridge, ASHKARR_WORLD_DEFINITION.md §12. All five scripts
          are gone and `worldmap.py`'s write() now raises. Kept only so the old stage names
          in the notes below can be read):
            source -> paint_ashkarr -> populate_ashkarr -> name_ashkarr_regions
                   -> name_ashkarr_factions -> clean_ashkarr_hydrology
                   -> redo the world-object water mask -> load and read jawa/world_stats
          ⚠️ HOLE: no replacement exists yet for the populate / name-regions / name-factions
          / hydrology-prune stages. They must be re-specified as bridge importer work.

          REMAINING WORK, owner's order:
          1. ORDERING. Seas FIRST, then rivers, then the terrain that depends on rivers.
             Today rivers are inherited from worldgen and merely pruned. Author them:
             walk downhill neighbour-to-neighbour from mountain clusters to a sea, write
             the river arrays (they ARE arrays - see savegame-editing.md).
          2. LUSH TERRAIN ONLY ON RIVERS. Jungle/dense vegetation placed after rivers
             exist, on river tiles only. AB_TarPits adjacent to those. AB_FeraliskInfested
             Jungle only there.
          3. MUTATORS. 5,233 `Coast` of which 4,831 are on non-water tiles and 2,116 deep
             inland; 4 `VEE_CoralReef` incl. one at arc 177 on the nightside. They were
             placed for the ORIGINAL sea layout and the repaint moved the water. Editable:
             tileMutatorTilesDeflate (4B tile) + tileMutatorDefsDeflate (2B shortHash),
             38,877 entries, hashes resolve against DefDump/defs/TileMutatorDef.json.
             Recompute Coast from real adjacency; strip marine mutators inland. The
             ice-and-fire desert inside the extreme desert is almost certainly this too.
          4. ROADS. Fragmented in the OLD save because clean_ashkarr_hydrology (⛔ deleted
             2026-08-19) removed segments in water and nothing reconnected them - that was
             an ERROR, not decay. Lay roads
             LAST, as shortest paths over the graph between actual settlements. Plus a
             specific one: the Fuel Works -> the propane lakes, along the cold swirl where
             it reaches nearest the twilight.
          5. SHAPES. The Scald Spine is a perfect circle - use world_shape.roughen(). Only
             the crater itself may be round. No geometric shapes anywhere else.
          6. PLACEMENT. Ascendant Helix sited by DENSITY OF BIOLOGICAL HORROR around it
             (ocular forest, horror wastes) - that is what they came to study. At least
             TWO Deepwater Compact settlements on The Scald despite the Empire.
          7. HORROR WASTES lore is ruled (build_concepts, 2026-08-17): scattered small
             holdings in the rotting Twilight, RETREATING not spreading.
          8. SANITY PASS. The owner's words: evaluate "how sane is this planet?", not
             "did the script run". Check: stranded coasts, biomes without their climate,
             rivers that reach no sea, single-tile islands, settlements unreachable by road,
             lush terrain off-river.

          ✅ THE HOLE IS SMALLER THAN IT LOOKS (CHECK, 2026-08-19). Deleting the nine
          savegame writers did NOT take this item's tooling with it. Everything above is
          an OFFLINE authoring judgement and the offline painter is intact:
          `ashkarr_paint.py`, `ashkarr_settle.py` and `world_relief/hydro/biomes/settle.py`
          still emit the whole bundle (`world/ASHKARR_WORLDMAP_*`), and `worldview.py`
          still renders it. What died was only the tail - splicing that bundle into a
          `.rws`. That tail is now `worldpaint-live-bridge-route-9d41c7`: the same arrays,
          pushed into the live WorldGrid over the bridge. Settlement conversion and
          faction/region naming, which `populate_ashkarr.py` and the two `name_*` scripts
          used to do IN the save, are bundle fields today and become importer work.
          ⚠️ One thing genuinely cannot be re-measured by anything in the repo: the
          Blackstar Company faction swap (was `swap_faction_def.py`) and the final
          21,872-tile world-stats histogram. Treat both as historical, not as checks.

verify:   EMPTY
criteria: the owner looks at the planet and does not immediately name a defect.
state:    ready

owner ruling 2026-08-17, evening, after looking at 8 screenshots of the built world:

🔴 THE DIAGNOSIS, mine, accepted: the painter builds independent per-tile fields in
   PARALLEL and smooths the result. A planet is a CAUSAL CHAIN - elevation -> sea level
   -> drainage -> moisture -> vegetation -> settlement -> roads - and each stage must
   READ the one before it. Consequences visible on screen:
   * `RELIEF` is a per-region constant + jitter, so two neighbours differ by coin flip.
     There is no slope, so "downhill" is UNDEFINED and rivers are underivable.
   * The painter writes NO river. Every river on the OLD planet was a fossil of VANILLA's
     elevation field, truncated by clean_ashkarr_hydrology (⛔ deleted 2026-08-19) where it
     met the new water. That is why they started in flat sand and ended in open desert.
     🔑 The fix is unchanged and is now the bridge importer's job: author rivers ourselves.
   * Lush terrain is off-water because biome = region_of(arc, bearing, elev). Water is
     not an input to that function.
   * Anything defined by a RADIUS renders as a CIRCLE - the Scald disc, the Spine
     annulus, the Rust Cathedral bullseye. roughen() papers over it; the real fix is
     that a range must be a CONTOUR of a field, not the definition of a region.
   * "specks 2326 -> 237" was the wrong metric. It measures texture, not sense.

ORDER, ruled: 1 elevation field over the graph (plates + distance-to-boundary uplift +
   multi-octave noise) · 2 sea level = threshold on it · 3 rivers = priority-flood fill
   + steepest-descent routing + flow accumulation, graded into Creek/River/HugeRiver,
   arrays written by us · 4 rainfall field advected from seas + terminator ice, with
   orographic shadow · 5 biome = Whittaker f(temp, rainfall, elev), NOT a region
   predicate · 6 riparian pass, dilate rivers 1-2 and upgrade vegetation · 7 anisotropic
   blob growth along isotherms · 8 roads LAST, cost-weighted over the graph between real
   settlements · 9 offline sanity linter that must PASS before the owner ever looks.

Three owner answers, 2026-08-17:
   RIVER MOUTHS: BOTH. High-accumulation trunks MUST reach a sea; low-accumulation
     rivers MAY die in playas / salt pans. So "reaches no sea" is a defect only above
     the trunk threshold - the linter must know which.
   GREEN RIBBON: NILE-STYLE. A 1-2 tile lush band follows EVERY river wherever it goes,
     including through ExtremeDesert at the substellar point.
   REPAINT SCOPE: FULL REPAINT. ⛔ "from the pristine source ... passes re-run after"
     is DELETED 2026-08-19 - savegame writing is out and no source .rws is read or
     written. The RULING stands: nothing from the old world is preserved; the planet is
     derived end to end and delivered over the live bridge.

🔴 MAGENTA: FLAT_ONLY in paint_ashkarr.py (⛔ deleted 2026-08-19; the successor is
   `ashkarr_paint.py`) lists 3 biomes and the screenshots show many
   more (Nightspill, Gray Marches, South Marches, one on the nightside ice). Audit every
   biome x hilliness against the BiomesKit texture folders OFFLINE. This was catchable
   without a load and was not caught.

🔴 MAGENTA — SETTLED 2026-08-17, and my first two diagnoses were both wrong.
   CAUSE: `ZBiome_DesertOasis`, used in `dew_belt` (52 < arc < 92 around bearing 178 -
   exactly the twilight band where every magenta patch sits). It has a Forest/ texture
   set and NO Hills/ folder, and it was simply absent from `FLAT_ONLY`. The clamp at
   paint_ashkarr.py:334 was working the whole time (⛔ that file is deleted, so the line
   reference is unresolvable; the clamp logic moved to `ashkarr_paint.py`);
   `hh + (1 if random() < 0.18)`
   promotes ~18% of its tiles off flat, and those are the patches. FIXED.
   ⛔ REFUTED, do not re-raise: "missing _Snowy variants cause it". The snow suffix
   fires ONLY from per-biome `*SnowyBelow` temperature fields on
   ReGrowthCore.BiomesKitControl, and Alpha Biomes / More Vanilla Biomes / Advanced
   Biomes declare NONE - so their _SemiSnowy/_Snowy/_VerySnowy art is dead weight and
   can never be requested. Proof by correlation: RG_BoilingForest sets zero snow
   fields, ships zero snow art, and has never gone magenta.
   🔑 There is no Mountains/ folder anywhere - Mountains and Impassable live INSIDE
   Hills/. The Hills-vs-Mountains split I worried about does not exist.
   LATENT, not live: ExtremeDesert declares mountainsSnowyBelow -5 and ships only
   _SemiSnowy; Scarlands declares mountainsFullySnowyBelow -21 and ships no
   _FullySnowy. Both are dayside-hot on Ash'karr today. Recorded as COLD_FLAT.
   MOD SETTING: ReGrowth 2 -> General -> "Enable world map beautification"
   (`RG_WorldMapBeautificationProject`, default True, never toggled here - its store
   `Config/ModSettingsFrameworkMod_Settings.xml` does not exist). Turning it OFF does
   fix magenta, by removing the BiomesKitControl extensions entirely - i.e. it deletes
   every hill/forest/mountain sprite from the world map. It is a sledgehammer; the
   one-line FLAT_ONLY fix is the right tool.

🔑 RIVER/ROAD ADJACENCY - HOW FAR IT IS SOLVED, 2026-08-18. Read this before trying again.
   FORMAT: three parallel arrays; each entry is (origin tile uint32, adjacency byte,
   def shortHash uint16). Origins are SORTED ASCENDING and REPEAT - a tile carries one
   entry per link, so a through-tile appears twice.
   ✅ PROVED: the adjacency byte indexes an ANGULAR neighbour ordering. Evidence, and
   it is decisive: over the 67 river tiles and 163 road tiles that carry exactly two
   links, the slot DIFFERENCE is only ever 2 or 3 - never 0, 1, 4 or 5. A river passing
   through a tile bends 120 or 180 degrees and never doubles back at 60. Only an
   angular ordering makes a slot difference encode a turn angle. River 58.2% straight,
   road 67.5%, against 33.3% for a uniform distribution.
   ✅ PROVED: the rotation offset is PER-TILE, not global. Rivers and roads score their
   best on DIFFERENT (winding, rotation) pairs, and no pair beats ~0.27 reciprocity.
   ⛔ REFUTED, do not repeat: scoring candidate orderings by "is the implied target
   also a river tile". 27% of river origins have NO river neighbour, so the test tops
   out near chance whatever the mapping. It cost two rounds.
   ⛔ Distance-order and ID-order were both tried. Neither is it.
   ⇒ WHAT IS STILL NEEDED: one number per tile - which neighbour is slot 0, plus the
   winding. 21,872 of them. Only the engine has it. The route is a companion [Tool]
   that dumps Find.WorldGrid.GetTileNeighbors order per tile, which needs the game DOWN
   to deploy because the OS locks the assembly. `Outputs\Adjacent Distance Between
   Layer Tiles` exists as a debug action and RAN, but its output went to a window, not
   to Player.log or jawa/drain_log - if it prints per-tile distances IN neighbour order
   those distances are a fingerprint that recovers the permutation without any new code.
   Try reading it via rimworld/get_ui_state before building the DLL.

## dll-capability-roster-and-cull-a41c02
row:      tooling
spec:     Owner, 2026-08-18, for the next token refresh. Produce the FULL roster of
          RimWorld functionality we could implement as companion [Tool] methods in
          JawaBench.BridgeTools - not what is built, what is POSSIBLE - then have the
          owner select down from it for the next version of the DLL.
          The roster is the deliverable; the cull is the owner's, not ours.
verify:   EMPTY
criteria: EMPTY - owner sets the pass condition when he picks from the roster.
state:    ready

## cherrypick-settings-actually-load-3b71ae
row:      10
spec:     The Cherry Picker settings file has never loaded. Two synthesised keys,
          `ThingDef/<nodef#10>` and `<nodef#11>`, put a raw `<` in the XML; the game
          logged `Caught exception while loading mod settings data for 3521312241.
          Generating fresh settings.` and discarded ALL 1,308 cuts. Repaired offline:
          1,306 keys, well-formed, written to the live config and the tracked freeze.
verify:   done offline — output parses, and is the ratified list minus exactly those
          two lines (`diff <(grep -v nodef <freeze>) <new>` empty). See the closing
          commit.
          ⭐ Owner answered the two open questions 2026-08-19 and both are applied:
          all 11 recorded weapon/apparel cuts went in WITH the 4 turret buildings whose
          guns they are, and 28 of the 30 recorded biome cuts went in. `AridShrubland`
          and `Lake` are held out by name — 2,300 tiles of the frozen Ash'karr map are
          those two biomes and BiomeDef is really DELETED, not neutered. Final: **1,349**.
criteria: on the NEXT load, `Player.log` carries NO `mod settings data for 3521312241`
          exception, and a cut def is actually gone — pick one that resolves in the
          dump and is not from a dead mod, e.g. `ThingDef/Gun_BlastCharge`, and confirm
          it no longer appears in game. ⚠️ Cherry Picker NEUTERS ThingDef/PawnKindDef/
          IncidentDef in place rather than deleting them, so check the trade/craft/spawn
          lists, not the def database.
state:    ready

## alien-worlds-preset-is-edited-inside-a-steam-folder-8d40f3
row:      —
spec:     `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3626210061\Worldbuilder\TidallyLocked\Preset.xml`
          has been hand-edited on this machine (mtime 18:54 against 18:45 for its
          sibling assets) and now carries our eight `Jawa_*` faction counts,
          `planetCoverage 1` and `saveGenerationParameters True`. It holds generation
          PARAMETERS only — no per-tile data — so it does not deliver the map. But it is
          real authored work sitting in a directory **Steam owns and will silently
          revert on any update to that mod.**
verify:   `ls -l` the file against its siblings; confirm the `Jawa_*` faction entries
          are present.
criteria: the faction roster and coverage settings live somewhere in the repo, and the
          workshop copy is reproducible from it rather than being the only copy.
state:    ✅ DONE 2026-08-19 (f427f3a). `design/Jawa/worldbuilding/TidallyLocked_Preset.xml`
          is the repo copy, annotated at the top with its deploy path and why it matters.
          Read back from the copy: 15 `Jawa_*` lines, `myLittlePlanetSubcount 7`,
          `planetCoverage 1` — which independently cross-confirms the pin recorded in
          `worldmap-import-is-pinned-to-mlp-subcount-7-4c9e1a`. Steam can now revert the
          workshop file without costing us the authoring.

## seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8
row:      9
spec:     `<requiredCountAtGameStart>1</requiredCountAtGameStart>` added to the seven
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/` defs that lacked it — Jawa_HuttCartel ·
          Jawa_Junkers · Jawa_DeepwaterCompact · Jawa_GeonosianFoundryHive ·
          Jawa_WildsteamClan · Jawa_AscendantHelix · Jawa_FreeDroidEnclaves.
          `JawaTribes.xml` untouched (already 1, max 2). Deployed to the game copy.
verify:   done offline — `grep -c requiredCountAtGameStart …/FactionDefs/*.xml` = 1 on all
          eight; `validate_patch.py --defs` 0 errors, 8 files. The one warning is a
          pre-existing `iconPath` note on JawaHuttCartel, unrelated.
criteria: on the Configure Factions page at the owner's worldgen run, all eight Jawa
          factions arrive at a count of at least 1 without him touching a counter.
state:    ready
