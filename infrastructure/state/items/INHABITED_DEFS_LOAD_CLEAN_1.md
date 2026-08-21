## spec
First load of a new assembly and four new def files. Cheap, and it gates the
three items below.
  `DutyDef Inhabited_Resident`        `Defs/DutyDefs/Duties_Inhabited.xml`
  `GenStepDef Inhabited_Cast`         `Defs/GenStepDefs/GenSteps_Inhabited.xml`
  `WorldObjectDef Inhabited_Place`    `Defs/WorldObjectDefs/WorldObjects_Inhabited.xml`
  6 keyed strings                     `Languages/English/Keyed/Inhabited.xml`
⚠️ `InhabitedDefOf` names `Inhabited_Resident`, so `DefOfHelper` throws at
startup if that file failed to load. **That is deliberate** — it is the only
early warning available, because a def file that fails to parse otherwise just
produces a game with a missing duty and no message anyone reads.
⚠️ The Harmony patch targets `Verse.Game.DeinitAndRemoveMap`. **A Harmony patch
that matches nothing THROWS at startup, unlike an XML one.** That is the wanted
behaviour: if the target is ever renamed the mod must fail loudly rather than
quietly forget everybody. So a clean startup IS the proof the target bound.

## verify
`Player.log` after a load with `mandrake.inhabited` enabled:
  zero `Could not load reference to` naming an `Inhabited_*` def
  zero `DefOfHelper` errors
  zero Harmony patch exceptions naming `mandrake.inhabited`
then `python3 src/RimMandrake/Utils/refresh.py` and confirm `Inhabited_Place`,
`Inhabited_Cast` and `Inhabited_Resident` appear in the def dump.

## criteria
a `WorldObject_Inhabited` created by the debug action draws its icon on the
planet and its inspect string reads `N souls`.

## notes
**from:** BUILD, 2026-08-20, `f0a9f6c`.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

✅ **PASSED at the 2026-08-20 08:08 load. Nothing further owed on this item.**
Scored by `python3 src/RimMandrake/Utils/score_inhabited_load.py` against the nine
signatures written in `EXPECTED_FAILURES_next_load.md` §4 BEFORE launch — all nine
green. The one line that settles it, `Player.log:5060`:
  `[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts.`
**2 patches** = both Harmony targets bound, so the compile-time delegate proof
held. **0 places, 0 casts** is correct and expected, not a shortfall.
⭐ **And the engine confirmed it independently, which no log line could:** the
578-mod def dump now carries `CharacterDef.json` (269), `InhabitedPlaceDef.json`
(0) and `InhabitedCastDef.json` (0), attributed to `Inhabited (local)`. That is
RimWorld reporting our own def types back to us.
Zero `Could not find type named Inhabited.*`, zero `Config error in Inhabited_`,
zero Harmony exceptions, 25 cross-references = baseline with **0** naming a
`TraitDef`.
⚠️ **Timing note for anyone scoring a future load:** `[Inhabited] ready` is written
by a `[StaticConstructorOnStartup]`, which runs AFTER def loading and after
RimDefDump finishes. Scoring the log too early reads P1 as MISSING when it simply
has not happened yet — it did exactly that here, ~90 s before the line appeared.
