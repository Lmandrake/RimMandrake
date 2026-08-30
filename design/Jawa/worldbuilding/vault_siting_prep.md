<!-- status: live -->
# Vault siting prep — for the VAULT_DUNGEON_CONCEPT_1 owner sitting

> 🔶 **PROPOSAL THROUGHOUT.** Nothing below is ruled. Prepared 2026-08-30 for
> point 1 of the sitting brief in
> `infrastructure/state/items/VAULT_DUNGEON_CONCEPT_1.md`
> ("COUNT + SITING: how many vault sites on the frozen world, which tiles").
> The owner rules count, mix and exact tiles at the sitting; this is the
> candidate menu, not a decision.

## Source and currency

Frozen world doctrine: `design/Jawa/worldbuilding/the_one_map.md`. Numeric
definition: `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md`. Canon
triad and Rust Cathedral: `design/Jawa/reconciled_lore/03_deep_history.md`.

Bundle stem used: **`world/ASHKARR_WORLDMAP`** — the stem `infrastructure/state/canon.yml`
and `FDE_NIGHTSIDE_VERIFY_1` both cite as the live frozen bundle, and `worldview.py`
takes this stem directly. Read fresh this session, not reused from a stale dump:

| file | rows measured | matches doc |
|---|---|---|
| `world/ASHKARR_WORLDMAP_tiles.csv` | 21,872 | yes — `ASHKARR_WORLD_DEFINITION.md` §1 |
| `world/ASHKARR_WORLDMAP_settlements.csv` | 121 | plausible post-08-26 Wildsteam additions (doc's 108 predates them) |
| `world/ASHKARR_WORLDMAP_landmarks.csv` | 563 | — |
| `world/ASHKARR_WORLDMAP_links.csv` | 1,665 (road+river) | — |

⚠️ One decay in the settlements CSV, noted so it isn't mistaken for a siting
error below: the `biome` column for the six Free Droid Enclave seats the
08-24 ruling moved onto Cathedral ground (Cell Seven, Vent Twelve, No Owner,
Vent Forty, The Cracking Yard, Second Speaker) still reads `ExtremeDesert` /
`ZBiome_Grasslands`, not `AB_MechanoidIntrusion` — the biome column is stale,
the `tile` id is current. Settlement-exclusion below was done **by tile id**,
not by biome label, so this does not affect the free/occupied calls.

## How tile-freedom was verified (not a duplicate of FDE_NIGHTSIDE_VERIFY_1)

Built the full settlement-tile set from `ASHKARR_WORLDMAP_settlements.csv`
(121 tile ids, all 12 factions) and rejected any candidate whose tile id is
in that set. This is a broader check than `FDE_NIGHTSIDE_VERIFY_1` (which
verifies Free Droid Enclave nightside siting only) — it is not a duplicate,
and I did not re-derive or restate their FDE nightside finding. I did read
`world/ASHKARR_WORLDMAP_settlements.csv` for the same purpose they did
(tile-freedom checks), which the task explicitly allows.

**Incidental count, filed here per the task's instruction, not in their item:**
of the 236 `AB_MechanoidIntrusion` biome tiles, **zero carry a settlement tile
id**, even though six Free Droid seats are conceptually "on Cathedral ground"
per §7d of the world definition — those seats sit on adjoining halo tiles
(`ExtremeDesert`/`ZBiome_Grasslands`), not inside the 236-tile biome core
itself. All six vault candidates below were independently checked
settlement-free by tile id (table has the distances).

## The canon this leans on

- **Triad** (`03_deep_history.md`): ① mechanoid garrison, vault held; ②
  flesh weapon loose, vault fell; ③ frozen Rakata, rare, the emotional scene.
- **Two threat classes are not interchangeable** (`ASHKARR_WORLD_DEFINITION.md`
  §6c): `AB_MechanoidIntrusion` and `Wasteland` are **contamination** (ground,
  air, water poisoned — no Anomaly casting). `HorrorWastes`,
  `AB_GelatinousSuperorganism`, `AB_OcularForest`, `Scarlands` are **bioweapon**
  (the wildlife itself is the danger, engineered and still alive). ⇒ type-①
  garrisons belong on contamination ground (the Cathedral); type-② breaches
  belong on bioweapon ground, because "flesh weapons loose" *is* the bioweapon
  class, not the contamination class.
- **Rust Cathedral** = `AB_MechanoidIntrusion`, exactly 236 tiles, region
  `Rust Cathedral` (arc < 12.5), with a measured four-ring pollution halo
  bleeding into the adjoining `Scorch` region (arc 12.5–17) — a decay gradient
  already painted on the map, not something to invent.
- Existing `AncientGarrison`/`AncientWarehouse`/`AncientLaunchSite` landmarks
  are pre-authored "somebody defended/sealed this" tiles — six candidates
  below sit ON one of these, so the siting is grounded in gazetteer content
  that already exists rather than picked blind.

## Candidates

| # | tile | arc / bearing (lat, lon) | biome / region | landmark | type | why here | conflicts |
|---|---|---|---|---|---|---|---|
| **V1** | 678 | 10.31° / 47.4° | `AB_MechanoidIntrusion` / **Rust Cathedral** (core) | `AncientGarrison` — "somebody defended this once" | **①** mechanoid garrison, vault held | Inside the 236-tile Cathedral biome itself, at Arsenal's densest per `03_deep_history.md`; a pre-authored garrison landmark, not an invented one. Elev 624 m, 60.7 °C, Flat (hilliness 1) — reads as the "floor" §7d insists the Cathedral is | Nearest settlement **No Owner** (Free Droid Enclaves) 9.4° away, on adjoining halo ground the Enclaves hold sacred; digging here risks the −15/Building desecration hysteresis (`03_deep_history.md`). Not on a road — `allowRoads=false` on this biome, so no caravan approach exists by design |
| **V2** | 4000 | 16.66° / 33.3° | `Scarlands` / **Scorch** (Cathedral's own halo) | `AncientLaunchSite` — landmark text *literally* names "The Rust Cathedral — mechanoid ground, permanently at war" | **①** — outer works of the same complex, breached-approach flavor | Sits in the measured pollution halo ring (0.66→0.18 falling outward from the 236-tile core) — the decay-gradient atmosphere the sitting asked for is already painted here, not proposed. Pairs naturally with V1 as an "outer works" entrance if the concentric-map structure (sitting point 2) is ruled | Only **3.1°** from **No Owner** (FDE) — the closest candidate to a live settlement of any of the six; if the owner wants a vault the Enclaves actively contest, this is it |
| **V3** | 9167 | 60.09° / 8.1° | `ExtremeDesert` / **Fall Line** | `AncientGarrison` — "somebody defended this once" | **①** — Arsenal-guarded, away from the Cathedral | Route-spread: a second, independent garrison vault far from the substellar point (49° of arc from V1), so not every ① raid is a Cathedral trip. Sits in the same region as the Empire's **Ashgarrison** chokepoint seat (Fall Line pass) | 7.4° from **Zeddo's Toll** (Hutt Cartel); the Fall Line pass itself is one of only 3 Empire world holdings (`ASHKARR_WORLD_DEFINITION.md` §7) — an Imperial patrol route runs directly past this candidate |
| **V4** | 17461 | 127.57° / 195.7° | `HorrorWastes` / **Deadstone** | `AncientWarehouse` — "sealed, and worth the trip" | **②** — flesh weapon loose | `HorrorWastes` is bioweapon-class by the §6c ruling: "ancient bioweapons that adapted... utterly hostile lifeforms." Sits at the **warm edge** of the band (−35.5 °C, arc 127.6, vs the band's −55…−30 °C range) — closest HorrorWastes ground to the dayside, so a crew doesn't need a deep-nightside expedition to reach a type-② site | 15.0° from **Specimen Hall** (Ascendant Helix) — the Helix is canonically sited "where the bioweapon is" (§7), so they have an active research interest in whatever is loose here; a quest-hook rival, not a settlement occupying the tile |
| **V5** | 37 | 90.0° / 79.0° | `AB_GelatinousSuperorganism` / **Slough** | none pre-placed | **②** — flesh weapon loose, second instance | Terminator patch of the biome `03_deep_history.md` names directly as one of the flesh-weapon's naturalised homes ("escaped and naturalised in... the gelatinous superorganism"). Sits exactly on the terminator (arc 90.0), giving a second ② reachable from the opposite play route (meridian dayside-edge vs. V4's deep-nightside approach) | 10.4° from **Dripstone** (Homestead Defense League) — a moisture-farming settlement near a live bioweapon patch is its own tension; no landmark here yet, so this candidate needs one authored if picked |
| **V6** | 20853 | 159.7° / 310.0° | `AB_PropaneLakes` / **Umbra** | `AncientWarehouse` — "sealed, and worth the trip" | **③** — frozen Rakata (the one) | Deepest nightside of any candidate (−70.2 °C, arc 159.7, past the "only the most alien life" line the `03_deep_history.md`/§6c ruling draws at arc ≥ 150) — remoteness and cold are literal here, not metaphorical, which is what the sitting brief asked a ③ site to carry. Farthest from any road (20.3°) and any settlement (20.3°, **The Cracking Station**, FDE) of all six candidates — the rare scene the canon calls for is not a stop on the way to anywhere | Only the FDE's two deep-nightside refugee seats (Coldfire, The Cracking Station — see `FDE_NIGHTSIDE_VERIFY_1`) are anywhere nearby, and both sit 20°+ away; effectively conflict-free, which is itself worth flagging as maybe *too* isolated to ever get visited |

**Mix as proposed: ①×3 (V1, V2, V3), ②×2 (V4, V5), ③×1 (V6) — 6 total**,
inside the sitting brief's own 5–7 proposal and its "one ③ only" line.
V1+V2 can double as the concentric outer-works/core pairing from sitting
point 2 if the owner wants that structure demonstrated on one complex before
ruling it doctrine.

## Route spread

Arc spread: 10.3° (V1) to 159.7° (V6) — dayside plateau, meridian desert,
terminator, warm nightside, deep nightside. Distance to nearest road ranges
3.1° (V2, V3) to 20.3° (V6): some candidates sit near the road net for an
easy first raid, V6 is deliberately off every route for the rare scene.

## Look-once map

`Transient/vault_siting_prep.png` — biome-layer equirectangular render of the
live bundle (`worldview.py world/ASHKARR_WORLDMAP --layer biome`), unmarked
(the tool has no pin/highlight mode). Cross-reference by arc/bearing from the
table above; this PNG is not the only copy of anything — it is disposable
render output and can be regenerated from the same command.
