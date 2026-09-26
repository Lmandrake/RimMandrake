# FEATURE_DRAWCENTER_UNVERIFIED_1 — 69 of 71 label positions have never been checked

## what is wrong

Each world feature carries a `drawCenter` saying where its label is drawn. MEASURED
2026-09-21 while sizing the labels: **only `Fall Line` and `The Breaks` have a verified
`drawCenter`.** The other 69 have never been checked against the region they name.

🔴 **A wrong `drawCenter` gets WORSE as the label grows.** The planet-wide size pass
(`WORLD_LABEL_SIZE_HIERARCHY_1`, ruled by the owner 2026-09-21) raises effective draw sizes
from a uniform 15 to a range of 15–104. A misplaced label that was unnoticeable at the
floor becomes a large caption sitting over the wrong ground.

⚠️ **8 of the 71 regions exist in multiple disconnected pieces** — `Salt` is in **seven**.
Each gets ONE label, at the centroid of all its pieces, which for a scattered region can
land somewhere that belongs to none of them. That is a design question, not just a
coordinate fix.

## spec

1. For each of the 71, check the `drawCenter` against the region's actual tiles.
2. Fix the ones that are wrong. The tile→feature mapping is `tileFeatureDeflate` keyed by
   feature **`uniqueID`** — 🔴 not the list index, which was a live defect until
   `1a96f1e2a` (`WORLDVIEW_MISLABEL_FALLOUT_1`).
3. Decide what a multi-piece region should do: centroid of all pieces, centroid of the
   largest piece, or one label per piece. **The owner picks** — it is a looking decision.
4. Re-render and LOOK before writing anything to a save.

## Watch out

- 🔴 **Write no savegame without his word**, and never the canonical save — a new slot, per
  the Fall Line precedent, which left `CANONICAL_ASHKARR_START_2026-09-12.rws`
  byte-unchanged. A `.rws` edit must use binary mode; check the size delta.
- ⚠️ Sequence this **with or after** the size pass, not before — the sizes are what make a
  bad position visible, and fixing positions at the old uniform size proves nothing.
- ⛔ Do not cite a tile count as evidence that a biome is or is not built. Tile counts are
  the right instrument HERE (they are geometry, not build state) but not for that question.

## criteria

Every feature's label sits over the region it names, at the sizes the hierarchy pass
assigns, confirmed by looking at a render — and the multi-piece rule is the owner's.

## DONE OFFLINE 2026-09-26 (FOUNDRY) — 52 wrong single-piece drawCenters fixed to a new
slot, 8 multi-piece regions rendered with 3 candidates each, waiting on his look

**Re-measured fresh, live from the canonical `.rws`**: still 71 `WorldFeature`s, tile
membership decoded the same `uniqueID`-keyed way `world_label_curve.py` already proved
correct (`tileFeatureDeflate`, one uint16 per tile, 21,872 total). New tool:
`src/RimMandrake/Utils/feature_drawcenter_audit.py` — reads it, only ever, never edits
the canonical save.

**The coordinate transform between the raw engine `Vector3` `drawCenter` and this
codebase's own `worldgeom.py` tile-vector convention had to be MEASURED, not
assumed**: the two disagree on the sign of z (radius confirmed 100 on both). Verified
against the two features an earlier pass already hand-checked (Fall Line, The Breaks)
before trusting it on the other 69.

🔴 **The first version of the "is this wrong" test was itself wrong, and would have
mis-fixed Fall Line** — a hand-verified-correct feature. Testing "is the single
globally-nearest-of-21,872 tile a member of this feature" flagged 60 of 63
single-piece features, because at any shared border several different features' tiles
sit within a fraction of a degree of each other. The right test is distance to the
NEAREST TILE THAT ACTUALLY BELONGS TO THE FEATURE: a clean, unambiguous cluster of 9
features sits at 0.30–4.08 deg, Fall Line (prior verification) lands at 2.43 deg
matching that cluster, and nothing else appears until 6.32 deg. `FOOTPRINT_TOL_DEG =
5.0` sits in that gap. A self-check baked into the tool refuses to run at all if either
Fall Line or The Breaks would fail this test (`_selfcheck_transform`).

**Result, re-run after fixing the test**: of 63 single-piece features, **52 are
genuinely WRONG** — sitting tens to (worst case) 154 degrees from their own region's
nearest tile, i.e. drawn on a completely different named region's ground. Confirmed
directly for the worst case, not just by the numbers: "Salt Gate"'s stored
`drawCenter` resolves to a tile whose owner is "Deadstone", 106 degrees away. 11 of 63
are fine as stored (including Fall Line, unmoved). The other **8 are the known
multi-piece regions** (Salt in 7 pieces, Dew Belt in 4, Scorch/Twilight Crags in 3,
Sunreach/Pyrelands/The Breaks/Anvil in 2) and were left untouched — that decision is
his per the item's own text.

**Applied OFFLINE to a NEW slot, canonical untouched, verified by SHA-256 not just
size**: `CANONICAL_ASHKARR_START_2026-09-12.rws` sha256 `98b8ef82…` unchanged (matches
the hash recorded when `WORLD_LABEL_SIZE_HIERARCHY_1` closed). The fix was applied on
top of THAT item's own new slot (`ASHKARR_LABELSIZES_2026-09-26.rws`) rather than a
fresh copy of canonical — checked first that the two are identical apart from
`maxDrawSizeInTiles` (all 71 `drawCenter` values byte-identical between them before
this fix), so the result previews BOTH pending passes together, which is what actually
answers "does a wrong position get worse at the new size":
`ASHKARR_LABELSIZES_DRAWCENTERFIX_2026-09-26.rws` (in the live Saves folder),
17,500,411 bytes, 52 `<drawCenter>` tags changed by exact byte offset in document
order (same technique as `world_label_curve.py`), verified by reparsing the output and
confirming every intended fix landed. If the size pass is rejected independently, the
71-region drawCenter fix must be re-applied to a plain copy of canonical instead — it
does not depend on the sizes being kept, only on being built on a file with unchanged
tile/feature data, which was checked.

**The review pictures**, all offline, written to
`Transient/world_drawcenter_audit/`:
- `drawcenter_overview.png` — whole planet, every feature's CURRENT stored
  drawCenter (not a recomputed centroid — `worldview.py`'s own render always shows a
  freshly-computed position and would have hidden this defect entirely, which is why
  the size-pass's earlier render never surfaced it). Green = already correct, red with
  a line to a green star = wrong and where it moves to, yellow diamond = multi-piece
  (see per-region panel).
- `drawcenter_multipiece_<Name>.png` × 8 — one per multi-piece region, showing every
  piece's own centroid plus all three candidates (star = centroid of all pieces,
  triangle = centroid of largest piece, X = current stored position) for the owner to
  pick by looking, per the item's own instruction not to decide this here.
- `Transient/world_drawcenter_audit/audit.json` — the full per-feature numeric audit,
  for anyone who wants the raw numbers instead of the picture.

**What is still owed, and is his**: which of the three placements to use for each of
the 8 multi-piece regions (or a per-piece split, which is a bigger structural change
this pass only illustrates, not implements), and whether to commit the 52 single-piece
fixes (and the size pass they're layered on) to the canonical save at all.
`rimflow needs FEATURE_DRAWCENTER_UNVERIFIED_1 --to owner` set accordingly; item left
in `doing`, not closed.
