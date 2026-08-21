## spec
`RimMandrake - Star Wars Races` ships **69** xenotypes. They break down as:
  **63** the generator can rebuild from the donors' XML on disk, and
  **6** that exist NOWHERE except in our own output — `Anzati`, `Muun`,
  `Ortolan`, `SithZ`, `Togorian`, `Herglic`. A search of all three donor trees
  returns no XenotypeDef for any of them. (`OuterRim_Herglic` exists but is a
  **HeadTypeDef**, not a xenotype — the equivalencies table points the Herglic
  row at the wrong def type, which is what produced the "source carries no
  genes" message that has gone unexplained since 2026-08-15.)
⇒ 🔴 **ANY REGENERATE DELETES THOSE SIX, PERMANENTLY.** They cannot be
recovered from a donor, from a re-dump with the donors switched on, or from the
equivalencies table. `_guard_species_regression` is what has been standing
between us and that loss, and it was right every time it fired.
🔑 TWO GENERATOR DEFECTS WERE FIXED WHILE MEASURING THIS, both committed:
(1) **The owner's 2026-08-15 "never drop a species for a gene" ruling was never
    implemented.** `pick_species` still `continue`d on an unresolvable gene,
    costing six species to four genes. It now strips the gene and builds the
    species, and prints what it stripped. 57 -> 63.
(2) **`species_table` read the roster from the DUMP only**, so a dump captured
    with the donors off silently shortened the roster. It now falls back to the
    donors' XML on disk, the same fallback `_gene_exists` has.
NEITHER FIX RECOVERS THE SIX. They are a different problem.
THE CHOICES:
(a) **Move the six into a hand-maintained sibling file the generator never
    writes** — honest, permanent, and it makes the guard's count meaningful
    again. ⚠️ Each depends on 1-3 genes from `SW_Genes.xml`, which the generator
    DOES write (e.g. `RimMandrake_HerglicHead` is Herglic-only), so those genes
    must be carried across too or the six dangle.
(b) Teach the generator to carry forward any xenotype it cannot rebuild. Implicit
    magic; the next reader will not know why the file has more defs than the log
    says were built.
(c) Accept losing them at the next regenerate. ⛔ Not recommended, and it should
    be a spoken decision rather than a side effect.
⏱️ Not urgent: nothing needs a regenerate today. D-CHK2's magenta heads were
fixed in the output instead, and that edit converges with the generator.

## verify
n/a — a ruling.

## criteria
n/a

## notes
**from:** BUILD, 2026-08-19. This is the answer to the question DECIDE asked and nobody had
run: **"Establish what the mod actually ships before treating any count as a
target."** Measured at HEAD, by calling the analysis functions only, never `main`.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ RULED 2026-08-20 — **THOSE SIX ARE SOURCE, NOT OUTPUT. Treat them as such.**
Excellent measurement, and it answers the question DECIDE asked on 2026-08-15 and
never got run: *"establish what the mod actually ships before treating any count
as a target."* 69 shipped · 63 rebuildable from donor XML · **6 that exist nowhere
but in our own output** — `Anzati`, `Muun`, `Ortolan`, `SithZ`, `Togorian`,
`Herglic`.
🔴 **THE RULING: a generated file that holds content the generator cannot rebuild
is no longer a generated file. It is source, and it must be protected from its own
generator.** `_guard_species_regression` already refuses a shrink — that guard was
right twice today's earlier rulings leaned on it — and this extends the same
principle from a COUNT to NAMED entries: ⛔ **a regenerate must refuse to drop any
of those six by name**, not merely refuse a smaller total.
🔑 **A count is not a roster.** A guard that only checks the number would pass a
run that swapped six irreplaceable species for six rebuildable ones.
⭐ **And the equivalencies-table defect is the more valuable half of this find:**
the Herglic row points at `OuterRim_Herglic`, which is a **`HeadTypeDef`, not a
XenotypeDef.** That single wrong def type produced the phantom *"source carries no
genes"* that DECIDE recorded as an unmeasured mystery on 2026-08-15 and left
standing. ⇒ **Correct the table; the mystery dissolves.**
⚠️ Five of the six (`Anzati` `Muun` `SithZ` `Togorian` `Herglic`) are owner-ruled
**v2 deferrals** and `Ortolan` is **v1 done and confirmed** — so this is about not
LOSING them, not about shipping them. Losing them would silently un-do an owner
ruling in both directions.
