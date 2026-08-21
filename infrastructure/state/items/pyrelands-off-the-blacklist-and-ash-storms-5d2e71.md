## spec
Two edits. ENABLING ONLY — do not add a `scoreOffset` for this biome and do
not tune how much of it appears; that is the owner's at the map screen.
(a) `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml` — DELETE the line
    `<li>ZBiome_Grasslands</li>` from `<biomeBlacklist>`. Leave `<li>Savanna</li>`
    and `<li>Grasslands</li>` blacklisted; only the ZBiome one carries the
    Pyrelands. Add NO `<biomeConfigs>` entry for it — neutral, it competes on
    its own allowed range, which is what "barrier between the wet biomes and
    the dry desert" means.
(b) Ash storms over the Pyrelands. `AB_VolcanicAsh` ALREADY LOADS (Alpha
    Biomes, confirmed in the 585 dump): grey sky (0.6,0.6,0.6),
    `WeatherOverlay_Fog`, `accuracyMultiplier 0.7`, `favorability Bad`,
    `weatherThought AB_VolcanicAshThought`. No new weather is authored.
      - PatchOperationAdd on
        `/Defs/BiomeDef[defName="ZBiome_Grasslands"]/weatherCommonalities`,
        value `<li><weather>AB_VolcanicAsh</weather><commonality>3</commonality></li>`
        (`DryThunderstorm` sits at 2 there, so this reads as the dominant
        storm without erasing it).
      - PatchOperationReplace `WeatherDef[defName="AB_VolcanicAsh"]/label`
        -> `ash storm`, and `/description` -> text with no volcano in it.
        ⚠️ The relabel is GLOBAL; `AB_PyroclasticConflagration` also uses this
        weather and is RARE. "ash storm" reads correctly there too. Accepted.
🪤 `weatherCommonalities` is a LIST of `WeatherCommonalityRecord`, so the
`<li><weather>..</weather><commonality>..</commonality></li>` form above is
mandatory. It is NOT the dictionary shorthand that killed `biomeConfigs` in
D29(b) and the FactionDefs in B56 — do not copy that pattern here.
⏳ ORDER: this rides on top of B63/D29(b). Until the `is not <li>` bug is
fixed, `biomeConfigs` reads `[]` and every offset in that file is inert.

## verify
`grep -c 'ZBiome_Grasslands' <the biomeBlacklist block>` returns 0;
`python3 skills/rimworld-modding/scripts/validate_patch.py <both files> --defs`
scoped to the active list, 0 errors; the added weather node uses `<li><weather>`.

## criteria
on the world the owner rolls, stormy-savanna tiles exist and are sited between
the wet biomes and the desert, and an ash storm occurs on one with the label
`ash storm` and a grey sky.

## notes
**from:** DECIDE, 2026-08-15, on the owner's D30 (1) ruling.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20 (offline half). Half (b) built as one new file,
`src/Jawa/Jawa_Patches/Patches/AshStorms_Pyrelands.xml`, deployed and in sync.
⛔ Half (a) NOT done — it is VOID by D29 and nothing depends on it.
verify output: `validate_patch.py --defs` -> `OK - 0 errors, 3 warning(s)`.

🔴 **EVERY PART OF THE OPERATION THE ITEM SPECIFIED WAS WRONG, and each one
would have failed SILENTLY.** Measured before writing anything:
1. **The field is `baseWeatherCommonalities`.** There is no `weatherCommonalities`
   on `BiomeDef` — `BiomeDef.cs:55`. The specified xpath matches nothing, and a
   PatchOperation that matches nothing logs nothing.
2. **It IS the dictionary shorthand, and the item has it exactly backwards.** The
   item calls the `<li><weather>..</weather><commonality>..</commonality></li>`
   form *mandatory* and the shorthand forbidden.
   `WeatherCommonalityRecord.LoadDataFromXmlCustom` reads the **node NAME** as the
   weather def and the node's **text** as the commonality:
     `RegisterObjectWantsCrossRef(this, "weather", xmlRoot);`
     `commonality = ParseHelper.FromString<float>(xmlRoot.FirstChild.Value);`
   So `<AB_VolcanicAsh>3</AB_VolcanicAsh>` is the only form that loads. The
   shipped def is written that way, twelve entries of it.
3. **The def dump cannot answer this.** `weatherCommonalities` is not a key it
   captures, so it reads back `None` whether the field is empty, full or
   imaginary — the same "null means NOT INSPECTED" trap the dump warns about
   elsewhere. The real table came out of the mod's own 1.6 XML.
   ⚠️ And the version folder matters: the same mod's **1.0** copy of this def has
   a different label and no weather table at all.
✅ **What the item got right:** `DryThunderstorm` does sit at 2, so commonality 3
reads as the dominant storm without erasing it. Full table now recorded in the
patch file's header.

⚠️ **A NOTE ON THE VALIDATOR, because I could not settle it and nobody should
repeat the attempt blind.** Three ops warn `0 nodes in the on-disk Defs`. I tried
to characterise when that warning is real and **failed**: a controlled probe file
reports 0 nodes even for `Defs/PawnKindDef[defName="AncientSoldier"]`, a Core def
that matches perfectly well inside a real patch file. ⇒ **The 0-node warnings are
NOT a reliable measurement and a `PatchOperationConditional` test line is not one
either.** Verify a patch against the def's own XML, which is what was done here.
Not filed as a tool defect because I could not produce a reproducible case.

⏳ Live half is CHECK's: `ASH_STORM_OVER_PYRELANDS_1` in `queue/CHECK.md`.
