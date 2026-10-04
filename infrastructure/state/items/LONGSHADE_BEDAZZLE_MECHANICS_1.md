# LONGSHADE_BEDAZZLE_MECHANICS_1 — the Long Shade's shade package

Ruled 2026-09-29, `LONGSHADE_BEDAZZLE_SITTING_1` volley turns 2–4, with every ruling on the ledger.
Design source: `design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md`, in
particular §3, §6.2–6.5 and "Rulings — volley turn 4". **Blocked on `SOLAR_HEAT_EXPOSURE_1`**,
which provides the heat, the directional grid and the dash system.
**Model: opus** (complex code generation).

## spec

1. **Golden hour** (owner: *"I like the golden hour concept. A perpetual beautiful sunset."*).
   One map component gives the permanent sunset sky and glow, plus the pinned sun angle
   that the directional grid and the long rendered shadows share (§3.1–3.2).
2. **Mirrak** (IN). A flat ambush predator that lies in the open looking like a shadow, with its
   "shadow" pointing the wrong way. The dash job giver treats it as shade and the grid does not.
   When the smoke-calendar haze stretches the real shadows, the mirraks stay short.
   **Mirrak hide** is the deepest shade cloth, feeding `SHADE_GEAR_FAMILY_1` (§6.2).
3. **Swimmer's road** (IN, with a condition). One young sarlacc swimmer per map, ever. It
   surfaces and travels rim to rim toward the largest dew ring, usually the player's, and roots
   into a permanent well if it arrives. Build it on the existing `src/RimStarWars/Sarlacc/`
   (`RSW_SarlaccSwimmer` / its comp). RSW/Utinni tier (§6.3). 🔴 The owner's condition: *"we can't have
   animals "disappear spontaneously." There needs to be SOME kind of indication of what happened
   to them."* Every animal the swimmer takes, and every one the mirrak takes, leaves a readable
   sign: a wake that ends, drag marks, remains, a disturbed patch, or a message.
4. **Crawler Road** (IN, *"Cool inhabited vision"*). A line of wrecked vehicles across the widest
   gap, ending at a dead sandcrawler. Every wreck is shade, and stripping the wrecks breaks the
   crossing; the player can rebuild it. Build on the Inhabited, AshkarrInhabited and
   DesertVehicleReskin content (§6.4).
5. **Long Carry** (IN). Unlooted dead lie out in the sun and can only be reached with shade gear.
   🔴 Their journals must **not** point to gnomons: the gnomon line was CUT. Treat them as salvage
   and lore only (§6.5).

CUT, and not to be built: the gnomon line, and the farm on the horizon / heliograph. The
smaller ideas are deferred to `LONGSHADE_SHADE_EXTRAS_1`.

## criteria

- Each of the five features is quicktest-proven on a Long Shade map, and each ships a Mod Settings
  toggle.
- Every swimmer or mirrak kill leaves a visible sign; the test checks for it.
- The swimmer is proven one-per-map.

## tuning + audio pass (2026-10-03, round 36)

Owner rulings 2026-10-03: vanilla audio ships as final; first-guess numbers ship marked PROVISIONAL.

- **PROVISIONAL numbers** (def comments say so): mirrak wildAnimals weight 0.05; `RSW_SwimmerRoad`
  baseChance 0.6, earliestDay 20; Crawler Road spacingFactor 0.8 (spacingCells 6~24, minGapSpacings 1.5,
  maxGapCells 160); sun graves count 1~3, load silver 80 / components 2 / herbal medicine 4 / pemmican 20,
  readableChance 0.5; wreck tick interval 1.5~6 s, volume 6~10, pitch 0.55~0.8.
- **Audio (vanilla):** the swimmer's under-sand grinding is Anomaly `FleshbeastDigging` as a sustainer while
  the road/seep swimmer moves (setting `swimmerGrindSoundEnabled`); the metal wrecks (skiff, crawler tread)
  tick via vanilla `CompAmbientSound` + `RSW_WreckMetalTick` (vanilla Tick_Tiny grain folder; wrecks now
  tickerType Normal). First script: `src/RimStarWars/Sarlacc/selftest_longshade_audio.py`.
- Still owed: the quicktests (game-up) and the mirrak haze (smoke calendar, unbuilt).
