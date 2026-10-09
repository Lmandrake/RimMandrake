# SHEET_DONOR_COLUMN_FALSE_PASS_1 — gate req 4 passes on our own copy of donor art

MEASURED 2026-10-06 01:55. `art_sheet.py` marks a donor-kind column `ours` when the package is `mandrake.*`
(our deployed copy, "not a donor original", l.~321), but never exported that key into the sheet's ITEMS, so
`scaled_review_gate.check_donor_column` (req 4) counted our copy as the donor column. Exporting it (tried tonight,
reverted) made req 4 fail on: Plant_Ambrosia (WeepingStones), AB_ToxicGamma (Abyss), Plant_HydenockTree_Wild +
Plant_JoganTree_Wild (FeverWood), AA_Agaripawn/AA_MycoidColossus/AA_Swarmling/AB_* (TheRot).

Two causes behind those rows: (a) the owner PURGED the donor original (Ambrosia's VTE original, ToxicGamma's Alpha
Biomes original) — req 14 hides it, req 4 then wants it; (b) no donor original is known at all (Jogan/Hydenock).

NEXT: export `ours`, teach req 4 that a donor original the owner purged counts as shown-and-rejected, and list rows of kind (b) as UNMEASURED donor art rather than passing them.
