
## what is wrong

`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortA_Bodies.xml`
(`DESERT_FAMILY_PORT_EXECUTION_1`, batch SWAC_A) **uses eight defs that are
defined nowhere on this machine**:

| def | type | referenced at |
|---|---|---|
| `RSW_HornAttackTool` | BodyPartGroupDef | lines 314, 321, 328 |
| `RSW_TailAttackTool` | BodyPartGroupDef | (same file) |
| `RSW_LeftWing` · `RSW_RightWing` | BodyPartDef | lines 515, 690, 828, … |
| `RSW_FrontHorn` · `RSW_LeftHorn` · `RSW_RightHorn` · `RSW_Club` | BodyPartDef | (same file) |

MEASURED 2026-09-20, three searches, all empty:

```
grep -rn "<defName>RSW_HornAttackTool</defName>" src/                       → 0
grep -rn ... "C:/.../Steam/steamapps/common/RimWorld/Mods/SWBestiary/"       → 0
grep -rln ... "C:/.../steamapps/workshop/content/294100/"                    → 0
```

The ONLY file on the machine mentioning any of them is the one that uses
them. ⛔ This is not a reduced-tier artifact — it was measured against the
whole installed mod set, not against the 15-mod tier it was noticed on.

## consequence, from the live log

```
Could not resolve cross-reference to Verse.BodyPartGroupDef named RSW_HornAttackTool (wanter=groups)
Could not resolve cross-reference: No Verse.BodyPartDef named RSW_LeftWing found to give to Verse.BodyPartRecord BodyPartRecord(NULL_DEF parts.Count=0)
BodyPartRecord with null def. body=Dewback
BodyPartRecord with null def. body=Reek
```

⇒ At least the **Dewback** and **Reek** bodies carry null-def part records,
and any `tools` entry keyed on `RSW_HornAttackTool`/`RSW_TailAttackTool`
binds to an empty group — a melee tool that can never be selected.

🔑 Noticed while closing `PORTED_BEAST_MECHANICS_REBUILD_1`; unrelated to that
assembly. Filed rather than fixed because deciding what each part should be
(add the missing defs vs. repoint to vanilla parts) is port work, not a
one-line correction.

## criteria

1. `grep -c "BodyPartRecord with null def" Player.log` reads **0** on a load
   that includes SWBestiary.
2. Zero `Could not resolve cross-reference` lines naming any `RSW_` body part
   or body-part group.
3. Every species whose `tools` reference those groups has a working melee
   tool — checked on a live pawn, not from the XML.

## fixed, not yet live-verified — 2026-09-20/21

All eight refs were repointed in `RSW_DesertPortA_Bodies.xml` to the sibling
defs `RSW_DesertPortA_BodyParts.xml` (same folder, same batch) already
defines under bare names: `RSW_Club`→`SW_Club`, `RSW_TailAttackTool`→
`SWTailAttackTool`, `RSW_HornAttackTool`→`SWHornAttackTool`,
`RSW_LeftWing`/`RSW_RightWing`→`SW_LeftWing`/`SW_RightWing`,
`RSW_FrontHorn`/`RSW_LeftHorn`/`RSW_RightHorn`→`SW_FrontHorn`/`SW_LeftHorn`/
`SW_RightHorn` (17 occurrences total, all 17 confirmed repointed, zero old
refs remaining). This was a naming-mismatch bug, not a genuinely missing
concept: `RSW_DesertPortA_BodyParts.xml` was clearly authored as this file's
companion (identical header/batch comment) and its bare `SWTailAttackTool`/
`SWHornAttackTool` were already resolving correctly for
`RSW_DesertPortB_Bodies.xml`'s own references — repointing was the
conservative choice over adding duplicate `RSW_`-prefixed defs.

Verified offline: `validate_patch.py` clean (0 errors/warnings), raw
`ET.parse` clean, `run_selftests.py` 67/67 pass. **Not verified**: criteria
1–3 above, which need a live log/pawn check — the bridge was held by BENCH
for the whole of this pass (`bridge who` checked, never taken). Also noted:
the `Dewback`/`Reek` BodyDefs in this file are currently orphaned (no live
ThingDef references them bare — `RSW_Dewback`/`RSW_IridonianReek` use
differently-named BodyDefs from an unrelated Mlie-wave batch), which is why
RimWorld's load-time validation still caught the broken refs despite no
current consumer — see `SWBESTIARY_BODYPART_LIVE_VERIFY_1`, filed to close
out the live-check debt (`needs: bridge`).

## live-verified — 2026-09-21

Criteria 1 and 2 MEASURED on a live load: `BodyPartRecord with null def` went
**11 → 0** and `Could not resolve cross-reference` lines naming any of the
eight `RSW_` body-part names went **17 → 0**, against a baseline taken from
the game that was up on the owner's FULL 618-mod list with the un-deployed
(broken) copy. The five BodyDefs this file defines all resolve live out of
`RSW_DesertPortA_Bodies.xml`, so the zero is a fix rather than a file that
failed to load. Criterion 3 has no live subject yet (no ThingDef consumes
`Dewback`/`Reek`, and `RSW_Sketto`'s `Bogwing` body links vanilla tool
groups), so it is deferred, not failed; the wing repoint itself was proven on
a live Sketto. Full evidence and method:
`SWBESTIARY_BODYPART_LIVE_VERIFY_1`.
