# GREATBOLE_BARK_EDGE_ART_1 — the greatbole is a wood blob with a bark edge, and its art is a placeholder

## the ruling

**Owner, 2026-09-23**, correcting a misunderstanding in the session:

> *"There has been a significant error in communication. Here's what I want. A blob of wood on the map,
> representing a trunk so vast that you can't even see the tree in the game. The outside edge looks like
> Bark, the same way that the outside edge of stone or minerals looks different than the inside. And it
> 'heals' slowly within itself: wood once removed slowly returns back. The player can carve out tunnels
> within and even remain inside so long as they continue to mine out the wood. How this became a Deep
> Drill I have no idea."*

## ✅ MOST OF THIS IS ALREADY BUILT — MEASURED 2026-09-23 by reading the source

🔑 **Five of the six things he describes exist**, which reframes this item from "build the greatbole" to
"finish how it looks." Read, not inferred:

| his words | what exists |
|---|---|
| *"a blob of wood on the map"* | `RUT_GreatboleHeartwood`, `ParentName="RockBase"`, placed as a footprint of radius **4–6 cells** by `RM_GenStep_LivingBoles` (order 222) |
| *"the player can carve out tunnels within"* | `mineable=true`, `mineableThing` `RUT_Hardwood`, yield 15/cell, `isResourceRock` |
| *"wood once removed slowly returns back"* | `RM_MapComponent_LivingRegrowth` — per-cell `Scheduled → Warning → Crushing` state machine, **Scribed** because a mined-out chamber carries no Thing to re-derive from |
| *"even remain inside so long as they continue to mine"* | the same state machine: a cell regrows quietly if empty, **creaks once as a warning** if occupied, then crushes — pawns pushed to the nearest open cell, items destroyed, buildings damaged |
| *"a trunk so vast you can't even see the tree"* | the blob is the trunk's cross-section; no tree is drawn, by design |
| *"the outside edge looks like Bark"* | 🔴 **NOT BUILT.** `graphicClass Graphic_Single`, one flat texture, **no edge-versus-interior distinction of any kind** |

⇒ **The one genuinely missing mechanic is the bark edge.** Everything else is finished and Scribed.

### 🔴 And a correction to what he was told earlier in the session

He was told *"the landmark is a retinted vanilla deep drill."* **That is wrong about the blob.** Precisely:

- **`RUT_GreatboleHeartwood`** — the blob, the thing a player sees and mines. Its art is its own
  **flat-colour placeholder PNG**, and the def's own header already says *"real bespoke art (a living-wood
  grain, not a rock fleck) is owed, DEPLOY_HOLD."* ⇒ Owed, and already known to be owed.
- **`RUT_GreatboleCore`** — only a **1×1 marker** at the centre, whose `RM_CompLivingBoleMarker` registers
  the bole with the regrowth component at spawn. *This* is the def carrying
  `Things/Building/Misc/DeepDrillPowered` retinted `(74,58,36)` at `drawSize (7,7)`.

🔴 **So "how this became a Deep Drill" has an answer: the marker did, not the blob** — and because the
marker draws at 7×7 from a 1×1 cell, a recoloured mining drill is rendered across the middle of the
wood. ⇒ **That is a real visual defect in shipped content**, and it is the thing that made the greatbole
look like machinery. Fix is one of: give the marker real art, or make it draw nothing at all, since its
job is bookkeeping and the blob is what the player is meant to see.

## ✅ MEASURED 2026-09-23 — the bark edge mechanism (answer in the Desktop section below; the questions that follow were the ones asked)

🔴 **How vanilla makes a stone or mineral's outer edge read differently from its interior is UNMEASURABLE
from the Mac.** No game, no def dump, no decompiler, and RimSage has never connected here. ⛔ Name no
field, class or value for it from reasoning — including anything that looks like an obvious answer.

The question to answer on the Desktop, stated so it can be answered in one sitting:

1. **What does vanilla rock actually do** to get an edge that differs from the interior — a linked/atlas
   graphic, a separate edge def, a corner-filler draw mode, or something else? Read a live vanilla rock
   ThingDef and whatever `RockBase` already supplies.
2. **Does `RockBase` give it for free?** `RUT_GreatboleHeartwood` already inherits `RockBase` and still
   renders flat, so either the parent does not supply it or the child's `graphicData` override defeats it.
   That distinction decides whether this is an art job or a def job.
3. **What art does the answer require** — one texture, an atlas, or an edge set? ⛔ Do not commission art
   before this is known; the wrong number of PNGs is the expensive mistake here.

## ✅ Desktop answer — how vanilla rock gets an edge that differs from its interior (MEASURED, RimSage, 2026-09-23)

**Mechanism: ONE atlas PNG + the linked corner-filler draw mode. No separate edge def, no second texture.**

- `RockBase` (Defs/Core/ThingDefs_Buildings/Buildings_Natural.xml:16-58): `thingClass Mineable`,
  `graphicData.texPath Things/Building/Linked/Rock_Atlas`, `graphicClass Graphic_Single`, **`linkType CornerFiller`**,
  `linkFlags Rock, MapEdge`. Every vanilla mineable (Sandstone, Granite, MineableSteel …) inherits exactly this.
