# Research tree prep — for RESEARCH_TREE_NORMALIZATION_1

Prep only. No rulings made here; the owner rules at the sitting. Absorbs
`TECH_TREE_WEAPON_GROUPS_1`'s two threads (ship-systems-online arc, weapon
techs grouped by kind).

**Sources, stated once:**
- Def dump capture `2026-08-30T08-49-45Z` (585 mods, fingerprint
  `5c9df49e6e32f67e`) — newest at prep time, confirmed via
  `src/RimMandrake/Utils/game_paths.py` `newest_capture()`.
- Cherry Picker cut list: live settings file, 1,513 defs, saved 2026-08-29
  17:20 (`cherrypicker.load()` provenance line).
- `515 ResearchProjectDef` total, `MEASURED` via the `measure` tool
  (`measure count ResearchProjectDef`), not a scan.
- Each research row's unlocks came from the dump's own `cachedUnlockedDefs`
  field (the game's runtime "what this project unlocks" cache) — **this field
  is incomplete**: it captures buildable Thing/Recipe unlocks but NOT
  mechanism-only unlocks (a vanilla biosculpter cycle, a surgery operation, a
  quest-start, a flat stat/tab gate). Every row below with an empty cache was
  individually read against its `description` + `descriptionHyperlinks`
  (and, for the ambiguous ones, the mod's own XML) before being called dead —
  never on the empty cache alone.

## 1. Orphan census — MEASURED dead

| row (defName) | mod | why dead | evidence |
|---|---|---|---|
| `DisruptorFlares` | Anomaly | all 1 unlock cut | unlocks `Apparel_DisruptorFlarePack`, Cherry-Picker cut |
| `VAE_SterileAttire` | Vanilla Apparel Expanded | all 3 unlocks cut | `VAE_Apparel_DoctorScrubs`, `VAE_Apparel_LabCoat`, `VAE_Headgear_SurgicalMask`, all cut |
| `VWE_MakeshiftWeapons` | Vanilla Weapons Expanded - Makeshift | all 6 unlocks cut | 6 `VWE_Gun_Makeshift*` guns, all cut |
| `VFEP_SweatFermentation` | Vanilla Factions Expanded - Pirates | all 1 unlock cut | unlocks `VFEP_Apparel_Rumsuit`, cut |
| `MM_Research_Repulsor` | Star Wars KotOR Resources and Materials | 0 unlocks, mod-wide | dump cache empty; grepped the WHOLE mod tree — no ThingDef/RecipeDef anywhere references it as a prerequisite |
| `MM_Research_AncientShipDesigns` | same | 0 unlocks, mod-wide | same check |
| `MM_Research_CWShipDesigns` | same | 0 unlocks, mod-wide | same check |
| `MM_Research_EmpireShipDesigns` | same | 0 unlocks, mod-wide | same check — this 4-row chain (`MM_StarWarsShipTab`) unlocks nothing at all, top to bottom |
| `guy762_ResearchKotOR_revan` | Star Wars KotOR Resources and Materials | author-flagged dead | `ParentName="KOTOR_UnobtainableResearch_Base"` in `ResearchProjects_KotORDebugUncraftables.xml`: baseCost 99,999,999, techprintCommonality 0. Sibling row literally says *"Hey! You're not supposed to unlock this one!"* |
| `guy762_ResearchKotOR_exile` | same | author-flagged dead | same parent/base |
| `WallStuff` | WallStuff | author-flagged dead | description: *"No Longer needed, just left for now so it doesn't cause errors."* |
| `MatterToEnergyConversion` | WallStuff | author-flagged dead | same description, same mod |

**12 rows, MEASURED dead**, across 4 mods + Anomaly + 3 Vanilla Expanded rows.

### Royalty — cut-CANDIDATES by ruling, not by measurement
`canon.yml` (`royalty.dead_ruled`) already rules Royalty's player-facing
systems dead and names this item as the place to cut its research. All 19
Royalty `ResearchProjectDef` rows still unlock live, uncut content
(`NobleApparel`, `CataphractArmor`, `JumpPack`, `Gunlink`, `BrainWiring`,
`SpecializedLimbs`, `CompactWeaponry`, `VenomSynthesis`,
`ArtificialMetabolism`, `NeuralComputation`, `SkinHardening`,
`HealingFactors`, `FleshShaping`, `MolecularAnalysis`,
`CircadianInfluence`, `Harp`, `Harpsichord`, `Piano`, `RoyalApparel`) — they
are not orphans by the same evidence standard as the table above. List them
here as the owner's cut-candidates for the sitting, not as measured dead.

### The task's seed does NOT hold — biggest surprise
The prep brief's known seed, *"vanilla Mortars unlocks nothing since the
turret cuts,"* is **stale once measured**. `Mortars` unlocks 21 things; only
2 are cut (`Turret_Mortar`, `FT_Turret_Mortar`). It still unlocks three OTHER
turrets not on the canon 56-def official roster (`VFES_Turret_Artillery`,
`VFES_Turret_AutomatedMortar`, `VFEP_Turret_FieldGun`) plus 5 live shell
recipes and 2 apparel/machining recipes. Per canon's own rule
(*"Everything not on this roster dies at normalization"*) those three
turrets are themselves due for a Cherry Picker cut, at which point `Mortars`
would still unlock shells with nothing to fire them from — a genuinely new
kind of "half-orphan" worth a look at the sitting, but NOT the clean case the
seed described. Do not carry the seed forward as fact.

### Dump blind spot — 22 more empty-cache rows, confirmed alive, not listed above
34 rows total had an empty unlock cache; 12 are the dead ones above. The
other 22 read as live once checked by hand — mechanism unlocks the cache
doesn't track: vanilla `Bioregeneration`/`Archogenetics`/`BlissLobotomy`/
`GhoulInfusion` (biosculpter cycle / gene assembly / surgery ops),
`ComplexClothing` (51 recipe hyperlinks, tailoring tier — clean dump miss),
`VFET_Mining` (unlocks a work type, not a def), 10 Dungeon Pack `DP_RGive*`
rows (each starts a named dungeon quest — ties to `VAULT_DUNGEON_CONCEPT_1`,
out of this item's scope), and several stat-buff/flavor rows
(`ResearchDrillTurretEfficientDrilling`, `RimFridge_PowerFactorSetting`
— an internal dev-only row, `VFEP_WarcasketRemoval`,
`OuterRim_DroidEnergySys`, etc.). None of these get a table row; they are
recorded here so nobody re-derives "empty cache = dead" and cuts something
live.

**58 further rows are partial-cut** (some but not all unlocks gone) — none
qualify as orphans by this item's bar; not tabulated individually.

## 2. Weapon-tech grouping — PROPOSAL (owner rules)

Not a ruling. A shape to react to, built off vocabulary ALREADY ratified
elsewhere so it doesn't invent a new one:
`design/Jawa/worldbuilding/setting_physics.md` Part 1 (forms of harm) and the
turret register's own `form`/`group` fields
(`design/Jawa/worldbuilding/review/turret_register.json`), which already
sort 93 turrets into families like *Imperial Emplacements — turbolaser
doctrine*, *Rakatan Relics — light of the Builders*, *Gravship Hardpoints —
the Utinni's guns*.

**PROPOSAL: sort weapon-kind ResearchProjectDefs onto the same forms**, not
by mod:

| form (from setting_physics.md) | scattered rows found (defName — mod) |
|---|---|
| Thermal / blaster | `guy762_ResearchKotOR_blasters`, `_hvyblasters`, `_miniblasters` (KotOR); `OuterRim_Blastersmithing` (Outer Rim); `VWE_LaserWeapons`, `VWE_LaserTargetingSystems` (Vanilla Weapons Expanded); `KOTOR_Research_plasmaApplications` |
| Ionic | `IW_IonChargeWeaponry` (Ion Weaponry mod); `guy762_ResearchKotOR_ion`, `_iondamp` (KotOR); `JawaIon_Weaponry` (our own, canon: personal ion = Jawa innovation, emplaced ion = Empire — `canon.yml weapons.ion_doctrine`) |
| Neural (sonic) | `guy762_ResearchKotOR_sonic` — currently the ONLY sonic-tagged research row found; a "sonic" family is thin without more content |
| Kinetic (slug) | `SniperTurret` ("uranium slug turret", Core), `VFES_Railgun` |
| Gravitic | `GravForge`/`GravWeapon`/`GravTuning`/`GravBionics` (GravTech), `GTbc_BigCannons`, `VGE_GravshipWeaponry` — this is also the ship-systems arc, below |

Same three-mod-plus-donor scatter the turret pass found: KotOR alone
contributes 89 of 515 research rows (17%, more than vanilla `Core`'s 77) and
supplies THREE separate blaster tiers and its own ion/sonic/plasma rows,
duplicating vocabulary the Jawa canon already owns (`JawaIon_Weaponry`).
Normalizing means picking ONE research chain per kind and re-pointing the
survivor unlocks onto it — the same move the turret pass already made for
buildings.

**Ship-systems-online arc sketch (PROPOSAL):** `VGE_GravshipWeaponry` /
`VGE_GravshipPower` / `VGE_GravshipLiving` (Vanilla Gravship Expanded) plus
`BasicGravtech`/`StandardGravtech`/`AdvancedGravtech` (Odyssey) already form
a rough spine for "bring the Utinni's systems up." `STARTING_SHIP_ANTICRAFT_1`
ties the anticraft caster showpiece to this same arc — sketch is: gravtech
tier unlocks → gravship system tier unlocks → anticraft/turret tier, with the
turret register's own "Gravship Hardpoints — the Utinni's guns" group as the
payoff at the top.

## 3. Row counts per mod (77 mods carry research; 515 rows total)

Top 15 by row count:

| rows | mod |
|---|---|
| 89 | Star Wars KotOR Resources and Materials |
| 77 | Core |
| 42 | Anomaly |
| 19 | Royalty |
| 16 | Outer Rim - Core |
| 16 | Outer Rim - Droid Depot |
| 14 | Biotech |
| 14 | Rimefeller |
| 13 | Vanilla Factions Expanded - Tribals |
| 10 | Dungeon Pack (Continued) |
| 10 | Research Reinvented: Stepping Stones |
| 9 | Odyssey |
| 9 | Vanilla Furniture Expanded - Art |
| 8 | Alpha Mechs |
| 8 | Vanilla Factions Expanded - Pirates |

Remaining 62 mods carry 1–7 rows each (full per-mod counts derivable again
from `measure sql` against this capture; not reproduced row-by-row here).
