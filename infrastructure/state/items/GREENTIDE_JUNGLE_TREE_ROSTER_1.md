# GREENTIDE_JUNGLE_TREE_ROSTER_1 — ten-plus jungle trees of our own, plus the signature giant

## the ruling

**Owner, 2026-09-22**, verbatim, answering a card that asked whether the generic Greentide's
oak-and-poplar tree list was wrong:

> *"Absolutely not. We should have wild jungle trees with bizarre Starwars names. And lots of
> them, a diversity of perhaps ten types of trees at least. Plus the signature huge tree."*

("Absolutely not" answers *"is that deliberate?"* — he is rejecting the current list, not
defending it.)

🔑 **And he already ruled the ownership question, on trees specifically**, on
`TREE_GRAPHICS_OWNERSHIP_1`: *"Rather than use the whole Comingo tree thing, we should simply
generate our own tree graphics at the scales we want and drop all the nonsense of multiple tree
mods modifying our designs to who-knows-what scale."* ⇒ **the ten-plus trees are OURS**, not more
donor rows. Do not re-ask him this.

## what exists — MEASURED 2026-09-22 (parsed off our own files, on the Mac)

### The generic twin has temperate flora under a rainforest texture

`src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml` — `texture`
`World/Biomes/TropicalRainforest`, described as a furiously humid ground-hugging jungle, and its
entire `wildPlants` block is six vanilla temperate entries:

| plant | commonality |
|---|---|
| `Plant_TreeOak` | 2.0 |
| `Plant_TreePoplar` | 1.2 |
| `Plant_Bush` | 1.5 |
| `Plant_Grass` | 2.0 |
| `Plant_TallGrass` | 1.0 |
| `Plant_Berry` | 0.6 |

⇒ **Two trees, both temperate-forest.** That is the list he rejected.

