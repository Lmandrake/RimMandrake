# ARIDSHRUBLAND_SHIPPING_NAMES_1 — owner card: arid_shrubland working names

## the ask

`design/Jawa/worldbuilding/biomes/arid_shrubland.md`'s own "Owed" section
lists a set of names still the owner's pick:

> **Names, owner's pick:** the giants, the snake-analogs, the bird-analogs,
> the sweetline trees, the fuzz itself, venomvine (working name stands?), the
> Stall and the Gale as player-facing weather names.

The sweetline trees already shipped under their working name
(`RUT_SweetlineTree`, "sweetline tree" — `TREE_GRAPHICS_OWNERSHIP_1`), so
that one is likely settled by use, but is included below in case it isn't.

This pass (`COMMISSION_LEDGER_CLEANUP_1`, arid_shrubland sheet) shipped THREE
more of these under working names, which is what makes this card concrete
rather than abstract:

- **`RUT_Fuzz`**, label "the fuzz" — the biome's dominant groundcover plant
  (0.9 commonality), `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/
  RUT_Fuzz.xml`.
- **`RSW_ShrublandGiant`**, label "the giant" — the huge-grazer flagship
  (reskinned Fambaa body/art), `src/RimStarWars/SWBestiary/Defs/
  ThingDefs_Races/RSW_ShrublandGiant.xml`.
- **`RSW_TunnelSnake`**, label "the tunnel snake" — the signature corridor
  predator (reskinned Klorslug body/art), `src/RimStarWars/SWBestiary/Defs/
  ThingDefs_Races/RSW_TunnelSnake.xml`.

Venomvine already has a def (`RM_Venomvine`, `VENOMVINE_CONTACT_VENOM_BUILD_1`)
under its own working name, and the biome doc's own Owed line already
half-asks the question — "(working name stands?)" — so it's folded in here
too rather than opening a fourth card.

## the decision this needs

For each of the five names below, pick one — or write your own, which beats
every option here:

1. **The fuzz** (`RUT_Fuzz`) — the knee-high silver-green groundcover.
   Working name is plain and descriptive; alternatives could lean more
   Jawa/alien (in the register of `nysyllin`, `dervish`, `creep stern`
   already in this biome's flora list) or stay plain-English.
2. **The giant** (`RSW_ShrublandGiant`) — the huge-grazer flagship with large
   young. "The giant"/"the giants" collectively covers this flagship AND the
   pre-existing donor megafauna already in the biome (Ronto, Bantha,
   Corinathoth) — worth deciding whether the ruling should name the FLAGSHIP
   specifically or the whole huge-grazer class.
3. **The tunnel snake** (`RSW_TunnelSnake`) — the corridor ambush predator.
4. **Venomvine** (`RM_Venomvine`) — "(working name stands?)" per the sheet's
   own text; may need no action at all if the answer is yes.
5. **The Stall / the Gale** — the biome's two named wind-weather states
   (§4 "The ripple"). No `WeatherDef` exists for either yet
   (`arid_shrubland.md`'s own Owed section: "no WeatherDef exists yet for the
   Stall/Gale; SS Owed") — these names would land on defs nobody has
   authored, so this half of the card is naming-ahead-of-building; fine to
   rule now or defer until the WeatherDefs themselves are built.

## why it matters

Three working-name defs shipped live this pass (same status as
`RUT_Staggerseed`, gated on `STAGGERSEED_SHIPPING_NAME_1`) — every `RUT_Fuzz`/
`RSW_ShrublandGiant`/`RSW_TunnelSnake` defName, label and texPath is
provisional. The rename, per the staggerseed precedent, is cheap (defNames,
labels, texPaths, the one `RUT_AridShrubland.xml` wildPlants/wildAnimals line
each) and blocks nothing else — these items don't need to stay open on this
card the way `DESERT_STAGGERSEED_BUILD_1` stayed open on its own, since
nothing about these three defs' mechanics depends on the name.

## Watch out

- The name lands in more than one place per def: `RUT_Fuzz` touches its
  ThingDef and the `RUT_AridShrubland.xml` wildPlants line; each animal
  touches its ThingDef + PawnKindDef (same defName reused for both) and its
  own wildAnimals line, plus any texPath under the shared donor art
  directories stays put (the ART is reused from `RSW_Fambaa`/`RSW_Klorslug`,
  UNCHANGED — only the new defName's own label/description need to move, not
  the texPaths, since those still point at the donor's own art folders).
- `rutfuzz_v1` (`infrastructure/artpipe/pending/`) is a queued art job under
  the working id — same as `RUT_Staggerseed`'s own jobs, the render is
  name-free so nothing needs re-queuing when the name lands, but the
  ThingDef's `texPath` will need to move to wherever the final name's texture
  folder ends up once the daemon delivers it.

## criteria

Each of the five names carries the owner's chosen name (or is explicitly
ruled "keep the working name"), and `arid_shrubland.md`'s own "Owed" names
line is updated to drop whichever are resolved.

## 🔴 Owner ruling 2026-09-21 — partial (1 of 5)

**#2, the giant (`RSW_ShrublandGiant`): RULED — `thunderstep`.** Owner, verbatim: "Thunderstep",
in answer to a question scoped specifically to the flagship def (not the collective "the
giants" class, which still covers the flagship plus the pre-existing donor megafauna and is
unaffected by this ruling). Label changed on both the `ThingDef` and the `PawnKindDef`
(same defName reused for both, per this item's own "Watch out"), plus the life-stage label
`giant calf`/`giant calves` → `thunderstep calf`/`thunderstep calves`
(`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShrublandGiant.xml`). No live-tile or
save-compat risk — MEASURED via literal-string check against
`CANONICAL_ASHKARR_START_2026-09-12.rws`: no placed `RSW_ShrublandGiant` instance exists on
the canonical save.

## 🔴 Owner ruling 2026-09-21 — 4 of 5 now landed

**#3, the tunnel snake (`RSW_TunnelSnake`): RULED — `yanker`.** Label changed on both the
`ThingDef` and the `PawnKindDef` (same defName reused for both). No life-stage sub-labels
existed to rename. No live-tile/save risk — MEASURED via literal-string check against
`CANONICAL_ASHKARR_START_2026-09-12.rws`: no placed `RSW_TunnelSnake` instance exists.

**#4, venomvine (`RM_Venomvine`): RULED — stands, no rename.** Card closes with no action
on this def.

**#5, the Stall/the Gale: RULED — stand, locked in now** ahead of their `WeatherDef`s being
built, so whoever builds them has a name to build against.

**#1, the fuzz (`RUT_Fuzz`): STILL OPEN, do not pick a name.** Owner, verbatim: "Bench is
currently shipping you work items for this question, please wait." BENCH has a work item
in flight for this specific name — this item stays open on this one entry only until that
lands; do not rename `RUT_Fuzz` ahead of it.

`arid_shrubland.md`'s "Owed" names line updated to reflect all four landed rulings plus the
one still-waiting name.
