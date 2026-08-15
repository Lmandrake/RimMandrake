# How a species gets its face

Read this when a species renders wrong, renders as a plain human, or an art
audit says it has nothing. All measured on the 587-mod 1.6 stack unless marked
*inferred*.

## Start by asking which of the four mechanisms is supposed to be doing the work

A GeneDef reaches the pawn's picture four ways, and a search for one finds
nothing when the answer is another:

1. `renderNodeProperties` — the gene draws its own textures on the pawn.
2. `forcedHeadTypes` — the gene forces `HeadTypeDef`s; the sprite is on those.
3. `skinColorOverride` / `hairColorOverride` — colour only, no texture at all.
4. `bodyType` → `BodyTypeDef`, `fur` → `FurDef` — silhouette and pelt.

**Walk all four across the whole gene list before reporting anything absent.**
Measured: `BTD_Lasat` has 24 genes of which 13 carry pawn art; `Hutt` 34/17;
`Gamorrean` 28/7. A species whose art is entirely in mechanism 2 has *zero*
`renderNodeProperties` anywhere and still renders perfectly.

## Render nodes

The pawn is a **stack of layers sorted by `drawData.defaultData.layer`.** Two
nodes with the same layer have undefined order relative to each other
(*inferred* — we never needed to rely on it). Real numbers from this repo: head
attachments at 51, glowing eyes at 55.

A full node, from `RimMandrake_Jawa_Eyes_HugeOrange` in
`D:\Luke\dev\Rimworld\src\Jawa\RimMandrake_StarWarsRaces\Defs\GeneDefs\Jawa_EyeColours.xml`:

```xml
<li Class="PawnRenderNodeProperties_Eye">
  <texPath>RimMandrakeSW/Jawa/jawaeyes_glow</texPath>
  <shaderTypeDef>MoteGlow</shaderTypeDef>
  <color>(255, 130, 20)</color>
  <anchorTag>RightEye</anchorTag>
  <rotDrawMode>Fresh, Rotting</rotDrawMode>
  <parentTagDef>Head</parentTagDef>
  <drawSize>0.16</drawSize>
  <side>Right</side>
  <drawData>
    <defaultData>
      <layer>55</layer>
      <offset>(0, 0, -0.25)</offset>
    </defaultData>
  </drawData>
</li>
```

Notes that cost time to learn:

- **`side` and `anchorTag` come in pairs.** The left node repeats the whole block
  with `side Left`, `anchorTag LeftEye`, and `flip true` in `defaultData` — plus
  `dataWest` overriding `flip` back to `false`. **Per-direction overrides are
  `dataNorth` / `dataSouth` / `dataEast` / `dataWest` alongside `defaultData`.**
- **`texPaths` (plural) is the variant list.** RimWorld picks one per pawn using
  the pawn's `texSeed`. This is why two members of one species differ, and why an
  art audit that reads only the first entry under-counts.
- **`colorType Skin` with `useSkinShader`** makes the node take the pawn's skin
  gene colour, so one grey texture serves every skin tone. A node that looks
  wrongly-coloured in game is usually this, not the PNG.
- **`skipFlag Hair`** hides the node when hair draws over it. A head attachment
  that "vanished" on some pawns and not others is a skipFlag plus a hair gene.
- **`rotDrawMode` `Fresh, Rotting`** keeps the node on the corpse. Omit it and
  the species partially reverts to human on death.

### 🔴 Facial Animation deletes the vanilla head draw

Measured 2026-08-10: Facial Animation paints its own face and removes the vanilla
head render, so **a gene can only draw its own eyes on a pawn FA is not
drawing.** The LFS eyes mod demonstrates the consequence — its FA compat patch
*strips `renderNodeProperties` off every one of its own eye genes.*

⇒ **If a species relies on eye or face render nodes, exclude it from Facial
Animation.** Our Jawa are excluded, which is the only reason the glow eyes work.

⚠️ **Do not edit a non-human pawn's HEAD in Character Editor.** Confirmed
2026-08-10: it destroys the head on Mon Calamari and Bith. Eye and gene edits are
safe; the head selector is not.

## Head types

`forcedHeadTypes` names `HeadTypeDef`s, each with its own `graphicPath`. **Half
of a species' identity lives here**, which is why our 69 species needed **104
HeadTypeDefs** — more head types than species.

🔴 **60 of those 104 shipped with no `requiredGenes`.** A head type without
`requiredGenes` is in the **global random-head pool for every pawn in the game**,
so a donor mod's alien heads appear on ordinary humans. That is how the donor
mods ship them, and copying them forward carries the behaviour.

**Decide deliberately: either write `requiredGenes` on every head type you copy,
or accept a wider pool and say so.** There is no error either way.

`HeadShapeDef` is a separate def type and is not `HeadTypeDef`. Do not
cross-reference them.

`TabulaRasa.DefModExt_HeadTypeStuff` appears as a modExtension on 36 head-type
defs in this stack — a head type can therefore carry a hard C# dependency. See
`references/closure.md`.

## Textures

Texture resolution, bundles, `resources.assets`, blank PNGs and the
substring-matching traps are all the `reading-rimworld-graphics` skill's
territory. Two points that belong here:

- **A missing texture is not a missing gene.** A node with an unresolvable
  `texPath` still exists on the def; the pawn just draws nothing there.
- **713 textures travelled with our 69 species.** If a rescued species renders as
  a magenta or blank patch, count the copied PNGs before suspecting the defs.

## The diagnostic order for "this species looks wrong"

1. **Spawn one and look** (`jawa/spawn_pawn` with a `xenotype` argument). Cheapest
   and most conclusive.
2. Does the xenotype exist at runtime at all? A dedup mod may have deleted it —
   SKILL.md §6.
3. Walk the gene list for all four mechanisms above.
4. Check head types resolve, and whether `requiredGenes` gates them.
5. Only then go to the filesystem for textures.
