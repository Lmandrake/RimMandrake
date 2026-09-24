# FlowWorks Liquid Matrix — the six faces × the liquid registry

**Status: DRAFT for the `FLOWWORKS_LIQUID_FACES_1` sitting.** Design prose only — no XML, no C#.
Written 2026-09-24 by a design subagent against the ticket, the LiquidDef registry
(`design/RimMandrake/liquids_framework_design.md` §3), the tar pilot
(`SUMP_TAR_HYDROLOGY_1`), the biome/mod architecture
(`design/RimMandrake/biome_mod_architecture.md` §2/§2a–2c), and the frozen biome sheets'
head sections. Sheets are FROZEN: nothing below contradicts a sheet ruling; where a sheet
names its liquid story, that IS the answer here.

## 1. Scope and laws carried in

These are already ruled or MEASURED; the matrix applies them, it does not reopen them.

1. **The six faces** (ticket table): floods (FlowWorks pulsed spread) · rain (weather
   form slot; tar rain is the pilot) · rivers · lakes (terrain bodies + landmark meres;
   the Deep Black is the pilot) · oceans (**map-scale and lore ONLY** — the frozen world
   map is not touched until the paint pass) · **ground pump** (buildable on-site
   producer; every YES is a Mod Settings toggle by ruling — scenario-dependent).
2. **The edge law** (`SUMP_TAR_HYDROLOGY_1` ruling 6, engine law for ALL liquids): a
   canal dug to the map edge is a **sink for any liquid**; edges are **never sources**;
   sources are local and as rich as needed; an on-map ocean, canal-connected, is
   effectively an **infinite source**.
3. **The native-liquid ruling** (ticket, owner typed 2026-09-24): each biome declares
   **one native liquid** — what saturates its ground and/or falls from its sky — or
   explicitly NONE. Any other liquid may sit on the surface as a **guest** for local
   reasons. Presence is free; nativeness is declared.
4. **Multi-liquid maps are engine-native** (MEASURED, per the ticket): `waterBodyType`
   bodies coexist on one map and rebuild on terrain change. No engineering blocker to a
   map carrying two liquids.
5. **Scarcity is stock, not rate** (framework §4, owner reversal 2026-09-16): every
   source carries real volume; "infinite" only means stock too large to exhaust.
6. **The mod-vs-scenario split** (tar rain, ruling 1): a dangerous face can ship in the
   MOD and stay OFF in the Ash'karr campaign scenario. Cells below marked "mod-only"
   use exactly this split.
7. **The registry rows are the matrix rows.** No liquid is invented here. Deferred
   registry rows (lava, coolant, ammonia, machine oil, brackish, hemogen/beer/milk,
   kolto/bacta) get no matrix row — where a biome's fiction wants one, it is an
   annotation, not a cell.

## 2. The matrix — liquids × faces

Cell values: **YES** (with the hosting biome/mod) · **NO** (one-line reason) ·
**LATER** (plausible, not owed by any current sheet or ruling). "Mod-only" = ships in
the named mod, off in the campaign scenario, per law 6. Tar's row is largely
**RULED** — carried in from `SUMP_TAR_HYDROLOGY_1`, cited per cell.

