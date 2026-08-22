> 🔴 **CORRECTED 2026-08-22 by `FIRE_ARCHER_SPEC_STILL_WRONG_1`. This item is CLOSED and
> what shipped (`d82c5cb`) is right — but the spec below asserted two facts that
> `CUT_TABLE_PAIRED_WRONG_1` had already ruled dead, and a closed item is exactly what a
> later reader copies. Both are struck in place. Do not re-derive either.**

## spec
Ruled in `CUT_DISARMED_VANILLA_KINDS_1`. Our cut removed `Flamebow` (Biotech), the **sole**
carrier of `NeolithicRangedFlame`. ~~which is the only ranged tag on `Tribal_Archer_Fire`
and `Tribal_Hunter_Fire`. Both spawn bare-handed.~~

⛔ **STRUCK: only `Tribal_Archer_Fire` was ever disarmed.** `Tribal_Hunter_Fire` was not, and
`weapon_tag_audit.py` does not list it — it resolves to
`['NeolithicRangedDecent', 'NeolithicRangedFlame']`, a live tag with 6 carriers.
🔑 **The mechanism is published once, in `infrastructure/state/BUILDABLE.md` 9 and 10:
losing a tag's sole carrier disarms a kind ONLY if that kind also blocks inheritance.**
`Tribal_Archer_Fire` carries `<weaponTags Inherit="False">`; `Tribal_Hunter_Fire` does not,
so it appends to `Tribal_Hunter`'s live tag. Cite that, do not re-derive it. Patching
`Tribal_Hunter_Fire` would have widened its pool and lowered its quality band for nothing.

⛔ **`Flamebow` STAYS CUT.** The owner ruled on *mech* weaponry; a neolithic fire-bow is not
that and its cut reads deliberate. These kinds become plain archers — armed, not on fire.

**Add ops to the hand-authored block of**
`src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`, using the exact pattern
`THREE_ANCIENT_KINDS_ARMED_1` already proved there (see the `AncientSoldierBoss` /
`AncientSoldierBossN` / `AncientMallGuards` group at ~line 1863):

- **APPEND** ~~the vanilla tag `NeolithicRanged`~~ **`NeolithicRangedBasic`** to
  `weaponTags` on `Tribal_Archer_Fire` ~~and on `Tribal_Hunter_Fire`~~. Do **not** replace
  `NeolithicRangedFlame` — leave the dead tag beside the live one, exactly as the Ancient
  block does, so the diff stays legible and a later un-cut of `Flamebow` restores the fire
  bows with no further edit.
  🔴 **STRUCK: `NeolithicRanged` has ZERO carriers.** It would have applied cleanly, matched
  its xpath, logged nothing and left the kind bare-handed with this item closed green — the
  silent-success class this project keeps paying for. What shipped is `NeolithicRangedBasic`
  (5 carriers), the tag `Tribal_Archer` itself already carries at the same `weaponMoney`
  80~80.
- ⚠️ **Check per kind whether `weaponTags` is WRITTEN or INHERITED** before choosing the op.
  That is the trap the Ancient block documents: `AncientSoldierBoss` writes its own node and
  takes an `Add`; `AncientSoldierBossN` inherits from `AMBossBase` with no node of its own
  and needs the node created first. A `PatchOperationAdd` against an xpath that matches
  nothing **logs nothing** (`CLAUDE.md`).

## verify
- `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml --defs …`
  passes, and each new op is reported as MATCHING — not merely well-formed.
- `weapon_tag_audit.py` under a FRESH dump no longer lists either kind as tagless.
- `Flamebow` still reads `weaponTags: []`, MarketValue 0 — it must remain cut.

## criteria
CHECK, next load: a `Tribal_Archer_Fire` spawns holding a bow.
