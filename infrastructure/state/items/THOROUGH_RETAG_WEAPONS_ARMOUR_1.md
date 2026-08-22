## spec
🔴 **OWNER, 2026-08-22:** *"We need a THOROUGH retag of all the weapons and armor to ensure
they are properly used in the game. Ensuring the appropriate vanilla tags even on custom
items may be useful here, give me advice if that's not so."*

### The advice he asked for: his instinct is right, and it is already the shipped design

There are two directions and they are **not** interchangeable.

| | reach | when it is right |
|---|---|---|
| **item-side** — put vanilla tags on our custom items | **global**. Every kind in the game asking for `AssaultRifle` can now spawn our blaster | when the custom item is meant to REPLACE the vanilla one everywhere |
| **kind-side** — give the KIND a tag that has surviving carriers | **surgical**. That kind only | when one kind is broken and the item set is fine |

✅ **For this campaign the item side is correct, and `WeaponTags_Renormalise.xml` already
argues it in its own header:** *"This re-tags the SURVIVORS into the vanilla vocabulary
instead of un-cutting the weapons. The cut stands; the ladders refill. Fixing it at the
weapon end also fixes every future pawn kind, where patching 49 kinds would not."*
The campaign cut the vanilla firearm line, so **every** vanilla kind is looking for guns
that no longer exist. Fixing that kind-side means patching dozens of kinds and every future
one; item-side fixes it once, for kinds nobody has written yet.
⚠️ Kind-side remains right for the narrow case — a single kind whose tag no item carries.
That is what shipped for `Tribal_Archer_Fire` and the three Ancient kinds, and it stays.

### Where it actually stands, measured 2026-08-22 against `OFFICIAL-2026-08-21T22-44-59Z`

**Weapons — 12 kinds with every tag empty**, three of which today's work should already
have fixed pending a load (`Drone_Sentry`, `Mech_Pikeman`, `Tribal_Archer_Fire`). The other
nine are third-party and each needs a call: `BS_Crossbow*` ×3, `DP_ArtilleryPirate`,
`DP_RocketPirate`, `OuterRim_ImperialTrader`, `VEE_Hunter`, `VEE_TribalHunter`,
`VFEP_Footsoldier`.

**Armour — 8 of 442 kinds**, all third-party, none ours: `AncientMallGuards`,
`AncientSlaughter`, `AncientSoldierBoss`, `AncientSoldierBossN`, `OuterRim_ImperialTrader`,
`OuterRim_RebelJumpTrooper`, `OuterRim_RebelOfficer`, `OuterRim_RebelTrader`.
🔑 **Armour is a LOOK defect, not an arming one.** A kind with no matching apparel tag is
not naked — `apparelRequired` and the general pool still dress it. The symptom is a
stormtrooper in a duster. Do not let it borrow the weapon audit's urgency.

### ⚠️ "36 unclassified guns" is NOT a 36-item backlog

The audit's summary says *"unclassified (left alone): 36"*, which reads like work. Named
with `--list-unclassified` (added 2026-08-22, `03c68efc`), **most of it is the classifier
correctly declining**: `AM_MechanoidMortar`, `AM_SiegebreakerTurret`, `Gun_VulcanTurret`,
`AM_Gun_HellsphereOrbital` (an orbital strike targeter), four grenade defs, three
`VFEP_Warcasket*` guns that only warcasket pawns can hold, and `Gun_ProwlerSpit`, which is
an animal organ. ⛔ **Tagging those into a vanilla ladder would hand an ordinary raider an
orbital strike.** The genuinely arguable few are `Gun_Slugthrower`, `Gun_Spiner`,
`RBM_Bullslinger` and `RN2SWGun_EWebMounted_GPMG`.

## 🔴 THE BLOCKER, AND IT IS WHY THERE IS NO SINGLE COMMAND YET
`weapon_tag_audit.py --emit-patch` **cannot regenerate the patch from the current dump**,
and this is by design rather than a bug: the dump is captured with `Jawa_Patches` ALREADY
APPLIED, so every weapon the last run tagged reads as already-tagged and drops out. A
regenerate emits **9 operations against the 151 on disk**. The tool now refuses and names
the 142 it would lose.
⇒ **A real retag needs a def dump captured with `Jawa_Patches` DISABLED**, which is a
load-window action and the first thing to do at the next shutdown.

## verify
With a Jawa_Patches-disabled dump in hand: `--emit-patch` writes without refusing, the op
count does not shrink, the hand-authored block survives verbatim, and `validate_patch
--defs --live` reports every op MATCHING.

## criteria
`weapon_tag_audit.py` reports 0 kinds with every weapon tag empty among the kinds we own,
and every remaining unclassified gun is unclassified **on purpose**, with the reason
recorded.
