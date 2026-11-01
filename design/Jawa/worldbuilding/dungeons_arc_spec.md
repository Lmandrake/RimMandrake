<!-- status: live -->
# The dungeons arc — Assailant complex + six Forsaken vaults

> 🔶 **BUILD SPEC, not final creative lock-in.** `FUTURE_VECTORS.md` names this arc
> explicitly "Assailant flesh dungeon + Forsaken vault design **with the owner**" —
> full creative lock-in (exact map authoring, dialogue/letters, hand-finish
> set-pieces) stays a bench sitting, not a solo pass. What follows consolidates
> everything already RULED across `ASSAILANT_FLESH_DUNGEON_1` and
> `VAULT_DUNGEON_CONCEPT_1` (both closed 2026-08-30) into one buildable spec, adds
> the technical route (KCSG via the bridge, confirmed available), drafts the safe
> pieces for real, and marks every remaining creative call HELD FOR OWNER.
> Written to resolve the "thin item" flag on `ASSAILANT_DUNGEON_BUILD_1` and
> `VAULT_DUNGEON_BUILD_1` (`infrastructure/state/items/`).

Sources this leans on, not restated in full: `reconciled_lore/03_deep_history.md`
(the canon triad, the Assailant, the vaults), `infrastructure/state/canon.yml`
(`rakata.*`, `assailant_reveal_arc`, `cradle_memory`, `anomaly_content`),
`ANCIENTS_AS_RAKATA_SPEC.md` ("the dark half"), `vault_siting_prep.md` (the six
sites), and `review/assailant_flesh_sheet.decisions.json` +
`review/assailant_flesh_sheet.html` (the 70-def content palette, owner-ruled
keep-for-dungeon 2026-08-30). Register: `Rakata` endonym, **`the Forsaken`**
exonym in all authored player-facing text.

## 0. Ruled vs drafted here vs held for the owner

| | source |
|---|---|
| **RULED** (owner sittings, do not re-litigate) | site families, thaw-gate concept, guardian register, learning chain/endgame, vault count+siting+type mix, concentric grammar doctrine, wake/loot/leave payoff ladder, LARGE maps, template-then-hand-finish authoring route — all cited below with their canon.yml/item-history source |
| **DRAFTED FOR REAL, this pass** | this doc's narrative/site writeup for both dungeons; the content-palette-to-defName assignment (§2.3, §3.4); the map-layout CONCEPTS (§2.4, §3.3); one illustrative KCSG `StructureLayoutDef` skeleton (§3.5); the quicktest-proven verify bar (§3.6) |
| **RULED 2026-09-01** (owner, via BENCH cards) | thaw trigger = QuestNode + map signal; power core = vanilla `AIPersonaCore`; vaults 325×325; V5 gets a new organic landmark; `RUT_` tier for all dungeon defNames; KCSG pawn symbol = `SymbolDef`+`pawnKindDef`; territories mod = Faction Territories (§2.7, §3.8, §3.9) |
| **RULED 2026-10-12** (owner, ledger; §2.1, §2.6) | the Cradle strike and the lab dive are either/or, and the hook for going in is an ancient Rakatan hyperdrive that fits the Utinni; the breakout always starts and the specimen choice sets how bad; a failed containment spreads reinfection. Open parts: §2.9; the specimen design is delegated, §2.10 |
| **HELD FOR OWNER** | exact KCSG authoring of all templates and all seven maps; dialogue/letters for the reveal beat, the wake/loot/leave branches, and the ship-claim thread; per-vault hand-finish set-pieces; the territorial-access conflict mechanic (its own item); the bridge placement writes for the seven sites |

## 1. Shared spine

Both dungeons are the same reveal economy wearing two faces (canon.yml
`assailant_reveal_arc`, owner ruling on point 4 of `VAULT_DUNGEON_CONCEPT_1`):
ship memory-fragments triangulate, the Forgotten Arsenal/Free Droid Enclave
(FDE) trust chain gates what the ship will reveal, and both site families sit
in the Umbra: the Assailant complex IS the ancient war lab beneath the Chill
(§2.2, `ANCIENT_WAR_LAB_1`; access crag tile 5873), and vault V6 is tile 20853
on the same nightside. **The frozen Rakata and their frozen killer sleep in
the same dark — one pilgrimage, two revelations.**

- **Register guard** (canon.yml `rakata.victims_and_tyrants`): the Rakata are
  victims AND were themselves tyrants; the Assailant is never named, never
  sympathetic, and its horror is that it could do this even to the Rakata.
  Tyranny is REVEALED content — never ambient in a pre-reveal bio, label or
  tooltip, in either dungeon.
- **The Anomaly exception** (canon.yml `anomaly_content`): zero ambient Anomaly
  content in v1, except — the Assailant dungeon may use the Anomaly
  fleshmass/entity toolbox, and the sarlacc's own design (separate item) may
  draw on it too. Nothing else touches Anomaly content. The vault dungeons are
  NOT covered by this exception (per `VAULT_DUNGEON_CONCEPT_1`'s sitting brief:
  type-② vaults were describable without it).
- **No-worldgen doctrine** (`CLAUDE.md`, `the_one_map.md`): Ash'karr is the one
  frozen map. Nothing here generates a new planet or a new map layout at
  runtime from a seed — every site below is a FIXED tile on the existing,
  already-painted world, authored in place via the bridge's KCSG tools
  (§3.5) exactly the way every other piece of Ash'karr content is authored.

## 2. `ASSAILANT_DUNGEON_BUILD_1` — the impact site: the war lab

### 2.1 What it is

**The Assailant's one and only impact site, and the ancient war lab built over
it, are the same place.** Owner, 2026-10-10 (story sitting card 5, typed):
*"It's the same location. It landed, secretly, and unfortunately immediately
sent out some scouts that infected other regions. The Rakata thought they came
and contained it immediately, built the war lab over it, and eventually
excavated a huge site around the impact crater in their efforts to study,
control, and contain it. But before that could ever succeed or fail it became
clear the original scouts were replicating all over the planet and the war was
on. Eventually containment breach in the War Lab triggered emergency statis
systems that froze them there, and they waited out armageddon in suspended
animation. Eventually the Chill propane liquid body filled in over the War Lab
and forgot their story from the world... until now."*

