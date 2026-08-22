## spec
🔴 **Owner's call: which Star Wars species may wield giant and warcasket weapons.**

The mechanism is settled — see
`infrastructure/state/evidence/big_weapon_xenotype_audit_2026-08-22.md`. The short of it:
adding `BS_GiantWeaponWielder` to a xenotype's `genes` list grants the `BS_Giant` trait,
which opens **both** gates (all 23 giant weapons and all 15 warcasket weapons) and
**changes no body size at all**. It costs `biostatCpx 1`, `biostatMet 0`.

⛔ **Do not reach for a size gene to do this.** The size route needs `totalSize > 1.99`,
which is ogre scale — twice a human's mass. Right for a Jotun, wrong for a Wookiee.

**Nine STRONG candidates**, canonically large and built to fight:

`RimMandrakeWookiee` · `RimMandrakeGamorrean` · `Jawa_Xeno_Gamorrean` ·
`RimMandrakeHerglic` · `RimMandrakeTrandoshan` · `RimMandrakeTogorian` ·
`RimMandrakeLasat` · `RimMandrakeFeeorin` · `RimMandrakeSithMassassi`

**Seven PLAUSIBLE** — the owner could go either way: `RimMandrakeAqualish`,
`RimMandrakeCathar`, `RimMandrakeChagrian`, `RimMandrakeGungan`, `RimMandrakeKaleesh`,
`RimMandrakeKlatoonian`, `RimMandrakeNelvaanian`.

**One SPECIAL:** `RimMandrakeHutt` — canonically the largest species we field, so a size
gene would be right, but a sessile slug with vestigial arms cannot swing a giant hammer.
Size yes, giant weapons no.

The full 139-row table, with a reason on every row, is section 4 of the report, and
regenerates from
`python3 src/RimMandrake/Utils/xenotype_size_audit.py shortlist --markdown`.

## verify
`jawa/get_defs` reports `BS_GiantWeaponWielder` in the `genes` list of each xenotype the
owner rules in, and a pawn of that xenotype can equip `BS_GiantHammer` in game.

## criteria
The owner has named the species. BUILD then edits one line per xenotype.

## notes
Filed by BUILD 2026-08-22 out of `BIG_WEAPON_XENOTYPE_AUDIT_1`.
