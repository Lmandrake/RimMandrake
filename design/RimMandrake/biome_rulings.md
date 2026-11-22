# Biome, roster and naming-tier rulings — owner's words

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

## 🔴 A biome's mechanics work by their conditions — owner, 2026-11-21

Before you design, build or audit a biome's mechanic, read `GUIDING_PRINCIPLES.md` entry 1. By default, a mechanic works by the physical conditions where it acts (sun angle, heat, water, fire, ground, roof, food), not by which biome it is in. This is a default, not a prohibition: many mechanics will in effect appear in one biome only, because only that biome has the conditions. A mechanic that is a heavy load even where it is not active may stay unloaded outside its parent biome, as an exception written in the mod's design with its reason. A biome holds its data: plants, animals, terrain, weather odds and map generation; the roster rulings below are biome data. A biome depends on a mechanic, showcases it, or holds its materials or sources. Vanilla and third-party biomes follow the same rule. A mechanic is tested where it matters, in game on its home biome. His words and card answers: `design/RimMandrake/standing_rulings.md` §Biome mechanics work by their conditions. What each existing mod converts at its next version: `design/specs/2026-11-21-guiding-principles/conversion_list.md`.

## 🔴 A BIOME WITH ZERO TILES IS NOT A DEFECT — owner, 2026-09-20, said repeatedly

> *"Correct we will repaint the whole world when all the biomes are in. **You don't need
> to keep rediscovering this.**"* · *"Don't worry about worldmap painting. Once we have
> all the biomes in mods we will do the painting once and for all."*

**The planet is painted ONCE, at the end, after every biome's content is mod-migrated.** Biome-to-tile
assignment is redone wholesale at that pass. *(Packaging ruled 2026-09-27, §7 Q17 of
`design/RimMandrake/biome_mod_architecture.md`: the biome mods were merged into ONE
player-facing `RimMandrake.Biomes` mod with per-biome toggles — `BIOME_MOD_UNIFICATION_1`, closed 2026-10-09.)*

- ✅ **A BiomeDef of ours carrying 0 of 21,872 tiles is the EXPECTED mid-migration state.**
  It is not a finding, not a defect, and not a reason to do, defer or escalate anything.
- ⛔ **Never repoint owned content at a donor def to make it appear on today's map.** That
  is backwards and was nearly shipped twice.
- ⛔ **Do not cite a tile count as evidence that something is or is not built.** It answers
  a question nobody is asking until the painting pass.
- ✅ Do keep a paint list of owned BiomeDefs as biomes finish, so the repaint has a source
  of truth. Item: `BIOME_PAINT_ONCE_AT_THE_END_1`.

🔴 **This has now cost three reconciliation passes.** The Pyrelands was "discovered" to
have all its content on `RM_FE_Pyrelands` with 0 tiles on 2026-09-19 AND AGAIN on
2026-09-20, the second time producing a whole filed item
(`PYRELANDS_WRONG_BIOME_DEF_1`, closed) and a false report to the owner. **If you find
yourself about to report that one of our biomes is on zero tiles, you have rediscovered
this. Stop.**

## 🔴 And the instrument that keeps producing it: the tiles CSV is a RECORD, not the planet

`world/ASHKARR_WORLDMAP_tiles.csv` is **exported from the savegame**, last on 2026-09-12.
Its own freeze stamp (`ASHKARR_WORLDMAP_tiles.csv.frozen.json`, owner ruling 2026-09-07)
says it outright:

> *"It is a RECORD of the planet, not a rival to it. To change the world, change the
> WORLD and re-export — never edit this file and import it back."* … *"Any future
> live-vs-CSV validate must state which direction it is evidence for."*

⇒ **Reading that CSV tells you what the planet looked like on its export date, never what
it is now.** A live bridge edit after that date is invisible to it — which is exactly what
happened: a live read on 2026-09-19 recorded the Pyrelands on 222 tiles of
`RM_FE_Pyrelands`, while the CSV still showed 222 on the donor `ZBiome_Grasslands`. ⛔ Do
not resolve such a disagreement from the CSV, and ⛔ never call a CSV-derived tile count
MEASURED about the live world — the live system is the only instrument for "right now"
(`~/.claude/skills/measuring-large-artifacts`).

