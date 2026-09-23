# GREENTIDE_JUNGLE_TREE_ROSTER_1 — ten-plus jungle trees of our own, plus the signature giant

## ✅ Three further rulings, 2026-09-22 — after the 21-row roster was proposed

### 1. 🔴 A FELLABLE GIANT STILL EXISTS. The landmark is not the only giant.

He earlier answered *"which tree is the signature huge tree?"* with **the one already built** —
`RUT_GreatboleCore`. The design pass then found that this **breaks the wood economy**, and the
finding is MEASURED and correct:

- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleCore.xml:49` — `deconstructible
  false`. It cannot be felled.
- `design/Jawa/worldbuilding/biomes/the_greentide.md:199` — *"True hardwood — only from the heart of
  fallen giants."*
- `the_greentide.md:214` — *"The tree ladder runs: normal trees (fall) → giants (crack, fall, hardwood
  jackpot)."*

⇒ Choosing a non-fellable landmark removed the rung the premium wood came from. Put to him as a card,
he ruled: **keep a fellable giant too.** The landmark stays the built structure; a separate huge
fellable tree also exists — *not* the signature, simply the largest thing that falls.

🔑 **So the roster owes a fellable giant row after all**, and it is what finally gives
`RM_FellableTreeExtension` / `CompProperties_CrackFall` real content instead of a placeholder.
⛔ Their roles must stay visibly distinct — one is a landmark you mine, one is a tree that comes down
— or they read as redundant.
⚠️ The earlier instruction in this item and in the roster document to design **no** new giant is
superseded by this.

### 2. Foraging yields the new fruit plant, not a vanilla berry

`RM_Greentide` currently has `foragedFood` `RawBerries` (MEASURED). He ruled the roster's own fruit
plant replaces it. ⚠️ Its nutrition and value now matter where a stock berry's did not — set them
deliberately rather than inheriting.

### 3. The humming grove is a QUESTION, not a mechanic — `GREENTIDE_HUMMING_GROVE_1`

He asked whether trees could hum at differing frequencies to make a soundscape that shifts as you
walk. ⛔ Unmeasurable on the Mac, and **do not infer it works from the Rust Cathedral's shipped hum** —
that is map-wide and camera-attached, not positional. There is also a recorded obstacle (no partial
volume ramp on sustainers) and a signature collision with the Cathedral. All of it is on that item.

### 🔴 And one thing that needs the Desktop before the roster can be authored

The fire ruling — *"Fire will harm and burn things, but no they do not catch fire themselves, just
take damage"* — **may not be expressible as a single `Flammability` value at all.** A value low enough
to prevent ignition may also prevent fire damage, which would break the first half of the ruling.
UNMEASURABLE here. Settle it against the engine before authoring 21 rows that all depend on it.

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
`fungusfern_a/b/c/d_v1`.

🔴 **CORRECTION — my hopeful reading of that inventory was WRONG, and the item said it as if it were
a finding.** I wrote *"a large part of ten trees' worth of art may already be on disk."* MEASURED
2026-09-22 by the roster design pass: **every subject in `artpipe/done/` names its own
`Source row: flora:<biome>:<donorDefName>`**, so a subject is bound to the row it was generated for.
Only **4** key to Greentide/Fever-Wood rows and transfer; ~14 belong to other biomes (the Contagion,
Miasma, Slime, Forge, Rot, Webwork, Lantern Deeps) and are **not free**. ⇒ **10 of 13 trees owe
art.** The standing check-for-existing-art rule still applies, but the answer here came back mostly
negative — do not plan on reuse.

🔴 **And the giant's reserved art is under-resolved.** `jungletree_v1` was rendered at **256×256**
for a tree declared ~10 cells; the canvas law wants **1280×1280**. This is the same defect
`alientree_v2` was re-rendered to fix (256→1024) under `FLORA_LEGIBILITY_BAR_1`, and that fix was
never applied to the four Greentide tree subjects. Shipping as-is puts a 5×-upscaled 256px sprite at
the biome's visual centre.

✅ **Also already ruled, and I nearly re-asked it:** the donor rows' fate is settled.
`Transient/port_tail_2026-09-20.decisions.json` and `port_swac_2026-09-20.decisions.json` are
**frozen**, carrying `approvedSaid: "Yes replace everything."`, and all four Greentide donor trees
carry `decision: replace`. Today's *"draft the replacements for everything right now"* confirms a
standing ruling rather than making a new one.

## 🔴 SUPERSEDING RULING — NO CANON TREES AT ALL. Owner, 2026-09-22, latest.

Shown the verified canon tree list, he removed canon from this item entirely:

> *"I don't think it's important to use actual Star Wars trees. They're not a primary part of the
> universe. Let's just make our own tree and thus the mod isn't encumbered with Star Wars plant lore
> that no one even remembers, easier for the non-star-wars version anyway. You may get inspired by
> the star wars versions you found, but we're making our own. There should be no conniferous plants
> here, but rather large-leafed lush plants, plants with hanging tentacle-like leaves, willow-like
> canopies... get wild with them."*

⇒ **Every tree in this roster is OURS and INVENTED.** Canon research is now *inspiration only* — a
canon tree may suggest a silhouette or an economic role, but no row carries a canon name, and no row
needs a canon citation.

### What this collapses — several open questions are now MOOT, not deferred

- ✅ **The tier tension is GONE.** No invented name is Star Wars IP, so **the whole roster is `RM_`
  tier and sits in `RM_Greentide`'s own `wildPlants`.** There is no Star Wars plant patch layer for
  trees, and the franchise-free mod is automatically as rich as the campaign one — which is exactly
  what the 2026-09-22 Q11a ruling required and what this item could not previously deliver.
- ✅ **The Legends-versus-current-canon question is moot for trees.** He had ruled *"allow, label, and
  have the user verify it's really canon"* — that still governs canon content elsewhere, but no tree
  row is canon any more, so there is nothing to label or verify here.
- ✅ **The "orga is a plant, not a tree" and "is a Force-sensitive tree appropriate" questions are
  moot** — both were canon-admission questions.
- ✅ **The false-canon row is moot too.** `felucian glowspore` was corrected from "Canon" to NOT
  canon earlier the same day (it cited the donor mod as its own evidence); under this ruling it is
  simply one more invented row, like every other.
- ⇒ The canon-verification labour this roster spent is **not wasted**: it produced a set of proven
  silhouettes and economic roles to be inspired by. Keep the research as inspiration notes, drop the
  canon claims.

### 🔑 The silhouette direction — his words are the brief

- ⛔ **No coniferous plants.** A hard ban, biome-wide. (Note the current generic list's `Plant_TreeOak`
  and `Plant_TreePoplar` are not conifers but *are* temperate-forest trees, and they are what this
  whole item replaces.)
- ✅ **Large-leafed and lush** — leaf mass, not needles.
- ✅ **Hanging tentacle-like leaves.**
- ✅ **Willow-like canopies.**
- ✅ *"Get wild with them."*

🔑 These are **silhouette** instructions, and silhouette is what makes a dense canopy legible rather
than a green smear — which matters doubly under `GREENTIDE_BIOME_DENSITY_1`'s ruling that virtually
no square is uncovered. A roster of large-leaf / hanging-tentacle / willow forms reads as distinct
species at a glance in a way a roster of generic round crowns cannot.

## ⛔ SUPERSEDED — the tier split by name provenance (kept only to explain why the roster is RM_)

The section below was correct when written and is now moot for trees, because no tree carries a canon
name. It still governs any **canon** content elsewhere in this biome, so the reasoning is retained.

## 🔑 The tier split — by NAME PROVENANCE, not by aesthetic. Owner ruling 2026-09-22.

**Owner, verbatim**, asked what the jungle looks like for a player with no Star Wars content:

> *"The fact that we will use "star wars style" naming doesn't mean they have to live in the star
> wars layer. The top mod without star wars will look precisely the same as the star wars enhanced
> one save for any star wars beasts we populate it with: we will provide enough diversity here that
> there will be plenty of beasts from non canon sources to make it rich."*

⇒ **This REFINES §7 Q11; it does not overturn it.** Q11's own words are *"RimMandrake should not
name star wars ever"* — that forbids referencing actual Star Wars **IP**. An **invented** name that
merely *sounds* exotic is not IP, so it is free to live in the franchise-free tier.

- ✅ **Invented name → `RM_` tier, in `RM_Greentide`'s own `wildPlants`.** This is where the bulk of
  the roster belongs.
- ✅ **Genuine canon name → `RSW_` tier, patched onto the biome** (hydenock, jogan, muja, hubba
  gourd, felucian glowspore, chak-root, tooke-trap are real Star Wars IP). The shape to copy is
  `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`, which already delivers 22 Star
  Wars animals that way.
- ⇒ 🔴 **There is NO separate thin fallback roster, and the question of one is CLOSED.** The mod
  without Star Wars content looks *the same* as the enhanced one, plus canon beasts on top. So the
  RM-tier roster must be rich enough to stand alone — that is the design constraint, not a
  nice-to-have.

⛔ **An earlier revision of this item said the opposite** — that the bizarre-named trees must all go
in the Star Wars tier and that `RM_Greentide` keeps a vanilla floor. That was BENCH over-reading
Q11 by assuming "bizarre Star Wars names" meant canon IP. It is wrong and is removed.

## ✅ SCOPE WIDENED — all ten borrowed rows, not just the trees. Owner ruling 2026-09-22.

Asked whether the seven non-tree borrowed rows should be replaced now or later, **owner, verbatim:**

> *"We work on drafting the replacements for everything right now. No reason to wait! Let's do this!"*

⇒ This item now covers **our own replacements for all ten borrowed flora rows**, not the ~4 trees
alone. The ≥10 trees remain the headline ask; the seven non-tree rows (muja fruit, hubba gourd,
sugar famewort, bubble spore, chak-root, tooke-trap, and the felucian glowspore) are in scope too.

🔑 **`DONOR_DEFS_PORT_TO_OURS_1` is the existing programme for turning a donor def into ours — read
it before designing a replacement**, and check whether a port already exists. `biome_mod_architecture.md`
§4a records that of the 8 Star Wars `wildPlants` rows, **2 already have our ports and 6 do not**, and
that **casting a donor defName is forbidden**. Do not duplicate a port that exists.

⚠️ `AB_SugarFamewort` is an Alpha Biomes donor invention, not Star Wars — its concept may be kept
under an invented `RM_` name with no canon question at all.

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
