---
name: rimworld-xenotypes
description: Authoring, moving, spawning and debugging RimWorld xenotypes and the genes that give them a face. A XenotypeDef is a list of gene names and nothing else — appearance lives in GeneDef renderNodeProperties, forcedHeadTypes and HeadTypeDefs; a xenotype cannot be spawned at all without a PawnKindDef; xenotypeChances is dictionary-keyed and an `<li>` there discards the whole FactionDef silently; xenotypeSet inherits and appends so a Star Wars faction fields vanilla Hussars unless Inherit="False"; and a def can ship in an active mod and still not exist in the running process because a dedup mod deleted it at load. Use when writing or reviewing a XenotypeDef, GeneDef, HeadTypeDef or species mod, when a species has "no art", when a faction stops generating or generates the wrong pawns, when copying species between mods, when a .xtp needs promoting to a def, or before concluding any xenotype is missing or broken.
---

# Xenotypes — the def is a gene list; everything else is somewhere else

Almost every expensive mistake here is the same mistake: **reading the
XenotypeDef and expecting to find the species in it.** The def is a pointer. The
species is spread across GeneDefs, HeadTypeDefs, RulePackDefs, text files,
textures and sometimes a C# assembly, and each of those fails silently on its
own.

Measured on this project's 587-mod 1.6 stack, rescuing 69 Star Wars species into
`D:\Luke\dev\Rimworld\src\Jawa\RimMandrake_StarWarsRaces`. Everything below was
observed there unless marked *inferred*.

| I want to… | Start at | Reference |
|---|---|---|
| **write** a xenotype and see one in game | §1, §4 | — |
| find out **why a species looks wrong or "has no art"** | §2, §3 | `references/appearance.md` |
| get a species **into a faction's pawns** | §5 | — |
| work out **why a def is missing at runtime** | §6 | `references/verifying.md` |
| **copy species out of a donor mod** | §10 | `references/closure.md` |
| **prove** any of it actually worked | §9 | `references/verifying.md` |

---

## 1. The whole surface of a XenotypeDef

Our 69 species defs use these fields and no others:

```xml
<XenotypeDef>
  <defName>RimMandrakeAbednedo</defName>
  <label>Abednedo</label>
  <description>...</description>
  <iconPath>RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Abednedo</iconPath>
  <inheritable>true</inheritable>
  <canGenerateAsCombatant>true</canGenerateAsCombatant>
  <factionlessGenerationWeight>0</factionlessGenerationWeight>
  <genes>
    <li>Hair_BaldOnly</li>
    <li>RimMandrake_AbednedoHead</li>
    <li>Skin_Orange</li>
  </genes>
</XenotypeDef>
```

**Genes own everything that matters** — appearance, stats, hediffs, abilities,
needs. Judge a xenotype by walking its `genes` list, never by reading the def.

⭐ **A gene list can still randomise per pawn.** `GeneEyeColor` is an abstract
parent carrying `exclusionTags: EyeColor`, so listing four of its children on one
xenotype makes the engine pick one per pawn. `guy762_xenotype_hutt` ships four
big-eye colours this way. So "the gene list is fixed" does not mean "every pawn
of this species looks identical".

---

## 2. 🔴 An icon is not the appearance

`iconPath` is a UI symbol for the xenotype panel. **A xenotype with no icon at
all renders perfectly**, because none of its appearance was ever in the icon.

Reporting "no art" from an icon audit invites someone to delete working content.
Measured gene counts against genes actually carrying pawn art:

| xenotype | genes | genes carrying pawn art |
|---|---|---|
| `BTD_Lasat` | 24 | 13 |
| `Hutt` | 34 | 17 |
| `Gamorrean` | 28 | 7 |

**Say out loud which question you are answering** — *does this have a UI icon* or
*does this render* — before auditing. A live spawn settled this after file
analysis reached the wrong conclusion twice; see §9.

---

## 3. Four different ways a gene supplies appearance

Guess the wrong one and you find nothing, which reads as "the species has no
art". Check all four before concluding anything is missing.

