# Biome name provenance audit: the mineral sheet (2026-10-28)

Trigger, owner 2026-10-28: "this mineral sheet reveals something terrible. Do you really think you have that many
Baroque Biomes? I see RM_TheScald, RM_SeabedFloor_TheScald. I see RUT_Desert (labeled Jawa Desert)..."
Subject: `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\` (inventory.csv rows 60-96, design.md:22-26) and the
published copy `Transient\mineral_matrix_round_two\data.json` (commit 9ca2c776d7), 37 biome columns.
Method: read-only. MEASURED = I read the file/def/commit named. INFERRED = reasoned, not checked in game or dump.
No tile counts in this report are live facts.

## Summary

1. We have **27 world biomes** (23 standalone land + 4 seas) plus 1 non-natural aftermath biome (RM_ChillCrater) and 1 cave layer (RM_LanternDeeps). The sheet shows 37 columns and calls all 33 `RM_` columns "Baroque Biomes", which is the MOD's name, not a biome count.
2. **10 of 37 columns are not biomes of their own**: 4 sea-floor dive layers, 3 frozen `RUT_` twins duplicated next to their `RM_` successors (Desert, ExtremeDesert, AridShrubland), RUT_Umbra (real land, but it is the campaign def of the coldest land and is labelled with the retired "Fuel Snows" name), the OTHER_vanilla bucket, and RM_LanternDeeps (a cave layer). That leaves 26 legitimate world-biome columns (22 land + 4 seas). Renamed twins such as RUT_CrackedLands have no column at all, and a suffix-match twin rule cannot reach them.
3. The root error is one sentence, `design/RimMandrake/minerals_where_they_belong_design_2026-10-02.md:100` (8f99b3560d): it calls arid shrubland, desert and extreme desert "RUT-only". They are the frozen twins of RM_LeaningScrub, RM_LongShade and RM_Stillsand. The 10-03 registry CSV, its generator and the C# kernel all inherited it. The kernel's twin lookup is `"RM_" + suffix` (`RM_MineralPolicyKernel.cs:222-236`), which cannot find any renamed twin.
4. Since then the twin columns have drifted apart: RUT_ExtremeDesert has steel 3 and RM_Stillsand has none. On the seas, RM_TheScald is empty while RM_SeabedFloor_TheScald holds 8 minerals, so the sea's floor and its catch were split across two columns, against the owner's ruling that a sea biome describes both.
5. The "(Jawa)" labels are not in any def. Every RUT_ label in src reads "the Desert", "the arid shrubland", "the Extreme Desert", "Auroral Umbra". The generator that wrote them (`gen_matrix.py`, cited by design.md) is missing from the folder, so where those labels came from is UNMEASURED. I propose 9 repair tickets, 3 of which need the owner.

## The authoritative biome list

Sources (MEASURED): parsed BiomeDef XML under `src/**/Defs/BiomeDefs/`; the 2026-09-20 ruled table in
`design/RimMandrake/biome_mod_architecture.md` §2 ("all 27 world biomes", 23 standalone + 4 seas); the frozen
definition sheets `design/Jawa/worldbuilding/biomes/_freeze_matrix.csv` (30 sheets, BIOME_FREEZE_FABLE_REVIEW_1,
2026-09-07, bf70b43b73). The `RM_` def is the biome. A `RUT_` def is the frozen campaign twin that carries the painted
world until the one terminal repaint (architecture rule 3: "The def the world carries must BE the RimMandrake def.
Never a RUT_ twin").

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
| 18 | RM_FeverWood | the Fever Wood | surface land | RUT_FeverWood | the_fever_wood.md / poison_forest.md |
| 19 | RM_TheSump | the Sump | surface land | RUT_Sump | the_sump.md |
| 20 | RM_Pyrelands | the Pyrelands | surface land | none (donor ZBiome_Grasslands painted) | the_pyrelands.md |
| 21 | RM_TheForge | the Forge | surface land | RUT_TheForge | the_forge.md |
| 22 | RM_Cauldron | the Cauldron | surface land | RUT_Cauldron | (no frozen sheet found in _freeze_matrix.csv) |
| 23 | **none** | (Auroral Umbra) | surface land, campaign only | RUT_Umbra ("Auroral Umbra") | the coldest land; owner card 2026-10-19 (AURORAL_UMBRA_RENAME_BACK_TO_DARK) |
| 24 | RM_TheScald | the Scald | sea (surface + floor + catch) | RUT_TheScald | the_scald.md |
| 25 | RM_TheChill | the Chill | sea (propane) | RUT_PropaneLake | the_propane_lakes.md |
| 26 | RM_GreySea | the Grey Sea | sea | RUT_GreySea | terminator_sea.md + the_grey_deep.md (the floor) |
| 27 | RM_TwilightSea | the Twilight Sea | sea | RUT_TwilightSea | the_twilight_deep.md (the floor) |
| - | RM_ChillCrater | (aftermath) | background, `generatesNaturally=false` | none | CHILL_WORLD_CRATER_1, 2026-09-28 |
| - | RM_LanternDeeps | the Lantern Deeps | cave injection layer, "not a worldmap biome" (architecture §2c, owner: "that was a mistake") | none | the_lantern_deeps.md |
| - | (none) | | RUT_Jawa_BackgroundWater: utility background def | | |

Labels are as I recall them from the 10-28 parse (scratch `biomedefs.txt`). Row 23 is the one land with no `RM_` home.
That is an open question for the owner, not a defect. `fall_line.md` is a REGION (308 tiles in the 2026-08-16 canon,
not a live count) with no BiomeDef, which is expected. `wreck_fields.md` was superseded by it.

Not biomes (MEASURED, `src/RimMandrake/DivingInteraction/Defs/PlanetLayerDefs/`): RM_SeabedBiomeBase (abstract),
RM_SeabedUnavailable, RM_SeabedFloor, RM_SeabedFloor_{TheScald,GreySea,TwilightSea,TheChill}. These are dive-map
planet-layer BiomeDefs. They give each sea its floor, and the owner ruled that the sea biome describes both its
floor and its catch.

"Baroque Biomes" (MEASURED, commit f04561bbd0, 2026-09-27; `biome_mod_unification_spec.md` §1/§8) is the MOD
`mandrake.rm.biomes`. Its roster has 29 member mods, including kits (SeaShores, DivingInteraction,
EnvironmentalHazards, CreatureBehaviors, LanternDeeps, MovingDunes, ExplosiveGrowth). The gate logs
"30 BiomeDef(s) mapped". Neither number counts biomes.

## Every sheet column classified

Classes: **L** = legitimate world biome · **LY** = layer (floor or cave), not a biome · **TW** = frozen twin
duplicated next to its successor · **TU** = twin with no successor (campaign-only land) · **NN** = non-natural
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
| RUT_Umbra | "Umbra / Fuel Snows (coldest land)", Hills | TU + RET | RUT_Umbra.xml:5-20 (renamed back from RUT_FuelSnows on the owner's card 2026-10-19, 3056163ac3). The "Fuel Snows" half of the label is the retired name; design.md:22-26 says "Umbra (which stands for Fuel Snows)" |
| OTHER_vanilla | Elsewhere | BK | sheet-only bucket for every non-owned biome. It is not a def |

**Counts: L 26 (one with a label defect, two empty seas) · LY 5 (4 floors + Lantern Deeps) · TW 3 · TU/RET 1 ·
NN 1 · BK 1 = 37.** No column is an outright invention. Every name exists as a def in src or the 10-28 dump. The
errors are about kind (layer or twin counted as a biome), duplication, retired labels and the "(Jawa)" labels.
The sheet is also missing things, though by design rather than by mistake: RUT_CrackedLands, RUT_Scarlands,
RUT_Sump, RUT_Slime, RUT_PropaneLake and the other renamed twins, which the world actually carries today.

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
| `D:\ClaudeWork\rimmandrake\mineral_matrix_2026-10-28\design.md:22-26`, `PROGRESS.md:12`, `lessons.md:97-101`, `inventory.csv:60-96`; `Transient\mineral_matrix_round_two\data.json` | the 37-column sheet itself; "(Jawa)" labels; "Baroque Biomes" on floors | 9ca2c776d7 |
| Files still naming RUT_FuelSnows (grep, not each read): `biome_mod_architecture.md`, `alpha_biomes_hits_2026-10-16.json`, `explosive_growth_ruled_spec_2026-10-16.md`, `explosive_growth_bench_design_pass_2026-10-16.md`, `flowworks_liquid_matrix.md`, `plant_draw_layers_2026-10-14.md`, `world_remake_2026-10-19/02_world_pipeline.md`, `13_owner_rulings_2026-10-19.md`, `design/Jawa/fauna/biome_name_migration.py`, `design/Jawa/mods/biome_flora.py`, `queue/FOUNDRY.md`, items DONOR_DEFS_PORT_TO_OURS_1, PACK_ANIMALS_RESTORE_EMPTY_SADDLES, CUT_FALLOUT_GENERATED_DATA_1, `art_rulings/prefill/2026-10-03_mineral_numbers_review_2026-10-03.decisions.json` | retired name (some may be historic records that are right to keep it) | grep 10-28 |

## Proposed repair tickets

Names are proposals in SUBJECT_INTENT_TWIST form. They are NOT namechecked and NOT filed (the brief forbade ledger writes).

| name | title | seat | evidence |
|---|---|---|---|
| MINERAL_KERNEL_TWIN_MAP_NOT_SUFFIX | Kernel and generator resolve RUT_ twins through an explicit twin map, not "RM_"+suffix; selftest covers every renamed twin | FOUNDRY | Kernel.cs:222-236; gen_mineral_registry.py:310-312; Program.cs:232 |
| BIOME_TWIN_MAP_ONE_SOURCE_OF_TRUTH | One machine-readable biome registry (RM_ def, RUT_ twin, kind: land/sea/floor/cave/background) that sheets, registry and kernel read | FOUNDRY | the chain above; architecture §2 as its seed |
| MINERAL_REGISTRY_TWIN_COLUMNS_DROP_DIVERGED | Delete the RUT_Desert/ExtremeDesert/AridShrubland/FuelSnows columns from the registry CSV after the owner picks which values win | BENCH-needs-owner | draft_matrix_v2 divergences (steel 3 vs 0; 10 vs 8; 10 vs empty) |
| SEA_MINERALS_FOLD_FLOOR_INTO_SEA_ROW | Merge RM_SeabedFloor_* values into their sea's column (one biome = surface + floor + catch), or the owner rules floors keep their own numbers | BENCH-needs-owner | RM_TheScald empty vs floor 8 minerals; owner ruling "sea describes its floor and catch" |
| MINERAL_SHEET_REBUILD_FROM_RULED_LIST | Rebuild the mineral matrix from the 27 + ChillCrater + LanternDeeps list, with layers marked as layers, real src labels and no "(Jawa)" tags; restore or recreate gen_matrix.py | BENCH | design.md:22-26; inventory.csv:60-96; gen_matrix.py missing |
| BAROQUE_LIST_PAGE_UMBRA_STALE_REWRITE | Fix baroque_biomes_list_2026-10-19.html: no RUT_FuelSnows, Umbra is the Auroral Umbra (not a duplicate), sea floors listed as layers | BENCH | 173323cace vs 3056163ac3 |
| MINERALS_DESIGN_RUT_ONLY_CLAIM_CORRECT | Correct the 10-02 :100 and 10-03 :199 sentences (successor names; ChillCrater and LanternDeeps have no twin) | BENCH | the two lines quoted above |
| WARSCAR_LABEL_ARTICLE_RESTORE | RM_Warscar label "the Warscar" per the 2026-09-26 label ruling | FOUNDRY | RM_Warscar.xml; architecture §7 Q5 |
| FUELSNOWS_NAME_SWEEP_LIVE_DOCS | Sweep live (non-historic) references to RUT_FuelSnows; also fix the biome_paint_list RUT_Desert row and its stale labels | FOUNDRY | upstream table rows above |

## Open questions only the owner can answer

1. **Auroral Umbra's home.** RUT_Umbra is a real campaign land with no RM_ successor. On 2026-09-21 you said
   "Umbra is a region not a biome" (architecture §7 Q1, line 528). On the 2026-10-19 card you said "Back to Umbra,
   dark" and asked for perpetual auroras in "that biome". Does it get an RM_ def in Baroque Biomes, or is it
   painted onto another biome at the terminal repaint?
2. **Diverged twin numbers.** Where a RUT_ column and its successor disagree (ExtremeDesert steel 3 vs Stillsand
   none; AridShrubland steel 10 vs LeaningScrub 8; Desert steel 10 vs LongShade empty), which values are yours?
   The 10-03 review decisions file may hold your rulings. I did not check whose they were.
3. **Sea floors.** Should a sea's dive-floor minerals live on the sea's own row, as your ruling implies, with the
   floor defs as plumbing only? Or do you want floor and surface shown separately and labelled as layers?
4. **RM_Cauldron** has no frozen definition sheet in `_freeze_matrix.csv`. Is it ruled canon (it is in the
   architecture §2 table), or does it need a sheet?

UNMEASURED: the 10-28 def dump itself (I relied on the builder's PROGRESS.md for its contents); where the "(Jawa)"
labels came from (gen_matrix.py missing); what the kernel returns live for renamed-twin tiles; the labels in the
table above are from my 10-28 parse, not re-read line by line.
