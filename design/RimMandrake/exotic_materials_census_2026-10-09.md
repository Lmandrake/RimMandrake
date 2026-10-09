# Exotic materials census — 2026-10-09

Analysis only: no def was changed. Every proposal below is a one-line option for the owner, not a ruling.
Frame: `design/RimMandrake/canon_materials_design_2026-10-09.md` (plasteel **Shape**, durasteel **Hold**,
plastoid **Seal**, duranium **Brace**, doonium **Contain**, beskar **Protect**, cortosis **Disrupt**, phrik
**Parry**, transparisteel **Observe**, stygium **Conceal**, coaxium **Extend**, kyber **Focus**, tibanna
**Charge**, bronzium **Decorate**; plasteel/durasteel salvage+trade only; phrik, transparisteel, stygium,
coaxium trade-only). The "like X but more Y" lines map our materials onto those verbs **without** giving a
local material any reserved canon job.

Data: `design/RimMandrake/exotic_materials_census_2026-10-09.csv` (one row per material, 36 columns).
Re-run: `python3 src/RimMandrake/Utils/exotic_materials_census.py` (about 2 s).

## Method and coverage

The script parses all 2,684 XML files under `src/` (0 parse failures; 431 are patch files), giving 3,110
ThingDefs and 62 BiomeDefs. It resolves `ParentName` across `src/` (a Core parent such as `LeatherBase` or
`FishBase` is mapped to the categories it implies). A ThingDef counts as a **material** if it has
`stuffProps`, sits in a material `thingCategory`, inherits from a resource-type parent, or is named by a
producer: race `leatherDef`/`meatDef`, `butcherProducts`, `killedLeavings`, plant `harvestedThingDef`,
building `mineableThing`, or any milk/shear/egg/spawn/harvest/gather comp. That is **561** producer links
to our own defs, plus **306** to Core or donor defs (vanilla leather, meat and so on), which fall outside
this census.

- **Biome:** read from BiomeDef `wildAnimals`/`wildPlants`/`fishTypes` as element names, plus patch-added
  rosters attributed by the PatchOperation's own `BiomeDef[defName=…]` xpath, plus mineables named in a
  BiomeDef or GenStep.
- **Uses:** RecipeDef ingredients and fixed filters, `costList` (including patched-in ones), refuel
  filters, stuff-category consumers (a Core stuff category such as Leathery or Metallic counts as consumed
  by Core gear), C# identifier mentions, and quest/trader/thing-set mentions.
- **Clusters:** a keyword pass, then a written judgment layer (`CLUSTER_OVERRIDES` in the script) for the
  roughly 120 defs the keywords mis-filed. Each override follows the def's own description.

**Sanity probes** (found by the census ÷ ThingDefs with that name):