- The atlas: `MaterialAtlasPool.MaterialAtlas` (Verse/MaterialAtlasPool.cs:8-40) slices the ONE texture into a
  **4 × 4 grid of 16 sub-materials**, each `0.25` of the texture with a `1/32` padding inset (`mainTextureScale 0.1875`),
  indexed by the `LinkDirections` bitmask of which of the four cardinal neighbours also link. Sub-tile 0 is "no
  neighbours" (a lone boulder), sub-tile 15 is "all four" (pure interior); the other 14 are the edges and corners.
- `Graphic_Linked.ShouldLinkWith` (Verse/Graphic_Linked.cs:66-81): a neighbour links when
  `linkGrid.LinkFlagsAt(c) & def.graphicData.linkFlags != 0`; out-of-bounds cells link iff `MapEdge` is set.
  `Graphic_LinkedCornerFiller.Print` (Verse/Graphic_LinkedCornerFiller.cs:5-79) additionally prints a 0.5-cell cover
  square over each diagonal gap when both flanking cardinals link, so interior corners read solid.
- `LinkFlags` (Verse/LinkFlags.cs): `Rock = 2` links to every other rock-flagged thing; **`Custom1 … Custom10`
  (0x20000 …)** exist for a def that should link only to its own kind.

**⇒ What the greatbole needs, and the number that matters: ONE PNG, laid out as a 4 × 4 atlas in `Rock_Atlas`'s
cell order** (extract `Things/Building/Linked/Rock_Atlas` from `resources.assets` per `reading-rimworld-graphics`
to copy the exact layout; the sub-tile order is the `LinkDirections` bit order, not reading order). Interior cells
show heartwood, edge and corner cells show bark. Def change on `RUT_GreatboleHeartwood`
(src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleHeartwood.xml:31-32): keep `Graphic_Single`, add
`<linkType>CornerFiller</linkType>` and `<linkFlags><li>Custom1</li></linkFlags>` (not `Rock`, or the bark would
weld onto adjacent stone; not `MapEdge`, a bole never touches the map edge by design). `drawSize` stays 1×1 — linked
graphics are per-cell. The edge is then free: no per-cell edge def, no GenStep work, nothing to Scribe.

⚠️ Two things this does NOT settle, both Desktop/live: (a) whether `Mineable`'s mined-away cell re-links its
neighbours on the same frame (vanilla rock does, so the expectation is yes — it is the same class); (b) the
`RUT_GreatboleCore` 1×1 marker with `drawSize (7,7)` is a SEPARATE defect and unaffected by this.

`needs` moves from `game-up` to `offline`: art can be commissioned now that the PNG count (one atlas) is known.

## spec

1. Answer the three questions above on the Desktop. ⛔ Nothing authored or commissioned first.
2. **Fix the marker's rendering** — real art or no art. Independent of the bark question and the larger
   visible defect of the two.
3. Commission the blob's real art: **living-wood grain, not rock fleck**, in whatever form question 3
   turns out to require, with a distinct bark treatment at the edge.
4. ⚠️ **Check the radius against his words.** A 4–6 cell radius is an INVENTED number (the extension's own
   comment says so) for *"a trunk so vast you can't even see the tree."* It may be too small to read as
   vast — but ⛔ it is not mine to change, and changing it moves every regrowth timer and the roof patch
   with it.
5. Mod Settings per the standing rule — the regrowth rate is exactly the "a number is the experience" case.

## verify

A player walking up to a greatbole sees bark where the mass meets open ground and wood where they have
cut into it, with no mining-drill sprite anywhere. Mined cells still regrow, still creak once, and still
crush what stays. ⛔ No live-proven claim from the Mac.

## criteria

You mine into what is unmistakably a tree, and the tree closes the wound behind you.

## Watch out

- 🔴 **The regrowth state is Scribed save state, not re-derivable.** Any change to the footprint, the
  radius, or the def names risks existing saves. ⛔ Treat this as live shipped content, not a draft.
- ⚠️ **`FEVER_WOOD_MECHANICS_1` is blocked on this exact class** (its F7, *"bore-caves / Greatbole
  reuse"*), and `RM_MapComponent_LivingRegrowth` was deliberately written content-blind — it names no
  bole, no biome and no Greentide. ⛔ Do not specialise it while fixing the art.
- ⚠️ **`RM_GenStep_RootCauseways` (order 228) reads `BoleCenters`** and runs after the bole genstep.
  Anything that changes when or whether a bole registers can silently empty the causeways.
- 🔑 **This is the second time the greatbole's *appearance* has misled a design pass in one session** —
  once into believing the landmark had no art, once into believing it had drill art. The def split
  (bookkeeping marker with a big `drawSize` + separate mineable blob) is what makes it easy to read
  wrong. Say which def you mean, every time.
