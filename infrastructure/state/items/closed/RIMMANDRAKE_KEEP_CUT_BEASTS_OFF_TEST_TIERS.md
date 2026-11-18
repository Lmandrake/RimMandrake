## spec

No test tier may load a creature the owner's full mod list cuts. Today every modset_builder tier loads Core and the
DLC without Cherry Picker, so the vanilla beasts the full list removes (VANILLA_BEAST_EXCISION_1) come back on every
test load. On tier `evening_20261113` that put a vanilla Thrumbo in the Explosive Knockback proof scene `mass_and_power`.

His words (owner, at the game, 2026-11-13 ~10:30 PM PST, looking at that scene): "WTF is that Thrumbo creature?! We
shouldn't have anything called a Thrumbo in the game anymore, and that is a HIDEOUS image. I don't even know what it is!"

**Acceptance test:** `python3 src/RimMandrake/Utils/tier_cut_creature_check.py` exits 0 (every tier clean). It reads the
SHIP cut list (`infrastructure/state/cherrypicker/CherryPicker.SHIP.xml`), the newest DefDump capture's `animals.json`
and every `modset_builder.TIERS` entry resolved against the installed mods. A tier passes when it carries Cherry Picker
or loads no mod that defines a cut creature.
Fails today [measured 2026-11-13]: exit 1, 60 of 60 tiers FAIL; `evening_20261113` loads 66 cut creatures (128 cut
creatures on the SHIP list, defined by 5 mods: Core and DLC).

## What was found (2026-11-13, measured)

- On the evening tier the creature is vanilla `Thrumbo` (label "thrumbo"; no def patch changes it). Its picture was
  not vanilla: `src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Thrumbo/Thrumbo_{east,north,south}.png`
  sat at vanilla's texPath and reskinned it. Those PNGs are the first RUT_Vhessk render (artpipe job
  `dregen_RUT_Vhessk_Thrumbo_v1`, installed c56af2e075 2026-10-19 by the bulk accept-for-now). RUT_Vhessk moved to its own
  texPath `Things/Pawn/Animal/Vhessk/Vhessk` on 2026-10-26 (3e37d884f2), which left the Thrumbo files orphaned. They
  were retired under this item.
- On the full list Thrumbo is cut (live Cherry Picker settings and SHIP; also `IncidentDef/ThrumboPasses`).
- Explosive Knockback's proof code also named vanilla beasts (Rat, Muffalo, Thrumbo, plus an any-animal search for
  `body_override`). That was fixed alongside this item, and then reworked (Conductor, 2026-11-13: Explosive Knockback is
  a franchise-free RM_ mod, so it names no creature, canon or vanilla). The scenes now choose their animals BY MASS
  from the loaded animal kinds (`RM_KnockbackProof.ByMass`): the lightest, the heaviest under 150 kg, one of 160-200 kg
  and one of 220-260 kg, non-Ludeon kinds first, then mass, then defName; an empty band throws, naming the band in kg.
  Each result row prints the chosen label and its measured mass. The `explosiveknockback` tier loads
  `mandrake.rsw.swbestiary` so those picks are our animals; on a tier with no non-Ludeon animal in a band the
  vanilla one is picked, which is exactly this item's gap. The mod's settings and About text name no creature.
- Not fixed here: `Things/Pawn/Animal/Thrumbo/Dessicated_Thrumbo` is vanilla art reused as the desiccated graphic of
  RUT_Vhessk, RM_Dorrak and RM_MycoidColossus (no player-facing "Thrumbo" name).

## Options (not decided here)

1. Add Cherry Picker to every test tier, so the live cut list applies (it is per user, so the SHIP list must be the
   live one when a test load runs).
2. Have `modset_builder --apply` refuse a tier that loads a cut creature without Cherry Picker.
Either has to keep the 22-second minimal loads fast; measure Cherry Picker's load cost before picking.
