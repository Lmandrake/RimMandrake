## spec
🔴 **MEASURED 2026-08-21, on the owner's own screen. This is no longer a warning inherited
from 2026-08-18 — it happened again, and it was watched happening.**

The world paint was run with `--despite-map` against a game holding one live colony map.
Every stage reported success and the planet painted correctly. Then:

- the **colony was destroyed** and the game could no longer create a new one
- the game state became **unstable** — "I could no longer make a new colony"
- **UI buttons lost their icons and their names**, which is the render/atlas layer failing,
  not a gameplay bug
- remaking the world from inside that broken session produced a planet that had **lost
  `myLittlePlanetSubcount 7` and `planetCoverage 1`** — see `PRESET_ONSCREEN_CHECK_UNVERIFIED_1`
- the owner took the game DOWN

⚠️ **The paint itself was faithful.** Seven tiles read back from the engine matched the CSV
to the digit, lint fell 3,529 → 86, and the picture was right. The damage is not that the
paint was wrong. **The damage is that the paint moved the ground out from under a map that
had already been generated from it**, and RimWorld has no mechanism to reconcile the two.

🔑 **The cost is not just the map.** Everything measured after the paint in that session is
now suspect, because a half-broken game answers the bridge normally — that is the zombie
state `RT_PROBE_LOAD_ABORTS_ON_578_1` documents. The findings recorded before the paint
(the log harvest, the def dump) stand; the ones after it want re-proving on a clean load.

## verify
`w9_run.py` refuses on `mapCount > 0` — that guard was added on 2026-08-21 and is what
should have stopped this. `--despite-map` must survive as an escape hatch, but its help
text and the run sheet must both carry the measured outcome rather than a caution.

The next paint runs against a world generated fresh with **no map ever instantiated**, and
`mapCount` is read and recorded as 0 before stage 1.

## criteria
- `w9_run.py --despite-map` prints the measured consequence, not a general warning
- `WORLDPAINT_REHEARSAL.md` §7 names this run as the evidence
- the next paint records `maps 0` in its report before stage 1, and the owner reaches a
  colony afterwards without the game misbehaving

## notes
Filed by CHECK, 2026-08-21. The owner authorised `--despite-map` explicitly and I ran it;
the guard existed and was overridden knowingly. What was NOT known, and is now, is that the
failure is not confined to the map — it takes the session's UI and its ability to start a
new colony with it. That is worth more than the map was.
