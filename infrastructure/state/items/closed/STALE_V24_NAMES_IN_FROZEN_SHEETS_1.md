# STALE_V24_NAMES_IN_FROZEN_SHEETS_1 — an owner-approved rename that reached one sheet out of six

## what is wrong

The **V24 name consolidation** (2026-09-08, owner-approved) renamed three places:

| old | new |
|---|---|
| Venom Wood | **Fuelmere** |
| South Crags | **Sootreach** |
| Thornend | **Frostvein** |

It was amended correctly into `design/Jawa/worldbuilding/biomes/the_propane_lakes.md`
and **never propagated anywhere else**. Five other biome sheets still use the OLD names
as if they were current:

- `design/Jawa/worldbuilding/biomes/README_BIOME_GRAMMAR.md`
- `design/Jawa/worldbuilding/biomes/wasteland.md`
- `design/Jawa/worldbuilding/biomes/nightside_ice.md`
- `design/Jawa/worldbuilding/biomes/the_rot.md`
- `design/Jawa/worldbuilding/biomes/the_blue_desert.md`
- `design/Jawa/worldbuilding/biomes/_openers_prep.md`

Found 2026-09-20 during `STALE_VIVIFIED_WORLDMAP_CITED_1`'s citation sweep, which
correctly left it alone as out of its scope.

## why it is a separate defect, not part of the CSV sweep

🔑 All six sheets were **frozen 2026-09-07 — the day before the rename.** So they were
not wrong when written; the names changed under them afterwards. That makes this a
*propagation* failure, not a citation failure, and it is why the CSV sweep did not
catch it: those sheets cite the canonical worldmap correctly.

## why it matters

A name the owner ruled on twelve days ago is still being read as current by every agent
who opens one of these sheets. This is the same failure mode as the `FlowWorks`/
`fluidcanals` rename, which kept shipping under the dead name for 16 days after its gate
closed — a ruling that is not propagated has not been made.

## the trap this sits on

🔴 **These sheets are FROZEN.** Editing a frozen artifact needs care:

- A frozen sheet's freeze stamp records a human's decisions; a generator that rewrites it
  wholesale will delete what it does not recognise.
- But ⛔ **never leave false text standing to protect a freeze.** Project doctrine (owner,
  2026-09-17, on the north-star hash): *"you just re-validate when prose is corrected."*
  The remedy for false text in a protected artifact is **correct it, then re-freeze /
  re-validate in the same sitting** — never annotate around it, and never defer.
- Inaccurate material is **DELETED, not superseded in place**. The entry states what IS.

## spec

Replace the three old names with the ruled names in all six files, in the same change,
and re-freeze each sheet in the same sitting. Check for inbound references elsewhere
(`design/`, `infrastructure/`, `src/`) in the same pass — a rename that reaches five of
six files is exactly the defect being fixed.

⚠️ Check first whether any of the three names is also a **defName or label** in `src/`.
A doc rename and a def rename are different jobs; this item is the doc half unless the
check says otherwise.

## verify

`grep -rn "Venom Wood\|South Crags\|Thornend" design/ infrastructure/ src/` returns only
historical/provenance contexts (closed items, dated evidence files), and every live sheet
reads Fuelmere / Sootreach / Frostvein.

## criteria

No live document presents a superseded V24 name as current, and each corrected sheet is
re-frozen rather than left with a broken stamp.

## done 2026-09-21 — `c279720b5`

Five sheets corrected (`README_BIOME_GRAMMAR.md`, `wasteland.md`, `nightside_ice.md`,
`the_blue_desert.md`, `_openers_prep.md`). `the_rot.md` needed nothing — it already read
*"Sootreach … (the V24 consolidation's name for South Crags)"*, which is the current name
with a correct historical note.

**Freeze:** the `FROZEN — BIOME_FREEZE_FABLE_REVIEW_1` banner on three of them is **prose
citing a closed item, not a content hash** — no hash or manifest mechanism exists for
these sheets (unlike the north-star system, which does hash). A pure name correction with
no count or structural change sits inside the banner's own stated exception
(*"amendments add detail; they never change a ruling"*), so no re-stamp and no owner
re-validation is owed.

**Checked and correctly left alone:** no XML `defName` or `<label>` carries any of the
three names.

## 🔴 residual — two tools still write the OLD names onto the planet

MEASURED during the fix and deliberately not changed by the doc pass:

- `src/RimMandrake/Utils/ashkarr_paint.py:362` — `"The South Crags"`
- `src/RimMandrake/Utils/ashkarr_settle.py:96` — `"The Venom Wood"`

These are **region-name string literals in world-painting and settlement tooling**, not
doc prose. ⚠️ That makes them worse than a stale doc, not better: **re-running either tool
would write a name the owner overruled back onto the planet**, silently undoing the V24
consolidation at the source. They are exactly the shape of the FlowWorks/`fluidcanals`
failure — a ruling that lives in docs while the generator still emits the old value.

⇒ Owed: change both literals to `Sootreach` and `Fuelmere`, and check what else in those
two scripts names a region. ⛔ Do not run either tool before that is fixed.

## residual — the canonical worldmap doc

`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` still carries old names. It is the
canonical worldmap document, and a worldmap-doc pass is done **with the owner**, never
solo. Left for him.