| mechanism | field on the GeneDef | gives you |
|---|---|---|
| **render nodes** | `renderNodeProperties` | textures drawn on the pawn |
| **head types** | `forcedHeadTypes` → `HeadTypeDef.graphicPath` | the whole head sprite |
| **colour only** | `skinColorOverride` · `hairColorOverride` | tint, no texture |
| **body/fur** | `bodyType` → `BodyTypeDef` · `fur` → `FurDef` | silhouette and pelt |

**Half the species identity lives in head types, not in the genes.** Our 69
species needed **104 HeadTypeDefs**. `HeadShapeDef` also exists and is a
different def type from `HeadTypeDef` — do not conflate them.

**The pawn is a stack of layers.** Each render node carries
`drawData.defaultData.layer`, and paint order is that number. A real node from
`RimMandrake_Jawa_Eyes_HugeOrange`:

```xml
<li Class="PawnRenderNodeProperties_Eye">
  <texPath>RimMandrakeSW/Jawa/jawaeyes_glow</texPath>
  <parentTagDef>Head</parentTagDef>
  <anchorTag>RightEye</anchorTag>
  <rotDrawMode>Fresh, Rotting</rotDrawMode>
  <drawData><defaultData><layer>55</layer></defaultData></drawData>
</li>
```

The fields that carry the meaning, from real nodes in this stack:

| field | what it does |
|---|---|
| `nodeClass` / `Class=` | e.g. `PawnRenderNode_AttachmentHead`, `PawnRenderNodeProperties_Eye` |
| `parentTagDef` | what it anchors to — `Head`, `Body` |
| `texPath` | one texture |
| `texPaths` | 🔴 a **LIST of variants**, picked per pawn by `texSeed` — two pawns of one species differ |
| `drawData.defaultData.layer` | paint order in the stack (`guy762_FacialRidges_bumpy` = 51, our glow eyes = 55) |
| `colorType` + `useSkinShader` | `Skin` tints the node to the pawn's own skin gene |
| `skipFlag` | `Hair` hides it when hair is drawn over it |
| `rotDrawMode` | `Fresh, Rotting` keeps it drawn on the corpse |

`guy762_FacialRidges_bumpy` is the reference example for the attachment form:
`PawnRenderNode_AttachmentHead`, `parentTagDef Head`, two `texPaths` variants,
`layer 51`, `colorType Skin` + `useSkinShader`, `skipFlag Hair`, `rotDrawMode
"Fresh, Rotting"`.

> **Which node class, which parent tag, what a layer number means, and how a
> render node interacts with Facial Animation?** → `references/appearance.md`

⚠️ **60 of our 104 head types had no `requiredGenes`** — those enter the GLOBAL
random-head pool and can land on any pawn in the game. That is how donor mods
ship them. If you copy head types, decide deliberately whether you want that.

---

## 4. 🔴 A xenotype cannot be spawned — PawnKindDef is the handle

Pawn generation takes a `PawnKindDef`. **A XenotypeDef on its own is
unverifiable in game.** To test our 70 xenotypes we had to author 70
PawnKindDefs.

**Author the PawnKindDef in the same commit as the XenotypeDef**, or the species
exists and nothing can ever produce one.

On the bridge, `jawa/spawn_pawn` takes a `xenotype` argument directly and is the
fastest way to look at one.

---

## 5. Getting a xenotype into the world

### 🔴 `xenotypeChances` is dictionary-keyed

```xml
<xenotypeChances>
  <BTD_Nikto>0.3</BTD_Nikto>
</xenotypeChances>
```

The key is the defName. **Writing `<li><xenotype>X</xenotype><chance>Y</chance></li>`
makes ParseFloat return null and DISCARDS THE ENTIRE FactionDef, silently.**
This killed five of our authored factions. The tell was pure correlation: every
file *without* an `<li>` loaded, every file *with* one did not.

**Write the keyed form and check every existing `xenotypeChances` you inherit.**
Vanilla is unanimous — every instance in the game is keyed.

⚠️ `validate_patch.py` cannot catch this; its own banner says it does not check
field names, types or shapes.

### 🔴 `xenotypeSet` inherits and APPENDS

A child's list is **appended to its parent's**, not substituted. Measured:

