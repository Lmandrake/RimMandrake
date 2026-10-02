# CereanManeFix — validation walk
subject: src/RimStarWars/StarWarsPatches  (packageId: mandrake.rsw.patches)
feature: cerean-mane-fix
absorbed: CereanManeFix (dying id rsw.cereanmanefix) folded into StarWarsPatches at Source/CereanManeFix + Textures/OuterRim/Hairs/Cerean/CereanMane_south.png in Sprint wave A (commit 7e6eda0bd) — no longer ships alone.
deps: Neronix17.OuterRim.GalacticDiversity (Outer Rim - Galactic Diversity) — required
list: minimal+Neronix17.OuterRim.GalacticDiversity
status-hint: replaces the fully-transparent OuterRim/Hairs/Cerean/CereanMane_south.png so Ceans wearing HairDef OuterRim_CereanMane stop rendering bald from the front (south) view.

## must be true
- Ships exactly one loose PNG at Textures/OuterRim/Hairs/Cerean/CereanMane_south.png, no Defs, no code.
- Declares no loadAfter (deliberate — on 1.6 the donor serves this art from an AssetBundle via LoadFolders.xml's Common/ folder, and a loose file always wins over a bundled asset regardless of load order).
- The shipped PNG is 512x512 and carries non-zero alpha (the donor's file at the same path, inside its AssetBundle, is 512x512 with alpha maximum 0).
- HairDef OuterRim_CereanMane (owned by Outer Rim - Galactic Diversity, Hairs_Cerean.xml line 37) still resolves with texPath OuterRim/Hairs/Cerean/CereanMane.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.patches"   # load-time
2. [D] asset check: script (PIL, same pattern as Source/draw_mane_south.py) opens the deployed .../CereanManeFix/Textures/OuterRim/Hairs/Cerean/CereanMane_south.png; confirms canvas 512x512 and max alpha > 0
3. [B] jawa/get_def {defType: "HairDef", defName: "OuterRim_CereanMane"} resolves and its texPath field reads OuterRim/Hairs/Cerean/CereanMane — confirms the donor mod that owns this def is present and its path is unchanged
X. [S] (human pass) put a Cerean pawn wearing the Cerean mane hairstyle on the map, view from the south/front, and confirm the crest renders instead of a bald scalp

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**The mane from the front**
- [ ] `cerean_mane_visible_south` — a pawn with the Cerean mane hair seen from the
      front (south) shows the mane, matching what its east view shows.

### cannot show

- [ ] `cerean_never_bald_from_front` — the same pawn rendering bald from the
      front, the transparent-donor-texture defect this fix replaces.
