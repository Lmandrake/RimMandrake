# Biome name candidates — 2026-09-26

Naming design pass for the twelve `RM_` biomes still carrying an unruled label. Every candidate
is traced to a phrase in the biome's own design sheet (`design/Jawa/worldbuilding/biomes/*.md`).
Already-ruled names (Stillsand, Long Shade, Leaning Scrub, Warscar, Cracked Lands, Pyrelands,
Greentide, Scald, Sump, Forge, Miasma, Weeping Stones, Rust Cathedral, Fever Wood, Forsaken
Crags) are out of scope and untouched.

## Summary

**9 STAY · 3 RENAME** (plus two label-string fixes on names that stay).

| biome | current label | verdict | recommended |
|---|---|---|---|
| `RM_BlueDesert` | the Blue Desert | STAY | — (owner: *"the name stays"*) |
| `RM_Contagion` | the Contagion | STAY | — (owner's pick) |
| `RM_GelatinousSlime` | the gelatinous slime | RENAME (label to the ruled name) | **the Slime** |
| `RM_LanternDeeps` | lantern deeps | STAY — fix label case/article | **the Lantern Deeps** |
| `RM_NightsideIce` | the Nightside Ice | RENAME (sheet: *"name owed"*) | **the Ringing Ice** |
| `RM_PoisonForest` | the Poison Forest | RENAME (sheet: *"'Poison' was a label, not a mechanism"*) | **the Slagwood** |
| `RM_Wasteland` | the wasteland | RENAME — weakest call; keeping it is defensible | **the Dead Ends** |
| `RM_Webwork` | the Webwork | STAY | — (owner's pick) |
| `RM_TheRot` | the Rot | STAY | — (owner's pick) |
| `RM_GreySea` | the Grey Sea | STAY | — (world-map name) |
| `RM_TwilightSea` | the Twilight Sea | STAY | — (world-map name) |
| `RM_PropaneLake` | the Propane Lake | STAY | — (owner, typed: *"the propane lake"*) |

Honest framing: only **two** of the twelve are genuinely open naming questions — the Nightside Ice (its own
sheet says *"name owed"*) and the Poison Forest (its own sheet says the name was never a mechanism). The
Slime is a label that drifted from a ruled name. The Wasteland is a category word the doctrine has leaned on;
renaming it is a taste call, not a defect. Everything else is already ruled or is a world-map proper noun.

## Vanilla collision check

MEASURED 2026-09-26 by parsing every `BiomeDef` under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\*\Defs\**\*.xml` (Core + Royalty + Ideology +
Biotech + Anomaly + Odyssey): **25** labels — `arid shrubland`, `boreal forest`, `cold bog`, `desert`,
`extreme desert`, `ice sheet`, `lake`, `ocean`, `sea ice`, `temperate forest`, `temperate swamp`, `tropical
rainforest`, `tropical swamp`, `tundra`, `underground`, `labyrinth`, `metal hell`, `undercave`, `glacial
plain`, `glowforest`, `grassland`, `lava field`, `orbit`, `scarlands`, `space`. None of the twelve current
labels nor any of the nine candidates (Slime, Slough, Registry, Ringing Ice, Dirty Ice, White Slabs,
Slagwood, Breathing Ground, Smelter Wood, Midden, Dead Ends, Scour) matches or contains one. Nearest
brushes, noted per biome: *Nightside Ice* ↔ `ice sheet`/`sea ice`/`glacial plain` (the rename removes
it); *Wasteland* ↔ `scarlands` (a different word; our own `the_scarlands.md` sheet is the real neighbour).
Modded biome labels in the 600-mod list were NOT swept — only vanilla, as briefed.

Repo-internal collision sweep (grep over `design/` and `src/`, `.md`/`.xml`/`.json`): *Slagwood*, *Ringing
Ice*, *Breathing Ground*, *Smelter Wood*, *White Slabs* — 0 files each. *Dirty Ice* — 12 files, all the
Nightside Ice's own physics prose (expected). *Midden* — 14 files, a lair-structure term (see the Wasteland
block). *Slough* and *Scour* are existing world-map region names, noted in their blocks.

## RM_BlueDesert

- **Current label:** `the Blue Desert` · **Verdict: STAY**
- The sheet (`the_blue_desert.md`) records this as already the owner's call: *"**the name stays**: it IS
  extremely blue, just not up close"* (2026-09-06), and the whole artistic theme is built on the name —
  *"Extremely blue from far away; colorless up close."* It names what a person meets (a blue plain that is
  not blue), not a category. Nothing to propose.

## RM_Contagion

- **Current label:** `the Contagion` · **Verdict: STAY**
- Sheet (`the_contagion.md`): *"**The biome's name is THE CONTAGION** (owner's pick; the earlier working
  name 'the Overdrive' is superseded)"*, reaffirmed 2026-09-10 when "the Overdrive" was kept as the Helix's
  in-faction word for it. Ruled, with identity. Nothing to propose.

## RM_GelatinousSlime

- **Current label:** `the gelatinous slime` · **Verdict: RENAME** (label only — the name is already ruled)
- The sheet is titled *"The Slime"* and says *"**The biome's name is THE SLIME** (owner's pick)"*. The def
  label still carries the donor's working name (`AB_GelatinousSuperorganism` → "gelatinous slime"). This is
  a defect of the label, not an open naming question; the three below are given for completeness.
  1. **the Slime** — *"The biome's name is THE SLIME (owner's pick)"* (sheet intro).
  2. **the Slough** — its largest lobe: *"in four patches: **Slough (58)**, Glass Reach (15), Nightspill (14),
     Chalk Marches (9)"* (§0); a slough is literally a place of mire and a shed skin — apt for *"wearing a
     landscape as its skin"* (§1).
  3. **the Registry** — the thematic handle: *"**the living registry** … a body the size of a country,
     reading everything that touches it"* (intro, §9).
- **Recommended: the Slime.** It is the owner's pick on a frozen sheet; the others are offered only if he
  wants to reopen it, and he has not.

## RM_LanternDeeps

- **Current label:** `lantern deeps` · **Verdict: STAY** (fix the label's case and article: **the Lantern Deeps**)
- Sheet (`the_lantern_deeps.md`) amendment of 2026-09-18 on the owner's word (`DEEP_FLORA_RENAME_1`):
  *"lanternstone and **the biome name unchanged**."* The name is grounded in the place itself — *"Lantern
  Deeps is named for the light these leak"* (§8, the natural emergences) and *"a blue lantern burning under
  the mountain"* (§9). The only defect is the label string: lower-case, no article, out of house style.
  Not a naming question.

## RM_NightsideIce

- **Current label:** `the Nightside Ice` · **Verdict: RENAME**
- The sheet itself (`nightside_ice.md`) says the name is open: *"own def, not a patch; **name owed if the
  dirty-ice plateau wants one**"*. "Nightside Ice" is a coordinate plus a material — a category, and it
  brushes vanilla's `ice sheet` / `sea ice` / Odyssey's `glacial plain`. The sheet's image: *"dirty white ice
  on the highest ground of the night, under the aurora, with something moving inside it."*
  1. **the Ringing Ice** — *"at −60 °C water ice does not behave like snow, it behaves like rock. **The
     ground rings when you strike it** and fractures in slabs"* (§1).
  2. **the Dirty Ice** — *"Not blue: **dirty ice** (owner's ruling)… white ice holds impurities — bubbles,
     mineral dust, everything the distillation column drops from the sky"* (§1); the owner's own phrase for
     the place, and the physics the whole second pass hangs on.
  3. **the White Slabs** — *"Ice as hard as quartzite, **white**, on the highest ground of the night"* and
     *"fractures **in slabs**"* (§1); *"a slab calving — and whatever was frozen inside is suddenly in the
     open"* (§3).
- **Recommended: the Ringing Ice.** It names the first thing a person does here — strike the ground and
  hear it ring like rock — and carries the sheet's unease (a sound from a place where *"nothing… makes a
  sound on purpose"*) without repeating a vanilla label.

## RM_PoisonForest

- **Current label:** `the Poison Forest` · **Verdict: RENAME**
- The sheet's own diagnosis: *"**'Poison' was a label, not a mechanism**, so its trees defaulted to
  tree-shaped."* The mechanism it found is metallurgical, not toxic: *"The poison is not a weapon. It is
  **metabolic waste**, and the tree is slowly plating itself in its own tailings"* (§4). The artistic theme
  is *"**A forest slowly turning into a smelter**, lit like a dawn that never arrives."*
  1. **the Slagwood** — *"an old trunk is **part tree, part slag heap**"* (§1); *"trunks widening downward
     into scab and **slag**"* (§9).
  2. **the Breathing Ground** — *"A low, wet-black forest standing in permanent dusk over **ground that
     breathes**"* (§1); *"they stir constantly, because **the ground exhales**"*; the vents are the anomaly
     the whole biome is forced from (§2).
  3. **the Smelter Wood** — *"A forest slowly turning into a **smelter**"* (§9); sits beside *the Fever Wood*
     in the same grammar.
- **Recommended: the Slagwood.** One concrete word for what you actually walk through — trunks plated in
  their own tailings — in the Warscar register; it drops the genus-word "forest" and the label-word "poison"
  the sheet itself disowned. No vanilla label contains "slag" or "wood" alone (`glowforest` is the nearest).

## RM_Wasteland

- **Current label:** `the wasteland` · **Verdict: RENAME** — the weakest of the rename calls; see the note.
- "Wasteland" is a category word, lower-cased in the def as if it were one, and the world doctrine uses it as
  a *term* ("the war-legacy split… `Wasteland` is the poisoned one"). The sheet's handle is **"no outlet"**;
  its image *"a just-lost sunset, flickering with wrathful lightning."*
  1. **the Midden** — *"for all the ages since the war it has also been **the place you throw what nobody
     wants**, because it was already ruined"* (§1); *"**the tipping fee** — the one biome with an income
     stream attached to its awfulness"* (§7); *"the planet's chimney soot"* (§2).
  2. **the Dead Ends** — *"**the salt plains are dead river ends** … every river branch ends in a dead salt
     plain — 235 termini"* (§0); *"the first truly **dead** ground"*; *"anywhere the planet drains to and
     nothing drains from"* (§2) — a dead end is exactly a place with no outlet.
  3. **the Scour** — *"**the dark scour** — Sunreach, Cinderdark, Sootreach, Gray Crags"* (§0 family table);
     *"the Wasteland's dark scour"* is how the Blue Desert sheet refers to it too. Already a region name here,
     which cuts both ways.
- **Recommended: the Dead Ends.** It is the sheet's handle ("no outlet") said plainly, and it is literally
  what the place is — the termini of every river on the planet, and the first dead ground on the ladder.
  *The Midden* was the first choice for covering all three drains at once, but "midden" is already a working
  term in 14 repo files — the beast-lair generator's *bone midden*, and a `midden` field in the narrative
  dictionary (`narrative_dictionary_design.md`) — so a biome by that name would muddle a lair-structure word
  used in every lair. **Note:** if the owner feels "the Wasteland" has earned its identity through the
  doctrine that leans on it, keeping it costs nothing; the rename cost is a term used across the world
  definition, not just a label. Vanilla has no `wasteland` label (nearest: Odyssey `scarlands`).

## RM_Webwork

- **Current label:** `the Webwork` · **Verdict: STAY**
- Sheet (`the_webwork.md`): *"**The biome's name is THE WEBWORK** (owner's pick)"*, ratified *"Go for it,
  write it up!"*. Grounded in the mechanism — *"elaborate **webwork** laid through the entire ecosystem"*,
  *"the silk is the plumbing"* — and the thematic handle is *the loom*. Nothing to propose.

## RM_TheRot

- **Current label:** `the Rot` · **Verdict: STAY**
- Sheet (`the_rot.md`): *"**The biome's name is THE ROT** (owner's pick)"*; handle *"the planet's gut"*,
  image *"a pale forest with a heartbeat of rot"*, mechanism *"the rot clock… raw meat left exposed is gone
  within a day."* Ruled, and the name is the mechanism. Nothing to propose.

## RM_GreySea

- **Current label:** `the Grey Sea` · **Verdict: STAY**
- The Grey Sea is a named body of water on the planet, not a working label: `terminator_sea.md` §2 defines
  *"the **Grey Sea** (θ 92, bearing 8, *salt-encrusted, shrinking*)"* against its sister, and `Grey Sea` is a
  region name on the world map (it appears in other sheets' region counts). Its bottom has its own sheet,
  *the Grey Deep* (`the_grey_deep.md`), which inherits the name. The def description keeps it concrete:
  *"salt-encrusted and shrinking faster than its sister sea — the planet's chemical works."* No vanilla
  collision (`ocean`, `lake`, `sea ice` are the nearest). Nothing to propose.

## RM_TwilightSea

- **Current label:** `the Twilight Sea` · **Verdict: STAY**
- Same footing as the Grey Sea: `terminator_sea.md` §2 — *"the **Twilight Sea** (θ 91, bearing 170,
  *moldy*)"*; a world-map region name; its bottom is *the Twilight Deep* (`the_twilight_deep.md`, *"the last
  ordinary sea"*). The two sea names are a deliberate pair (grey/salt vs twilight/mould) and are used across
  at least six sheets. Nothing to propose.

## RM_PropaneLake

- **Current label:** `the Propane Lake` · **Verdict: STAY**
- The owner named it himself, typed verbatim at the terminal-seas sitting
  (`terminal_seas_cast_proposal_2026-09-25.md` §4): *"There is body of liquid called **the propane lake**.
  Then there was an alpha biome called propane lakes that we are redoing… No change. Just confusing
  words."* The sheet (`the_propane_lakes.md`) gives the surrounding land the region name **Umbra** — *"the
  antistellar cap it holds, **Umbra**"*, *"Umbra — the propane sea"* — which is the evocative name if one is
  ever wanted for the *land* def, but the 57-tile water body is *the propane lake* by his own words. Nothing
  to propose.
