## spec
found-by: BENCH helper (2026-11-05), running `proof_all.py --offline-gate`: the only red is validation:O6_review_round1, B14 "recoloured pieces stale: 8 stale of 24" (Green/Brown/Yellow/Blue Junction_T/X).
cause: 9bb5b6eaad (GSS_JUNCTION_REDRAW_BODY_WIDER_THAN_CORD) re-necked each coloured ExtCord junction variant separately (art_source/junction_necks_2026-11-05/make_necks.py), so the variants no longer equal `recolor_extcord_pieces.py`'s recolour of the new orange base; 300-800 pixels per piece differ by more than 24 levels. Running the recolour would overwrite judged art, so it was not done blind.
effect: every `proof_all.py --live` refuses at the offline gate unless `--allow-red O6_review_round1` (the GSS live proofs filed 2026-11-05 carry that flag and cite this item).
## criteria
- A1 L0: either regenerate the 8 variants from the new base via recolor_extcord_pieces.py and judge them against the necked versions (art pipeline), or teach the B14 check to accept the make_necks output; `recolor_extcord_pieces.py --check` exits 0 and O6_review_round1 PASSes
- A2 L0: drop `--allow-red O6_review_round1` from infrastructure/state/live_proofs/GSS_SWITCHES_PROVE_LAST_FOUR_STANDING.txt and GSS_WATER_STUB_FIX_PASSED_LAST_WEEK.txt
