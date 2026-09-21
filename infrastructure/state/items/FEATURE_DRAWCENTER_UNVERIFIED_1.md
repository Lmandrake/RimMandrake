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
