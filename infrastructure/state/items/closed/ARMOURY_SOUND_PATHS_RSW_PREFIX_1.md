# ARMOURY_SOUND_PATHS_RSW_PREFIX_1 — 18 blaster sounds silently resolve to nothing

## spec

MEASURED by BENCH 2026-09-03 against `src/RimStarWars/Armoury/`, after the live
589-mod load logged one missing clip:

```
Could not load AudioClip at 'BlasterSound/RSW_DC-17_Blaster_Pistol_Shot'
in any active mod or in base resources.
```

That is not one broken sound. **18 of the Armoury's 19 declared `clipPath`s point
at files that do not exist**, and all 18 are fixed by the same one-character-class
edit: the `RSW_` prefix belongs on the **defName**, not on the **path**.

```xml
<defName>RSW_DC-17_Blaster_Pistol_Shot</defName>          <!-- correct -->
<clipPath>BlasterSound/RSW_DC-17_Blaster_Pistol_Shot</clipPath>   <!-- wrong -->
```
The file on disk is `Sounds/BlasterSound/DC-17_Blaster_Pistol_Shot.ogg` — no
prefix. Dropping `RSW_` from the path (never from the defName) resolves all 18;
verified by checking `.ogg`/`.wav`/`.mp3` for every declared path. The 19th,
`LMG/eWebShotSFX`, is fine — it ships as `.wav`.

Almost certainly collateral from the naming migration: the defName was correctly
prefixed and the `clipPath` was prefixed along with it, but the assets were not
renamed — and nothing checks that a clipPath resolves.

**Why only one error appeared in the log:** RimWorld resolves an AudioClip
lazily, on first play. Each of the other 17 fires the first time its weapon
shoots — so the log looks nearly clean while most of the Armoury's guns are
silent in play. Same shape as the texture rule this repo already knows: the asset
binds by PATH, never by defName.

Deploy is in sync (1755 files), so the game copy has the same broken paths — this
is a source defect, not a deploy drift.

## verify

Every `clipPath` in `src/RimStarWars/Armoury/Defs/SoundDefs/*.xml` resolves to a
file that exists under `src/RimStarWars/Armoury/Sounds/`, checked for all three
audio extensions; and a live load logs no `Could not load AudioClip` naming an
`RSW_` path. Best proven by firing one of the affected weapons, since the failure
is lazy.

## criteria

1. **No defName is renamed** — the fix touches `clipPath` only. `RSW_` is correct
   on the defName and is the shipping grammar.
2. A guard so this cannot recur silently: a selftest that asserts every declared
   `clipPath` in our own mods resolves to a real asset. This class of defect is
   invisible to `validate_patch.py` and to a def dump, and only surfaces when a
   player fires the gun.
3. Re-checked after any future naming migration — the same mistake is available
   to every `texPath` and `clipPath` we own.
