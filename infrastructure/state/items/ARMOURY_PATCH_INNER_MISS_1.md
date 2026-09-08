## evidence (full-list load, 2026-09-07, 598 mods)

`harvest_log.py` RED: **patch operations failed = 8, baseline 5.** The three new
lines are all ours:

```
908: [Jawa Armoury Rebalance] PatchOperationFindMod(Dungeon Pack (Continued)) failed
910: [Jawa Armoury Rebalance] PatchOperationFindMod(Outer Rim - Core) failed
912: [Jawa Armoury Rebalance] PatchOperationFindMod(Star Wars : The Force - Lightsaber) failed
```

## why this is NOT a missing mod

🔑 **All three mods are installed AND active** — measured by parsing every
About.xml under Workshop + Mods (1341 scanned) against `ModsConfig.xml`:

| mod name | packageId | active |
|---|---|---|
| Dungeon Pack (Continued) | `Mlie.DungeonPack` | ✅ |
| Outer Rim - Core | `Neronix17.OuterRim.Core` | ✅ |
| Star Wars : The Force - Lightsaber | `lee.theforce.lightsaber` | ✅ |

And `PatchOperationFindMod.ApplyWorker` (read from source) **returns `true` when
the mod is absent** and there is no `nomatch`. It returns false ONLY when the mod
WAS found and the inner `match` operation failed.

⇒ **The mods were found; our own inner xpath missed.** This is our defect, not a
donor's, and it is invisible to `validate_patch.py` because the outer op is
well-formed.

## leading hypothesis — NOT yet proven, do not close on it

Two of our files patch the SAME field on the same def with opposite operations:

- `src/RimStarWars/Armoury/Patches/Turrets_DamageDoctrine.xml` line 221:
  `PatchOperationAdd` on `/Defs/ThingDef[defName="DP_Cannonball"]/projectile`
  ADDING `<damageAmountBase>560</damageAmountBase>`
- `src/RimStarWars/Armoury/Patches/Armoury_RangedDamage.xml` line 126:
  `PatchOperationReplace` on
  `/Defs/ThingDef[defName="DP_Cannonball"]/projectile/damageAmountBase` → 335

If the Replace runs before the Add, the field does not exist yet and the Replace
fails. Order-dependent, and the same Add/Replace pairing appears for the Outer
Rim projectiles.

⚠️ Alternative not ruled out: the defName genuinely does not exist in the current
version of the donor mod. **Check the live def dump for each xpath's target
before assuming the ordering story** — a hypothesis that fits is not evidence
(this is the failure mode `read-the-mechanism-before-filing-the-fix` names).

## fix belongs upstream

These files are generator output (`gen_armoury_patch`). A hand-edit will be
regenerated away. Related open item: `ARMOURY_SUBSTRING_RUNG_TRAP_1`.

## how it will be settled

Re-run a load and read `harvest_log.py --show patchfail`: **patch operations
failed must return to baseline 5**, with none of the three `[Jawa Armoury
Rebalance]` lines present.

## RESOLVED (FOUNDRY, 2026-09-08) — all three confirmed, two different root
causes, both fixed at the generator source

Read the actual captured stack traces in
`Transient/Player_log_ninefold_crash_598mod_2026-09-07.log` (lines 848-866) —
RimWorld logs the exact failing xpath and file for each, so nothing here was
guessed:

```
[Jawa Armoury Rebalance - Start of stack trace]
Verse.PatchOperationReplace(xpath="/Defs/ThingDef[defName="DP_Cannonball"]/projectile/damageAmountBase"): Failed to find a node with the given xpath
...
Source file: .../Mods/Armoury/Patches/Armoury_RangedDamage.xml
[Jawa Armoury Rebalance - Start of stack trace]
Verse.PatchOperationReplace(xpath="/Defs/ThingDef[defName="OuterRim_Proj_ProtonArtillery"]/projectile/damageAmountBase"): Failed to find a node with the given xpath
...
Source file: .../Mods/Armoury/Patches/Armoury_RangedDamage.xml
[Jawa Armoury Rebalance - Start of stack trace]
Verse.PatchOperationAdd(xpath="/Defs/ThingDef[defName="Force_Lightsaber_Custom"]/tools/li[label="hilt"]"): Failed to find a node with the given xpath
Verse.PatchOperationConditional(...tools/li[label="hilt"]/armorPenetration): Error in <nomatch>
...
Source file: .../Mods/Armoury/Patches/Armour_Penetration.xml
```

**1. Dungeon Pack (Continued) — hypothesis CONFIRMED, exactly as written.**
`DP_Cannonball` (`ParentName="BaseBullet"`, vanilla — decompiled: `BaseBullet`
has no `<projectile>` block at all) ships no `damageAmountBase` of its own.
`gen_turret_doctrine.py`'s `Turrets_DamageDoctrine.xml` correctly emits a
`PatchOperationAdd` to create the field. But `gen_armoury_patch.py`
independently classified the same projectile onto its own "artillery" rung
and emitted a `PatchOperationReplace` for it into `Armoury_RangedDamage.xml`
— which sorts before `Turrets_*` alphabetically, so it ran first and failed.

