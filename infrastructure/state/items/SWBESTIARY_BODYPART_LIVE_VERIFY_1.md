# SWBESTIARY_BODYPART_LIVE_VERIFY_1 — prove the body-part repoint actually cleared the log

## what is wrong

`SWBESTIARY_MISSING_BODYPART_DEFS_1` fixed the eight dangling defName refs in
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Bodies.xml` by
repointing them to the pre-existing sibling defs in
`RSW_DesertPortA_BodyParts.xml` (same folder, same batch) — the refs were
authored with a stray `RSW_` prefix (`RSW_Club`, `RSW_TailAttackTool`,
`RSW_HornAttackTool`, `RSW_LeftWing`, `RSW_RightWing`, `RSW_FrontHorn`,
`RSW_LeftHorn`, `RSW_RightHorn`) that matched no def on the machine, while
the bare names (`SW_Club`, `SWTailAttackTool`, `SWHornAttackTool`,
`SW_LeftWing`, `SW_RightWing`, `SW_FrontHorn`, `SW_LeftHorn`, `SW_RightHorn`)
were sitting right there already defined and — for `SWTailAttackTool` /
`SWHornAttackTool` — already resolving correctly for
`RSW_DesertPortB_Bodies.xml`'s own references. `validate_patch.py`, a raw
`ET.parse`, and `run_selftests.py` (67/67) all pass clean on the fix, but
none of that is the live log the original item's own criteria named — the
bridge was held by BENCH the whole build pass (`bridge who` checked, not
taken).

## the work

1. Load (or advance) a save that includes SWBestiary, on a mod list where
   `RSW_DesertPortA_Bodies.xml`'s BodyDefs actually load.
2. `grep -c "BodyPartRecord with null def" Player.log` reads **0**.
3. Zero `Could not resolve cross-reference` lines naming any `SW_`/`RSW_`
   body part or body-part group from this file.
4. Any live pawn built on a body that uses `SWHornAttackTool` /
   `SWTailAttackTool` (via `tools` on a ThingDef, if one is later wired to
   the orphaned `Dewback`/`Reek` BodyDefs in this file — see watch out)
   shows a working melee tool, not from the XML alone.

## watch out

The `Dewback` and `Reek` BodyDefs defined in `RSW_DesertPortA_Bodies.xml`
are currently **orphaned** — no live ThingDef references `<body>Dewback</body>`
or `<body>Reek</body>` bare. The actual live races (`RSW_Dewback`,
`RSW_IridonianReek`) use *different* BodyDefs of the same concept
(`RSW_Dewback` from `RSW_MlieWaveB_Bodies.xml`, `RSW_Reek` from
`RSW_MlieWaveC_Bodies.xml`, an unrelated `MLIE_FAUNA_ABSORPTION_1` batch) and
their own `tools` already correctly link `RSW_SWTailAttackTool` /
`RSW_SWHornAttackTool` (the Wave-B/C namespace, not this file's). RimWorld
still validates every loaded BodyDef's part tree at startup regardless of
whether a race consumes it — that is why the original log showed
`body=Dewback` / `body=Reek` null-def errors even with no live consumer,
and it is why criterion 2 (zero cross-reference errors) is checkable even
before any ThingDef is wired to this file's `Dewback`/`Reek`/`Bogwing`/
`RSW_Mynock`/`FlyingAvian` BodyDefs. Criterion 4 (a live pawn with a working
tool) only becomes checkable once `DESERT_FAMILY_PORT_EXECUTION_1` actually
wires a ThingDef to one of these bodies — until then, note it as not yet
applicable rather than a failure.

## criteria

Criteria 2/3 from `SWBESTIARY_MISSING_BODYPART_DEFS_1` confirmed on a live
log. Criterion 4 confirmed once a ThingDef consumes one of this file's
bodies, or explicitly deferred with a note if none does yet.
