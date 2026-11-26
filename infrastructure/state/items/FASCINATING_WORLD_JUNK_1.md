# FASCINATING_WORLD_JUNK_1 — every wreck on the map is a flavour of ice cream to a Jawa

Owner, 2026-09-12, at the bench, minutes after the first landing at Zeddo's Yard,
verbatim:

> *"we really need to reskin all the old junk around the map that looks like tanks,
> trucks, cars, etc. to be more Star Wars wreckage focused. that's a big ticket: first
> scan for what it all IS anyway, and specifically scan through donor mods set for
> removal like urban ruins just to get ideas. Then decide on the roster we actually
> want spawning, and finally re-graphic and re-text them to make the world come alive
> by... being dead, in the right flavor. Lots to do here. Call that ticket
> FASCINATING_WORLD_JUNK because that's what it should be! This is a scavving game: so
> what ARE all the kinds of junk out there already? They are like flavors of ice cream
> to a Jawa. Let's get creative!"*

## the ask
Ash'karr's maps are scattered with vanilla-earth wreckage — ancient tanks, trucks,
cars, mech drop beacons, generic "ancient" junk — that reads as a crashed 21st-century
motorway, not a Star Wars scrapworld. This is a scavenging campaign: the wreckage IS the
content. Every kind of junk a Jawa walks past should be legible as *what it was, what
it yields, what it risks* — a flavour. The programme: know what exists → borrow shapes
from the donors we are about to throw away → rule the roster → re-graphic and re-text.

Relations:
- `PLAYER_START_SITE_1` — Zeddo's Yard (the Hutt junkyard, "a mountain of the galaxy's
  discards") is the showcase; whatever roster lands here is what the player sees first.
- `design/Jawa/worldbuilding/fall_line.md` (FROZEN): the Fall Line's wreckage is
  **fresh** — "Nothing here is old" — renewable, Empire-claimed. The yard is downstream
  accumulation; the Rakatan megastructure debris is a third, ancient register. Three
  ages of junk, and the roster must keep them distinct.
- `MOD_OPTIONS_RETROFIT_1` — the standing Mod Settings rule applies to whatever ships.
- `design/NAMING_SCHEME_PLAN.md` — new defs are `RSW_` (any Star Wars game) unless
  campaign-specific (`RUT_`).

## spec
Four phases, each a sitting-sized deliverable.

### Phase 1 — CENSUS: what IS all the junk, and who spawns it
MEASURED off the live def dump and `measure`, never a grep guess (`0` means measured
zero; ignorance answers `UNMEASURED`). Every ThingDef that map generation scatters as
wreck / junk / ruin / debris:
- vanilla `Ancient*` (AncientTank, AncientCar, AncientTruck, AncientMechDropBeacon,
  AncientLamp, AncientFence, AncientTerminal, ship chunks, crashed-ship parts, mech
  cluster debris, etc.) and Odyssey scrap/wreck things;
- Vanilla Expanded props & decor, VFE Ancients / Ancient Urban Ruins
  (`xmb.ancienturbanruins.mo`, `meteores.ancienturbanruins*`), Alpha Biomes derelicts
  (`AB_Derelict*`), KOTOR core and Outer Rim salvage defs, Dungeon Pack / GMMP dungeon
  furniture that lands outdoors;
- our own: `StructureInjectionsRUT` templates (`broken_ring.txt` etc.),
  `RM_WreckedMachines`, `RM_Graffiti*`, the Fall Line deposition set.
For each def: **what spawns it** (GenStep, TileMutatorDef, LandmarkDef, structure
template, KCSG layout, quest), `texPath`, label + description, and **count seen on a
real map** (the Zeddo's Yard arrival map and one Fall Line map — `jawa/list_things`,
whole map, by def). Then a **contact sheet of the real sprites** for the owner to LOOK
at, built the `rimworld-content-moderation` way (render straight from the defs, loose
PNG or AssetBundle — `reading-rimworld-graphics`). Deliverable:
`design/Jawa/worldbuilding/junk/junk_census_<date>.md` + the sheet.

