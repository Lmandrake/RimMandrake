<!-- status: draft — BENCH roster for FOUNDRY design iteration, 2026-08-31. Frame: PROMISES + WHISPERS, one of each per tile (whisper rolled). Engine: rimplace; naming: framework RimMandrake, SW content RimStarWars, Ash'karr content RimUtinni -->
# Structure Injection Roster — Promises & Whispers

_The owner's architecture, 2026-08-31: our own mutators as visible map markers
we answer with injected Lua content, plus hidden surprise injections by biome
and territory — "perhaps there should always be one of each." This roster is
the content list FOUNDRY iterates designs against._

## 0. Inventory (MEASURED, frozen dump `1742630eb6253187`)

- **rimplace**: 2 Lua templates exist (`design/Jawa/templates/dwelling.lua`,
  `nursery.lua`); the engine lints, renders, verifies defNames against the
  dump, and compiles to `jawa/*` bridge calls. Sandboxed, seeded, selftested.
- **mapsynth**: gravship-hull pipeline plus ONE authored terrain design
  (`authored/coastal_mesa` with before/after renders + improvement loop) —
  the render-sheet iteration pattern to reuse.
- **Vocabulary in-stack**: 113 LandmarkDefs (45 Odyssey · 59 VEE · 6 Alpha
  Biomes · 2 SW sarlacc · 1 van.beasts) and 336 TileMutatorDefs (82 Odyssey ·
  144 VEE · 48 AB · 44 Geological Landforms · 9 SW · 5 Core). Sacred-sites
  flagged ~46 legal-but-unused landmarks as free real estate.
- **The shipped precedent**: `sw_Sarlacc` (LandmarkDef, world-visible) +
  `sw_SarlaccLair` (TileMutatorDef, mapgen) is already a working
  promise→responder pair in the stack. We are generalizing a pattern the SW
  collection proves.

## 0b. The responder mechanism (VERIFIED in source)

`TileMutatorDef` carries `extraGenSteps` / `preventGenSteps`
(TileMutatorDef.cs:26–28); `MapGenerator.cs:155–175` concatenates every
mutator's extraGenSteps into the map's genstep pipeline and honors prevents.
**So the whole architecture is def-driven, no Harmony:** our mutator +
`GenStepDef` = the injection hook. `GenStep_RandomSelector`
(Verse, weighted options) gives whisper variety natively. Landmarks are the
world-visible face; a LandmarkDef can carry our mutator so the icon IS the
promise. **The one NEW piece of C#:** a `GenStep_RimplacePlan` that replays a
compiled rimplace BuildPlan at mapgen (rimplace today emits live bridge
calls; mapgen needs the same plan executed engine-side) — flagged
VERIFY-at-build for terrain/roof ordering.

## 1. The two channels, and the laws

