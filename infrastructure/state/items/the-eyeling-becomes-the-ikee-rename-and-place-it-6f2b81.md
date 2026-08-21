## spec
(a) **RENAME ONLY — the art is untouched.** `PatchOperationReplace` on
    `ThingDef[defName="AA_Eyeling"]/label` -> `ikee`
    and on `/description` -> the text in `SCENARIO_SPEC.md` §"The ikee".
    ⚠️ `Races_Eyeling.xml` declares `AA_Eyeling` **twice** (the ThingDef at
    line 4 and a second block at line 82 — check what the second one is before
    patching, it may be a PawnKindDef sharing the defName).
    Source: `...\workshop\content\294100\1541721856\1.5\Defs\ThingDefs_Races\Races_Eyeling.xml`
(b) **WILD PLACEMENT.** `PatchOperationAdd` into `BiomeDef/wildAnimals` for
    `Wasteland` (main), `ExtremeDesert` (sparse), `ZBiome_DesertOasis` (uncommon).
    🔴 **NOT the nightside** — the shipped `ComfyTemperatureRange` is 0–60 °C, so
    it freezes there. Not in `Ocean`/`Lake`, not in the wet biomes.
    🪤 `wildAnimals` is a LIST of `<li><animal>X</animal><commonality>N</commonality></li>`
    — NOT the dictionary shorthand that killed `biomeConfigs` in B63 and the
    FactionDefs in B56.
(c) **STARTING SAVE** — one ikee, tamed, **bonded to Yeku**, trained to Obedience
    only (Release left untrained). Rides with `B55`, not with this item.
⛔ Do NOT change `race/trainability`, `wildness`, `baseBodySize`, `foodType` or any
stat. Every one of them was checked and is already right for this campaign; the
identity is what changes, not the animal.

## verify
`validate_patch.py --defs` clean on the patch; the live def's label reads `ikee`
and its description contains no "extradimensional corruption"; `AA_Eyeling`
appears in exactly the three BiomeDefs named and no others.

## criteria
the clan starts with a bonded ikee; it reads as belonging to this campaign rather
than to Alpha Animals; and a player can find another one in the waste.

## notes
**from:** DECIDE, 2026-08-19, closing D26 on the owner's 2026-08-15 ruling
*"AA_Eyeling MUST be made into a star-wars-style pet for the starting Jawa clan
to keep!"* Design is settled in `design/Jawa/worldbuilding/SCENARIO_SPEC.md`
("The ikee") and `fauna_placement.md`. ⛔ Do not re-decide any of it.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20 — halves (a) and (b). One new file,
`src/Jawa/Jawa_Patches/Patches/Ikee_Rename.xml`, deployed and in sync.
⏳ Half (c), the bonded starting ikee, rides with `B55` as the item says and is
NOT done here.
verify output: `validate_patch.py --defs` -> `OK - 0 errors, 6 warning(s)`.

🔴 **THE ITEM'S XML WARNING IS BACKWARDS — the second time in two items.** It
says `wildAnimals` needs
`<li><animal>X</animal><commonality>N</commonality></li>` and *"NOT the dictionary
shorthand"*. `BiomeAnimalRecord.LoadDataFromXmlCustom` reads the **node NAME** as
the animal and the node's **text** as the commonality, so
`<AA_Eyeling>1.2</AA_Eyeling>` is the only form that loads and the prescribed
`<li>` form would misparse.
🔑 **Both wrong warnings were generalised from the `biomeConfigs` / FactionDef
lesson, which is a real trap but a DIFFERENT one.** The rule that actually
decides it: **read the record class.** A type with `LoadDataFromXmlCustom` taking
the node name is shorthand-only; a plain class is `<li>`-only. `BiomeAnimalRecord`
and `WeatherCommonalityRecord` are both the former.
✅ **The item's OTHER warning was right and worth having:** `Races_Eyeling.xml`
does declare `AA_Eyeling` twice — a `ThingDef` and a `PawnKindDef` sharing the
defName. Both shipped `label: eyeling`, so **both are renamed**; `wildAnimals`
resolves to the PAWNKIND, and renaming only the ThingDef would have left "eyeling"
showing wherever the kind's label is used.
⚠️ **Version folder:** the item cites the mod's `1.5` copy. Alpha Animals ships
1.5 AND 1.6, and 1.6 is what loads. Both read; the fields agree, so no harm this
time — but the GRiNDTerra item was bitten by exactly this and the More Vanilla
Biomes def differs between its 1.0 and 1.6 copies.
⛔ No stat touched: wildness, baseBodySize, foodType, trainability and every
statBase are untouched, as instructed. ComfyTemperatureRange 0-60 confirmed, which
is why the nightside is excluded.
Placement: `Wasteland` 1.2 · `ExtremeDesert` 0.5 · `ZBiome_DesertOasis` 0.8.
⏳ Live half is CHECK's: `IKEE_READS_AS_OURS_1` in `queue/CHECK.md`.
