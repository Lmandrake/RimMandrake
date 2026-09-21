
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
