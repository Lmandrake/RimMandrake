## spec

🔴 **DECIDE's ruling, 2026-08-22, discharging `WEAPON_FLOOR_BOWS_KNIVES_1`.** Full reasoning
and the measured roster: `design/Jawa/mods/neolithic_floor.md`, roster CSV
`design/Jawa/mods/neolithic_floor_roster.csv`.

The owner's floor is *"bows and knives for anyone"*. Four of the seven cut neolithic weapons
went out as collateral of the vanilla **industrial gun** cut and must come back.

**Un-cut these four, by deleting their lines from the LIVE Cherry Picker config**
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`:

```
<li>ThingDef/Bow_Recurve</li>          NeolithicRangedDecent — the ONLY vanilla carrier
<li>ThingDef/Bow_Great</li>            NeolithicRangedHeavy + NeolithicRangedChief — only vanilla carrier of Chief
<li>ThingDef/Pila</li>                 NeolithicRangedHeavy
<li>ThingDef/MeleeWeapon_Ikwa</li>     a knife by any reading of the ruling
```

⛔ **These three STAY cut — do not touch them:** `Bow_Great_Unique` (Odyssey quest-unique),
`MA_VerdantBow`, `VWE_Throwing_Rocks`.

⛔ **This does NOT re-open the eight vanilla INDUSTRIAL guns.** They stay cut, on the
owner's ruling. Nothing here adds a mod or changes mid/high tier pricing.

**Why it matters, measured:** with `Bow_Recurve` cut, `NeolithicRangedDecent` resolves to six
defs and not one of them is a bow — `NerveSpiker`, `AG_ForsakenBow`, `BMT_ThrumbungusShroom`,
`BMT_BlastSpore`, `BS_GiantPrimitiveBow`, `BS_OgreThrowinRock`. A tribal hunter asking for a
decent neolithic ranged weapon is handed a mushroom or an ogre's rock.

🔑 **No retag patch is needed for the four.** Core already gives them their tags
(`Data/Core/Defs/ThingDefs_Misc/Weapons/RangedNeolithic.xml`); un-cutting restores them.
Do NOT add operations to `WeaponTags_Renormalise.xml` for these — that file must not be
regenerated (its own header explains why).

⚠️ **A CONFIG FILE NEVER BLOCKS ON GAME STATE** — write it whether the game is up or down;
it takes effect at the next load. But re-freeze afterwards: the repo's frozen copy
`deployed/config/v1_freeze/` must be updated in the same commit or the next currency check
reports a false drift.

## verify

    grep -c "ThingDef/Bow_Recurve\|ThingDef/Bow_Great<\|ThingDef/Pila\|ThingDef/MeleeWeapon_Ikwa" \
      "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/Mod_3521312241_Mod_CherryPicker.xml"

PASS = **0**, and `Bow_Great_Unique` still present. Then after the next load:

    python3 src/RimMandrake/Utils/neolithic_floor_roster.py

PASS = 39 surviving, 3 cut, and `NeolithicRangedDecent` carries `Bow_Recurve`.

## criteria

- [ ] The four lines are gone from the live Cherry Picker config.
- [ ] `Bow_Great_Unique`, `MA_VerdantBow`, `VWE_Throwing_Rocks` are still cut.
- [ ] `deployed/config/v1_freeze/` re-frozen in the same commit.
- [ ] No new operation added to `WeaponTags_Renormalise.xml`.
- [ ] Post-load: `NeolithicRangedDecent` resolves with a real bow in it.

## watch out

- 🔴 **In the def dump a Cherry-Picked weapon reads `weaponTags: []` and `MarketValue: 0`,
  it is NOT absent.** Tag-emptiness is the signature of a CUT, not of an untagged weapon —
  an audit that reads it the other way reports the cut list back as a pile of bugs.
- The config's mtime must end up NEWER than the dump, or the roster script will say the
  dump is authoritative when it is not.
