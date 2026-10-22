# Fuel spill research — realistic numbers for FlowWorks sheets (BENCH, 2026-10-22)

Owner, 2026-10-22 ~15:40 PDT: "Do some web research to see what realistic numbers are for what would happen if liquid
propane or chemfuel (gasoline) or astrofuel (jet fuel) were spilled."
Mapping: chemfuel = gasoline · astrofuel = jet fuel (Jet A / JP-8) · propane = liquid propane (LPG).

Confidence key: **F** = read in a fetched source this session · **C** = my calculation from F numbers and standard
physics · **R** = recalled handbook value, NOT re-fetched this session (treat as approximate).

## 1. Real numbers

| quantity | gasoline (chemfuel) | jet fuel Jet A / JP-8 (astrofuel) | liquid propane | water (our ruled baseline) |
|---|---|---|---|---|
| boiling point | ~30–200 °C range (R) | ~150–300 °C range (R) | **−42 °C** (F: CAMEO CH9018) | 100 °C |
| flash point | **−43 °C** (F: JRC RAPID-N / REACH profile; UW vehicle-fire table −36 to −45 °F) | **≥ 38 °C** spec minimum (R: ASTM D1655 / MIL-DTL-83133; secondary web hit 38 °C); JP-8 52 °C in an NPTEL table (F) | **−104 °C** (−156 °F, gas) (F: CAMEO) | — |
| autoignition | **~280 °C** (F: RAPID-N; UW range 280–456 °C) | **~210 °C** (R; secondary hit 210 °C) | **450 °C** (842 °F) (F: CAMEO) | — |
| flammable limits in air | 1.4–7.6 % (R) | 0.6–4.7 % (R) | **2.1–9.5 %** (F: CAMEO) | — |
| does it pool? | yes; unconfined spill spreads to ~0.5 mm minimum thickness (F: Zhao et al. 2017, ethanol) | yes; on water it spreads to < 0.01 mm sheen (F: NOAA ORR) | **barely**: adiabatic flash ~30 % at 20 °C (C: cp 2.5 kJ/kg·K × 62 K / 426 kJ/kg); free-flashing propane jets formed **no pool** in INERIS tests, butane rain-out ≤ 10 % (F: Gexcon pool-evaporation docs) | yes |
| evaporation of a thin ground pool | log-in-time, not wind-limited: %Ev = k·ln(t min), measured k = **8.55 still air, 15–21 at 1–2.5 m/s** for a 1.87 mm layer at ~22 °C (F: Fingas, "The Evaporation of Oil Spills", BSEE OSRR 120). Still air: ~35 % gone in 1 h, ~60 % in a day; with wind most gone in ~4–6 h. A few-cm pool ≈ 1.5–3 cm/day at 20 °C (C) | kerosene-range, far less volatile; on open water "most … will evaporate or naturally disperse within a day or less" (thin sheen); under canopy "much slower, allowing the fuel to persist" (F: NOAA ORR "Kerosene and Jet Fuel Spills", 2019). A cm pool on land: well under water's rate (C) | **boils on ground heat**, not air drying: q = kΔT/√(παt); moist soil (k 0.9 W/m·K, α 4.3e-7 m²/s), ΔT 62 K → 6.2 kW/m² at 1 min, 0.8 kW/m² at 1 h; cumulative boil-off **~2.3 cm in the first hour, ~11 cm in a day** (C; Yellow Book CPR 14E form, cited by Gexcon) | ~0.3–0.7 cm/day outdoors (our 0.5 cm/day at 20 °C) |
| temperature dependence | Fingas-type constants rise ~1–1.5 %/°C; still evaporates below 0 °C (C/R) | strong; little loss in cold (R) | none above −42 °C beyond ground heat; **stops below −42 °C** (C) | stops when frozen |
| soil infiltration vs water | Darcy K ∝ ρ/μ: 740/0.5 vs 1000/1.0 → **~1.5x water** (C) | 800/1.2 → **~0.7x water** (C); "penetrate[s] porous sediments quickly"; fuel 1 ft into sand takes **> 18 months** to degrade (F: NOAA ORR) | ~0: boiling + frozen ground (C; LPG pools hold ice, F: Gexcon/INERIS) | 1x (4/2/1 cm/day sand/soil/gravel, ruled) |
| how long a 2–3 cm pool persists (20 °C, open ground) | hours to ~1–2 days (light ends in hours, heavy residue lingers) (C from Fingas) | days to weeks; most of it soaks in (C) | **~1 hour** (C) | days (soak) |
| flame spread across the pool | above flash point: fast, ~1–2 m/s (R; vapour-phase); spill fire "immediate flame spread" (F: Markova et al. 2020) | below flash point (normal ambient): slow liquid-phase creep (R: ~1–10 cm/s); no change until fuel is **~11 °C above flash point**, then up to **150 cm/s** (F: Leonard et al. 1992, NRL, DTIC ADA250371) | vapour-cloud flash fire, several m/s, flashback to the source (F: CAMEO/ERG "flame can flash back to the source of leak very easily") | — |
| burning (regression) rate | pool **0.045–0.064 kg/m²/s → ~4–5 mm/min**; thin unconfined spill **0.011 kg/m²/s → ~0.9 mm/min** (F: Gottuk & White via Markova et al. 2020, IJERPH 17:411; C: ÷ 740 kg/m³). Spill fires ≈ 0.89 × pool (F: Zhao et al. 2017) | JP-4 0.051, JP-5 0.054, kerosene 0.039 kg/m²/s (R: Babrauskas 1983 / SFPE) → **~3–4 mm/min** (C, ÷ 800) | LPG/butane 0.078 kg/m²/s (R: Babrauskas) → **~8 mm/min** (C, ÷ 580); LNG 20 m pool 0.106 kg/m²/s (F: search abstract, firedoc.nist.gov) | — |
| vapour hazard | heavier than air, flammable from −43 °C | low vapour at ambient; mist/heated fuel flammable | heavier than air, travels to ignition; **isolate 100 m, large spill evacuate 800 m downwind** (F: CAMEO/ERG 2024) | — |