## 🔴 The painted worldmap answers "which biomes exist": owner, 2026-10-28, ruled more than once

> *"Why have I had to rule ok this multiple times? Look at the painted worldmap please."* ·
> *"There is only the sea floor. Of course. That's all they ever was."* · *"Toxic pools.
> Near the terminator. Yes it's there. Look harder."*

**The painted worldmap is the 2026-10-20 dev world:** `world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_tiles.csv`
and its render report `D:\ClaudeWork\remake\2026-10-20\view\biome\ASHKARR_DEV_LANDED_2026-10-20.report.json`.
It holds **27 biomes**: 26 `RM_` defs and `RUT_Umbra`, the **Auroral Umbra** (2,531 tiles, perpetual
aurora, kept by the 2026-10-19 ruling, sheet `the_propane_lakes.md` §0). Every other `RUT_` def is a frozen twin,
and its RM_ successor wins. **A sea IS its floor:** one row per sea, and the `RM_SeabedFloor_*` defs are
plumbing. **RM_Cauldron's sheet is `design/Jawa/worldbuilding/biomes/cauldron.md`**, keyed
`poison_forest` in `_freeze_matrix.csv`: toxic pools in the terminator band. ⛔ Never ask him about a
biome's existence, home or sheet before reading those files. He had to rule again because
`biome_mod_architecture.md` §7 Q1 still said "Umbra is NOT a biome" after 10-19, and because this file
carried no Umbra, painted-map or Cauldron entry. The 2026-10-28 audit then read the 09-12 record
instead of the painted map. Corrected in `biome_name_provenance_audit_2026-10-28.md`.

## Design process and biome/roster rulings

- 🔑 **Before designing anything, read the source and the roster — this project keeps having already built
  it.** MEASURED 2026-09-23 in one session: the owner proposed a "special oil to seal part of the greatbole
  so it cannot regrow" and it ships as `RM_ToxinSealant` (item + terrain) with
  `RM_MapComponent_LivingRegrowth` **already gating regrowth on that terrain**; the grubs' two behaviours are
  `RM_EatCleanableExtension` and `RM_ParentalEnrageExtension` with one axis widened each; their breeding is
  `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` + its alert; and the mining thresholds need no
  new tracking because `BoleRecord.footprint`/`timers` are already Scribed. **Four of six mechanisms already
  built.** Again 2026-09-25: `SEA_SHORE_TILE_MUTATOR_1` was filed and sent to design while
  `mandrake.rm.seashores` — the exact mutator — had shipped two days earlier. ⇒ Search `src/` before FILING, not only before building. ⇒ Same for CONTENT: the flora roster had already named the wasps' hosts, the ant hive's farmed
  species and the sealant's toxic plant. ⛔ A design pass that invents before it reads will re-invent.
- 🔴 **Say which greatbole you mean, every time — the species is THREE defs.** `RM_Greatbole` is the mature
  fellable giant (roster row 22); `RUT_GreatboleHeartwood` is the mineable `RockBase` blob a player actually
  sees and digs, carrying its own flat-colour placeholder; `RUT_GreatboleCore` is a **1×1 bookkeeping
  marker** whose `drawSize (7,7)` renders a retinted vanilla `DeepDrillPowered` across the middle of the
  wood — a real visible defect in shipped content (`GREATBOLE_BARK_EDGE_ART_1`). Confusing them produced two
  false statements to the owner in one session, in opposite directions.
