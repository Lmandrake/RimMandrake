# BLUEDESERT_MECHANICS_BUILD_1 — the Warnings, blue-ice quarrying, the vhaulk trap, weathers, sound, Cold Hold

Ruled at `BLUEDESERT_BEDAZZLE_SITTING_1` (2026-09-28, full accept of the whole
slate). Authorities: the 2026-09-28 amendment in `the_blue_desert.md` +
`bluedesert_bedazzle_review_2026-09-28.md` §4 (the developed pitches). Separate
from `BLUEDESERT_RULED_CONTENT_1` (the defs) so each has its own catcher. Build
order matters: weathers (4) before murrek re-seeding (6); blue ice (content
item) before the Cold Hold (7).

## 1. Vhaulk detonation gating (one comp edit, no new mechanism class)

- Death gate in the shipped charge family (`RM_HydrocarbonCharge`,
  KillFinalize path): read the killing DamageInfo's def — detonate ONLY on the
  heat family (Flame/Burn; lightning's strike damage IS Flame, so lightning
  comes free). Kinetic/cold kills leave the cistern intact.
- 🔴 **The ion trap: EMP is checked ON HIT, not on death** — any EMP damage
  against a living vhaulk detonates it immediately (PostApplyDamage-family
  hook). Stunning it is the worst thing you can do; that sentence shapes the
  description obliquely.
- Radius ~15 Flame explosion; balance care near flora chains (one death can
  glass a quarter map — that is the point, but verify the chain doesn't cascade
  off-map-edge into perf death).
- Tap-alive harvest: work-giver operation at a valve body part (dorrak-hump
  logic scaled up) → cold-wax windfall at manhunter risk.

## 2. The Warnings — the discovery ladder (marks 2+9, BIOME-LOCAL)

- 🔴 NO Ideology defs, no precepts, no rituals (owner-ruled). Study
  interactables on the ruled KCSG quarry tableaus; three tiers via hidden
  unlock flags (WorldComponent or hidden ResearchProjectDefs — pick the
  cheaper): (i) hazard-sense near quarries (map reveal of buried hazards),
  (ii) **cold-cutting** — the kept mining technique: ice extraction that never
  crosses the phase line, the earned counter to §3's thaw rolls, (iii) the
  full reading — the gods layer delivered as prose, and the warnings include
  *do not still the mountain* (ties to §1's trap).
- Couples to `HORRORS_RAIDING_FACTION_1`'s crysalis triggers — coordinate,
  don't duplicate.

## 3. Blue-ice quarrying — the push-your-luck loop

- Thaw-roll comp on the RM_BlueIce mineable (or MapComponent watching mined
  cells — greatbole-heartwood precedent): every N blocks cut rolls nothing / a
  fallen-debris find / a release. **Ship with debris-only rolls first**; the
  release table joins when the Horrors item lands. Cold-cutting (§2) suppresses
  the roll.

## 4. The three ruled weathers (ticket-ready since 2026-09-24)

- Ice-sand drift on Odyssey's sand grid (blue-white tint patch) — the owner's
  "goes deep" live test gates done; the Haze exposure hediff via
  `EnvironmentalWeatherExtension` (zero new C#); ice fog at BlindFog-verbatim
  severity + `maxRangeCap`. Replace the shipped `Clear 100` weather block.

## 5. The soundscape + the crack cue

- Vanilla SFX reuse/retint FIRST (artpipe is images; audio is a new pipeline
  ask — scope small): wind-over-ice ambient keyed to WeatherDefs, drift hiss,
  virr fields, ossivel choirs. One MECHANIC: a sharp cracking sustainer on the
  charge comp's existing two-longtick warm countdown, so a listening player
  gets a beat to run. Ossivel silence-alarm: choir stops when a big pawn nears.

## 6. Murrek drift re-seeding

- MapComponent listens for the drift weather's end → buried murrek re-seed at
  fresh drift cells; dig the drift, flush the thing. Burrow/unburrow job driver
  — the biome's first genuinely new one. Needs §4 first.

## 7. The Cold Hold + drift burial (mark 6)

- Blue-ice blocks as ship water stock (`WATER_KINDS_TAXONOMY_1` row); the
  pantry-bomb story rides the already-shipped `CompTemperatureRuinable` + §5's
  cue aboard. **Drift burial**: ice-sand accumulates against a landed
  gravship's windward hull (same sand grid), costing a dig-out after a storm —
  tune to read as weather, not tax.

## 8. Dovvik minesweeper + ablation salvage

- Drained plant = charge-safe for a day (flag + graphic tint on
  `RM_CompPlantCharge`); wild dovvik trails read as safe paths; tamed dovvik
  approved (owner-ruled). Ablation-line incident family ("the line gave
  something up"): IncidentDef, edge-biased placement, freeze-dried corpse via
  vanilla corpse gen — sequence AFTER §2/§3 so "the fallen" isn't
  double-authored.

## Watch out

- New .cs in an existing assembly needs its `<Compile Include>` line — silent
  no-compile otherwise.
- 🔴 Never live-test vrisk/any flyer unattended — state reads only.
- Mod Settings law: every mechanic here gets its per-feature toggle, defaults =
  shipped behavior.

## verify

- Quicktest: EMP hit on a live vhaulk detonates; a bullet kill does not; a
  Flame kill does. Tableau study grants tier flags; cold-cutting suppresses
  thaw rolls; drift end re-seeds murrek; choir goes silent on approach (state
  reads).
