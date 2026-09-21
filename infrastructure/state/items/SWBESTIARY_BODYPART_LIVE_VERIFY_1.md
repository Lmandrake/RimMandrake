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

## live-verified — 2026-09-21, PASS

Driven by FOUNDRY on the bridge, on a purpose-built 19-mod tier
(`modset_builder.py --tier desertplants`, all five DLC per the 2026-09-19
ruling) holding `mandrake.rsw.swbestiary` and its full dependency closure.
Deploy first: `deploy_custom_mods.py --mod SWBestiary --apply` wrote the
repointed `RSW_DesertPortA_Bodies.xml` to the game folder (it had never been
deployed — the live game was still loading the broken copy).

**Baseline, taken from the live `Player.log` of the game that was up on the
owner's FULL 618-mod list immediately before this pass, i.e. the UNFIXED
deployed copy:**

| string | before | after |
|---|---|---|
| `BodyPartRecord with null def` | **11** | **0** |
| `Could not resolve cross-reference` naming any of the eight `RSW_` names | **17** | **0** |
| occurrences of `RSW_HornAttackTool` / `RSW_TailAttackTool` / `RSW_LeftWing` / `RSW_RightWing` / `RSW_FrontHorn` / `RSW_LeftHorn` / `RSW_RightHorn` / `RSW_Club` anywhere in the log | 3/3/3/3/1/1/1/2 | **0/0/0/0/0/0/0/0** |

The 11 before-records named `body=Dewback`, `body=Reek` (×3), `body=Bogwing`
(×2), `body=RSW_Mynock` (×2) and the rest. 219 `Could not resolve
cross-reference` lines remain on the after-load; **none** of them names a body
part or a body-part group — they are absent-mod refs (`guy762_Robes_jawa`,
`OuterRim_Durasteel`, vanilla `SoundDef`s) that the 19-mod tier does not carry.

**Guard against a false pass** (a file that failed to load produces no errors
either): `jawa/get_defs` resolved **13 of 13**, including all five BodyDefs
this file defines — `Dewback`, `Reek`, `Bogwing`, `RSW_Mynock`, `FlyingAvian`
— each reporting `fileName: RSW_DesertPortA_Bodies.xml`, `packageId:
mandrake.rsw.swbestiary`, plus `SWHornAttackTool`, `SWTailAttackTool`,
`SW_LeftWing` and `SW_Club`. The file loaded; the errors went.

**Criterion 4 — NOT YET APPLICABLE, exactly as this item's "watch out"
predicted.** No live ThingDef consumes `Dewback` or `Reek`, and the only
ThingDef consuming any body in this file is `RSW_Sketto` (`<body>Bogwing</body>`),
whose own `tools` link vanilla groups (`FrontLeftPaw`, `Teeth`,
`HeadAttackTool`), not `SWHornAttackTool`/`SWTailAttackTool`. So the
"working melee tool on a group from this file" check has no subject and is
deferred, not failed.

What was checkable, and passed, is the wing repoint on a live pawn: four
`RSW_Sketto` spawned clean (`Moving 1.0`, zero `capacityErrors`, zero
hediffs), and a positive existence test on the repaired parts —
`jawa/pawn_health add Bruise` to **`SW_LeftWing` succeeded** and to
**`SW_RightWing` succeeded**, while the same call for a part this body does
not have was correctly refused (*"No body part 'Torso' on this pawn"*), which
is the negative control that makes the two successes mean something. Before
the repoint those two parts were the dangling `RSW_LeftWing`/`RSW_RightWing`
and were exactly what produced `body=Bogwing` null-def records.

⇒ Criteria 2 and 3 of `SWBESTIARY_MISSING_BODYPART_DEFS_1` confirmed on a live
log against a measured baseline; criterion 4 deferred with the note this item
asked for. Both items close.