- 🔑 **An animal belongs to ONE biome unless there is an IN-GAME reason** — owner ruling
  2026-09-21, verbatim: *"Animals sound be biome-specific unless there is an in-game reason
  (e.g. flyers that migrate, young versions that grow in the miasma then migrigate to the sea
  later, etc.) So stonebacks hould have one home. We have plenty of creatures left to fill
  rosters if there are holes."* ⇒ 🔑 **A hole in a roster is filled with a NEW creature, never
  by re-using a neighbour's** — we have surplus cast. MEASURED 2026-09-22: **55** species are
  wired into more than one of our biomes. (⛔ Not 52 — that figure was published twice, on two
  different membership sets, by an instrument that cannot read a patched-in roster. See the twin
  trap in `infrastructure/state/facts/instrument_traps.md`.)
  🔴 **The carve-out is NARROW, and habitat is not part of it** — owner, 2026-09-22: *"you are not
  understanding. I meant pick one arid home."* ⇒ **when he names several biomes for a creature,
  that is the CANDIDATE set, not an assignment**, and "they're both arid / both nightside / both
  sea" is **not** an in-game reason. Only his two mechanism cases are: a flier that migrates (he
  widened it: *from a wetter region into a hot one to lay eggs*), or a life stage that moves.
  🔴🔴 **EVICTIONS ARE STOPPED, AND THIS IS NOT A RULE SYSTEM** — owner, 2026-09-22: *"Let's stop
  evictions right now, because I think it's much better to carefully handle biome by biome rather
  than sweeping changes between unfinished biomes and nearly finished biomes."* ⇒ **No pass edits a
  roster to enforce this law.** A biome's multi-homed species become rows on **that biome's own
  review sheet** when it comes up for its sitting, judged at that biome's stage of completion.
  Deliberate multi-homing is **annotated in place, never cut** (worked precedent: the screecher,
  `29ccede91` — both rosters keep it, both say why, both say do not "fix" it).
  🔴 **The failure this ruling ends, because it cost a whole session:** "which biome does this
  creature live in" was escalated into a tie-break algorithm, and three owner cards each *added a
  clause* to it (a canon fork, a provenance override, a scope exception) until it deleted a species
  out of the Greentide roster that had been frozen and cast **the same day**. His diagnosis: *"I
  don't think we should be having rules here. This is a human review process issue."* and *"Just
  don't apply these broad sweeping rules to overturn human requests."* ⇒ 🔑 **If consecutive
  questions to him each add a clause to a procedure rather than resolving a concrete case, STOP** —
  it is review work, and review sheets are the existing machinery. ⛔ **Do not re-derive the
  algorithm from the rulings recorded in `BIOME_SPECIFIC_FAUNA_LAW_1`**; that item is now input to
  per-biome sittings, not a work queue. ⛔ And a rule derived in-session never overturns a placement
  a human already approved.