### Phase 2 — IDEAS: mine the donors we are about to retire
Read-only pass over the mods slated for removal (the urban-ruins family, and whatever
the current retirement list names — check the ledger for `*_RETIRE_*` / donor
retirement items before assuming): pull every wreck/ruin/debris shape, silhouette and
description that is worth keeping *as reference* into
`design/Jawa/worldbuilding/junk/donor_ideas.md` with the texPath and the source mod.
Retirement itself is another item's business; this phase takes notes, it never
uninstalls. Add non-mod references the owner may want: Jawa sandcrawler yards,
Jakku's Starship Graveyard, Raxus Prime, Bracca (the Scrapper Guild), Lotho Minor.

### Phase 3 — ROSTER: the flavours (owner sitting, by cards)
Card the roster to the owner, one card per junk *kind*, simple language, each with its
trade. A kind is named for what a scav reads in it — **what it was, what it yields, what
it risks** — e.g. a burnt-out speeder chassis (yields plasteel and a working
repulsorlift one time in ten; risks nothing), a cracked droid carapace (yields
components; risks a live restraining bolt), a fallen TIE panel (yields the Empire's
attention if hauled in bulk — ties to the concealment arc's volume rule), a
half-buried Rakatan spine (yields nothing a scav can lift; risks waking what sleeps
under it). Per **region**:
- **Fall Line** — fresh, Imperial, renewable (frozen sheet's law; no "old" here);
- **Zeddo's Yard / Hutt accumulation** — decades of hauled discards, sorted by nobody;
- **Rakatan megastructure debris** — ancient, alien, and mostly not junk at all;
- plus the biome-specific extras (Rust Cathedral roach-cleaned scrap, the Wreck Fields
  injection layer, sea-floor hulks for the diving arc).
The card set also decides what is CUT from spawning (the tanks, trucks and cars go
unless a card keeps one under a new skin). Deliverable: the ruled roster as data
(`design/Jawa/worldbuilding/junk/junk_roster.json`), not prose, so generators can
read it.

### Phase 4 — RE-GRAPHIC + RE-TEXT
- Sprites: commission-first through the art pipeline daemon
  (`generating-rimworld-sprites`; ART_PIPELINE_DAEMON_1 queue), canvas and silhouette
  bound to the def's `drawSize`/footprint; validate offline before any load.
- Binding: texture binds by **texPath**, not defName (memory
  `texture-binds-by-texpath-not-defname`) — a retexture override mod
  (`mandrake.rsw.<x>artoverride` pattern) for donor defs we keep, new `RSW_`/`RUT_`
  defs for kinds that do not exist yet, and the spawner (mutator / structure template /
  scatterer) repointed at the roster.
- Text: label + description in the scavenger register (what it was, what it yields,
  what it risks) — every def in the ruled roster, no vanilla-earth nouns left
  ("truck", "car", "tank" are gone from the player's screen).
- Mod Settings: on/off per major mechanic (junk reskin on/off; roster spawning on/off
  per region), defaults = shipped behaviour, all-off degrades to vanilla.

## verify
- A real arrival map at Zeddo's Yard, screenshotted: **zero** tanks/trucks/cars
  visible; every wreck on it resolves to a def in `junk_roster.json` (MEASURED by
  `jawa/list_things` over the whole map, diffed against the roster — say the count);
  the owner LOOKS at the screenshot and at the contact sheet before and after.
- One Fall Line map the same way, and its wrecks read fresh, not old.
- A load on the small list of StarWarsPatches and FallLineArrivals, zero new Config errors; every retextured def renders
  (no magenta). Full-list testing is retired until integration (CLAUDE.md §Mod development runs on small lists).

## criteria
- A freshly generated map on the current build carries no def that the roster cuts, every junk def on it is in a kept
  kind, and no junk label on it says car, truck or tank (live, the whole map by `jawa/list_things`).
- In the running game, the Fall Line mutator carries the no-old-junk step and a junk factor of 0.
- A judge (a delegated taste call, CLAUDE.md §Only five acts stay his) looks at a screenshot of that map and at the
  roster contact sheet, and finds the wrecks read as Star Wars scavenger junk.

## refs
file: design/Jawa/worldbuilding/junk/junk_roster.json
file: src/RimStarWars/StarWarsPatches/Patches/AncientJunk_RosterCut.xml
file: src/RimStarWars/StarWarsPatches/Patches/AncientJunk_RosterText.xml
file: src/RimUtinni/FallLineArrivals/Defs/GenStepDefs/RUT_FallLine_NoOldJunk.xml
file: src/RimUtinni/FallLineArrivals/Source/FallLineArrivalsMod.cs

## status

**Phase 1 (CENSUS) — complete, 2026-09-13.** Full writeup:
`design/Jawa/worldbuilding/junk/junk_census_2026-09-13.md`. Summary: RimSage only
indexes vanilla+DLC (`Defs/{Core,Royalty,Ideology,Biotech,Anomaly,Odyssey}`), never
third-party or our own mods — the def dump (rebuilt this session from an
already-captured `DefDump/`, 594 mods, offline, no bridge/game load) carried
everything else. Found: the vanilla/DLC `AncientJunkClusters` GenStep family
(wired into every common map generation via the active Ideology expansion) is the
actual source of "crashed motorway" junk on every map — full def/texPath/GenStep
detail in the census. `xmb.ancienturbanruins.mo` (735 ThingDefs) is confirmed as
the prime Phase 2 donor. KOTOR core and Outer Rim core are **negative findings**
(no wreck-scatter content — resource/apparel packs). VFE Props and Decor (1805
ThingDefs) has no GenStep/TileMutator of its own — decoration catalog only.
`mandrake.rut.injections` (StructureInjectionsRUT) is fully authored in the repo
but **not in the currently active mod list**. `RSW_CrashedShip` / `RSW_PodracerWreck`
are active but their own source comments say "NOT YET PLACED on any Ash'karr tile."
Live per-map counts (Zeddo's Yard, Fall Line) and the contact sheet were **not**
attempted — both need the bridge/more session time and are explicitly deferred,
per the census's own "what Phase 2 needs" section.

**Phase 2 (IDEAS) — complete, 2026-09-13.** Appended to the same census doc
(`design/Jawa/worldbuilding/junk/junk_census_2026-09-13.md`, "Phase 2 — ideas mined
from retiring donors") rather than a separate `donor_ideas.md`, to keep one
document per the "inaccurate material is deleted, not superseded" discipline and
avoid a second file the owner has to cross-reference. Findings: read `xmb.
ancienturbanruins.mo`'s own XML on disk directly (RimSage doesn't index it; a prior
deep audit, `design/Jawa/mods/ancient_ruins_mod_audit.md`, already triaged its
content as uniformly non-Star-Wars but hadn't looked at shape/silhouette value
independent of the earth-flavor text — that's what this pass adds). **6 borrowable
shapes found**, each with real def size/drawSize/texPath to bind a reskin to:
`AM_AbandonedBus` (3×8, big single-orientation hull), `AM_FireTruck` (7×3, wide
armored-vehicle silhouette), `AM_AncientTruckCarriages`/`AM_FreightTrainCarriages`
(3×5, cargo-module/carriage shape), `AM_Amublance` (5×2, small vehicle,
`Graphic_Single`), `AM_AbandonedForklift` (2×4, cargo-loader shape),
`AM_AVendingMachine` (1×1, smallest tier, interior/kiosk dressing). Everything else
in the mod (rubble/rebar, mall shells, modern firearms, CPU/GPU/credit-card loot,
the body-horror faction) is confirmed dead weight, no shape worth a card.
`mlie.dungeonpack` and `gmmp.dungeon` are **negative findings** — read their def
files directly: Dungeon Pack has 7 ThingDefs total (traps/turrets, no wreck
silhouette at all); GMMP Dungeon is fantasy-dungeon dressing (gibbet cages, bone
piles, generic rubble) with no tech/vehicle register. Neither needs further mining.
`neronix17.outerrim.furnitureanddecor` was explicitly **not** mined this pass —
it's already Star-Wars-themed content, so mining it for "ideas to reskin as SW" is
circular, and it isn't a near-term retirement (Wave 3, entangled with
`DROID_SYSTEM_BUILD_1`); its Phase-1 open question (does anything actually spawn
its junk PropDefs as map content) is a spawn-mechanism question, not a shape-mining
one, and stays deferred. Added the item's requested non-mod references (Jawa
sandcrawler yards, Jakku's Starship Graveyard, Raxus Prime, Bracca/Scrapper Guild,
Lotho Minor) each tied to one of the three registers (Fall Line fresh / Zeddo's
Yard accumulation / Rakatan ancient).

**Phase 3 (ROSTER) — built 2026-11-11 at `29b71f8f34`, as a delegated design call.** The owner's card of 2026-10-09
("appearance now, flavours later") ordered the phases, and the appearance work shipped first (STARWARS_JUNK_RESKIN_1,
done). The roster is data: `design/Jawa/worldbuilding/junk/junk_roster.json` (regions, kinds with what each was,
yields and risks, the kept defs, the cut defs and the cut prefabs). The owner can overrule any row.

**Phase 4 (RE-GRAPHIC + RE-TEXT) — built 2026-11-11 at `29b71f8f34` and `274e6da319`.**
- The cut patch `src/RimStarWars/StarWarsPatches/Patches/AncientJunk_RosterCut.xml` and the re-text patch
  `AncientJunk_RosterText.xml` are generated from the roster by `gen_junk_roster_cut.py`. Edit the roster, never the XML.
- The vehicle and war-machine defs carry the judged Star Wars art of STARWARS_JUNK_RESKIN_1.
- On Fall Line tiles, `RUT_FallLine_NoOldJunk` (`src/RimUtinni/FallLineArrivals/`) prevents the vanilla old-junk
  steps, and the mutator's junk factor is 0.
- Mod Settings: `junkRosterCut` (StarWarsPatches) and `noOldJunk` (FallLineArrivals), both default on; off is vanilla.
- Offline proof: `selftest_junk_roster.py`.

**Live step — done 2026-11-26 on SteveDesktop (work bundle WB-game-dungeons-and-wreckage-20261126-171519).**
`prove_junk_roster_live.py` (proof file `infrastructure/state/live_proofs/FASCINATING_WORLD_JUNK_1.txt`):
- A1, a fresh quicktest map read whole by `jawa/list_things`: the first real reading FAILED, because five defs stood in no
  roster kind (Biotech's exostrider remains, which the census never read, and the hermetic crate of ruins and
  complexes). The roster now has the kind `fallen_assault_walker`, and the crate sits in `old_tech` (039ac93be3). Then
  A1 PASS: 622 junk things, 30 defs, none cut, none in no kind, no car/truck/tank label (J20261126T210118Z-43bce0).
- A2, the loaded RUT_FallLine mutator: junk factor 0, the no-old-junk step listed, the setting on (PASS).
- `design/Jawa/worldbuilding/junk/junk_live_seen.json` pins each live reading; `selftest_junk_roster.py` holds every
  def in it to a kept kind or the cut list.
- The proof's list carries StarWarsRaces: without it StarWarsPatches' AlienSpawnEnablers PawnKindDefs load with no race
  and no quicktest map generates.

**Open: the judge's look** (a delegated taste call, routed on the shape): a screenshot of a fresh map on this build at
play zoom, and a contact sheet of the roster's sprites, judged by `design/RimMandrake/art_judge_brief.md`. The contact
sheet of 2026-11-11 (git `8130ec9f07:whittle/fascinating_world_junk_1/evidence/roster_contact_sheet.png`) predates the
`fallen_assault_walker` kind.

## traps
- Donor art is **loose PNG vs AssetBundle** — a texture that "does not exist" on disk
  can still render; use `reading-rimworld-graphics` before declaring anything missing.
- `StructureInjectionsRUT` templates carry their **own defNames** — a roster cut on
  the scatterer alone leaves the injected copies standing.
- A **retextured donor def is invisible to defName denylists** — the tanks may already
  hide under a mod prefix (`defname-denylist-misses-retextures`).
- **Cherry Picker cuts are invisible to the dump** (commonality 0, not a missing def) —
  the census must read the live game or the cut list, not the dump alone.
- The dump drops whole fields (`def-dump-has-no-statbases`): `texPath`/graphicData come
  from the mod XML, not the dump.
- Generic `Ancient*` defs are referenced by quests and KCSG layouts — deleting a def
  breaks a layout silently; **reskin, never delete**, unless a grep of every
  `.txt`/`.xml` layout proves zero references.
- A patch that matches nothing logs nothing.
