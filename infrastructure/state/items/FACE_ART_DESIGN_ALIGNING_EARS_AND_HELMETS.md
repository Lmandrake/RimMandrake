# FACE_ART_DESIGN_ALIGNING_EARS_AND_HELMETS

**A DESIGN ticket for BENCH, filed in the background. Not a work order: nothing is to be built, repainted or deployed from it.**
Owner, 2026-10-20: *"create a background ticket to re-assess all the in-game alien face art (and humans too) so we can figure out how we'd like to handle that. Right now it's just a ticket to do the design, not a work order, for Bench."*

## The question
How should every in-game head (our aliens AND the humans) be authored, aligned, tinted and dressed, so painted art matches what the game expects? Owner's read of the lineup: our art is MUCH higher quality than the game's, but is not aligned to what the game expects (Ortolan ears doubled and misplaced, Mimbanese side profile far too wide).

## Already established (read before redoing)
- `design/RimStarWars/head_parts_painted_vs_attached_2026-10-20.md` — design pass: paint silhouette parts into the head; add-on gene parts only for separable cosmetics; skin-colour options; Rakata eye-stalks; helmet options. Verdict recorded there; owner agreed in direction (*"perhaps it merely allows them to overlap the body, but likely creates more issues later if avoidable. If so, let's just draw them"*).
- Evidence: `D:\ClaudeWork\screenshots\2026-10-20\heads_lineup_ALL_FACINGS.png` (the 2026-10-20d live shots) and `Transient/live_testing_2026-10-20d/RESULTS.md`.
- Offline fixes already made and awaiting live check: `XENO_HEADS_VERIFY_BALD_AND_BLUSHING`.

## What the design must decide (the scope of the re-assessment)
1. **Every head in the game:** inventory all head types in use (our species heads under `src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/Heads/`, plus the human heads / vanilla head types and any donor heads still in the live list), per facing, with the measured extents of each.
2. **The envelope:** the vanilla head's drawn extents per facing (UNMEASURED today) as the target every painted head must fit; the allowed overhang for ears, crests, stalks.
3. **Painted vs attached parts, per species:** apply the rule to each species; list the gene attachments to strip (ears, big eyes, ridges, brows) and the slot placeholder (`Ears_Human`, unverified).
4. **Skin colour:** per species choose painted-as-is, neutral-paint-tinted, or mask-split; and whether HUMANS' heads stay vanilla-tinted or are repainted at all. Test the mask-split on one species first.
5. **The wild species** (Rakata eye-stalks, trunks, antennae, anything wider than the skull) and their head-canvas needs.
6. **Headgear:** hide the graphic, species helmets, or per-head-type scale/offset (check Tabula Rasa's `DefModExt_HeadTypeStuff` and apparel `drawData`). Needs one joint hat test with him.
7. **Hair, beards, FacialAnimation:** how they sit on painted heads (the FA-excluded list is `Human-RSW_*`).
8. **Tooling:** what `fit_head_canvas.py` and the head tools must learn (envelope, ear-tip handling), as a follow-on work order only after he approves the design.

## Output wanted
A design document for the owner (mockups first, per his loop), ending in options he can rule on by question card. **No code, art or def changes until he rules.**