- 🔑 **A sea biome describes BOTH its floor and its catch** — owner ruling 2026-09-21:
  *"The biomes should be describing the sea floors (what you encounter as an animal there) as
  well as what you can FISH out of the oceans on the shore. There should be defs made for each
  fish as something swimming around the floor area as well as something you can pull out as a
  fish."* ⇒ each sea species owes **two** defs: a floor resident in `<wildAnimals>` and a
  catchable entry in `<fishTypes>`. ⚠️ **Only fish-sized creatures owe a catch** (decision taken by question card
  2026-10-06): giants and predators (RM_GrippingTerror, RSW_SandoAquaMonster) stay floor-only.
  🔴 **THE SHIP IS THE ONLY WAY DOWN AND THE ONLY WAY BACK — owner, 2026-09-26, verbatim:
  *"You can't 'dive' as an individual pawn nor return as one. It's ship or nothing."*** The
  gravship carries the player onto the sea floor and carries them off it. ⛔ The old
  `RM_DiveEligible` shore-terrain mechanism — right-click a tagged shallow cell and a
  colonist swims down — is **RETIRED AND DELETED FROM THE CODE**, along with
  `RM_FloatMenuOptionProvider_Dive` and both JobDrivers. 🔴 **The ship FLIES to the sea floor:
  it is its own planet layer, `RM_SeabedLayer`** (`2db33bf23`). Owner, 2026-10-01: *"the sea hatch
  might have been something from a previous build. Now the ship just flies to a new planetary
  layer called sea floor."* ⛔ `RM_SeaDiveHatch` is a leftover, not the mechanism — removal is
  `SEA_DIVE_HATCH_REMOVE_1` (the def still exists).
  🔑 **Every fishable is ALSO a living creature on the floor, in EVERY sea** (owner,
  2026-09-26): *"All the fishables should also be alive and moving around in the depths
  (this is true for ALL seas)."* A catch item with no living counterpart swimming the floor
  map is incomplete work, not a finished species.
  ✅ **RE-MEASURED 2026-09-26 on the RM tier, which is what ships: all four seas now carry
  `fishTypes` AND a real floor roster** — Scald 3 inline + 3 canon patch-added, Grey Sea 6,
  Twilight Sea 6, Propane Lake 6. The old "no `fishTypes` at all and 2 animals each" line
  described the `RUT_` twins and was already stale; the split did that work.
  🔴 **Parse `<wildAnimals>` as an XML ELEMENT, never by counting `<li>`.** `BiomeAnimalRecord`
  has a custom loader reading the node NAME as the animal and the node TEXT as the commonality
  — `<RSW_Faa>0.5</RSW_Faa>`, no `<li>`. A `<li>` count returns **0 for a populated roster**,
  which is how one pass in this very session first read all four seas as empty.
  ✅ **The "do wildAnimals spawn on an impassable biome" question is ANSWERED — MEASURED from
  the decompiled engine 2026-09-26, and `impassable` is a red herring.** Nothing in
  `GenStep_Animals` or `WildAnimalSpawner` reads it. The real gates are **`animalDensity > 0`**
  (`DesiredAnimalDensity` multiplies `map.TileInfo.AnimalDensity`, so 0 makes
  `DesiredTotalAnimalWeight` 0 and `AnimalEcosystemFull` instantly true) and, for ongoing
  spawns only, a walkable cell that `CanReachMapEdge`.
  ⇒ **Every BiomeDef with a roster must set `animalDensity`** (unset defaults to `0f`). The Propane
  Lake (now `RM_TheChill`, 0.08) was fixed at `3fa505fbb`. The `RM_SeabedFloor_*` biomes' 0 is by design:
  `RM_SeabedFloorLife` copies each sea's cast onto its floor at startup.
- 🔑 **A review sheet's `cut` is scoped to THAT SHEET'S BIOME, never the planet** — owner
  ruling 2026-09-21. The Lantern Deeps sheet cut `RSW_AaroxisDendoria`, `RSW_PodWorm` and
  `RSW_MossBeetle`; all three legitimately remain admitted elsewhere (the first two in the
  Miasma, the third in the Arid Shrubland at 0.3). ⛔ So a species cut in one sheet and
  alive in another biome is **correct, not a leak** — do not "fix" it, and do not read one
  sheet's verdict as a planet-wide sweep. A cut with an empty note says nothing about
  anywhere else.

## 🔑 "Star Wars style" naming is NOT Star Wars IP — owner, 2026-09-22 (Q11a)

*"The fact that we will use "star wars style" naming doesn't mean they have to live in the star
wars layer. The top mod without star wars will look precisely the same as the star wars enhanced
one save for any star wars beasts we populate it with."*

**The tier line is IP, not flavour.** An **invented** exotic name is free to live in the
franchise-free `RM_` tier and be cast inline; only a **genuine canon** name (hydenock, jogan, muja,
chak-root, tooke-trap …) is IP and must route through the Utinni patch layer as Q11 requires.
Authority: `design/RimMandrake/biome_mod_architecture.md` §7 **Q11a**, beside Q11.

- ⇒ 🔴 **A `RM_` biome does NOT get a thin dependency-free "fallback" roster.** The free mod must look
  *the same* as the campaign one, with canon content added on top — never substituting for an
  impoverished base. "Rich enough to stand alone" is a requirement on every `RM_` roster.
- 🔴 **BENCH got this exactly backwards for an hour of his session**: read *"bizarre Starwars names"*
  as canon IP and routed a whole **invented** tree roster into the Star Wars layer. ⛔ Don't repeat it.
