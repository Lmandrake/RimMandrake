# Biome name provenance audit: the mineral sheet (2026-10-28)

Trigger, owner 2026-10-28: "this mineral sheet reveals something terrible. Do you really think you have that many
Baroque Biomes? I see RM_TheScald, RM_SeabedFloor_TheScald. I see RUT_Desert (labeled Jawa Desert)..."
Subject: `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\` (inventory.csv rows 60-96, design.md:22-26) and the
published copy `Transient\mineral_matrix_round_two\data.json` (commit 9ca2c776d7), 37 biome columns.
Method: read-only. MEASURED = I read the file/def/commit named. INFERRED = reasoned, not checked in game or dump.
No tile counts in this report are live facts. Tile counts below come from the painted worldmap, the 2026-10-20 dev
world: paint input `world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_tiles.csv` and its render report
`D:\ClaudeWork\remake\2026-10-20\view\biome\ASHKARR_DEV_LANDED_2026-10-20.report.json` (MEASURED). That save still
carries the pre-Wave-1 names RM_Wasteland and RM_NightsideIce (renamed RM_Wastes and RM_SleepingIce in 80e0635c30).

## Summary

1. We have **27 world biomes** (23 standalone land + 4 seas), exactly the 27 painted on the worldmap: 26 `RM_` defs plus `RUT_Umbra`, the Auroral Umbra, plus 1 non-natural aftermath biome (RM_ChillCrater) and 1 cave layer (RM_LanternDeeps). The sheet shows 37 columns and calls all 33 `RM_` columns "Baroque Biomes", which is the MOD's name, not a biome count.
2. **9 of 37 columns are not biomes of their own**: 4 sea-floor dive layers, 3 frozen `RUT_` twins duplicated next to their `RM_` successors (Desert, ExtremeDesert, AridShrubland), the OTHER_vanilla bucket, and RM_LanternDeeps (a cave layer). RM_ChillCrater is a real but non-natural biome. The other 27 columns are the 27 painted biomes (23 land + 4 seas). RUT_Umbra is one of them: it is the Auroral Umbra, painted on 2,531 tiles and kept on purpose, but the sheet labels it with the retired "Fuel Snows" name. Renamed twins such as RUT_CrackedLands have no column at all, and a suffix-match twin rule cannot reach them.
3. The root error is one sentence, `design/RimMandrake/minerals_where_they_belong_design_2026-10-02.md:100` (8f99b3560d): it calls arid shrubland, desert and extreme desert "RUT-only". They are the frozen twins of RM_LeaningScrub, RM_LongShade and RM_Stillsand. The 10-03 registry CSV, its generator and the C# kernel all inherited it. The kernel's twin lookup is `"RM_" + suffix` (`RM_MineralPolicyKernel.cs:222-236`), which cannot find any renamed twin.
4. Since then the twin columns have drifted apart: RUT_ExtremeDesert has steel 3 and RM_Stillsand has none. Nobody ruled any of those twin numbers: the 2026-10-03 review decisions file is an agent prefill with all 37 rows "pending". So the RM_ column is the biome's number and the twin columns go. On the seas, RM_TheScald is empty while RM_SeabedFloor_TheScald holds 8 minerals. The owner ruled on 2026-10-28 that a sea IS its floor, so each sea gets one row that carries its floor minerals.
5. The "(Jawa)" labels are not in any def. Every RUT_ label in src reads "the Desert", "the arid shrubland", "the Extreme Desert", "Auroral Umbra". The generator that wrote them (`gen_matrix.py`, cited by design.md) is missing from the folder, so where those labels came from is UNMEASURED. 9 repair tickets are filed for FOUNDRY (offline). None of them needs the owner.

## The authoritative biome list

Sources (MEASURED): parsed BiomeDef XML under `src/**/Defs/BiomeDefs/`; the 2026-09-20 ruled table in
`design/RimMandrake/biome_mod_architecture.md` §2 ("all 27 world biomes", 23 standalone + 4 seas); the frozen
definition sheets `design/Jawa/worldbuilding/biomes/_freeze_matrix.csv` (30 sheets, BIOME_FREEZE_FABLE_REVIEW_1,
2026-09-07, bf70b43b73). The `RM_` def is the biome. A `RUT_` def is the frozen campaign twin that carries the 2026-09-12
campaign save. The painted worldmap (2026-10-20) already carries the `RM_` defs (architecture rule 3: "The def the
world carries must BE the RimMandrake def. Never a RUT_ twin"). Its one exception is `RUT_Umbra`, which is not a twin.

| # | RM_ defName (the biome) | label in src | kind | frozen RUT_ twin (campaign carrier) | definition sheet (2026-09-07) |
|---|---|---|---|---|---|
| 1 | RM_Stillsand | the Stillsand | surface land | RUT_ExtremeDesert | deep_desert.md (dune_sea.md is a REGION of it) |
| 2 | RM_LongShade | the Long Shade | surface land | RUT_Desert | desert.md |
| 3 | RM_LeaningScrub | the Leaning Scrub | surface land | RUT_AridShrubland | arid_shrubland.md |
| 4 | RM_Wastes | the Wastes | surface land | RUT_Wastes | wasteland.md |
| 5 | RM_Abyss | the Abyss | surface land | RUT_Abyss | abyss.md |
| 6 | RM_SleepingIce | the Sleeping Ice | surface land | RUT_SleepingIce | nightside_ice.md |
| 7 | RM_BlueDesert | the Blue Desert | surface land | RUT_BlueDesert | the_blue_desert.md |
| 8 | RM_TheRot | the Rot | surface land | RUT_TheRot | the_rot.md |
| 9 | RM_GelatinousSlime | the Gelatinous Slime | surface land | RUT_Slime | the_slime.md |
| 10 | RM_Contagion | the Contagion | surface land | RUT_Contagion | the_contagion.md |
| 11 | RM_FloodedCanyon | the Cracked Lands | surface land | RUT_CrackedLands | the_cracked_lands.md (architecture §7 Q4: FloodedCanyon IS the Cracked Lands) |
| 12 | RM_WeepingStones | the Weeping Stones | surface land | RUT_WeepingStones | weeping_stones.md |
| 13 | RM_Greentide | the Greentide | surface land | RUT_Greentide | the_greentide.md |
| 14 | RM_Webwork | the Webwork | surface land | RUT_Webwork | the_webwork.md |
| 15 | RM_Warscar | **Warscar** (no article; label defect) | surface land | RUT_Scarlands ("the Warscar") | the_scarlands.md |
| 16 | RM_RustCathedral | the Rust Cathedral | surface land | RUT_RustCathedral | the_rust_cathedral.md |
| 17 | RM_Miasma | the Miasma | surface land | RUT_Miasma | the_miasma.md |
| 18 | RM_FeverWood | the Fever Wood | surface land | RUT_FeverWood | the_fever_wood.md |
| 19 | RM_TheSump | the Sump | surface land | RUT_Sump | the_sump.md |
| 20 | RM_Pyrelands | the Pyrelands | surface land | none (donor ZBiome_Grasslands painted) | the_pyrelands.md |
| 21 | RM_TheForge | the Forge | surface land | RUT_TheForge | the_forge.md |
| 22 | RM_Cauldron | the Cauldron | surface land | RUT_Cauldron (was RUT_PoisonForest) | cauldron.md (git-renamed from poison_forest.md; `_freeze_matrix.csv:10` keys it `poison_forest`). Toxic pools near the terminator: θ75-105, 546 painted tiles, median arc 91 |
| 23 | **RUT_Umbra** (the biome itself, not a twin) | Auroral Umbra | surface land, painted 2,531 tiles, perpetual aurora | none: kept, not repainted (`paint_inputs_remap.json:36`; `02_world_pipeline.md:153-156, 264`) | the_propane_lakes.md §0 (the land of the Propane Lakes; RM_TheChill is its sea); owner 2026-10-19, `13_owner_rulings_2026-10-19.md` row 18 |
| 24 | RM_TheScald | the Scald | sea (surface + floor + catch) | RUT_TheScald | the_scald.md |
| 25 | RM_TheChill | the Chill | sea (propane) | RUT_PropaneLake | the_propane_lakes.md |
| 26 | RM_GreySea | the Grey Sea | sea | RUT_GreySea | terminator_sea.md + the_grey_deep.md (the floor) |
| 27 | RM_TwilightSea | the Twilight Sea | sea | RUT_TwilightSea | the_twilight_deep.md (the floor) |
| - | RM_ChillCrater | (aftermath) | background, `generatesNaturally=false` | none | CHILL_WORLD_CRATER_1, 2026-09-28 |
| - | RM_LanternDeeps | the Lantern Deeps | cave injection layer, "not a worldmap biome" (architecture §2c, owner: "that was a mistake") | none | the_lantern_deeps.md |
| - | (none) | | RUT_Jawa_BackgroundWater: utility background def | | |

Labels are as I recall them from the 10-28 parse (scratch `biomedefs.txt`). Row 23 is the one painted biome whose def
is not `RM_`. It lives in `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml`, not in the Baroque Biomes mod.
Its regions on the painted map are Deadstone 861, Umbra 773, Ammonia Flats 692 and Fuelmere 69, among others, and 29 of
RM_TheChill's 57 tiles lie in its Umbra region. `fall_line.md` is a REGION (308 tiles in the 2026-08-16 canon,
not a live count) with no BiomeDef, which is expected. `wreck_fields.md` was superseded by it.

Not biomes (MEASURED, `src/RimMandrake/DivingInteraction/Defs/PlanetLayerDefs/`): RM_SeabedBiomeBase (abstract),
RM_SeabedUnavailable, RM_SeabedFloor, RM_SeabedFloor_{TheScald,GreySea,TwilightSea,TheChill}. These are dive-map
planet-layer BiomeDefs and they are plumbing. Owner, 2026-10-28: "There is only the sea floor. Of course. That's all
they ever was." A sea IS its floor, so its floor minerals belong on the sea's own row.

"Baroque Biomes" (MEASURED, commit f04561bbd0, 2026-09-27; `biome_mod_unification_spec.md` §1/§8) is the MOD
`mandrake.rm.biomes`. Its roster has 29 member mods, including kits (SeaShores, DivingInteraction,
EnvironmentalHazards, CreatureBehaviors, LanternDeeps, MovingDunes, ExplosiveGrowth). The gate logs
"30 BiomeDef(s) mapped". Neither number counts biomes.

## Every sheet column classified

Classes: **L** = legitimate world biome · **LY** = layer (floor or cave), not a biome · **TW** = frozen twin
duplicated next to its successor · **NN** = non-natural
background biome · **RET** = retired or renamed name still shown · **BK** = pseudo-bucket. The sheet's `mod` field
says "Baroque Biomes" for every RM_ row, the floors included (inventory.csv rows 60-96, MEASURED).

| sheet column | sheet label / family | class | evidence |
|---|---|---|---|
| RM_Contagion | Mountain country | L | src RM_Contagion BiomeDef; architecture §2 |
| RM_FloodedCanyon | "the Cracked Lands" | L | architecture §7 Q4. Twin RUT_CrackedLands has no column, and the kernel's suffix rule cannot map it (`RM_MineralPolicyKernel.cs:222-236`) |
| RM_TheForge | Mountain | L | src def; §2 |
| RM_RustCathedral | Mountain | L | src def; §2 |
| RM_WeepingStones | Mountain | L | src def; §2 |
| RM_Abyss | Hills | L | src def; §2 |
| RM_LongShade | Hills | L | src def. Its matrix row is `d4_empty` while its twin RUT_Desert holds steel 10 (draft_matrix_v2.csv) |
| RM_TheRot | Hills | L | src def |
| RM_SleepingIce | Hills | L | src def |
| RM_Warscar | Hills | L (label defect) | `src/RimMandrake/Scarlands/Defs/BiomeDefs/RM_Warscar.xml` label "Warscar", against the 2026-09-26 ruling "every biome label is `the Xxx`" (architecture §7 Q5) |
| RM_Webwork | Hills | L | src def |
| RM_BlueDesert | Flats | L | src def |
| RM_Cauldron | Flats | L | src def |
| RM_FeverWood | Flats | L | src def |
| RM_Greentide | Flats | L | src def |
| RM_LeaningScrub | Flats | L | src def. Steel 8 vs twin RUT_AridShrubland steel 10 (divergence) |
| RM_Miasma | Flats | L | src def |
| RM_Pyrelands | Flats | L | src def; §2 row 15 (donor ZBiome_Grasslands painted) |
| RM_GelatinousSlime | Flats | L | src def. Twin RUT_Slime cannot be mapped by the suffix rule |
| RM_Stillsand | Flats | L | src def. Phrikite/magnetite/salt, no steel; twin RUT_ExtremeDesert has steel 3 |
| RM_TheSump | Flats | L | src def. Twin RUT_Sump cannot be mapped by the suffix rule |
| RM_Wastes | Flats | L | src def |
| RM_TheScald | Sea surfaces | L (empty) | src def [background]. Zero minerals, while its floor column holds 8 |
| RM_TheChill | Sea surfaces | L | src def. Twin RUT_PropaneLake cannot be mapped by the suffix rule; lessons.md:97-101 calls it "superseded" |
| RM_GreySea | Sea surfaces | L | crystal_salts 5 vs floor 3 (two numbers for one sea) |
| RM_TwilightSea | Sea surfaces | L (empty) | empty vs floor steel 2 |
| RM_ChillCrater | Flats | NN | src def `generatesNaturally=false`; CHILL_WORLD_CRATER_1. Shown as an ordinary flat |
| RM_LanternDeeps | Underground | LY | architecture §2c: not a worldmap biome. Shown in the "Baroque Biomes" count (design.md:22-26) |
| RM_SeabedFloor_TheChill | Sea floors | LY | DivingInteraction PlanetLayerDefs |
| RM_SeabedFloor_GreySea | Sea floors | LY | same |
| RM_SeabedFloor_TheScald | Sea floors | LY | same. Holds the Scald's whole mineral set |
| RM_SeabedFloor_TwilightSea | Sea floors | LY | same |
| RUT_Desert | "desert (Jawa)", Hills | TW | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Desert.xml:3-10` "FROZEN 2026-09-24 ... until Phase B repaints the planet onto `RM_LongShade`". The src label is "the Desert", not "(Jawa)" |
| RUT_ExtremeDesert | "extreme desert (Jawa)", Flats | TW | RUT_ExtremeDesert.xml:5 FROZEN → mandrake.rm.stillsand; architecture §2 row 1 |
| RUT_AridShrubland | "arid shrubland (Jawa)", Flats | TW | architecture §2 row 9 → RM_LeaningScrub |
| RUT_Umbra | "Umbra / Fuel Snows (coldest land)", Hills | L + RET (label) | Painted biome, 2,531 tiles, kept by the 2026-10-19 ruling (row 23 above). RUT_Umbra.xml:5-20 (renamed back from RUT_FuelSnows on the owner's card 2026-10-19, 3056163ac3). The "Fuel Snows" half of the label is the retired name; design.md:22-26 says "Umbra (which stands for Fuel Snows)" |
| OTHER_vanilla | Elsewhere | BK | sheet-only bucket for every non-owned biome. It is not a def |

**Counts: L 27 (two with a label defect, two empty seas) · LY 5 (4 floors + Lantern Deeps) · TW 3 · NN 1 · BK 1 =
37.** The 27 L columns are exactly the 27 biomes on the painted worldmap. No column is an outright invention. Every name exists as a def in src or the 10-28 dump. The
errors are about kind (layer or twin counted as a biome), duplication, retired labels and the "(Jawa)" labels.
The sheet is also missing things, though by design rather than by mistake: RUT_CrackedLands, RUT_Scarlands,
RUT_Sump, RUT_Slime, RUT_PropaneLake and the other renamed twins, which the 2026-09-12 campaign save still carries.
The painted worldmap carries their RM_ successors.

## How the sheet got its list (causal chain)

1. **2026-09-20/24 (correct).** The owner ruled the RM_ def is the biome. Successors were built and the RUT_ defs
   frozen. Several successors took new names (Desert→LongShade, ExtremeDesert→Stillsand,
   AridShrubland→LeaningScrub, CrackedLands→FloodedCanyon, Scarlands→Warscar, Slime→GelatinousSlime,
   Sump→TheSump, PropaneLake→TheChill). MEASURED: architecture §2.
2. **2026-10-02, the root error.** `minerals_where_they_belong_design_2026-10-02.md:100` (8f99b3560d): "28 `RM_`
   BiomeDefs (parse of `src/**`), each with a `RUT_` twin plus RUT-only biomes (arid shrubland, desert, extreme
   desert, fuel snows, Umbra)." It paired twins by suffix and read the three renamed desert/scrub twins as
   unpaired. It also counted Lantern Deeps and ChillCrater among the 28 that "each have a twin", which is wrong:
   neither has one. MEASURED.
3. **2026-10-03, baked in.** `mineral_abundance_registry_design_2026-10-03.md:199` (ed68a7a980): "the 28 RM_
   biomes, the four sea floors, the five RUT-only biomes, and OTHER_vanilla_biomes. RUT twins read their RM
   column." `mineral_abundance_registry_2026-10-03.csv` columns 7-44 are exactly that set, and they still include
   the dead RUT_FuelSnows (last edits e99a6c8566, ff98040c4f, c889832f22, 2026-10-25). MEASURED.
4. **The code encodes the same rule.** `src/RimMandrake/Utils/gen_mineral_registry.py:152-153`
   (biome columns = keys starting RM_/RUT_) and :310-312 (twin = "RM_"+c[4:]).
   `RM_MineralPolicyKernel.cs:222-236` RegistryValue resolves a RUT_ biome to `"RM_" + biome.Substring(4)` and
   returns 0 when that def is absent. `SelfTest/Program.cs:232` only tests same-suffix twins. The three hand-added
   desert/scrub columns were the workaround, and their values have since drifted from their successors'.
   INFERRED, not live-measured: tiles painted RUT_Scarlands, RUT_CrackedLands, RUT_Sump, RUT_Slime or
   RUT_PropaneLake resolve to 0 for every mineral.
5. **2026-10-19, a stale page.** `design/RimMandrake/baroque_biomes_list_2026-10-19.html` (173323cace, 20:56)
   says RUT_FuelSnows exists and RUT_Umbra is a "byte-for-byte behavioural duplicate of Fuel Snows ... to be
   deleted after repaint". The rename-back (3056163ac3) landed at 21:14 the same day. The page was never
   updated: 13 FuelSnows mentions remain. MEASURED.
6. **2026-10-28, the sheet.** The builder enumerated dump BiomeDefs by prefix (PROGRESS.md:12: "28 RM_ biomes + 4
   seabed floors + 2 utility; RUT-only: AridShrubland, Desert, ExtremeDesert, Umbra, BackgroundWater") and reused
   the 10-03 column set. It found RUT_FuelSnows absent, which is correct, but kept the 10-19 page's framing
   ("Umbra (which stands for Fuel Snows)", lessons.md:97-101 "RUT_Umbra duplicates the coldest land"). It put the
   mod name "Baroque Biomes" on every RM_ row, floors and cave included, and design.md:22-26 then turned that into
   "the 28 RM_ Baroque Biomes". The "(Jawa)" labels came from `gen_matrix.py`, which is missing. That origin is
   UNMEASURED. Plausibly the script tagged RUT_ (RimUtinni = Jawa campaign) rows with the tier.

## Upstream sources carrying the error

| source | what it carries | evidence |
|---|---|---|
| `design/RimMandrake/minerals_where_they_belong_design_2026-10-02.md:100` | the "RUT-only" misclassification (root) | 8f99b3560d |
| `design/RimMandrake/mineral_abundance_registry_design_2026-10-03.md:199` | the 28 + 4 floors + 5 RUT-only column rule | ed68a7a980 |
| `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv` cols 7-44 | twin and floor columns; dead RUT_FuelSnows; drifting duplicate values | c889832f22 (latest) |
| `src/RimMandrake/Utils/gen_mineral_registry.py:152-153, 310-312` | prefix columns; suffix twin rule | read 10-28 |
| `src/RimMandrake/Minerals/Source/Kernel/RM_MineralPolicyKernel.cs:222-236` | suffix twin lookup; silent 0 for renamed twins | read 10-28 |
| `src/RimMandrake/Minerals/SelfTest/Program.cs:232` | test covers only same-suffix twins | read 10-28 |
| `design/RimMandrake/baroque_biomes_list_2026-10-19.html` | RUT_FuelSnows alive; Umbra a "duplicate"; no floors | 173323cace vs 3056163ac3 |
| `infrastructure/state/facts/biome_paint_list.md` | RUT_Desert row "PAINT" with no FROZEN/successor note; stale labels (RM_FloodedCanyon "flooded canyon", RM_Wastes "the Wasteland") | 80e0635c30 |
| `src/RimMandrake/Scarlands/Defs/BiomeDefs/RM_Warscar.xml` | label "Warscar" without the article | read 10-28 |
| `design/RimMandrake/biome_mod_architecture.md` §7 Q1 | "Umbra is NOT a biome", never updated after the 2026-10-19 Auroral Umbra ruling (corrected 2026-10-28) | read 10-28 |
| `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\design.md:22-26`, `PROGRESS.md:12`, `lessons.md:97-101`, `inventory.csv:60-96`; `Transient\mineral_matrix_round_two\data.json` | the 37-column sheet itself; "(Jawa)" labels; "Baroque Biomes" on floors | 9ca2c776d7 |
| Files still naming RUT_FuelSnows (grep, not each read): `biome_mod_architecture.md`, `alpha_biomes_hits_2026-10-16.json`, `explosive_growth_ruled_spec_2026-10-16.md`, `explosive_growth_bench_design_pass_2026-10-16.md`, `flowworks_liquid_matrix.md`, `plant_draw_layers_2026-10-14.md`, `world_remake_2026-10-19/02_world_pipeline.md`, `13_owner_rulings_2026-10-19.md`, `design/Jawa/fauna/biome_name_migration.py`, `design/Jawa/mods/biome_flora.py`, `queue/FOUNDRY.md`, items DONOR_DEFS_PORT_TO_OURS_1, PACK_ANIMALS_RESTORE_EMPTY_SADDLES, CUT_FALLOUT_GENERATED_DATA_1, `art_rulings/prefill/2026-10-03_mineral_numbers_review_2026-10-03.decisions.json` | retired name (some may be historic records that are right to keep it) | grep 10-28 |

## Repair tickets (filed for FOUNDRY, `--needs offline`)

| id | what | evidence |
|---|---|---|
| MINERAL_KERNEL_REWIRE_TWINS_BY_PAINT_MAP | Kernel and generator resolve a RUT_ twin through the painted map's RUT→RM pairs (`biome_paint_list.md`, `paint_inputs_remap.json`), not "RM_"+suffix. The selftest covers every renamed twin. RUT_Umbra resolves to itself | Kernel.cs:222-236; gen_mineral_registry.py:310-312; Program.cs:232 |
| BIOME_TWIN_MAP_UNIFY_ONE_REGISTRY | One machine-readable biome registry (biome def, RUT_ twin, kind: land/sea/cave/background) that the sheets, the registry and the kernel all read. Seed it from the 27 painted biomes | the chain above; architecture §2 |
| MINERAL_TWIN_COLUMNS_DELETE_RM_WINS | Delete the RUT_Desert, RUT_ExtremeDesert, RUT_AridShrubland and RUT_FuelSnows columns from the registry CSV. The RM_ column's numbers stand, because no owner ruling exists on the twin values (10-03 decisions: prefill, 37 pending). Keep the RUT_Umbra column: it is a painted biome | draft_matrix_v2 divergences; `Transient/mineral_numbers_review_2026-10-03.decisions.json` |
| SEA_MINERALS_MERGE_FLOOR_INTO_SEA_ROW | Move each RM_SeabedFloor_* column's minerals onto its sea's row (TheScald, GreySea, TwilightSea, TheChill), then drop the floor columns. The floor defs stay as plumbing | owner 2026-10-28 "There is only the sea floor" |
| MINERAL_SHEET_REBUILD_FROM_PAINTED_MAP | Rebuild the mineral matrix from the 27 painted biomes, plus ChillCrater and LanternDeeps marked as what they are, using real src labels and no "(Jawa)" tags. Restore or recreate gen_matrix.py | design.md:22-26; inventory.csv:60-96; gen_matrix.py missing |
| BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME | Fix baroque_biomes_list_2026-10-19.html: no RUT_FuelSnows, and the Auroral Umbra is a painted biome, not a duplicate. Sea floors are not listed as biomes | 173323cace vs 3056163ac3 |
| RUT_ONLY_CLAIM_CORRECT_IN_MINERAL_DOCS | Correct the 10-02 :100 and 10-03 :199 sentences (successor names; Umbra is a painted biome; ChillCrater and LanternDeeps have no twin) | the two lines quoted above |
| WARSCAR_LABEL_RESTORE_THE_ARTICLE | RM_Warscar label "the Warscar", per the 2026-09-26 label ruling | RM_Warscar.xml; architecture §7 Q5 |
| FUELSNOWS_NAME_CULL_FROM_LIVE_DOCS | Remove live (non-historic) references to RUT_FuelSnows. Also fix the biome_paint_list RUT_Desert row and its stale labels | upstream table rows above |

## The owner's 2026-10-28 answers, and where each was already on record

He had already ruled three of the four questions this audit first asked, or painted the answer into the world. They
are answered above and removed from this doc.

| subject | his answer, 2026-10-28 (card) | already on record at | why this audit missed it |
|---|---|---|---|
| Umbra's home | "Look at the painted worldmap please." | `13_owner_rulings_2026-10-19.md` row 18 ("Let's call it the Auroral Umbra… perpetual Auroral activity in that biome"); `02_world_pipeline.md:153-156, 264`; `paint_inputs_remap.json:36`; `world/paint_inputs_2026-10-20/README.md` (RUT_Umbra ×2,531 kept) | It read the 2026-09-12 record CSV and `biome_mod_architecture.md` §7 Q1, which still said "Umbra is NOT a biome" after the 10-19 ruling (now corrected) |
| Diverged twin numbers | "Look for the auroral baroque biomes there." | Painted map: every twin was repainted onto its RM_ successor, and only RUT_Umbra was kept. The 10-03 decisions file holds no ruling (prefill, all pending). His only ruled desert numbers are the 10-09 phrikite in ONE desert and transparisteel fine sand from the extreme desert. Both sit on RM_Stillsand, which already has sand 99 | It never opened the painted map |
| Sea floors | "There is only the sea floor. Of course. That's all they ever was." | `biome_rulings.md` 2026-09-21 "A sea biome describes BOTH its floor and its catch" | It treated the floor layer as a possible second biome |
| RM_Cauldron | "Toxic pools. Near the terminator. Yes it's there. Look harder." | `design/Jawa/worldbuilding/biomes/cauldron.md` (was poison_forest.md); `_freeze_matrix.csv:10` row `poison_forest`; toxic water in `RM_CauldronFlora.xml:247-252`, `RM_CauldronFauna.xml:337-339` | It grepped the freeze matrix for "cauldron" (the row is keyed by its old name) and credited poison_forest.md to the Fever Wood |

UNMEASURED: the 10-28 def dump itself (I relied on the builder's PROGRESS.md for its contents); where the "(Jawa)"
labels came from (gen_matrix.py missing); what the kernel returns live for renamed-twin tiles; the labels in the
table above are from my 10-28 parse, not re-read line by line.
