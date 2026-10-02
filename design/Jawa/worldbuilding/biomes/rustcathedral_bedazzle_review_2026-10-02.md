# The Rust Cathedral: bedazzle review (grandfathered sitting, turn 1 drafted)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 7. Item to be filed by the
parent (`RUSTCATHEDRAL_SCORING_SITTING_1` shape).

_BENCH design pass, 2026-10-02. Seventh sitting of the grandfathered track, in the order of
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Rust Cathedral; sitting order row 7). The sheet
`the_rust_cathedral.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07) with three ratified
amendments (name: Archon, 2026-09-12; Scald history, 2026-09-10; terramanufacture, 2026-09-11). Already
ruled and **not re-argued here**: the wall ladder, the sacrilege economics (−15 per sacred building,
hostile at −75, un-hostile only at 0), the roach split (synthetic roach here, organic roach to the
Scarlands, owner addendum 2026-09-07), the concealment arc (`cathedral_concealment_arc_spec.md`, its
nine open build items `CATHEDRAL_*`), and the mechanoid axis, which is **excluded from wild rosters by
design** (`MECHANOID_BIOME_PRESENCE_REVIEW_1`). The seven hard bans of sheet §6 bind every slate row;
the ones that bite hardest here: **no plot truth in player text** (ban 1), **no explaining the droids'
mercy** (2), **no hunting Sentinels** (3), **no explaining the deep drill** (6), and **nothing organic
spawns beyond §4's short list; green flora count zero** (7)._

Sources read, all in the BENCH clone: `src/RimMandrake/RustCathedral/` (BiomeDef
`Defs/BiomeDefs/RM_RustCathedral_Biome.xml`, every def file, `About.xml`, the Hum, Walls and
RustCathedral C# lists and all three settings classes), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml`, `src/RimUtinni/RustCathedralRoaches/`,
every patch under `src/` that names the biome (`BiomeFlora_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`,
`WildAnimals_Warscar.xml`, `RUT_CathedralWallScatter_MapGenPatch.xml`; xpath resolved per op), the
roster `rosters/the_rust_cathedral.json`, the kit spec's item `RUST_CATHEDRAL_MECHANICS_1`, the nine
live `CATHEDRAL_*` items, `cathedral_concealment_arc_spec.md`, `divine_satiation_engine.md` §⑤ to ⑨,
the register `design/Jawa/salvation_rites_2026-10-01.md`, the ledger's 2026-10-02 rulings (Webwork,
Greentide, the Open Boast to the Warscar), and the Greentide review for shape. Rosters were parsed as
XML elements; the creature census reads descriptions, not defNames.

## 0. The Rust Cathedral in plain words (for the card)

The Rust Cathedral is a metal country at the foot of the eternal noon, where the sun stands almost
straight overhead forever. The ground is not ground: the whole flat plateau is the roof of an ancient
factory, a maze of deliberate walls like a circuit board the size of a country, with rust dust banked
against them and heat shimmer for weather. Almost nothing lives there. Under everything, always, is a
hum that shifts with a mood and answers how you behave: you survive the place by manners, not walls.
Mine the plain plate freely, touch nothing sacred, stop moving when the hum drops. Tiny dancing
bolt-creatures, a tireless cleaning roach and blind eels in the coolant canals are its whole cast, and
the most powerful guardian machines on the planet patrol it slowly, never hunting. It has no giant, no
sky of its own, nothing to learn and no god's name yet.

## 1. What is there: ruled vs built

### A complete free kit, and a campaign layer that adds nothing to the biome itself

`src/RimMandrake/RustCathedral/` (`mandrake.rm.rustcathedral`) ships the whole built kit: the hum-mood
system (`RM_MapComponent_BiomeAttitude`, `RUT_RustCathedralAttitude`, three hum layers
`RUT_HumLayerDrone/Tense/Alarm`, droid commentary, sustained-sacrilege goodwill drain); the living
bolts (`RUT_LivingBolt`, resonant dance `RM_JobGiver_ResonantDance`, freeze on low bands, shed
curiosities, watched pricing `HarmonyPatch_WatchedBolts`); the cathedral roach (`RM_CathedralRoach`,
a mechanoid cleaner); coolant-eel fishing with a hum consequence and the `RUT_CoolantLoad` residue; the
wall ladder (deck plate, dead smartsteel vein and item, the sacred conduit wall, live pattern metal
gated by `HarmonyPatch_GateLivePatternMetal`); the deep-drill response (`RUT_DeepDrillCathedralResponse`);
its own biome worker and terrains; and **three Mod Settings screens** (hum: 9 toggles and a slider;
walls: 3 toggles and a slider; the mod: rarity, roach cleaning, cross-biome spread). Every C# gate
names **`RM_RustCathedral`** (`GenStep_ScatterSacredWalls`, `GenStep_ScatterCathedralWallTiers`,
`HarmonyPatch_GateLivePatternMetal`, `RUT_IncidentWorker_CathedralResponse`, the attitude def's
`targetBiome`).