- 🔑 **The bigger lesson, and it recurred within 24 hours of the same failure in another domain:** he
  then removed canon from the roster altogether (*"we're making our own"*), which made **four** queued
  questions **moot rather than deferred**. ⇒ **When a tier or provenance question starts generating
  sub-questions, ask whether the CATEGORY is needed at all before adjudicating inside it.**
  Adjudicating first and having the category deleted is the same shape as the multi-homing tie-break
  algorithm he stopped (`BIOME_SPECIFIC_FAUNA_LAW_1`).
- ⚠️ **A canon claim whose evidence is a donor mod's defName is not sourced at all.** A roster row read
  *"Canon. Felucian glowspore is canon Felucia flora; the donor row `Plant_FelucianGlowspore_Wild` is
  the wild form"* — circular, and false: `glowspore` returns **zero** Wookieepedia hits. Verify via the
  search API (`action=query&list=search&srsearch=`), never a guessed exact title — a title miss returns
  `MISSING` and proves nothing. Absence from `canon_references/` proves nothing either (a curated set by
  design), which is exactly why the donor def is often the only evidence available and must still not
  count.
- ⚠️ **`<wildPlants>` uses the shorthand `<DefName>commonality</DefName>` form**, not `<li><plant>`
  children — a parser written for the `<li>` form reads every row as empty and reports a roster of
  `None`. It produced two flatly contradictory measurements of one file in a single session.

## 🔑 No random anima trees, on any biome — owner, 2026-10-11

*"Anima tree is blocked on ALL biomes as a random occurrence. In Utinni, it should be a rare/unique
entity that's placed quite intentionally (TBD)."* Royalty's random anima-tree generation is blocked
planet-wide, not only on Pyrelands. Intentional Utinni placement is undesigned. Item:
`ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR`.

## 🔴 No biome-specific sun or heat — owner, 2026-10-19

*"no biome-specific heat, no biome-specific sun. It's a matter of geometry"* A biome sheet or
BiomeDef never declares a heat kind, a sun-heat number or a shade rule. Its sun is its tile's
position; its hot air is its temperature. Full text: `standing_rulings.md` §Direct Sun.

**Hot water is physics, not a Scald exception** (his card of 2026-11-21): *"the harm comes from the water's heat,
not the map. Any water that hot, on any map, harms the same way; the Scald is simply where it is common."* His card of
2026-11-20 says how it harms: *"yes keep the clock, AND it should be even worse in the Scald water itself (hot water is
not the same as hot air"*. Steam from hot water keeps its exposure clock and the water harms faster than that steam,
on any map where such water is. The Scald's clock is rewritten to read those conditions at its next version. Detail:
`standing_rulings.md` §Direct Sun.

## Natives drink their own environmental water — owner, 2026-11-01

*"Yes, natives should drink their own environmental water. That's a ruling for all Baroque Biomes, period, including this one."* A native creature standing in or beside its biome's own water (the Scald's boil included) must not accrue thirst/dehydration from it; applies to every Baroque Biome. Consequence for the player is unchanged (Scald ban 1, never potable). First finding: `SCALD_NATIVES_THIRST_PROBE_PARCHED_LAKESIDE`; a roster-wide audit is filed as `NATIVES_DRINK_OWN_WATER_AUDIT_EVERY_BIOME`.

## Five biome answers by card — owner, 2026-11-19, 11:20 to 11:24 PM PST

He answered five cards in one sitting. The card store held no copy; the cards and his picks are read from the
Conductor window's session (`66b3b472-803f-4aa2-a899-c6cd70eb7752`, tool results 2026-11-20T07:20:37Z and
07:24:01Z). The ledger event is OWNER tsn `1795159482276691000` on item
`RIMMANDRAKE_ENACT_FIVE_BIOME_ANSWERS_INTO_26_DESIGNS`; it stamps card 1 only, and its "10:17 PM PST" is one hour
early against those timestamps. He typed no words of his own on any of the five. The 26 biome designs carry these
answers in their `Answered on 2026-11-19` sections.

