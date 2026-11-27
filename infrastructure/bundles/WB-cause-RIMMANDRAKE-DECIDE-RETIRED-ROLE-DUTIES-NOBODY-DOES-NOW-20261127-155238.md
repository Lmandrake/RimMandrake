# Work bundle WB-cause-RIMMANDRAKE-DECIDE-RETIRED-ROLE-DUTIES-NOBODY-DOES-NOW-20261127-155238

One member: `RIMMANDRAKE_STEADY_FIRST_PASS_CALIBRATION_SELFTEST_READS_REAL_PICTURES` (class REAL).

## Group 1 (the one member)

- Red: the item's check, 7 FAIL (the ticket said 6; `GOOD is pass` and `refuse` also passed vacuously on an empty
  result). Cause: `build_card` opens every case's real picture with PIL; a slim clone has none, and one case
  (RM_DecayDrake_r2) reads the D: artstore.
- Fix: `selftest_art_first_pass_calibration.py` wraps `F.cases` so every picture is a drawn stand-in (a `.stand-in`
  file, PNG content, shipping canvas, its own colour). could-not-look got a positive control (the whole case is judged).
- Green: the item's check, and a plain run in the slim clone. Planted fault (`GOT["WEAK"]="pass"`): 1 FAIL, as meant.
- Polish: the two vacuous `all()` checks also check the case count.
