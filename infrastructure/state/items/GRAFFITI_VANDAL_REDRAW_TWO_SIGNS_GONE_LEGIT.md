## spec
Class MOD (art), from test pilot gen 19 of GRAFFITI_NORTHSTAR_GREEN_FULL_1 (live A2, 2026-11-05, small list, fresh quicktest).
- Expected: no Graffiti mark reads as a contemporary real-world sign (bar `mark_carries_no_earth_signage`; owner ruling
  2026-09-16 in the bar text: "He chose to replace the offending glyph rather than exempt it").
- Observed: the judge FAILed the bar on both gallery pages, independently, citing "a red circle crossed by a diagonal slash ...
  the standard real-world 'prohibited/no' sign" and "a green lightning bolt that looks like an electrical-hazard" sign.
- Proof the shapes are ours: the gallery's bottom run is `_PAGES[0][0]` = `RM_Graffiti_Vandal` (screen rows are z-flipped);
  its Graphic_Random set is `src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Vandal/vandal_0..5.png`, and
  vandal_1.png is a clean pink prohibition sign, vandal_0.png a green hazard bolt (the regen of GRAFFITI_VANDAL_ART_REGEN_1, 2869c15750).
  The CrossOut and WarningGlyph art do not hold these shapes (checked).
- Evidence: results `D:\ClaudeWork\rimmandrake\testpilot_GRAFFITI_NORTHSTAR_GREEN_FULL_1\g19\exp2b_results.json`, gallery capture `D:\ClaudeWork\rimmandrake\testpilot_GRAFFITI_NORTHSTAR_GREEN_FULL_1\g19\shots\gallery_page_0_*`, texture strip `D:\ClaudeWork\rimmandrake\testpilot_GRAFFITI_NORTHSTAR_GREEN_FULL_1\g19\vandal.png`.
## verify
Both variants are replaced through the art pipeline (judged against the bar), or removed from the set; then the Graffiti judge's
`mark_carries_no_earth_signage` stops citing a prohibition sign or a hazard bolt on a fresh gallery run.
