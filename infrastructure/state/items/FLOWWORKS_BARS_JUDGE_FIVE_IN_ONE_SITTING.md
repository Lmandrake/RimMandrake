## spec
`design/validation_walks/RimMandrake/FlowWorks.md` `## north star` gained `still_water_one_surface_height` (R9,
owner said 2026-10-17, `OWNER.jsonl` tsn 1792258162801304562). The validated-hash covers the whole section, so he
re-validates it in one sitting, together with the bars the rebuild rewords: `fill_tier_legible` (one more state
under 25 cm) and `depth_and_fill_jointly_legible` (both in metres), `pit_depth_ladder_legible` and
`pawn_height_ladder_legible` (both say "four depths"). Measuring script stub for the new bar:
`src/RimMandrake/FlowWorks/northstar/level_surface_bar.py` (chain `water_level_surface` in
`src/RimMandrake/FlowWorks/validation.py`). Validation is his; no agent marks it.

## verify
- L4: `modcheck floor --all` shows FlowWorks' north star validated at the new hash, on his word.
