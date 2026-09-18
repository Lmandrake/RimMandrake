## spec
Owner's verbatim (2026-09-14): "Please start again to make something more
interesting than yet another horned beast. Something like a scorpion but
with a thick domed body and a bifurcated double tail." This is the ART/species
identity ask, tracked separately from the def mechanics (twin venom missiles,
pincer assault), which are their own, still-open, sibling item
`BARBSLINGER_SCORPION_REDESIGN_1`.

Delivered by a two-step pipeline, both same day (2026-09-17):
- `3a1b7072f` "Barbslinger scorpion redesign: fresh 3-facing candidate set" —
  a brand-new scorpion concept generated from fresh prompts per the owner's
  words above (domed body, two independent tails each with a javelin-like
  needle, pincers). Explicitly did NOT reuse any prior "hated" scorpion
  render or its prompts. Passed `facing_set_audit.py` at generation time
  (size spread 0.0%, anchor drift 0.0%, south judged EYELEVEL). Candidates
  held for owner review before wiring.
- `d004443e4` "Barbslinger scorpion v1 wired (owner approved 2026-09-17)" —
  the exact same candidate bytes (byte-size-identical: east 32367,
  north 40606, south 40667) wired into the live art override at
  `src/RimUtinni/BarbslingerArtOverride/Textures/Things/Pawn/Animal/AA_BarbSlinger/`
  (`AA_BarbSlinger_{north,south,east}.png`), replacing the old grazer art.
  Commit message records the mechanics split explicitly.

`AA_BarbSlinger` is a donor-mod (Alpha Animals) creature; this repo's
`BarbslingerArtOverride` mod is ART-ONLY (loose Textures + About.xml, no
Patches, no def edits) — the body-shape/health def stays whatever the donor
mod ships. So "thick domed body" and "bifurcated double tail" are visual
redesign claims about the sprite, not a BodyDef change, which matches this
item's scope (species identity via art) versus the sibling item's scope
(combat mechanics).

## verify
Read all three current PNGs directly (this session) and checked each
against the owner's three asks:
- **Thick domed body**: all three facings (north/south/east) show a rounded,
  segmented, shell-like dome — not a horned quadruped. Present.
- **Bifurcated double tail**: north (back view) shows two independent
  curved tail structures rising from the rear, each ending in a distinct
  pointed spike ("javelin-like needle") — genuinely two tails, not one tail
  drawn twice or a single forked tip. East (profile) shows one tail arched
  over the back ending in the same needle tip (the second tail is naturally
  occluded in a strict side profile — consistent, not contradictory).
  Present, matching the owner's specific "bifurcated double tail" ask (not
  just "a scorpion" in name only).
- **More interesting than another horned beast**: species class changed
  entirely from mammal grazer to armoured arthropod with pincers, a domed
  carapace and twin tails — a genuine identity change, not a retexture.

Facings/consistency: south is a front-on face with mandibles and raised
pincers, north is a rear view with tails arched and no face, east is a
strict side profile with head right, tail curled over the back — three
distinct, non-duplicate poses consistent with the game's
north=back/south=face/east=profile convention (matches the read already
recorded independently in `PYRELANDS_FACING_REGRESSION_1`'s per-creature
notes this same session).

Re-ran `facing_set_audit.py --set .../AA_BarbSlinger` this session (fresh,
not reused from the candidate commit's claim): canvas uniform 256x256 RGBA
all three, size spread 0.0%, anchor drift 0.0%, no palette-distance flag, no
byte-identical-pair flag, south viewpoint check (claude -p judge) ran and
raised no OVERHEAD/UNMEASURED flag → PASS, full metric gate green, exit 0.
All three files confirmed PIL-openable, non-zero, correct RGBA mode.

No files were touched this pass (pure verification + writeup), so no
`validate_patch.py` run was needed; `deploy_custom_mods.py` sync state for
`BarbslingerArtOverride` was already confirmed in sync by
`PYRELANDS_FACING_REGRESSION_1` this same session.

## criteria
A Barbslinger sprite exists, wired and owner-approved, that is genuinely a
scorpion-form creature with a thick domed body and two independent
(bifurcated) tails each carrying an oversized needle-like spike — not a
reskinned horned beast and not a scorpion in name only. Met.
