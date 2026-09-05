## spec — RESCOPED 2026-09-05, larger than first filed

**Verified, not guessed:** both `guy762.KotORWeapons` ("Star Wars KotOR
Weapons and Armor") and `M3.Continued.JangoDsoul.StarWars.BTI` ("[JDS]
StarWars - Armory") are retired donor mods, absorbed into
`mandrake.rsw.armoury` — and **neither packageId is in the live 595-mod
`ModsConfig.xml`'s `<activeMods>`** (checked directly, not inferred from
the About.xml `modDependencies` list, which only proves "installed", not
"active" — the mistake an earlier reviewing subagent made this session).

`PatchOperationFindMod`'s real semantics (`skills/rimworld-modding/
references/patch-operations.md`): when NONE of `<mods>` is active, it
returns `true` immediately and **never runs its wrapped `<match>` at
all** — no error, nothing logged. Six Armoury patch files still guard
their donor-family rebalance content behind `PatchOperationFindMod` on
these two now-permanently-inactive mod names:

| file | guard | inner ops (currently dead) |
|---|---|---|
| Armour_DamageCategories.xml | [JDS] StarWars - Armory | 2 |
| Armour_Penetration.xml | Star Wars KotOR Weapons and Armor | 73 |
| Armour_Penetration.xml | [JDS] StarWars - Armory | 6 |
| Armour_Ratings.xml | Star Wars KotOR Weapons and Armor | 46 |
| Armoury_MeleePower.xml | Star Wars KotOR Weapons and Armor | 27 |
| Armoury_MeleePower.xml | [JDS] StarWars - Armory | 6 |
| Armoury_RangedDamage.xml | [JDS] StarWars - Armory | 8 |
| Armoury_TorpedoSpeed.xml | [JDS] StarWars - Armory | 2 |

**170 PatchOperationReplace ops, total, currently silent no-ops in the
live game right now.** The concrete ThingDefs these targeted (guy762_v*
melee weapons, and whatever JDS-Armory's weapons/armor are — the whole
"Jawa Armoury Rebalance"-attributed 1112-def absorbed pool) still exist
and are still playable — they just get NONE of this mod's ranged-damage/
melee-power/torpedo-speed/armor-penetration/armor-rating rebalance,
silently keeping their raw absorbed values. This directly undercuts the
mod's own stated purpose (README: median ranged damage 12, blaster
weaker than a fist, etc.) for a whole donor family, in the actual
591-595-mod campaign the owner plays.

Reopened as DIRTY (see `code_review_status.py reopen` calls, this date):
Armour_DamageCategories.xml, Armour_Penetration.xml, Armour_Ratings.xml,
Armoury_RangedDamage.xml, Armoury_TorpedoSpeed.xml — all previously marked
clean in wave 38 by reviewers who checked validator output and "installed"
status but never checked ACTIVE status against ModsConfig.xml themselves.
(Armoury_MeleePower.xml is already DIRTY/blocked via `ARMOURY_MELEEPOWER_STALE_1`.)

## correction 2026-09-05
`Armour_Ratings.xml` is under a standing owner hold —
`src/DEPLOY_HOLD.txt`: "Owner ruled SHIP NEITHER, 2026-08-12" (alongside
`Warcasket_HazardRetune.xml`) — so it is never actually written to the live
Mods folder regardless of this bug. Its 46 ops are NOT part of the "currently
live" impact; only the other 5 files (124 ops: DamageCategories 2,
Penetration 79, MeleePower 33, RangedDamage 8, TorpedoSpeed 2) were actually
shipping and silently dead. Fixed and deployed all 5; fixed but NOT deployed
Armour_Ratings.xml (repo-only, per the hold — the fix is still correct and
harmless to have in the repo).

## why not fixed on the spot
This needs a design call, not just a mechanical patch: replace the
`PatchOperationFindMod(donor-name)` guard with something that tests for
the *content* now, not the retired mod — most likely
`PatchOperationConditional` testing whether the target ThingDef/xpath
exists (`skills/rimworld-modding` reference: "Conditional tells you the
thing you're about to edit is present, which is the fact you actually
depend on" — exactly this situation). That's a real semantic change
across 6 files and ~170 ops; each guard's `nomatch` behavior (if any) also
needs checking so a genuine "mod truly absent" case (if the owner ever
does drop this content) still degrades gracefully. Not something to do
in the same pass as discovering it.

## deployed 2026-09-05
`deploy_custom_mods.py --mod Armoury --apply` — 5 files deployed and
verified in sync (Armour_Ratings.xml correctly skipped, held). **Needs a
RimWorld restart to take effect** (defs only parse at startup) — not forced
tonight since the owner was actively using the bridge/game for his own
review session; verify on the next natural full-list load instead of
forcing one. Did not deploy via a fresh restart myself to avoid interrupting
that.

## criteria
- Each of the 8 guard blocks above tests presence of its actual target
  content (e.g. `PatchOperationConditional` on the first concrete
  defName/xpath each block edits) instead of a retired mod name.
- `validate_patch.py` clean against the full 595-mod list.
- Spot-check via bridge/dump read (or a load) that at least one previously-
  dead value now actually lands on a live ThingDef (e.g. `guy762_vaxe`
  edge power reads something other than its raw absorbed value).
- Fresh independent review of each touched file finds nothing, then
  `code_review_status.py mark-clean`.
