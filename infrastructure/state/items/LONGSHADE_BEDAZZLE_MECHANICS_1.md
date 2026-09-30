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