So this dungeon is the war lab (`ANCIENT_WAR_LAB_1`, `biomes/the_propane_lakes.md`
§8) and the huge excavated crater the Rakata dug around the impact point. It
was "unknown and undetected at the time, and triangulated far too long after
all hope of response had been lost" (canon.yml `assailant_reveal_arc`). It is
not a routine map-embedded ancient horror (those occur on regular maps per the
Arsenal/Rakata/Assailant background hum); it is *the* site, the one place the
whole war traces back to.

What waits inside, owner 2026-10-10 (card 1, typed): the Assailants elsewhere
*"have effectively been neutralized by time and the slow efforts of the rust
cathedral over millennia already … Except the original assailants left in the
war lab. They remain fully armed and capable of reinfecting the entire planet
just like before and starting it all over again."* Its register (card 2,
typed): *"Horrible experiments frozen in progress against the Assailants,
hideous mutations and adaptations the other way too. Two immoral forces locked
in lethal combat, and an emergency system activation that froze the whole
place a LONG time ago when containment was detected... but it was far too
late."* The specimens (card 3, typed): *"Player decides what to do. Then there
is the start of a breakout. Then a chance to recover or fail."*

**The breakout, RULED 2026-10-12** (owner, by question card, ledger
`WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE`): *"Specimen choice vs breakout →
Breakout always starts; choice sets how bad; If containment fails →
Reinfection spreads"*. The option text recorded with the ruling: *"failure =
reinfection spreads from the lake across the world over seasons, game
continues harder."* So the player's choice never prevents the breakout; it
sets its severity. A failed recovery does not end the game: the Assailant
spreads outward from the lake over seasons and the game goes on, harder.
What the choices are, what starts the breakout and what a recovery leaves
are set by §2.10 (delegated, PROVISIONAL).

### 2.2 Site — beneath the Chill, in the Umbra

