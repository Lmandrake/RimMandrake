# Explosive Plant Growth — per-biome terminal-moment variant roster (proposal)

Design proposal for `EXPLOSIVE_PLANT_GROWTH_1`. Subject: §3 of
`design/Jawa/worldbuilding/explosive_plant_growth_design.md`, whose default Burst is
RULED (owner, 2026-09-20) and whose per-biome variants are PROPOSED.
Transient — BENCH lands whatever survives into the design doc. Nothing here is ruled.

## What is already ruled (not re-opened here)

- Default terminal moment is **the Burst, and it sows**, zone-indifferent — owner, 2026-09-20.
- Burst lethality ceiling = injury + knockdown; lethal outcomes are for flagship performances only (§7.1).
- Irrigation pump ships as-is (§7.2). Fever Wood Nectar Flush is IN (§7.3). Stepped growth default, smooth close-up cap (§7.4).
- Ambient groaning-growth register on jungle/river/miasma tiles (§7, 2026-09-10) — atmosphere, not a terminal moment.
- Carve-outs stand: terminator/poison forest never soaks (R-G3); fungal biomes and every saline shore never soak (§3 carve-outs).
- Webwork's Churn is the sheet's own use of the engine (§4c); §3 already says "no new rule" — already ruled, no action.

Nothing below re-opens any of these; every variant diverges FROM the ruled Burst.

## Method: when a biome earns a variant

A biome earns a variant only when the ruled default Burst would **contradict that
biome's own frozen sheet** if it ran there unchanged. Novelty is not a reason; a
roster where every biome is special has no signal. Three tests, applied to all 27
painted defs (`biomes/_def_bindings_2026-09-09.md`, regenerated 2026-09-20):

