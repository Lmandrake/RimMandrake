# Webwork: bedazzle review (grandfathered sitting, turn 1 drafted)

Item: `WEBWORK_SCORING_SITTING_1` (BENCH; filed by the parent). Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 5.

_BENCH design pass, 2026-10-02. Fifth sitting of the grandfathered track, worst-first by
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Webwork; sitting order row 5). The sheet
`the_webwork.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07) and owner-ratified; the owner
species, nest and egg economy were ruled at `WEBWORK_DESIGN_SITTING_1`
(`webwork_owner_and_nest_2026-09-23.md`, fourteen rulings 2026-09-23/24), and both rosters were
ruled and built (`webwork_fauna_roster_2026-09-23.md`, `webwork_flora_roster_2026-09-23.md`).
**Nothing ruled there is re-argued here.** The six hard bans of sheet §6 bind every slate row
(above all: no tamed, traded or allied ollathrix, ever; no safe dense-canopy cell)._

Sources read, all in the BENCH clone: `src/RimMandrake/Webwork/` (BiomeDef
`Defs/BiomeDefs/RM_Webwork_Biome.xml`, both race files, flora, nest, egg, hediffs, soundscape, the
five C# files), `src/RimMandrake/CreatureBehaviors/` (SenseWeb, FrontCreep, ChewAnchors, SunScald,
AdhesiveSlick), the twin `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Webwork.xml` and
`RUT_WebworkStructures.xml`, `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Webwork.xml` (empty by
ruling) and `WildPlants_Webwork.xml`, `src/RimUtinni/ShokkweaveEconomy/`, `src/RimUtinni/EggReckoning/`,
`src/RimStarWars/Shokk/`, the items `WEBWORK_KIT_BUILD_1`, `WEBWORK_WEB_STRUCTURES_1` (both closed),
`SHOKKWEAVE_SOLE_SOURCE_1`, `WEBWORK_EGG_BROKER_CHANNEL_1`, `WEBWORK_FIRST_SCRIPT_1`, the register
`design/Jawa/salvation_rites_2026-10-01.md`, and the Pyrelands and Sump reviews for shape and for the
signatures to avoid. Rosters were parsed as XML elements; the creature census reads descriptions.

## 1. What is there: ruled vs built

### A thin, deliberate biome with a real kit, split badly across the tiers

`src/RimMandrake/Webwork/` (`mandrake.rm.webwork`) ships the owner species `RM_Ollathrix` (bs 2.6,
dormant debris-pile ambush via vanilla `CompCanBeDormant`/`CompWakeUpDormant`, the mouth-loom spit as
a `CompProperties_TurretGun`, the loom-bound hediff `RM_LoomBound`, sun-scald `RM_Webwork_SunScald`
read by `RM_Hediff_SunScald` on `InSunlight`), the nest cluster (`RM_Webwork_NestWall`,
`RM_Webwork_EggClutch`, one per map by `RM_GenStep_WebworkNest`, re-laying, `RM_CompEggClutchRelay`),
the egg item, `RM_CompEmergentSpawnOnDestroy`, the hush-and-thrum soundscape, and its own placement
worker. CreatureBehaviors carries the shared web machinery: `RM_MapComponent_SenseWeb` +
`RM_CompSenseWebNode` (touch a web, be felt), `RM_MapComponent_FrontCreep` + `RM_FrontCreepExtension`
(the margin advance, live-verified at `WEBWORK_KIT_BUILD_1`), `RM_JobGiver_ChewAnchors` (the
quarrok's anchor war), and `RM_CompProperties_AdhesiveSlick`.

The campaign layer adds the silk economy (`src/RimUtinni/ShokkweaveEconomy/`: the hyperweave rename
to Shokkweave, the trader strip, harvest nodes and scatter, creep-web and butcher yields, the
Hutt-cartel egg market), the egg-assassination quest (`src/RimUtinni/EggReckoning/`), and the
Wyyyschokk skin over the ollathrix (`src/RimStarWars/Shokk/`).

🔴 **Finding 1: the free tier has neither its signature nor its silk.** The web structures
(`RUT_Webwork_Anchor` / `_Web` / `_Gutter`) and therefore the creeping front live only on the frozen
twin `RUT_Webwork`; the free def's own comment says the extension is *left off until
`WEBWORK_WEB_STRUCTURES_1` ports the structures*. That item closed (art and the slick/locked
mechanism) **without porting them**, so the gate is now stale. The silk is the same: sitting ruling 4
names it **thrixweave** in the free tier, yet no free-tier def renames hyperweave or yields silk
(`RM_Webwork_DamageDefs.xml` l.26: *"this def yields nothing and creates no thrixweave"*). On the
free tier the web-sense has no web to be felt through, the quarrok's anchor war has no anchors to
chew, and the biome's one unique material does not exist. Q11a (*"rich enough to stand alone"*)
fails on the biome's spine. The remedy is already ruled (sitting ruling 1: *mechanisms move to the
free tier*; Q11a/Q12): port the three structures and the front to `RM_`, and give the free tier a
thrixweave rename and its harvest routes, with Shokkweave as the campaign's rename on top (§4 row 0).

### Fauna, merged (inline + patch-added), read as XML elements

`WildAnimals_Webwork.xml` is **empty by ruling** (all four donor rows cut 2026-09-24), so the free
def's `<wildAnimals>` is the whole cast on both tiers:

| def | label | bs | commonality | role (from the description) |
|---|---|---|---|---|
| `RM_Ollathrix` | ollathrix | 2.6 | 0.15 | the owner: blind, bone-white, hunts by feel through the web; *"a spider the size of an elephant, weight for weight closer to a horse"* |
| `RM_Quarrok` | quarrok | 1.4 | 0.3 | slab-backed beetle that *"hates the web"*, cuts anchors; never troubles anything with legs; chitin |
| `RM_Vennick` | vennick | 0.12 | 0.6 | egg-mite: *"read as a current, not as animals"*; the living treasure map |
| `RM_Skennet` | skennet | 0.35 | 0.4 | stilt-legged prey gleaning the fellome pods the owners sow |
| `RM_Cravvet` | cravvet | 0.5 | 0.25 | scuttler parked on a stain: a fresh kill site, readable danger |
| `RM_Sivvern` | sivvern | 0.3 | 0.2 | silent dusk-flier (real flight, `MaxFlightTime` 8); circling low marks egg traffic |

All six are invented `RM_` and single-homed (no other biome's file names them). **Multi-homed: none.**
The thinness is doctrine (sitting ruling 5: *"silence is doctrine"*); the fill in §3 respects it.

### Flora, merged

Sixteen invented `RM_` rows inline (kollavane, threllick, dulloth, grennick, vessark, varrisk,
pellareth, fellome, tavrosk, brennoth, sellith, kessaroth, norrveth, sorrivel, brimlock, ruddreth),
plus the canon tooke-trap patched on by `WildPlants_Webwork.xml` at 0.3 (campaign only). Harvests:
tavrosk liquor (`RM_TavroskLiquor`), brimlock water (`RM_BrimlockWater`). The pellareth trace the web
and the ruddreth ring the nest (*"the only warm colour in the biome"*): the palette is the map, as
the sheet rules.

### Heat: the biome has not declared its kind

🔴 **Finding 2: the Webwork is an extreme-heat biome with no heat kind.** The sheet measures
temperature p10/median/p90 38.6 / 49.2 / 58.2 °C under a sun median of +51°; the law (owner,
2026-09-29/30) requires every extreme-heat biome to declare `overhead`, `lowSun` or `ambient`, sun
angle from the tile's latitude. `RM_Webwork` carries no `RM_SunHeatExtension` (six biomes do). The
fit is **`overhead`**, and it makes the sheet's light-moat cut both ways: the sunlit clearing that
keeps the owners out is also where colonists overheat, while the canopy that is cool is never safe
(sheet ban 6). One heat, no new kind. ⚠ The ollathrix's sun-scald is **light** lethality (unroofed
sunlight, `InSunlight`), not heat: it stays, worded as light, never as a heat kind (§4 row 0b).

🔴 **Finding 3: the sun-scald cannot see the canopy, so the light-moat has no inside.**
`RM_Hediff_SunScald` keys on vanilla `InSunlight` (unroofed and sky glow above 0.1). Trees do not
roof a cell, and Ash'karr's dayside never has night, so read from the code the ollathrix scalds on
**every unroofed cell of its own jungle**, all the time: the sheet's law (*"helpless in direct
sunlight… clearings are the only safe ground"*) becomes "helpless everywhere outdoors". The shade
model the sheet needs already exists: `RM_MapComponent_ShadeGrid` casts shade from big plants as well
as roofs (built for the Stillsand and Long Shade). Re-keying the scald from `InSunlight` to the shade
grid makes the canopy the owners' home and a clearing their wall, which is the light-moat as ruled
(§4 row 0b). UNMEASURED live; read from source only.

### Ruled mechanics, built and unbuilt

- **Built:** web-sense (map component and nodes), the front (twin only), anchor-chewing AI with the
  quarrok as consumer, loom-spit and loom-bound, sun-scald, dormant ambush, nest on every map,
  re-laying, egg relay, emergent spawn, the silk economy and egg market (campaign), egg-assassination
  quests (campaign), the hush soundscape.
- **Ruled, unbuilt:** the ollathrix's own think tree and the convergence JobGiver
  (`RM_JobGiver_SenseWebConverge`), so web-sense is felt but not yet *acted on*; droid-priority
  targeting (rides that JobGiver); the light-moat's lit-ground pathing aversion; melee verbs and venom
  authored on the race; the carried-eggs mark; the Wildsteam still-burner and mandible bounty; the
  egg broker channel (`WEBWORK_EGG_BROKER_CHANNEL_1`, blocked on the Bazaar tab system).
- **Unruled marks:** learned technology (2), the colossus (5), the ship (6), weather (8), a Salvation
  rite (9).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_MapComponent_SenseWeb` / `RM_CompSenseWebNode`: who touched which web, where. Any
  "the web knows" idea is a reader of this, not new tracking.