## 2. Model units and time scale

- A notch is 50 cm (`RM_Volume.CentimetresPerNotch`); `DlPerCm` dL per cm per square.
- RimWorld day = 60,000 ticks = 24 game hours: 2,500 ticks a game hour, ~41.7 ticks a game minute. Physical rates are
  applied **1:1 in game time** (as the ruled water numbers already are: 0.5 cm/day is real outdoor evaporation).
- Sheet pulse = 250 ticks → 240 pulses a day.
- Soak/evaporation percents are of water's ground-class soak (4/2/1 cm/day) and air drying (0.5 cm/day at 20 °C,
  × T/20 capped 3x, 0 at or below 0 °C, roofed 30 %).

## 3. Game numbers applied

| fluid | field | old | new | why (one line) |
|---|---|---|---|---|
| chemfuel | `sheetSoakPercent` | −1 (derived 100) | **150** | gasoline flows into soil ~1.5x water (ρ/μ). |
| chemfuel | `sheetEvaporationPercent` | −1 (derived 100) | **600** | 3 cm/day at 20 °C: a 2 cm puddle is mostly gone in under a day, as Fingas's log curve says. |
| chemfuel | `sheetBurnMmPerMinute` (new) | channel inferno, 50 cm / 300 ticks (~70 mm/game-min) | **4** | pool-fire regression; a 2 cm puddle burns ~5 game minutes (~210 ticks, 3.5 s at 1x). |
| astrofuel | `sheetSoakPercent` | −1 (100) | **70** | jet fuel is a little more viscous than water. |
| astrofuel | `sheetEvaporationPercent` | −1 (100) | **50** | kerosene-range: a puddle lingers about a week and mostly soaks in. |
| astrofuel | `sheetBurnMmPerMinute` (new) | channel | **3** | used only when the Detonation setting is off (detonation consumes the square at once). |
| propane | `sheetSoakPercent` | 0 | **0** | it boils and freezes the ground; nothing soaks. |
| propane | `sheetEvaporationPercent` | 2000 | **0** | air drying is the wrong mechanism; replaced by boiling. |
| propane | `sheetBoilCmPerHour` (new) | — | **2** | ground-heat boil-off ~2.3 cm in the first hour: a 2 cm spill is gone in ~1 game hour (~100x water at 20 °C). Roof-independent. |
| propane | `sheetBoilPointC` (new) | — | **−42** | below its boiling point liquid propane really does stand as a pool. |
| propane | `sheetBurnMmPerMinute` (new) | channel inferno | **8** | LPG pool fire regression. |

Code: `FluidRule.BoilMilliDl / BoilAboveDeciC` (kernel loses max(air drying, boil) while the cell is above the boiling
point), `RM_SheetFluidMath.BoilMilliDlPerPulse`, `RM_SheetFluidMath.SheetBurnTicksPerNotch` (scaled by the chemfuel
burn-rate dial for an inferno). Fire front speeds (`fireFrontTicksPerCell`) and fire kinds are unchanged: chemfuel 2
ticks/cell (~0.5 m/s game time) is in the real band; propane 2 likewise.

## 4. Where we depart from realism for play

- **Propane flash fraction (~30 % instantly) is not removed at the spill**; the 2 cm/h boil carries it. Removing it would
  need a new ledger exit at spill time. A 2 cm propane spill still lasts ~1 game hour (~40 s at 1x) — long enough to see.
- **Propane boil is constant**, not the real 1/√t decay (fast at first, slow after the ground chills). Simpler to read.
- **Astrofuel still detonates** (owner card 2026-10-15). Real Jet A at ambient is below its 38 °C flash point: hard to
  light, slow creeping front, ~3 mm/min burn, no blast. The 3 mm/min applies only with Detonation off.
- **Fuel air-drying still uses water's temperature curve** (0 at or below 0 °C; capped 3x). Real gasoline keeps
  evaporating below freezing (~75 % of its 20 °C rate at 0 °C) and a roof barely slows it (oil evaporation is not
  wind/boundary-layer limited, Fingas). Not changed: a per-fluid temperature curve is a kernel change; noted as owed.
- **Gasoline evaporation is linear** (3 cm/day) instead of log-in-time with a heavy residue; a puddle simply shrinks.
- **The canal channel's own burn (300 ticks/level inferno) is unchanged** — the owner's "burns the Chemfuel down
  rapidly" card covers moats; only spilled sheets take the real regression rate.

## 5. Applied (files, tests, shas)
See section 5 below (filled at commit time).