### The campaign twin already has the bizarre names — but 10 of its 11 rows are BORROWED

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml` (frozen 2026-09-22):

| plant | commonality | owner | tree? |
|---|---:|---|---|
| `AB_JungleTree` | 3.0 | donor `sarg.alphabiomes` | tree |
| `Plant_HydenockTree_Wild` | 1.5 | donor `mlie.starwarsanimalcollection` | tree |
| `Plant_JoganTree_Wild` | 1.2 | donor `mlie.starwarsanimalcollection` | tree |
| `RUT_GiantLeaf` | 1.0 | ✅ **OURS** | no |
| `Plant_MujaFruit_Wild` | 1.0 | donor Mlie | no |
| `Plant_HubbaGourd_Wild` | 0.8 | donor Mlie | no |
| `AB_SugarFamewort` | 0.6 | donor Alpha Biomes | no |
| `Plant_FelucianGlowspore_Wild` | 0.6 | donor Mlie | tree |
| `Plant_Bubblespore_Wild` | 0.5 | donor Mlie | no |
| `Plant_Chakroot_Wild` | 0.5 | donor Mlie | no |
| `Plant_TookeTrap_Wild` | 0.5 | donor Mlie | no |

🔑 **So the gap against his ruling is TREES, not flavour.** The bizarre Star Wars names are
already there — hydenock, jogan, muja, hubba gourd, felucian glowspore, chak-root, tooke-trap —
but only **4 of 11 rows are trees**, and **exactly one row of eleven is a def of ours**. He asked
for ≥10 tree types, ours.

### The signature giant already exists as a deliberate placeholder, and its art is already made

`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_Placeholder_GreentideGiantTree.xml`
(GREENTIDE_MECHANICS_2 M6) is a `ParentName="TreeBase"` stub that exists **only** so
`RM_TreeFallUtility` / `RM_CompCrackFall` / `RM_FellableTreeExtension` are provably wired. Its own
header says it is *"NOT the real roster giant that the flora roster pass eventually authors"* and
that its brief forbade authoring the real one. **This item IS that flora roster pass.**

✅ **Art check done before filing, per CLAUDE.md's standing rule.** Real giant-tree art is already
generated and reserved for exactly this: `infrastructure/artpipe/done/jungletree_v1.json`, which
the placeholder names as *"reserved, already roster-tracked art … for the flora roster pass's own
real giant"*. Further already-finished tree/fern subjects in `artpipe/done/`: `alientree_v1`,
`alientree_v2`, `alientreepolluted_v1`, `halfalientree_v1`, `hydenocktree_v1`, `jogantree_v1`,
`mangrovetree_v1`, `firevinetree_v1`, `largeslimytree_v1`, `greenrockfern_v1`, `slimyfern_v1`,
`fungusfern_a/b/c/d_v1`. ⇒ **Search `artpipe/done/` and `_artsrc/` per subject before queuing a
single new art job.** A large part of ten trees' worth of art may already be on disk.
⚠️ UNVERIFIED which of those subjects are *replacement art for the donor rows above* versus free
for a new def of ours — several match donor defNames (`jungletree`→`AB_JungleTree`,
`hydenocktree`/`jogantree`→the Mlie rows). Establish that per subject before reusing one.

## 🔴 The tier trap — where these defs may and may not go

**A RimMandrake-tier def never names Star Wars** (`biome_mod_architecture.md` §7 Q11). So:

- ⛔ **The bizarre-named trees do NOT go in `RM_Greentide`'s own `wildPlants`.** That def is
  certified campaign-free and Q11-compliant; putting Star Wars flora in it is the same violation
  the paint list was just corrected for ordering (`f4998b494`).
- ✅ **They go in the Star Wars / campaign tier and reach the biome by PATCH**, exactly as the 22
  Star Wars animals already reach it through
  `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`. That file is the shape to copy.
- ⇒ `RM_Greentide`'s own list stays a vanilla-safe floor so the mod still generates on a stranger's
  planet with no dependencies. Whether that floor's two temperate trees should become vanilla
  *tropical* ones is a separate, smaller question and is **NOT ruled** — his answer was about the
  bizarre-named roster, not about the generic fallback.

🔴 **`BiomeFlora_Ashkarr.xml` is GENERATED — do not hand-edit it.** Header: *"GENERATED by
design/Jawa/mods/biome_flora.py — do not hand-edit."* `TREE_GRAPHICS_OWNERSHIP_1` already hit this
and recorded it. Flora wiring goes through that generator, or through a separate hand-owned patch
file the generator does not own.

## spec

1. **Design the roster first, on paper**: ≥10 jungle TREE species with bizarre Star Wars names,
   plus the signature giant. Canon names get checked against
   `design/RimStarWars/canon_references/` — ⚠️ and absence there proves nothing, it holds 137
   entries by design.
2. **Per subject, search `artpipe/done/` and `_artsrc/` before queuing art.** Establish for each
   candidate whether existing art is free or is a donor row's replacement.
3. **Author the defs in the correct tier** (`RSW_`/`RUT_`), `ParentName="TreeBase"`, and wire them
   onto the biome by patch — never into `RM_Greentide`'s own def.
4. **Replace the placeholder giant** with the real one and retire
   `RUT_Placeholder_GreentideGiantTree.xml` only once the feller mechanisms
   (`RM_FellableTreeExtension`, `CompProperties_CrackFall`) are re-pointed at the real def — that
   placeholder is load-bearing for three mechanisms today.
5. Decide the donor rows' fate: his tree ruling points at replacing the three donor TREES with
   ours. ⛔ Not an eviction sweep — the non-tree donor rows are out of this item's scope.

## verify

`RM_Greentide`'s own `wildPlants` still names zero Star Wars content. The biome's patched roster
carries ≥10 tree species that are defs of ours. The real giant exists, the placeholder is gone, and
all three feller mechanisms point at the real def. `validate_patch.py` clean on every touched file.
⛔ No live-proven claim from the Mac — no game and no def dump here.

## criteria

Landing in the Greentide looks like a Star Wars jungle, not an oak wood, and every tree in it is
ours.

## Watch out

- 🔴 **The generic def is not a placeholder.** It is 123 lines *because* it is deliberately
  campaign-free. Do not "enrich" it by copying the campaign twin's body in — that is the exact
  move `biome_mod_architecture.md` §4a and the twin's own frozen header both forbid, and it was
  nearly shipped twice.
- ⚠️ A `<li>` in the wrong place discards the WHOLE def, silently.
- ⚠️ `wildPlants` uses the `<DefName>commonality</DefName>` shorthand, not `<li><plant>` children —
  a parser written for the `<li>` form reads every entry as empty and reports a roster of `None`.
  Cost me a contradictory measurement this session before I read the raw block.
- ⚠️ Donor rows carry `MayRequire`; ours must not, or the biome silently loses them for a player
  without that donor mod.
