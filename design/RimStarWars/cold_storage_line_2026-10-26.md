# Cold storage line: our own Star Wars preservation devices (replaces RimFridge)

Status: DESIGN, not built. Filed 2026-10-26 by BENCH. Umbrella item: `COLD_STORAGE_BUILD_OWN_LINE_DROP_RIMFRIDGE`.
Every choice in this doc not quoted from the owner is **delegated: design**
(`design/RimMandrake/delegation_policy.md` §1). Only the two questions in §10 are reserved for him (§2 of that policy).
Research scratch, with the raw API extracts: `D:\ClaudeWork\rimmandrake\cold_storage\` (`wook_pages.txt`,
`wook_pages2.txt`, `fridge_refs2.txt`, `preservation_scan2.txt`).

## 0. Owner ruling (verbatim, 2026-10-26 ~07:00 PDT)

> "We would need to skin this anyway, and it's just one thing, so let's just make our own Starwars-type freezer
> unit with our own properties. Commission it, and drop RimFridge, as long as there's no strange amazing code they
> have we need (doubt it). Do some research to figure out what Star Wars uses as Fridges anyway. Let's make them in
> a few sizes and tech levels. Rakatan would be full Stasis Chambers (what you unlock through the ship or loot from
> their ancient tech dungeons/experiences) and the local Star Wars one would be cruder devices that work based on
> cold temperature as expected (fridge-like) and of course then there are the stranger versions like the one that
> seals things in tar, canning-type options from/through VFE. this is a critical interaction with Star Wars Cuisine
> of course. Sealing in sap as well. some of them would not only be food preservation but required to impart
> particularly wonderful tastes."

Earlier rulings this doc obeys (`design/Jawa/proposals/high_cuisine_deep_design.md`):
- preservation-vocab, 2026-09-02: *"Canning is terrestrial… Different food will need different preservation
  methods… salt flats, or the tar pits, or sand dunes… a barrel of tar… More than one method should work for each
  food type, maybe some work for all… Sand-oven should be sand-drying."*
- vce-repoint: *"leverage what they have and reskin it to us."*
- hazard-pantry: effects should be good, bad, strange and wonderful, and *somewhat unreliable*.
- terroir: production supercharges in the right biome or latitude.

## 1. RimFridge audit: what we would lose

Source audited: workshop 2898411376 ("RimFridge: Now with Shelves!", `rimfridge.kv.rw`), `1.6/Source`, 4,442 lines.

**Verdict: SAFE TO DROP. There is no strange, amazing code.** The whole trick is one Harmony prefix of about
twenty lines. Everything else is a convenience we either rebuild in a few lines or do not need.

| RimFridge feature | How it works | Keep? |
|---|---|---|
| Per-cell cold | Prefix on the `Thing.AmbientTemperature` getter. For an unpowered or dead thing standing on a fridge cell it returns `fridge.currentTemp` from a map-keyed cache, so `CompRottable` sees freezing. | **Rebuild.** This is the engine (§4.0). |
| Setpoint and drift | `CompRefrigerator` holds desiredTemp/currentTemp and runs on power or on fuel. | Rebuild, with drift when unpowered. |
| Wall fridges | 1x1 wall units. Patches keep prisoners and social rooms from treating them as improper, with light-blocking and airtight options. | Rebuild as the canon wall cooling unit (§4.1). The propriety patches are needed only for the wall form. |
| Nutrient-paste hopper | `isHopper` true | Keep, as one flag on the cooling units. |
| Frosty drinks | `CompFrosty` moodlet | Drop. Cuisine does flavour better (§5). |
| Trade beacon | A fridge counts as an orbital trade beacon. | Drop. |
| Neat stacks | Stacked-item display and label offsets, `maxItemsInCell` 3 | Drop; use vanilla shelf rendering. LWM Deep Storage already does multi-stack. |
| Wall-fridge corpse palls | Death pall for corpses in wall fridges | Drop. |
| Power-factor research | `RimFridge_PowerFactorSetting`. Its tab is nulled at game start. Our Cherry Picker removes the def, which **is** the new-game NRE (`RIMFRIDGE_NEWGAME_DIAGNOSE_COMPONENT_NRE`). | Gone with the mod; the NRE goes too. |
| Public `FridgeCache` | Other mods read it by reflection. | Not needed. See below. |

**Who depends on RimFridge** (scan of all 320 active mods, indexed by the About.xml root `packageId`):
- **LWM Deep Storage**: a MayRequire-guarded patch adds `LWM_DS_RimFridge_Refrigerator`, and its dll sets
  `uglyStackAppearance` by reflection.
- **Replace_Stuff**: a guarded "FridgeCompat" hook.

Both hooks are optional and fail quietly. Nothing hard-depends on RimFridge.

A functional fridge already exists without RimFridge: Dubs Bad Hygiene Lite's `HygieneRefrigerator`
(`DubsBadHygiene.Building_Fridge`, 20 W). So the colony is never without cold storage between the drop and our
build.

**Our references to fix when the drop ships** (step 9.9):
- `src/RimMandrake/Utils/research_manifest_validate.py`: `KNOWN_SELF_LOOP = "RimFridge_PowerFactorSetting"`,
  lines 33, 162 and 177.
- `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py:792` and `:851`, a noise list.
- The Cherry Picker config, around line 1409.
- Mentions in `design/RimMandrake/mod_audit/*`, the `world_remake_2026-10-19` files and
  `design/Jawa/research_review/*`.

## 2. Canon research: what Star Wars uses as fridges

Source: Wookieepedia, read through the MediaWiki API. The extracts are in `wook_pages.txt` and `wook_pages2.txt`.
"Canon" means Disney canon; "Legends" is marked. Canon and Legends both name with **RSW_**. Our own inventions name
with **RM_**.

| Thing | What the source says | Status | Our use |
|---|---|---|---|
| **Cooling unit** (coolth unit) | Wall-installed in the Lars homestead kitchen; Jira's cooling unit | Canon | `RSW_CoolingUnit_Wall`, and the name of the local ladder |
| **Cooling supply unit** | Food mini-fridge aboard the Halcyon | Canon (Galactic Starcruiser) | `RSW_CoolingSupplyUnit`, the 1x1 |
| **Chiller / drinks chiller** | Beverage storage (*The Acolyte*; Outlander Club) | Canon | Label flavour for the drinks variant |
| **Cooling chamber** | "could be used to store food" | Legends | `RSW_CoolingChamber`, the walk-in |
| **Cryo unit** (cryogenic stasis unit) | Freighter cargo-hold device that keeps foodstuffs fresh (*Platt's Starport Guide*) | Legends | `RSW_CryoUnit`, the spacer deep-cold tier |
| **Stasis field** | Slows or stops time to preserve (Luminara's body; the Drengir Progenitor) | Canon | The stasis mechanic |
| **Stasis-field horticapsule** | Preserves plants (*Complete Vehicles*, 2018) | Canon | Precedent that stasis is used on organics |
| **Food-ration stasis boxes** | Ruusan grub boxes kept indefinitely by a stasis field | Legends-era | Precedent for food in stasis |
| **Stasis chamber / tank / booth** | Suspended animation; an entropy field (booth, Legends) | Canon / Legends | Rakatan chamber naming |
| **Rakatan stasis vaults** | Belsavis Ancient Stasis Zone; stasis vault 113 held prisoners for millennia | SWTOR (Legends) | Rakatan chamber; `canon_references/rakata/description.md:149` |
| **Carbonite / carbon-freezing** | Goods encased in carbonite for transport (Tibanna); carbon-freezing chamber | Canon | `RSW_CarbonFreezingPress` |
| **Carbonite 'n' Cream Pie** | Blast-chilled in a *miniature carbon-freezing chamber* (Strono Tuggs, Empress Teta) | Canon | Proof that carbon-freezing is a kitchen tool, and a recipe that requires it |
| **Portaak amber** | Resin from the portaak leaf; a natural fungicide the Korunnai rub on weapons (*Shatterpoint*) | Canon | Closest canon to sap or resin sealing (§4.4) |
| **Wroshyr sap / sap syrup** | Kashyyyk "tree blood"; a syrup glaze for Glazed Kod'yok (*Life Day Cookbook*) | Canon | Sap as an ingredient rather than a seal |
| **Greel-wood syrup**, **plooey-sap** | Lothal syrup in vintage bottles; Akiva sap liquor | Canon | Sap-aged sweets and drinks |
| **Pickled mynock** | Kept in a tank behind the bar at Oga's (Strono Tuggs) | Canon | A recipe that requires pickling |
| **Pickled coodler-roe** | A Goliath Mal culinary rite | Canon | A recipe that requires pickling plus cold |
| **Smoked nerf**, **jerky** | Corellian smoked meat; dried and cured meat | Legends | Sand-drying and salt-crust products |
| **Tinuvian tar pits** | A canon *idiom* only ("dragged through a Tinuvian tar pit") | Canon phrase | **Not** a preservation method. |

**Headline.** Star Wars keeps food in three canon ways:
- a plain **cooling unit**, a fridge built into the wall of a Tatooine kitchen;
- **stasis fields**, the canon "stop time" method;
- **carbon-freezing**, which canon itself uses in a kitchen (Carbonite 'n' Cream Pie).

**Not canon, so ours (RM_):**
- **tar-seal** and **sap/resin-seal**, though portaak amber is a near canon cousin;
- **sand-drying**;
- **salt-crust**, which the Grey Sea salts already give us.

**Canning is terrestrial**, so it comes through VCE (Vanilla Cooking Expanded) under a reskin (owner).

## 3. Existing systems this ties into

| System | What it gives | Path or def |
|---|---|---|
| Star Wars Cuisine (`mandrake.rsw.cuisine`) | The salt-crust line already shipped: `RSW_CureWith{White,Pink,Violet,Amber}Salt` → `RSW_SaltCuredRation_*`, `RSW_AteCrystalSaltCured`; `RSW_TaozinBrine`; `RSW_MarshFungus`; the `RSW_CultureStarters` tag that the fermentation crock will read | `src/RimStarWars/Cuisine/Defs/` |
| Cuisine design | §4 tar-preserved aged meat (tar pits) and nightside cryo-delicacies (a cold chain); §9 salt-crust, tar-seal, sand-oven → sand-drying; line 75's catalog (pickling crock, fermentation crock, aging rack, cryo rack) | `design/Jawa/proposals/high_cuisine_deep_design.md` |
| The Sump (`mandrake.rm.thesump`) | `RM_Bitumen` (solid pitch); `RM_Seepwax`; `RM_TarRuinedGoods` (what tar does to food *by accident*); `RM_Tarred`; `RM_Leather_TarCured`; `RUT_PreservedDrawJoint` | `src/RimMandrake/TheSump/` |
| Terminal Biomes | `RM_ChillCryoponicsVat`; the nightside temperature band | `src/RimMandrake/TerminalBiomes/` |
| Wrecked Machines (`mandrake.rm.wreckedmachines`) | The grade ladder: Wrecked / Kludged 0.2 / Refurbished 0.75, with the original 1.0 unreachable by default. Layer 1 carries no Rakatan words; layer 2 is the RSW Rakatan skin; layer 3 is RUT | `design/RimMandrake/ancient_machines_design.md` |
| Vault dungeons (`mandrake.rut.injections`) | `RUT_VaultType3_FrozenRakata`; `RUT_Symbol_RakataCasket` (wraps the vanilla cryptosleep casket); `RUT_WarLabContainmentCell` | StructureInjectionsRUT |
| The ship | *"The SHIP is what unlocks everything else… unlocked by restoring a Kolyska subsystem"* | `design/RimMandrake/balance_paradigm.md` Axis 18a |
| Carbonite trophy design | `SWC_CarboniteSlab`; carbonite freezing of pawns or stacks (chemfuel plus uranium). Canon materials: carbonite has *"no def until a consumer exists"*, and this line is that consumer | `design/Jawa/carbonite_trophy_mod.md`, `canon_materials_design_2026-10-09.md:223` |
| VCE canning (active) | `VCE_CanningMachine`, `VCE_Can*` recipes, `VCE_Canned{Meat,Fish,Fruit,Produce,AP}`, `VCE_Canning` research | VanillaExpanded.VCookE |
| Outer Rim core (active) | `OuterRim_CarboniteFreezing` hediff, `OuterRim_FrozenInCarbonite` job | Pawn carbonite only; we do not touch it |
| DBH Lite (active) | `HygieneRefrigerator`, a working fridge | The fallback during the gap |

## 4. Device ladder

### 4.0 The engine: one comp, three modes (`mandrake.rm.coldstorage`, C#)

The engine is `CompStorageClimate` on a storage building, plus one Harmony prefix. It is the RimFridge trick,
written clean and named for us. It has three modes.

- **Chill.** The building keeps its own cell temperature. It drives toward a setpoint while it is powered or
  fuelled, and drifts back toward room temperature at an *insulation* rate when it is not. Items on its cells read
  that temperature through the `Thing.AmbientTemperature` prefix, so vanilla `CompRottable` does the rest. There is
  no rot math of our own, so there is nothing to drift out of step with the base game.
- **Stasis.** Items on its cells get a rot-rate multiplier of 0 through a prefix on the rot tick, not through
  temperature. Food comes out **unfrozen and fresh**, which no fridge can do. While the field holds it also stops
  corpse rot and deterioration.
- **Sealed.** This mode belongs to the *item*, not the cell. `CompSealed` sits on a sealed-goods ThingDef (the VCE
  can pattern). It records the method and the sealing tick; rot is off while sealed. After N days an **aging
  transition** turns it into its aged def, and that aged def is where the taste lives (§5). Opening is a short job
  or a recipe ingredient.

The engine also carries:
- one `ColdStorageMethodDef` per method (Chill / Stasis / CarbonFreeze / TarSeal / ResinSeal / SaltCrust / SandDry
  / Canned / Brine). This is the vocabulary that Cuisine recipes require (§5);
- an inspect line ("Cold box: −8 °C (set −10)"; "Stasis: holding"; "Tar-sealed 12 d, ages in 18 d");
- a `Building_Storage` subclass with the hopper flag, and a wall-placeable variant with the propriety patches the
  wall form needs.

**Performance.** RimFridge rebuilt a per-map dictionary every tick. Our cache is a per-map cell bitmap, rebuilt
only when a cold building spawns, despawns or changes power. The getter prefix is one array read on the hot path.

### 4.1 Local Star Wars cooling (Chill mode; canon names, `RSW_`)

These are the crude devices: *"cruder devices that work based on cold temperature as expected"*. All of them can
break down.

| Device | Canon anchor | Size | Reaches | Power / fuel | Research | Notes |
|---|---|---|---|---|---|---|
| `RM_EvaporativeCrock` | none (zeer pot) | 1x1 | ambient − 12 °C, only below 30 % humidity; useless in rain | none; needs water hauled every 2 days | none (day one) | The Jawa day-one cold box. Strong scorchside (terroir) and weak elsewhere. Generic, so RM. |
| `RSW_CoolingSupplyUnit` | cooling supply unit | 1x1 | −5 °C | 60 W | `RSW_CoolingUnits` (after vanilla Electricity) | Paste hopper on. The "mini-fridge". |
| `RSW_CoolingUnit_Wall` | Lars wall cooling unit | 1x1 in a wall | −8 °C, serving the room-side cell | 80 W | `RSW_CoolingUnits` | Replaces RimFridge's wall fridge, with the propriety patch. |
| `RSW_CoolingChamber` | cooling chamber (Legends) | 2x2 | −10 °C | 150 W, or chemfuel 6/day as an option | `RSW_CoolingUnits` + vanilla AirConditioning | Larder size, 12 stacks; drinks-chiller label variant. |
| `RSW_CryoUnit` | cryo unit (Legends) | 1x2 | −25 °C, which is the **cryo-aging** threshold (§5) | 250 W | `RSW_CryoStorage` (spacer; after `RSW_CoolingUnits` + vanilla Cryptosleep) | Gravship-safe (cargo-hold device in canon). Allowed on substructure. |

**Crude** means four things in play:
- Setpoints are coarse: three detents, Cool / Cold / Deep.
- Each unit has a **frost-up chance**: a breakdown that warms the unit until a pawn clears it.
- Units are loud: a small beauty penalty and the noise of a working machine.
- Units drift quickly when unpowered: low insulation.

### 4.2 Rakatan stasis (Stasis mode; *"full Stasis Chambers"*)

The stasis chamber spans three layers, as the ancient-machines design requires:
- **Layer 1, RM.** `RM_AncientStasisLocker` lives in `mandrake.rm.coldstorage`. It is a generic ancient machine
  with no Rakatan words. It takes Wrecked / Kludged / Refurbished grades when Wrecked Machines is present, and it is
  plain loot when that mod is absent.
- **Layer 2, RSW.** The Rakatan skin: `RSW_RakatanStasisCasket` (1x2) and `RSW_RakatanStasisVault` (3x3, 36
  stacks at Original: 4 per cell; built 36, not the 30 first drafted, because capacity is per cell). Labels, descriptions and art are Belsavis-styled. These sit in Cuisine until the layer-2 Rakatan mod
  exists, then move there.
- **Layer 3, RUT.** Ways to get the chamber:
  - **ship unlock**: restoring the relevant Kolyska subsystem grants `RSW_RakatanStasis` research, which lets you
    *build* Refurbished-grade chambers from Ancient Components;
  - **vault loot**: `RUT_VaultType3_FrozenRakata` and the war-lab rooms place chambers at Wrecked or Kludged grade,
    some still holding `RUT_StasisHeldProvisions` (§5).

**Stasis strength follows the quality grade** (owner ruling by card, 2026-10-26, `OWNER.jsonl:1793027548999599115`:
"Stasis grade → Strength follows grade"). Strength is the share of rot the field stops, so the rot factor on held
items is `1 − strength`. The grade also sets capacity, power and flicker:

| Grade | Stasis strength | Rot factor on held items | Capacity | Power | Field flicker |
|---|---|---|---|---|---|
| Wrecked | none (salvage or repair only) | 1 (no field) | n/a | n/a | n/a |
| Kludged | 0.2 | 0.8 | 0.2 × capacity | 1 / 0.2 × base draw (Kludged runs hungry) | each flicker lets one in-game hour of normal rot through and is visible as a mote |
| Refurbished | 0.75 | 0.25 | 0.75 × capacity | 1 / 0.75 × base draw | rare |
| Original (1.0) | full | 0 | full | base | none; unreachable by default, as Wrecked Machines ruling 1 says |

Base draw is 400 W. As built (COLD_STORAGE_STASIS_BUILD_RAKATAN_CHAMBERS), each grade is its own def on one
Wrecked Machines ladder line (`replaceTags`), which is how that mod restores every other machine: `<line>_Wrecked`,
`_Kludged`, `_Refurbished`, `_Original`. With Wrecked Machines loaded, the strength comes from its grade sliders
(`ColdStorageStartup.GradeStrength`); without it, the def's `stasisRotFactor` is the fallback (0.8 / 0.25 / 0).
Capacity is per cell (`maxItemsInCell` 1 / 3 / 4). The Rakatan chambers draw 400 W × 1/strength
(`scalePowerByStrength`). The RM locker draws nothing. A flicker can be switched off in Mod Settings.
Vault loot, as built: `RUT_VaultType3_FrozenRakata` places one Wrecked vault and two caskets (one Wrecked, one
Kludged). The war-lab rooms and `RUT_StasisHeldProvisions` are not built yet.

### 4.3 Carbon-freezing (Sealed mode, CarbonFreeze; canon)

`RSW_CarbonFreezingPress` is a 2x2 workbench, the *miniature carbon-freezing chamber* of Strono Tuggs' kitchen.

- **Recipe.** It encases a food stack in a carbonite block: `RSW_CarbonitePack_{Meat,Fish,Produce,Meal}`.
- **Input.** Each batch takes a carbonite charge, `RSW_CarboniteCharge`, crafted from chemfuel plus a little
  uranium, following `carbonite_trophy_mod.md`. This line is the first consumer that canon_materials said
  carbonite was waiting for.
- **Power.** 300 W while working.
- **Gate.** `RSW_CarbonFreezing` research, after `RSW_CryoStorage`.
- **Effect.** A pack never rots and stacks small (the canon use: transport), so it is the long-haul trade method.
- **Thawing.** A bill at the press. There is a **carbon-shock** chance: 5 % of meals come out "carbon-burnt"
  (tastes of metal; a small bad thought). The hazard-pantry ruling asks for some unreliability.
- **Blast-chill.** Without a full encasing, the press flash-chills ingredients. Carbonite 'n' Cream Pie
  **requires** this (§5).

### 4.4 The strange seals (Sealed mode; RM inventions)

| Method | Station | Input | Size | Power | Gate | Behaviour | Home |
|---|---|---|---|---|---|---|---|
| **Tar-seal** | `RM_TarSealingVat` | `RM_Bitumen` 5 per stack | 2x1 | heat: fuelled by wood or bitumen | `RM_TarRendering` (exists in The Sump) | → `RM_TarSealed{Meat,Fish,Egg,Produce}`. Ages 30 d → `RM_PitchAged*`. **Failure:** below Cooking 8 there is a 10 % chance per stack of becoming the existing `RM_TarRuinedGoods`. That is the hazard (an accident in the pits) made deliberate. | `mandrake.rm.thesump` (it owns bitumen) |
| **Resin/sap-seal** | `RM_ResinSealingJarShelf` (storage) + `RM_ResinTap` (placed beside any tree; yields `RM_SealingResin` per day by tree size; trees in the right biome yield 2×, the terroir rule) | `RM_SealingResin` 3 per stack | 1x1 tap, 1x2 shelf | none | `RM_ResinWork` (neolithic, day one) | → `RM_ResinSealed{Fruit,Meat,Sweet}`. Ages 20 d → `RM_AmberAged*`: sweet, resinous, slightly antiseptic (portaak amber is canon's fungicide resin). Some colonists find it *strange* (a random-trait thought). | `mandrake.rm.coldstorage` |
| **Salt-crust** | existing crafting spot / butcher bills | Grey Sea crystal salts | n/a | none | as shipped | **Already shipped** as `RSW_CureWith*Salt` → `RSW_SaltCuredRation_*`. The engine only tags these `SaltCrust` so recipes can require them. A plain RM salt-crust for non-Grey salt: `RM_SaltCrusted{Meat,Fish}`, using vanilla or VCE salt if present. | Cuisine (existing) + coldstorage |
| **Sand-drying** | `RM_SandDryingBox` (a box of hot sand, which the owner asked for: *"piles of sand in a box"*) | none; needs outdoor temp ≥ 35 °C, or doubles as a sun-bed | 2x2 | none | none (day one) | → `RM_SandDried{Meat,Fruit,Fungus}` (jerky). Rot ×0.1, not sealed. Works only scorchside or in summer, so terroir decides where. | `mandrake.rm.coldstorage` |
| **Brine/pickle** | `RM_BrineCrock` (the catalog's pickling crock) | brine: `RSW_TaozinBrine` where present, otherwise salt plus water | 1x1 | none | `RM_ResinWork` | → `RM_Pickled{Meat,Fish,Roe,Veg}`. Rot ×0.05. Canon pickled mynock and pickled coodler-roe come from here. | `mandrake.rm.coldstorage` (crock) + Cuisine (canon recipes) |
| **Canning** | VCE `VCE_CanningMachine` reskinned as an RSW **ration sealer** | VCE as shipped | VCE | VCE | VCE `VCE_Canning` | Patch label, description and texture only. defNames stay VCE's (vce-repoint ruling). Cans read "sealed ration tin". | Cuisine (`PatchOperationFindMod` on VCookE) |

**More than one method per food type** (preservation-vocab ruling). Every food class has at least three methods,
and Chill and Stasis work for everything:

| Food class | Chill | Stasis | Carbon | Tar | Resin | Salt | Sand | Brine | Can |
|---|---|---|---|---|---|---|---|---|---|
| Meat | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Fish / roe | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ |
| Fruit / sweet | ✓ | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ |
| Vegetable / fungus | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ |
| Eggs | ✓ | ✓ | — | ✓ | — | ✓ | — | ✓ | — |
| Meals | ✓ | ✓ | ✓ | — | — | — | — | — | ✓ (VCE soup) |

## 5. Star Wars Cuisine interaction: preservation that imparts taste

*"Some of them would not only be food preservation but required to impart particularly wonderful tastes."*

**Rule.** A *preserved* product is not the same def as fresh food. The taste lives in the **aged def**, and a recipe
**requires** that def, or the method tag on it. A fridge only keeps food. Seals and carbon change it.

| Product | Requires | Taste / effect | Canon? | Home |
|---|---|---|---|---|
| `RSW_CarboniteNCreamPie` | carbon-press blast-chill + milk + sweet | Dessert; strong "luxury" thought; very high value | Canon (Strono Tuggs) | Cuisine |
| `RSW_PickledMynock` | Brine on mynock meat (where a mynock race exists; otherwise the recipe is hidden) | Party dish; social bonus at gatherings | Canon | Cuisine |
| `RSW_PickledCoodlerRoe` | Brine **and** Chill after (a cold chain) | Acquired taste: + for some traits, − for others (Leia disliked the texture) | Canon | Cuisine |
| `RM_PitchAgedMeat` (any tar-aged class) | Tar-seal, aged 30 d | Smoky, mineral; best meal ingredient in the line; *only* obtainable this way | RM; Cuisine §4 "tar-preserved aged meat" | The Sump |
| `RM_AmberAgedFruit` / `RM_AmberSweet` | Resin-seal, aged 20 d | Sweet, resinous; a small infection-resist buff for a day (fungicide resin) | RM; portaak-amber inspired | coldstorage |
| `RM_FrostAgedRoe`, `RM_FrostAgedMeat` (nightside cryo-delicacies) | Chill at ≤ −25 °C for 15 d. That takes a `RSW_CryoUnit`, or a storage on a nightside tile where outdoor temperature stays below −25 °C (terroir: free, unpowered) | Delicate; luxury | RM; Cuisine §4 | coldstorage + Cuisine recipe |
| `RSW_SaltCuredRation_*` | Salt-crust with the right Grey salt | As shipped (`RSW_AteCrystalSaltCured`) | Existing | Cuisine |
| `RM_SandDriedJerky` → `RSW_NerfJerky` label variant where nerf meat exists | Sand-dry | Travel food: light, slow rot, caravan-friendly | Jerky is Legends | coldstorage + Cuisine |
| `RUT_StasisHeldProvisions` | Found only in Rakatan vault chambers | Millennia old and perfectly fresh. Eating it can give a *strange* thought or, rarely, a vision-flavoured inspiration. The hazard-pantry "strange, wonderful" | RUT | `mandrake.rut.injections` |
| Stasis itself | No taste change by design | Its value is perfect freshness, not flavour. That is the contrast with the seals. | Canon | n/a |

The fermentation crock and the `RSW_CultureStarters` tag stay in the Cuisine design. Brine is the only crock built
in this line.

## 6. Mod Settings

Every mod ships "superb" Mod Settings. Defaults equal the shipped behaviour, and with everything off the game
degrades gracefully.

**`mandrake.rm.coldstorage`:**
- **Engine.**
  - Chill on/off. When off, cooling buildings are plain shelves.
  - Stasis on/off. When off, stasis chambers act as Chill at −10 °C.
  - Seal aging on/off. When off, sealed goods never age; open them for the plain food.
- **Rates.**
  - Power-draw multiplier, 0.25–3 (the useful part of RimFridge's power factor).
  - Unpowered insulation multiplier.
  - Aging-time multiplier.
  - Seal failure-chance multiplier (0 = never ruins).
- **Methods.** One toggle each for resin, sand-drying, brine and the evaporative crock. Turning one off hides its
  station and recipes.
- **Behaviour.**
  - Cooling units act as paste hoppers.
  - Wall units block light.
  - Wall units are airtight.
  - Show the inspect-line climate readout.

**Cuisine:**
- Carbon-freezing press on/off.
- Carbon-shock chance.
- VCE ration-sealer reskin on/off. When off, VCE appears as shipped.
- Preservation-required recipes on/off. When off, the canon dishes accept fresh ingredients, so nobody gets locked
  out.

**The Sump:** tar-seal on/off, and tar-ruin chance.

**RUT:** stasis provisions in vault loot on/off.

## 7. Art needs

Every item goes through the art pipeline (`rimworld-art-evaluation`) and the review sheets. None of it reaches the
owner unread.

- **Buildings, single facing unless noted:**
  - Evaporative crock;
  - cooling supply unit;
  - wall cooling unit (wall-mounted, 4 facings);
  - cooling chamber (2x2);
  - cryo unit (1x2, 4 facings);
  - generic ancient stasis locker (Wrecked, Kludged and Refurbished looks);
  - Rakatan stasis casket and vault (Belsavis style; `canon_references/rakata/` is the visual target);
  - carbon-freezing press (2x2);
  - tar-sealing vat;
  - resin tap (tree-side);
  - resin jar shelf;
  - sand-drying box;
  - brine crock.

  Each machine also needs off/on state overlays. That makes 14 sprites plus 3 grade variants.
- **Items (icons):**
  - carbonite packs ×4;
  - tar-sealed ×4 and pitch-aged ×4;
  - resin-sealed ×3 and amber-aged ×3;
  - pickled ×4;
  - sand-dried ×3;
  - frost-aged ×2;
  - stasis provisions;
  - carbonite charge;
  - sealing resin.

  About 33 icons. Many are recolours of one base: a tar lump, an amber block, a jar, a carbonite slab.
- **Reskin:** VCE ration sealer, plus a ration-tin icon set (5).
- **Effects:** a stasis shimmer mote, a frost-up overlay and a carbon-steam mote.

## 8. Where it lives

| Mod | packageId | Holds |
|---|---|---|
| **Cold Storage** (new) | `mandrake.rm.coldstorage`, `src/RimMandrake/ColdStorage/` | The C# engine (§4.0), `ColdStorageMethodDef`s, evaporative crock, resin tap, resin jars and resin-seal, sand-drying, brine crock, plain salt-crust, frost-aged goods, generic `RM_AncientStasisLocker`. Settings. **No Star Wars words**, so it is publishable as layer 1. |
| Star Wars Cuisine | `mandrake.rsw.cuisine` (depends on coldstorage) | Cooling-unit ladder, cryo unit, carbon-freezing press and packs, Rakatan stasis skin (until layer 2 exists), canon preserved dishes, VCE ration-sealer reskin, SaltCrust tagging of the existing salt rations. |
| The Sump | `mandrake.rm.thesump` (optional dependency on coldstorage, gated by `PatchOperationFindMod`) | Tar-sealing vat, tar-sealed and pitch-aged goods. |
| StructureInjectionsRUT | `mandrake.rut.injections` | Chambers in vault loot, `RUT_StasisHeldProvisions`, the ship-subsystem grant of `RSW_RakatanStasis`. |
| Wrecked Machines | `mandrake.rm.wreckedmachines` | Nothing new. Coldstorage reads its grade signal if present. |

## 9. Build plan

The items are filed in rimflow and done in this order. Each step names the dependency it waits on.

1. `COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP`: the `mandrake.rm.coldstorage` skeleton.
   - C# `CompStorageClimate` (Chill/Stasis), the `AmbientTemperature` prefix with the bitmap cache, `CompSealed` plus
     the aging transition, `ColdStorageMethodDef`, settings.
   - Selftests on rot rate at a fixed temperature.
   - **Wait:** first.
2. `COLD_STORAGE_COOLERS_BUILD_RSW_LADDER`: the evaporative crock and the four RSW cooling units, with the wall
   propriety patch and the research. **Wait:** step 1.
3. `COLD_STORAGE_SEALS_BUILD_RESIN_SAND_BRINE`: resin tap and resin-seal, sand-drying box, brine crock, plain
   salt-crust, the aged defs. **Wait:** step 1.
4. `COLD_STORAGE_TARSEAL_BUILD_SUMP_VAT`: the tar-sealing vat in The Sump, and pitch-aged goods. **Wait:** step 1.
5. `COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS`: the press, the charge, the packs, thaw, carbon-shock.
   **Wait:** steps 1 and 2 (research chain).
6. `COLD_STORAGE_STASIS_BUILD_RAKATAN_CHAMBERS`:
   - the RM locker plus grades;
   - the RSW casket and vault skin;
   - the RUT vault loot, stasis provisions and ship-subsystem grant.

   **Wait:** step 1. (§10 Q2 is ruled: strength follows grade.)
7. `COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES`:
   - the canon dishes and the aged-product recipes that require methods;
   - the SaltCrust tag on the existing salt rations;
   - the VCE ration-sealer reskin.

   **Wait:** steps 3, 4 and 5.
8. `COLD_STORAGE_ART_BUILD_SPRITE_BATCH`: the §7 art through the pipeline and review sheet. **Wait:** can start
   after step 1, so the defs exist for sizing.
9. `COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE`: a live proof on the 13-mod minimal list plus Cuisine and The Sump.
   - Measured rot per mode.
   - Aging transitions.
   - Wall-unit propriety.
   - Gravship carry of the cryo unit.

   **Wait:** steps 2–7.
10. `RIMFRIDGE_DROP_FIX_INBOUND_REFS`: take RimFridge off the active list and fix every inbound reference in §1.
    That covers the validator self-loop entry, the proof_all noise list, the Cherry Picker line and the doc
    mentions; wrong material is deleted, not superseded. **Wait:** step 9 (§10 Q1 is ruled: drop after our units ship). This seat does not touch
    ModsConfig.

## 10. Questions for the owner (§2 only), both RULED 2026-10-26

Both questions were reserved under `delegation_policy.md` §2. Everything else above is delegated.

- **Q1** (§2.2, an irreversible act on his save): drop RimFridge now, or only after our cooling units ship?
  **Ruled by card (2026-10-26 08:11 PDT, `OWNER.jsonl:1793027547189804844`): option 1, drop RimFridge AFTER our
  units ship.** His words: *"We don't have saves to keep right now, remember?"* Save loss is not a concern; the
  order is kept so the colony always has cold storage. Step 10 follows step 2 shipping (and step 9's proof).
- **Q2** (§2.4, reconciling two of his rulings): full stasis at every working grade, or stasis *strength* following
  the Wrecked Machines 0.2 / 0.75 ladder? **Ruled by card (2026-10-26, `OWNER.jsonl:1793027548999599115`):
  strength follows grade** (0.2 / 0.75 / full). §4.2 carries the table; the engine hook is
  `COLDSTORAGE_STASIS_WIRE_GRADE_FACTOR`.
