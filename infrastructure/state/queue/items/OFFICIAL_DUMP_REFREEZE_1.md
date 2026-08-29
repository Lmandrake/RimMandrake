# OFFICIAL_DUMP_REFREEZE_1 — capture a 584-mod dump, freeze it, regen the armoury

Owner authorized 2026-08-29: "we need to re-freeze the official mod list again, and
likely regenerate your official dump files".

`dump_request.txt` is armed (`all`). After the next FULL-list cold load, in order:

1. Verify the new capture under `DefDump/captures/` carries **584** mods including
   `mlie.showmeyourhands` and `meathax.showmeyourtools` (read its manifest.json,
   never a quoted count).
2. `python3 src/RimMandrake/Utils/refresh.py --freeze` (dry run) → read the line it
   would append → `--freeze --by owner`.
3. `python3 src/RimMandrake/Utils/refresh.py --patches` — Jawa_Armoury/Patches is
   STALE and its generator correctly refuses the 582-mod dump; it needs this fresh
   capture. Then validate per the tool's own output.

The list snapshot side is already done (`801bd127`); saves already sync'd to 584.
