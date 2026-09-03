# STARWARSRACES_UNDECLARED_GENE_DEPS_1 — five real dependencies are not in About.xml

Found 2026-09-03 while building a trimmed mod list for `LIVE_BIRTH_AND_HATCH_DEMO_1`.
The owner watched the symptom happen and confirmed the fix.

## spec

`src/RimStarWars/StarWarsRaces/About/About.xml` declares four `<modDependencies>`:
Biotech, VEF, `Neronix17.Outland.Genetics`, `Turnovus.Biotech.IntegratedGenes`.

Its own `<description>` says more than that: *"Genes that belong to Biotech, Core,
Outland Genetics, Integrated Genes, LFS Genes Expanded - Eyes and Big and Small remain
theirs; those mods are dependencies and must stay installed."* **Those last two are
never declared**, and `RedMattis.BetterPrerequisites` — whose `GeneExtension` the genes
also use — is not mentioned at all.

⇒ Any dependency-walking list builder (`modset_builder.py`, `ModsConfig.MINIMAL.xml`,
a human reading About.xml) produces a list that loads StarWarsRaces **without** them.

## what that costs — measured live

On a 23-mod list built exactly that way:

```
Exception loading def from file SW_Genes.xml:
  System.ArgumentException: Could not find type named BigAndSmall.PawnExtension
  System.ArgumentException: Could not find type named BetterPrerequisites.GeneExtension
Could not resolve cross-reference to GeneDef RSW_Head_hutt   (wanter=requiredGenes)
Could not resolve cross-reference to GeneDef RSW_Head_selkath (wanter=requiredGenes)
Could not resolve cross-reference to GeneDef RSW_statgene_predator (wanter=genes)
```

A missing `modExtension` type discards the **whole def**, silently
(`modextension-missing-type-discards-def`). So the head-type genes went with them.

🔴 **The symptom is a RENDERING one and does not name a gene.** The owner, watching:
*"the graphical images of the humans are blinking off and on around 0.3 Hz"* and
*"Zooming out causes all the humans to reappear. Zooming in irregularly removes them
until they are all invisible."* The cached texture atlas still had the pawns; the
zoomed-in dynamic draw path did not. Nobody would connect that to a gene XML.

**Fix, confirmed:** adding `RedMattis.BetterPrerequisites`, `RedMattis.BigSmall.Core`,
`RedMattis.BigSmall`, `RedMattis.Optional`, `LazyFridayStudio.GenesExpandedEyes` took
those log lines to **0** on the next load, and the owner confirmed: *"Correct analysis
of blinking. All gone."*

## Watch out

⚠️ **`RedMattis.Optional` and `RedMattis.BigSmall` were added together with the other
three, so the minimal sufficient set is UNMEASURED.** `BetterPrerequisites` and
`BigSmall.Core` are the two the log actually named; the other three are plausible
carry-alongs. Do not write all five into About.xml without testing which are needed —
an over-declared dependency is a mod nobody can run without.

⚠️ The full 589-mod list has all five active, so **this is invisible on the owner's
stack** and only bites trimmed/minimal lists — which is exactly where tier-b tool work
now happens, since hot-reload was retired (`HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1`).

## verify

Build a list from About.xml's declared dependencies alone, load it, and grep the log
for `Could not find type named BigAndSmall.PawnExtension` — expect present before the
fix, absent after. Then bisect the five to find the minimal set before declaring them.

## criteria

`About.xml` declares every mod StarWarsRaces genuinely needs, tested one at a time, and
`ModsConfig.MINIMAL.xml` (or whatever list carries StarWarsRaces) includes them.