| probe | found | note |
|---|---|---|
| `RM_ToxinSealant` | 1 / 1 | |
| `*Leather*` | 31 / 31 | |
| `*Seepwax*` | 2 / 2 | `RM_Seepwax`, `RM_ThrummelSeepwax` |
| `*Bitumen*` | 1 / 1 | |
| `*Chitin*` | 25 / 26 | the miss is `RM_Apparel_ChitinSpiderHelmet`, apparel, correctly excluded |
| `*Silk*` | 5 / 6 | the miss is `RUT_Webwork_SilkKnot`, a harvest-node building, correctly excluded |
| `KOTOR_AlloyDurasteel` | 1 / 1 | the first pass missed it (a parent's `Abstract="True"` leaked through inheritance); fixed |

**Total: 685 materials.** Of these, **401 are food only** (meat, eggs, fish, fruit, milk), and **40 are out
of scope**: live breeding stock in a sack, water containers, ammunition, finished medpacs and stims,
crashed-ship salvage. That leaves **244 non-food materials**, which are the subject of this document.

**Instrument limits.**
- A producer wired only in C# (`RM_ThrummelSeepwax`, `RM_SapResin`, `RM_Bitumen`, the Rot teas) shows an
  empty `sources` column. Empty means the instrument did not see a producer, not that nothing makes it.
- "ORPHAN" means no recipe, costList, fuel filter, stuff consumer, C# mention or quest/trader mention. It is
  a candidate list; a sale price at a trader is a use the instrument cannot see.
- `biomes` comes from the def files, not the live planet, and says nothing about tile counts.

## Summary

| cluster | n | from creature | from plant | from mineral | no producer seen | twins | orphans | RM / RSW / RUT |
|---|---|---|---|---|---|---|---|---|
| armour hide/leather/chitin/plate | 73 | 67 | 1 | 0 | 5 | 18 | 6 | 27/43/3 |
| chemical reagent/salt/venom/pigment | 32 | 6 | 10 | 9 | 9 | 0 | 9 | 29/1/2 |
| drug/medicine base | 26 | 2 | 6 | 1 | 17 | 0 | 2 | 19/7/0 |
| trophy/relic/curio | 20 | 5 | 3 | 3 | 9 | 6 | 7 | 17/1/2 |
| fuel/oil/wax/hydrocarbon | 18 | 4 | 9 | 1 | 5 | 2 | 2 | 14/2/2 |
| structural wood/bone/stone/ice/clay | 17 | 0 | 6 | 2 | 9 | 0 | 3 | 12/3/2 |
| metals, alloys & synthetics | 16 | 0 | 1 | 5 | 9 | 2 | 3 | 4/10/2 |
| glass/silica/optics | 13 | 1 | 5 | 1 | 6 | 0 | 2 | 12/0/1 |
| textile/silk/wool/fibre | 13 | 7 | 4 | 0 | 2 | 4 | 0 | 7/5/1 |
| adhesive/resin/lacquer/sealant | 7 | 3 | 1 | 0 | 3 | 0 | 3 | 6/0/1 |
| gem/crystal/light-stone | 6 | 2 | 1 | 5 | 0 | 0 | 0 | 3/2/1 |
| soil/fertiliser | 3 | 1 | 1 | 1 | 0 | 0 | 1 | 2/0/1 |
| **non-food total** | **244** | | | | | **32** | **38** | |
| food-only | 401 | 200 | 27 | 5 | 168 | 0 | 1 | 143/199/59 |
| out of scope | 40 | | | | | | 11 | |

"twins" = rows whose full stat vector **or** whose label and description match another row (columns
`stat_twins`, `text_twins`). The mechanical pass found 9 stat-twin groups and 9 text-twin groups.

### Top proposals

**Unify (five):**
1. **Chitin ladder, three copies:** `RM_*Chitin` (Lantern Deeps), `RM_Rot*Chitin` (the Rot) and `RSW_*Chitin`
   (Bestiary) carry identical stats for brittle, tough, toxic, fragile, gray and crystal chitin (6 twin
   groups). Under ruling Q13 (duplicate, then regenerate one copy into a variant), either regenerate each
   second copy now or fold the RSW copies onto the RM ones.
2. **RM_/RUT_ item twins:** `RUT_GlowerCrust`, `RUT_CathedralRoachShell`, `RUT_BrinePlate`, `RUT_SeepStone`,
   `RUT_SaltCameo`, `RUT_Hardwood` and `RUT_SweetlineWool` repeat an `RM_` item. Three of the RUT copies
   are orphans, and one more is seen only in C#. Fold each pair into one def and point both producers at
   it. `RM_GreatboleHardwood` is itself an orphan while its twin `RUT_Hardwood` is code-referenced, so the
   surviving def is not automatically the RM one.
3. **Salt:** `RM_RawSalt` (Grey Sea), `RM_DeltaSalt` (Miasma), `RM_SeepSalt` (Weeping Stones),
   `RM_KettlewickSalt` (orphan), `RM_Brine` (orphan) and the brine plates and bezoars (orphans) are seven
   kinds of coarse salt that share no recipe. Make one common salt, keep the four Grey Sea crystal salts as
   the premium curing set, and turn the rest into biome-flavoured sources of that one salt.
4. **Plasteel slag:** `KotORChunk_plasteel` and `ChunkSlagPlasteel_GT` (GravForge leavings, an orphan) are
   one item. Keep the KotOR one. It is also the only honest salvage route to plasteel (§3.3).
5. **Tibanna:** `KOTOR_Tibanna` (Armoury pipe network) and `RUT_TibannaGas` (beldon shearing, code-only)
   are the same canon gas. Make one def, with beldon herds as the source and the pipe network as the
   consumer.

**Differentiate (five):**
1. `RM_CloakLacquer` (chotrix hide film that bends light) is **like stygium but crude and organic**:
   personal camouflage cloaks only, never ship cloaking, so stygium stays trade-only.
2. `RUT_Mindstone` (Lantern Deeps, value 900, used to cut mindstone matrices for droid heads) is **like kyber
   but for machines**: the local Focus crystal for droid minds, where kyber is the Focus for the Force.
3. `RM_GlowerCrust` (Warscar radiotrophic varnish, already the cost of `RM_GlowerPlate` and
   `RM_GlowerShieldPanel`) is **like doonium but crude**: radiation and heat shielding for small things, while reactor and ship cores
   stay doonium.
4. The glass family (`RM_SunGlass`, `RM_Biosilica`, `RM_GlassPearl`, `RM_WaveglassShard`, `RM_Lanternstone`)
   is **like transparisteel but brittle**: windows, lenses and lamps that are not blaster-proof, so
   transparisteel keeps the armoured canopy and observation dome.
5. `RSW_Leather_KraytDragon` (value 20; the highest blunt and joint-highest sharp of any hide) is **like beskar but organic**: the
   planet's heirloom armour hide, from a quest-scale kill only and never farmed.

**Orphans: 38 non-food materials** have no consumer the instrument can see (plus 1 food item and 11 out of
scope). The list is in §Orphans.

## Clusters

Stats are written as value / sharp / blunt / heat / cold-insulation / heat-insulation (stuff powers), from
the CSV.

### 1. Armour hide, leather, chitin and plate (73)

**What is there.** 43 RSW Bestiary hides and chitins (a donor family taxonomy: saurian, reptavian,
mammavian, insectile, insectine…), 27 RM biome hides and plates, and 3 RUT. 67 come from creatures. The top
of the ladder is krayt 20 / 2.3 / 2.5, horax and gloomcast 15 / 2.2 / 2.4, bright and dark fur 15 / 1.8 / 1.8,
testudine and zakkeg 15 / 2.0 / 2.0. The bottom is brittle and fragile chitin at 1.0 / 0.4.

**Unify**
- The chitin ladder exists three times (Lantern Deeps `RM_`, Rot `RM_Rot`, Bestiary `RSW_`): brittle,
  tough, toxic, fragile, gray and crystal are stat-identical across copies. Regenerate each second copy
  into a variant under Q13, or fold the copies together.
- Fragile and brittle chitin (1.0 / 0.45 / 0.50 vs 1.0 / 0.40 / 0.40) are one rung, named twice inside each
  tier. Keep one.
- `RM_GloomcastHide` and `RSW_Leather_Horax` are stat-identical (Q13 duplicate not yet regenerated).
- The low-tier Bestiary family leathers (reptavian 2.2 / 0.9 / 0.2, mammavian 2.2 / 0.9 / 0.4, nerf
  1.8 / 1.0 / 0.6, reptomammal fur 1.8 / 0.75 / 0.25, saurian 2.4 / 1.0 / 0.5) are five near-identical
  "plain hide" rungs. Fold them into two (plain hide, plain fur) and let the RM biome hides carry the
  identity.
- Three heat-proof leathers come from one biome, The Forge: `RM_DhokkurHide` (heat 2.4 / heat-insulation
  40), `RSW_Leather_Magma` (heat-insulation 50) and `RSW_Leather_LavaFlea` (heat-insulation 50). Keep
  dhokkur as the Forge's own and move or cut the donor two.
- `RM_CathedralRoachShell` and `RUT_CathedralRoachShell` are the same text, and both are orphans.

**Differentiate**
- `RSW_Leather_KraytDragon`: like **beskar** but organic. The apex heirloom hide, from a rare kill.
- `RM_Vexxith` (Cauldron; Metallic stuff; fire cannot warm it; acid beads off): like **durasteel** but
  acid- and heat-proof. Vat linings, acid-rain roofing, hazard doors; not hull plating.
- `RUT_CrackWax` (already the cost of `RM_CrackWaxSuit`), `RM_Leather_TarCured` (waterproof) and
  `VAEWaste_ToxicLeather`: like **plastoid** but organic. Sealed suits for one biome's hazard; plastoid
  keeps mass sealed armour.
- `RM_ScaldWalkerChitin` (boil suits) and `RSW_DeepChitin` (heat 6, heat-insulation 50): the **heat-suit**
  rung. Give them one job (boil and fire suits) so they stop competing with the general armour hides.
- `RM_RoyalRind` (greatbole fruit rind cured to a coat, `RM_Apparel_RindCoat`): like **plasteel** but
  grown. A formable rind for masks and coats; never droid shells or prosthetics, which are plasteel's
  key jobs.
- `RM_MoonlessSilk` is labelled "moonless leather" and `RM_MushroomLeather` is "not really leather"; both
  are Leathery stuff. Rename or move one to textile so the label says what it is.

**Orphans (6):** `RM_CathedralRoachShell`, `RUT_CathedralRoachShell`, `RM_DredgelChitin`,
`RM_SkellarnChitin`, `RM_ThrummelChitin`, `RM_QuarrokChitin`. All are butcher plates with no stuff
category and no recipe. Give them `RM_ChitinStuff`, or one "scrap chitin" recipe that renders them into
the biome's chitin.

### 2. Textile, silk, wool and fibre (13)

**What is there.** `RM_LilianaSilk` and `RSW_CrimsonSilk` (beauty 6, comfort 1.5; stat-identical),
`RM_Dewsilk` (value 9, sheds water, heat-insulation 30) and its cocoon, `RM_MurrelithPlumage`,
`RM_RuqqalFibre`, `RM_FuzzFiber`, `RM_SweetlineWool` and `RUT_SweetlineWool` (stat-identical), three
Bestiary wools, and `KOTOR_FabricArmorweave`. There are no orphans.

**Unify**
- `RSW_WoolBantha` (sharp 1.1, heat 2.2, cold 40 / heat 10) and `RSW_WoolNerf` (1.0, 2.0, 38 / 8) are one
  wool. Keep bantha.
- `RM_SweetlineWool` and `RUT_SweetlineWool` (giant-wool): one def.
- `RM_LilianaSilk` and `RSW_CrimsonSilk`: the Q13 regeneration is owed. Liliana is already the RM
  identity, so retire crimson or regenerate it.

**Differentiate**
- `KOTOR_FabricArmorweave` (sharp 1, blunt 0.8, heat 1.2): the canon-tier fabric, the only textile with
  real armour.
- `RM_Dewsilk`: the hot-climate luxury, sitting between cotton and devilstrand. Its job is heat
  insulation plus water-shedding.
- `RM_FuzzFiber` (too short to spin; used only by `RM_Make_SmotherBlanket`): stuffing and padding only,
  never cloth, which is fine. Name the job in its description.

### 3. Structural: wood, bone, stone, ice and clay (17)

**What is there.** Woods (`RM_OllimWood` bone-white and fireproof, `RM_MushroomLog`, `RM_SlackwaxTimber`
flammability 1.3, `RM_DeadVenomvine` "refused to burn", `RUT_Greenwood`, two heartwoods), bone
(`RM_SummBone`, `RM_Bones`), ice (`RM_BlueIce` mass 3, also a cold-rack fuel; `RM_StonewaterIce`), clay
and ceramic (`RM_PottersClay`, `RSW_KilnClay`, `RSW_CrackedCeramicShards`, `RSW_FiredCeramicware`),
`RM_SlimeBlock` (Stony), and `RM_TollhornCore`.

**Unify**
- `RM_PottersClay` (FeverWood) and `RSW_KilnClay` (Bestiary onnik feed) are both raw clay. Make one clay
  def; the onnik eats it and the kiln fires it.
- `RM_GreatboleHardwood` (an orphan, mass 1.2) and `RUT_Hardwood` (code-referenced): one heartwood.

**Differentiate**
- `RM_OllimWood` (flammability 0.05, heat-insulation 30) and `RM_DeadVenomvine` (refuses to burn): two
  fireproof woods. Keep ollim as the desert's fireproof timber and make venomvine fuel-free kindling. As
  written, both say "won't burn".
- `RM_BlueIce` and `RM_StonewaterIce`: like **carbonite** but local and temporary. Cold storage and
  preservation; the cold-rack fuel use already points there.
- `RM_SummBone` (light, honeycombed, has a melee-cooldown factor): like **phrik** but organic. Light hafts
  and staffs; phrik keeps saber-proof blades.

**Orphans (3):** `RM_GreatboleHardwood`, `RM_TollhornCore`, `RSW_CrackedCeramicShards`.

### 4. Metals, alloys and synthetics (16)

**What is there.** The Armoury canon set (durasteel, beskar raw and ingot, cortosis, bronzium, duracrete,
plastoid, three slag chunks), `Gravitonium` (Research Retag), and four of our own: `RM_CharLace` (pure
carbon lattice, Metallic stuff, mass 0.1), `RM_DeadSmartsteel` and `RM_LivePatternMetal` (Rust Cathedral
ancient alloy), and `RM_ZennaqFilament` (copper-like wire).

**Unify**
- `KotORChunk_plasteel` and `ChunkSlagPlasteel_GT`: one plasteel slag.
- `RM_DeadSmartsteel` (orphan) is ancient salvage alloy, the exact §0b "Ancient" yield. Fold it into
  the canon salvage chain: smelt to `RSW_Durasteel`, or rarely to `RSW_Duranium`, rather than keeping a
  standalone metal.

**Differentiate**
- `RM_CharLace`: like **plasteel** but more beautiful (beauty 1.5, very light). Ornament, art and fine
  trims; never armour plates or droid shells.
- `RM_LivePatternMetal` ("this metal is not dead"): like **cortosis** but alive. A Rust Cathedral relic
  for the occasional rare-material hack (§0a).
- `RM_ZennaqFilament` (orphan; conducts): the local conductor. An input to components or electrical work,
  so the Flooded Canyon gets a reason to farm zennaq.

**Canon-frame conflict to flag:** `KOTOR_Plastoid` is an ingredient of `kotor_Plasteel_recipe` and
`kotor_Plasteel_10xrecipe`, a bench route to plasteel, which §3.3 removes. `KOTOR_Plastoid` is also
`Woody` stuff, where §2c treats plastoid as the Seal material. Both are already build duties of
`CANON_MATERIALS_BUILD_1` §5.1–5.2; listed here so the census agrees with them.

**Orphans (3):** `RM_DeadSmartsteel`, `RM_ZennaqFilament`, `ChunkSlagPlasteel_GT`.

### 5. Glass, silica and optics (13)

**What is there.** Stillsand alone has `RM_GlassSand`, `RM_FineSand`, `RM_BiosilicaGrit`, `RM_Biosilica`
(grown lenses), `RM_SunGlass` (Stony stuff; solar ovens, stills, goggles) and `RM_GlassPearl` (ground into
a lens). The Twilight Sea has `RM_WaveglassShard` and `RM_VeilPane`. Elsewhere: `RM_FexxilShard` (Cauldron
cobalt glass), `RM_FE_Fulgurite`, `RUT_AuroraGlass` (Propane Lake), `RM_Floatstone` (Forge spun glass,
`RM_SpunstoneWeave` stuff; `RM_FloatstoneKeelBrace`) and `RM_Filth_CleaverShards`.

**Unify**
- `RM_GlassSand` and `RM_FineSand` are both "clean silica sand" (one shovelled, one sifted). Make one sand
  with a sieve step, or say in the descriptions why there are two.
- `RM_Biosilica` and `RM_GlassPearl` both end as lenses (`RM_SunGoggles`; `RM_GrindPearlLens`). Pick one
  lens route per use.

**Differentiate**
- The whole family is like **transparisteel** but brittle: windows, lenses and lamps that are not
  blaster-proof. Transparisteel keeps armoured canopies and domes.
- `RM_Floatstone`: like **duranium** but light. Light frames and keel braces for small craft; large frames
  stay duranium.
- `RM_FexxilShard` (orphan) and `RUT_AuroraGlass` (trade only) are coloured glasses. Give them a stained
  glass or art job (the Decorate verb) rather than a third lens route.

**Orphans (2):** `RM_FexxilShard`, `RM_Filth_CleaverShards` (filth; probably correct as is).

### 6. Gem, crystal and light-stone (6)

`RM_Lanternstone` (and its chunk), `RSW_ResourceBlueCrystal`, `DV_Pyrinth`, `Force_KyberCrystal`,
`RUT_Mindstone`.

**Unify:** `RSW_ResourceBlueCrystal` (crystal-crab drop) has stuff factors identical to `RM_Lanternstone`,
which was ported from it. Point the crab at lanternstone.

**Differentiate**
- `RUT_Mindstone`: like **kyber** but for machines (droid-mind Focus).
- `DV_Pyrinth` (glows and emits heat; heaters, lamps, blade): like **kyber** but thermal. A heat focus for
  warm lamps and heaters, never a saber focus.
- `Force_KyberCrystal` is consumed only by a quest (`RUT_KyberDonationSmuggle`) as far as this instrument
  sees; the lightsaber chain consumes the crystal-part defs. That is expected.

### 7. Fuel, oil, wax and hydrocarbon (18)

**What is there.** The Sump chain: `RM_KorvethPitch` → `RM_Bitumen` → `RM_TarGas` (fuels
`RM_GaslightLamp`); `RM_Seepwax` → `RM_ThrummelSeepwax` → `RM_WeakTarSolvent`. The Chill:
`RM_HydrocarbonFlesh` (to chemfuel), `RM_TarspoolStalk`, `RM_PitchpearlBeads`. Others: `RM_ColdWax` (Blue
Desert and Lantern Deeps; flammability 2), `RM_SeepOil` (FeverWood), `RM_GlowerCrust`, the Twilight Sea
lamp bulbs, `RM_SootBrick`, `KOTOR_Tibanna`, `RUT_TibannaGas`, `KOTOR_RawRhydonium`.

**Unify**
- Tibanna: one def (see top proposals).
- Chemfuel feedstocks: `RM_Make_ChemfuelFromHydrocarbonFlesh`, `…FromGillAsh` and `…FromTholin` are
  three bills doing one job. Make one "render to chemfuel" bill over a feedstock category; each biome
  keeps its own feedstock.
- `RM_GlowerCrust` and `RUT_GlowerCrust`: one def (the RUT copy is an orphan).

**Differentiate**
- `RM_TarGas`: like **tibanna** but dirty. Lamp and heating gas only, never blaster charge.
- `RM_HydrocarbonFlesh` and `RM_ColdWax`: like **coaxium** but low-grade. Volatile local fuels that must
  stay cold, if the coaxium cold-hazard mechanic is built; coaxium keeps range.
- `RM_GlowerCrust`: like **rhydonium** as a dirty fuel, plus the doonium-like shielding above. It already
  has both uses; keep both.

**Orphans (2):** `RM_SootBrick`, `RUT_GlowerCrust`. `RM_ColdWax` and `RM_SeepOil` are code-only (a C#
consumer is assumed).

### 8. Adhesive, resin, lacquer and sealant (7)

`RM_SapResin` → `RM_ToxinSealant` and `RM_StellockLace`; `RUT_CrackWax`; `RM_CloakLacquer`;
`RM_VaulmLacquer`; `RM_RedSap`; `RM_StellockBranch`.

**Unify:** `RM_VaulmLacquer` (FeverWood amber resin that "takes a fine finish"; orphan) and
`RM_SapResin` (Greentide amber resin) are both amber resin. Give vaulm a finish or varnish job
(furniture beauty) or treat it as FeverWood's sap resin.

**Differentiate:** `RM_CloakLacquer` (stygium-lite; see top proposals). `RM_ToxinSealant` stays the one
anti-regrowth sealant; nothing else should seal greatbole wood.

**Orphans (3):** `RM_RedSap` (insect-repelling, wound-sealing sap: a natural medicine or repellent input),
`RM_VaulmLacquer`, `RM_StellockBranch` (a self-sealed branch; no recipe reads it, though stellock lace
exists).

### 9. Chemical reagent, salt, venom and pigment (32)

Salts (Grey Sea crystal salts ×4 with curing recipes, raw, delta, seep and kettlewick salt, brine, brine
plates ×2, bezoars ×3); venoms and toxins (`RM_RawVenom`, `RM_GorbelethToxin` → `RM_FrenzyDose`,
`RM_StenchSporeExtract` → stench grenade); pigments (`RM_Deepfire`, `RUT_LampBlack`,
`RM_WreckLichenScrapings`, `RM_CrowncarpetDead`); solvents (weak and strong tar solvent); and others
(`RM_WarDust`, `RM_Tholin`, `RM_GillAsh`, `RM_RawSlime`, `RM_DeltaSilt`, `RM_VauliskLureOrgan`,
`RSW_GlowGoo`, `RM_RadioactiveSuppressant`).

**Unify**
- Salt (see top proposals). The four crystal salts are already differentiated by their curing recipes;
  the other seven are not.
- Bezoars: `RM_ContaminantBezoar`, `RM_VitrifiedBezoar` and `RUT_MetalSaltBezoar` are three "metal-salt
  lump" orphans. Make one bezoar, with the vitrified one as its rare grade, and give it a smelt-to-metal
  recipe.
- `RM_BrinePlate` and `RUT_BrinePlate`: one def.

**Differentiate**
- `RSW_GlowGoo` (orphan; luminous), `RM_VauliskLureOrgan` (holds light after death) and the Twilight Sea
  bulbs are three biological light sources. Make glow goo a light-pigment input next to `RM_Deepfire`.
- `RUT_LampBlack` and `RM_WreckLichenScrapings` are both dye bases. Black ink (writing, the Compact) and
  rust-orange dye are distinct; give the scrapings a dye recipe.

**Orphans (9):** `RM_Brine`, `RM_KettlewickSalt`, `RM_BrinePlate`, `RUT_BrinePlate`,
`RM_ContaminantBezoar`, `RM_VitrifiedBezoar`, `RUT_MetalSaltBezoar`, `RM_WreckLichenScrapings`,
`RSW_GlowGoo`. (`RUT_LampBlack` is consumed only in quest or trader defs.)

### 10. Drug and medicine base (26)

Rot brews and symbionts (fed by the live-ingredient caps), `RM_MedicineFungal`, `RM_UnjoiningDraught`,
`RM_FrenzyDose`, `RM_SlimeAntidote`, `RM_StellockLace`, `RM_RimeNoduleEuphoric`, `RM_AmbrosyxShroom`,
`RM_TavroskLiquor`, `RM_SekkulaathSpleenChemicals`, plus the canon or donor set: `RSW_Bacta`, `KOTOR_kolto`,
`KOTOR_Spice`, `KOTOR_Deathstick`, `RSW_BufoBile`, `RSW_MutapoxVial`, `RSW_RawNysyllin`.

**Unify:** `RSW_Bacta` and `KOTOR_kolto` are two healing gels in one role. Unless both are wanted, keep
bacta as the working gel and make kolto a rare trade good.

**Differentiate:** `RM_MedicineFungal` is "less potent than industrial" and `RSW_RawNysyllin` is "refined into
primitive medicine" (orphan). Both are herbal-medicine rungs; wire nysyllin into a recipe or cut it.

**Orphans (2):** `RM_SekkulaathSpleenChemicals` (the description promises a narcotic brew that no recipe
makes) and `RSW_RawNysyllin`.

### 11. Trophy, relic and curio (20)

Fossils (impression, deep stratum, skeleton), salt cameos ×2, seep stones ×2, mantis claws ×2, grub
spines, sweetline token, crest plate, shed curiosity, the sealed Elder relic, the wombpod sac, and others.
Most are trade value by design.

**Unify:** `RM_SaltCameo`/`RUT_SaltCameo`, `RM_SeepStone`/`RUT_SeepStone` and
`RM_FungalMantisClaw`/`RSW_FungalMantisClaw` are text twins.

**Differentiate:** the fossils (values 18, 140 and 650) are the Flooded Canyon's aurodium-like wealth. Give
them one display or sale use (a museum shelf, a Bazaar collector) so they are not dead weight.

**Orphans (7):** `RM_FossilImpression`, `RM_FossilDeepStratum`, `RM_FossilSkeleton`,
`RM_GreatboleGrubSpines`, `RM_SweetlineToken`, `RM_FungalMantisClaw` ("needed for special…" says its own
description), `RM_WombpodSac`.

### 12. Soil and fertiliser (3)

`RM_DeltaLoam` (used), `RUT_FungalSoil` (trade only), `RM_SeedFistFertilizer` (orphan). **Unify:** one
"rich soil" item feeding one fertiliser or soil-laying use, with each biome supplying its own flavour.

### 13. Food only (401)

Out of this document's scope: fish 125, eggs 198 (100 fertilized, 98 not), meat 36, plant food 31, and 11
others. One food
item, `RM_SekkulaathCream`, has no consumer and no `ingestible` block in its resolved def, although its
description says it will "fill pastry". It is probably missing that block.

## Orphans

38 non-food materials are produced or defined with no consumer the instrument can see. Biome and
source are from the def files. The proposal column says what would give each one a job, or whether to cut it.

| material | label | cluster | made by | biome(s) | proposal |
|---|---|---|---|---|---|
| `RM_RedSap` | red sap | adhesive | RM_Sapblister | RM_Contagion | repellent or wound-salve input |
| `RM_StellockBranch` | stellock branch | adhesive | — | — | read by a stellock-lace recipe, or cut |
| `RM_VaulmLacquer` | vaulm lacquer | adhesive | RM_Vaulm | RM_FeverWood | furniture-finish job, or treat as FeverWood sap resin |
| `RM_CathedralRoachShell` | roach shell plating | armour hide | RM_CathedralRoach | RM_RustCathedral | chitin stuff category, or scrap-chitin recipe |
| `RM_DredgelChitin` | dredgel chitin | armour hide | RM_Dredgel | RM_TheSump | chitin stuff category |
| `RM_QuarrokChitin` | quarrok chitin | armour hide | RM_Quarrok | RM_Webwork | chitin stuff category |
| `RM_SkellarnChitin` | skellarn spine-chitin | armour hide | RM_Skellarn | RM_TheSump | chitin stuff category, or spike-trap cost |
| `RM_ThrummelChitin` | thrummel chitin | armour hide | RM_Thrummel;RM_ThrummelBroodmother;RM_Th | RM_TheSump;RUT_Sump | chitin stuff category (Sump building plate) |
| `RUT_CathedralRoachShell` | roach shell plating | armour hide | RUT_CathedralRoach | RUT_RustCathedral | fold into RM twin |
| `RM_Brine` | brine | chemical reagent | — | — | solar-still input (its description says so); wire it |
| `RM_BrinePlate` | brine plate | chemical reagent | RM_BrineDeposit_BrinePlate | RM_Wasteland;RUT_Wasteland | fold into common salt / bezoar smelt |
| `RM_ContaminantBezoar` | contaminant bezoar | chemical reagent | RM_MiddenshellSeam;RM_Sloghog | RM_Wasteland | one bezoar, smelt to metal |
| `RM_KettlewickSalt` | kettlewick salt | chemical reagent | RM_Kettlewick | RM_TheScald | fold into common salt |
| `RM_VitrifiedBezoar` | vitrified bezoar | chemical reagent | RM_MiddenshellVitrifiedSeam | — | rare grade of that bezoar |
| `RM_WreckLichenScrapings` | wreck-lichen scrapings | chemical reagent | RM_WreckLichen | — | dye recipe (its description says dye base) |
| `RSW_GlowGoo` | glow goo | chemical reagent | RSW_PodWorm | RM_Miasma;RUT_Miasma | light-pigment input beside deepfire |
| `RUT_BrinePlate` | brine plate | chemical reagent | RUT_BrineDeposit_BrinePlate | genstep:RUT_Jawa_ScatterWastelandBrinePl | fold into RM twin |
| `RUT_MetalSaltBezoar` | metal-salt bezoar | chemical reagent | RSW_Excretor | RM_Wasteland;RUT_Wasteland | fold into the bezoar |
| `RM_SekkulaathSpleenChemicals` | sekkulaath spleen chemicals | drug | — | — | the narcotic brew its description promises, or cut |
| `RSW_RawNysyllin` | nysyllin | drug | RSW_Plant_Nysyllin_Wild | — | primitive-medicine recipe, or cut |
| `RM_SootBrick` | soot brick | fuel | RM_Sootgrazer | RM_Wasteland | fuel filter on Wasteland burners |
| `RUT_GlowerCrust` | glower crust | fuel | RUT_Glower | RUT_Scarlands | fold into RM twin |
| `RM_FexxilShard` | fexxil glass | glass | RM_Fexxil | RM_Cauldron | stained-glass / art use |
| `RM_Filth_CleaverShards` | cleaver shards | glass | RM_Cleaver | RM_LanternDeeps | filth; leave |
| `ChunkSlagPlasteel_GT` | plasteel slag chunk | metals | GravForge | — | fold into KotORChunk_plasteel |
| `RM_DeadSmartsteel` | dead smartsteel | metals | RM_MineableDeadSmartsteel | RM_RustCathedral;RUT_RustCathedral | Ancient-salvage smelt to durasteel / duranium |
| `RM_ZennaqFilament` | zennaq filament | metals | RM_Zennaq | RM_FloodedCanyon | conductor input to components |
| `RM_SeedFistFertilizer` | seed-fist fertilizer | soil | RM_BloodyFist | RM_Contagion | fold into one soil/fertiliser item |
| `RM_GreatboleHardwood` | heartwood | structural wood | RM_GreatboleCore;RM_GreatboleHeartwood;R | RM_Greentide;RUT_Greentide | fold with RUT_Hardwood; give one a stuff category |
| `RM_TollhornCore` | tollhorn core | structural wood | RM_Tollhorn | — | carving / art input |
| `RSW_CrackedCeramicShards` | cracked ceramic shards | structural wood | — | — | failure product; regrind to clay or leave as filth-like |
| `RM_FossilDeepStratum` | deep-stratum fossil | trophy | RM_FossilSeam_Unique | RM_FloodedCanyon;RUT_CrackedLands | collector sale / display |
| `RM_FossilImpression` | fossil impression | trophy | RM_FossilSeam_Impression | RM_FloodedCanyon;RUT_CrackedLands | collector sale / display |
| `RM_FossilSkeleton` | articulated fossil skeleton | trophy | RM_FossilSeam_Skeleton | RM_FloodedCanyon;RUT_CrackedLands | collector sale / display |
| `RM_FungalMantisClaw` | fungal mimic mantis claw | trophy | RM_Skerrith | RM_TheRot | the 'special' recipe its RSW twin has |
| `RM_GreatboleGrubSpines` | grub spines | trophy | RM_GreatboleGrub | — | spike-trap or arrow cost |
| `RM_SweetlineToken` | pilgrim's token | trophy | — | — | ritual or pilgrimage use, or cut |
| `RM_WombpodSac` | wombpod sac | trophy | RM_Wombpod | RM_Contagion;RUT_Contagion | hatch mechanic (its description says it hatches); check C# |

Not counted as orphans: 1 food item (`RM_SekkulaathCream`, see §13), and 11 out-of-scope rows (seven
breeding-stock items, two water containers, the sealed water jar, and the brain-worm shell). Those are
carried by C# or by hand, and the instrument cannot see that.
