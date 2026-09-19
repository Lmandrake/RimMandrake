## spec

The approved Pyrelands render wave (`9e7e773a0`, 2026-09-17) replaced Orray's
three facings and took `art_checks.py`'s `facing_height_consistency` from
unflagged to **2.488**, the second-worst row in the Pyrelands corpus — which
also broke the selftest, since Orray was pinned in `HEIGHT_MUST_PASS` as a
known-good control for the 1.35 threshold.

The instrument said the silhouettes disagree on height; it could not say which
facing was wrong. That was the owner's call and he made it.

## ruling

Owner, 2026-09-18, having looked at a contact sheet of the current art beside
the pre-wave art himself, verbatim:

> "New Orray art is vastly better than old. North and east are good. South
> needs regen it is 'fat' somehow. Older art is horrible. Discard."

So: the armoured-crocodilian design stands, north and east ship untouched, the
pre-wave feathered long-neck art is discarded permanently, and only the south
facing was regenerated.

## what shipped

`src/RimStarWars/OrrayArtOverride/Textures/swanimals/Orray/Orray_south.png`,
regenerated 2026-09-18 on the gemini channel (`gemini-3-pro-image`) with the
approved `Orray_east` and `Orray_north` passed as reference images, so the new
facing is the same individual animal. The codex channel was unavailable at the
time — `usage_limit_exceeded` — which is why the job filed as
`orray_v3_south` sits in `infrastructure/artpipe/failed/`.

The defect was mass, not height: the old south drew a barrel-chested,
hippo-wide torso whose head-on silhouette measured **421x510** against a side
profile showing a slim low reptile. The new south measures **210x486 at
(151,13)** — within 31 px of the approved north's **179x489 at (167,13)**, so
the three facings now agree on how heavy the animal is and where it sits on
the canvas. It is also composed to the same recession as north (near end of
the body toward the bottom of the frame, far end toward the top) rather than
the old south's front-elevation framing.

Before/after, labelled, all four facings at craft size and true 96 px sprite
size: `Transient/orray_south_regen_2026-09-19.png` (shelf life ~14 days).

## verify

- `art_checks.py --selftest` passes (84 files, 17 directories).
- `facing_height_consistency` on Orray reads **2.385**, still over the 1.35
  threshold — and correctly so: the residual ratio is north (a near-full-length
  rear view, 489 px) against east (a low side profile, 205 px), i.e. camera-angle
  variety in the two facings the owner approved by eye. Orray therefore moved
  from `HEIGHT_REGRESSION` (now empty) to `HEIGHT_MUST_FLAG` in
  `src/RimMandrake/Utils/art_checks.py`, with his words recorded there.
  ⛔ `FACING_HEIGHT_MAX_RATIO` was not touched, and must not be: it is calibrated
  against seven confirmed breaks.
- Deployed to the live Mods folder (`deploy_custom_mods.py --apply`, VERIFIED in
  sync). Art presence in game is unproven until the next load; the observable is
  an Orray walking south that reads as slim as its side profile, not as a hippo.
