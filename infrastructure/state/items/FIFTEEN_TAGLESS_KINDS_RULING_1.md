## spec
`weapon_tag_audit.py`, run 2026-08-21 against a dump captured 08:20:20Z that MATCHES the
live 578-mod list, reports **15 pawn kinds whose every weapon tag resolves to an empty
set**. Such a kind spawns bare-handed with no red error and nothing in `Player.log`.
Independently confirmed by the owner's 01:23 `first_light` run against the live process,
which found the same 15 among 710 tool-using kinds.

🔑 **THE CUT IS NOT THE CAUSE, and that is the whole reason this needs a ruling rather
than a fix.** The audit's own headline reads `weapon tags in the dump: 390 — emptied by
the cut: 0`. Our cherrypick emptied NONE of these. They were already empty in this mod
set, so `WeaponTags_Renormalise.xml`'s remedy — re-tag the survivors into the vanilla
vocabulary, which repaired 49 kinds — has nothing to work with here: the audit
classified **0** of the 36 untagged survivors into any of these roles.

**The 15, grouped by what they probably are:**

⚠️ **Probably DELIBERATE upstream, and a fix would be wrong:**
  `DP_ArtilleryPirate` · `DP_RocketPirate` — tags are literally `DP_CannonNoEquipTag`
  and `DP_RocketNoEquipTag`. The names say the weapon is not equipped from a tag pool.
  `VFEP_Footsoldier` — `WarcasketBasic`; VFE-Pirates equips warcaskets by its own system.
  `Mech_Pikeman` · `Drone_Sentry` — mechs and drones normally carry built-in weapons.

🔴 **Probably GENUINE — a raider or hunter that will arrive with empty hands:**
  `BS_Crossbowman` · `BS_CrossbowDvergr` · `BS_DvergrTraditionalist` (three tags each,
  all empty: `BS_CrossbowTag`, `DankPyon_Arbalest`, `VFEM2_Arbalest` — this reads like a
  mod expecting a crossbow mod we do not have)
  `AncientSoldierBoss` · `AncientSoldierBossN` (`AMHP`) · `AncientMallGuards` (`PKM`)
  `Tribal_Archer_Fire` (`NeolithicRangedFlame`) · `VEE_Hunter` · `VEE_TribalHunter`
  `OuterRim_ImperialTrader` (`ORImperialOfficer`)

**THE RULING NEEDED, and it is scope, not mechanism:** do we repair other mods' pawn
kinds at all? BUILD can do it — the mechanism is proven, it is more `PatchOperationAdd`
ops in `WeaponTags_Renormalise.xml` mapping each empty tag onto a surviving weapon of
the right role — but choosing WHICH weapon a Blackstar crossbowman or an Ancient boss
should carry is a content decision, and picking it silently would put weapons in raiders'
hands that nobody chose.
⛔ Do not rule "fix all 15": at least five are upstream-deliberate and arming them would
break the mod's own design.

## verify
after whatever DECIDE rules, `weapon_tag_audit.py` reports a kinds-with-every-tag-empty
list containing only the kinds DECIDE explicitly declared out of scope, by name.

## criteria
DECIDE's, and it is a written ruling naming which of the 15 are in scope and what role
of weapon each in-scope kind should receive. No artefact is owed by this item itself.

## notes
BUILD measured this and stopped at the scope line deliberately. The instrument is
`python3 src/RimMandrake/Utils/weapon_tag_audit.py`; it REFUSES to report unless the
dump's mod set matches `ModsConfig.xml`, and it did match at the time of writing.
⚠️ `first_light`'s version of this check EXCLUDES kinds with no `weaponTags` field at
all as deliberately-unarmed civilians (291 of them), so a combat role that loses its
tags entirely will read clean there. The audit tool does not have that blind spot.