| parent | ships |
|---|---|
| `OutlanderFactionBase` | 5 — Hussar, Dirtmole, Genie, Neanderthal, Starjack |
| `PirateBandBase` | 9 |
| `TribeBase` | none (luck, not design) |

**Write `<xenotypeSet Inherit="False">` on any faction whose species list is
meant to be exactly what you wrote**, or your Star Wars outlanders field
Hussars. Same rule as `pawnGroupMakers`.

### 🔴 `factionlessGenerationWeight` and `canGenerateAsCombatant` do not discriminate

Unset defaults are `0` and `false`, and a runtime field read cannot tell an unset
field from a deliberate suppression. Measured: `BTD_Jawa` declares **neither**
(only 1 of BTD's 71 xenotypes declares `factionlessGenerationWeight` at all) and
reads `0.0 / False` at runtime — **identical to a xenotype that is deliberately
suppressed, and identical to `MandrakeJawa`, which must and does generate.**

**Settle "does this generate?" from the SOURCE XML — does the def declare the
field? — or by repeated generation. Never from a runtime field read.**

Note what the field actually governs: `factionlessGenerationWeight` controls
**wanderer/factionless generation only**. A faction whose `xenotypeSet` names a
xenotype still generates it at weight 0.

---

## 6. 🔴 A def can ship in an active mod and not exist in the running process

Another active mod can delete it at load. Measured:
`[BTD] Xenotype REMIX: Star Wars` ships **70 XenotypeDefs, zero genes**, and a
Harmony assembly whose only job is deduplication — `BTD_EquivalenceLoader`,
`GetAllDefsToRemove`, `CalculateDuplicatesRemoved`, and the log string:

```
- {0} defs have {1} references to removed xenotype '{2}'
```

Its `BTD_Data/XenotypeEquivalencies.xml` maps each species to its BTD, SWX and OR
equivalents, and it keeps its own. So `OuterRim_Jawa` and `guy762_xenotype_jawa`
load and are then removed; `BTD_Jawa` survives.

⇒ **A def dump captures pre-deletion state; the live process is post-deletion.**
Both readings are correct about their own moment, and no mod-list check finds
this — all three mods are active and all three files are on disk.

**The discriminating test is a runtime lookup by defName.** `set_pawn_xenotype`
returned `"No XenotypeDef named 'X'"` for the two removed names while converting
a pawn with the third in the same call.

⇒ **Remove such mods as a SET.** Removing only the dedupper resurrects every
collision it was suppressing.

---

## 7. Name makers: the def is not the content

`nameMaker` and `nameMakerFemale` on a XenotypeDef point at **RulePackDefs**,
whose `Rule_File` entries point at plain-text word lists under
`Languages/<lang>/Strings/`.

🔴 **Copy the def alone and the namer resolves cleanly and generates nothing** —
a silent empty success, no error anywhere. Our 48 RulePackDefs needed **140
`.txt` files**.

**Copy the `Strings/` tree with the RulePackDefs, and follow `include` for
chained packs**, which pull further packs and further files.

---

## 8. `.xtp` files are not defs

A xenotype saved in the game's own editor lands in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes\<name>.xtp`.
It is loaded by the pawn editor and **cannot be referenced by anything** —
`PawnKindDef.xenotypeSet` takes XenotypeDefs.

**To use one, promote it into a real def by transcribing its genes**, and keep
the two in step by hand thereafter; they drift.

🔴 **The `.xtp` carries only `name` and `inheritable`. Every other field in the
promoted def was INVENTED by whoever transcribed it.** We found
`canGenerateAsCombatant false` invented that way, which stopped a faction
generating any fighter at all. **Audit every non-gene field of a promoted def
against the `.xtp`; if the `.xtp` does not say it, you chose it — so choose it
deliberately.**

---

## 9. Verifying xenotype work

Nearly everything above fails silently, so **choose the check that can actually
see the failure you care about**:

| the question | the check that answers it |
|---|---|
| does this def exist in the *running game*? | a runtime lookup by defName — the def dump is disk, not runtime (§6) |
| does this species render? | **spawn one and look.** Beats any file analysis |
| does this faction still load? | it generates pawns at all — a discarded FactionDef is silent (§5) |
| does this xenotype generate? | repeated generation, or the source XML. Not a runtime field read (§5) |
| is this standalone set really standalone? | **a load with the donor mods switched OFF.** Nothing else proves it |

🔴 **The live def dump is disk state, not process state.** It is the right tool
for "what did the mods ship" and the wrong tool for "what exists right now".

🔴 **A spawn test beats any amount of file analysis.** One spawned pawn settled
the art question in §2 after two file-based analyses got it wrong. If the bridge
is available, spawn first and read files second. Bridge rights belong to CHECK —
ask before driving.

🔴 **A standalone mod is only proven standalone by a load with the donors
disabled.** Loading it *alongside* its donors proves nothing: every reference you
forgot to copy resolves against the donor and the mod looks complete.

> **The full protocol — what each of these actually costs, and the order to run
> them in?** → `references/verifying.md`

---

## 10. Moving species between mods

The closure is much wider than genes. Rescuing 69 species pulled:

```
113 genes · 104 head types · 48 rule packs · 140 word lists · 713 textures
plus hediffs, recipes, abilities, damage defs, effecters, flecks, thoughts,
tattoos, hair, style categories, gene categories, furs, body types
```

Three mask hediffs alone pulled 3 ThingDefs and 6 RecipeDefs.

**Two traps that decide whether the copy works at all:**

🔴 **Grep `geneClass` and `Class=` before assuming a gene is pure XML.** Measured
C# dependencies hiding in genes and modExtensions:

| symbol | from |
|---|---|
| `VEF.Genes.GeneGendered` | Vanilla Expanded Framework — 6 genes / 7 species |
| `OuterRimDiversity.Gene_NoEyes` | one species (Miraluka) |
| `IntegratedGenes.*` · `OutlandGenes.Gene_Empathic` | their own mods |
| `EyeOffsetSouth.ModExtension_EyeOffsetSouth` | an assembly shipped INSIDE another mod |
| `BigAndSmall.PawnExtension` · `BetterPrerequisites.GeneExtension` | frameworks |
| `TabulaRasa.DefModExt_HeadTypeStuff` | 36 defs |

🔴 **`Name=` is a second global namespace, and defNames collide across def
types.** Abstract parents must travel with the copied defs **and be renamed**, or
`ParentName` resolves to nothing and the child is a silent discard. And
`OuterRim_Wookiee` is **both** a XenotypeDef and a PawnKindDef — an index keyed
on defName alone silently keeps whichever was walked last.

⇒ **A prefix migration is never a string replace.** Key every index on
`(defType, defName)`.

> **The full extraction procedure, the closure walk, and the per-def-type list of
> what points at what?** → `references/closure.md`

---

## In this repo

```
src/Jawa/RimMandrake_StarWarsRaces/       69 xenotypes, 114 genes, 104 head types
src/RimMandrake/Utils/gen_races_mod.py    builds that mod from the donor stack
src/RimMandrake/Utils/refresh.py          rebuilds the offline def dump (disk state)
```

**Survey tooling that predates this skill — reach for it before writing your own.**
It is the reason a xenotype question usually needs no new script:

```
src/RimMandrake/Utils/genome_scan.py         every XenotypeDef + GeneDef in the ACTIVE list -> JSON
src/RimMandrake/Utils/genome_matrix_build.py the genome register: every candidate xenotype, aligned by gene
src/RimMandrake/Utils/genome_art_cache.py    gene and xenotype icons OUT of AssetBundles (needs ~/.venvs/rimart/bin/python)
design/Jawa/worldbuilding/review/genome_register.html   the rendered result, art inlined
```

⚠️ `genome_art_cache.py` is the answer to "the icon does not exist on disk" —
vanilla ships gene art inside Unity bundles, so a `find` sweep reports most of
Biotech's genes as art-less. It is not; you are looking in the wrong place. Full
treatment in `reading-rimworld-graphics`.

⇒ **These existed for a day before this skill did, and the knowledge in them was
invisible** — it lived in scripts and one generated HTML page, so the next person
to touch a xenotype re-derived it by hand. That is the failure this file exists
to prevent: if you learn something here, write it HERE, not only into a script.

Deploying it is `rimworld-deploy`; looking at the art is
`reading-rimworld-graphics`; spawning to check is `rimbridge`.