| liquid | floods | rain | rivers | lakes | oceans (map-scale/lore only) | ground pump | native of |
|---|---|---|---|---|---|---|---|
| **Fresh water** | **YES** — FloodedCanyon (the Cracked Lands' flash flood is the sheet's thematic handle; FlowWorks is already its flood engine, arch. §2d) | **YES** — the planet's own rain law (R-H1: only at the greatest altitudes; Contagion peaks, Cracked Lands' Dew Horn) | **YES** — the world's rivers exist; Greentide (85% river tiles) is the showcase | **YES** — Weeping Stones oasis landmarks (hand-placed, ruled); canyon pools | **NO** — no fresh ocean was authored on the frozen world; the seas are salt/brine/boiling/propane | **YES** — the well/borehole; the least controversial pump | Greentide · Weeping Stones · FloodedCanyon · LeaningScrub · Webwork · FeverWood · Pyrelands (sky) |
| **Salt water** | **YES** — Miasma delta surge (the sheet's own word: "surge, salt") | **NO** — salt rain is physical nonsense at map scale | **NO** — rivers are fresh by definition; the salt is where they end | **LATER** — a coastal lagoon needs no v1 owner | **YES** — the Twilight Sea (`RM_TwilightSea`, TerminalBiomes); canal-connected shore = infinite source per edge law | **YES** — coastal intake well; feeds desalination play (framework: salt → fresh at stills) | TwilightSea · Miasma (OPEN, §3) |
| **Boiling water** | **LATER** — a Scald-shore geyser surge event is flavor-plausible, owed by nothing | **NO** — scalding rain is a weapon, not weather; the Scald's "clean breath" falls elsewhere as ordinary rain | **NO** — cools to fresh the moment it leaves the heat source | **NO** — the one boiling body is the sea itself | **YES** — the Scald (`RM_TheScald`, TerminalBiomes): the authored boiling ocean | **NO** — boiling is a state you heat water into, not a substance you pump | TheScald |
| **Icy water** | **NO** — frozen water does not flow; melt is fresh water's face | **NO** — frozen precipitation is vanilla snow already | **NO** — same | **NO** — frozen meres are terrain, not liquid | **NO** — ice fringes on the seas are terrain | **NO** — an ice borer produces an item, not a canal fluid | NightsideIce · BlueDesert (OPEN, §3) — ground ice, bottled/terrain forms |
| **Toxic water** | **LATER** — a Contagion red-flow pulse event; not owed | **LATER, mod-only** — poison rain on the tar-rain split; owner call (§Open) | **YES** — the Contagion's red-flowing water (R-H7: the ocular forests excrete it); map-local streams, no worldmap river | **YES** — Poison Forest standing water (sheet: water non-potable, ruled) | **NO** — no toxic sea authored | **LATER** — no scenario wants to produce poison on site yet | PoisonForest · Contagion |
| **Acid water** | **LATER** — the wired corrosion liquid has no host biome; guest-only until one claims it | **LATER, mod-only** — acid rain on the tar-rain split; owner call (§Open) | **NO** — no source fiction anywhere | **LATER** — an acid pool set-piece is event dressing, not a biome body | **NO** — none authored | **NO** — producing corrosive on site serves no ruled scenario | none (guest everywhere) |
| **Tar** | **YES — RULED** (Sump belches, glass-rim fronts; rulings 2–3) | **YES — RULED, mod-only** (tar drizzle in `RM_TheSump`, off in campaign; ruling 1) | **NO — RULED** (edge law: no inflow seams; the tar's arrival is geological and unseen; player canal-work is the canal face, not a river; rulings 4/6) | **YES — RULED** (the Deep Black landmark mere, the biome's map-scale "ocean"; ruling 7) | **NO — RULED** (no new world body; the option was offered and not taken; ruling 7) | **YES** — the Junker pumping derrick is the ticket's own fiction precedent | TheSump |
| **Slime RED / GREEN / WHITE** (3 rows, one line — faces identical, hazards distinct) | **YES** — Heavy-viscosity oozing is the framework's own slime look (GelatinousSlime) | **NO** — the organism secretes; the sky does not | **YES** — viscous streams (framework §3: "viscous streams and pools"), map-local in the Slime | **YES** — pools, same source | **NO** — the registry is a body, not a sea | **LATER** — a tap INTO the organism is better fiction than a pump; needs its own sitting | GelatinousSlime (OPEN which of the trio, §3) |
| **Slime YELLOW** | NO | NO | NO | NO | NO | NO | none — the documented example row for other scenarios; not on Ash'karr |
| **Blood** | **NO** — item-only in v1 by registry ruling; map pooling is v2 | NO — v2+ horror-scenario material at best | NO | NO | NO | **NO** — grim and absurd as production | none |
| **Chemfuel** | **NO** — a chemfuel flood is an area-denial weapon, not scenery | **NO** — chemfuel rain is a bombing run | **NO** — same logic | **NO** — the ticket names the chemfuel lake as the canonical weapon-not-scenery case | **NO** — none authored, and never will be | **YES** — THE ground-pump case: an oil-derrick-style producer, settings-toggled, default OFF in campaign (§Open) | none — an industrial product (tar cracks into it), never a landscape |
| **Astrofuel** | NO — a piped industrial adoption (VGE net) | NO | NO | NO | NO | **NO** — VGE's own synthesizer owns production | none |
| **Brine** | **NO** — nothing surges brine | **NO** | **NO** | **YES** — Wasteland brine pans (the mod owns the `RUT_WastelandBrine*` terrain family, arch. §2a row 4) | **YES** — the two authored brine seas (registry ruling 5 / `LIQUID_BIOMES_MAP_1`); the Grey Sea is the hypersaline one | **LATER** — a brine well for salt-works play; no scenario owes it yet | GreySea · Wasteland |
| **Propane** | **NO** — a cryogenic flood is a freeze-and-ignite weapon | **YES** — propane condensation weather in its own biomes (physics ruled: liquefies below −42 °C; `RUT_FuelSnows` is named for it); hazard-first design (§Open) | **NO** — it pools at the drain, it does not run | **YES** — the authored propane body under Umbra (`RM_PropaneLake`, TerminalBiomes); canal-connected = infinite source on its maps | **NO further** — the authored body already is the map-scale body; no new world bodies | **YES** — a condenser/cryo-pump in the Propane Lakes; refueling-by-pipe already ruled v1 (`propane_gas_deep_design.md`) | PropaneLake (ground + sky) · FuelSnows (sky), when its row reaches the migration list |

**Row count: 16 registry liquids in 14 matrix lines** (the slime trio shares one line).
Deferred registry rows get no line, per law 7 — lava (the Forge) and coolant (the Rust
Cathedral's canals) are the two whose absence a biome will feel; both are annotated in §3
and one is an open ruling.

## 3. Native-liquid table — one row per biome

All 27 painted biomes (arch. §2a/2b) plus the Lantern Deeps (mod 26, not painted) and a
`RUT_FuelSnows` footnote. **Native** = saturates the ground (G) and/or falls from the sky
(S), one liquid or NONE; everything else is a surface guest. OPEN rows carry the best
candidate and go to the owner (§Open).

| # | biome (mod) | native liquid | G/S | sheet evidence, one line |
|---|---|---|---|---|
| 1 | the Stillsand / Dune Sea (`RM_Stillsand`) | **NONE** | — | the emptiness is the texture; no water in the timeless deep dayside |
| 2 | the Long Shade (`RM_LongShade`) | **NONE** | — | the shade economy exists because water does not; any water is a guest |
| 3 | the Rot (`RM_TheRot`) | **OPEN — candidate NONE** | — | 54 water tiles are Twilight Sea shore (a guest), zero rivers; the gut digests, it does not rain |
| 4 | the Wasteland (`RM_Wasteland`) | **brine** | G | "no outlet" — the drained flat; the mod owns the `RUT_WastelandBrine*` terrain family |
| 5 | the Nightside Ice (`RM_NightsideIce`) | **icy water** | G+S | the atmosphere's drain freezing out in order; dirty ice ground, snow sky |
| 6 | the Forsaken Crags (`RM_ForsakenCrags`) | **NONE** | — | the fog light cannot cross is weather, not saturation; 36 water tiles are strays |
| 7 | the Blue Desert (`RM_BlueDesert`) | **OPEN — candidate icy water** | G | zero water, zero rivers, but the ice IS the mechanism (cold-storage forms in it) |
| 8 | the Cracked Lands (`RM_FloodedCanyon`) | **fresh water** | S | thematic handle "the flood": rain max 1,442 mm on the Dew Horn highs, hidden canyon water |
| 9 | the Leaning Scrub (`RM_LeaningScrub`) | **fresh water** | G | "the last damp ground before the stormwall" |
| 10 | the Poison Forest (`RM_PoisonForest`) | **toxic water** | G | ruled in the sheet's own axioms: water non-potable |
| 11 | the Scald (`RM_TheScald`, TerminalBiomes) | **boiling water** | G | the biome IS the authored boiling ocean |
| 12 | the Rust Cathedral (`RM_RustCathedral`) | **NONE** (v1) | — | the coolant canals want a coolant row the registry defers; annotation, not a declaration |
| 13 | the Greentide (`RM_Greentide`) | **fresh water** | G | 85% river tiles — "water is the only argument" |
| 14 | the Weeping Stones (`RM_WeepingStones`) | **fresh water** | G | tended water: stone sweating on cold faces, hand-placed oasis pools |
| 15 | the Pyrelands (`RM_Pyrelands`) | **fresh water** | S | the sheet's "water answer": the already-built BlackRain weather — ash-fouled water from the sky (Fouled thirst quality) |
| 16 | the Contagion (`RM_Contagion`) | **toxic water** | G | R-H7: the ocular forests excrete red-flowing water; the highs' fresh rain (R-H1) is the planet's law, a guest here |
| 17 | the Webwork (`RM_Webwork`) | **fresh water** | G | 0 surface water by MEASURE — the jungle steals its water through parasitic roots; the ground carries it |
| 18 | the Slime (`RM_GelatinousSlime`) | **OPEN — candidate slime GREEN** | G | the sheet's trio are three registry rows; one must be declared (§Open) |
| 19 | the Miasma (`RM_Miasma`) | **OPEN — candidate salt water** | G | deltas where fresh rivers meet the hypersaline Grey Sea; true answer is brackish, which the registry defers |
| 20 | Warscar (`RM_Warscar`) | **NONE** | — | 90 tiles of battlefield in the deep dayside Scorch |
| 21 | the Forge (`RM_TheForge`) | **NONE** (v1) | — | its liquid is lava, deferred by registry (STUDY Lava Must Flow); annotation, not a declaration |
| 22 | the Fever Wood (`RM_FeverWood`) | **fresh water** | G | the water made to HOLD STILL — black mirror pools and mud (Fouled quality; the mud doc details the ground state) |
| 23 | the Sump (`RM_TheSump`) | **tar** | G (+S in mod) | ruled: the only liquid is tar; tar rain in the mod, not the scenario |
| 24 | the Propane Lake (`RM_PropaneLake`, TerminalBiomes) | **propane** | G+S | the authored body plus condensation weather below the −42 °C dew point |
| 25 | the Twilight Sea (`RM_TwilightSea`, TerminalBiomes) | **OPEN — candidate salt water** | G | one of the "two brine seas" bookkeeping questions: recommend Twilight = salt, Grey = brine (§Open) |
| 26 | the Grey Sea (`RM_GreySea`, TerminalBiomes) | **brine** | G | hypersaline, terminal, shrinking fastest |
| 27 | the Lantern Deeps (`RM_LanternDeeps`, injection layer, not painted) | **NONE** | — | an enclosed cave layer at ≤ −40 °C; nothing saturates, nothing falls |

**Footnote — `RUT_FuelSnows`** (Umbra's land successor, not yet in the migration list per
arch. §2b): when its row arrives, its native is **propane (S)** — the name is the
declaration.

Tallies: **28 rows · 23 declared** (17 with a liquid, 6 explicit NONE) · **5 OPEN**
(Rot, Blue Desert, Slime, Miasma, Twilight Sea).

## 4. Ground pump table

Every YES ships as a **Mod Settings toggle** (owner ruling in the ticket: scenario-
dependent, switchable). Default state in the Ash'karr campaign scenario noted per row.

| liquid | pump? | fiction / host | campaign default |
|---|---|---|---|
| Fresh water | **YES** | well/borehole — any biome with ground water | ON |
| Salt water | **YES** | coastal intake — sea-shore maps | ON |
| Tar | **YES** | Junker pumping derrick — the Sump (ticket's named precedent) | ON |
| Chemfuel | **YES** | oil-derrick-style producer — no biome, industrial | **OFF** (§Open) |
| Propane | **YES** | condenser/cryo-pump — the Propane Lakes | ON (its own biome only) |
| Brine | LATER | brine well for salt-works — Wasteland | — |
| Slime trio | LATER | a tap into the organism, not a pump — needs its own sitting | — |
| Toxic water | LATER | no scenario wants on-site poison production yet | — |
| Boiling / icy water | NO | states of water, not substances — heat or freeze a canal instead | — |
| Acid water | NO | no ruled scenario | — |
| Blood | NO | grim, absurd | — |
| Astrofuel | NO | VGE's synthesizer owns production | — |

## Open rulings for the owner

At most one question each; recommendation attached. 1–5 are the OPEN natives; 6–10 are
the dangerous-face and deferred-row calls.

1. **Native — the Slime.** The sheet's trio is three registry rows but native is one
   liquid. **Recommend:** declare GREEN as ground-native; RED and WHITE are the same
   organism's co-secretions, formally surface guests.
2. **Native — the Miasma.** True answer is brackish, a deferred row. **Recommend:** salt
   water (G); the fresh river inflow is the guest. (Alternative: promote the brackish
   row — not recommended, it adds a registry row for one biome.)
3. **Native — the Rot.** **Recommend:** NONE — its 54 water tiles are the Twilight
   Sea's shore, a guest; the gut's own fluids are fiction, not a FlowWorks liquid.
4. **Native — the Blue Desert.** Zero surface water, but the ground ice is the biome's
   mechanism. **Recommend:** icy water (G) — it makes the ice a first-class substance
   for the weapon-in-the-ice fiction.
5. **The two brine seas.** Which authored seas are the registry's "two brine seas"?
   **Recommend:** Grey Sea = brine, Twilight Sea = salt water (adopting vanilla ocean) —
   the Twilight is the "last ordinary sea" by its own sheet.
6. **Poison and acid rain.** Weapons as weather. **Recommend:** LATER, and when built,
   mod-only on the tar-rain split — never in the campaign scenario.
7. **Chemfuel ground pump.** The flagship dangerous pump. **Recommend:** YES, settings-
   toggled, default OFF in the campaign scenario; it exists for industrial scenarios.
8. **Propane weather.** Fuel snow/rain in the Propane Lakes (and FuelSnows when it
   arrives). **Recommend:** YES as biome-native sky, designed hazard-first (it coats,
   it ignites, it freezes flesh) — it is the biome's identity, not an event.
9. **Scald shore floods.** Boiling geyser-surge events on Scald coastal maps.
   **Recommend:** LATER — flavor-plausible, owed by nothing, dangerous to tune.
10. **Lava and coolant.** The Forge and the Rust Cathedral each want a deferred row.
    **Recommend:** keep both deferred (lava behind STUDY Lava Must Flow; coolant with
    the ammonia/coolant batch); both biomes declare NONE v1 with the annotation standing
    in §3.
