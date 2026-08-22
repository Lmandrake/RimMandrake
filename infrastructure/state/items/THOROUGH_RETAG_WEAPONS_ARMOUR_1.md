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

---

# 🔴 SCOPE REWRITTEN 2026-08-22 ON THE OWNER'S RULING — this is one job, not "add tags to the tagless"

Verbatim: *"We don't just need to add tags to the tagless. We need to A) rationalize certain
tags to ensure that every weapon and faction/pawntype that prefers them can select them
properly can do so, B) ensure that all tags are applied to all appropriate weapons (e.g. all
bows no matter what they're called are considered bows), and C) ensure that previously
'exotic' weapons like Blasters are available to everyone as the new 'Vanilla replacement'
they were intended to be."*

## The finding both seats reached independently, and it reframes everything

CHECK measured it live (`observed/2026-08-21/armed_sweep_48/README.md`) and BUILD measured it
off the config the same evening. Same answer, **27 of 27**:

**The stripped weapons are the OWNER'S OWN CURATION.** Cherry Picker is C#/Harmony — at load
it NEUTERS a cut def rather than deleting it, and part of neutering a weapon is emptying its
`weaponTags`. Every one of the 27 measured-stripped defs is in the kill list; neither of the
two measured-intact is. ⛔ **Nobody undoes the cut.**

    Artillery_AutoMortar  Artillery_Mortar  Bow_Great  Bow_Recurve  Bow_Short  Flamebow
    Gun_AssaultRifle  Gun_Autopistol  Gun_ChainShotgun  Gun_HeavySMG  Gun_HellcatRifle
    Gun_Incinerator  Gun_LMG  Gun_MachinePistol  Gun_Minigun  Gun_Needle  Gun_PumpShotgun
    Gun_Revolver  Gun_Scattergun  Gun_SniperRifle  MeleeWeapon_Axe  MeleeWeapon_Gladius
    MeleeWeapon_Ikwa  MeleeWeapon_LongSword  MeleeWeapon_Mace  Pila

🔑 **Read the pattern: every basic gun, ALL THREE BOWS, and the entire medieval melee set.**
That is the starting kit of every low-tech and mid-tech faction in the campaign — which is
precisely why (C) is not a nicety. The replacements were always meant to carry the vanilla
vocabulary; only the guns ever got it.

🪤 **A Cherry Picker cut is invisible to every XML-shaped search.** CHECK swept 1,437 XML
files across 1,254 workshop mods for something targeting these defs and found nothing,
*because there is nothing to find*. Read the kill list first.

## The measurement that scopes the job

**The vanilla tag vocabulary is 60 tags**, extracted from every `<weaponTags>` block Core and
the DLCs ship. Against the live 578-mod capture:

**(A) — 5 vanilla tags have ZERO surviving carriers.** A pawn kind asking for one gets an
empty set and spawns bare, silently.

| tag | status |
|---|---|
| `MechanoidGunLongRange` | ✅ fixed pending a load — `Gun_Needle` un-cut (`143ee4e`) |
| `SentryDroneGunShortRange` | ✅ fixed pending a load — `Gun_Scattergun` un-cut |
| `NeolithicRangedFlame` | ⛔ deliberate — `Flamebow` stays cut; the archer was re-tagged instead |
| `Artillery_BaseDestroyer` | 🔴 **OPEN** — both carriers cut |
| `Flamethrower` | 🔴 **OPEN** — all three carriers cut |

**⚠️ And 28 more vanilla tags are down to 1–2 carriers** — `Axe` 1, `LongSword` 1,
`PumpShotgun` 2, `Neolithic` 2. One more cut anywhere and each becomes a silent hole. That
list is the fragility map and belongs in the same pass.

**(B)/(C) — 166 surviving weapons speak NONE of the 60-tag vocabulary.**
⚠️ **166 is a CEILING, not a work list, and most of it is correct.** By `techLevel`:
Ultra 65 · Spacer 56 · Industrial 28 · Undefined 8 · Archotech 6 · Medieval 3. The bulk is
deliberately locked to something: `AM_*` mechanoid-only, `BS_*Giant*` giant xenotypes,
`AG_Forsaken*` one xenotype, `*_Persona` quest rewards, `Proj_Chunk_*` Minotaur throwables,
`HerculeanWeapon`. ⇒ **Triage by FAMILY, not by weapon.** The question per family is "should
this circulate generally?", and for most the answer is no.

⛔ **BUILD nearly reported a wrong number here.** A first pass used a hand-written set of
"bow-ish" tags and flagged 11 kinds, of which `AG_ForsakenBow` and `BS_GiantPrimitiveBow`
were false positives — they carry `NeolithicRangedBasic` but their `weaponClasses` says
Melee, so a class-based split mislabels them. The vocabulary must be MEASURED off Core/DLC
XML, never hand-listed.

## What is NOT blocked
🔑 **No re-dump is needed, and the earlier claim that one was is withdrawn.** The owner:
*"If we know what the tags are now, we should be able to just add them."* Correct. The patch
file records all **151** weapons it already tags; the current dump gives the **36** still
untagged. `151 + 36` reconstructs the whole population. A re-dump is needed only to
REGENERATE the file — and regenerating would re-derive tags for 151 working operations
through a median split, which is churn we do not want. ⇒ **EXTEND, never regenerate.**

## The armour half
823 apparel tags; 442 kinds ask for apparel by tag; **8 have no surviving carrier for any of
theirs** — all third-party, none ours. `apparel_tag_audit.py` (new, `432cf408`) is the
instrument. 🔑 Severity is different and must not be borrowed from the weapon side: a kind
with no matching apparel tag is **not naked**, because `apparelRequired` and the general pool
still dress it. The symptom is a faction losing its LOOK.
