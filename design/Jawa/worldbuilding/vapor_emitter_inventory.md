<!-- status: live -->
# vapor_emitter_inventory.md — every vapor/smoke/gas emitter on Ash'karr, and the decay law per type

`VAPOR_EMITTER_PLACEMENT_1` scopes 1-2 (inventory + placement rules). Scopes 3
(live-map audit) and 4 (bridge fix-up) are **flagged at the bottom, not done here**
— owner AFK, game DOWN, this pass is offline-only.

**The owner's ruled law** (filed on the item, verbatim): steam-geyser-type emitters
**radially decay away from mountain/volcanic sources and reach ZERO before the
terminator** — the deep nightside and the seam never see them. Every OTHER vent
type needs the same treatment: inventory, then a placement rule per type.

## 0. Provenance

**MEASURED against `OFFICIAL-2026-08-29`** (frozen, 584 mods,
`modlist_sha 5c47dd8885eda025`, capture
`.../DefDump/captures/2026-08-29T13-30-02Z`) — the design target per
`infrastructure/state/dumps/README.md`. `defs.sqlite` was rebuilt this session
from that exact capture (clean: 79,288 defs / 535 types, `absent=0 shadowed=0
ambiguous=0 orphan=0 partial=0 failed=0` — no collision damage, per the
`measuring-large-artifacts` skill's own incident history). Every count below is
tagged MEASURED (with the instrument) or UNMEASURED (with why); nothing here is a
scan of the dump — a scan of the def dump reads one giant line and lies (see
`measure explain DefDump`).

**Prior work cited, not redone**: `unused_mutators_census.md` already MEASURED
the live world's 88 in-use `TileMutatorDef`s against
`world/ASHKARR_WORLDMAP_mutators.csv` (2026-09-06, superseded totals but the
in-use-name roster stands) and the full unused-mutator list against a *different*,
596-mod capture — its per-def counts are cited by name, not re-measured; its
absolute totals (343/255) diverge slightly from this session's 584-mod official
count (336 `TileMutatorDef`) because the two captures are different mod-list
snapshots, not because either is wrong. `tile_augmentation_catalogue.md` §2's A1–A9
rows are cited for the green-gas/helixien family, which it analysed in depth and
this file does not repeat.

## 1. The typed inventory

**22 emitter-type families MEASURED** in the official dump (`ThingDef` +
`TileMutatorDef` + `GenStepDef` + `LandmarkDef`, deduped by mechanism), plus one
biome-level phenomenon (poison forest cold vents) that has **no discrete def** —
UNMEASURED as an object, confirmed as biome chemistry from the sheet text.
Decor-only duplicates (VFEPD props) and one quest-scoped machine are listed but
excluded from the placement-law scope.

| # | family (defName / mutator) | type(s) | source mod | MEASURED | what it does |
|---|---|---|---|---|---|
| 1 | `SteamGeyser` + `GenStepDef SteamGeysers` | ThingDef, GenStepDef | Core (vanilla) | MEASURED exists (dump) | the base steam vent building; commonality set by the biome's own field (dump has **no statBases/field-level export** — `def-dump-has-no-statbases` blind spot — UNMEASURED at the density-field level, confirmed live only) |
| 2 | `SteamGeysers_Increased` | TileMutatorDef | Odyssey | **MEASURED in-use** on Ash'karr (`unused_mutators_census.md` Part 1, cross-checked against `world/ASHKARR_WORLDMAP_mutators.csv`) | raises geyser count factor on a tile above baseline |
| 3 | `VEE_SteamGeysers_Decreased` | TileMutatorDef | Vanilla Landmarks Expanded | MEASURED unused on Ash'karr (absent from the 88-name in-use list) | the inverse knob — lowers geyser density |
| 4 | `GeothermalVent` ("sulfur spout") + `GenStepDef GeothermalVents` | ThingDef, GenStepDef | Odyssey | MEASURED exists; in-use status UNMEASURED (workerClass gate logic not captured in def data, per census's own caveat) | a second geothermal-family building distinct from `SteamGeyser` |
| 5 | `HotSprings` | TileMutatorDef | Odyssey | **MEASURED in-use** on Ash'karr (mutators.csv) | terrain-only geothermal tile (no separate scatterable building found) |
| 6 | `AB_MagmaVent` + `AB_MagmaVents` mutator | ThingDef + TileMutatorDef | Alpha Biomes | **MEASURED in-use** (mutators.csv) | a magma-family vent building, already sited on/near the Forge |
| 7 | `AB_MagmaticQuagmire` | TileMutatorDef | Alpha Biomes | **MEASURED in-use** | magma-adjacent terrain hazard, no distinct building found |
| 8 | `AB_GeothermalHotspots` | TileMutatorDef | Alpha Biomes | **MEASURED in-use** | geothermal terrain hazard |
| 9 | `LavaCrater` / `LavaFlow` / `LavaLake` (+ `LavaCaves` unused) | TileMutatorDef | Odyssey (vanilla) | **MEASURED in-use** (3 of 4; `LavaCaves` unused) — these ARE the Forge's own zonation per `the_forge.md` | the volcanic massif terrain itself, not a separate "vent" object — the epicenter, not a decayed instance |
| 10 | `VEE_RotstinkVent` + `VEE_RotstinkVents` mutator | ThingDef + TileMutatorDef | Vanilla Landmarks Expanded | **MEASURED in-use** (mutators.csv; also cross-confirmed by `VEE_RottenStench` in the same 88-list) | a "rotstink geyser" — decay-gas themed, not obviously geothermal |
| 11 | `VEE_SmokeVent` + `VEE_SmokeVents` mutator | ThingDef + TileMutatorDef | Vanilla Landmarks Expanded | MEASURED unused on Ash'karr (absent from 88-list) | smoke geyser hazard |
| 12 | `VEE_ToxicVent` + `VEE_ToxicVents` mutator | ThingDef + TileMutatorDef | Vanilla Landmarks Expanded | MEASURED unused | toxic geyser hazard |
| 13 | `VEE_DeadlifeVent` + `VEE_DeadlifeVents` mutator | ThingDef + TileMutatorDef | Vanilla Landmarks Expanded | MEASURED unused | deadlife-gas geyser hazard |
| 14 | `VEE_SulfurVent` (fissure) + `GenStepDef VEE_SulfurVents` | ThingDef + GenStepDef | Vanilla Landmarks Expanded | MEASURED exists; **no matching TileMutatorDef found** in the official dump (checked explicitly) — placement mechanism UNMEASURED, flag for a live contact-sheet | a "sulfur fissure" |
| 15 | `AncientHeatVent` (+ matching TileMutatorDef + LandmarkDef, all three types share the name) | ThingDef + TileMutatorDef + LandmarkDef | Odyssey | **MEASURED in-use** (mutators.csv) — and **already the site of a named Jawa sacred object**: `the_forge.md` §8 names "his LavaLake/LavaCrater sites, the AncientHeatVent's 'right kind of joke'" on the Forge itself | an ancient-artifact heat vent, not geologic magma |
| 16 | `AncientSmokeVent` (ThingDef+Mutator+Landmark) | as above | Odyssey | MEASURED unused | ancient-artifact smoke vent |
| 17 | `AncientToxVent` (ThingDef+Mutator+Landmark) | as above | Odyssey | MEASURED unused | ancient-artifact toxic vent |
| 18 | `AB_AncientBloodRainVent` (ThingDef+Mutator) | as above | Alpha Biomes | MEASURED unused | ancient weapon/hazard vent — triggers a blood-rain event, not a gas cloud |
| 19 | `AB_AncientDeathPallVent` (ThingDef+Mutator) | as above | Alpha Biomes | MEASURED unused | ancient weapon/hazard vent — death-pall (toxic) |
| 20 | `AB_AncientFreezingVent` (ThingDef+Mutator) | as above | Alpha Biomes | MEASURED unused | ancient weapon/hazard vent — freezing |
| 21 | `AB_AncientGreyPallVent` (ThingDef+Mutator) | as above | Alpha Biomes | MEASURED unused | ancient weapon/hazard vent — grey-pall |
| 22 | `VHGE_GasGeyser` | ThingDef | Vanilla Helixien Gas Expanded | MEASURED exists; **zero TileMutatorDef/LandmarkDef/GenStepDef ships for it** (checked explicitly — none exist) | the green/helixien tibanna-adjacent gas geyser; placement is **wholly unbuilt** — `tile_augmentation_catalogue.md` A3-A5 already found this and calls for a new mutator to be authored |
| — | Poison forest cold gas vents | biome chemistry, no discrete def found | (native to `poison_forest.md`) | UNMEASURED as an object — confirmed from sheet text only: "cold gas venting" is the biome's driving force (§3), explicitly **not** steam/lava/magma/geyser (§6 hard ban) | the terminator's own emitter family — see §2 below, ruled OUT of this law by design |
| — (excluded) | `VFEPD_Geyser`, `VFEPD_GeothermalVent`, `VFEPD_SmallVent`, `VFEPD_TinyVent`, `VFEPD_VentilationShaft`, `VFEPD_MeatSmoker*`, `VFEPD_AB_Ancient*Vent`, `VFEPD_AncientHeatVent` etc. | ThingDef (decor) | VFE – Props and Decor | MEASURED exist, all decor duplicates of rows above | player-placed cosmetic props, non-functional, no map-gen placement — out of this law's scope |
| — (excluded) | `VQE_Genetron_ThermalVent` | ThingDef | Vanilla Quests Expanded – The Generator | MEASURED exists | quest-site-scoped machine, not a general biome placement — out of scope |
| — (excluded) | `Vent`, `Vent_Over`, `WallVent`, `OuterRim_VentedFloor_*`, `AtmosphericHeaterGlowingVents` | ThingDef/Mote | Core, Replace Stuff, WallStuff, Outer Rim, Anomaly | MEASURED exist | building **airflow/climate** furniture and a heater's cosmetic mote — false-positive matches on "vent," not vapor emitters |

## 2. Placement rule per type — RULED vs PROPOSED

RULED = follows directly from the owner's law or an existing frozen biome sheet.
PROPOSED = my extension to a type the owner never named; flagged, not decided.

| type / family | biomes allowed | decay anchor | banned zones | R/P |
|---|---|---|---|---|
| `SteamGeyser` + `SteamGeysers_Increased`/`VEE_SteamGeysers_Decreased` | dayside generally (Desert, Wasteland, Dune Sea, the Scald, Weeping Stones seep oases) | radial distance from **the Forge** (Dune Sea interior massif, the law's own named epicenter) and **the Scald** (substellar crater — the sheet itself calls it *"the vapor law's second densest ground after the Forge"*) | nightside (already hard-banned, `nightside_ice.md` §6), the terminator/seam (poison forest + terminator sea), Rust Cathedral (no tectonics, §below) | **RULED** — this is the law verbatim |
| `GeothermalVent` (sulfur spout) + `HotSprings` | same dayside volcanic-adjacent set as `SteamGeyser` | same Forge/Scald radial decay | same bans | **RULED** (same geothermal family) |
| `AB_MagmaVent` + `AB_MagmaVents`/`AB_MagmaticQuagmire`/`AB_GeothermalHotspots` | Forge-adjacent Dune Sea tiles (already how Alpha Biomes ships and how it's assigned) | radial from **the Forge specifically** — magma is the Forge's own signature material | everywhere else; strict ban nightside/terminator | **RULED** (magma is Forge-native by the sheet's own text) |
| `LavaCrater`/`LavaFlow`/`LavaLake`/`LavaCaves` | the Forge massif tiles only | none needed — these tiles ARE the epicenter (zero decay distance) | everywhere outside the Forge | **RULED** |
| `VEE_RotstinkVent(s)` | currently in-use somewhere on Ash'karr (biome unverified offline — needs scope-3 read); chemistry reads as decay-gas, not geothermal | UNCLEAR whether radial-from-mountain applies at all if it is biological/decay-sourced rather than volcanic | if non-volcanic, no terminator/nightside ban follows automatically from this law | **PROPOSED** — owner never named this type; treat as exempt from the radial law pending his call |
| `VEE_SmokeVent(s)`, `VEE_ToxicVent(s)`, `VEE_DeadlifeVent(s)` | all currently unused on Ash'karr | if ever assigned: same open question as Rotstink — VLE's "geyser" family reads as ancient-danger/decay hazard, not magma-driven | PROPOSED: ban from the deep nightside interior regardless of source chemistry (nothing plausibly bursts through kilometres of dead ice), keep dayside siting a free design choice | **PROPOSED** |
| `VEE_SulfurVent` (fissure) | placement mechanism itself UNMEASURED (no mutator found) | two candidate anchors: (a) Forge/Scald volcanic decay, since sulfur reads geologic, OR (b) Rust Cathedral's own sulfuric pools, which are explicitly canon dressing there (`the_rust_cathedral.md` §6 ban #5: *"No true acid terrain: sulfuric dressing only"* — i.e. sulfuric IS present there, just cosmetic) | — | **PROPOSED**, genuinely two-anchor; owner call needed (Q1 below) |
| `AncientHeatVent` | in-use on Ash'karr, and already a named Jawa sacred site **on the Forge itself** | tied to the Forge already by lore — consistent with the radial law without any change | should not appear nightside/terminator under the general vent bans | **RULED** as currently sited; **PROPOSED** extension below |
| `AncientSmokeVent`, `AncientToxVent` | unused currently | same ancient-artifact family as `AncientHeatVent`; Rust Cathedral's droid-enclave names are literally *Vent Nine*, *Vent Forty*, *Vent Twelve* (`the_rust_cathedral.md` §8) — a strong textual hook to site this family there as **machine** vents, decaying by ancient-ruin/artifact density, never by distance to magma | — | **PROPOSED** — the owner never ruled the Cathedral hosts this family; flagged as Q2 |
| `AB_AncientBloodRainVent`/`DeathPallVent`/`FreezingVent`/`GreyPallVent` | unused currently | **not** a steam/geothermal family at all — each triggers a specific ancient-weapon hazard (blood rain, toxic pall, freezing, grey pall); siting should follow that hazard's own chemistry, not mountain distance | out of this law's scope entirely | **PROPOSED**, flagged out-of-scope rather than ruled |
| `VHGE_GasGeyser` (green/helixien gas) | per `tile_augmentation_catalogue.md` A3-A5: Desert/ExtremeDesert/Wasteland/Scarlands | placement is wholly unbuilt (no mutator exists to author yet); no natural reason to tie chemical seepage to volcanic distance — could instead be flat-rate biome commonality, or tied to Rust Cathedral's collapsing ancient chemical works | — | **PROPOSED**, and separately blocked on the pump-strip prerequisite the catalogue already names (`required_mods.md:489-492`) |
| Poison forest cold gas vents | terminator/seam **only** (`poison_forest.md`, `hydrology_and_fire_ecology.md` R-H2b) | **not** decay-from-mountain — driven by the terminator's own thermal-boundary mechanism (warm dayside gas meeting frozen nightside rock); this is exactly the "cold-gas types separately" carve-out the item itself names | hard-banned from both dayside interior and nightside interior by the biome's own chemistry (`poison_forest.md` §6: *"No volcanism, lava, magma, steam or geysers. The vents are COLD."*) | **RULED** — confirms this family is categorically NOT steam and is exempt from the radial law by design, not omission |
| Weeping Stones seep oases (vent-fed pools) | Cratercrown / Anvil tiles (~35 hot aberrant oases, up to 63 °C) — fed by "groundwater and vent-warmed springs rising through the rock... near vulcanism" (`weeping_stones.md` §2b) | radial from the nearest volcanic source (Forge or Scald, whichever nearer) — the sheet explicitly defers this exact question to this item | outside vulcanism range, an oasis must revert to ordinary dew-fed status, not seep-fed | **RULED** — directly named in the item's own "known couplings" |
| Nightside (all steam/geothermal) | none | n/a | total ban — `nightside_ice.md` §6 names vents, geysers, geothermal, volcanism, hot springs and fumaroles explicitly | **RULED** (pre-existing sheet ban; the owner's law doubles it) |
| Rust Cathedral (as a *natural* steam host) | none | n/a — "time stopped here... no tectonics" (`the_rust_cathedral.md` §3) | banned as a natural source; may still host the ancient-artifact vent family (see `AncientSmokeVent`/`AncientToxVent` row) under a separate, non-radial rule | **RULED** (natural ban) / **PROPOSED** (artifact-vent hosting) |

## 3. Flagged remainder — NOT done tonight

### Scope 3 — the live-map audit, and what instrument it actually needs

**Two different questions hide inside "audit the map against the rules," and they
need two different instruments:**

1. **Per-tile mutator PRESENCE** (does tile X carry `HotSprings`/`AB_MagmaVents`/
   `AncientHeatVent`/etc.) is **world data, already offline and readable right
   now** — `world/ASHKARR_WORLDMAP_mutators.csv` joined against
   `world/ASHKARR_WORLDMAP_tiles.csv` for arc/position. **No bridge, no game load
   needed** to check whether the currently-assigned vent mutators actually decay
   away from the Forge/Scald and hit zero before the terminator — that is a CSV
   join and a distance calc, doable tonight if this item's scope had included it
   (it explicitly does not — scope 3 is reserved).
2. **Actual `SteamGeyser`/`AB_MagmaVent`/etc. BUILDING COUNT on a tile** only
   exists once a **Map is generated** there (`GenStep_ScatterThings` runs on
   arrival, per `tile_augmentation_catalogue.md` §7.1's world-tile vs. Map
   distinction) — this half genuinely needs the bridge/a quicktest map, one per
   sampled tile, and cannot be read from any world CSV.

So scope 3's instrument is **CSV-join first (free, offline), bridge-sampling
second (to confirm the mutator actually produces the expected building density on
landing)** — not a single audit pass.

### Scope 4 — bridge fix-up

Not touched. Waits on scope 3's findings and a game-up session; flagged per the
item, not started.

## Owner questions

1. **VLE's four "geyser" hazards** (`VEE_RotstinkVent`/`SmokeVent`/`ToxicVent`/
   `DeadlifeVent`) and Alpha Biomes' four `AB_Ancient*Vent` hazards — are these
   part of the steam-decay law at all, or a separate ancient-danger/decay-gas
   family exempt from it? This inventory treats them as exempt (their chemistry
   reads as biological/artifact, not geothermal) but that is my read, not his.
2. Should the ancient-artifact vent family (`AncientHeatVent`/`SmokeVent`/
   `ToxVent`) be sited on **Rust Cathedral** ground as machine-vents — matching
   its droid-enclave names *Vent Nine*, *Vent Forty*, *Vent Twelve* — even though
   the Cathedral is banned as a *natural* steam source ("no tectonics")?
3. `VHGE_GasGeyser`'s placement mutator is entirely unbuilt. Should its future
   density knob follow the same Forge/Scald radial-mountain decay, or an
   independent chemical-seepage rule (the catalogue's own working assumption,
   never ruled)?