- **PROMISE** — world-visible (landmark icon + inspect string). A promise is
  a CONTRACT: the player chose this tile expecting it. **Coverage law
  (lint-enforced, zero-rows lesson): no promise def ships without a
  registered responder genstep — a promise that generates nothing is a bug
  class, not a shrug.** On the fixed map, promises are PLACED by the owner
  (Ash'karr is hand-authored; nothing rolls at worldgen).
- **WHISPER** — invisible from orbit; rolled at map generation from the
  territory table (god-country per `sacred_sites_pass_1.md` × biome).
  **Trust law: a whisper announces itself in the landing letter's last beat
  (god-voiced, F9-signed) — a surprise is a reveal, never a silent gotcha.**
  Ishko's authored-nothing is a legal whisper, rare, and the letter still
  speaks ("Nothing is here. He is quite sure you understand how rare that
  is.").
- **The one-of-each rhythm (owner's instinct, adopted):** every landable
  tile carries exactly ONE promise (authored) and rolls exactly ONE whisper.
  The pair is the tile's story: what you came for, and what the country
  adds.

## 2. PROMISES (22) — visible from orbit, responder-backed

Format: **Name** · gating · from orbit · injection · voice · stakes.

1. **The Moisture Farm** (RSW) · Desert/AridShrubland · vaporator field icon ·
   NEW rimplace `moisture_farm.lua`: vaporator ring, cistern hut, walled yard ·
   Oomo · water+power salvage; squatters or kin may hold it.
2. **The Sarlacc** (RSW, EXISTS) · adopt `sw_Sarlacc`/`sw_SarlaccLair` as-is,
   add our responder polish (warning totems ring the pit — someone knew) ·
   Sh'kaar · the mouth in the sand; feed it or fence it.
3. **The Krayt Graveyard** (RSW) · ExtremeDesert · bone-crescent icon · NEW:
   rib-cage terrain set + pearl-bearing skulls · Sh'kaar · pearls worth a
   fortune; the owner of the bones still patrols.
4. **The Podracer Wreck** (RSW) · Dune Sea band · smoke-plume icon · NEW small:
   scattered engine pods, one intact · Ta'Baa · engines are engines; first
   caravan there wins.
5. **The Junkers' Field** (RUT) · sacred-sites' Rekko country · debris-field
   icon (maps existing `Ruins` reads) · NEW: gravship debris arcs via
   coastal_mesa-style authored pass · Rekko · dense scrap; the old reasons
   come calling.
6. **The Dead Crawler** (RSW) · any desert · crawler-silhouette icon · NEW
   flagship rimplace: a fallen sandcrawler hull, three interior decks ·
   Rekko+Mob'Unloo · a dungeon-lite full of sleeping hands.
7. **The Signal Mast** (RM, reskin `AncientUplink`) · anywhere · mast icon ·
   existing mutator + our comms-console room · Ohm · working uplink; using it
   raises Visibility.
8. **The Monument** (RUT) · Ozzik's monument reads · colossus icon · NEW:
   half-buried statue + plaza, high-beauty tiles · Ozzik · pride on claiming
   it; the pride-meter knows.
9. **The Rakatan Trace** (RUT) · vault-adjacent tiles (dungeons arc) ·
   angular-glyph icon · NEW: a sealed door and forecourt only — the vault
   teaser · Narrator · nothing opens yet; everything is implied.
10. **The Oasis Shrine** (RUT) · `Oasis` mutator tiles · palm+stone icon ·
    NEW small: spring-side shrine, offering bowls · Oomo · fertility boon
    ground; desecration is remembered.
11. **The Kiln** (RUT, contested per sacred-sites) · geothermal · furnace
    icon · NEW: geothermal works, half-alive · Ohm vs Sh'kaar argue it ·
    free power that feeds the escalation meter.
12. **The Hunting Lodge** (RSW) · shrub/grass bands · lodge icon · NEW
    rimplace: trophy hall, kennels, cold room · Ishko · taming gear and
    trophies; something still uses the kennels.
13. **The Toll Gap** (RUT) · road tiles through cliffs · gate icon · NEW:
    canyon chokepoint with toll house · Mob'Unloo · a defensible gap; ghosts
    of unpaid tolls.
14. **The Dead Beacon** (RUT) · terminator band · dark-lighthouse icon ·
    NEW: light tower, cold; relighting it is a CHOICE · Ishko vs Sh'kaar ·
    light the dark and see what answers.
15. **The Bantha Graveyard** (RSW) · herd routes · ivory-scatter icon · NEW
    terrain-scatter set · Oomo · ivory and calm; herds return in season —
    hunt or shepherd.
16. **The Glass Sea** (RUT) · Sh'kaar country arc <74 · mirror-flat icon ·
    NEW terrain: fused sand, brutal glare · Sh'kaar · solar output soars;
    so does exposure.
17. **The Ashfall Battery** (RUT) · `AncientLaunchSite` reads (sacred-sites
    worked example) · gantry icon · existing mutator + our fuel-farm room ·
    Ta'Baa · launch fuel components; the Ashfall Road's origin story.
18. **The Mynock Roost** (RSW) · cave-mouth tiles · winged-swarm icon · NEW
    light: cave mouth + roost combs · Zizzik · power cables are food here.
19. **The Cistern** (RUT) · terminator band · well icon · NEW rimplace:
    buried waterworks, pump room, dark stair · Oomo · water security; the
    stair goes further down than the pumps need.
20. **The Broken Ring** (RUT) · anywhere, rare · arc-of-metal icon · NEW:
    crashed orbital ring segment, rich tech scrap · Zizzik · everything
    salvaged from it carries his spark for a season.
21. **The Imperial Waystation** (RUT) · road/`Empire` reads · prefab icon ·
    NEW rimplace: modular imperial prefab, intact stores · Ozzik · loot and
    statecraft hooks; pursuit heat rises on looting.
22. **The Homestead** (RM) · any temperate-read tile · hut icon · REUSE
    `dwelling.lua`+`nursery.lua` today (the two shipped templates ARE the
    first responder content) · Mob'Unloo · a fair squat or a fair purchase.

## 3. WHISPERS (22) — rolled by territory, announced on landing

1. **Something Buried** (Rekko, any) · a working machine under the sand near
   the center; mining reveals it · "Dig gently. It is sleeping, not dead."
2. **The Listening Dark** (Ishko, nightside) · pre-connected cave network
   under the map (Hollow/Caves mutators) · free hidden base; something
   already listens in it.
3. **Old Reasons** (Rekko→Ishko, junker reads) · the salvage is claimed;
   claimants arrive in N days · the theft rule made terrain.
4. **The Wrong Spark** (Zizzik, broken places) · one machine the colony
   builds here will glitch — sometimes in your favor · his country, his
   rules.
5. **Soft Ground** (Ta'Baa/Ishko, dunes) · natural sink-cells that behave as
   unrated pit covers (pit-trap synergy; mass rules apply) · free kill-zone;
   also under YOUR paths.
6. **The Passing Herd** (Oomo, herd routes) · a migration crosses mid-stay —
   meat, taming window, tramplings · the family walks past; take or shepherd.
7. **The Sun's Anvil** (Sh'kaar, arc <74) · heat events run hotter; solar
   runs stronger · his country taxes and pays in the same coin.
8. **The Debtor's Cache** (Mob'Unloo, roads) · buried strongbox + ledger
   page; taking it books a debt event later · nothing is free; everything is
   priced.
9. **The Glimmer Field** (terminator) · bioluminescent flora draws game by
   night — and what hunts game · light as bait, both ways.
10. **The Hollow Below** (vault-adjacent) · a cavern under the map with a
    sealed door (dungeons feed) · the knock comes on the third night.
11. **Static Ghosts** (Ohm country) · holograms flicker at night — old crew
    scenes, lore fragments · the machines remember being watched.
12. **Never Was** (Ishko, RARE) · genuinely nothing injected · "Nothing is
    here. Consider how rare that is, and who arranged it."
13. **The Egg Sands** (Oomo, warm dunes) · a buried clutch hatches mid-stay
    — brood to tame or repel · the ground was a nursery first.
14. **The Feud** (any wild band) · two beast populations spawn hostile to
    each other · Ta'Baa doctrine: let them ruin each other, then walk in.
15. **Quicksand Veins** (`AB_QuicksandPits` reads) · mass-triggered natural
    hazard cells · the desert already knows the pit doctrine.
16. **The Prospector's Bones** (Mob'Unloo/Rekko) · a corpse, a claim map to
    a named other tile (chain hook) · the ledger outlives the debtor.
17. **Iron Rain** (Zizzik/Sh'kaar, ring-adjacent) · periodic small debris
    falls all stay — free steel, real danger · the sky sheds.
18. **The Choir Wind** (Ozzik, monument reads) · wind through the ruins
    sings at dusk; mood up, grief pressure up · beauty with a hook in it.
19. **The Mirage Twin** (Sh'kaar) · a structure visible at map edge that
    resolves to nothing up close (scam-prop tech from the trap spec) · the
    sun lies at noon.
20. **The Rootstock** (Oomo, dry lakes) · dormant seedbank blooms after any
    rain/water event · the desert holds its breath, not its death.
21. **The Sleeper's Knock** (RUT, Rakatan traces) · rhythmic knocking from
    below on a timer; stops if answered wrongly · the vault arc's ambient
    dread, spent one tile early.
22. **The Sarlacc Sign** (RSW, sarlacc-adjacent) · edge-of-map burrow signs;
    small livestock vanish near edges · something patient owns the borders.

## 4. Composition & lint rules

1. **One promise, one whisper, per landable tile.** Promise authored on THE
   map (owner's pen); whisper rolled at mapgen from the territory table.
2. **Coverage law**: lint refuses any promise def without a registered
   responder genstep AND any territory with an empty whisper table. Assert
   against the tile inventory, not the def list (zero-rows lesson).
3. **Placement negotiation**: responder gensteps run AFTER terrain mutators,
   BEFORE scatter steps; a promise structure refuses cells inside another
   injection's footprint (`ctx:refuse` is a result — log, shrink, or move).
4. **Whisper weights are god-country rows** in one table the engine and the
   judgement letter both read; the landing letter's last beat names the
   whisper in its god's register.
5. **Naming**: framework defs `RM_` (`mandrake.rm.injections`); SW content
   `RSW_`; Ash'karr `RUT_`. The lint from `naming_lint.py` applies from
   birth.

## 5. FOUNDRY iteration protocol

1. Claim a batch of roster rows (3–5); one item per batch.
2. Author each as a rimplace template (`design/Jawa/templates/<name>.lua`) —
   `lint` → `render` → `verify` (defNames vs live dump) before any review.
3. Render a SHEET per batch (mapsynth's coastal_mesa before/after pattern;
   review-sheets rules if the owner curates) — the owner picks/redlines by
   LOOKING.
4. Improvements loop in the template file; the render is disposable, the
   `.lua` is the artifact. Seeded RNG: same seed, same house — diffs are
   honest.
5. A row ships when: template verified, responder genstep registered,
   whisper/promise letter text exists in the god's register (narrator corpus
   conventions), and the coverage lint passes.
