# WASTELAND_MECHANICS_BUILD_1 — the Middenshell, the processor comps, storms and the dose layer

Ruled at `WASTELAND_BEDAZZLE_SITTING_1` (2026-09-27/28, owner-typed; "Full accept.
Bedazzled!"). Design authority: the sitting's ledger notes + the 2026-09-28
amendment block in `wasteland.md` + `wasteland_survivor_cast_2026-09-28.md`
§3–§4/§6. Separate from `WASTELAND_RULED_CONTENT_1` (the cast defs) so each has
its own catcher. This item also absorbs the storm-defs question:
`WASTELAND_STORM_WEATHER_DEFS_1`'s scope card was ANSWERED at the sitting — ash
exhumation reuses the **MovingDunes mechanism**, so the mutator-churn scoping that
card waited on is moot.

## 1. The Middenshell — the giant (owner: "Bezoar Colossus loved")

- **TWENTY CELLS WIDE, owner-ruled.** Rides the TitanicCreatures engine
  (`RM_TitanicExtension`, Large Pawns multi-cell body, wander-route AI,
  destruction wake). Never hostile; proximity aura dose; its walk is the danger.
- **Corpse = permanent bezoar-quarry landmark**: mined like resource rock for
  `RM_ContaminantBezoar` + rarer `RM_VitrifiedBezoar`, priced in dose.
- Spawn: never `<wildAnimals>` — one-per-map-at-most via the titanic engine's
  mutator/incident spawn machinery; dark scour + war-ground range.
- 🔴 **Verification bar (escalate, never shrink):** verify the engine's maximum
  footprint tier actually handles a 20-cell body; if it does not, REPORT — the
  width is an owner ruling.
- Art at 512 (already queued): "landscape that turns out to be an animal".

## 2. The processor comps (Sloghog / Sootgrazer)

- Terrain-gated gatherable comp: `CompHasGatherableBodyResource` subclass (crib
  `CompMilkable`); fill rate gated on standing on polluted/ash terrain where
  Biotech pollution is present, else on time. Sloghog → bezoars; Sootgrazer →
  `RM_SootBrick`.
- Pollution CONSUMPTION per the ruling ("living furnace approved + extended to
  pollution emission/consumption/usage creatures"): where the engine allows,
  grazing a polluted cell occasionally un-pollutes it. If awkward, the output
  alone satisfies the economy half — note it and ship.

## 3. The ambient-dose comp (Smolderback / Middenshell aura)

- Smolderback: vanilla `CompHeatPusher` on the pawn + a small
  hediff-per-rare-tick ambient tox/radiation dose to its room. Spawns alone,
  wanders alone (no spacing mechanic owed). The trade goes in the description:
  heats a shelter all winter, doses it the whole time.
- Middenshell reuses the same comp family at larger radius/strength.
- 🔴 **Dose layer ruled: radiation AND pollution, ridden mostly on the Biotech
  pollution mechanism** — do not invent a parallel radiation system.

## 4. The three storms + MovingDunes exhumation

- Three WeatherDefs: ash storm (everywhere), radiation-halo (everywhere the
  plasma doesn't reach), plasma storm (🔴 TERMINATOR FAMILIES ONLY, sheet §6
  ban 7). Halo/plasma player-facing names still owed to the owner (sheet Owed).
- **Exhumation reuses the MovingDunes mechanism** (owner-ruled): post-storm
  terrain re-deal rides that existing machinery — no new mutator-churn tooling.
- Cinderfelt germination: the ash storm's aftermath seeds it on fresh-fall
  terrain (weather post-effect or MapComponent, whichever is cheaper); it dies
  in ~8 days as the fall compacts.

## Watch out

- All C# in an existing assembly needs its `<Compile Include>` line
  (`EnableDefaultCompileItems` is false) — a new .cs without one compiles into
  nothing, silently.
- No anomaly flavor anywhere; wildlife never the headline threat (the ground
  is) — the Middenshell CONCENTRATES the ground's danger, it never attacks.
- The dose is ambient, never an attack.

## verify

- Quicktest: Middenshell spawns at ruled scale, wake destroys, corpse hardens
  mineable; a penned Sloghog on polluted ground produces a bezoar; Smolderback
  heats and doses a closed room (state reads, not screenshot hunts).
- Ash storm ends → cinderfelt appears on fresh fall; exhumation re-deal fires
  via the MovingDunes path.