The campaign layer's only biome-side content is the frozen twin `RUT_RustCathedral` (vanilla fields,
the donor worker, `Ling_Cockroach` and `RUT_CathedralRoach`, `GR_Mecharat`) and the separate
`mandrake.rut.rustcathedralroaches` (the RUT roach, which `RM_CathedralRoach` duplicates, and
`RUT_ScarRoach`, which is the Warscar's). Its real campaign content is the **concealment arc**: Regard,
stage-keyed hum and commentary, the mechanoid pass, mission and gravtech-boon offers priced against
Imperial Heat, the survey misdirection quest, the walkable descent site and the exposure ending in
which *"the ship mourns"*. All nine `CATHEDRAL_*` items are open; **none is built**.

### 🔴 The two systemic defects of the last two sittings: checked, both CLEAN here

- **(a) Invented content stranded in the campaign tier: none.** Every invented creature, resource and
  mechanic of this biome already lives in the free mod. The only campaign-only creature is
  `RUT_CathedralRoach`, and it is already duplicated as `RM_CathedralRoach` in the free def. The tier
  slip runs the **harmless direction**: **19 defs named `RUT_`** (MEASURED, a parse of the free mod's
  `Defs/`) and the `RimMandrake.Utinni.RustCathedralHum/Walls` namespaces ship **inside** the free mod,
  as the scores doc noted. Content is on the right side; only the names are wrong (a rename on the next
  touch, no design question).
- **(b) Campaign patches that replace the free list, or mechanics on the frozen twin: none.** No patch
  anywhere targets `RM_RustCathedral` (the four patches that name the biome touch the donor
  `AB_MechanoidIntrusion`'s description, the Warscar, a comment, and the shared `MapCommonBase`
  genSteps, which self-gate to `RM_`). The twin carries no mechanic at all, so nothing is lost when the
  planet is painted onto `RM_RustCathedral`. This is the shape the Greentide and Webwork fixes are
  aiming for, already in place.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_RustCathedral/wildAnimals` (3 rows):** `RM_CathedralRoach` 0.12 (*"a small mechanoid,
roach-shaped… patrols the deck plate… clearing filth"*), `GR_Mecharat` 0.5 (donor VGE mech-vermin,
`MayRequire` on the element itself, which works), `RUT_LivingBolt` 0.06 (*"a bolt with legs, or a gear
with opinions"*). `animalDensity 0.1`. Thin by ruling, not by neglect: ban 7 makes *"each exception a
story"*, and Q11a is met because the campaign adds no creature on top for the free tier to be missing.

**Campaign patch-adds to `RM_RustCathedral`: none.** `WildAnimals_*.xml` has no Rust Cathedral file.

**Flora:** zero rows, ruled (ban 7, `flora_purged`). Not a gap.

**Fish:** `RUT_CoolantEel` is native `fishTypes` on the free def (maxFishPopulation 150).

**Findings in the cast:**
- **The coolant eel is ruled a living creature and built only as a catch.** The roster's `new_defs`
  lists it as a creature with *"canal-locked movement"*, and the sheet has eels *"circling the closed
  loop for uncounted generations"*; what ships is a `FishBase` item. The canals hold nothing that moves.
- **Mynock flocks** (sheet §4: *"the one grazer that belongs… the Cathedral tolerates them, or grooms
  them"*) are canon, so campaign-only, and **wired nowhere**: the roster's confidence note parks them as
  a homeless-reserve visitor under R17 (*"fliers cross biomes"*). Listed for the owner, not argued.
- **Scaria-mad strays** are map dressing by the sheet's own word (*"the desiccated dead are map
  dressing, not spawns"*); no dressing step for them exists (searched `src/` for the dressing; none).
- **Multi-homed species:** `GR_Mecharat` (a VGE donor, cross-roster; not re-censused this pass,
  UNMEASURED); `RUT_ScarRoach` is the Warscar's by ruling, not a second home. Listed only.

### Heat

🔴 **No heat kind is declared.** The Rust Cathedral is the planet's highest steady sun (+79°, median
62.5 °C) and carries no `RM_SunHeatExtension`; `SOLAR_HEAT_EXPOSURE_1` never names it either
(the BiomeDefs that do declare one: Stillsand, Long Shade, the Forge, Flooded Canyon, the Greentide, the Scald). Under the
one-heat law (owner, 2026-09-29/30) it is **overhead sun**: shade works, and the deck plate's
never-moving geometric shadows (sheet §9) are the shade. A one-line ruled fix (§4 row 0).

### Ruled mechanics, built and unbuilt

- **Built (free):** hum-mood system with three layers and commentary, goodwill drain, living bolts
  (dance, freeze, shed, watched pricing), the roach, eel fishing and its residue, the wall ladder and
  its gate, the deep-drill response, all three settings screens.
- **Ruled, unbuilt (free, deferred by the kit's own v1 line):** **the line-cycle** (*"a mile of
  machinery turning over in its sleep, and every living thing on the plateau stops until it passes"*,
  sheet §3; the kit lists it as *"the line-cycle ambient dressing event"*), **hum literacy** (*"learnable,
  tradeable knowledge: reading the tones and the bolts' dances tells you what no instrument can"*, §7),
  a per-colonist mood thought, the eel as a living creature.
- **Ruled, unbuilt (campaign):** the whole concealment arc (nine items), gravtech boons
  (`TECHPRINT_FACTION_GATING_1` mechanism undecided), the Warscar pilgrim camps' *"a god's deathbed"*
  lore rung.
- **Ruled in prose, never given a body:** *"the really powerful ones… slowly on patrol, terrifying in
  their destructive capacity against any biological they spot"* (§1), *"patrol routes (including the
  great ones', slow and visible from far off)"* (§8). This is the natural giant (§3), and it is the
  mechanoid axis the roster excludes, so it is nobody's today.
- **Unruled marks:** a giant (5), a ship touch in the free tier (6), a sky (8), a god and a rite (9).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_MapComponent_BiomeAttitude` and its bands (`RM_ThinkNode_ConditionalAttitudeBand`): every new
  behaviour here should read the hum rather than add a meter.
- `RM_JobGiver_ResonantDance` (the bolts' figures), `HarmonyPatch_WatchedBolts` (a watched-state
  check: the seed of any "behaves differently when seen" mechanic).
- `RUT_IncidentWorker_CathedralResponse` (a biome-gated incident worker: the line-cycle's shape).
- `RM_CathedralFishing` + `NegativeFishingOutcomeDef` (eel fishing consequences).
- The wall GenSteps (`GenStep_ScatterCathedralWallTiers`, `GenStep_ScatterSacredWalls`): a patrol
  route or giant's lane can be laid the same way, self-gated to `RM_RustCathedral`.
- `RM_GlareBlind` hediffs and `RM_Mirage` game conditions (`mandrake.rm.creaturebehaviors`): glare
  exists, so any bright-sky idea reuses it (but the mirage is Stillsand's register; avoid).
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against
the sheet, the arc spec and the source. Two marks move from the scores doc, both on evidence.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | the hum that answers you; watched bolts; the drill response: both | the line-cycle is ruled, unbuilt |
| 2 | Discoverable technology | PARTIAL | PARTIAL | 0 | **moved from MISS**: hum literacy is ruled learnable knowledge (§7), but it is only useful here; campaign adds gravtech boons (arc §3, mechanism undecided), granted by the mind rather than discovered |
| 3 | Unique resources | **HIT** | **HIT** | deck plate, dead smartsteel, the sacred wall, live pattern metal, bolt-shed curiosity, roach shell, coolant eel: all free | |
| 4 | Surprising creatures | **HIT** | **HIT** | living bolt, cathedral roach (free); eel as catch only | the eel is ruled a living canal creature, built as a fish item |
| 5 | GIANT beast | MISS | MISS | 0 (largest resident bs 0.22) | the great patrolling machines are named in prose, never given a body |
| 6 | Gravship touch | MISS | PARTIAL | 0 | **campaign moved from MISS**: the arc rules the gravship *is* why the mind hides (stage 0, *"the gravship IS the reason"*) and that the ship mourns its fall (§6.1); nothing acts on the ship physically |
| 7 | Soundscape | **HIT** | **HIT** | three hum layers driven by the mood bands; bolts' dance | the line-cycle's rolling sound is ruled, unbuilt |
| 8 | Interesting weather | MISS | MISS | vanilla Clear 90, DryThunderstorm 4 | the sheet names shimmer as *"the standing weather"* but nothing renders it |
| 9 | Relationship to the gods | PARTIAL | PARTIAL | sacred walls, watched; sacrilege economics | no god named, no rite; the Warscar's *"a god's deathbed"* rung is specced only |

**Free 4 HIT / 2 PARTIAL / 3 MISS. Campaign 4 HIT / 3 PARTIAL / 2 MISS.** The scores doc had 4/1/4 on
both; mark 2 rises on the ruled hum literacy, and the campaign's mark 6 rises on the arc. Unlike the
Greentide and the Webwork, nothing here is built-but-misplaced: **the free tier is complete for what was
ruled, and the misses are genuinely unruled** (giant, sky, god) or **ruled and deferred** (the
line-cycle, hum literacy, the living eel).

**Rite: none.** The scores doc's seeds (*"a rite of manners before the sacred core, or a resonant-dance
rite"*) are both taken in kind: manners and stillness are Ishko's (the Dark Vigil and the
Stall-Hold), and a dance to a machine's mood is Ohm's (at cap; the Answering already settles with a
machine mind). §6 pitches for the only two gods with room: Rekko and Ta'Baa.

## 3. Roster fill

### The gaps, read from the sheet's short list (§4) and the ruled roster only

Ban 7 closes the usual move: **no new organic species may be added here**, and the mechanoid axis is
excluded from wild rosters by design. So the only holes a new creature may fill are the ones the sheet
already opens: a machine (the great patrollers, §1/§8) or an eel (the one organic resident).

| sort (sheet §4, §1, §8) | free tier today | campaign today | fill |
|---|---|---|---|
| The dancers (bolts) | built, in roster | same | none |
| The cleaners (roach) | built, in roster | same + RUT duplicate | none (retire the RUT duplicate at the repaint) |
| **The eels** | catch item only | same | **build the ruled living eel**: canal-locked, circling, never leaves the coolant (no new creature) |
| The grazer (mynock) | none (canon, campaign-only) | **wired nowhere** | owner's call: patch a visitor row onto `RM_RustCathedral` in the campaign, or keep R17's rowless visit |
| **The great patrollers (the giant)** | prose only | prose only | **the platewalker** or **the loop-mother**, below (card Q2) |
| The strays (dressing) | none | none | a dressing GenStep of desiccated, scaria-marked carcasses at the map edges (no spawn, ban 7) |

Names follow this biome's own accent, which is **plain descriptive compounds** (living bolt, cathedral
roach, coolant eel, deck plate, dead smartsteel), not invented syllables. Collision-proven 2026-10-02
on both instruments: **platewalker** and **loop-mother / loopmother** return zero files in `src/`,
`design/`, `infrastructure/` and zero Wookieepedia search hits (sanity probes: `wyyyschokk` and `mynock`
return 5 hits each on Wookieepedia). *Linewalker* was rejected (3 repo files, the Blue Desert's fauna);
*eldest* was rejected (8 repo files). Both candidates are one-home, free tier, alien in colour, never
hunt (ban 3), never tamed.

- **The platewalker** (`RM_Platewalker`, the great patroller made a body). A colossal guardian machine,
  drawn huge on an ordinary large footprint (no new rig, static art in three facings), legs like gantry
  sections, hull a blued gunmetal crazed with verdigris at every seam and one band of cold white light
  sweeping its front. It walks **one fixed loop** through the maze, laid at map generation as a lane
  the walls were built around (the wall GenSteps' shape, self-gated to `RM_RustCathedral`), so the
  route is readable in the plate itself: a worn bright track. It never leaves the loop and never
  pursues (ban 3); anything biological **inside its sight line** while it passes is destroyed, so the
  play is manners made physical: learn the loop, read the track, be behind a wall when it comes. The
  hum drops a band a few hundred ticks before it rounds a corner (the bolts freeze first, which they
  already do on low bands). Destroying one is possible and is the deepest sacrilege on the plateau
  (goodwill and the hum, the ruled economics). **Reuses:** the attitude bands, the bolt freeze, a
  vanilla mechanoid race base, a custom `LordJob` patrol with a leash (S to M). Not a neighbour's giant:
  the furnace-beast is warmth, the tar beast a catastrophe you evacuate, the hessarund a ridge, the
  Webwork's urraveth a skeleton, the Greentide's thurrock a herd that fells trees; the platewalker is
  **a clock you live by**, the one giant you survive by timing, not by fighting or fleeing.
- **The loop-mother** (`RM_LoopMother`, the eldest eel). The canals' oldest eel grown to the width of
  the canal itself, pale as the others, blind, faintly metallic, a long slow shape that fills the loop
  and circles it once a day; the small eels part ahead of her. She is the only organic giant ban 7
  allows, because she *is* one of §4's eels. She never leaves the coolant; she rises only when a
  line-cycle runs under the plate, and a line in the water while she passes is taken, rod and arm
  (the fishing-consequence code already exists). Butchered, she is a fortune and a desecration in one
  body (the hum's deepest drop short of the drill). **Reuses:** the living-eel build (the ruled fix
  above), `RM_CathedralFishing`, the line-cycle event (§4 row 0). Not a neighbour's giant: the Grey
  Sea's brine elders are a sea's, she is a closed machine loop's, and she makes the canals the one
  place on the plateau where the danger is alive.
- **Wire, don't invent:** the living eel (ruled), the strays' dressing (ruled as dressing).
- **Retire on the move:** `RUT_CathedralRoach` and `mandrake.rut.rustcathedralroaches`'s roach half once
  the twin is gone (the RM duplicate already carries it); `RUT_ScarRoach` stays the Warscar's.

## 4. The slate

Proposed for owner turn 1. Row 0 executes existing rulings (the sheet's §3 line-cycle and §7 hum
literacy, the roster's living eel, the heat law, the tier grammar); rows 1 onward need his word.
Nothing here touches tiles, and nothing on the slate explains the mind, the mercy or the drill.

**0. Finish what was ruled (free tier; sheet §3, §4, §7; heat law; tier grammar).** In
`mandrake.rm.rustcathedral`, under Mod Settings toggles:
- **The line-cycle:** a rare biome-gated incident (`RUT_IncidentWorker_CathedralResponse`'s shape): a
  deep rolling sound under the plate travels across the map over a minute or two, the hum drops a band,
  the bolts freeze, and **every animal on the map stops where it stands** until it passes (a short
  forced wait job; colonists get a "felt the ground turn over" memory, no stop). Readable: the sound,
  a dust shiver along the plate, a message.
- **Hum literacy:** a colonist who has spent long enough on Cathedral ground with the hum in a calm band
  gains a trait-like knowledge record (no stat buff) that lets the inspect pane name the current band
  and the bolts' figure in plain words. Learnable, tradeable as a skill-book-style text (ruled
  *"learnable, tradeable knowledge"*). Useful only here; it is the ruled half of mark 2, not the new tech.
- **The living eel:** a canal-locked swimming pawn circling the coolant (the roster's ruled creature
  shape); the catch item stays.
- **Heat:** `RM_SunHeatExtension heatKind overhead` on `RM_RustCathedral`, and add the biome to
  `SOLAR_HEAT_EXPOSURE_1`'s list.
- **Strays' dressing:** desiccated, scaria-marked carcasses scattered at map edges at generation.
- **Names:** rename the 19 `RUT_` defs and the two `Utinni` namespaces inside the free mod to `RM_` on
  this touch (a save-safe rename pass, `defName` back-compat via the engine's legacy-name hook).
Size M (no new design, five small builds and a rename).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant** (§3): the platewalker on its fixed loop, taking GPT idea 2's readable parts (a visible inspection sweep, a marked danger sector, tread sound before arrival, its body as moving cover); or the loop-mother; or both. | 5 | attitude bands, bolt freeze, wall-GenStep lane, a leashed patrol `LordJob`; for the loop-mother, the living eel and line-cycle (row 0) | M to L |
| 2 | **Remnant rebuilding** (§5 idea 1, GPT's "Vethr stitching", renamed): study fracture casts made with dead-smartsteel powder; learn to rebuild a destroyed made thing around its labelled remnant, quality and history intact, at full material cost plus a costly compound. Usable everywhere. | 2 (and 3: a new use for dead smartsteel) | wall ladder's dead smartsteel, vanilla research | L |
| 3 | **Sun bars** (§5 idea 3, GPT's "Irrav", renamed): rust fines rise and hang in sheets; hard white bars of focused noon fall on the deck and creep; under them vanilla temperature spikes; roof or screen the work or leave it. | 8 | heat law (overhead), `RM_GlareBlind`, vanilla temperature | M |
| 4 | **Stowaway bolts** (BENCH, not GPT; GPT's answer skipped mark 6): a landed ship on deck plate draws the living bolts; they gather and dance on its hull and under its struts while the hum watches; at liftoff a few are aboard, and away from the hum each goes still within a day, leaving a still bolt (a curiosity) where it stopped. The biome marks the ship in its own voice; nothing vanishes unseen. | 6 | the bolt dance, shed curiosity, watched state | S to M |
| 5 | **The interlock doors** (§5 idea 4, GPT's "Dorrik"): paired factory doors that the line-cycle swings; brace one to save its route and the other seals for good. Held for turn 2 unless he picks it. | 1 (deepens the line-cycle) | row 0's line-cycle | M |
| 6 | **A Salvation rite** (§6 R1, R2, or §5 idea 5). | 9 | found-rites row, `RUT_ResearchMod_GrantRite` | M |
| 7 | **Art commission:** platewalker (three facings, plus a wreck) or loop-mother, the living eel, the fracture bench and remnant, sun-bar overlay, the still bolt, the rite's inscription. | all | artpipe (check existing renders first) | — |

🔴 **Sequencing:** row 0 first; it is small and every later row leans on it (the loop-mother and the
interlock need the line-cycle; the sun bars need the declared heat kind; the giant's warning reads the
hum bands). Row 1 rides row 7's art batch. `RUST_CATHEDRAL_FIRST_SCRIPT_1` should be written against
row 0's state. ⚠ Every row keeps the bans: the giant's sweep and the sun bars carry **no text that
explains** the mind; stowaway bolts are never explained either (ban 1).

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/rustcathedral_gpt.md` (prompt beside it,
`rustcathedral_gpt.prompt.md`), run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`,
ruling 2026-10-01): exactly five ideas, different from each other (GPT's own check: verbs reconstitute /
yield / screen / brace / vouch; systems artifact persistence / territorial combat AI / solar exposure /
map topology / ideological obligations) and from every other biome's signature, which the prompt listed
in full, **including the Webwork's and the Greentide's 2026-10-02 rulings** (urraveth, traction lance,
Felled Noon; thurrock herd, blood-stopping lace, Ceded Room, Open Boast to the Warscar). Model
`gpt-6.1-sol`, high effort, via `gpt_consult.py`, answered in 1,301 s. GPT cites Caves of Qud, VFE
Ancients, Rain World, Subnautica, Oxygen Not Included, ReGrowth, Dwarf Fortress, Against the Storm,
Ideology and VFE Tribals; its links are not verified here. ⚠ **GPT did not answer mark 6 (the ship)**
although the prompt asked; row 4 is BENCH's own. Names checked (repo / Wookieepedia, probes as in §3):
**dorrik** clear on both; **vethr** (17 repo files), **kharv** (1) and **irrav** (2) collide in the repo
(zero Wookieepedia hits each) and are replaced by plain-English names, which is this biome's accent anyway.

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **Vethr stitching:** researchers cast matching breaks at a derelict fracture bench using powder milled from dead smartsteel; the colony learns to rebuild a destroyed made thing around its remnant, quality, biocode and history intact, paying full materials, a costly compound and powered work. | 2 | free | L | Strongest. The dead smartsteel (*"it was smart once… self-repairing"*) teaches repair without coming alive again, so ban 1 holds. Powerful, balanced by cost, usable everywhere, like the lightning breakers. Also Rekko-shaped in spirit. Size is real: catching destruction and keeping identity is compatibility work. Rename: **remnant rebuilding**. |
| 2 | **The Kharv:** a tracked guardian sixteen cells long patrols an avenue, sweeps an inspection fan, fires only inside a marked sector, never pursues; its body blocks sight and is cover. | 5 | free | L | Same seed as §3's platewalker, with better readable parts (the sweep, the sector, the cover). **Merged** into the platewalker; the 16-cell moving footprint is the expensive part and is not needed: drawn huge on an ordinary large footprint does the job. |
| 3 | **Irrav:** rust fines rise and hang; white bars of focused sun fall on the deck, brighten and creep; under them vanilla temperature spikes (a scoped `GetTemperatureForCell` postfix); screen it or leave. | 8 | free | M | Good, and legal under the one-heat law (it raises vanilla temperature, no new kind). Distinct from Long Shade (shade as an economy) and the Abyss's etchfall. Seen and felt, not abstract. Rename: **sun bars**. |
| 4 | **The Dorrik interlock:** paired doors the line-cycle swings; brace one to keep its route and the other seals permanently. | 1 | free | M | Clever, and it gives the ruled line-cycle teeth. It is a fourth new mark-1 mechanic on a biome already HIT on mark 1, so it is held for turn 2. Permanent choice: the owner dislikes reversible choices, so permanence is in its favour. |
| 5 | **Rekko's Second Signature:** found at an enclave repair court; the congregation names a repaired possession's repairer and witnesses and pledges to keep it; deliberately scrapping it later breaks trust, losing it in battle is shared grief; favour shows as earlier breakdown warnings. | 9 | campaign | M | Respects the rulings (cohesion, odds only). It competes with §6 R1 for Rekko's one slot. It is less of this place than R1 (any workshop could teach it) and adds a lasting bookkeeping obligation; R1 is a single risky act on the biome's own sacred walls. Offered on the card as the second Rekko option. |

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. Five-rite cap per god (raised from four 2026-10-02, card).

**Cap count, by hand from the register plus the 2026-10-02 ledger rulings** (found rites only; the
liturgy tab's B1 rows and the B5 devotions are not found rites):

| God | Found rites | Count |
|---|---|---|
| Ishko | Dark Vigil, Charged Reed, Stall-Hold, the Sinking | 4, one slot |
| Ohm | Engine Hour, Last Track, Deserter's Welcome, the Answering | 4, one slot |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March | 4, one slot |
| Mob'Unloo | Blind Offering, Storm's Receipt, Cold Ledger, the Sump's effigy Price | 4, one slot |
| Sh'kaar | Snuffing, Anvil Gift, Shade Tithe, Felled Noon | 4, one slot |
| **Ozzik** | Lightless Burial, Salted Keeping, Flawed Masterwork, **the Ceded Room** (Greentide, ruled 2026-10-02), **the Open Boast** (Warscar, ruled 2026-10-02) | 5, at cap |
| Zizzik | five | at cap |
| **Rekko** | Unfinished Laid Down, Inherited Wreck, Mud Claim | 3, two slots |
| **Ta'Baa** | the Returned, Shadow Walk, Vindication Walk | 3, two slots |

**Ozzik is at five**, the cap since it was raised to five by question card 2026-10-02 09:23 PDT; the earlier "one over the cap" reading is resolved.

**Not taken, and why:** a rite of manners before the sacred core, or of standing still while the hum
drops (stillness is Ishko's); a dance in the bolts' figures to the mind's mood (a machine mind
answered is Ohm's Answering); returning eels to the canal (water, Oomo); anything that
names, explains or worships the mind (ban 1, ban 2: the Cathedral is not a god of the nine and must
never read as one); anything that drills or digs deep (ban 6); a launch (Ta'Baa's own launch-rite
exists); dragging something the colony grew to the map edge (the Greentide's unchosen Uprooting).

### R1. The Mending Weld, for Rekko: feeding, by giving salvage back (PITCHED)

- **Grounding:** Rekko is *"positive when we mend, sharply negative when we scrap the mendable"*
  (`divine_satiation_engine.md` ⑤), and his lever is *scrap for resources vs. repair for piety*. The
  Rust Cathedral is the planet's purest version of that lever: the whole map is salvage you are invited
  to take (*"every wall is money"*), and the mind itself *"kept assembling itself the slow way"* after
  its smart metal died. A rite that **gives salvage back to mend a thing that is not yours** inverts the
  biome's whole economy, which is exactly Rekko's sacrament.
- **Found:** a run of the maze broken once and mended in a foreign hand: a gap in a sacred conduit wall
  filled with mismatched scrap, welded rough, clearly not the builders' work, and the living bolts
  dancing calm figures around it while they freeze everywhere else. Scratched on the patch plate, in the
  clan's old trade marks: *what was taken came back.* (Who mended it is never said; ban 2 territory.)
- **Asks:** the colony chooses its most valuable salvaged piece (a component, a smartsteel bar, a part
  stripped from a wreck) and the participants carry it to a damaged structure **the colony does not
  own** (an ancient ruin wall, a wreck, a cracked run of the maze) and weld it in by hand, by
  construction skill. The material is consumed into the structure, which is mended and stays
  someone else's. Anywhere a ruin or wreck stands, the rite can be held.
- **Risk (the point):** the material is really gone; the work stands in the open for hours. On
  Cathedral ground the mend is made at a sacred wall in the platewalker's sight lines (if built), and a
  botched weld (a failed construction roll) reads as damage to a sacred thing: the hum drops and the
  ruled goodwill drain runs. Elsewhere, ancient ruins carry their own dangers.
- **Outcomes (cohesion only):** shared memories by quality. Rekko's favour is told by the Narrator and
  shows only as odds (his Exalted register: *"salvage yields feel providential"*), never a buff. On
  Cathedral ground an Excellent mend leaves a calm band in the hum for a while, a world-state sign, not
  a reward.
- **Readable signs:** the mended run on the map, visibly patched; the bolts' calm figures there; the
  letter.
- **Collision check:** the Scrap Shrine offers scrap to Rekko; the Seating puts a relic into **our**
  hull; the Mud Claim and the Inherited Wreck take salvage; Nine Faults leaves a broken thing as an
  offering. None gives salvage back to mend something that is not ours.

### R2. The Loosing, for Ta'Baa: feeding, by unfixing what was built to stay (PITCHED)

- **Grounding:** Ta'Baa's favour *"erodes on its own time-rooted clock"*; his lever is *leave vs.
  entrench*. The Cathedral is the most entrenched thing on the planet, a mind whose whole strategy is
  *"So it waits."*, and its droid holy city has exactly one seat that refused to: *No Master*, the only
  enclave that *"kept a road out"* (sheet §8).
- **Found:** at the No Master seat, a droid's anchor plate on the deck: its four mounting bolts pulled
  and laid in a row pointing off the plateau, the chassis that stood there long gone along the one road.
- **Asks:** the participants take apart, by hand, the one thing the colony **bolted down to stay** that
  it values most (a turret, a fixed workbench, the oldest standing structure), carry every piece aboard
  the ship's hold rather than to a stockpile, and leave the footprint bare. The pieces may not be
  rebuilt on this map; raising them again before the next landing sours the memories.
- **Risk (the point):** a real hole in the colony on the map it is still living on (an empty turret
  mount on the wall is a weakness every raid will find), and the time unbuilding it. Anywhere it is
  the same cost; on Cathedral ground the unbolting noise is heard by the hum (a mild band dip).
- **Outcomes (cohesion only):** shared memories by quality. Ta'Baa's favour is told by the Narrator
  only, shown as his Exalted odds (*"better landing sites, travel opportunities, a sense of momentum"*).
- **Readable signs:** the bare footprint with its bolt holes, the crated pieces in the hold, the letter.
- **Collision check:** the launch-rite is a launch; the Returned seals a body aboard; the Shadow Walk
  and Vindication Walk are walks; the Left Behind devotion leaves things; the Greentide's unchosen
  Uprooting dragged a planting to the edge. ⚠ The Loosing shares the Uprooting's spirit (refuse what
  has rooted); it differs in the act (**unbuild a built anchor and carry it on**, never discard it).
  Say so on the card.

GPT's rite idea, if any, is in §5 and is not repeated here.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends
in "?", and no option is a "none" (the card's own write-in line covers that). Above the card, read
him §0's description of the Rust Cathedral, per the standing rule that he is never assumed to remember.
Say in one line above it that both of last sitting's defects were checked and are clean here, and that
the pride god is now at five rites (§6).

**1. Build first** — *What should be built first for the Rust Cathedral?*
- **Finish what was already decided (recommended):** the rare moment a mile of machinery turns over
  under the plate and every animal freezes until it passes; colonists slowly learning to read the hum;
  the blind eels swimming the canals instead of existing only as a catch; the overhead-sun heat rule;
  the cooked strays at the edges; tidy the names. Buys: everything the sheet promised, working, and the
  ground the new ideas stand on. Costs: a medium batch with no new mark this round. *Why: it is small,
  and the giant, the sky and the doors all lean on it.*
- **Finish it and add the giant together:** Buys: a visible colossus alongside the repair. Costs: a
  bigger first batch, and art waiting on it.
- **New ideas first, finishing later:** Buys: new marks sooner. Costs: the eel giant and the interlock
  doors have nothing to stand on until the machinery moment exists.

**2. The giant** — *Which giant should the Rust Cathedral get?*
- **The great patroller (recommended):** a colossal guardian machine, blued gunmetal crazed with
  green at the seams, walking one fixed loop worn bright into the plate; its light sweeps ahead and
  anything living in that sweep dies, but it never leaves the loop and never chases. You learn its loop
  and are behind a wall when it comes; its body is cover while it passes. Buys: the sheet's "great
  ones, slowly on patrol" made real, a giant you survive by timing, unlike any other. Costs: one large
  machine, its art and a patrol behaviour. *Why: the sheet already describes it; it turns the biome's
  manners into a daily clock.*
- **The eldest eel:** one coolant eel grown to the width of the canal, circling once a day, rising only
  when the machinery turns over; a line in the water as she passes is taken, rod and arm. Buys: the one
  living giant the place allows, and danger in the canals. Costs: needs the swimming eels and the
  machinery moment first; quieter on the map.
- **Both:** Buys: a machine giant on the plate and a living one in the canals. Costs: two builds and two
  art sets.

**3. New marks** — *Which new ideas should be built (pick any)?*
- **Remnant rebuilding:** researchers study fracture casts made from dead smart-metal powder and learn to
  rebuild a destroyed made thing around its labelled remnant, quality and history intact, paying full
  materials plus a costly compound. Usable everywhere. Buys: the biome's learned technology, powerful
  and kept. Costs: a large build (catching every kind of destruction safely).
- **Sun bars:** rust dust rises and hangs, and hard white bars of focused noon fall on the deck and
  creep; under a bar it is suddenly far hotter; roof or screen the work, or leave it. Buys: a sky that
  belongs nowhere else, felt as ordinary heat. Costs: a medium build.
- **Stowaway bolts:** a ship landed on the plate draws the dancing bolts onto its hull; at liftoff a few
  ride along, and away from the hum each goes still within a day and leaves a still bolt behind. Buys:
  the place marks your ship in its own voice. Costs: a small to medium build.
- **All three (recommended):** Buys: technology, sky and ship marks in one sitting, none repeating
  another biome. Costs: one large and two smaller builds. *Why: each fills a different missing mark,
  and together they bring the biome to the full bar except the god.*

**4. Rite** — *Which rite should the Salvation find in the Rust Cathedral?*
- **The Mending Weld, for the god of repair (recommended):** the colony carries its most valuable piece
  of salvage to a broken wall or wreck that is not theirs and welds it back in by hand; the material is
  gone, and a botched weld at a sacred wall angers the hum. Buys: a rite only this place could teach,
  giving back in the one country built to be stripped. Costs: a medium build; real material lost.
  *Why: it inverts the biome's whole salvage economy, which is exactly what the repair god loves.*
- **The Second Signature, for the god of repair:** the colony gathers around something it repaired,
  names the repairer and witnesses, and pledges to keep it; scrapping it later breaks trust, losing it
  in battle is shared grief. Buys: a lasting bond to the things you mend. Costs: a medium build, an
  obligation to track, and it is less tied to this place.
- **The Loosing, for the god of flight:** the colony takes apart the thing it built to stay that it
  values most, a turret or a fixed bench, and carries every piece aboard, not to be rebuilt here. Buys:
  a real sacrifice of rootedness in the most rooted place on the planet. Costs: a medium build and a
  hole in your defences; close in spirit to the jungle's dragged-tree idea he passed over.
