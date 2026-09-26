# EXPLOSIVE_PLANT_GROWTH_1 — visible plant growth as a world mechanic

Born in the Cracked Lands enrichment (`biomes/the_cracked_lands.md` §10b), ruled
**world-wide** by the owner (verbatim on the filing event): water-soaked plants grow
VISIBLY — the player watches them get bigger, not animal-motion but growth — and it
should feel intimidating anywhere water soaks a plant. The jungles should visibly
grow.

**The design is ruled and lives in one place:**
`design/Jawa/worldbuilding/explosive_plant_growth_design.md` (owner sittings
2026-09-10, 2026-09-20, 2026-09-21; §9 indexes the rulings). The per-plant roster is
`design/RimUtinni/explosive_plant_growth_roster.md` (regenerated 2026-09-21 against
ruling 4). `FLOOD_WITNESS_EVENT_1` is the plot's guaranteed showcase.

## Build state — 2026-09-26 (FOUNDRY pass, static only)

Built and `dotnet build` clean (0 errors). **Not deployed, not loaded, nothing
live-verified.**

| piece | where | commit |
|---|---|---|
| ×10 wet-ambient band (Greentide/Miasma/Fever Wood, ruling 6) — a fourth band on the existing PlantGrowth postfix, replacing ×4 there, trees ×6.25 (🄸 keeps the ruled 2.5:4 ratio) | `src/RimUtinni/PlantGrowth/` | `19b2f9496` |
| The engine, new mod `mandrake.rm.explosivegrowth` (RM tier, no campaign names in code): sparse per-cell SOAKED + suppression grid (`RM_MapComponent_ExplosiveGrowth`), ×10 soak postfix on `Plant.GrowthRate` stacking on the ambient band, staged re-print of soaked wild plants (vanilla re-prints only cultivated plants per growth step — verified `Plant.TickLong`), overgrowth past natural size via `Plant.Print` prefix/finalizer scaling `visualSizeRange`, hue shift via `Plant.Graphic` postfix (Graphic_Single/Random only), the §2 tell ladder, the six tops, harvest jackpot (`YieldNow`), last-swing gamble (`PlantCollected`), soak routes, reflection API, BloomBurst worker, debug actions, full Mod Settings | `src/RimMandrake/ExplosiveGrowth/` | `5a91b3d46`, `5d246f7e5` |
| FloodedCanyon's soak stub RETIRED (its x6 `RM_Patch_Plant_GrowthRate` + `soakUntilTick` deleted); the flood hands its cells to the engine by reflection (`RM_ExplosiveGrowthBridge`) | `src/RimMandrake/FloodedCanyon/` | `09ce6fb4e` |
| Roster wired: RM-tier rows (AB_/RG_/vanilla/RM_) in the engine; campaign rows (RUT_/RSW_/SW donors), `noSoakBiomes` carve-outs and `RUT_BloomBurst` IncidentDef in `PlantGrowth/ExplosiveGrowth/`, loaded by `LoadFolders.xml` `IfModActive` only | both | `a3f1308ae` |
| Greentide M10 grazing hook AND M2 dry-air blower wired to the suppression grid (reflection, no hard dep) | `src/RimMandrake/EnvironmentalHazards/` | `555df9b7b` |

**The plant-variant shape** (for anyone wiring a plant): enum
`RimMandrake.ExplosiveGrowth.RM_GrowthTop` = `Churn` (default) / `Burst` / `Slime` /
`Tinder` / `Rupture` / `Flush` / `None`. Carried either as
`RM_ExplosiveGrowthExtension` on a def you own (`top`, `produceFactor`, `ringPlant`,
`slimeTerrain`) or as a row in any `RM_ExplosiveGrowthRosterDef` (`plants/li`:
`plant` string, `top`, `produceFactor`, `ringPlant`, `slimeTerrain`; plus
`exemptPlants`, `noSoakBiomes`, `rupturePawnKinds`, `ruptureMutationHediffs`,
`irrigationFluids`, `soakWeathers`). Rows are strings, so an absent donor is skipped,
never a def-eating cross-reference. The biome is never an input to the top; its only
input is the soak carve-out list.

**Soak routes (design doc §1):**
- `crack_flood` — BUILT (FloodedCanyon pushes every flooded cell).
- player irrigation — BUILT: a DUG FlowWorks cell holding `RM_Fluid_Water` soaks
  itself + 8 neighbours (natural rivers/lakes deliberately do not — `river_steam` is
  not a soak since 2026-09-21).
- `miasma_axis` fresh side — BUILT: while the gradient-axis surge shift runs, cells at
  salinity 0.25–0.48 (🄸 band) soak.
- `slime_flood` — PARTIAL, 🄸: slime-fluid FlowWorks channels irrigate; the Slime
  biome has no flood event of its own.
- `red_water` (Contagion rain), `scald_melt` — OWED: no weather/runoff system exists.
  The engine soaks on any `soakWeathers` WeatherDef a roster names; list is empty.
- Greentide extract — OWED: the item does not exist. Engine side is ready
  (`ExplosiveGrowthAPI.Soak`).