### 1. Cover from orbit: one step each, and steps add up

Card: *"After each landing the Empire searches for the ship from orbit, up a ladder: probe droid, scouts, strike
team. The game has five levels of how hidden a crew is; one level more makes each wait about 1.4 times longer. On
2026-11-18 you ruled that canopy, steam and fog each slow the search one step, and that the Abyss's Dark and the sea
floor are 'VERY concealed. But nowhere pauses it indefinitely.' Two things are open: what ordinary full darkness is
worth on the side where the sun never rises, and whether two kinds of cover add up. I then apply one reading to every
case: cover is what is on the tile at that moment. ... Which cover scale do you want?"*
He picked **"One step each, they add up"**: *"Why: each place earns what it has. Full dark is one step, like fog;
canopy, steam, fog and rock walls one step each, added. Buys: where you land is a real choice everywhere. Costs: the
plain night side is only a little safer than day; a stop there runs about six weeks. Recommended: it keeps your 'no
biome a free hideout'."*

- One step is one level of the crew's visibility: each wait of the search is about 1.4 times longer.
- Ordinary full dark is one step. How dark a tile is comes from the sun's angle at that tile (a measurement).
- Canopy, steam, fog and rock walls are one step each. Steps on the same tile add up.
- The Abyss's Dark and the sea floor are the top level. No sum of ordinary steps goes past the top level.
- Nothing pauses the search for good. No biome is a free hideout.
- Cover is what is on the tile at that moment: fog counts on fog days; a blast, a Burn, an Unveiling or a lit ship
  takes away the dark or the cover while it lasts.

### 2. A biome's first version: one signature that a stop is sure to see

Card: *"Each biome mod has a first version (0.1.0) and a next one (0.2.0). On 2026-11-17 you picked 'Land, life, one
signature' for the first version: terrain, plants, animals, weather, and exactly one signature mechanic. On
2026-11-18 you asked that every design be seen through the Jawa ship on the run, as 'the overriding priority'. The
rewrites then brought many 'did you see that?' moments back into first versions; the Leaning Scrub keeps nearly all
thirteen. Seven designs ask the same thing. How much goes into each biome's first version?"*
He picked **"One signature a stop surely sees"**: *"Why: it keeps both rulings. Land and life, the ship's three
shared systems (cover, hull wear, fuel), and one signature a normal stop must see; the rest goes to 0.2.0. Buys: the
smallest build that can pass. Costs: several of your own picks wait a version and some designs need a re-cut.
Recommended: it keeps your 11-17 hard edge."*

- A biome's 0.1.0 holds land, life, the ship's three shared systems (cover, hull wear, fuel) and one signature.
- A normal stop must see the signature. Each design names its signature and says why a stop is sure to see it.
- Everything else goes to 0.2.0, with its text kept. A moment that the rewrites of 2026-11-18 moved into 0.1.0 goes
  back to 0.2.0 unless it is part of the signature or one of the three shared systems.
- Picks of his that are not the signature also wait for 0.2.0. The card named that cost.

### 3. Rich fuel: three of the strongest, and the Chill stays replete

Card: *"You ruled on 2026-11-18 that most biomes have only the 'hideously slow' fuel route (plants and carcasses,
for emergencies), that 'A few biomes have richer sources', and that buying fuel is 'the intended motivation to have
to trade constantly'. Nine of the 26 designs now claim a richer source: the Abyss, Blue Desert, Cauldron, Fever Wood,
Greentide, Lantern Deeps, Sump, Wastes and Webwork. Two more name a candidate. Only one richer recipe is built: the
Abyss's tholin. The Chill's frozen beach stays the one place full of fuel. How many richer fuel sources do you
want?"*
He picked **"Three or four strongest"**: *"Why: trade stays the main route. The pick is the Abyss (built), the Fever
Wood (your fuel card named its seep-oil) and the Sump (your story card calls it the fuel route). Buys: fewer builds,
and trade matters. Costs: six designs lose a draw and need another reason to visit. Recommended: 'a few' and 'buy
it' are your words."*

