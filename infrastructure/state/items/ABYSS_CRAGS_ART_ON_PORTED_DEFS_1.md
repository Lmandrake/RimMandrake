## spec
Split from `ABYSS_FREE_TIER_BODY_1` (steps 2 and 3; steps 1/4/5/6/7 landed or were already true, 2026-10-03).

1. Wire the 12 finished donor-cast art sets (`crags_<label>_{south,east,north}`; `artpipe_state.py find crags_` first:
   vrakk, dhukk, hulggarok, zekkra, kessik, brekkugar, korrag, bhoruk, gruzz, shekkur, ulkhorr, thrizzik) onto the
   Abyss's PORTED defs. No ported defs exist yet: this waits on `DONOR_DEFS_PORT_TO_OURS_1`. Spend no new art job on them.
2. The dusk rat's art redo (owner "replace" ruling, `port_alphaanimals_2026-09-20.decisions.json`): wire it when its
   commission lands (the commission waits on the owner).

Check facings by eye when wiring; west mirrors east.

## criteria
The 12 sets render on their ported defs; the dusk rat carries its redo; no art job spent on a set that already existed.
