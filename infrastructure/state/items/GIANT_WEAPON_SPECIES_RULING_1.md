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

## 🔴 RULED AND SHIPPED — owner, 2026-08-23
> *"For the sake of interest, please include both the Nine plus seven plausible as a yes."*
> *"Author this all the way to deploy, do not use the queue system."*

**All sixteen are in.** The nine strong and all seven plausible; `RimMandrakeHutt` stays out on the
audit's own reasoning (size yes, giant weapons no). Authored, validated, deployed and pushed at
`b07c3968` — **not handed to BUILD**, on the owner's explicit instruction while at the BENCH.

- 15 upstream defs: `src/Jawa/Jawa_Patches/Patches/GiantWeaponWielders_Ashkarr.xml`, one
  add-if-missing `PatchOperationConditional` each.
- `Jawa_Xeno_Gamorrean` is ours, so the gene went straight into
  `src/Jawa/Jawa_Patches/Defs/XenotypeDefs/GamorreanXenotype.xml`.

**Measured before writing, against the 2026-08-23T22:49:51Z capture (581 mods):** all 16 defNames
exist and are `XenotypeDef`s · `BS_GiantWeaponWielder` exists (`redmattis.bigsmall.core`) · none of
the 16 already carried it · **all 15 declare a literal `<genes>` node and none has a `ParentName`**.
That last check is the one that matters — a patch cannot extend a list a def INHERITS, and it fails
silently when it tries. Proven with a real xpath engine against the mod's own XML: **15/15 target
`<genes>` nodes matched, 15/15 guards matched nothing**, so every Add fires exactly once.

⏳ **Unproven until a load** — defs parse only at startup. After the next one:
`BS_GiantWeaponWielder` in each of the 16 `genes` lists, and a pawn of one of them able to equip
`BS_GiantHammer`.
