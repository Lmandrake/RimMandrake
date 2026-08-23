## spec
Two saber patch blocks were guarded on `Star Wars : The Force - Lightsaber`, which ships
the saber ThingDefs but does **not** create the `<tools>` those blocks edit.

- `src/Jawa/Jawa_Armoury/Patches/Armoury_MeleePower.xml` — Operation[2], **27 bare
  `PatchOperationReplace`s** on `Force_*saber*/tools/li[label="tip"]/power` and siblings.
- `src/Jawa/Jawa_Armoury/Patches/Armour_Penetration.xml` — Operation[3], **24 conditionals**
  on the same tools' `armorPenetration`.

## the measurement
The concrete sabers (`Force_Broadsaber`, `Force_Lightsaber_Custom`, `_Dual`,
`_Inquisitor`, `_Curved`, `_Shoto`, `_Crossguard`, `Force_Darksaber`) declare **no
`<tools>` of their own** — verified in
`workshop/294100/3466124712/1.6/Defs/ThingDefs_Misc/Lightsaber.xml`, where each is
`ParentName="Force_LightsaberBase"` and nothing more. The string `<label>tip</label>`
appears **zero** times in that whole mod; its base ships `hilt` / **`point`** / `edge`.

🔑 **What creates them is `Star Wars KotOR Weapons and Armor`**, in
`workshop/294100/2938932438/1.6/AdditionalMods/_TheForceLightsabers/Patches/Patch_KotORLightsaberBalancing.xml`
— `PatchOperationAdd`s, itself guarded `IfModActive="lee.theforce.lightsaber"`, that give
each concrete saber `hilt` / **`tip`** / `edge`. The live dump proves whose they are: the
capacities read `guy762_ToolCapacity_SaberStab` and `guy762_ToolCapacity_SaberSlash`,
defined by `guy762.mm.kotorcore`.

**Load order is what made it work, and nothing enforced it:**

| order | mod | role |
|---|---|---|
| 566 | Star Wars : The Force - Lightsaber | ships the saber defs — what we guarded on |
| 567 | Star Wars KotOR Resources and Materials | defines the tool capacities |
| 569 | **Star Wars KotOR Weapons and Armor** | **adds the `hilt/tip/edge` tools** |
| 570 | Jawa Armoury Rebalance | our two blocks |

⚠️ **Remove KotOR Weapons and nothing warns you.** The lightsaber mod stays active, the old
guard still passes, the sabers fall back to `hilt/point/edge` — and MeleePower's 27 bare
Replaces match nothing. A Replace that matches nothing is a **red error at load**, not a
silent no-op, so that block would have thrown 27 of them; Penetration's 24 conditionals
would have gone quietly dead.

## verify
```
python3 skills/rimworld-modding/scripts/validate_patch.py \
  src/Jawa/Jawa_Armoury/Patches/Armour_Penetration.xml \
  src/Jawa/Jawa_Armoury/Patches/Armoury_MeleePower.xml --defs …
```
and, in game, `Force_Broadsaber` still reads hilt **35** / tip **92** / edge **120** with
`armorPenetration` 0 throughout — the values that are already live.

## criteria
Each block is gated on the mod that actually creates what it edits.

## notes
✅ **CLOSED 2026-08-22.** Both blocks now carry a **nested** `PatchOperationFindMod` on
`Star Wars KotOR Weapons and Armor` inside the existing lightsaber guard.

⛔ **Nested, not one FindMod listing both mods — `<mods>` is an OR and this needs an AND.**
Listing both would fire when only one is present, which is the bug wearing a different hat.

🔑 **Penetration is SPLIT, not wholesale re-guarded.** Its first six conditionals target
`Force_LightsaberBase` and `Force_ImbuedBlade`, whose tools the lightsaber mod really does
ship — those stay under the outer guard. Only the 24 concrete-saber operations moved.

Validated: 2 files, **0 errors**. Deployed and verified in sync. ⏳ Live confirmation rides
on the next load; the values are already correct in the 2026-08-21 dump, so this change is
expected to be invisible — that is the point.

⚠️ **This was found by the `FALSE_ZERO_XPATH_RESWEEP_1` sweep and nearly missed.** The
sweep saw 48 operations reading 0 on disk, verified the values were RIGHT in the live dump,
and filed the mechanism as UNCERTAIN rather than calling it fine. It was not fine.