1. **Does qualifying water reach plants here at all?** (§1's roster, `water_taxonomy.csv`).
   If not, the biome is a carve-out and has no terminal moment to vary.
2. **Would a synchronised pop-and-sow break the sheet?** Permanent soak makes the Burst
   wallpaper (Greentide); a sheet whose sown ring must convert rather than sprout (Slime);
   a sheet whose weather already owns "everything budding" (Contagion).
3. **Is the difference mechanical or a skin?** If the sheet's flavour can ride the default
   Burst's pieces (effecter, filth, husk, sown ring), it is a CHEAP reskin, not a variant.

Result: **4 variants** (one of them a downgrade of the doc's own Pyrelands proposal to a
reskin), **2 already ruled** (Fever Wood, Webwork), **5 keep the default**, **16 never soak**.

## Roster: biomes that keep the default Burst

### Already ruled — no action

| biome | def | status |
|---|---|---|
| Fever Wood — Nectar Flush | `RUT_FeverWood` | IN (owner, 2026-09-10 §7.3). Design §3 row stands as written; nothing to add. |
| Webwork — the Churn | `RUT_Webwork` | Sheet §4c's own use of the engine; design §3 says "no new rule". Not a variant of the Burst — the thicket has no terminal moment per plant. Recommend BENCH move this row out of the variants table into the carve-outs paragraph so the table lists only true variants. |

### Default Burst is correct here

| biome | def | why the default is right | note |
|---|---|---|---|
| **Cracked Lands — the Bloom** | `RUT_CrackedLands` | The flagship, and it is the default Burst run at carpet scale in flood synchrony — exactly what §3 already says. The boom-bust die-off on the dry and the bloom harvest are **sheet-ruled** (§10b/§11), not new terminal mechanics; the Spender feeding frenzy is the sheet's fauna. | Keep the row, but label it "default at scale"; its only build beyond the default is `RUT_BloomBurst` (already contracted with `FLOOD_WITNESS_EVENT_1`). Cost: already priced there. |
| **Miasma** | `RUT_Miasma` | §1 already rules "fresh side only — the surge line decides which half blooms". The geography IS the variant. One consequence worth writing into §4 SURVIVE, 🄸 INVENTED but derived from §4's own "salted ground refuses the soak": a surge that carries the salt line over a charging plant **defuses** it (no burst, plant reverts). | Ambient groaning register applies here anyway (§7). No card. |
| **Desert** | `RUT_Desert` | No qualifying water (dew at shade lines is trace). Soak arrives only by player irrigation, which is the ruled water-for-food pump. Freeze matrix notes the sheet's old "explosive ban" is STALE — superseded by the world-wide ruling. | No card. |
| **Arid Shrubland** | `RUT_AridShrubland` | Fog plumes are `fog_condensate`; §1 says dew quantities never soak. Whether a Hadley plume wets ground past the threshold is a §1 soak-trigger question, not a terminal-moment one — UNCONFIRMED, outside this roster. | Default Burst via irrigation. No card. |
| **Weeping Stones** | `RUT_WeepingStones` | Sheet ban: "no rain-fed ecology"; water is dew combed from wind, and the pools are hand-placed Oasis terrain. A burst-and-sow ring at a truce pool is tonally wrong for a place the sheet makes sacred and scarce. 🄸 INVENTED recommendation: **the pools do not soak** — only the player pouring pool water onto ground does, which is the sheet's own tension (every drop caught is a drop spent). | **Card #5** — whether pools count as a qualifying wet cell is not answered by §1 (it names `fog_condensate` only in dew quantity). |

### Never soak — no terminal moment to vary (carve-outs)

| biome(s) | def(s) | source of the carve-out |
|---|---|---|
| Poison Forest | `RUT_PoisonForest` | R-G3 / R-H2b — stunted; design §3 already lists it. |
| the Rot | `RUT_TheRot` | fungal; Sheen is not water (taxonomy). Design §3 already lists it. Ambient register only. |
| Terminator seas + both deeps | `RUT_TwilightSea`, `RUT_GreySea` | saline; design §3 already lists every saline shore. |
| **Deep Desert / Dune Sea** | `RUT_ExtremeDesert` | 🔴 **Missing from design §3's carve-outs.** `deep_desert.md` hard ban 4: *"No fast growth. The planet's freakish-growth fact does NOT apply here — the same deliberate exception the terminator gets (R-H2b). A global growth multiplier must not flatten it."* Its own "ground blooms within hours" after a rare flood and the sarlacc breach flood's "bloom clock" are **that sheet's mechanic**, under `SARLACC_HABITAT_BUILD_1`, not this engine. BENCH should add this def to §3's carve-outs and to `PLANT_GROWTH_SPEC` R-G3's biome list. Sheet-ruled; no card needed. |
| Wasteland | `RUT_Wasteland` | `waste_brine` saline; growth "glacially slow" (sheet). |
| Scarlands | `RUT_Scarlands` | ToxRain is not in the water taxonomy — UNCONFIRMED as water; sheet growth "crusts thicken over centuries". Treat as never-soak until the taxonomy says otherwise. |
| Rust Cathedral | `RUT_RustCathedral` | zero flora (sheet). |
| Nightside Ice | `RUT_NightsideIce` | `night_ice` frozen; "does not grow" (sheet). |
| Blue Desert · Propane Lakes · Umbra | `RUT_BlueDesert`, `RUT_PropaneLake`, `RUT_Umbra` | hydrocarbons, not water (taxonomy). |
| Forsaken Crags | `RUT_ForsakenCrags` | `crags_trickle` is "thin; scarce" — below §1's wet-ground threshold. 🄸 INVENTED call; UNCONFIRMED quantity. |
| the Forge | `RUT_TheForge` | closed boiling rain "flashes back to steam on the rock within seconds" — the ground is never wet, so §1's quantity rule excludes it. Not in the taxonomy — UNCONFIRMED. Fireweed's flash-interval growth is the sheet's own register. |
| the Sump | `RUT_Sump` | no water; tar by drainage. |
| the Scald | `RUT_TheScald` | `scald_water` saline/boiling, never potable; `scald_melt` runs OFF it into the Greentide rivers. |
| Fall Line · Lantern Deeps · Wreck Fields | unbound | injection layers, not painted defs (bindings §2). |

## Roster: proposed variants

All four are 🄸 INVENTED. Each diverges FROM the ruled Burst; none touches the soak
trigger, the charge cycle, the lethality ceiling or the zone-indifferent sowing where
the Burst runs.

### V1 · Greentide — the Fruit Glut (understory) 🄸 INVENTED

- **biome**: `RUT_Greentide` (permanent soak — the rivers and the steam are the weather).
- **what the player sees**: understory plants swell past size, tremble, creak — and then
  instead of popping, they **dump**: fruit and produce cascade off in a heap and the plant
  shrinks back to normal and starts charging again. No husk, no chaff, no sown ring. The
  trees keep their own top — the sheet-ruled crack-and-FALL.
- **why THIS biome**: the soak here never ends, so the default Burst would fire on every
  plant on every clock — popcorn as wallpaper, and the Burst stops being a signal
  anywhere. The sheet already owns the encroachment story ("plants grow into and block
  your doors", the blower doorway as counter-tool), so a sown ring adds nothing the
  biome does not already do; and the sheet says the fruit "yearns to be eaten… beyond
  any other biome's dreams" — the glut IS the Greentide's terminal moment.
- **mechanical difference**: terminal = **drop-and-reset** (premium produce, plant returns
  to normal scale, re-charges) instead of pop + husk + sown ring. Treefall is the
  Greentide kit's own C# fall event (three fellers, one fall), NOT this item's build — the
  design's §3 row currently reads as if this item owns it; it does not.
- **cost**: MEDIUM — one new terminal branch in the same comp; the produce drop and the
  reset reuse the Burst's DROPS half.
- Also note for BENCH: this is a two-tier rule (understory: glut; trees: fall). The
  Greentide extract (sheet §7, ruled) "charges plants to burst" — under V1, extract-charged
  plants in the Greentide should still Burst, because the extract is the deliberate
  weaponised form. 🄸 INVENTED; harmless either way, flag not card.

### V2 · Slime — the Conversion Burst 🄸 INVENTED

- **biome**: `RUT_Slime` (`slime_flood` — organism-induced slime rain, potable floodwater,
  "soaks on its way through" per §1).
- **what the player sees**: the default Burst, pop and all — but the ring that comes up
  around the husk is **slime**: slime-grass and pseudo-plants, not the plant's own sprouts,
  and the ground under the ring reads as slime terrain creeping in from the husk.
- **why THIS biome**: sheet, owner-ruled — *"Farms fail by conversion: fertility-1.0
  slime-grass lures cultivation, and fields convert back to slime within a few harvests."*
  A slime-rain soak bursting your crop and sowing slime in your field is that ruling made
  watchable. The premium DROP stays — the jackpot is the lure the sheet describes.
- **mechanical difference**: the sown-ring sprout def is swapped for the biome's slime
  flora (and, if the Slime kit's terrain-conversion already exists, a conversion tick on
  the ring cells). Everything else is the default Burst.
- **cost**: CHEAP — a per-biome sprout-def override on the sown ring; MEDIUM only if the
  terrain-conversion tick is wanted and the Slime kit has not built it yet.

### V3 · Contagion — the Spore Burst, and the Burn defuses 🄸 INVENTED

- **biome**: `RUT_Contagion` (`red_water` — real rain at the peaks, R-H1's exception; spore
  + toxin loaded until sunned).
- **what the player sees**: under the Bloom (the standing red-fog storm) a soaked plant
  bursts in a **red spore puff** rather than pale chaff, and its sown ring comes up as the
  biome's half-transformed flora. When the cloud tears and a **Burn** lances the valley,
  every charging plant in the open **cooks**: it stops swelling, greys to a husk, and does
  not burst — the UV sterilised the charge. Overgrown plants can be harvested safely in
  that window.
- **why THIS biome**: the sheet's grammar is inverted weather — "Move in the Burn; hide
  in the Bloom" — and "the Bloom follows: the goo, fed on what the Burn killed, buds
  furiously." The Burst belongs to the Bloom; the Burn is the biome's sterilising window
  and should sterilise the charge too, otherwise the mechanic ignores the one weather
  rule the owner ratified for this place.
- **mechanical difference**: (a) terminal moment is **weather-gated**: charge completes
  only under Bloom; under Burn a charging plant goes to husk with no burst, no drop, no
  ring. (b) the chaff is a spore filth. Whether the spore chaff ALSO applies the sheet's
  owner-ruled **Contagion-touched** exposure hediff is an open question — it would push
  the burst past a bruise (not past the injury+knockdown ceiling in kind, but a lasting
  mutation hediff is a bigger consequence than the default carries). Card #3/#6.
- **cost**: MEDIUM — the Burn-defuse is a weather check in the existing terminal branch;
  the spore filth is a reskin. Exposure-on-burst is CHEAP if the kit's hediff exists.

### V4 · Pyrelands — the Burst leaves tinder 🄸 INVENTED (downgrade of the doc's row)

- **biome**: `ZBiome_Grasslands` (donor def; `PYRELANDS_WRONG_BIOME_DEF_1` is open on which
  def carries the roster — either way the biome is the Pyrelands). Soak source: R-H1 river
  floods along the 9 river tiles.
- **what the player sees**: the default Burst — but the spent husk and the drifting chaff
  are dry and yellow within the hour, and the sown ring comes up as quickgrass that goes
  from green to gold on the sheet's days-clock. A burst under a dry thunderstorm is a fire
  waiting for its strike.
- **why THIS biome**: R-H3/R-H4 — "freakish growth → standing dry grass → lightning → it
  lights". The doc's current row ("not a burst but the cure") describes the ambient R-H3
  register, which every Pyrelands plant already has; it is not a terminal moment and does
  not need this engine. What the engine can add is the fuel spike: a burst here is the
  fire's supply line, delivered in one event, around whatever the player built.
- **mechanical difference**: none in kind — the husk and chaff carry high flammability and
  the ring's sprout def is quickgrass. A reskin of the Burst with a stat on its leftovers.
- **cost**: CHEAP. (The doc's "green → gold → standing tinder in hours" is not
  separately buildable — a plant's flammability is a def stat, not a growth stage —
  which is the second reason to downgrade this row.)
- Card #4: A (Burst with tinder leftovers) or B (no burst at all in the Pyrelands — quiet
  cure, the fire loop unchanged). Recommend A.

## Owner must rule (ranked)

Plain-language cards, most consequential first. Each names the trade.

1. **Greentide (V1):** In the river jungle, where plants are wet all the time, do
   plants **dump their fruit and start over** instead of bursting? — YES keeps the Burst a
   rare, scary event everywhere else and makes the jungle a fruit glut (the sheet's own
   word); NO means the jungle pops nonstop and a burst stops meaning anything.
2. **Slime (V2):** When a slime-soaked crop bursts, does the ring around it **come up as
   slime instead of sprouts** (you still get the big harvest, but the field starts turning)?
   — YES makes "farms fail by conversion" something you watch happen; NO keeps the Slime
   on the plain default.
3. **Contagion (V3a):** Does a clear-sky **Burn cook a charging plant** into a dead husk
   (no burst, no harvest, but safe to work near), so bursts only happen under the red
   storm? — YES gives the player a safe window that matches "move in the Burn"; NO is one
   fewer rule to build and to learn.
4. **Pyrelands (V4):** A: the burst leaves **dry tinder** (husk, chaff and a ring of
   quickgrass that dries in days) — feeds the fire loop, and a burst in a dry storm can
   start one. B: **no burst** in the grasslands at all. — A is spectacle that feeds a
   ruled mechanic; B is quieter and cheaper.
5. **Weeping Stones:** Do the **truce pools soak the plants beside them**? — NO keeps the
   sacred water quiet, and the only way to make things burst there is to pour the pool
   out on the ground yourself (spending it); YES puts bursting, sowing plants at the one
   peaceful place on the planet.

Sixth, lower stakes, only if he takes #3: **Contagion (V3b):** does the spore puff from a
burst give a pawn the Contagion-touched exposure the sheet already rules for spore
contact? — YES makes a Contagion burst a real threat beyond a bruise; NO keeps it a
recolour.

Findings for BENCH that need no card (sheet-ruled or doc hygiene):
- Add `RUT_ExtremeDesert` (deep desert / dune sea) to design §3's carve-outs and to
  `PLANT_GROWTH_SPEC` R-G3's biome list — `deep_desert.md` hard ban 4 already rules it.
- Move the Webwork row out of the variants table (it is the sheet's own engine use, the
  doc itself says "no new rule").
- Relabel the Cracked Lands row "default Burst at carpet scale" — its extras are
  sheet-ruled and already contracted to `RUT_BloomBurst`.
- The Greentide row currently implies this item builds the treefall; the fall event is
  the Greentide kit's (three fellers, one C# fall).

## UNCONFIRMED names and facts

- `ZBiome_Grasslands` as the Pyrelands def: bindings table says it is the painted def
  (222 tiles) but `PYRELANDS_WRONG_BIOME_DEF_1` is open on `RM_FE_Pyrelands` carrying the
  roster instead. The variant is per-biome-sheet; which def it keys on is that item's call.
- Whether Arid Shrubland fog plumes, Weeping Stones pools, Forsaken Crags melt-trickle and
  the Forge's flash-rain reach §1's "wet ground" threshold — §1 only names dew-quantity
  `fog_condensate` as excluded. Pools are carded (#5); the other three are recommended
  never-soak and need a §1 answer, not a §3 one.
- Scarlands ToxRain and Pyrelands BlackRain are not rows in `water_taxonomy.csv`; treated
  as not-water here.
- Slime kit terrain-conversion mechanism: assumed to exist from the sheet's donor notes
  ("terrain-attack"); not verified against the kit spec. V2's CHEAP cost does not depend on it.
- Contagion-touched hediff: owner-ruled in `the_contagion.md` ("spore exposure starts…");
  not checked for an existing def. V3b's cost assumes the kit builds it regardless.
- No engine member, defName or field beyond those named in the design doc and the bindings
  table has been asserted here.
