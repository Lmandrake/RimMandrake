## spec

🔴 **OWNER, 2026-08-22, verbatim:** *"strike the two docs. The cheap end should be bows and
knives for anyone... but it's ok if you make them cheaper so that nobody just spawns with
fists, that's a bit silly."*

**Two rulings in one sentence, and the second is the one that changes work.**

**1. The floor is NEOLITHIC, and it is universal.** The eight vanilla industrial guns stay
cut. The bottom of the ladder is bows and knives — *"for anyone"*, so this is not a tribal
carve-out: any faction, any kind, any culture may arrive with a bow or a knife. Outer Rim's
cheap end sits above it. This closes the ambiguity in *"vanilla low-tech"* that made two
docs read as arguments against the gun cut for three weeks.

**2. 🔑 A bare-handed pawn is fixed by CHEAPENING the pool, never by raising `weaponMoney`.**
This reverses the standing proposal in several open items and is the executable half.

⛔ **What this kills.** `CHEAPEST_WEAPON_IS_ABSURD_1` correctly refused
`first_light.py`'s advice to raise `Town_Trader`/`Hunter`/`Scavenger` budgets to 340 so they
could afford `Gun_IncendiaryLauncher`; the owner has now ruled the general case. Arming a
hunter with an incendiary launcher because the budget was raised to reach it is the failure,
not the fix. **Do not raise a `weaponMoney` max to clear a bare-handed kind.** Lowering a
weapon's `MarketValue`, or retagging a cheap neolithic weapon into the kind's tag set, is
the sanctioned move.

✅ **What this does NOT change.** It is not licence to cheapen mid or high tier gear —
blasters, bowcasters, legendaries keep their prices; scarcity is the point. It does not
re-open the vanilla gun cut. It does not touch `weaponMoney.min` in either direction
(`BARE_HANDS_REMEASURE_AFTER_LOAD_1` already refuted the low-roll theory and that refutation
stands).

**What DECIDE owes:** the roster — which defs are "bows and knives" across the 578-mod set,
what each should cost, and which pawnkind tags must reach them. Then BUILD patches
`MarketValue` / `weaponTags`. The measured victim list already exists and should be the
verify set, not re-derived:
`sixteen-authored-role-kinds-spawn-bare-handed-on-weaponmoney-7c31a9` (16 `Jawa_*` role
kinds, 5/5 bare live), `neolithicmeleedecent-is-empty-so-every-tribal-spawns-bare-handed-9c02d5`
(`NeolithicMeleeDecent` resolves to the empty set, taking every `TribalWarriorBase` kind with
it), `CHEAPEST_WEAPON_IS_ABSURD_1` (17 kinds priced out).

⚠️ **Three of the sixteen have a defect price cannot fix:** `Jawa_Droid_Leader`,
`Jawa_Droid_Specialist` and `Jawa_TradeMoot_Specialist` carry **no `weaponTags` field at
all**, and Droid Grunt/Heavy carry `weaponMoney 0-0`, which no price satisfies. Those need a
tag and a range, not a discount — do not report them fixed by a cheapening pass.

## verify

The pass condition is a live census, not a price table:

    spawn every affected kind 5x through the bridge, read equipment back with jawa/pawn_get

**PASS = no kind is bare 5/5**, and no kind that was armed before is now carrying something
absurd for its role. ⛔ A dump-derived affordability check (`weapon_affordability.py`) is
NOT sufficient on its own — it read *"48 always arm, 0 never"* while CHECK watched 23 of 54
kinds field a bare pawn across 270 spawns. The live spawn is the authority.

## criteria

- [ ] A roster exists naming every def that counts as the neolithic floor, with its price.
- [ ] No `weaponMoney` **max** was raised anywhere in the change to clear a bare kind.
- [ ] The three tagless Droid/TradeMoot kinds are handled as a tag defect, reported separately.
- [ ] `design/RimMandrake/Custom_World.md` and `design/Jawa/mods/required_mods.md` say
      "bows and knives", matching the owner's words rather than "bows and clubs".
- [ ] Live 5x spawn census: zero kinds bare 5/5.

## watch out

- `MarketValue` is a `statBases` entry and several tagged weapons **report none in the dump**
  (inherited from a parent the dump does not resolve) — those read UNMEASURED, not cheap.
- Cheapening a weapon changes what traders stock and what a raid drops, not only what spawns.
- The floor weapons must be reachable by TAG as well as by price; a discount on a def no
  kind's tags select changes nothing and reports success.