- Richer sources: the Abyss (tholin), the Fever Wood (seep-oil), the Sump (tar at the found refinery).
- Replete: the Chill's frozen beach.
- Every other biome has the slow route (biomass rendered to chemfuel) and buying. The Blue Desert, the Cauldron,
  the Greentide, the Lantern Deeps, the Wastes and the Webwork lost their richer claim. The Forge and the Leaning
  Scrub, which named candidates, stay on the slow route.
- He did not pick "Decide at 0.2.0", which moved every richer source but the tholin to 0.2.0. So the three richer
  sources are each biome's fuel in 0.1.0.
- A biome that lost a draw still needs a reason to visit (his note of 2026-11-18): the table is
  `design/RimMandrake/biome_reason_to_visit_2026-11-19.md`.

### 4. Ship ideas turned down before the ship lens stay turned down

Card: *"Before 2026-11-18, review cards offered about twenty ideas where a biome acts on the landed ship: roots that
split a doorframe, a tentacle that holds a hull edge, a mould film that rides the hull to the next landing. You said
no to about six in typed words, for example 'No, we dont need a downwind lee around the ship.' About fourteen were
passed over with no words. Then you put hull wear into the first version and said to keep old version decisions 'a
LITTLE open'. One precedent: you passed over the Greentide's hull rasp on 2026-10-02, then said yes to it by name on
2026-11-18. What should happen to the ship ideas you turned down before the ship lens?"*
He picked **"They stay turned down"**, not the recommended option: *"Why: a decision is a decision. Buys: no work
now, and you can bring any one back by name. Costs: a good idea stays down unless you happen to remember it."*

- Every ship idea that he refused or passed over before 2026-11-18 stays out of every version. There is no review
  sheet and no second look.
- He can bring any one back by name. Nobody else revives one.
- The recount of 2026-11-19 (`design/RimMandrake/biome_declined_ship_ideas_recount_2026-11-19.md`: 11 refused in
  his typed words, 1 replaced in his words, 29 passed over silently) is the list of what stays down.

### 5. Overheating: a crew member walks to shade alone

Card: *"The sun heats people by its angle; shade comes from roofs, parasols and trees. On 2026-11-10 you wrote 'We
need a deeper design discussion here' about what people do when they overheat. That talk has not happened and
nothing is built. The Long Shade design uses a starting rule: before heatstroke turns serious, a crew member walks to
the nearest shade, recovers, and goes back to work; people under the player's direct control are left alone. The
same rule would apply on every day-side biome. Type more if you want the full talk. ... What does a crew member do
alone when the sun starts to hurt them?"*
He picked **"They walk to shade alone"**: *"Why: nobody dies of sun without a sign. Buys: the player sees the danger
as a crew that runs for shade. Costs: work stops on hot days, and the new behaviour needs a test on every day-side
map. Recommended: it is the smallest rule that stops silent deaths, and one rule serves every day-side biome."*

- Before heatstroke turns serious, a crew member walks to the nearest reachable shade where they can recover,
  recovers there, and goes back to work.
- A person under the player's direct control (drafted) is left alone.
- It is one shared rule for every day-side biome, built once with the one sun (`standing_rulings.md` §Direct Sun).
  It is not built. Its test runs on every day-side map.
- He typed nothing more, so the fuller discussion of 2026-11-10 has not been held. The rule stands until he opens
  it.

## Seven signature picks by card — owner, 2026-11-20, about 5:45 to 6:00 AM PST

