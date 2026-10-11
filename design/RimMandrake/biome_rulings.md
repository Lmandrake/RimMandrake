# Biome, roster and naming-tier rulings — owner's words

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

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
