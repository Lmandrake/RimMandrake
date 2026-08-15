# Copying species out of a donor mod

Read this before extracting xenotypes into a standalone mod, or before merging
two species mods. Measured while rescuing 69 Star Wars species into
`D:\Luke\dev\Rimworld\src\Jawa\RimMandrake_StarWarsRaces`; the builder is
`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\gen_races_mod.py`.

## What actually travelled

69 xenotypes pulled:

| kind | count |
|---|---|
| GeneDefs | 113 |
| HeadTypeDefs | 104 |
| RulePackDefs | 48 |
| word-list `.txt` files | 140 |
| textures | 713 |

plus hediffs, recipes, abilities, damage defs, effecters, flecks, thoughts,
tattoos, hair defs, style categories, gene categories, furs and body types.
**Three mask hediffs alone pulled 3 ThingDefs and 6 RecipeDefs.**

⇒ **Budget for a transitive walk, not a file copy.** Every def type above can
name another def type, and each unresolved name is a *silent* discard, not an
error.

## Walk the closure, do not guess it

Start from the XenotypeDef and follow, repeatedly, until nothing new appears:

```
XenotypeDef.genes            -> GeneDef
XenotypeDef.nameMaker(Female)-> RulePackDef
GeneDef.forcedHeadTypes      -> HeadTypeDef        -> graphicPath (textures)
GeneDef.bodyType / .fur      -> BodyTypeDef / FurDef
GeneDef.renderNodeProperties -> texPath / texPaths (textures)
GeneDef.hediffGiver / abilities / damageDefs / thoughts / tattoos / hair
GeneDef.displayCategory      -> GeneCategoryDef
RulePackDef.Rule_File        -> Languages/<lang>/Strings/*.txt
RulePackDef.include          -> more RulePackDefs (chase these)
ThingDef (from a hediff)     -> RecipeDef, style categories
```

**Anything reached by `ParentName` travels too.** See the abstract-parent rule
below.

## 🔴 The def is not the content — RulePackDefs

A `RulePackDef` is a pointer at plain text. `Rule_File` entries name files under
`Languages/<lang>/Strings/`. **Copy the def alone and the namer resolves cleanly
and generates nothing** — no error, no red text, just pawns with empty or
fallback names. 48 packs needed 140 `.txt` files here.

**Copy the whole `Strings/` subtree the packs point at, and follow `include`**,
which chains into further packs and further files.

## 🔴 C# hides in `geneClass` and `modExtensions`

A gene that looks like pure XML can be a class in someone else's assembly.
**Grep `geneClass` and `Class=` across everything you are about to copy** — and
grep `<li Class=` inside `modExtensions` too, which is the half people miss.

Measured dependencies in this stack:

| symbol | lives in | reach |
|---|---|---|
| `VEF.Genes.GeneGendered` | Vanilla Expanded Framework | 6 genes / 7 species |
| `OuterRimDiversity.Gene_NoEyes` | Outer Rim Diversity | 1 species (Miraluka) |
| `IntegratedGenes.*` | Integrated Genes | several |
| `OutlandGenes.Gene_Empathic` | Outland Genes | one gene |
| `EyeOffsetSouth.ModExtension_EyeOffsetSouth` | 🔴 an assembly shipped **inside another mod** | modExtension |
| `BigAndSmall.PawnExtension` | Big and Small | modExtension |
| `BetterPrerequisites.GeneExtension` | Better Prerequisites | modExtension |
| `TabulaRasa.DefModExt_HeadTypeStuff` | Tabula Rasa | 36 defs |

⇒ **Each of these is either a hard dependency in `About.xml` or a def you must
rewrite in pure XML.** A missing class is a load error on that def and the def is
gone; the species then generates without whatever the gene did.

⚠️ `EyeOffsetSouth` is the instructive one: the namespace does not match any mod
folder name, so a dependency list built from namespaces alone misses it. Find the
owner by `strings -a -el` on the assemblies, not by guessing.

## 🔴 `Name=` is a second global namespace

Abstract parents are addressed by `Name=`, which is global and separate from
`defName`. **An abstract parent must travel with its children AND be renamed with
them** — if `ParentName` resolves to nothing, the child is a **silent discard**.
You get a mod that loads clean and is missing defs.

## 🔴 defNames collide ACROSS def types

`OuterRim_Wookiee` is **both** a XenotypeDef and a PawnKindDef in this stack.
An index keyed on defName alone silently keeps whichever was walked last, so one
of them vanishes from your extraction and you never see it happen.

**Key every index, map and rename table on `(defType, defName)`.**

⇒ **A prefix migration is never a string replace.** A blind
`s/OuterRim_/RimMandrake_/` over the tree also rewrites texture paths, `Name=`
attributes, unrelated mods' cross-references and comment text. Rename by parsing
defs, per type, and rewrite references only where the pointed-at def is one you
actually copied.

## Do not forget PawnKindDefs

A rescued XenotypeDef with no PawnKindDef cannot be spawned or tested at all
(SKILL.md §4). We authored 70. **Generate them in the same pass as the
xenotypes** so the set is testable the moment it exists.

## The dedup-mod hazard

If the donor stack contains a deduplicating mod such as
`[BTD] Xenotype REMIX: Star Wars`, the defs *you can see on disk* are not the
defs the game had (SKILL.md §6). Decide which of the three equivalent species
defs you are actually rescuing, and remove the dedup mod together with the mods
it was deduplicating — removing it alone resurrects the collisions.

## Proving the result

Loading the new mod alongside its donors proves nothing: every reference you
forgot resolves against the donor. **The only proof is a load with the donor mods
switched off** — see `references/verifying.md`.
