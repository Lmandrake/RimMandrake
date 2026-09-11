# West End Games Star Wars D6 (1987-1999) — dungeon-design mining report

Scope: WEG's D6 Star Wars RPG line only. Siblings own FFG/Saga/d20 (SW-MODERN),
KOTOR/Jedi games (SW-VIDEOGAMES), non-Star-Wars derelict RPGs (SCIFI-DERELICT).

## Retrieval method and what it means for confidence

- `WebSearch` 400-erred as predicted. Fetcher was running but had a long shared
  queue (30-40+ requests from sibling agents); rather than wait, I confirmed
  direct network egress works from this sandbox (`curl` succeeds against
  archive.org) and used that plus `WebFetch` throughout. All acquisition below
  is via archive.org's public API/download endpoints, not Fetcher.
- **The mother lode**: archive.org item `adventure-journal-2` (titled "Star
  Wars West End Sourcebooks") is a 28.6 GB, 183-file collection containing
  **every single title on the owner's lead list**, each under its real WEG
  catalog number, as an individual EPUB. This item is CONFIRMATION that all
  15 adventure titles in the prompt are real WEG products — I did not have to
  guess or infer this from a wiki.
- **Critical caveat — these EPUBs are DRM-locked.** I downloaded
  `WEG40005 Tatooine Manhunt_lcp.epub` (24.8 MB) and unzipped it: it contains
  a `META-INF/encryption.xml` declaring AES-256-CBC Readium LCP encryption on
  every page and image. The page HTML is ciphertext, not text. Every other
  file in that collection sharing the `_lcp.epub` naming is the same DRM
  wrapper. **I could not open any of these.** This is why the specific
  adventures (Tatooine Manhunt, Scavenger Hunt, Otherspace II, Strike Force
  Shantipole, Battle for the Golden Sun, Crisis on Cloud City, Graveyard of
  Alderaan, Riders of the Maelstrom, Black Ice, Domain of Evil, Supernova,
  Twin Stars of Kira, Instant Adventures, Classic Adventures vols 1-5, Death
  in the Undercity, Black Sands of Socorro, and others) are marked UNREACHED
  below despite being confirmed real. Do not treat "exists in the catalog" as
  "I read it" — I did not fabricate room lists for any of these; I simply
  could not open the file.
- **What WAS reachable**: separate, non-DRM archive.org items (standalone
  scans with OCR `_djvu.txt`/PDF, not the DRM collection) exist for several
  titles. I downloaded the plain-text OCR for these and read them directly —
  this is genuine CONFIRMED full-text access, saved verbatim to
  `research/game_design/sources/sw_d6/`.

## Full corpus catalog (from `adventure-journal-2` metadata — CONFIRMED to exist, catalog numbers real)

Every filename below is a real WEG SKU pulled from the collection's file
listing (`https://archive.org/metadata/adventure-journal-2`). Owner's lead
list cross-referenced:

| Owner's lead term | Real WEG title & SKU found | Reachable full text? |
|---|---|---|
| Tatooine Manhunt | WEG40005 Tatooine Manhunt | NO — DRM (see above) |
| Graveyard of Alderaan | WEG40019 Graveyard of Alderaan | NO — DRM |
| Starfall | WEG40016 Starfall | NO — DRM |
| Otherspace | WEG40018 Otherspace | **YES** — standalone item `Otherspace` |
| Otherspace II | WEG40028 Otherspace 2 Invasion | NO — DRM |
| Strike Force: Shantipole | WEG40009 Strike Force Shantipole | NO — DRM (only a Swedish fan-translation booklet found separately, not verified) |
| Battle for the Golden Sun | WEG40017 Battle for the Golden Sun | NO — DRM |
| Crisis on Cloud City | WEG40022 Crisis on Cloud City | NO — DRM |
| Riders of the Maelstrom | WEG40021 Riders of the Maelstrom | NO — DRM |
| Black Ice | WEG40030 Black Ice | NO — DRM |
| Domain of Evil | WEG40034 Domain of Evil | NO — DRM |
| Scavenger Hunt | WEG40020 Scavenger Hunt | NO — DRM |
| Supernova | WEG40066 Supernova | NO — DRM |
| Classic Adventures (vols) | Vols 1-5: WEG40083/40128/40133/40138/40165 | NO — DRM |
| Instant Adventures | WEG40137 Instant Adventures | NO — DRM |
| Twin Stars of Kira | Twin Stars of Kira: New Republic WEG40060 | NO — DRM |
| Goroth: Slave of the Empire | WEG40098 Goroth Slave of the Empire | **YES** — standalone item `goroth-slave-of-the-empire` |
| Death Star Technical Companion | WEG40008 | **YES** — standalone item `the-death-star-technical-companion` |
| Galaxy Guide (Tatooine vol) | Galaxy Guide 7: Mos Eisley WEG40069 | **YES** — standalone item `galaxy-guide-7-mos-eisley-weg-40069` |
| Planets of the Galaxy | Vols 1-3: WEG40050/40057/40072 | **YES** — all 3, standalone items |
| Gundark's Fantastic Technology | Gundarks Fantastic Technology Personal Gear WEG40158 | **YES** — standalone item |
| Galladinium's Fantastic Technology | WEG40025 | **YES** — standalone item |
| Creatures of the Galaxy | WEG40080 | **YES** — standalone item |
| Star Wars Sourcebook | Two editions found (`starwarssourcebo0000smit`, `starwarssourcebo0000bill`) | OCR available, not yet read (time-boxed out) |

Additionally confirmed to exist (not on the owner's lead list, worth flagging
for later pulls): **Darkstryder Campaign** (4-book flagship linked campaign —
WEG40209 + Kathol Outback WEG40118 + The Kathol Rift WEG40121 + Endgame
WEG40112), **Mos Eisley Adventure Set** WEG40212 (**YES, reachable** — a
different, non-DRM standalone item exists for this exact box set), **Lords of
the Expanse** (Tapani Sector mini-campaign, 6 books), **Han Solo and the
Corporate Sector Sourcebook**, **Hideouts & Strongholds**, **Wretched Hives of
Scum & Villainy**, **Cracken's Threat Dossier/Rebel Field Guide/Rebel
Operatives**, and the full **Star Wars Adventure Journal** (issues 1-15 +
"Best of 1-4" compilation) which is itself a trove of short WEG-published
adventures per issue — UNREACHED for per-issue contents in this pass, flagged
as the single highest-value target for a follow-up pull (all 15 issues have
OCR `_djvu.txt` sitting right there in the same collection, unlike the
DRM'd single-adventure modules).

## CONFIRMED deep finds (I read the actual text)

### 1. Mos Eisley Adventure Set (WEG40212) — `sources/sw_d6/mos_eisley_adventure_set_djvu.txt`
Box contents per its own introduction: an adventure booklet, Galaxy Guide 7:
Mos Eisley, and a 17"x22" two-sided miniatures map of downtown Mos Eisley +
the cantina. Adventure booklet contents (verbatim ToC): **Vested Interest**,
**There's Many A Slip Betwixt Cup and Lip**, **Harvest Day**, **The Passage
from Perdition**, **A Line in the Sand** (miniatures scenario), **New
Republic Adventure Hooks**.

- **"Vested Interest" (full read)** — a chase/rescue plot, not room-crawl:
  NPC Zogrov begs PCs to stop his friend Beeyon Nace from being blackmailed
  by Ccalras Corp (a Jabba front). Structure: confront Nace → find datachip
  (planted evidence trigger) → stakeout at Lucky Despot Hotel → tail a Duro
  through the city (chase obstacle: thugs from an earlier unrelated
  misadventure recognize the PCs — a **callback/reputation trigger**, not
  scripted) → a pair of Jawas on a ronto crossing the street is the
  *escape valve* obstacle (staging note explicitly says this is placed to let
  PCs shake pursuers) → captive-rescue at a safehouse → the "rescued" love
  interest Eila is revealed as a **con**, flipping the adventure's apparent
  resolution into a second ambush. Ends with a moral-compromise hook (help
  Jabba's smuggling in exchange for protection). GM staging notes explicitly
  call out which encounters ("positive encounter with Balu") are designed to
  seed the *next* adventure in the booklet — deliberate adventure-to-adventure
  threading via a recurring NPC contact, confirmed in the text.
- **"A Line in the Sand" (full read)** — a 3-faction miniatures battle
  (Empire vs. Mos Eisley Militia vs. swoop gang) set entirely inside Docking
  Bay 87. Real tactical map elements, verbatim: sheer unclimbable walls
  (one level, swoops can fly over), cargo-crate cover that can be pushed,
  4 entry doors + 2 stairwells + a balcony, a Primary Cargo Door (opens
  end-of-turn) and 3 Secondary Cargo Doors (opens end-of-*next*-turn) each
  with inside/outside control panels — a real timed-mechanism puzzle. **Hidden
  trap**: Imperial player secretly marks 2 of the placed crates with an "X";
  arming takes a full turn adjacent, then any figure within 1" detonates a
  Damage-7 grenade blast (2.5" radius template) — a classic ambush-trap
  mechanic reusable directly for a RimWorld IED/sabotage dungeon beat.

### 2. Galaxy Guide 7: Mos Eisley (WEG40069) — `sources/sw_d6/galaxy_guide_7_mos_eisley_djvu.txt`
**This is the single richest map-template source found.** It is a location
sourcebook built entirely as a set of numbered, keyed floorplans — exactly
the "room-by-room" format requested. Verbatim room lists captured for:

- **Docking Bay 94** (14 numbered areas): 1. Office, 2. Restroom,
  3. Maintenance Garage, 4. Ship Supplies, 5. Passenger Entrance (blast door,
  Str 6D), 6. Back Blast Ceiling Vent, 7. Sand Trap (electrostatic
  repellers keep sandstorms out of the pit — direct desert-hazard dressing),
  8. Fusion Generators, 9. Landing Lights, 10. Docking Pit, 11. Entrance Ramp,
  12. Tractor Beams (2 of 8 are failing — a maintenance-debt plot hook),
  13. Service Entrance, 14. Customs Inspector's Office (cross-referenced to a
  different location's key elsewhere in the book — an explicit
  location-to-location link).
- **Mos Eisley Cantina** (7 areas): 1. Entrance And Droid Detector (droids
  physically barred — a diegetic access-control puzzle for droid PCs/allies),
  2. Booth (7), 3. Bandstand, 4. Back Hallway (three separate routes to the
  basement: back stairs, an office trapdoor, and the power-room access
  shaft — redundant connectivity, a real branching structure), 5. Office
  (hidden trapdoor + a decoy "explosives" crate that's actually the cash
  stash), 6. Bar (hidden floor hatch), 7. Power Room.
- **Mos Eisley Police Station / detention block** (16 areas) — the closest
  thing to a classic sealed-structure dungeon: 1. Desk Clerk (bank of
  monitors on all 4 cells + entrances/roof/basement; door lock = Moderate
  security roll or trips an alarm), 2. Fines & Permits, 3. Property Room
  (retina-scan/mugshot processing), 4. Detective Offices (5, 2 empty),
  5. Chief's Office, 6. Questioning Room (keypad, Easy security to pick),
  7. Visitation Room (transparisteel divider, Str 3D — a *deliberately weak*
  wall, i.e. an intended breakout weak point), 8/9. Locker/Rest Rooms,
  10. Security Doors (2, Moderate security/Str 6D), 11. Perimeter Alley (sole
  access route to the cells — a chokepoint), 12. Duty Station (elevated,
  watches all 4 cells), 13. Cell (4) (one-way mirror Str 6D on the
  duty-station side, iron bars Str 4D/Easy pick on the *opposite* side —
  asymmetric defense, a real "which side do you attack from" puzzle),
  14. Speeder Parking, 15. Ladder (roof-to-lot), 16. Speeder Ramp
  (sand-trap-covered ramp to a basement garage).
- **Lucky Despot Hotel** (19 areas, luxury-hotel dungeon: turbolifts, service
  turbolifts, function rooms, "Native Tatooine Sandcastings" gift shop
  display) and **Jabba's Townhouse** (10 areas: Main Entrance, Guest Quarters
  x4, Lounge, Employee Entrance/Storage, Dining Room, Kitchen, Bathrooms
  w/ hidden entrance, Monitoring Station, Conference Rooms x2 blast-shielded,
  Audience Chamber) both fully keyed in the text but not transcribed room-by-
  room here for space — full verbatim text is in the saved file, grep for
  "1. Main Entrance" and "1. Entrance And Droid Detector".
- **Chapter Three: Adventure Ideas** gives short hooked scenario outlines by
  episode ("Spice Runner's Gamble" — Episode One: rumor-gathering triggers a
  tail-and-lose-the-tail beat exactly like "Vested Interest"; Episode Two:
  a meet at an abandoned Docking Bay 56 is an explicit trap-you-know-is-a-trap
  setup) — reusable low-effort hook templates.

### 3. Death Star Technical Companion (WEG40008) — `sources/sw_d6/death_star_technical_companion_djvu.txt`
Facility sourcebook, not a room-list adventure. Useful structural ideas:
a formal **Restricted Level 0-3 information/access tier** (higher levels =
harder computer-programming difficulty to access, and cross-reference which
department's data lives at which tier — reusable as a "clearance tier" gating
mechanic for a sealed RimWorld facility). Detention Block section (map is an
uncaptured image, not OCR'd as text — flagged UNREACHED for the room list
itself) is explicitly pitched to the GM as reusable for "rescue or escape
missions, with the added excitement of trying to beat the interrogation
droids to the target" — i.e., the book states its own intended trigger
(time pressure vs. interrogation) as design advice, not just flavor.

### 4. Otherspace (WEG40018) — `sources/sw_d6/otherspace_djvu.txt`
**A genuine derelict-ship dungeon crawl**, and the best trigger-logic example
found. The derelict Rebel transport *Celestial* is explored as 9 numbered
rooms: 1. Upper Airlock (locker cache: 2 vac-suits, 2 medpacs, glow rod,
rations), 2. Rec Room, 3. Galley (Perception roll reveals alien-webbing
evidence of a prior boarding), 4. Engine Room (two-level open shaft,
catwalks/ladders — verticality), [5 missing from my excerpt / cargo hold
elsewhere in doc], "9. Tech Shop" (mislabeled — OCR numbering glitch,
verify against original page scan before use), 6. Medical Bay (bacta tank
stolen, claw-marks), 7. Crew Quarters (Moderate search roll → cache: 2
medpacs, glow rod, syntherope, detonite, blaster pistol), 8. The Bridge
(**trigger: a Moderate security roll plays back the ship's log as a
holographic in-scene flashback** — NPCs' ghost-images physically appear and
act out the final battle in the room the PCs are standing in; this is the
single cleanest "search reveals lore via staged flashback" trigger mechanic
in the whole corpus), 9. Communications Station (Easy computer-programming
roll → comms record). The wider plot: the ship was boarded by an alien
species (the "Charon") who left equipment stripped and webbed shut — dungeon
dressing that *tells* the story of a prior raid without a single line of
dialogue. Reusable directly as a "second scavenger got here first" dungeon
state for RimMaster.

### 5. Goroth: Slave of the Empire (WEG40098) — `sources/sw_d6/goroth_slave_of_the_empire_djvu.txt`
A full planet sourcebook (History / System Overview / Geology / Environment /
native species / Present Situation / Major Settlements / New Technology /
Chapter Nine "Adventures in the Wilderness" / Chapter Ten "Story Starters"),
not a room-list dungeon. Highest-value extract: a **cumulative environmental-
poisoning survival mechanic** — every off-world character who eats native
food loses 1D+2/2D/3D from Strength+Dexterity per meal depending on trophic
level (moss vs. herbivore vs. carnivore), stacking and not clearing for 20
hours after the *last* meal, with a worked numeric example (a named NPC's
stat trail across three meals). This is a clean, portable "the world itself
punishes greed" tedium/challenge mechanic — directly relevant to your METRICS
sibling's tedium-vs-challenge question and to a desert-scavenger survival
dungeon.

### 6. Fan-made "The Scavenger's Handbook" — `sources/sw_d6/FAN_scavengers_handbook_djvu.txt`
**FLAG: NOT an official WEG product.** Its own credits page states it is a
fan work "Inspired by West End Games," built on the free/open "Open D6
System," Creative Commons-licensed. Thematically perfect (salvage life,
scavenging economy) but must not be cited as WEG canon — mark any content
pulled from it as fan-derived if it's used at all.

## Explicit design advice found

- Galaxy Guide 7's "Adventure Ideas" chapter models a two-episode hook
  structure (rumor-gathering → ambush-you-can-see-coming) as the default
  shape for a short adventure — advice-by-example rather than a stated essay.
- Death Star Technical Companion states its own trigger design intent inline
  ("if they aren't trying to break out of a detention block, they are eluding
  security guards set on their trail by a hidden alarm") — confirms alarm-as-
  trigger and time-pressure-vs-NPC-goal as the line's default escalation tool.

## Unreached — named plainly, not fabricated

Full adventure text for: Tatooine Manhunt, Starfall, Otherspace II, Strike
Force Shantipole, Battle for the Golden Sun, Crisis on Cloud City, Graveyard
of Alderaan, Riders of the Maelstrom, Black Ice, Domain of Evil, Scavenger
Hunt, Supernova, Classic Adventures vols 1-5, Instant Adventures, Twin Stars
of Kira, Planets of the Mists, Mission to Lianna, The Abduction, Death in the
Undercity, The Black Sands of Socorro, Secrets of the Sisar Run, No
Disintegrations, Operation Elrood, The Isis Coordinates, The Game Chambers of
Questal, Flashpoint Brak Sector — all confirmed to exist by exact WEG SKU in
the `adventure-journal-2` catalog, all DRM-blocked in that copy. The Star Wars
Adventure Journal (15 issues, each with OCR text sitting in the same
collection) is the fastest path to several of these in reprint form and is
the top recommendation for a follow-up pass. Darkstryder Campaign book 1 was
downloaded (`sources/sw_d6/darkstryder_campaign_book1_djvu.txt`, 758 KB OCR
text, opens with a Timothy Zahn-penned in-fiction cold open) but not yet
read in depth — flagged as the best CONNECTIONS/chained-campaign candidate
for a follow-up read.