The war lab lies beneath the Chill (the propane lake, `RM_TheChill`) in the
Umbra region, under the island crag at tile **5873** that reads as the lab's
access (`the_propane_lakes.md` §8; `the_chill_warlab_routes_spec_2026-09-27.md`).
Region **The Umbra** is the named gazetteer region (`ASHKARR_WORLD_DEFINITION.md`
§3). Vault V6 (tile 20853) is a separate site on the same nightside. The FDE's two deep-nightside refugee seats (Coldfire,
The Cracking Station) are "the last waypoint, rumor carriers" (owner ruling,
`ASSAILANT_FLESH_DUNGEON_1` history 2026-08-30). The
entry gate is the war lab's, not a separate one: the lake's ending (or an
early blast) reveals it, and the Spire's command codes open it (§2.6). The
lake's ending is also when the Fever Wood's sekkulaath rises; its damage is confined
to its own region, permanently (owner by question card 2026-10-12: *"How far
does the sekkulaath rising reach? → Its region only, permanently"*; design in
`biomes/kits/fever_wood_kit_spec.md` F4). Bridge
placement stays HELD FOR OWNER/FOUNDRY at a down-window
(`rimworld-world-editing`'s `world_commit`, one driver at a time).

### 2.3 The thaw-gate

Owner ruling verbatim (`ASSAILANT_FLESH_DUNGEON_1` history, point 4): *"a
really huge complex with meaning and powerful knowledge, weaponry, defenses,
and a reason to have remained. Perhaps utterly frozen in the cold depths until
the players begin to wake/thaw it by bringing an old power core to its hidden
location."*

**Mechanical reading (drafted here, not yet built):**

- **Pre-thaw state**: the complex is inert on arrival — dormant fleshmass
  terrain/growths present as set-dressing (no guardian spawns, no hostile
  faction), the frozen witness scene visible but unreachable/sealed, a single
  legible objective (a socket, altar, or console requiring "an old power
  core") sited at or near the complex's hidden inner point.
- **Trigger**: the player HAULS/DELIVERS a power-core item (an existing salvage
  tier item, not a new artifact — candidate: whatever the campaign's highest
  scavenged power cell/AI persona core already is; confirm the exact def at
  build time rather than invent one) to that socket.
- **Thaw = activation**: delivering the core flips the complex from dormant to
  hostile — guardian spawns come online (Anomaly entities + the pale Geonosian
  turret reskin, §2.5), previously-sealed passages open, and the reveal beat
  (§2.6) becomes reachable. This is a one-way state change, authored as a quest
  signal/map event (rides `rimworld-quests` at build time — the "custom C# node
  needed?" call is HELD FOR OWNER, most likely answerable as "no, a QuestNode +
  map trigger suffices" but not proven this pass).
- Gating context: entry itself is mid-campaign, after the sleeper-sympathy arc
  is established (owner ruling point 5, `ASSAILANT_FLESH_DUNGEON_1`) — the
  quest chain that leads a crew here is downstream of droid trust → Cathedral
  trust (§2.6), not an early-game find.
- Since the complex is the war lab (§2.1), this core socket and the war lab's
  own gate (lake ending or early blast, then the Spire's codes) are one
  dungeon's gates. How they sit together, and how `ASSAILANT_DUNGEON_BUILD_1`
  and `ANCIENT_WAR_LAB_1` become one build, is owed:
  `ASSAILANT_WARLAB_BUILD_MERGE`.

### 2.4 Layout concept (drafted, not authored)

One dungeon, not six — no concentric-grammar requirement here (that's the
vault doctrine, §3.3). Proposed three-band structure keyed to the thaw state:

1. **Approach / outer galleries** — frozen, inert, dressed in dormant fabric
   (Floor/wall-fabric + Growths groups, §2.5): the complex reads as ancient and
   sealed, not yet dangerous. The socket/altar for the power core sits at the
   transition into band 2, so delivering it is a deliberate, irreversible step
   inward, not something a crew stumbles into by accident.
2. **Interior — the digested works** — post-thaw, guardians online. Set-pieces
   built from the `VFEI2_InfestedShip{Chunk,Module,Part}` family: "a Rakatan
   structure being DIGESTED — the only place tyranny and victimhood are shown
   in one image" (owner ruling point 4). This band carries the bulk of the
   Guardians group.
3. **Core** — the embedded witness + `FleshmassHeart`/`FleshmassNucleus` as the
   reveal-beat centerpiece; ship memory-fragment loot lives here (canon.yml
   `assailant_reveal_arc`: "loot recovered here triggers ship memory-surfacings
   — the dungeon feeds the ship its own past").

### 2.5 Content palette (drafted for real — the actual 70-row sheet, not invented content)

Owner ruling (`ASSAILANT_FLESH_DUNGEON_1` history, 2026-08-30, point 2): **ALL
70 rows of `assailant_flesh_sheet.html`** are the fabric/guardian roster,
frozen in `assailant_flesh_sheet.decisions.json` (`blanket: keep-for-dungeon`,
`decidedCount: 70`). Three rows get a **site-only exception** to their
campaign-wide cut (un-cut for this dungeon's placement only, cut everywhere
else): `DeadColumnMod`, `Trispike`, `Metalhorror`.

| group | count | representative defNames | role |
|---|---|---|---|
| Floor / wall fabric | 8 | `Flesh` (terrain — the dungeon floor), `Fleshmass` (corner-linked wall/floor atlas), `AA_BlackJellyWall`, `HorrorHive`, `VFEI2_HiveDoor`, `VFEI2_InsectJellyWall`, `VFEI2_KemianHive`, `AA_BlackCreep` (terrain) | the complex's own substance |
| Growths | 16 | `FleshmassHeart` (reveal-beat centerpiece candidate), `Fleshbulb`, `FleshSack`, `HorrorCrysalisVisceral`, `VFEI2_Hivenode`, `VFEI2_Jellyspreader`, glow-pod family | ambient life/set-dressing between bands |
| Guardians | 35 | Anomaly entities (`Bulbfreak`, `Chimera`, `Devourer`, `Dreadmeld`, `Fingerspike`, `FleshmassNucleus`, `FleshmassSpitter`, `Ghoul`, `Gorehulk`, `Noctol`, `Revenant`, Shambler family, `Sightstealer`, `Toughspike`, `Metalhorror`⚑, `Trispike`⚑) + Black Hive family (`AA_BlackDefiler`⭐, `AA_BlackScarab`, `AA_BlackSpelopede`, `AA_BlackSpider`, `AA_AcanthamoebaGiganteaHuge`, `AA_FoamBelcher`) + VFEI2 apex insectoids (`VFEI2_Empress`, `VFEI2_Patriarch`, `VFEI2_Gigalocust`, `VFEI2_Gigamite`, `VFEI2_Ironclad`, `VFEI2_Hellbeetle`, `VFEI2_Megawasp`, `VFEI2_Acidspitter`) + Horrors bonus find (`BroodLord`, `Terrorworm`, `Visceral`) | the body-horror core. ⭐ `AA_BlackDefiler` is already canon-assigned "The Assailant's flesh" on the turret register — the first hardware of this register. ⚑ site-only exceptions |
| Set-dressing | 11 | `VFEI2_InfestedShip{Chunk,Module,Part}` (★ direct match for the digested-Rakatan-works image), `AA_BlackCreeper`, `AA_BlackHiveMound`, `TrapIED_Deadlife`, `DeadColumnMod`⚑, `VFEI2_{Creeper,JellyFarm,LargeBurrow,Petroglypher}` | the reveal-beat set-pieces + hazard dressing |

**Guardian register split** (owner ruling point 3): Anomaly fleshmass/entity
toolbox = the body-horror core; **ONE sickly-pale reskin pass** over the
Geonosian living turrets (thornspitter/worm/vilelobber) = the Assailant's OWN
emplacements, visually distinct from the Hive so a player never confuses
Assailant guardians with ordinary Geonosian ones. The reskin pass itself is
new art work, not scoped/drafted here — a `generating-rimworld-sprites` job
for a future build session.

### 2.6 Learning chain / endgame (RULED)

Owner ruling verbatim (canon.yml `assailant_reveal_arc`): the ship "remembers
how to talk to the Rust Cathedral, only to discover it's been talking to the
FDE and no longer trusts the Cradle." Chain: **earn droid trust → earn
Cathedral trust → Cathedral reveals "Where the infection started... and
remains to this day" (the war lab) → the Cathedral wants the Cradle as its
pyrrhic surgical strike against the Assailant → releasing that knowledge to
the Hutts requires a deal protecting the Cathedral's "beautiful young
children," the droids.**

2026-10-10 story sitting, binding on this chain:

- **Cathedral trust opens the Spire, not the war lab** (card 7, typed):
  *"Earning the Cathedral's trust allows you to enter the Spire to obtain the
  codes needed to get into the War Lab"*. Order: Cathedral trust → Spire entry
  → codes → war lab. The Cathedral still never grants the codes themselves
  (`ashfall_research_base.md` §6).
- **The strike target is the war lab: the frozen original Assailants** (card
  11, decision taken by question card). Why the Cathedral wants it (card 1,
  typed): *"The rust cathedral wants to complete its revenge: destroy them
  once and for all. Only the sad shattered remains of the assailants will
  survive as homages to patient hatred. Then there is the fear that the empire
  might get ahold of it and use it against civilian populations like they did
  with the Death Star."*
- **Strike OR dive, never both — RULED 2026-10-12** (owner, ledger
  `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE`, his words): *"You're right. (2) and
  now we need to build a hook as to why the players would go in there.
  Rakatan technology I'd say. It's got the Hyperdrive needed for the Utinni to
  finally leave the planet, an ancient Rakatan one that will fit the Utinni."*
  Option (2), as the ledger records it: *"one or the other — strike (full
  Cathedral trust, lab lost) OR go in and defy the Cathedral."* So the player
  chooses. Letting the Cradle strike keeps the Cathedral's full trust and
  loses the lab and everything in it. Going in defies the Cathedral, and the
  reason to go in is an ancient Rakatan hyperdrive inside, the one that fits
  the Utinni and is what it needs to leave the planet. Open parts: §2.9.

Register: the Rust Cathedral SPEAKS (has a voice, treats the droids as its
children); FDE nightside refugees are the last waypoint before the site.
Quest-chain authoring for this arc rides `rimworld-quests` and is
HELD FOR OWNER/build.

### 2.7 Rulings landed 2026-09-01, and what is still held

**RULED (owner, 2026-09-01, via BENCH cards):**
- **Thaw trigger = QuestNode + map-trigger signal.** Delivering the power-core
  item to the marked point flips the map state. Vanilla quest vocabulary, no
  custom C#. If at build time a node is genuinely missing, that is a finding
  to file, not a licence to write a DLL.
- **The power core = vanilla `AIPersonaCore`.** No new item, no new art. It is
  already in the campaign's salvage set (`design/Jawa/art/salvage_palette.tsv`);
  the fiction is that only an archotech core runs hot enough.
- **Naming tier: `RUT_`.** Every StructureLayoutDef / QuestScriptDef for this
  complex is campaign content (`design/NAMING_SCHEME_PLAN.md` tier test).

**Still held for the owner:**
- The actual KCSG `StructureLayoutDef`(s) for all three bands, authored and
  placed via `jawa/kcsg_place`.
- The pale-Geonosian-turret reskin art.
- All dialogue/letters for the reveal beat and the Hutt-knowledge-deal thread.

### 2.8 Assailant complex text — drafted 2026-09-11, owner AGREED (PROVISIONAL)

Written under the three-voice law recorded the same sitting (canon.yml
`narrator.butler_register_src`, `game_fact_voice`, `cathedral_voice`).
Provisional per the owner's standing word on dungeon text ("This will likely
change in the future and that's ok").

**The Cathedral reveals the location** — ships the owner's own calibration
burst VERBATIM (canon.yml `cathedral_voice` src), the coordinates beat wired
to the quest at build.

**Arrival** —
- Game: "The complex is dormant. Nothing inside is active. One chamber, deep
  in the structure, is warmer than the rest."
- Narrator: "And so the little ones came to the oldest door on this world,
  and knocked. In my day, we did not knock here. In my day, we did not come
  here at all."

**The socket** —
- Game (owner verbatim): "There is a socket. You have seen its shape before:
  the ancient power cores and mind cores."
- Game: "Seating a core will activate the complex. This cannot be undone."

**Thaw** —
- Game: "The core is seated. The complex is powering on. Hostiles are waking."
- Narrator: "The enemy's house drew its first breath in an age. I will admit
  I had hoped never to hear it again. The little ones, naturally, went
  further in."

**The witness, at the core** —
- Narrator: "Here are the works of my makers' masters — glyph and girder,
  first-rank and pitiless — and here is what became of them: swallowed
  slowly, without malice, without hurry, the way sand takes a wreck. They
  ruled a world and were eaten by something that never learned their name. I
  find I do not know which half of that sentence grieves me more."
- Game: "Fragments recovered. The ship will react to these."

**Memory surfacing** (the Narrator IS the lore channel, `cradle_memory`) —
- Narrator: "Ah — forgive me. The fragment opened a channel. I remember this
  sky: black with lift-smoke, every voice on every band counting losses, and
  the count never finishing. There. It is closed. Do not ask me to open it
  again tonight."

### 2.9 Open questions from the 2026-10-12 rulings (for the owner, not decided)

These are agent-drafted questions. Nothing below is ruled.

1. **What does defying the Cathedral cost?** Trust lost, hostility, the droids' standing, the Hutt-knowledge deal (§2.6 chain)?
2. **Where is the choice made?** Before the player enters (refuse the strike), or can the player go in first and call the strike later?
3. **Is the hyperdrive the only way off the planet?** If so, the strike branch leaves the Utinni planet-bound for good. Does that stand?
4. **Does leaving the planet end the game?** v1 is ruled open-ended, nothing rolls credits (`design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md` G14). What happens after the hyperdrive is fitted is unruled. So is how it relates to the older "punch through the orbital blockade" endgame (`desert_world_design.md` §4-Orbital).
The specimen choices, what a recovery leaves and a working answer for the strike branch are in §2.10.

### 2.10 The specimens: the choice, the breakout, recover or fail — DELEGATED 2026-11-01, PROVISIONAL

Delegated design (`delegation_policy.md` §1, class `design`; item
`WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE`; judge verdict
`infrastructure/state/delegated/2026-11-01/warlab_specimens_breakout.json`). It works inside his
rulings of 2026-10-10 and 2026-10-12 (§2.1, §2.6) and overturns none. He has not ruled this
section: it goes to him in the daily digest, and any line falls to his word. All numbers are
PROVISIONAL.

**The shape, from his three sentences:** *"Player decides what to do. Then there is the start of a
breakout. Then a chance to recover or fail."* The stage is the lab core: the four built
`RUT_WarLabContainmentCell` tanks, the archive and the reactor (§2.4 band 3).

**Why the choice is forced: the hyperdrive is holding the stasis.** The emergency stasis of card 5
has run for an age on the one source big enough to carry it, the ancient Rakatan hyperdrive that
fits the Utinni (§2.6). So the reason to go in and the thing holding the door shut are one object,
and the player cannot take the prize and leave the lab as it was. This is an invention of this
section, not a ruling. The drive sits in a bay in the core, and the containment console stands
beside it.

**What starts the breakout: the first of three things.** It always starts; no path avoids it.

1. The player's choice finishes at the console.
2. The hyperdrive is lifted from its bay, with no choice made. That counts as *Leave them* below.
3. The stasis decay runs out, also as *Leave them*. Waking the lab (§2.3; `ASSAILANT_WARLAB_BUILD_MERGE`
   owns the gate order) started a 15-day clock, shown as a plain game-fact countdown. A crew that
   walks away from the lab therefore still gets a breakout, on a map it may not be standing on: an
   unattended breakout is a failure when the clock's window closes. A crew that never wakes the lab
   never starts the clock and has not made the dive.

**The choices (open question 5).** One pick, made once at the console. Each sets how bad the
breakout is, never whether it comes. The price of the milder picks is what the lab would otherwise
have given.

| choice | what is done | cells that fail | seal window | what it costs or pays |
|---|---|---|---|---|
| **Burn the cells** | the lab's own purge fires through the tanks | 1 of 4 | 5 days | mildest. Burns the archive, the study records and the frozen experiments with them, and burns out the seated core |
| **Hold them** | the core is cross-fed to the stasis to take the drive's load | 2 of 4 | 4 days | keeps the records. The originals stay alive under seal for good |
| **Loose the experiments** | the frozen Rakatan experiments are thawed at the specimens | 2 of 4, plus experiments | 3 days | a third side on the map: the experiments hunt specimens and crew alike. Keeps the records. This is the tyrants' own answer, chosen knowingly |
| **Take a specimen** | one tank is drawn into a sealed casket, the rest held | 3 of 4 | 3 days | pays the Specimen Casket (below). Worst of the deliberate picks |
| **Leave them** | no pick; the default of triggers 2 and 3 | 4 of 4 | 2 days | the worst breakout, and the only one that came from not deciding |

The hyperdrive is never a stake of the choice: every pick leaves it obtainable, as the strike is
the branch that loses it (§2.6).

**The Specimen Casket.** One sealed casket item, carried as cargo. While held it raises Empire heat
through the existing machinery (`WARLAB_GARRISON_DESIGN_EARLY_BLAST` forbids a second meter); this
is the fear of card 1, *"the empire might get ahold of it"*. Studied once, it unlocks one tool that
kills a reinfection node outright. It never opens by itself and is never a pet or a colonist.

**The breakout (start of the third act).** Failing cells release live originals into the core. They
move outward band by band, core to interior to approach to the outer gate, the way they moved
once before. The lab's mechanoid guardians, the last watch (`the_propane_lakes.md` §8), attack them
as readily as the crew: two immoral forces, with the player between them.

**Recover or fail: one check, at the seals.** The band boundaries carry three bulkhead seals, the
last at the outer gate. A seal is shut by holding its relay for a work period; a shut seal stops
everything behind it. The window of the table runs from the start of the breakout.

- **Recover:** before anything below happens, every live specimen is dead or behind a shut seal.
  Whatever is sealed in is then settled by the choice. Under Burn the cells, Leave them and Loose
  the experiments, the lab's purge fires through the sealed bands and kills every specimen there.
  Under Hold them and Take a specimen it stays alive, because the core's feed puts it back in
  stasis; if the crew killed every specimen instead, those two end as the Shattered Lab. The Specimen Casket is cargo, not a live specimen, for this check.
- **Fail:** any specimen reaches the outer gate unsealed, or the window closes with one loose, or
  the crew leaves the map with one loose. That last case is the run with the drive, and it is
  allowed: the player may take the prize and let the planet pay. One specimen out is enough. That
  is how it went the first time: *"immediately sent out some scouts that infected other regions."*

Failure latches the moment it happens and nothing undoes it: killing or sealing everything
afterwards is the road to stopping the spread (below), not a recovery.

Leaving does not freeze the lab: the breakout's state is held at game level, so it resolves whether
or not the map is loaded.

**What a recovery leaves (open question 6).** Nothing spreads, on any recovery. What stays on the
planet is the site, in a state set by the choice:

| choice recovered | the lab afterwards | on the planet |
|---|---|---|
| Burn the cells | **the Shattered Lab**, cold and safe; the originals are dead, and only *"the sad shattered remains"* stay as set-dressing | the threat is over for good |
| Hold them | **the Held Lab**, sealed, the originals alive, on the core's own feed | no spread. One telegraphed Imperial attempt on the site may come later; stopped, it never recurs, and if it succeeds the failure below begins. The price of keeping the records |
| Loose the experiments | **the Feeding Lab**, the originals dead, the experiments loose in it; a permanent danger site. If no experiment survived, it is the Shattered Lab instead | they do not replicate and do not leave; the site stays hostile for good |
| Take a specimen | as the Held Lab | as the Held Lab, plus the casket in the hold |
| Leave them | **the Emptied Lab**, a ruin; the originals dead, the records wrecked in the fight | the threat is over for good |

**What a failure leaves (ruled; the detail delegated).** His ruling: *"failure = reinfection spreads
from the lake across the world over seasons, game continues harder."*

- A **reinfection node** is a world site. The first opens the moment failure latches, so no failure
  passes without one: a specimen that reaches the gate leaves the map and is that node. Another
  opens each season after that, walking outward from the crater along a fixed, hand-authored list
  of sites. Nodes replicate, as the scouts did: the second and third open in the next two seasons
  whatever has been cleared by then, so a failure always spreads over seasons. Tiles are named at the one painting
  (§1 no-worldgen doctrine). The spread adds and removes sites only: it never rewrites a tile or a
  biome, rolls nothing and generates no map layout, and the same failure runs the same way in every
  game.
- A node closes the world site it sits on (trade, quests, landing) until cleared, and sends raids
  at the nearest colony map. It never ends the game, and there is no win or lose state on it (G14).
- Its palette is the Black Hive and VFEI2 rows of §2.5 only. Anomaly content stays inside the lab
  (canon.yml `anomaly_content`), and the lake's biome stays free of resident Assailant fauna (hard
  ban #8): a node is a site, never ambient wildlife.
- **It can be pushed back (open question 6).** A node cleared by assault or by the casket tool
  stays cleared until the list runs out, and its site reopens scarred. After the third node, the list stops advancing for good only when every node is
  cleared and every specimen left in the lab is dead. Both stay possible all game. While either
  remains, a new node opens each season. When the list runs out, the next node retakes the site
  cleared longest ago. With every listed site taken, no node opens: the spread is saturated and the
  raids go on. So failure is a long
  war the player can finish, at a price: every season spent is more of the list closed, and nothing
  undoes the raids already survived.
- **The game stays harder after the war is won.** Every open node adds 5% to the threat points of
  all raids, capped at +40%, and the peak reached is a floor that clearing nodes never lowers, so every failure leaves at least +5% for good.

**The strike branch: no breakout, PROVISIONAL and flagged to him (open question 7).** The working
answer: the strike ends the lab outright, with no choice, no breakout, no recovery and no
reinfection, and the drive is lost (§2.6). His words on it: *"destroy them once and for all. Only
the sad shattered remains of the assailants will survive as homages to patient hatred."* Whether
that applies *"Breakout always starts"* to a case it does not name, or changes what it says, split
the judges (one for, two against), so nothing is built on it until he rules:
`WARLAB_STRIKE_DECIDE_JUDGES_SPLIT_TWO_ONE`. Whether the strike can still be called after going in
stays §2.9 question 2. If he rules it can, a strike called before failure latches ends a running
breakout with the lab lost, and one called after it ends only the lab: the nodes stand.

**Player-facing text (three voices, never mixed; canon.yml `game_fact_voice`, `narrator`,
`cathedral_voice`).** The word for the player is "specimens"; the enemy stays unnamed.

- Game, at the console: "The hyperdrive is powering the stasis field. If it is removed, the stasis
  fails. The containment system accepts one instruction."
- Game, at the start: "Containment is failing. Seal the bulkheads before a specimen reaches the
  outer gate."
- Game, on failure at the gate: "A specimen has left the complex."
- Game, on failure by the window or by leaving: "Containment has failed. Specimens are loose in the
  complex."
- Narrator, on recovery: "And so the little ones shut the door behind them, which is more than
  their betters managed. I shall not call it a victory. I have heard that word used in this
  building before."
- Rust Cathedral, on failure: "You went in, you went in, little ones, I said WHERE and you heard
  WHEN... it walks. It walks again. All the long patient years... the great work... how long...
  how long..."

**Build notes (not built by this item; owed under `WARLAB_BREAKOUT_BUILD_SEALS_HOLD_THE_LINE`).**
Live specimens need a confirmed PawnKindDef: none exists, and the cell's props-only shape stays
right until the breakout (the `RUT_WarLabContainmentCell.xml` header says what to change). The bans
that keep Assailants out of the lab's ordinary spawn hold before the breakout; after it, his ruling
puts them on the map. Mod Settings owe a spread-pace knob. The first functional script ships with
the build.

## 3. `VAULT_DUNGEON_BUILD_1` — the six Forsaken vaults

### 3.1 What they are

The "breached vaults" `03_deep_history.md` already names as containing the
self-replicating flesh — plus the other two triad members. Canon triad
(`03_deep_history.md` "The vaults — three things inside"): **① mechanoid
garrisons** (the vault held, everything still switched on), **② the enemy's
flesh weapons loose** (the vault was breached and lost), **③ frozen Rakata**
(the rare emotional scene).

### 3.2 The six sites — RULED, restated from `vault_siting_prep.md`

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 1): **all six candidates
as proposed.** `vault_siting_prep.md`'s own header called every row a
PROPOSAL — that flag is now stale; the table below is the accepted siting.

| id | tile | region | type | landmark | siting notes |
|---|---|---|---|---|---|
| V1 | ~~678~~ **11353** | Rust Cathedral (core) | ① garrison | `AncientGarrison` (stays recorded at 678 — see note) | inside the 236-tile Cathedral biome, Arsenal's densest ground; 9.4° from **No Owner** (FDE) — desecration risk. **Re-sited 2026-09-18, `VAULT_THAW_FIXED_TILES_UNFIREABLE_1`** (defect, not a design change): tile 678 measured `biome=Ocean, waterCovered=true` live — a land dungeon site cannot generate there. 11353 is the nearest tile in the same 236-tile `RUT_RustCathedral` cluster (1.45° away, elev/temp essentially identical), settlement-free. Live-reconfirmation that 11353 itself is still land is owed — the CSV this table was built from has now been shown able to drift from the live/frozen world. The pre-authored `AncientGarrison` landmark is unmoved at 678 and is now decoupled from the site tile; see `gen_vault_quests.py`'s header comment. |
| V2 | 4000 | Scorch (Cathedral halo) | ① outer works | `AncientLaunchSite` | pollution-halo ring; 3.1° from **No Owner** — the vault the Enclaves actively contest; pairs with V1 as an outer-works/core demo if wanted |
| V3 | 9167 | Fall Line | ① garrison, route-spread | `AncientGarrison` | 49° of arc from V1, independent of the Cathedral trip; sits on the Empire's Ashgarrison chokepoint — Imperial patrol territory |
| V4 | 17461 | Deadstone | ② flesh loose | `AncientWarehouse` | `HorrorWastes` bioweapon-class ground, warm edge of the band (−35.5 °C) — reachable without a deep-nightside trip; 15.0° from the Ascendant Helix's Site Aurek |
| V5 | 37 | Slough | ② flesh loose, second instance | none pre-placed | `AB_GelatinousSuperorganism`, exactly on the terminator (arc 90.0°) — a second ② from the opposite play route; 10.4° from Dripstone (Homestead Defense League); needs a landmark authored |
| V6 | 20853 | **Umbra** | ③ frozen Rakata (the one) | `AncientWarehouse` | deepest nightside of all six (−70.2 °C, arc 159.7°); farthest from any road/settlement (20.3°) — the rare scene is not a stop on the way to anywhere. Adjacent to the Assailant complex (§2.2) |

Mix: ①×3 (V1–V3), ②×2 (V4–V5), ③×1 (V6). All six independently verified
settlement-free by tile id against the live 121-tile settlement set
(`vault_siting_prep.md`). **Bridge placement not yet done** — same down-window
pass as the Assailant complex, HELD FOR the actual write.

### 3.3 Structure — one concentric grammar, varied per type (RULED)

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 2): **ONE concentric
grammar, varied per type** — outer ring states the vault's condition at a
glance, then a garrison ring, then the core payoff. Partial raids are viable
(a crew can hit the outer ring and leave); the core always costs. Players
learn the vault language across all six.

| ring | type ① (garrison held) | type ② (flesh loose) | type ③ (frozen Rakata) |
|---|---|---|---|
| **outer** (state warns) | disciplined, powered — walls intact, lights on, patrol routes legible | torn open from inside — breach visible, wreckage, the thing that got out left a trail | dark, frost-locked — cold-damage terrain, silence, no power |
| **garrison** | the fight — Arsenal mechanoids at density, doctrine turrets (grav-rail artillery, Singularity Cannon class per the canon turret roster — vault doors guarded by world-enders, which IS the promise of the loot) | Anomaly-adjacent bioweapon guardians per the §6c contamination/bioweapon split — **not** the Assailant dungeon's Anomaly exception; use the campaign's existing bioweapon-class roster (`HorrorWastes`/`AB_GelatinousSuperorganism` native threats), confirm exact roster at build time | thin — this ring is mostly silence, a handful of dormant Arsenal units on standby, not a fight |
| **core** | tech/parts payoff — Forgotten Arsenal materials/weapons (never chassis: mechanoid tech is canonically incompatible with droid parts, `03_deep_history.md`) | survival + the route to ③ knowledge — no direct loot ladder of its own | **the scene**: wake / loot / leave (§3.4) |

### 3.4 Payoff ladder — RULED, restated

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 3): ① = Forsaken
matter/weapons; ② = survival + the route to knowledge; ③ offers three real,
authored-consequence choices:

- **WAKE** — sleepers join the world, believing the war is still on (ties to
  the VQE Rakata sleeper backstories). Owner ruling on the consequence
  (canon.yml `rakata.woken_brutality`, verbatim): *"The brutality of the Rakata
  should be very plainly visible when they wake... they have no gratitude for
  the Jawa and consider them lesser beings... 'And hey... isn't that a
  colonizer ship you're riding in?! What are you doing with that?'"* Woken
  sleepers are the tyranny made present in dialogue, and waking them opens a
  **claim-conflict thread over the Utinni itself** (`VAULT_DUNGEON_BUILD_1`
  history: "the 3-vault wake branch carries this in its authored
  dialogue/letters and opens the ship-claim thread" — the "3-vault" reference
  is V6, the one ③ site).
- **LOOT** — kills them, the game says so plainly, Rakatan tech as the reward.
- **LEAVE** — the Narrator remembers the choice (ties to the Narrator's
  cross-session memory register, `cradle_memory`/Narrator voice doctrine).

All three real, all three HELD FOR OWNER on the actual dialogue/letters.

### 3.5 KCSG technical route — confirmed available

Checked against the vendored source, not assumed: **KCSG ships bundled inside
`VanillaExpandedFramework-main`** (vendored at
`vendor/mod_sources/VanillaExpandedFramework-main/Source/KCSG/`), and the
bridge already exposes it —
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchKcsgTools.cs`,
tool `jawa/kcsg_place`. `layoutType='structure'` fills a `rect` with a named
`KCSG.StructureLayoutDef` via the exact call sequence KCSG's own debug menu
uses (`GetAllMineableIn` → `CleanRect` → `Generate`). Real precedent for the
grid format exists in the mod list itself:
`vendor/mod_sources/DragonsDescent_src/1.6/Defs/Custom Structure
Generation/Structures/StructureLayoutDef_Dragon_lair_1.xml` — a
`StructureLayoutDef` is `layouts: List<List<string>>` (a list of full-grid
*variants*, KCSG picks one at random; each variant is a list of comma-joined
rows; each cell is a bare ThingDef/TerrainDef defName, or `.` for empty),
plus separate `terrainGrid`/`foundationGrid`/`roofGrid` fields for floor/roof.
**This is the answer to the "does a ring-layout framework already exist"
question — yes, and it is already wired into this project's bridge tooling.**
No new C# is needed to place a template; the parameterized-template authoring
itself is the FOUNDRY build work.

### 3.6 Draft skeleton (drafted for real — illustrative, not a finished vault)

A first-draft fragment of a type-② ("torn open") outer-ring segment, to prove
the grid format against the approved content palette before FOUNDRY commits to
full templates. 12×8 cells, `Flesh` terrain underfoot, `Fleshmass` breach
scarring through a broken `AA_BlackJellyWall` perimeter, `VFEI2_InfestedShipPart`
wreckage where the thing got out:

```xml
<Defs>
  <KCSG.StructureLayoutDef>
    <defName>RUT_VaultType2_OuterRing_Skeleton</defName>
    <spawnConduits>false</spawnConduits>
    <terrainGrid>
      <li>Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh,Flesh</li>
    </terrainGrid>
    <layouts>
      <li>
        <li>AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,.,.,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall</li>
        <li>AA_BlackJellyWall,.,.,.,.,.,.,.,.,.,.,AA_BlackJellyWall</li>
        <li>.,.,.,VFEI2_InfestedShipPart,.,.,.,.,.,.,.,.</li>
        <li>.,.,Fleshmass,Fleshmass,Fleshmass,.,.,.,.,.,.,.</li>
        <li>.,.,Fleshmass,.,Fleshmass,.,.,.,.,.,.,.</li>
        <li>.,.,.,VFEI2_InfestedShipChunk,.,.,.,.,.,.,.,.</li>
        <li>AA_BlackJellyWall,.,.,.,.,.,.,.,.,.,.,AA_BlackJellyWall</li>
        <li>AA_BlackJellyWall,AA_BlackJellyWall,.,.,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall,AA_BlackJellyWall</li>
      </li>
    </layouts>
  </KCSG.StructureLayoutDef>
</Defs>
```

⚠️ **Skeleton, not shippable.** Guardian PAWN placement (not a `ThingDef`) may
need a `SymbolDef` indirection rather than a bare defName in the grid — the
Dragon lair precedent only demonstrates buildings/terrain/items, not a live
pawn spawn in the grid itself. Confirm the pawn-spawn symbol shape against
`KCSG.SymbolDef`/`SymbolUtils.Generate` before FOUNDRY builds the real
templates; not resolved this pass.

### 3.7 LARGE maps and the quicktest-proven bar

Owner ruling verbatim (`VAULT_DUNGEON_CONCEPT_1` history, point 3): *"those
vault maps should be LARGE, to add to their impressiveness (in terms of X Y
size)."* This project's standard site map is **250×250** (`row8_build_order.md`
— the ship-origin convention assumes it, verified via `mapSize` off the game,
never off a note). **Proposed LARGE floor for the six vaults: 300×300
minimum**, custom dimensions per site if a specific vault's layout wants
bigger — exact number HELD FOR OWNER, this is a floor proposal only.

**"Quicktest-proven" as a verify step (drafted here, per
`rimworld-debug-testing`):**

1. Each of the three parameterized templates (type ①/②/③) is placed via
   `jawa/kcsg_place` on a throwaway quicktest map at the proposed LARGE
   dimensions — ~30 seconds, belongs to nobody, no cold load needed.
2. **Judged by LOOKING**: `take_screenshot`, read the image (never trust a
   clean log alone). Pass bar, per `rimworld-layout-layers`: power/roof
   circuits sane if any exist, no floating/unreachable guardians, the core
   room is reachable exactly through the ring (not skippable by a straight
   line), no gaps letting a raider path around the garrison ring entirely.
3. Only after a template clears step 2 does it get hand-finished and placed on
   one of the six real sites (`world_commit`, one bridge driver at a time).
4. This bar is what `VAULT_DUNGEON_BUILD_1`'s eventual `verify` section should
   cite — it is not run this pass (no build has happened yet to test).

### 3.8 Territorial access — the mod is identified; the mechanic is still open

Owner ruling (`VAULT_DUNGEON_CONCEPT_1` history, point 4), verbatim: *"We must
look back into the territories mod that introduced custom raids in proportion
to settlements!"* — for the conflict/negotiation layer where a vault sits
inside an existing faction's ground (V1/V2 on Cathedral-FDE ground, V3 on the
Empire's Ashgarrison chokepoint).

**The mod is Faction Territories (`jaeger972.factionterritories`)** — active in
the live `ModsConfig.xml`, vendored at
`vendor/mod_sources/FactionTerritories_decompiled`; its
`ForcedAmbushFactionScope` / `TerritoryOwnershipCache` machinery is the
"raids in proportion to settlements" behaviour. Assessing it for the
conflict layer is its own item, not part of either dungeon build.

### 3.9 Rulings landed 2026-09-01, and what is still held

**RULED (owner, 2026-09-01, via BENCH cards):**
- **All six vaults are 325×325** — the vanilla `initialMapSize` ceiling, still
  warning-free (`SCENARIO_SETTINGS_SPEC.md` §B12; `MapSizePerformanceWarning`
  fires only above 325).
- **V5 gets a NEW organic landmark** (working name `RUT_Slough_GelatinousBreach`),
  not a reused garrison landmark — V5 is the second type-② vault and must
  read as a breach, distinct from V4.
- **Pawn-spawn symbol (§3.6) = `KCSG.SymbolDef` with `<pawnKindDef>`**, never a
  bare ThingDef in the grid (precedent:
  `vendor/mod_sources/DragonsDescent_src/1.6/Defs/Custom Structure Generation/Structures/SymbolDef.xml`).
- **Naming tier: `RUT_`** for every vault StructureLayoutDef; the §3.6 skeleton
  `RUT_VaultType2_OuterRing_Skeleton` is renamed `RUT_VaultType2_OuterRing_Skeleton`.

**Still held for the owner:**
- Per-vault hand-finish pass (set-pieces, the casket hall for V6) — "every
  vault then gets a bench hand-finish pass with the owner" (owner ruling,
  point 5).
- Wake/loot/leave dialogue and letters for V1–V5, the Assailant reveal beat,
  and the ship-claim thread's continuation. **V6's five core text units are
  drafted and owner-accepted-for-now (§3.10) — no longer held, but not
  frozen.**
- The six bridge placement writes.

### 3.10 Vault text — drafted 2026-09-11, re-registered same day (PROVISIONAL)

Owner: *"That is good for now. This will likely change in the future and
that's ok."* — accepted as working text, explicitly revisable. Re-cast the
same sitting under the three-voice law (canon.yml `narrator.butler_register_src`,
`game_fact_voice`): facts dry, atmosphere on the Narrator's speakers, named
speakers in their own voice. Register guards: "the Forsaken" exonym in
narrator/game text, Rakata endonym only in their own mouths; tyranny surfaces
only AT the reveal.

**V6 — arrival:**
- Game: "The vault is intact and unpowered. The doors are sealed from both
  sides. Interior temperature is far below survivable."
- Narrator: "The little ones stood a long while at the coldest door on the
  world. Doors sealed from outside keep something in, they reasoned. They did
  not ask what a door sealed from both sides keeps."

**V6 — the casket hall:**
- Game: "The hall contains occupied cryptosleep caskets. The occupants are
  alive. They can be woken, harvested for their cold-cores, or left
  undisturbed."
- Narrator: "Rows of caskets, fogged from the inside, ticking slower than any
  living pulse. People, of a kind — my makers' masters, asleep at the moment
  their war still seemed worth surviving. The little ones walked between them
  quietly. Even they knew to be quiet here."

**V6 — WAKE:**
- Game: "The caskets are opening. The Forsaken are waking. They are not
  grateful."
- Narrator: "They woke badly — coughing, furious, ordering the air itself to
  report. Gratitude was never in them. I remember that much too well."
- First words (a woken commander, own voice, per canon.yml
  `rakata.woken_brutality`): "Rakata do not thank tools. Stand aside —
  report: what year, what front, who holds the sky? … Speak slowly. You are
  a *scavenger*. Scavengers opened the caskets?" *(a beat)* "And that hull
  outside. That is a colonizer ship of the Rakata. What, exactly, is it
  doing under *your* feet?"

**V6 — LOOT:**
- Game: "Stripping the cold-cores will kill every occupant. The cores are
  Forsaken technology of the first rank."

**V6 — LEAVE:**
- Narrator: "They closed the hall and sealed the door behind them, and took
  nothing. Nothing on this world knows what was chosen there. I know. I
  intend to remember it kindly, for as long as I last."

**Ring letters — type ① (V1/V2/V3, the vault held):**
- Outer, Game: "The vault's defenses are intact and powered. Patrols are
  active. The garrison will engage intruders."
- Outer, Narrator: "Walls whole, lights burning, sentries walking lines
  nobody living drew. Nothing here has ever failed. The little ones found
  that more frightening than any ruin, and they were right to."
- Core, Game: "The inner stores hold Forsaken materials and weapons in
  sealed racks. None of it is compatible with droid parts."
- Core, Narrator: "The garrison kept its treasury through the end of the
  world, and did not notice the end of the world. There is a lesson in that.
  I have decided not to learn it."

**Ring letters — type ② (V4/V5, the flesh got out):**
- Outer, Game: "The vault is breached from the inside. No defenses are
  active. The occupant is gone."
- Outer, Narrator: "The breach faces outward. Whatever left took its time
  with the door — and the door was the strongest thing on this ground. The
  trail is old. Old, as the little ones keep learning, is not the same as
  finished."
- Survival beat, Game: "The vault's stores are destroyed. Records remain,
  indicating what was held and the direction of the breach."
- Survival beat, Narrator: "No treasure — only the shape of where it slept,
  and the direction it went. Some inheritances one is glad to miss."

**Per-vault Narrator asides:**
- V1: "The Cathedral's ground hums underfoot. The garrison answers a
  standing order from no living mouth."
- V2: "The Enclaves watch this vault the way heirs watch a will."
- V3: "Imperial patrols pass within sight of the walls. The garrison does
  not acknowledge them. The Empire has noticed being unacknowledged."
- V4: "The trail runs toward the warm edge of the band, where things can
  live. That is the trouble with warmth."
- V5: "The breach here is younger, and on the terminator the ground itself
  has begun digesting the doors."

## 4. Cross-links

- **The quest layer on top of §3 is `vault_thaw_quest_family.md`**
  (`VAULT_THAW_QUEST_FAMILY_1`, 2026-09-05): reveal via CARTOGRAPHY, the six
  vaults as quest Sites at the fixed tiles (so §3.9's six `world_commit`
  placements are now only for V5's landmark and hand-finish), the V6 thaw as a
  vanilla refuelable heart taking the same `AIPersonaCore` as §2.3, the
  wake/loot/leave branches, the ship-claim thread and the Reclamation.
- `design/Jawa/reconciled_lore/FUTURE_VECTORS.md` — "the dungeons arc" bullet
  now points here.
- `infrastructure/state/items/ASSAILANT_DUNGEON_BUILD_1.md` — spec/verify point
  here.
- `infrastructure/state/items/VAULT_DUNGEON_BUILD_1.md` — spec/verify point
  here.