- `RM_MapComponent_FrontCreep` / `RM_FrontCreepExtension`: the advancing line, already a per-map
  clock with its own cells.
- `RM_JobGiver_ChewAnchors` / `RM_ChewableExtension` / `RM_ChewAnchorsConsumerExtension`: a
  creature that targets a structure class.
- `RM_CompProperties_AdhesiveSlick` (slick/locked adhesion, from `WEBWORK_WEB_STRUCTURES_1`).
- `RM_Hediff_SunScald` and the `InSunlight` primitive; `RM_SunHeatExtension` /
  `RM_MapComponent_ShadeGrid` / the `Thing.AmbientTemperature` postfix (CreatureBehaviors).
- `RM_CompEmergentSpawnOnDestroy`, `RM_CompEggClutchRelay`, `RM_GenStep_WebworkNest`.
- `RM_HeatSoundscapeExtension` (Long Shade): a camera-cell sound bed keyed to a map condition.
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against
the sheet, the sitting record and the source.

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | PARTIAL | **HIT** | front: twin only; web-sense, ambush, nest: both | finding 1: the creeping front and the web structures are not on the free tier |
| 2 | Discoverable technology | MISS | MISS | nothing learned | the loom-spit is the spider's own organ, not the colony's |
| 3 | Unique resources | **HIT** | **HIT** | tavrosk liquor, brimlock water, eggs, quarrok chitin: both; silk: campaign only | thrixweave is ruled for the free tier and unbuilt (finding 1) |
| 4 | Surprising creatures | **HIT** | **HIT** | all six | the vennick current, the cravvet parked on a kill, the blind owner |
| 5 | GIANT beast | PARTIAL | PARTIAL | ollathrix bs 2.6 | *"the size of an elephant"* by draw, horse by mass: a big spider, not a colossus |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | **HIT** | **HIT** | hush + thrum | the silence is the design; a sound that matters in play is still absent |
| 8 | Interesting weather | MISS | MISS | vanilla jungle table | Clear 50, fog, rain, thunderstorm |
| 9 | Relationship to the gods | MISS | MISS | 0 | no Salvation rite, no god named |

