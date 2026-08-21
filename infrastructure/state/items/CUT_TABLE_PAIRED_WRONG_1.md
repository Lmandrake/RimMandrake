## spec
🔴 **Two facts in `infrastructure/state/items/CUT_DISARMED_VANILLA_KINDS_1.md` are wrong,
and BUILD could not correct them — the file belongs to DECIDE and the seat guard refuses
the edit.** Both were measured 2026-08-21 against the 22:44:59Z dump, which
`weapon_tag_audit.py` reports as matching the live 578-mod list. Evidence:
`observed/verify/2026-08-21_mech_uncut_and_fire_archers.md`.

The shipped fix (`FIRE_ARCHERS_GET_BOWS_1`, `d82c5cb`) already went out against the
CORRECTED facts, so the code is right and only the doc is wrong. ⚠️ **That is the
dangerous state** — the next reader deriving from the table will re-make both errors.

**1. `NeolithicRanged` is not a tag in this game. Zero carriers.**
Line ~78 prescribes *"APPEND `NeolithicRanged`"*. It would have applied cleanly, matched
its xpath, logged nothing, and left the kind bare-handed with the item closed green. The
real tags are `NeolithicRangedBasic` (5 carriers), `NeolithicRangedDecent` (6),
`NeolithicRangedHeavy` (3). What shipped is `NeolithicRangedBasic` — the tag the kind's
own base `Tribal_Archer` carries, at the same `weaponMoney` 80~80.

**2. `Tribal_Hunter_Fire` is not disarmed and was not patched.**
Lines ~26 and ~78 both pair it with `Tribal_Archer_Fire`. It resolves to
`['NeolithicRangedDecent', 'NeolithicRangedFlame']`, and `weapon_tag_audit.py` does not
list it among the 12 tagless kinds. Biotech gives it `weaponTags` with **no**
`Inherit="False"`, so RimWorld list inheritance appends to `Tribal_Hunter`'s live tag.
`Tribal_Archer_Fire` is the one that carries `Inherit="False"` — which is precisely why
it is the only one left holding nothing.

🔑 **The generalisation, already published as `BUILDABLE.md` 9 and 10:** losing a tag's
sole carrier disarms a kind ONLY if that kind also blocks inheritance. A tag table pairs
kinds that a tag table cannot pair. Read the `Inherit` attribute in the source def.

## verify
`CUT_DISARMED_VANILLA_KINDS_1.md` no longer prescribes `NeolithicRanged` and no longer
lists `Tribal_Hunter_Fire` as disarmed — or carries a correction line at its head saying
so. Any other file naming either fact is corrected in the same commit.

## criteria
A reader arriving at that table cold cannot re-derive either error.
