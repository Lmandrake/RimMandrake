## spec
`src/RimMandrake/Utils/gen_pawnkind_roster.py` writes
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` and the file's header says
so. **The file has been hand-edited since and the generator has never heard of any of it.**

🔴 **MEASURED 2026-08-23 by running it.** A regeneration reverts, among other things, the
**stormtrooper lockdown** — the owner's hard requirement, built earlier the same day:

| field | in the file (correct) | what regenerating writes |
|---|---|---|
| `weaponMoney` | `950~1150` | `650~780` — **below the 906 that every ORImperialStandard rifle costs**, so the roll always fell back to `ORImperialLight`, which is PISTOLS |
| `apparelMoney` | `900~1100` | `500~600` |
| weapon tags | `ORImperialLight` removed | `ORImperialLight` back in |
| `apparelTags` | `ImperialStormtrooper` (3 carriers) | `ImperialApparel` (**21** carriers — Snowtrooper, Scout, Death Trooper, ISB) |
| `forceNormalGearQuality`, `inventoryOptions`, `apparelDisallowTags` | present | **deleted** |

It reports success. Nothing warns. This is the same shape as `RACES_GENERATOR_DIVERGED_1`
and it is the second generator in this repo found lying in its own header in one day.

⛔ **DO NOT RUN `gen_pawnkind_roster.py --write` UNTIL THIS IS SETTLED.** It reverts an owner
requirement silently.

## Decide one of three, then do it
1. **Generator wins.** Port the stormtrooper lockdown and every other hand edit into the
   generator, regenerate, and diff until the output is byte-identical to the current file.
   Then the header is true again.
2. **File wins.** Delete the "GENERATED / do not hand-edit" header, retire the write path,
   and own the XML by hand. Cheapest and honest.
3. **Split.** Generator emits a base file; a patch carries the hand decisions — which is
   what already happens for the droid gender rule (see below).

## What was done instead, and why it is not a workaround
`DROID_KINDS_MISS_FIXEDGENDER_1` needed `<fixedGender>Male</fixedGender>` on four kinds in
this file. The rule belongs in the generator; it went into
`src/Jawa/Jawa_Patches/Patches/DroidFemaleTexture_Fix.xml` instead, which already owns the
same rule for Droid Depot's own seven kinds. ✅ **Those four ops carry `[not(fixedGender)]`,
so they become no-ops the moment the generator emits the field** — settling this item costs
nothing and breaks nothing.

## verify
`python3 src/RimMandrake/Utils/gen_pawnkind_roster.py` then
`git diff --stat src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` -> **empty**.
Until that is empty, the header is false.

## Watch out
🔑 **Back up before running ANY generator in this repo.** Three were touched on 2026-08-23:
`cast_to_xml.py` was CLEAN (a full `--write` over 12 files changed only the intended blocks),
`gen_races_mod.py` REFUSES to write, and this one silently reverted an owner requirement. The
only cheap way to know which you have is `cp` the output, run it, `diff`, and restore.

## criteria
- [ ] One of the three routes is chosen and written down in the file's own header.
- [ ] If (1): `gen_pawnkind_roster.py` then `git diff` on `JawaFactionRoster.xml` is EMPTY.
- [ ] If (2): the "GENERATED / do not hand-edit" header is gone and the write path is retired.
- [ ] The stormtrooper lockdown's five fields survive whatever is chosen — verified by reading
      them back, not by the generator reporting success.