He answered two cards on the item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED` (the card store:
`python3 src/RimMandrake/rimflow/card_capture.py show RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`;
the ledger: OWNER notes of 2026-11-20T13:54:57Z and 14:02:58Z to 14:03:23Z). The enact item is
`RIMMANDRAKE_ENACT_SIGNATURE_PICKS_INTO_DESIGNS_SLIME_KEEPS_FILM`. Each design carries its answer in its answered
section, with the option's description word for word.

- **Gelatinous Slime: the contact film** (against the recommendation). The gene journey and resistance by gene are
  in 0.2.0. The card named the cost: the Slime had no unique take-away in 0.1.0 until his card of 2026-11-22 gave
  it two draws (§Six biome answers).
- **The Sump: the tar's burden.** The dig is in 0.2.0, so the "hides all" half of his line waits.
- **The Warscar: the mark.** The Settling and the shells its film finds are in 0.2.0.
- **The Weeping Stones: the truce at the water.** The pen, the netting of live stock, the ones that are not fish and
  the vhorrin are in 0.2.0.
- **The four seas: each its own signature, and the river shared by all four.** He took neither offered option and
  typed: *"Actually having underocean rivers should be commonplace in all the oceans, so this isn't even special for Twilight. EACH of them should get an actual special. Perhaps the Twilight should be the falling shards of the ocean's colorful cover"*. This replaces his approval of 2026-11-17 (one signature, the Twilight's river, for the
  four-sea mod). The Grey Sea's is *the sea keeps what it is given*; the Chill's is *the garden answers warmth*; the
  Scald's is **the herd** (picked on the second card; the vent cycle stays as plain land behaviour). His "Perhaps"
  for the Twilight was an invitation, not a ruling; his write-in of 2026-11-22 chose the Twilight's signature, and
  his card of 2026-11-22 put the river in the other three seas at 0.2.0 (§Six biome answers).
- **The Contagion: yes, inside the bubble too.** A raised particulate screen keeps the Bloom off crew inside its
  bubble. The built dose reads only what is overhead, so the build owes a change to a built default; no build ticket
  is filed while the mod is held.
- **The Scald's steam clock: keep.** His words: *"yes keep the clock, AND it should be even worse in the Scald water
  itself (hot water is not the same as hot air"*. On 2026-11-21 he ruled that hot water is physics on any map, not a
  Scald exception (§No biome-specific sun or heat).

## Six biome answers by card — owner, 2026-11-22, about 2:16 to 2:24 AM PST

He answered the questions page `D:\ClaudeWork\rimmandrake\conductor\biome_open_after_picks_20261120.md` on cards, on
the item `RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED` (the card store: `python3
src/RimMandrake/rimflow/card_capture.py show RIMMANDRAKE_PICK_SEVEN_BIOME_SIGNATURES_LISTED_NOT_GUESSED`; the ledger:
OWNER notes of 2026-11-22T10:19:27Z to 10:25:22Z). The enact item is
`RIMMANDRAKE_ENACT_SIX_BIOME_ANSWERS_SLIME_GETS_BOTH_DRAWS`. Each design carries its answer in its `Answered on
2026-11-22` section.

- **The Twilight Sea's signature: the light-wells, with coloured light from the panes everywhere else.** He took none
  of the three candidates and typed: *"The light well but in the places away from the light well there are regions of
  colored ambiance from the colored panes above. It the bare spots are so much brighter! That."* Away from a well the
  floor lies in regions of coloured ambient light from the panes above; the bare spots (the wells) are far brighter.
  The falling panes stay the Twilight's hull wear, not its signature. He did not say whether a well moves: the built
  moving-wells system stays in 0.1.0 as it is, and that question is not ruled. The coloured ambient light is owed.
- **Rivers: "Twilight now, others 0.2.0".** The Twilight keeps its built river in 0.1.0; the Grey Sea, the Chill and
  the Scald get the river at 0.2.0.
- **The Long Shade's 0.1.0 draw: "Chitin and shade mast".** Black chitin and the long-shade mast. The mast is not
  retired.
- **The Rot's 0.1.0 draw: "Food that warms its store".** Native food that warms its own store; the signature and the
  draw are one thing.
- **The Rot's cover from orbit: "It counts: three steps".** Canopy, fog and dark. The dark is measured by the sun's
  angle; the glow of the forest floor does not cancel it.
- **The Gelatinous Slime's 0.1.0 draw: both.** The options were raw slime as the antitoxin and the slime pit. He
  typed: *"Both. We can afford both."* Both are in 0.1.0; the slime pit moves up from 0.2.0.
