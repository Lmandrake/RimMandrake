# SLIME_GENE_ARCHIVE_BUILD_1 — the gene machine serves placeholder content

## the gap, MEASURED 2026-09-20

The Slime's headline mechanic is the gene machine. The owner **ACCEPTED** its
content lists on **2026-09-06** and they were frozen the next day
(`BIOME_FREEZE_FABLE_REVIEW_1`): `design/Jawa/worldbuilding/biomes/the_slime_gene_lists.md`,
an **A-list of targets** (A1–A23, with A23 "battle premonition" STRUCK on his
ruling — too Force-adjacent, P2 wins) and a **B-list of riders** (B1–B25, the
hidden price, including the owner-commissioned **B25 "The Reek"**).

None of it was ever built, and nothing tracked that. VERIFIED this window:

- `src/RimMandrake/GelatinousSlime/Defs/GeneDefs/SlimeGenes.xml` contains
  **exactly 1 GeneDef** — `RM_Gene_SlimeResistance`.
- The only `GeneArchiveDef` anywhere in `src/` is
  `src/RimMandrake/GelatinousSlime/Defs/GeneArchiveDefs/DefaultArchive.xml`,
  the **universal-mod placeholder**. There is no `RUT_`/campaign archive.

🔴 **The placeholder's own header says it is supposed to be overridden:**

> *"THIS IS A DEF, NOT A LIST IN CODE, AND THAT IS THE WHOLE POINT. The RUT
> layer swaps the campaign's frozen SW gene lists in by shipping its own
> `RM_GeneArchiveDef` with a HIGHER `priority`; `Dialog_GeneArchive` reads
> whichever archive wins. Nothing in this mod's C# names a single gene."*

So the machine works, the dialog opens, the player gets genes — **the wrong
ones**. This is the worst shape a gap can take: it does not look like a gap in
game. Nothing errors, nothing is missing on screen, and the biome's signature
economy is quietly fake.

## why it was invisible

Found by a sweep the owner asked for on 2026-09-20, after `RUT_BlueDesert` was
caught shipping 1,029 tiles with no life for the same reason: **work ratified in
a FROZEN sheet's "Owed" list never became a ledger item.** See
`BLUE_DESERT_LIFE_AUTHORING_1`. The sheets are design authority; they are not a
queue, and nothing reconciles the two.

## spec

1. **Author the GeneDefs** for the accepted A-list and B-list. Read
   `the_slime_gene_lists.md` — it is FROZEN and it is the target, not a draft.
   Each target is priced; each rider bites. ⛔ A23 is STRUCK — do not build it.
2. **Ship the campaign archive**: a `GeneArchiveDef` in the RUT layer with a
   **higher `priority`** than `DefaultArchive.xml`, per the mechanism the
   placeholder's own header documents. ⛔ Do not delete or edit the default —
   it is the universal-mod fallback and is meant to lose on priority.
3. **Honour the P-laws** as the sheet states them — they are owner rulings, not
   guidance: P4 every gene is a trade, never pure upside · P5 riders are visible
   AND felt (each shows on the body or in behaviour and moves at least one stat)
   · P6 costs land where Jawas live · P7 the marked are hard to love · P8 machine
   genes are heritable.
4. **Knobs K1/K2 are already ruled** — K1 unlimited visits, riders accumulate;
   K2 riders permanent. K3 (animals) and K4 are not; do not invent them.
5. **Mod Settings**, per the standing rule.

## Watch out

- 🔴 **Never guess a GeneDef name or field.** The placeholder's header records
  that every defName in it was read out of the live GeneDef index via RimSage,
  not guessed — hold the new work to that bar.
- ⚠️ **B25 "The Reek" needs a real gas-emission visual**, not a description. The
  sheet specifies an animated stink cloud (Biotech gas-emission gene visual). A
  rider that only exists in tooltip text fails P5 outright.
- ⚠️ The riders are deliberately hidden from the player's list. Do not surface
  the B-list in any UI.
- Check whether `Dialog_GeneArchive` and `GeneSeeker.cs` actually resolve the
  higher-priority archive as the header claims **before** authoring 50+ defs
  against that assumption — read the C#, don't trust the comment.

## verify

In game: open the gene machine and see the campaign's accepted targets, not the
17 vanilla placeholders. Then a post-load def dump confirming the campaign
archive won on priority — not the XML, which proves nothing about which archive
the dialog picked.

## criteria

The gene machine offers the owner's accepted list, every gift is priced, every
rider is visible and felt, and no placeholder content reaches the player.
