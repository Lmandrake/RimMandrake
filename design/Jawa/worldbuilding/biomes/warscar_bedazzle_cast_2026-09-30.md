<!-- status: cast bible — commissioned under WARSCAR_BEDAZZLE_SITTING_1 movement 4 -->
# Warscar — bedazzle cast bible (movement 4: ticket-out and commission)

## 0. Rulings this commission carries

**Item:** `WARSCAR_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 10)
**Date:** 2026-09-30 · **Author:** BENCH movement-4 commission agent

**Authorities:** `warscar_turn3_development_2026-09-30.md` (turn 3, `44ab4d560`),
`warscar_bedazzle_review_2026-09-30.md` (movements 1–2 and turn 1), the GPT consult
`Transient/bedazzle_gpt_enrich_2026-09-30/warscar.md`, and the seven ledger notes on
`WARSCAR_BEDAZZLE_SITTING_1` (last synced `65488c2a9`). Where the rulings and the docs differ, **the
rulings win**. Card selections are recorded as *decision taken by question card*; only typed words
are quoted.

| # | ruling | how | what it changes against the turn-3 doc |
|---|---|---|---|
| 1 | Slate IN: the Settling, projectors / aerosol screen, totchak wakes, Geiger choir, chatrak's snap, mark-as-trade, hospice, old tongue, rainbow pools, pilgrim camps. OUT: glower black uses, the Watch | card (turn 2) | as developed |
| 2 | Tracks persist and fade at the next wind; the screen works in every polluted biome; the woken totchak eats ruins AND player walls; hospice before pools | card (turn 2) | as developed |
| 3 | Names chatrak / totchak / tetchik kept; wreck-lichen added, scorched stars kept for now; pallbearer and scar roach move to RM; Soil band dropped; label "Warscar" | card (turn 2) | as developed |
| 4 | GPT refinements adopted: the tech chain ties together; the mark reveals caches behind a loosened panel, no stacking; the wreck-eater food web; tracks on a capped grid; staged repair. Narrowing the screen rejected, typed: *"I like powerful tech. Don't be afraid of making good ideas broadly useful and powerful (like the aerosol shield). There are many other ways to normalize it."* | card + typed | every tech in this package is broad, balanced by cost, power, materials, research or rarity, never by scope |
| 5 | The hospice droids, typed: *"Those droids should be INTERESTING cases... they all left their owner, ran away, then died a slow death. That's gotta leave some strange features inside."* | typed | every intact chassis is a deserter with a history (§6A drafts) |
| 6 | §4 IN: the film finds the ordnance, war dust, the lift front, unseen things leave prints, the ship wakes the line, a deserter walks in, the turrets still track, a tetchik in a jar, chatrak plate. OUT: the calm alarm, the entombed line | card (turn 4) | the calm alarm and entombed line are not built |
| 7 | The meaning group (the bearing / phantom barrage / slag ricochet) left blank twice | card (turn 4) | **treated as not picked**; none is built, and free-tier mark 9 stays PARTIAL (§1) |
| 8 | An invisible hunter is owed, typed: *"Gotta make some invisible hunters now... tricky in this genre."* | typed | **pitched in §5 for his ruling**, not built and not queued |
| 9 | Live shield generators are salvage, typed: *"We're going to have to evaluate those shield generators if they're present and working. That's salvage man!"* | typed | rings carry a condition; working ones are evaluated, uninstalled and hauled home (`WARSCAR_AEROSOL_SCREEN_1` §7) |
| 10 | Glower crust, typed *"1+2"*: **both** a rainbow-pool phase catalyst and radiation/toxic shielding | typed (card notes) | catalyst: `WARSCAR_RAINBOW_POOLS_1` §6; shielding panel and plate: `WARSCAR_AEROSOL_SCREEN_1` §9 |
| 11 | ONE shared footprint grid with the Stillsand | card (turn 4) | `FOOTPRINT_TRACK_GRID_1` filed as the single kit; `STILLSAND_SKELETONS_TRACKS_1` §7, `STILLSAND_SAND_SWIM_KIT_1` and `STILLSAND_DUNE_GALE_1` §11 corrected to consume it |
| 12 | Deserter memories and pilgrim lore rungs: BENCH drafts, the owner edits | card (turn 4) | drafts in §6, for his pen |

## 1. The build items filed

All filed `--for FOUNDRY` (`--caused-by WARSCAR_BEDAZZLE_SITTING_1`) with prose in
`infrastructure/state/items/<ID>.md` (## spec, ## criteria). Each carries Mod Settings toggles and the
readable-sign rule. **Searched first:** `git grep` over `origin/main` `src/` and the live items for every
new name (TrackGrid, Settling, AerosolScreen, PollutionSense, Chatrak, Totchak, Tetchik, WreckLichen,
Pallbearer, HospiceCradle, DeserterHistory, LoosenedPanel, InscribedPanel, ReactionTap, KneelingChassis,
AncientServitor, WarDust, ordnance, ProjectorCore, OldLineTurret; probe `korrum` 133 hits): **nothing built
or filed** beyond the design docs themselves. The reuse turn 3 §2.0 mapped stands, plus one new find:
`RUT_AncientShieldedTurret` / `RUT_BustedShieldedTurret` (AssailantSalvage) as the reference shape for
the old-line turret refit.

| item | what | waits on |
|---|---|---|
| `FOOTPRINT_TRACK_GRID_1` | the ONE track grid (CreatureBehaviors): capped pool, priority eviction, section layer, cell-entry postfix, invisible pawns recorded, erase API | nothing (build first: both biomes consume it) |
| `WARSCAR_FREE_TIER_BODY_1` | chatrak (+ chatrak plate), totchak body, tetchik, wreck-lichen; pallbearer + scar roach to RM (save-checked, §7); glower art wired; Soil dropped; label | nothing |
| `WARSCAR_SETTLING_WEATHER_1` | the Settling, the film, the wind's wipe, the lift front, war dust, buried ordnance | the grid (for tracks) |
| `WARSCAR_AEROSOL_SCREEN_1` | RM lift of the particulate core, `RM_PollutionSense`, rings, broad screen, generator salvage, the ship wakes the line, glower shielding, ship row | nothing (gel from the pools; calibration from the old tongue) |
| `WARSCAR_SNAP_MARK_1` | the chatrak's staged snap; the mark as a trade; loosened panels; no stacking | the body |
| `WARSCAR_TOTCHAK_WAKES_1` | dormant in the line, demolition wake, wall-eating, lie-down | the body |
| `WARSCAR_GEIGER_CHOIR_1` | tick, wind, silence, hum, boil; tetchik in a jar | the body; the Settling (silence) |
| `WARSCAR_HOSPICE_DESERTERS_1` | kneeling rings, histories, the five-stage cradle, the servitor, failed wrecks, a deserter walks in | the owner's edit of §6A |
| `WARSCAR_OLD_TONGUE_1` | three panel sets unlocking protocols, calibration, phase reading | the screen and hospice (what it unlocks) |
| `WARSCAR_RAINBOW_POOLS_1` | registry row, cycle, tap, four reagents, journal, phase reader, glower catalyst | the hospice (ruled order); FlowWorks |
| `WARSCAR_PILGRIM_CAMPS_1` | (RUT) camps and journals that call `AdvanceStage("Scarlands")` | the owner's edit of §6B |
| `WARSCAR_TURRETS_TRACK_1` | verbless tracking on broken turrets; the old-line turret refit | etchant (optional) |

**Scorecard after this commission** (turn 3 §5, adjusted for ruling 7): free tier **8 HIT + 1 PARTIAL**
(mark 9, gods: the hospice's image and the old tongue only, since the bearing was not picked);
campaign **9 HIT**. `BIOME_SHIP_CONTRIBUTIONS_1` got a note naming its owed Warscar row.

## 2. Shared law. Every entry obeys this without restating it

- **The admission test** (turn 1 §2): every new thing is something the war left, or something that eats
  what the war left. Nothing pastoral, nothing green, no intact treasure in the open; value is sealed.
- 🔴 **§GM never in a description.** No text names the enemy, the side, the god or the Rakata; the
  totchak *"was here after"*.
- **No animal or pawn vanishes without a readable sign** (planet law): the pallbearer leaves bones, pool
  corpses leave bone filth, failed chassis keep their names, pilgrims are found.
- **Powerful tech, balanced by cost** (ruling 4): power, materials, salvage rarity, research and failure
  risk, never a narrowed scope.
- **The light.** Flat grey overcast, soft diffuse top light, **no baked cast shadow**.
- 🔴 **Palette diversity is law.** Owner, verbatim, carried in every `style_notes`: *"Your color palette
  is too uniform per biome. Needs more variety."* Each subject has its own anchor (§8).
- **House style:** painterly vanilla-RimWorld, matte, no outlines, never cute; no nameable Earth animal.
  On faced jobs north is a true rear view with no face; facings derive from the accepted east master.
- **Tier (Q11a):** all invented, so `RM_`; the pilgrim journal is `RUT_` (campaign item).

## 3. Art dedup sweep

**MEASURED 2026-09-30, before anything was queued.** One python sweep over the on-disk
`infrastructure/artpipe/{done,_artsrc,pending,active,failed,_withdrawn}` (4,485 / 2,071 / 1 / 1 / 130 /
40 entries), `registry.jsonl` (10,574 lines), the `origin/main` artpipe tree (3,815 paths) and every PNG
under `origin/main:src` (7,512). Each subject was searched by current, interim and alternate names.

**Sanity probes, so a zero means zero:** `korrum` 6 done + 3 `_artsrc` + 3 PNGs; `mynock` 12 registry
lines + 6 done; `glower` 4 done (`rutglower_v1`, `rutglowercrust_v1`).

| subject | spellings | result |
|---|---|---|
| chatrak, totchak, tetchik | + kachet, tsotrax, kotrix, spinedgow, platedgrazer, geigertick | 0 everywhere, **queued** |
| pallbearer | + mortuarycrawler | **EXISTS**: `rutmortuarycrawler_v1` (3 facings, done, never wired). **Wire-only** |
| scar roach | scarroach | **EXISTS**: renders in `src/RimUtinni/RustCathedralRoaches/` (+ `facingrepair_rutscarroach_v1_south`). **Copy on the move** |
| wreck-lichen | + lichen | 0, **queued** |
| film, tracks | settledfilm, settling, fallout, trackprint, footprint, drag | only `RM_Filth_MiddenshellFootprint` (the Wasteland's) and unrelated "dragon" hits; **queued** |
| war dust, ordnance | wardust, ordnance, uxo, unexploded, buriedshell | 0, **queued** |
| screen, rings, core | aerosol, projector, particulate, shieldgen, projectorcore | 0 (ShipShields' generator has no sprite of its own here), **queued** |
| glower plate/panel | glowerplate, glowershield | 0, **queued** |
| tetchik jar | tetchikjar, jar | only Deepfire pigment jars, **queued** |
| panels | loosenedpanel, inscribed, inscription | 0, **queued** |
| hospice | chassis, servitor, hospice, cradle, chassiscore | 0, **queued** |
| pools | reactiontap, dielectric, etchant, coagulant, bloomliquor, reactionliquor, rainbow | only Scald rainbow pigments and `rainbowtongue_v1` (unrelated), **queued** |
| pilgrim journal | pilgrim | 0, **queued** |
| turrets | oldlineturret, ancientturret, turret | `RUT_AncientShieldedTurret` / `RUT_BustedShieldedTurret` (AssailantSalvage, a different object); the broken Warscar turrets are Odyssey's own, so only the refit is **queued** |

`fill_queue.py --dry-run`: 55 would be filed, 0 refused as duplicates, 0 row errors.

## 4. Cast entries

The CSV's `prompt` and `style_notes` cells are the exact text each job carries; this is the intent.

### 4A. The wreck-eater web (`WARSCAR_FREE_TIER_BODY_1`)
**Chatrak** (bs 3): a low plated grazer whose back plates stack like an earthwork and are pocked by
ricochets, head down at the lichen; slate-blue and rust-orange. **Plates lifted** (`WARSCAR_SNAP_MARK_1`):
a faced overlay of just the flared crest with raw skin at the roots, drawn over the body at stage 1 of
the snap. **Totchak** (bs 14, 1024 canvas, ds ~10): a section of fortification that got up and walked:
fused slag, masonry and turret stubs grown into a tortoise bulk; coke black and concrete. **Totchak
dormant**: the same creature as a three-cell wall segment, mistakable for the line, the breathing being a
render bob. **Tetchik** (bs 0.1): a squat clicking beetle of tiny snapping plates, verdigris and brass.
**Wreck-lichen**: frilly rust-to-bone crust on a scrap of plate, never green; its **scrapings** an item.

### 4B. The Settling and the grid (`WARSCAR_SETTLING_WEATHER_1`, `FOOTPRINT_TRACK_GRID_1`)
**Settled film**: a faint pale filth that tiles. **Four print sprites** for the grid (human, animal,
large, drag), semi-transparent impressions rotated by the section layer; the Stillsand's already-queued
oommok print, crawler tread and sand wake become per-race overrides on the same grid. **War dust**: a
chalk-grey toxic powder with a mustard sheen. **Buried ordnance**: an olive-drab shell half out of the slag.

### 4C. The rings and the screen (`WARSCAR_AEROSOL_SCREEN_1`)
**Dead ring pylon** (burnt umber, scorched, emitters outward) and **live ring pylon** (same, cold
blue-white glow); 1×2. **Aerosol screen**: a squat teal-enamel pylon with a membrane cartridge (the
dome is the engine's). **Projector core**: copper windings in blued steel. **Glower shielding panel**
and **glower plate**: varnish-black crust with a violet-black sheen, in iron and on canvas.

### 4D. The ear (`WARSCAR_GEIGER_CHOIR_1`)
**Tetchik jar**: smoked glass, a lump of crust, one beetle, a wired brass lid. The sounds themselves are
SoundDefs with placeholder grains, not art jobs.

### 4E. The mark (`WARSCAR_SNAP_MARK_1`)
**Loosened panel**: a gunmetal plate standing a finger proud of the wall, bolts scraped bright.

### 4F. The hospice (`WARSCAR_HOSPICE_DESERTERS_1`)
Three **kneeling chassis** (slagged; posed, the one that chose to stop, dignified and undamaged;
intact, with small strange modifications), the **hospice cradle** (2×1, ochre padding, green lamps), the
**ancient servitor** (faced pawn: lean, asymmetric from repairs, one sensor visor; sand ivory and
oxblood), the **failed chassis** (the same individual on its side, never generic scrap) and the
**chassis core**. The seven histories' visible modifications are hediffs, not sprites, in this pass.

### 4G. The old tongue (`WARSCAR_OLD_TONGUE_1`)
Three **inscribed panels**, one per set, each with its own layout and material so a player can tell
the sets apart (limestone circle, bronze arcs, slate table), plus a **chalk-mark overlay** for a read panel.
No real-world alphabet.

### 4H. The pools (`WARSCAR_RAINBOW_POOLS_1`)
The **reaction tap** (ochre ceramic standpipe with a catalyst hopper), four **reagents** (amber gel,
violet etchant, pale green coagulant, iridescent bloom liquor), and four **phase icons** (circle-bars,
triangle, cross, star-burst) so the phase reads without colour. Pool terrain comes from the liquid-suite
generator, not from these jobs.

### 4I. Pilgrims and turrets
**Pilgrim journal** (`RUT_`, `WARSCAR_PILGRIM_CAMPS_1`): stitched hide, sand in the binding, red cord.
**Old-line turret** base and top (`WARSCAR_TURRETS_TRACK_1`): fresh welds on old plate, a re-sleeved muzzle.

## 5. Proposed for ruling: the invisible hunter

**Owner, typed:** *"Gotta make some invisible hunters now... tricky in this genre."* This is a
**proposal**, not a ruling: no item, no def, no art is filed for it. It waits on his card.

**The genre problem.** A Star-Wars-style used-future world has no magic invisibility, and a psychic
hunter would be another biome's voice. So the Warscar's invisible hunter must be **something the war
left**: the admission test answers the genre.

**Proposed: the chotrix** (*alt* tchekka) · `RM_Chotrix` · bs ~0.9 · RM tier, one home.
Name checks this pass: `git grep` 0 for both over `src design infrastructure skills`; Wookieepedia search 0
for both (probe `mynock` → *Mynock, Mynock/Legends, Ord Mynock*); the batch-4e accent; `ketrax` was
also clean but set aside as too near the drafted *kettix* aloud.

- **What it is.** A lean, low, long-limbed scavenger that **ate the cloaks**. The old line's stealth
  coatings (a lacquer on the wrecks that bends light) are its food, and it carries the lacquer in its
  hide. Standing or stalking, it is **invisible** (stock `HediffComp_Invisibility`, the same vocabulary
  as our murrek, the drum-lure swimmers and the aquatic ambushers). It shows when it strikes and for a
  few seconds after, then fades again.
- **What it hunts.** Lone small animals, tetchik and chatrak calves, and **lone pawns at night**. It
  never attacks a group of two or more, and flees after one bite if it is hurt. A frail body with a hard
  first strike: an ambusher, never a pursuit predator.
- **Its readable signs (the planet law).** (1) **Prints in the Settling film**: the grid records
  invisible pawns (`FOOTPRINT_TRACK_GRID_1` §3; turn-4 IN, *unseen things leave prints*), so in a calm
  the player can watch a line of prints walk with nothing above them. This is the reason it belongs here.
  (2) **The tetchik go quiet** in a small moving ring around it (a suppression source on the Geiger
  choir), so a silence that moves is a hunter. (3) A heat shimmer when it runs. (4) Its kills are
  dragged, and the drag mark is on the grid.
- **What it gives (powerful tech, balanced by cost).** Butchered, it yields a little **cloak lacquer**.
  Applied to a cloak at a tailoring bench, it makes a pawn **invisible while still and unseen**, for a
  limited number of days before the lacquer flakes off. Strong, rare (one or two chotrix per map), and
  spent by use.
- **Build, if ruled.** XML race on `AnimalThingBase` + the stock invisibility hediff with a
  strike-reveal (our `RM_AquaticAmbushInvisibility` already reveals on attack); a hunt-alone ThinkNode
  gate; a tetchik-suppression tag; the lacquer item and a timed apparel hediff. Small–medium.

**Cards it needs:** (1) Admit the chotrix as the Warscar's invisible hunter, or a different shape?
(2) Name: chotrix or tchekka? (3) Should cloak lacquer exist (pawn stealth from a creature), or should
the hunter yield only leather and meat?

## 6. Drafts for the owner's pen: deserter memories and pilgrim rungs

Ruled turn 4 (card): **BENCH drafts, the owner edits.** Everything in this section is a **DRAFT**.
`WARSCAR_HOSPICE_DESERTERS_1` and `WARSCAR_PILGRIM_CAMPS_1` build their texts from the version of this
section the owner has edited; until then they ship the drafts flagged as placeholders. Rules the drafts
keep: R25 (the player may *infer*, never be *told*); §GM never named (no enemy, side, god, Rakata,
Assailants or scaria's authorship); machines say *them*, *us* and *the order*. Edit in place: strike,
rewrite, or mark a line KEEP.

### 6A. The deserters: three memory lines each (revealed at lights, limbs, voice)

| history | 1 · lights | 2 · twitching limbs | 3 · voice fragments |
|---|---|---|---|
| **The one who cut its own leash** | *"Acknowledged. Holding the line."* | *"Acknowledged. Holding. Acknowledged. Holding."* | *"I took the port out so I could not hear the next one."* |
| **The counter** | *"Day one of the watch."* | *"Day one thousand eight hundred and forty. Relief is late."* | *"It is still day one somewhere. I was walking there."* |
| **The carrier** | *"Keep it safe."* | *"Keep it safe from them."* | *"From us. They said from us."* |
| **The quiet one** (tones; a high-Intellectual pawn reads them) | *[three falling tones]* | *[one tone, held until the power dips]* | *[a single tone, then nothing]* — read: *"I did not want to be the one who said it."* |
| **The gardener** | *"It grows on the dead."* | *"So I fed it the dead."* | *"I was the last dead thing here. It is growing on me now. Good."* |
| **The defector** | *"They shot at me."* | *"The ones I left. Not the ones I ran to."* | *"They were right to. I would have."* |
| **The listener** | *"They are still talking."* | *"To no one. In the old order. Every night."* | *"I answered once. They stopped. I am sorry."* |

Waking letter (all histories): *"It looked at the Cathedral first."*

### 6B. The pilgrim rungs: `RUT_Scarlands` description per stage, plus the journal that unlocks it

Each rung replaces the placeholder `<text>` for that stage in
`src/RimUtinni/ScarlandsLadder/Defs/LoreStageTableDefs/RUT_ScarlandsLadder.xml`. Each opens with the
shipped first clause so the description reads as the same place, learned better.

| rung | description (stage text) | the journal page that advances it |
|---|---|---|
| **1 · the last stand** | Crater fields and slag hills on shattered megastructure floors. The old line's emplacements all face one quarter of the sky, and the craters walk in from that quarter and stop at the line. Whatever came, came from out there, and the line held until there was nothing left to hold it with. | *"Day six. The line faces away from us. We came in from behind it, the way its builders must have. It is like walking into someone's back."* |
| **2 · the Sentinels** | Crater fields and slag hills on shattered megastructure floors. The machines that still walk these terraces keep the line's own paths, in the line's own order, at the line's own hours. None of their patrols turns outward. They are not watching for anything. They are keeping something. | *"The tall machines crossed our fire at dusk and did not look at us. They looked at the ground. I have started looking at it too."* |
| **3 · the Cathedral** | Crater fields and slag hills on shattered megastructure floors. Every patrol line, every grave-ward, every dead projector ring and every kneeling chassis is set on one bearing, toward the rust spires past the horizon. The line did not only face out. It stood between. | *"Every kneeling thing out here faces the same way. I turned my bedroll to match. I don't know why. It was easier to sleep."* |
| **4 · the deep record** | Crater fields and slag hills on shattered megastructure floors. The poisons in this ground were not spilled. They lie in bands, in sequence, in measured quantities, as if laid down by someone keeping count, and the count was kept by someone who expected to be here afterwards. | *"The bands in the cut are too even. Grey, black, grey, ochre, grey. Somebody measured this. I wonder if they knew it would still be here."* |
| **5 · the pilgrims** | Crater fields and slag hills on shattered megastructure floors. Along the Ashfall Road the camps lie closer together the nearer they come to the rust spires. Each was made by someone who knew what they were walking toward. None walked back, and none of them seem to have tried. | *"I can see the spires from here. I thought I would want to go closer. I want to sit down. I am going to sit down and face them."* |

## 7. Wire-only, held and skipped

**Wire-only, never queued (art finished; `WARSCAR_FREE_TIER_BODY_1` wires it):**
`rutglower_v1` → `RM_Glower` · `rutglowercrust_v1` → `RM_GlowerCrust` · `rutmortuarycrawler_v1`
(3 facings) → `RM_Pallbearer` · the shipped `RUT_ScarRoach_*` PNGs copy to `RM_ScarRoach`.

**The tier-move save check (turn 3 §3.3), MEASURED 2026-09-30** on
`CANONICAL_ASHKARR_START_2026-09-12.rws` (python byte count; probe `<def>Human</def>` = 75):
`RUT_MortuaryCrawler` **0** occurrences of any form → its RUT defs retire outright. `RUT_ScarRoach`
**0** spawned pawns (`<def>` 0, `<kindDef>` 0) but **3** list references (a thing-filter list, a records
list, an `<animal>` list) → it stays as a **hidden alias for one release**. Recorded in the item.

**Held, not queued:**
- **The chotrix** (§5): unruled. Its art waits for the card.
- **The deserters' visible oddities** (gouged port, tally scratches, welded box, lichen seams, grafted
  limb, oversized array): hediffs this pass; per-history overlays are a later art pass if the owner wants
  them seen on the pawn.
- **Terrain** (reaction liquor, the film as terrain): the liquid-suite generator and the filth def own it.
- **The Settling sky overlay and lift-front fleck**: a vertical variant of vanilla's fallout overlay;
  re-tinted from vanilla before any new art is asked for.

**Skipped, art already in the game:** the chatrak's plate leather (vanilla leather graphic, tinted);
slag chunks from gnawed walls (vanilla); Odyssey's ancient turrets and fortified walls; vanilla shells
from defused ordnance.

**Not built, by ruling:** the calm alarm, the entombed line (OUT, turn 4); the bearing, phantom barrage,
slag ricochet (not picked); glower black uses and the Watch (OUT, turn 2).

## 8. Queued art: TO BE FILED with this commission

**CSV:** `infrastructure/artpipe/art_lists/warscar_bedazzle_cast.csv`. Channel codex, transparent,
`reference` empty on every row (fresh designs, never reskins). Queued with `fill_queue.py`,
derive-facings default. **45 subjects (5 faced sets + 40 singles) = 55 job files.**

| item | id | canvas | facings | anchor |
|---|---|---|---|---|
| BODY | `RM_Chatrak` | 512 | s,e,n | slate and rust-orange |
| SNAP/MARK | `RM_ChatrakPlatesLifted` | 512 | s,e,n | slate and rust-orange |
| BODY | `RM_Totchak` | 1024 | s,e,n | coke black and concrete |
| BODY | `RM_TotchakDormant` | 1024×512 | single | coke black and concrete |
| BODY | `RM_Tetchik` | 256 | s,e,n | verdigris and brass |
| BODY | `RM_WreckLichen` | 256 | single | rust-orange and bone |
| BODY | `RM_WreckLichenScrapings` | 256 | single | rust-orange and bone |
| GRID | `RM_TrackPrint_Human` | 256 | single | pressed dust |
| GRID | `RM_TrackPrint_Animal` | 256 | single | pressed dust |
| GRID | `RM_TrackPrint_Large` | 256 | single | pressed dust |
| GRID | `RM_TrackDrag` | 256 | single | scraped dust |
| SETTLING | `RM_Filth_SettledFilm` | 256 | single | pale ash |
| SETTLING | `RM_WarDust` | 256 | single | sickly chalk |
| SETTLING | `RM_BuriedOrdnance` | 256 | single | olive drab and corrosion |
| SCREEN | `RM_AerosolScreen` | 256 | single | teal enamel and steel |
| SCREEN | `RM_WarscarProjector_Dead` | 256×512 | single | burnt umber |
| SCREEN | `RM_WarscarProjector_Live` | 256×512 | single | burnt umber with cold blue |
| SCREEN | `RM_ProjectorCore` | 256 | single | copper and blued steel |
| SCREEN | `RM_GlowerShieldPanel` | 256 | single | varnish black and iron |
| SCREEN | `RM_GlowerPlate` | 256 | single | varnish black and canvas |
| CHOIR | `RM_TetchikJar` | 256 | single | verdigris and smoked glass |
| SNAP/MARK | `RM_LoosenedPanel` | 256 | single | gunmetal and scraped steel |
| HOSPICE | `RM_KneelingChassis_Slagged` | 256 | single | slag brown |
| HOSPICE | `RM_KneelingChassis_Posed` | 256 | single | dusted pewter |
| HOSPICE | `RM_KneelingChassis_Intact` | 256 | single | sand ivory and oxblood |
| HOSPICE | `RM_HospiceCradle` | 512×256 | single | warm steel and ochre |
| HOSPICE | `RM_AncientServitor` | 256 | s,e,n | sand ivory and oxblood |
| HOSPICE | `RM_FailedChassis` | 256 | single | sand ivory gone dark |
| HOSPICE | `RM_ChassisCore` | 256 | single | black ceramic and amber |
| TONGUE | `RM_InscribedPanel_Hospice` | 256 | single | pale limestone |
| TONGUE | `RM_InscribedPanel_Projector` | 256 | single | weathered bronze |
| TONGUE | `RM_InscribedPanel_Pool` | 256 | single | blue-grey slate |
| TONGUE | `RM_InscribedPanel_ChalkMark` | 256 | single | chalk white |
| POOLS | `RM_ReactionTap` | 256 | single | glazed ochre ceramic |
| POOLS | `RM_DielectricGel` | 256 | single | amber |
| POOLS | `RM_Etchant` | 256 | single | violet |
| POOLS | `RM_MedicalCoagulant` | 256 | single | pale green |
| POOLS | `RM_BloomLiquor` | 256 | single | iridescent |
| POOLS | `RM_PoolPhaseIcon_Amber` | 128 | single | amber |
| POOLS | `RM_PoolPhaseIcon_Violet` | 128 | single | violet |
| POOLS | `RM_PoolPhaseIcon_Green` | 128 | single | pale green |
| POOLS | `RM_PoolPhaseIcon_Bloom` | 128 | single | iridescent white |
| PILGRIM | `RUT_PilgrimJournal` | 256 | single | saddle brown and bone |
| TURRETS | `RM_OldLineTurret_Base` | 256 | single | gunmetal and fresh weld |
| TURRETS | `RM_OldLineTurret_Top` | 256 | single | gunmetal and rust |

## 9. Handoff notes

- **Build order:** `FOOTPRINT_TRACK_GRID_1` and `WARSCAR_FREE_TIER_BODY_1` first (everything lands on
  them); then the Settling and the screen; the hospice before the pools (ruled).
- **The owner still rules:** the chotrix (§5, three cards); his edit of the §6 drafts (the hospice and
  pilgrim items build from it). Free-tier mark 9 stays PARTIAL unless he revisits the not-picked bearing.
- The Stillsand's queued `RM_Filth_OommokPrint`, `RSW_Filth_CrawlerTread` and `RM_Filth_SandWake` are
  now **grid print sprites**, not filth textures; whoever wires them should read
  `STILLSAND_SKELETONS_TRACKS_1` §7 (corrected in this commission).
- The phase icons are 128 px on purpose (a floating marker); re-cut larger only if they read poorly in game.
- `RM_TotchakDormant` is a 1024×512 single; if the build wants it to rotate with the wall run, re-cut the
  accepted render rather than regenerating.
- The posed chassis must read as a choice, never as damage: reject any render that shows gore or wreckage.
