# Temples of several faiths: ruined ones as mutators, living ones with their people

Item `TEMPLE_RUINS_DESIGN_SEVERAL_FAITHS` · status: DESIGN, nothing built · 2026-11-01, relentless builder (gen 1).

**What the owner asked for**, 2026-10-19: *"Add ruined temples in various Star Wars-esque themes as
mutators, and Inhabited contents that feature actual religious people living in a temple that you
can find."* He picked this on the derelict-study card, choosing "Ruined temples as mutators +
Inhabited religious residents" over "Another mutator", "Drop it, Rust Cathedral covers it" and
"Warscar covers it". The item's own brief: *use vanilla/Odyssey ruin machinery, style-category
symbols*, and start from `design/RimMandrake/derelict_structures_lessons_2026-10-19.md`.

This answers that study's §8 question 1 ("Desert temple: which kind?"): **several kinds**. Two are canon
Force faiths (RSW tier), and the rest belong to this world (RUT) or to no franchise (RM).

## 1. The decisions in one table

| question | decision | why |
|---|---|---|
| How is a ruined temple placed? | A `TileMutatorDef` whose `extraGenSteps` runs a KCSG temple layout (`KCSG.GenStep_CustomStructureGen`). This is the hook every `StructureInjectionsRUT` structure already uses | It needs no C#, it is proven four times in our tree, and the mutator layer is what he asked for |
| Where does each faith get its look? | One Ideology `StyleCategoryDef` per faith, set as `styleCategory` on every KCSG `SymbolDef` in that temple. Vanilla `Pew`, `Column`, `Altar_Medium`, `Ideogram`, `Lectern`, `Sarcophagus`, `Brazier` and `TorchLamp` are then re-drawn by the kit | This is the item's "style-category symbols". KCSG supports the field (it is in `KCSG.dll`, and Alpha Memes uses it on 15 symbols), but **no symbol of ours sets it yet** |
| Why not Odyssey's procedural ruin generator (`TileMutatorWorker_AncientStructure` + `StructureLayoutDef` + `LayoutWorker_AncientRuins`)? | Not for the sanctum. It is optional later, for a monastery's outbuildings | Measured 2026-11-01: vanilla `PrefabDef`, `LayoutRoomDef` and `StructureLayoutDef` carry **no style field**, so a procedurally built room cannot wear a faith kit without a C# restyle GenStep. The derelict study also sends the first use of that generator to `RM_DerelictGeneLab`, which is not built. A temple is read by its plan (a processional axis, the sanctum at the end), and the plan is what a generator randomises away |
| How do ruins vary? | Each faith has a `gen_temple_layout.py` generator, the pattern of `gen_spire_layout.py`. It writes 3 variants per faith with different collapse, chosen by KCSG `chooseFromlayouts`. The ruin damage is baked into the drawing: missing wall runs, `Filth_RubbleBuilding`, fallen columns | Variety with no runtime randomness of our own, and a reviewer can read every drawing |
| How do living temples get their people? | Through **our own `Inhabited` mod**. The mutator `RUT_InhabitedTemple_<Faith>` lays out an *intact* temple and also runs `Inhabited_Cast` and `RM_InhabitedStock`. A `WorldObject_Inhabited` hand-placed on the tile carries an `InhabitedPlaceDef` and its cast | That is the PLACE+CAST model Inhabited already ships (`design/Jawa/bridge/INHABITED_DESIGN.md` §2: *"the mutator places the set; Inhabited places the company"*). There is no new machinery here |
| Whose faith do the residents hold? | **Only faiths a living faction already holds.** Every temple cast is drawn from an existing faction's cast roster (`CastRoster_<FACTION>`) | Each ideoligion is generated once, when the world is created, and frozen into the shipped save (`design/Jawa/worldbuilding/PRE_WORLDGEN_GATE.md`). A faith that no faction holds would need a new faction before the freeze. The canon Force orders are gone in this era anyway, so they appear as ruins only |
| How do they reach the map? | **By hand, at the one painting**: no `chanceOnNonLandmarkTile`, and no rolls | There is no worldgen of any kind, and the planet is painted once at the end. A temple on 0 tiles today is the expected state |

## 2. The ruined temples: five faiths

