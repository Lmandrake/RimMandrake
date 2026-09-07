## finding
Confirmed live in the fresh Player.log from today's full 598-active-mod load
(`harvest_log.py --show configerror` / `patchfail`, cross-checked against
`validate_patch.py --live` on the matching def dump captured the same load):

```
Verse.PatchOperationReplace(xpath="/Defs/ThingDef[defName="OuterRim_Proj_ProtonArtillery"]/projectile/damageAmountBase"): Failed to find a node with the given xpath
```

Two of Armoury's OWN patch files disagree about whether
`OuterRim_Proj_ProtonArtillery`/`OuterRim_Proj_ProtonMortar` already declare
`projectile/damageAmountBase` (they don't, in the donor's shipped XML — checked
directly in `Outer Rim - Core`'s own `Turret_ProtonArtillery.xml`/
`Turret_ProtonMortar.xml`):

- `Turrets_DamageDoctrine.xml` correctly uses `PatchOperationAdd` on
  `.../projectile` to CREATE `damageAmountBase` (3188 / 560) — this part is
  right, because the field is genuinely absent upstream.
- `Armoury_RangedDamage.xml` then does `PatchOperationReplace` on
  `.../projectile/damageAmountBase`, with its own comment stating the intent
  explicitly: `<!-- OuterRim_Proj_ProtonArtillery : 3188 -> 600 -->` /
  `<!-- OuterRim_Proj_ProtonMortar : 560 -> 335 -->` — a deliberate two-stage
  pipeline (Add the base, then re-tune it), but it only works if
  `Turrets_DamageDoctrine.xml`'s Add applies FIRST.

**Filename order is backwards for this dependency.** `Armoury_RangedDamage.xml`
sorts before `Turrets_DamageDoctrine.xml` alphabetically, and RimWorld applies
one mod's own `Patches/*.xml` files in that (filesystem/alphabetical) order, so
the Replace runs before the field exists and fails every load — silently
leaving both projectiles at their ADDED value (3188 / 560) instead of the
intended tuned value (600 / 335), a real balance defect, not just a log line.

This is NOT the `ARMOURY_LOADAFTER_STALE_1` defect (that item is about
cross-MOD `loadAfter` declarations vs. other mods' `FindMod` targets) — this
is an intra-mod, cross-FILE ordering bug between two of Armoury's own patch
files, and adding a `loadAfter` entry would not touch it.

## owner decision needed / fix
Pick one:
(a) Rename the files so alphabetical order puts the Add before the Replace
    (e.g. `Turrets_00_DamageDoctrine.xml`).
(b) Move both operations into the SAME file, Add then Replace, in that order.
(c) Whichever generator(s) emit these two files should assert this ordering
    dependency at generation time (the `declarer()`-style safety this
    session's Armoury work already leans on elsewhere) rather than relying on
    filename luck.

Check whether other defNames share this exact two-stage
Add-in-one-file/Replace-in-another shape before picking a fix — only
`OuterRim_Proj_ProtonArtillery`/`OuterRim_Proj_ProtonMortar` were confirmed
this pass; there may be more instances of the same generator pattern.

## verify
```
PROVE   after the fix, a fresh load's Player.log has no
        "PatchOperationReplace...damageAmountBase...Failed to find a node"
        line for either defName; jawa/get_def on OuterRim_Proj_ProtonArtillery
        reads damageAmountBase 600 (not 3188), OuterRim_Proj_ProtonMortar 335
        (not 560)
EXPECT  both values match Armoury_RangedDamage.xml's stated tuned targets
LIES    checking only that the Replace stops erroring (e.g. by reordering so it
        runs on a field that already exists at 0) without checking the RESOLVED
        value actually landed at the intended tuned number
```
