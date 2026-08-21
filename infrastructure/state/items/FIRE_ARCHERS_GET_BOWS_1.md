## spec
Ruled in `CUT_DISARMED_VANILLA_KINDS_1`. Our cut removed `Flamebow` (Biotech), the **sole**
carrier of `NeolithicRangedFlame`, which is the only ranged tag on `Tribal_Archer_Fire` and
`Tribal_Hunter_Fire`. Both spawn bare-handed.

⛔ **`Flamebow` STAYS CUT.** The owner ruled on *mech* weaponry; a neolithic fire-bow is not
that and its cut reads deliberate. These kinds become plain archers — armed, not on fire.

**Add ops to the hand-authored block of**
`src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`, using the exact pattern
`THREE_ANCIENT_KINDS_ARMED_1` already proved there (see the `AncientSoldierBoss` /
`AncientSoldierBossN` / `AncientMallGuards` group at ~line 1863):

- **APPEND** the vanilla tag `NeolithicRanged` to `weaponTags` on `Tribal_Archer_Fire`
  and on `Tribal_Hunter_Fire`. Do **not** replace `NeolithicRangedFlame` — leave the dead
  tag beside the live one, exactly as the Ancient block does, so the diff stays legible and
  a later un-cut of `Flamebow` restores the fire bows with no further edit.
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