All five follow the derelict study's plan: **a processional axis through rooms of rising sanctity**.
The gate, the doors and the holiest object sit on one line, so the plan reads from outside. Sizes
are the drawn footprint. Every one needs `Desert`/`ExtremeDesert`-family biomes or a stated reason.

| defName | tier | the faith, as the ruin tells it | plan (rooms, in order) | kit (`StyleCategoryDef`) and placeholder until art lands | reason to enter |
|---|---|---|---|---|---|
| `RSW_SithTombRuin` | RSW (canon: the Sith tombs of the Valley of the Dark Lords) | a dead Sith lord sealed in with his servants. Fits the existing Sith line, whose living adepts lurk in `RM_Abyss` (`design/RimMandrake/sith_line_design.md`) | gate colossi → hall of statues → sunken burial chamber with a `Sarcophagus` on the axis | `RSW_SithTomb` (red stone, spiked lintels); placeholder vanilla `Spikecore` | a reliquary loot roller in the sarcophagus room, plus sleepers that wake if disturbed (the VaultDungeons pattern), never a timer |
| `RSW_JediEnclaveRuin` | RSW (canon: a Jedi enclave, a meditation retreat of the old Order) | an order that left, or was purged. Nothing is defiled: it is swept bare, and the meditation ring still faces the sunrise | cloister court → refectory and cells → domed meditation ring with a lectern | `RSW_JediEnclave` (sandstone, cream and blue); placeholder vanilla `Rustic` | a holocron-shaped skill book on the lectern (one vanilla `Book`-class item, no Force mechanics), plus quiet. The reward is the room: a ready ritual room for an Ideology player |
| `RUT_TempleOfTheNineRuin` | RUT (this world) | the great temple of the Jawa's own nine gods from before the fall: **Ozzik the Shamed's** *"memory that we were once great"*, built in stone. The Salvation's own description names Ozzik *"a trap, and we love him anyway"* | crown court → nine niches (one per god, each a vanilla `Altar_Small` re-drawn) → the throne of the tarnished crown | `RUT_NinefoldAncient` (sandstone with copper inlay); placeholder vanilla `Totemic` | it is **the player's own faith's ruin**. The nine niches are a natural home for the Ninefold rite's favour (`src/RimUtinni/Rites`); visiting is a pilgrimage, not a raid |
| `RUT_SunCourtRuin` | RUT | an open-air court of Sh'kaar the All-Searing, the sun the Jawa fear. Unroofed **on purpose**: at noon the gnomon throws no shade at all | ring wall → open court (no roof anywhere) → gnomon dais | `RUT_SunCourt` (bleached limestone, gold leaf); placeholder vanilla `Horaxian` | a sight, plus Direct Sun used as level design: crossing the court at noon is a real cost (the one sun model; no new heat). A shaded side-vault holds the loot |
| `RM_StarSeerObservatoryRuin` | RM (franchise-free, invented, per the Q11a ruling) | a star-reading sect that charted the sky and vanished. It has no franchise ties and can travel to any future campaign | stair approach → orrery hall → roofless sighting platform | `RM_StarSeer` (dark slate, silver); placeholder vanilla `Techist` | a star-chart curiosity item (sellable art), and the platform as a photogenic landmark |

**The fifth slot is deliberate.** The derelict study's question 1 offered (a) a canon Sith tomb,
(b) an invented Ash'karr temple or (c) none. "Several faiths" means (a) and (b) both. One RM ruin
proves the kit pattern carries outside the franchise.

**What each temple ships** (per faith; numbers are the plan, not measurements):
- 1 `TileMutatorDef`, with `label`, a `description` written in that faith's voice, and `extraGenSteps` → 1 `GenStepDef`
  (`KCSG.GenStep_CustomStructureGen`) → 3 `KCSG.StructureLayoutDef` variants.
- About 12 `KCSG.SymbolDef`s, each with `<styleCategory>` and a stone `<stuff>`.
- 1 `StyleCategoryDef` re-drawing about 10 vanilla thingDefs (wall, column, door, pew, altar, lectern
  or sarcophagus, brazier, torch, ideogram, table): **about 10 sprites per faith, 50 in all**, through
  `art install` and judged against the art brief. Until a sprite lands, the placeholder is the
  named vanilla category, so **every temple can ship and be looked at on day one with zero art**.
- About 1 junk dressing thing per faith (a broken statue, a fallen column), `Graphic_Random`.
  It deconstructs to the faith's stone.

