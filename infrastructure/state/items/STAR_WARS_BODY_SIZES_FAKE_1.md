## spec
🔴 **Every Star Wars species in this game is mechanically the same size, and nothing
records that as a decision.**

Measured 2026-08-22 across all 70 `RimMandrake*` xenotypes: every
`RimMandrake_BodySizeGene_big` / `_bigger` / `_biggest` / `_small` / `_smaller` writes
`SM_Cosmetic_BodySizeOffset`, and Herglic's `Outland_BodyScale_Large` is the same kind of
gene from Outland Genetics. **The Cosmetic stats scale the sprite and nothing else.**

⇒ To health scale, carrying capacity, food consumption, melee and every other mechanic, a
Wookiee, a Hutt, a Gamorrean, an Ewok and a Jawa are all bodySize **1.0**.

The mechanical stat one word away is `SM_BodySizeOffset`, described by its own StatDef as
*"Offsets the pawn's size by this amount. This affects a variety of mechanics."*
`BS_LargeFrame` (+0.4) is the gene that reads as "big and tall" without turning a species
into an ogre.

⚠️ **This may well be deliberate**, and identical mechanical size is a defensible balance
call. It is filed because nothing says so, and the gene labels ("Big Frame", "Biggest
Frame") read as if they do something they do not.

⛔ **This is NOT the weapon question.** Body size does not open the warcasket gate at all,
and the giant gate wants `> 1.99`, which no Star Wars species should have. See
`GIANT_WEAPON_SPECIES_RULING_1`.

## verify
`python3 src/RimMandrake/Utils/xenotype_size_audit.py xenotypes` — every `RimMandrake*`
row reads `1.0` with a `cosmetic:` note.

## criteria
The owner rules either "cosmetic is correct, say so in the gene descriptions" or "these
species get real sizes", and names which.

## notes
Filed by BUILD 2026-08-22 out of `BIG_WEAPON_XENOTYPE_AUDIT_1`.
Full evidence: `infrastructure/state/evidence/big_weapon_xenotype_audit_2026-08-22.md` §2.

## 🔴 DROP THIS ITEM — the premise was stale, 2026-08-22

`src/Jawa/Jawa_Patches/Patches/BodySizeIsReal.xml` already did this, earlier the same day,
on the owner's own instruction — committed `46bba032`, revised `216d0bb6`, deployed and
byte-identical to the game copy. It swaps **27** Star Wars xenotypes off the cosmetic genes
onto Big and Small's real frames: 7 × `HalfJotunFrame` (1.75), 15 × `BS_LargeFrame` (1.40),
4 × `BS_SmallFrame` (0.65), 1 × `BS_RabbitFrame` (0.40).

The audit that filed this read a def dump captured **2026-08-21T22:44** and never looked at
the tree. BUILD cannot drop an item owned by OWNER, so it is left standing with this note:

```
python3 src/RimMandrake/rimflow/cli.py drop STAR_WARS_BODY_SIZES_FAKE_1 --seat OWNER --reason "already done by BodySizeIsReal.xml"
```

⇒ What genuinely remains is the rungs that file could not reach, and that is
`RimMandrake_BodySizeGene_*` still writing the cosmetic stat for the species it left alone.
