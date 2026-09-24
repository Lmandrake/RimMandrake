# SUMP_WALKWAYS_1 — duckboards and the glasswalk

Owner rulings 2026-09-24: the seed, typed — *"Maybe some advanced walkways you can
build that are resistant to the tar but are slippery so you can't walk full speed
ever but don't have to clean them anymore."* Structure and depth then ruled by
question card (decisions taken by card, 2026-09-24): **two tiers**, and **speed
cap + rare harmless pratfalls**.

## spec

1. **Duckboards** (early tier): cheap brindeth-wood plank path (`RM_Brindeth`,
   flora roster §3). Full speed when fresh; fouls with tar (accumulating filth
   slows it until scrubbed); flammable — a real liability in a biome whose
   defense economy is setting the ground on fire. The cleaning treadmill,
   ownable.
2. **Glasswalk** (advanced tier): poured bitumen cooled slick — manufactured
   glass reach (the biome's own precedent, sheet §8). Never fouls, never needs
   cleaning, tar-proof; permanently speed-capped (~80%, never full speed — his
   spec), plus rare slip-and-fall: a pawn moving fast or hauling sometimes goes
   prone, no real damage, just indignity (one small comp).
3. Materials ride the bitumen chain (korveth nodules, dig barrels). Chain ships
   in the mod; 🔴 road re-paving is OUT of campaign scope — owner, typed, same
   sitting: *"It's ok to make the mod to support that. But replacing the
   [road] isn't part of this campaign. There are other mods for that. And this
   one is about the ship."*
4. **Ship-buildable** (`BIOME_SHIP_CONTRIBUTIONS_1`): glasswalk flooring aboard
   the gravship is one of the owner's two named ship gifts from this biome —
   the slippery bitumen deck that never needs cleaning.
5. Both tiers are terrain/floor defs (path cost, filth acceptance, flammability);
   only the pratfall comp is new C#. Feature-gated in Mod Settings.

## verify

Quicktest: duckboards accumulate tar filth and slow; glasswalk accepts no filth
and caps speed; a hauling pawn on glasswalk occasionally slips prone without
injury; glasswalk is placeable on a gravship floor.

## criteria

The build progression is the biome's thesis: cheap-and-tidy is a treadmill; the
real answer is to stop fighting the tar and glaze it.
