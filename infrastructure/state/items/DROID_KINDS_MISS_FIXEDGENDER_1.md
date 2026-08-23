# DROID_KINDS_MISS_FIXEDGENDER_1 Four of our droid pawn kinds miss the fixedGender guard; one is already rendering wrong

## spec

### Measured

`harvest_log.py` against `observed/logs/2026-08-23_Player.log.final` reports
**texture path failures: 2, ABOVE baseline 0** — a NEW regression, not known noise.

```
19849: Failed to find any textures at OuterRim/Droid/Protocol/Body/Naked_Female
       while constructing Multi(initPath=..., color=RGBA(0.749,0.647,0.384,1))
19904: same path, color=RGBA(0.416,0.475,0.600,1)
```

Two different droids, two different colours, one missing texture.

⚠️ **Read with `--stale-ok`.** The instrument REFUSED this log on its own: `ModsConfig.xml`
was written **1466 s after** the run ended and now reads **580 active mods**. The stack has
changed since this log was written. The finding below is confirmed against source on disk,
not only against the log, but the log itself is from a different mod set than what is
installed right now.

### This is the 2026-08-10 droid-texture bug, arriving from a new direction

`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\DroidFemaleTexture_Fix.xml` already
fixes it, and its diagnosis is still correct: Outer Rim Droid Depot ships **only male body
textures** — all 11 body folders hold `Naked_Male_{north,south,east}.png` and no female
variant. The fix forces `fixedGender: Male` onto **7 upstream Droid Depot pawn kinds** so
the female texture is never requested. Its VERIFY block says the log line should be GONE.
It is not gone.

The fix is not broken. It is **incomplete in a way it could not have anticipated**: it
patches Droid Depot's own pawn kinds, and we have since authored **our own** pawn kinds that
use the same droid races and carry no `fixedGender`.

`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Defs\PawnKindDefs\JawaFactionRoster.xml`:

| our pawn kind | race | fixedGender | seen failing |
|---|---|---|---|
| `Jawa_Droid_Specialist` (line 1034) | `OuterRim_ProtocolDroid` | **absent** | **yes, twice** |
| `Jawa_Droid_Grunt` | `OuterRim_ImperialLaborDroid` | **absent** | not yet |
| `Jawa_Droid_Heavy` | `OuterRim_KXSecurityDroid` | **absent** | not yet |
| `Jawa_Droid_Leader` | `OuterRim_SuperTacticalDroid` | **absent** | not yet |

🔑 **Only the Protocol one appears in the log because only it happened to roll female this
run.** The other three are the identical defect and have simply not fired yet. Do not treat
the log's count of 2 as the size of this.

All four belong to `Jawa_FreeDroidEnclaves`, so this is a faction that visibly fields
broken-rendered pawns.

## Fix

**Generator, not the XML.** `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\gen_pawnkind_roster.py`
maps our droid roles onto Droid Depot races (the table at line 131). It must emit
`<fixedGender>Male</fixedGender>` for any kind whose race is an `OuterRim_*` droid — the same
rule `DroidFemaleTexture_Fix.xml` applies upstream, applied at the point we create the kind.

Alternative, if that generator is not the right home: extend `DroidFemaleTexture_Fix.xml`
with four more `PatchOperationConditional` ops in its existing add-if-missing shape. That
keeps one file responsible for the whole rule, which is arguably better — but it is a patch
reaching into our own defs, which is the shape we normally avoid.

⛔ **Do not "fix" this by generating female body art.** The upstream mod has no female
variant for any of the 11 chassis; matching its style for four bodies is real work for a
gender that is meaningless on a droid. `fixedGender` is what the 08-10 authors chose after
checking all 11 folders, and nothing has changed that.

## verify

- All four kinds carry `fixedGender`, in the generator's output and in the deployed copy
  under `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\`.
- Next load: `harvest_log.py` reports **texture path failures 0 = baseline 0**.
- 🔑 The log going quiet is necessary and NOT sufficient — it only proves no female droid
  rolled. Dev-spawn each of the four kinds several times and look; a magenta or absent body
  is the real failure. ⚠️ Per `prove-art-missing-before-generating`, `Graphic_Multi` is the
  case where magenta does NOT reliably appear, which is exactly what this is — so look at
  the pawn, not for a placeholder colour.

## Watch out

- 🔴 `DroidFemaleTexture_Fix.xml` states its VERIFY as *"GONE: Failed to find any textures
  at OuterRim/Droid/*/Body/Naked_Female"*. That check has been failing and nobody noticed,
  because the fix file is read as settled. Whoever takes this should add a line to that file
  pointing here — its diagnosis is right, its coverage is not.
- Our fix covers 7 of Droid Depot's 11 body folders (B1, B1A, B2, BX are unpatched upstream
  too). Whether any active pawn kind uses those four is **UNMEASURED**.
- `gen_pawnkind_roster.py` gets `initialResistanceRange` right on these kinds (14~22),
  unlike `gen_races_mod.py` in `PAWNKIND_RESISTANCE_UNDEFINED_1`. Different generator,
  different defect; do not conflate them.
- Filed by REP from the harvest instrument plus a source read, game DOWN. No pawn was
  spawned and nobody has looked at a droid.