**Tops as built** (all counts/radii 🄸 INVENTED, Mod Settings tunable):
CHURN splits, drops produce (×produceFactor; former-GLUT rows 2.5), stump, 2–4 sprouts
r1.9 respecting floors/buildings/interiors. BURST pops, ×1.5 produce scattered, hay
chaff as husk-fuel, 2–5 blunt + short stun on pawns in r2.9 (skipped on pawns at ≤50%
health — injury+knockdown ceiling), 3–6 sprouts r2.9 ignoring zones/floors/doorways.
TINDER = Burst with more hay and a ring of `ringPlant` (quickgrass). SLIME: Churn-shaped,
ring terrain → `RM_Slime_Rich` (roster hard call 10's reading). RUPTURE: ToxGas cloud
(vanilla has no red gas; red is blood filth), spawns `AA_RedGoo`/`AA_OcularJelly` by
name, sprouts, and a one-hour cloud zone where pawns without VacuumResistance ≥ 1 roll
the Contagion's `RM_Unfinished*` limbs onto outside leaf parts. FLUSH: produce at the
foot, plant survives, no spectacle.

## Live verify 2026-09-26 (coordinator, 629-mod cold load) and the fix

- ✅ MEASURED live: startup line `569 plant defs soak … roster rows resolved 111,
  absent 24`; no crossref/configerror/patchfail naming the four touched mods;
  `RUT_ExtremeDesert` refused soak (0 cells), an ice-biome map accepted it.
- ❌ Found live: six soaked, Mature plants (one per top) sat at `charging=0` for
  >6,000 ticks, so no top, tell, `Plant.Print` scale or hue patch was exercised.
- **Cause (static trace, `537bc7d26`):** in the charge loop, `wet && GrowthRate > 0`
  advanced and EVERYTHING else decayed. A dormant plant (vanilla `GrowthRate == 0`:
  cold, zero fertility, out of season, blight) is wet but not growing, so it fell into
  the decay branch: `StartCharge` set 0.0001, the same pass subtracted
  250 / (15000 × 0.5) = 0.033, the charge hit ≤ 0 and was removed — every pass, so
  `charging` always read 0 (and the ground tell re-fired each pass). An ice-biome map
  makes every plant dormant. **Fix:** the clock is now a pure
  `RM_MapComponent_ExplosiveGrowth.StepCharge` — wet+growing advances, wet+dormant
  HOLDS, dry decays — and a plant only arms when `GrowthRate > 0`.
  `RM_ChargeSelfTest` runs the three regimes at every startup and logs
  `charge clock self-test PASS|FAIL`. The debug report now splits soaked plants into
  immature / matureDormant / charging / topNone, so a zero can be explained live.
- ⚠️ Consequence for the re-verify: on a cold map a frozen plant correctly does NOT
  charge. Re-run on a map where plants grow (temperate/wet biome, daytime temp in
  range, fertile soil) — Soak 5x5 here → wait > 250 ticks → Report should show
  `charging > 0` and climb; ~60 passes (6 h) to the top at defaults, or use
  "Charge all charging plants to 0.9". **Live re-verify is OWED** — the bridge was
  held by BENCH (Scald round) when the fix landed; it was not taken.
- Also still owed from that load: the ×10 wet-ambient band (needs a wet-biome map).

## Owed

1. **The perf gate** (design doc §5) — TPS/frame-time on a jungle-density quicktest,
   {soaked plants} × {re-print cadence} × {dynamic-draw cap}. Needs a live load. No
   density is promised until it exists.
2. **Live proof of every mechanism** — nothing here has run in game. A load needs:
   `mandrake.rm.explosivegrowth` added to the mod list (it is NOT in any list yet)
   before `mandrake.rut.plantgrowth`; the startup log line `[RM ExplosiveGrowth] N plant
   defs soak (churn…)` with roster rows resolved/absent; then the debug actions
   (`RMExplosiveGrowth` → Soak 5x5 here / Charge all to 0.9 / Fire top here) to watch
   swell, hue, tremble, creak and each top.
3. The **dynamic-draw close-up layer** (§5 option 2, smooth swelling + real tremble) —
   not built; the staged re-print ships alone, with the tremble as a ±3.5% alternating
   re-print plus dust puffs.
4. Cut-vs-harvest distinction: §4 says cutting forfeits the jackpot; the `YieldNow`
   bonus currently applies to any yield from a charged plant.
5. Salted ground refusing the soak (§4 🄸) — no salt verb exists.
6. FLUSH's inside-the-giant presentation (bark swell, boughway re-route, thornbug
   nectar glut) — the Fever Wood kit's to draw.
7. Roster micro-questions, INVENTED defaults used (roster "UNMEASURED"): hoarders are
   `NONE`; the extract overriding CHURN→BURST is unbuilt (no extract); irrigation in a
   ×10 biome soaks and stacks (§0/ruling 8 reading).
8. Bespoke sounds — the creak/split/pop/rupture are vanilla tree clips re-pitched.
9. Pre-existing, not this item's: PlantGrowth's terminator list names only
   `PoisonForest`, not `RUT_PoisonForest`/`RM_PoisonForest`, and it does not exempt
   `RUT_ExtremeDesert` from ×4 (deep_desert HARD BAN 4). The engine's soak carve-out
   covers all four; the ambient band does not.