## 3. The living temples: four faiths that still have people

Each living temple is the same building **intact**, on a tile with a `WorldObject_Inhabited`.
The cast is that faction's own people. The faith casting rule (INHABITED_DESIGN §5.9, *"cast the
faith, not the industry"*) does most of the writing: a temple keeper of the Green Oath and one of
the Salvation are not the same man in a different robe.

| mutator | faction (cast roster) | its faith | the temple | sustenance, present and not produced (§2.1 of the Inhabited design) | fate |
|---|---|---|---|---|---|
| `RUT_InhabitedTemple_Salvation` | Jawa Trade Moot (`JAWA`) | The Salvation | a **heap-shrine of Rekko of the Second Hand**: repaired machines on plinths, each one *"a sleeping hand, owed its waking"* | offerings bowls, and meals the pilgrims leave | `Resident` |
| `RUT_InhabitedTemple_GreenOath` | Wildsteam Clan (`WILDSTEAM`) | the Green Oath | a grove-temple. The only faith that plants, so the temple **is** a tended garden, and its smugness is earned | a granary of the grove's harvest. Burn it and they leave | `FleeIfThreatened` |
| `RUT_InhabitedTemple_Continuity` | Free Droid Enclaves (`DROIDS`) | the Continuity Protocol | a memory-vault where droid archivists keep the origin records. They are religious about their own making | power cells and spare components, not food | `Resident` |
| `RUT_InhabitedTemple_SunDebt` | Deep Desert Tribes (`TUSKEN`) | the Sun-Debt | a high place. Water is sacred, and to them moisture farming is sacrilege | a herd and water skins | `FleeOnArrival`. A gravship landing is itself the offence |

**Who lives there** (per temple, 4 to 7 people): one keeper, two or three devotees, one pilgrim or
novice, and, where §7.1 of the Inhabited design allows, **one person who deals** (trade is a
person, not a place). New characters are written in `design/Jawa/bridge/INHABITED_CAST_<FACTION>.md`
and generated by `cast_to_xml.py`, never hand-typed into XML. Each is tested with the Inhabited
design's question, *"would this person be a different person in the faction next door?"*

**What the player can do there:**
- trade with the dealer;
- attend: the temple's altar is a real Ideology ritual seat of the residents' own ideo, so their rites
  run in front of the player (vanilla ritual machinery);
- steal from the offerings (the forbid hole is the warning shot: they notice, and FATE answers);
- or burn it. They leave and join the displaced pool (§4 of the Inhabited design), and *"the
  beggars at the player's gate may be the crew whose refinery they burned"*.

**Not living, by ruling:** no Sith congregation (a Sith is always an enemy, and the lair already exists
in `RM_Abyss`), and no living Jedi or Whills order (no faction holds that faith, and a new one cannot
be added to the frozen world after the freeze).

## 4. Mod Settings (every mod ships them)

Temple ruins on/off · inhabited temples on/off · per-faith on/off (9 switches) · sleepers on the Sith
tomb on/off · loot density slider (0.5× to 2×, default 1×). There is no worldgen-affecting switch,
because nothing rolls.

## 5. Where it lives

- Ruins and living temples go in existing mods, not a new one. **RSW** temples:
  `src/RimStarWars/` holds the kits and layouts, placed through the Utinni patch layer (Q11a canon route).
  **RUT** temples: `src/RimUtinni/StructureInjectionsRUT/Defs/Temples/`. **RM** temple:
  `src/RimMandrake/StructureInjections/Defs/Temples/`. The living temples' `InhabitedPlaceDef`s go in
  `src/RimMandrake/Inhabited/Defs/PlaceDefs/` (RM tier, where `RM_InhabitedPlace_Scrapyard` sits).
  Their mutators are RUT, because they name this world's factions.
- Every new mod surface comes with its first `validation.py` script (CLAUDE.md, how we debug). For a
  temple, that script loads the layout offline, checks that the axis cells are gate → door → holy
  object, checks that every symbol has a `styleCategory` that resolves, and checks that each variant's
  rubble count falls inside its band.

## 6. Build order and cost (estimates)

1. **One faith end to end:** `RUT_TempleOfTheNineRuin`, the player's own faith, with the zero-art
   placeholder kit. It proves the styleCategory-symbol route and the generator. About 1.5 agent-days.
