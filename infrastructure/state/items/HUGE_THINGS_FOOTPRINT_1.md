# HUGE_THINGS_FOOTPRINT_1 — Huge Things: solid trunks for huge plants, hitboxes for huge pawns

## Owner's words
- 2026-10-07 07:17, by question card, option 1 ("Solid trunk, open canopy") with a typed note: *"(1) and this may
  be related to another mod we have for enormous animals needing similar treatment"*.
- Owner typed in chat (relayed by the coordinating window, so `--owner-said` could not carry it): *"This might be
  an extractable mod to handle "huge plants" and "huge animals" together?"* — hence a standalone mod, not a kit.

## What
Built 2026-10-07: `src/RimMandrake/HugeThings` (`mandrake.rm.hugethings`). Design, per-species table and the
mechanism: `design/RimMandrake/giant_footprint_design_2026-10-07.md`. The Rot opts in nine giants
(`TheRot/Patches/RotGiants_HugeFootprint.xml`); Its titan half (Titanic Creatures, merged in 2026-10-07) opts in every tiered race.

## Verify
- Offline: `python3 src/RimMandrake/HugeThings/selftest_hugethings_footprint.py` (12/12) and
  `python3 src/RimMandrake/HugeThings/validation.py` (STATIC PASS).
- Live: the suite's `trunk` chain on a list with Harmony + Huge Things + `mandrake.rm.biomes`.
- Human: walk a Rot map — trunk sizes against the art, click the stem, pawns path round it and under the cap.

## Watch out
- Trunk sizes are first guesses from drawn width + description, not from the art.
- The plant's own cell is deliberately NOT blocked (it must stay reachable to cut/harvest); the trunk stands
  north of it because Plant.Print lifts the sprite's base onto that cell.
- Removing the mod from a save drops the blocker Things with a load error; turn trunks off and save first.