**Free 3 / 2 / 4. Campaign 4 / 1 / 4.** Same totals as the scores doc. Unlike the Pyrelands, half the
Webwork's trouble is ruled-but-unbuilt (the free tier's front and silk, the convergence AI, the
light-moat pathing), and half is marks nobody ruled (2, 5, 6, 8, 9).

**Rite: none.** The scores doc's two hints (offer brimlock water back to Oomo; a binding vigil
against the shadow for Sh'kaar) are both blocked now: Oomo is at the four-rite cap, and a vigil
against the dark sits too close to the Abyss's darkness rites. §6 offers others.

## 3. Roster fill

### The gaps, read from the sheet and the ruled roster only

| hole | why it is a hole | fill |
|---|---|---|
| The free tier has no web for its web-sense | finding 1; ruled (sitting ruling 1, Q11a) | **port the anchor, sheet web and gutter to `RM_`** and wire the front (§4 row 0) |
| No colossus | mark 5; the ollathrix is ruled one race, one kind (sitting ruling 2), so the giant cannot be a bigger spider, a queen or a caste | **the morravell** (one new `RM_` giant, proposed below) |
| Prey, flier, beetle, mite, scavenger | sitting ruling 5 asks for 4 to 6 rows besides the owner; five are built | none needed; the giant makes six, still inside the ruling |