2. **The other four ruins** on the same generator: about 0.5 agent-day each.
3. **`RUT_InhabitedTemple_Salvation`**: the intact Nine temple plus a JAWA temple cast. It proves the
   PLACE+CAST path for a temple. About 1.5 agent-days plus the cast writing.
4. **The other three living temples**: about 1 agent-day each, mostly writing.
5. **Art:** 5 kits × about 10 sprites, through the art pipeline. It never blocks 1 to 4.
6. **Placement** on the one map is not a build step. The temples join the paint-once list
   (`BIOME_PAINT_ONCE_AT_THE_END_1`'s pass), which places them alongside everything else.

## Cited machinery

Every name below is something this design builds ON and claims EXISTS today. The checker
`python3 src/RimMandrake/Utils/check_design_citations.py <this file>` searches the named root for each
one (`src` = this repo's `src/`, `vanilla` = the game's `Data/`, `vef` = Vanilla Expanded Framework).
Names that this design proposes to create are not listed: they do not exist yet.

| name | root | used for |
|---|---|---|
| `TileMutatorDef` | vanilla | the mutator itself |
| `extraGenSteps` | src | the mutator → GenStep hook, used in `StructureInjectionsRUT` |
| `TileMutatorWorker_AncientStructure` | vanilla | Odyssey's procedural route: considered, not used for the sanctum |
| `structureGenParms` | vanilla | the same route's parameter block |
| `LayoutWorker_AncientRuins` | vanilla | the same route's room-table worker |
| `StyleCategoryDef` | vanilla | the faith art kit |
| `thingDefStyles` | vanilla | the kit's per-thing rows |
| `Spikecore` | vanilla | placeholder kit, Sith tomb |
| `Rustic` | vanilla | placeholder kit, Jedi enclave |
| `Totemic` | vanilla | placeholder kit, Temple of the Nine |
| `Horaxian` | vanilla | placeholder kit, Sun Court |
| `Techist` | vanilla | placeholder kit, Star-Seer observatory |
| `Pew` | vanilla | re-drawn furniture |
| `Column` | vanilla | re-drawn furniture |
| `Altar_Small` | vanilla | the nine niches |
| `Altar_Medium` | vanilla | the main altar |
| `Ideogram` | vanilla | the faith's symbol |
| `Lectern` | vanilla | the Jedi enclave's holocron seat |
| `Sarcophagus` | vanilla | the Sith tomb's axis object |
| `Brazier` | vanilla | lighting |
| `TorchLamp` | vanilla | lighting |
| `Filth_RubbleBuilding` | vanilla | baked ruin damage |
| `GenStep_CustomStructureGen` | vef | the KCSG GenStep the layouts run through |
| `chooseFromlayouts` | vef | picks one of the variants |
| `styleCategory` | vef | the KCSG symbol field that applies the kit |
| `RM_SalvationDialect` | src | our one existing StyleCategoryDef (proof of the def shape) |
| `gen_spire_layout.py` | src | the layout-generator pattern to copy |
| `RM_InhabitedPlace` | src | the existing inhabited mutator: cast + stock GenSteps |
| `Inhabited_Cast` | src | the GenStep that spawns the cast |
| `RM_InhabitedStock` | src | the GenStep that drops the larder |
| `InhabitedPlaceDef` | src | the temple's PLACE archetype |
| `WorldObject_Inhabited` | src | the world object that holds the roster |
| `FleeIfThreatened` | src | a FATE value |
| `FleeOnArrival` | src | a FATE value |
| `RM_InhabitedPlace_Scrapyard` | src | the existing place archetype to copy |
| `cast_to_xml.py` | src | generates cast XML from the prose rosters |
| `RUT_Jawa_IndigenousTribes` | src | Jawa Trade Moot, holder of The Salvation |
| `RUT_Jawa_WildsteamClan` | src | holder of the Green Oath |
| `RUT_Jawa_FreeDroidEnclaves` | src | holder of the Continuity Protocol |
| `the Sun-Debt` | src | the Deep Desert Tribes' faith |
| `RM_Abyss` | src | where the living Sith already lurk |
| `RUT_OasisShrine` | src | an existing small shrine mutator. A temple must not duplicate it: that shrine is a spring and bowls, not a temple |
