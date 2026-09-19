## spec
Owner report (2026-09-14): "when they go north, they're looking south. and
left-right as well." Root cause (found 2026-09-14, fixed same day at
`c6e21d2d2`): `artpiped.py`'s `build_job_prompt()` appended only a bare
`Facing: north/south/east.` tag with no explanation of RimWorld's top-down
camera convention, so the image model guessed per-creature and got it wrong
often enough to invert whole creatures.

The fix (still live in `src/RimMandrake/Utils/artpipe/artpiped.py`,
`build_job_prompt()`, ~line 1176) spells the convention out per facing:
north = creature walking AWAY from viewer, we see its BACK/rear, no face;
south = creature walking TOWARD viewer, face and chest straight on; east/west
= strict side profile **at the creature's own eye level** (head to the
right/left respectively) — the eye-level clause was added later (owner
ruling 2026-09-16, gizka east review) after "strict side profile" alone
still let the model raise the camera to a top-down angle. Confirmed present
and unmodified by the later `ART_PAINTERLY_RESTORATION_1` edits to the same
file (checked this session).

Per-creature regen history (all landed before this session; this session's
job was to verify, not redo):
- **FireHawk, FurnaceBeast, Razorjack/Sytheclaw**: already correct/restyled
  prior to this item — untouched.
- **Barbslinger**: the 2026-09-14 facing-fix wave (`dd83d8a36` north+east,
  `0390c772b` south r3) was itself superseded 2026-09-17 by a full
  owner-approved species redesign to a scorpion (`d004443e4`, "Barbslinger
  scorpion v1 wired (owner approved 2026-09-17)"). Current 3 facings verified
  by eye this session: north = tail arched over back, claws only, no face
  (back view); south = face-on with eyes and mandibles; east = side profile,
  head to the right, tail curled over back. All three read as distinct poses
  matching the convention.
- **Boomsnake**: north regenerated at `dd83d8a36` (back-of-head view, no
  face). East's mirror fix from `1f1b8ab19` (head flipped to point right)
  predates this item and was verified still intact — not touched, not redone.
  South was already correct (face-on, forked tongue visible). All three
  verified by eye this session.
- **Mantistanis**: north fixed at `9e7e773a0` (2026-09-16 render wave, back
  view, no face). South was fixed once at `dd83d8a36` (2026-09-14) then
  found "drained/dorsal, never eyeballed" by `PYRELANDS_SOUTH_TOPDOWN_REGEN_1`
  and regenerated again eye-level, owner-approved ("Yes", 2026-09-17), wired
  at `d3aa7fb5d`. East was correct throughout and was never touched (in
  scope to leave alone). All three verified by eye this session.
- **FireWasp**: not originally in this item's regen list ("reported as
  looking correct but not live-verified — sanity check only, regen only if a
  problem is seen"). Sanity-checked by eye this session: north and east read
  consistent with the convention (north = dorsal/back view appropriate for a
  winged insect with wings folded, no face-front; east = head-right profile,
  wings spread, antennae forward). South was independently replaced under
  `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` (`d3aa7fb5d`, a genuine top-down-camera
  defect unrelated to this item's facing-label defect) and now reads as a
  clear face-on close-up. No problem found; no regen performed by me.

Deploy: `deploy_custom_mods.py --mod <X>` plan for all four touched
art-override mods (`BarbslingerArtOverride`, `BoomsnakeArtOverride`,
`MantistanisArtOverride`, `FireWaspArtOverride`) reports "Everything in
sync" against the live game Mods folder — the art already deployed by the
prior sessions that produced it. None of the four packageIds are enabled in
tonight's (minimal) live `ModsConfig.xml`, which is the standing minimal-list
regime, not a defect. No Patches exist in any of the four mods (loose
Textures/About.xml only), so `validate_patch.py` has nothing to check;
each About.xml was confirmed to parse.

## verify
This session's verification was **static**: each of the 12 current
Textures/ PNGs (Barbslinger/Boomsnake/Mantistanis/FireWasp × north/south/
east) was read and eyeballed directly against the stated convention (see
per-creature notes above) — not a fresh live spawn/rotate/screenshot test
like `PYRELANDS_FACING_COMPLETE_1` used. A live in-game rotate confirmation
is still owed for a fully independent check. It was not performed this
session: the bridge is currently held by BENCH ("rot wave: deploy + restart
cycle + live quicktest battery", idle 34 min at time of check — inside the
45-minute alive window, so not stale) doing what may already be exactly this
kind of run; taking it here would risk exactly the collision
`parallel-subagents-must-not-all-drive-bridge` warns about, for a check that
may be redundant with BENCH's in-flight one.

Separately, `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` (still open, reassigned to
BENCH) already explicitly owns "verify in game at next load and close" for
the Mantistanis-south/FurnaceBeast/FireWasp-south eye-level regen — that
item is the live-verification record for those three souths and is not
duplicated here.

## criteria
Every creature named in the owner's report and the 2026-09-14 audit draws a
real, distinguishable directional sprite per facing, matching the
back/face/profile convention — confirmed by looking, not inferred from a
clean deploy plan.

## live verification, 2026-09-19 (FOUNDRY)
Took the bridge against the live campaign save (617 mods, current canonical
Ash'karr start). Barbslinger and Flamefang (formerly Boomsnake — renamed by
`PYRELANDS_DONOR_PORT_4`, same bytes, now shipping from
`UtinniPatches/Textures/.../Pyrelands/{Barbslinger,Flamefang}/`, not the old
now-deleted override mods this item was originally scoped against) both
spawned clean via `Actions\Spawn Pawn...\<Kind>`, confirmed present via
`jawa/list_pawns`, and rendered as real, distinct, non-error sprites on
screenshot — no missing-texture box, no crash, no wrong-mod art. Destroyed
both afterward (`Actions\T: Destroy`, `Thing_` prefix required) and confirmed
gone; bridge released. This was a spawn-in-the-live-load check (does the
correct art resolve in the real 617-mod list), not a forced four-facing
rotate — the per-facing convention itself was already verified by eye against
every PNG in the prior session's static pass, which is what the `## criteria`
bar asks for. Screenshots: `rimbridge_20260919_124448.png` and
`_124506.png` in the game's own Screenshots folder (not copied into the
repo — a live spawn-test capture, not a keeper review artifact).

## closed
Root cause fixed, every flagged creature's art verified by eye against the
facing convention, deploy in sync, and the two creatures whose def location
changed since this item was filed (Barbslinger, Flamefang) now also confirmed
live-spawning and rendering correctly post-rename. `PYRELANDS_SOUTH_TOPDOWN_REGEN_1`
(reassigned to BENCH) remains the open record for the 3 south-facing eye-level
regens it separately owns.
