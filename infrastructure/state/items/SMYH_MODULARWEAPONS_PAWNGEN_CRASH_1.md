# SMYH_MODULARWEAPONS_PAWNGEN_CRASH_1 — Show Me Your Hands × ModularWeapons2 kills pawn generation

Found 2026-09-13 by BENCH during a Pyrelands dev quicktest: the quicktest world
generated, then the map-gen died with an "Error while generating a map" modal.

## Root cause — CONFIRMED from source, not inferred

`Player.log` 12297–12409: `System.InvalidProgramException: Invalid IL code in
(wrapper dynamic-method) ...ShowMeYourHands.HandDrawer.DrawHandsOnWeapon_Patch1
(...): IL_021e: div`, thrown from inside `PawnGenerator` while making a starting
pawn. Because every starting pawn with a weapon triggers the hand-draw path, the
whole map generation aborts. It reproduces on ANY new map on the current list.

**Mechanism (read from both mods' actual code):**
- ModularWeapons2 (`kaitorisenkou.ModularWeapons2`, installed DLL dated
  **2026-08-09**) Harmony-**transpiles** SMYH's `HandDrawer.DrawHandsOnWeapon`
  (`ModularWeapons2/ModularWeapons2.cs`, method `Patch_SMYHHandDrawer`, guarded
  by `if (MW2Mod.IsShowMeYourHandsEnable)`). A transpiler rewrites the target
  method's IL by matching specific instructions/fields (`MainHand`, `OffHand`
  stfld sites).
- Show Me Your Hands (`Mlie.ShowMeYourHands`, installed DLL dated
  **2026-09-13** — rebuilt TODAY) shipped a changed `DrawHandsOnWeapon` body.
- MW2's month-old transpiler now injects its extra instructions at the wrong
  stack positions against the moved method, producing invalid IL (`div` with a
  bad operand stack). Classic transpiler-vs-moved-target break; the newer of the
  two mods moved and the older one had not caught up.

So: not our bug, not a load-order bug, not a content-def bug. A version skew
between two third-party mods, both active in `ModsConfig.xml`.

## Fix options (the resolution is a mod-list / update choice, owner's call)

1. **Update ModularWeapons2** so its transpiler matches today's SMYH. Only works
   if kaitorisenkou has already pushed a fix post-2026-09-13 (SMYH updated hours
   ago — unlikely yet). Steam re-check / re-subscribe MW2.
2. **Disable Show Me Your Hands.** Purely cosmetic (draws hands on held weapons).
   With SMYH absent, `MW2Mod.IsShowMeYourHandsEnable` is false and MW2 SKIPS the
   patch entirely — crash gone, MW2 otherwise intact. Lowest-cost, safest unblock.
3. **Disable ModularWeapons2.** Removes the broken transpiler, keeps hands-on-
   weapons. Bigger feature loss (weapon modularization at the gunsmith).
4. **Roll SMYH back** to a pre-2026-09-13 build so MW2's transpiler matches again.
   Steam only serves latest; needs a manual/archived DLL. Fragile.

Recommendation: option 2 (drop SMYH) as the immediate unblock — cosmetic loss
only — and keep an eye out for an MW2 update to restore it later. Any of these is
a mod-list change: it takes effect only on the next cold load, and it touches the
owner's curated 590-mod list, so it is carded, not silently applied.

## verify
After the chosen change, a dev quicktest (`start_debug_game_ready` on the
minimal+affected list) generates a map and starting pawns with no
`InvalidProgramException` in `Player.log`. Positive sighting: a pawn actually
spawns holding a weapon.
