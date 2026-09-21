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
