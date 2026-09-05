## spec
Found 2026-09-05 while investigating `ARMOURY_MELEEPOWER_STALE_1`. Confirmed
by actually running `gen_armoury_patch.py` against the current live 595-mod
dump (fingerprint `3174253fcd55f69c`) with output redirected away from the
real `Patches/` dir, then diffing.

`SW_MODS` (the generator's list of donor mod names it groups
weapons/projectiles by) does not include whatever name(s) the absorbed
`guy762.KotORWeapons` and `[JDS] StarWars - Armory` content now presents as
in the live dump (those donor mods themselves are retired — their content
was carried forward into our own `Absorbed_AdditionalMods` subfolder,
per `WEAPONS_DONOR_RETIREMENT_1`). Because of this, a full regenerate
**silently drops the vibro-blade tuning blocks for those two donor
families entirely** from `Armoury_MeleePower.xml` — not a wrong value, an
entire missing block, with no error or warning.

This is why `Armoury_MeleePower.xml` cannot safely be regenerated right now
(see `ARMOURY_MELEEPOWER_STALE_1`, which is blocked on this): the vibro
values a naive reviewer computes from `BANDS`/`SOURCE_RANGE` alone
(e.g. expecting `OuterRim_VibroAxe` edge to move to 38, `guy762_vaxe` edge
to 42) may themselves be wrong, because those weapons might belong to a
donor-mod SW_MODS group whose current classification is broken by this gap
rather than being simple stale-constants drift.

## criteria
- Identify the actual live-dump modName(s)/packageId string(s) the absorbed
  KotORWeapons and JDS-Armory content now presents under (read the dump,
  don't guess), and add them to `SW_MODS` (or whatever mapping decides
  donor-mod grouping) so a regen includes their blocks again.
- Re-run the generator with output redirected to a scratch path (never
  overwrite the real `Patches/` dir directly — this generator has no
  dry-run flag; copy `Patches/` aside or redirect `OUTDIR` for testing),
  diff against the currently shipped files, and confirm the two vibro-blade
  blocks reappear with sane values before ever writing to the real path.
- Only then is `ARMOURY_MELEEPOWER_STALE_1`'s regenerate-and-compare step
  safe to attempt.