### Proposed: one new giant, free `RM_` tier, one home

- **The morravell** (`RM_Morravell`, invented, Webwork accent: doubled consonant, *-ell* like
  *sivvern*/*skennet*; no hit in `src/` or `design/`, zero Wookieepedia search results, sanity probe
  `wyyyschokk` returns 10). A colossal, slow canopy-browser, bs about 7, drawn huge on an ordinary
  footprint (the Orun-Ghal shape, no new rig), hide a deep wine-violet scored with old silver-white
  silk scars. It is **the one thing the web cannot hold**: it walks through sheet webs and tears
  them, and it eats the kollavane crown, so **where it fed, the canopy is open and the sun falls**.
  Its trail is a line of fresh sun-holes: safe ground for a day or two, until the dulloth seals the
  canopy again. It is also **the only loud thing in the Webwork**: a crash of canopy in a silent
  jungle is the morravell, and nothing else.
- **What it does in play:** the light-moat the colony must cut and burn by hand, the morravell opens
  for free and at random. Packs of ollathrix stalk it for days (the web-sense, read); when they bring
  it down the carcass is a kill site the cravvet park on, a jackpot of meat and hide sitting in the
  owners' dining room. Wild, not tameable, not hostile unless harmed. A few per map at most, often none.
- **Not a neighbour's giant:** the furnace-beast is warmth on the hoof, the greatbole is a tree, the
  hessarund a living ridge, the tar beast a catastrophe you evacuate. The morravell is the giant as
  **a moving source of sunlight** in a biome where light is safety.
- **Reuses:** `RM_ChewableExtension` / `RM_JobGiver_ChewAnchors` pattern pointed at sheet webs and
  canopy trees; vanilla plant-eating for the crown; `RM_CompSenseWebNode` already feels a web torn.
  New code: a small "canopy opened" marker so the sun-hole is readable (a cut-crown plant state or a
  short-lived terrain overlay). Static art, three facings.

## 4. The slate

Proposed for owner turn 1. Rows 0 and 0b are ruled already (they execute rulings, not new design);
rows 1 onward need his word. Nothing here touches tiles.

**0. The free tier gets its web and its silk (ruled: sitting ruling 1, ruling 4, Q11a/Q12).** Port
`RUT_Webwork_Anchor` / `_Web` / `_Gutter` to `RM_` structures in `mandrake.rm.webwork`, carrying the
`WEBWORK_WEB_STRUCTURES_1` art and the slick/locked adhesion, and add `RM_FrontCreepExtension` to
`RM_Webwork`. Add the free-tier silk: hyperweave renamed **thrixweave** with the sole-source strip and
the harvest routes in the free mod; the campaign's Shokkweave rename then patches thrixweave, never
hyperweave directly. Delete the now-stale gate comment in `RM_Webwork_Biome.xml`. Size M.

**0b. The heat law and the light law (ruled 2026-09-29/30; sheet §3, §7b).** Add
`RM_SunHeatExtension` to `RM_Webwork`: `heatKind overhead`, sun from the tile's latitude,
`heatOffsetC` an invented first value tuned in live play. Re-key `RM_Hediff_SunScald` from vanilla
`InSunlight` to `RM_MapComponent_ShadeGrid` (cast shade from big plants as well as roofs), behind a
Mod Settings toggle, so the canopy is the owners' home and a clearing their wall (finding 3). The
scald stays a **light** hediff, worded as light, never as heat. Size S to M.

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant** (§3 or §5 idea 2, owner picks): the living morravell that opens sun-holes, or the dead urraveth the owners ate, read bone by bone. | 5 | ChewAnchors pattern, ShadeGrid, SenseWeb (living); a saved map component and examine jobs (dead) | M |
| 2 | **The traction lance** (§5 idea 1): learned from a braced, intact gutter junction; a thrixweave tether that reels a target, usable everywhere. | 2 | thrixweave (row 0), the web alarm on cutting | L |
| 3 | **Sheetfall** (§5 idea 4): after a storm, torn canopy sheets fall and roof part of the light-moat until shot down. | 8 | vanilla storm transitions, the scald re-key (row 0b), the web structures (row 0) | L |
| 4 | **The hull trellis** (§5 idea 3): threllick roots thread a landed ship's doorframes from a living gutter; excise or carry the damage away. | 6 | the gutter structure (row 0), vanilla gravship transport | M |
| 5 | **A Salvation rite** (§6 R1, R2, or §5 idea 5). | 9 | found-rites row, `RUT_ResearchMod_GrantRite` | M |
| 6 | **Art commission:** the giant, the lance and its junction specimen, the falling sheet, the root intrusion, the rite's inscription. Web structures already have art from `WEBWORK_WEB_STRUCTURES_1`. | all | artpipe | — |

🔴 **Sequencing:** rows 3 and 4 depend on row 0 (no free-tier sheets or gutters exist until it lands),
and row 3 needs row 0b's scald re-key (a fallen sheet must shade the owners through the shade grid).
`WEBWORK_FIRST_SCRIPT_1` (the north-star script) should be written against row 0's state, not today's.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/webwork_gpt.md` (prompt beside it,
`webwork_gpt.prompt.md`), run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`,
ruling 2026-10-01): exactly five ideas, different from each other (GPT's own check: verbs reel /
reconstruct / excise / intercept / testify; systems combat displacement / forensic exploration /
building integrity / storm debris / colony history) and from every other biome's signature, which the
prompt listed in full (the Sump's included). Model `gpt-6.1-sol`, high reasoning effort, via
`gpt_consult.py` (`codex exec`). GPT cites Subnautica, VFE Ancients, Alpha Biomes, Anomaly, Odyssey,
Against the Storm, ReGrowth, Dwarf Fortress and Ideology; its links are not verified here.

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **The Mouth's Answer:** brace and cut out an intact gutter junction without breaking it; studying it teaches the **thrixweave traction lance**, a manned emplacement that fires a tether and reels a target in: a downed colonist out of danger, a mechanoid out of cover, **an ollathrix out into the sun**. Walls stop the pull; big targets cost more power and silk. | 2 | free | L | Strong. Learn-here, use-anywhere like the lightning breakers, but a different verb (drag, not protect). The pull-into-sunlight use is the Webwork's own lesson turned on its owner. Needs row 0's silk. |
| 2 | **They Ate the Colossus:** one Webwork map holds the wrapped skeleton of an **urraveth**, an extinct grazer bigger than a colony building. Examining it bone by bone reconstructs its death (pinned, bound, cut, eaten); opening the last wrapping shows the whole outline. Loaded bones creak and can collapse with warning. | 5 | free | M | A giant met as evidence: the owners ate it. Clean against the tar beast and the hessarund. Competes with §3's living morravell; the owner picks one or both. Name collision-checked: none in `src/`, `design/` or Wookieepedia. ⚠ "one designated map" must be one *kind of site*, not a worldgen feature. |
| 3 | **Your Hull Is a Trellis:** where a living gutter touches a building seam, threllick roots thread through it; on a landed ship a pale root comes through an inside doorframe, thickens, forces the door, splits the frame. Cut it out, or take off: the supply is severed but the damage flies with you. | 6 | free | M | The biome acting on the ship in its own voice (the plantation occupies structures), not a ship gadget. Applies to any building, so no ship-only special case. Close to Anomaly fleshmass in kind; different in that it rides the existing gutters. |
| 4 | **The White Sky Comes Down (Sheetfall):** after a thunderstorm, torn web sheets fall from the canopy and snag across the cleared moat as a real roof; shoot the suspension knots before it settles, or the owners have a shaded bridge until you destroy it. | 8 | free | L | Weather that does something visible on the map, tied to the light-moat. Depends on row 0b: the fallen roof only matters if the scald reads real shade. Roof ownership is the hard part; prototype first, as GPT says. |
| 5 | **Testimony Beneath Sh'kaar:** found on the sun-facing wall of a refuge whose survivors reached open sun; the rite names one real, unacknowledged colony loss and witnesses it together bare to the sky (vanilla heatstroke risk); each loss can be testified once. Favour shows only as a slight lean toward clear weather. | 9 | campaign | M | Fits the rulings (cohesion only, favour as odds). Sh'kaar has room. Overlaps §6 R1 on god and exposure; R1 is the biome-specific act (felling shade), this one is remembrance. ⚠ "once per loss" is a non-repeatable choice; fine for a rite, but say so on the card. |

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. Four-rite cap per god (Zizzik waived).

**Not taken, and why:** offering brimlock water back (Oomo is at its cap of four found rites); a vigil
against the shadow (the Abyss owns every darkness rite); anything with the owners as a party to it
(sheet ban 2, no truce language: a rite never pays, feeds or bargains with the ollathrix); sealing
an offering (Nightside Ice's Cold Ledger); lighting a fire you set (the Calling-Pyre). Ohm is also at
its cap. Sh'kaar carries two found rites (the Anvil Gift, the Shade Tithe) and Ta'Baa three, so both
have room.

### R1. The Felled Noon, for Sh'kaar: feeding, by letting the sun in (PITCHED)

- **Grounding:** the Webwork is the one place on the planet where the hungry sun is a *protector*:
  the owners die in it. Sh'kaar is fed by exposure; here exposure is safety, and the rite holds both
  truths at once.
- **Found:** a great kollavane stump in a ring of old sun, the cut face carved with a sun-mark, a
  ring of bleached ollathrix legs at the edge of the light where something waited and burned.
- **Asks:** the participants fell the tallest living tree on the map by hand, at the hour of highest
  sun, and stand bare-headed in the hole it leaves until the rite ends. On the Webwork the web feels
  the fall: the owners come to the shade line and wait there, pacing, for the length of the rite.
- **Risk (the point):** standing unshaded in an overhead-heat biome is vanilla heatstroke; on the
  Webwork it is also a ring of predators at arm's length from people who must not step back. Nothing
  protects them but the sun.
- **Outcomes (cohesion only):** shared memories by quality. Sh'kaar's pleasure is told by the
  Narrator and shows only as events and odds, never a buff.
- **Readable signs:** the stump, the sun-hole, the owners pacing the shade line, the letter.
- **Collision check:** the Shade Tithe (Sh'kaar) raises a roof to *make* shade at golden hour; this
  rite destroys shade at noon. The Anvil Gift gives a weapon to fire. Distinct.

### R2. The Cut Cocoon, for Ta'Baa: consolation, by refusing to be held (PITCHED)

- **Grounding:** the Webwork is the most rooted thing on the planet: roots that stole a river, a
  plantation, prey held in silk for days. Ta'Baa is the god of flight and refusal to root; the
  loom-bound colonist is the image of what Ta'Baa hates.
- **Found:** a silk cocoon on a sunlit rock, cut open **from the inside**, empty, knife marks on the
  inner wall and boot prints going away into the light. Someone got out.
- **Asks:** held for a colonist who is or was recently held: loom-bound, imprisoned, kidnapped and
  returned, or carried back downed. The others cut away a symbolic binding by hand, no tools, and the
  held one walks out first, ahead of everyone, and does not look back.
- **Outcomes (cohesion only):** shared memories by quality. Ta'Baa's favour is told by the Narrator
  only.
- **Readable signs:** the cut binding left where it fell, the letter naming who walked out.
- **Collision check:** the Returned (Ta'Baa, consolation) seals a body aboard; the Vindication Walk
  (Ta'Baa) walks a Settling's prints; the Shadow Walk (Ta'Baa) crosses a gloomcast. None frees the
  living from being held.

GPT's rite idea, if any, is in §5 and is not repeated here.

## 7. Draft turn-1 card

Plain language, no def names in option labels. Above the card, re-describe the Webwork in full (the
river-drinking jungle, the blind owner spider that dies in sunlight, the light-moat) per the standing
rule that he is never assumed to remember.

**1. Build first** — *What should FOUNDRY build first for the Webwork?*
- **Fix the base first (recommended):** give the free mod its creeping web and its silk, declare its
  heat, and let the spider's sunburn see tree shade. Buys: the biome works as written on the free
  tier, and every new idea below has something to stand on. Costs: no new mark lands this round.
  *Why: three of the four new ideas need the web and the tree shade to exist first.*
- **Base fixes and the giant together:** Buys: one visible new thing alongside the repair. Costs: a
  larger first batch and art waiting on it.
- **New ideas first, base later:** Buys: new marks sooner. Costs: the falling sheets and the ship
  roots cannot work on the free tier until the web exists.

**2. The giant** — *Which giant should the Webwork get?*
- **A living giant that opens the sky (recommended):** a huge, slow, violet canopy-eater the web
  cannot hold; where it feeds the canopy opens and the sun falls, a free and temporary safe zone, and
  its crashing is the only loud thing in the biome. Buys: a giant that plays into the light-moat and
  the silence. Costs: a new animal, its art and a small behaviour.
  *Why: it turns the biome's own rule (light is safety) into a creature.*
- **A dead giant the spiders ate:** a wrapped skeleton bigger than a building, read bone by bone
  until you see what killed it. Buys: dread and scale with no new animal. Costs: several bone pieces,
  inspection work and collapse logic; no living giant.
- **Both:** Buys: the living one and the proof of what happens to it. Costs: both bills.
- **Neither:** the big spider stays the biggest thing here. Buys: nothing to build. Costs: mark 5
  stays a miss.

**3. New marks** — *Which new ideas should be built (pick any)?*
- **The traction lance:** cut an unbroken silk joint out of the web, study it, and learn a tethered
  emplacement that reels a target in: a downed friend to safety, or a spider into the sun. Usable
  anywhere after. Buys: the biome's discoverable technology. Costs: a large build.
- **Falling sheets:** after storms, torn web sheets fall across your cleared ring and give the
  spiders a shaded bridge until you shoot them down. Buys: weather that belongs only here. Costs: a
  large build; roof handling is the hard part.
- **Roots in the ship:** where a living silk gutter touches your landed ship, pale roots thread
  through a doorframe and split it unless cut out; the damage flies with you. Buys: the biome marks
  your ship in its own voice. Costs: a medium build.
- **All three (recommended):** Buys: marks 2, 6 and 8 filled in one sitting. Costs: two large builds
  and one medium. *Why: each fills a different missing mark and none repeats another biome.*

**4. Rite** — *Which rite should the Salvation find in the Webwork?*
- **The Felled Noon, for the sun god (recommended):** fell the tallest tree at high noon and stand
  bare-headed in the hole it leaves; here the spiders gather at the shade line and wait. Buys: a rite
  only this biome could teach, with real risk. Costs: a medium build.
  *Why: the one place the hungry sun protects you gets the sun's rite.*
- **The Cut Cocoon, for the god of flight:** someone who was held walks out first while the others
  cut a binding by hand. Buys: a quiet consolation rite. Costs: a medium build; little danger.
- **Testimony under the sun:** name one real past loss of the colony together under open sky, once
  per loss. Buys: remembrance. Costs: a medium build and colony-history bookkeeping.
- **None:** the answer is recorded as none.
