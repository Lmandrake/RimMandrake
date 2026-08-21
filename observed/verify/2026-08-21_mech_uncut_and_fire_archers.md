# Verify evidence — MECH_WEAPONS_UNCUT_1 · FIRE_ARCHERS_GET_BOWS_1

BUILD, 2026-08-21. Dump used throughout: the 22:44:59Z capture, which
`weapon_tag_audit.py` reports as **matching the live list (578 mods)** — the items'
"one mod stale in both directions" warning is out of date.

## MECH_WEAPONS_UNCUT_1 — offline PASS, two clauses load-gated

Live file
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`
(backed up first to `…Mod_CherryPicker.xml.bak-20260821-mechuncut`, which still holds
both entries).

```
before          li=1349  Gun_Needle=1  Gun_Scattergun=1  Flamebow=1
after           li=1347  Gun_Needle=0  Gun_Scattergun=0  Flamebow=1
re-read (game UP, per the item's clobber warning)
                li=1347  Gun_Needle=0  Gun_Scattergun=0  Flamebow=1
```

Freeze copy `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` edited the
same way; `diff` against the live file after `tr -d '\r'` is **empty**. The change is
recorded in that folder's `README.md` under "Amended 2026-08-21".

⚠️ **UNMEASURED, and it cannot be otherwise until a load:** the item's clauses 3 and 4
(the next dump showing `Gun_Needle` / `Gun_Scattergun` with non-empty `weaponTags`, and
`weapon_tag_audit.py` no longer listing `Mech_Pikeman` / `Drone_Sentry`). The current
dump predates the edit and still reads:

```
Gun_Needle      weaponTags= []
Gun_Scattergun  weaponTags= []
Flamebow        weaponTags= []      <- correct, stays cut
```

Cherry Picker's list is applied at load, so this is the neutering signature persisting
from the pre-edit run, not a failure. Re-take the dump on the next load.

## FIRE_ARCHERS_GET_BOWS_1 — offline PASS, and the spec was wrong twice

Measured from the 22:44 dump (post-inheritance, post-patch):

```
Tribal_Archer     weaponTags= ['NeolithicRangedBasic']                        money 80~80
Tribal_Hunter     weaponTags= ['NeolithicRangedDecent']                       money 100~100
Tribal_Archer_Fire weaponTags= ['NeolithicRangedFlame']                       money 80~80
Tribal_Hunter_Fire weaponTags= ['NeolithicRangedDecent','NeolithicRangedFlame'] money 100~100

tag carriers in the dump:
  NeolithicRanged        0     <- the tag the spec named. Does not exist.
  NeolithicRangedBasic   5
  NeolithicRangedDecent  6
  NeolithicRangedFlame   0     <- Flamebow was its sole carrier
```

`weapon_tag_audit.py` lists **`Tribal_Archer_Fire`** among the 12 fully-tagless kinds.
It does **not** list `Tribal_Hunter_Fire`.

**Two corrections, both applied:**

1. **`Tribal_Hunter_Fire` is not disarmed and was not patched.** Biotech's
   `PawnKinds_Impid.xml` gives it `weaponTags` with **no** `Inherit="False"`, so RimWorld
   list inheritance appends its `NeolithicRangedFlame` to the parent's live
   `NeolithicRangedDecent`. `Tribal_Archer_Fire` is the one that carries
   `Inherit="False"` — which is exactly why it is the only one that ends up with nothing.
   Adding a tag to the hunter would have widened its pool and lowered its quality band.
2. **The tag appended is `NeolithicRangedBasic`, not `NeolithicRanged`.** The latter has
   zero carriers; the op would have applied cleanly, logged nothing, and left the kind
   bare-handed with the item closed. `NeolithicRangedBasic` is what the kind's own base
   `Tribal_Archer` carries, at the same `weaponMoney` 80~80 — the sibling logic the
   `THREE_ANCIENT_KINDS_ARMED_1` block already documents.

`NeolithicRangedFlame` is **kept beside** the new tag, so un-cutting `Flamebow` later
restores the fire bows with no further edit. `Flamebow` stays cut.

### validate_patch.py — the new op is MATCHING, not merely well-formed

Run against `--defs` (RimWorld Data + workshop 294100 + RimWorld/Mods) and
`--live` (the 22:44 DefDump):

```
info    Operation[153] > match (PatchOperationConditional): 1 match(es)  in Biotech: PawnKinds_Impid.xml(1)
info    Operation[153] > match > match (PatchOperationAdd): 1 match(es)  in Biotech: PawnKinds_Impid.xml(1)
info    Operation[153] > match > nomatch (PatchOperationAdd): 1 match(es)  in Biotech: PawnKinds_Impid.xml(1)

OK - 0 errors, 155 warning(s)
```

The def writes its own `weaponTags` node, so the `<match>` branch is the one that fires.

Deployed: `deploy_custom_mods.py --mod Jawa_Patches --apply` → 1 file, **VERIFIED in sync**.

⚠️ **UNMEASURED until a load:** the audit under a fresh dump no longer listing
`Tribal_Archer_Fire`.