**2. Outer Rim - Core — same mechanism, different defName.**
`OuterRim_Proj_ProtonArtillery` (also `ParentName="BaseBullet"`, confirmed by
reading the donor's own XML on disk, workshop 2919227155) has the identical
Add/Replace race between `Turrets_DamageDoctrine.xml` and
`Armoury_RangedDamage.xml`.

Both are exactly the debt `gen_armoury_patch.py`'s own header already named
(2026-08-29): "gen_turret_doctrine.py writes those... and its output file
sorts after this one so its writes win... On this generator's NEXT regen,
exclude those projectiles from the emplacement/artillery/turbolaser rungs
entirely." That regen never happened. **Fix**: `gen_armoury_patch.py` now
reads `Turrets_DamageDoctrine.xml` off disk (mirroring the existing
`self_supplied_tools_defnames()` pattern) and excludes every projectile
defName it manages from its own candidate pool. Removed 33 now-redundant
entries from `Armoury_RangedDamage.xml` (DP_Cannonball and
OuterRim_Proj_ProtonArtillery among them) — no other line changed, confirmed
by regenerating to a temp path and diffing defName-by-defName before
overwriting.

**3. Star Wars : The Force - Lightsaber — a DIFFERENT root cause, same
family of bug, different generator.** `Armour_Penetration.xml` is generated
by a *sibling* script, `gen_armour_patch.py` — not `gen_armoury_patch.py`.
It has an "injected tools" branch (aiming a `PatchOperationConditional`'s
`<nomatch>` `Add` at a concrete defName's `tools/li[label=X]`) with no
equivalent of `gen_armoury_patch.py`'s `self_supplied_tools_defnames()`
guard. `Force_Lightsaber_Custom` (and 7 sibling lightsabers) only gets its
`<tools Inherit="False">` node from
`Absorbed_Kotorweapons_TheForceLightsabers_Patch_KotORLightsaberBalancing.xml`,
a SUBFOLDER patch that RimWorld applies *after* top-level files —
`Armour_Penetration.xml` is top-level, so at the time it runs the `hilt` li
does not exist yet. This is the exact `LIGHTSABER_MELEE_PATCH_FAIL_1` /
`ARMOURY_LIGHTSABER_FINDMOD_1` trap recurring in a script that was never
given the fix. **Fix**: ported `self_supplied_tools_defnames()` into
`gen_armour_patch.py` verbatim (same PATCHDIR-reading logic) and skip the 8
self-supplied lightsaber defNames in the AP "injected" branch. Removed
exactly those 8 defNames' AP ops (24 `<li>` entries) from
`Armour_Penetration.xml` — nothing else changed.

**Ordering hypothesis for #1/#2: fully correct as written in this item.**
Alternative (field genuinely absent forever) was checked and ruled out —
`BaseBullet` never carries `damageAmountBase`; it is *always* absent until
something Adds it, and that something is `Turrets_DamageDoctrine.xml`.
**#3 was NOT the Add/Replace-ordering pattern** — no Replace/Add race between
two of *our* files on the same field; it was a *different* generator's
version of the tools-not-yet-injected trap. Do not conflate the two when
reading this item later.

**Regen environment note, for whoever runs these generators next**: at fix
time `ModsConfig.xml` was the 25-mod minimal test list (another window's), so
`def_inventory.build_offline()` could only resolve declarers for ~7% of
candidates — a full blind regen right then would have silently deleted
dozens of unrelated, correctly-tuned entries (confirmed by a scratch-path
diff before touching anything). Verification instead used
`infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260907_215737.xml`
(599 mods) passed as a **read-only backup swapped onto the live ModsConfig.xml
path only for the few seconds of the generator runs, then restored
byte-identical** (`md5sum` verified before and after) — the live file itself
was never left in a changed state. `Armour_DamageCategories.xml` and
`Armour_Ratings.xml` also differed under the full list (unrelated
retired-mod-status drift, nothing to do with this fix) and were deliberately
**not** touched — only the two files with an isolated, fully-understood diff
were overwritten.

`validate_patch.py` (run against the full modlist + a live def dump, since
the default minimal-list config makes it refuse to report a verdict): **0
errors, 0 warnings beyond the existing 101 advisory nomatch-shape ones**, all
three files. `run_selftests.py`: 44/45, the one failure
(`selftest_tool_metadata.py`, a BridgeTools DLL/source drift) unrelated and
pre-existing.

**Still owed**: a fresh full-list cold load + `harvest_log.py --show
patchfail` reading 5, not 8. Not done here — FOUNDRY was told another window
holds the live bridge session and must not restart the game. Left as an
explicit next step; see the block reason on this item.
