# CONTAGION_MECHANICS_BUILD_1 — the Burn/Bloom engine and the four ruled mechanisms

Ruled at `CONTAGION_BEDAZZLE_SITTING_1` (2026-09-27, owner: "Approved, this looks
great!"). Design authority: the sitting's ledger notes + the 2026-09-27 amendment
block in `the_contagion.md` + `contagion_grotesque_cast_2026-09-27.md` §Coalescence/
devices. Separate from `CONTAGION_RULED_CONTENT_1` (the cast defs) so each has its
own catcher; build in this order — the weather is the foundation.

## 1. The Burn and the Bloom (the biome's crown mechanic)

- The Bloom: standing storm state (donor red fog re-skinned; accuracy ×0.4 stands,
  ban 5). The Burn: rare tears — a WeatherDef we own firing UV damage +
  radiation-flavoured pressure on anything in the open; natives dive (AI: seek
  roof/water/goo), the fog lifts, ranged works.
- **The tells** (weather-window, ruled): our MapComponent knows the transition
  early — Gawpsacks sink/land N seconds before a Burn, Rattlegropes rattle
  (sound + shake). No forecast UI exists in vanilla, so the tells are the
  forecast.
- Ambient soundscape: endless rain/thunder baseline under the Bloom; the sheet §9
  sound direction. (Silence-as-alarm mechanic was CUT — ambience only.)

## 2. The Coalescence (the giant)

ONE continuous organism (ruled by card): spawns during long Blooms, absorbs
nearby Unfinished (they walk in and despawn into it), grows through 3 staged
forms (graphic swaps, art queued at 512: coalescence_stage1/2/3 — silhouette
continuity briefed), continuously emits manhunter Unfinished at everything not
absorbed. Cannot leave the storm shadow; ANY Burn kills it (natural or Repulsor-
forced) — death collapses it into a mulch + genome-sample bonanza.

## 3. The Cloud Repulsor

Helix trade device (+ quest availability BENCH's to wire into trade tables):
warmup, then forces the Burn while powered on a Contagion map; on any other map
cancels rain/fog-class weather. **Gravship hardpoint variant is the ship touch**
(buildable on a gravship, same beam). Art queued (purple vertical beam).

## 4. The Sunbeam

Helix UV projector weapon, purchasable + quest-given: low damage vs people +
nasty sunburn scar hediffs; large multiplier vs Contagion natives and the goo.
**Doubles as the ruled Contagion-touched ARREST tool**: a medical use that stops
mutation progression permanently; what changed stays (sheet §7, now ruled).

## 5. The bizarre Grown-limb line

Five gestation outcomes on the BUILT genome loop (Monstrous-grade samples roll
them): Pillar Arm, Lash, Eyeburst, Caudal Spring, Bellows — each a
`Hediff_AddedPart` with `renderNodeProperties` (the Anomaly Tentacle mechanism,
verified against installed defs: per-facing drawData, drawSize for oversized
limbs, Spastic writhe), melee tools where ruled, and its cost rider (see cast
doc). **Removal surgery spawns an Unfinished** (FleshbeastEmerge comp shape).
Every limb a bargain, never an upgrade — ban 6 untouched (deliberate surgery,
not spore mutation).

## Watch out

- Undersurge lesson (TWILIGHT_REVIEW_FIXES_1 #3): every map-wide roll gates on
  the BIOME, not just settings — the Burn must never fire on a non-Contagion map.
- Plant comps tick CompTickLong only (Rattlegrope's rattle, Wombpod).
- Weather transition control vs vanilla WeatherDecider: own the biome's weather
  commonalities so the Burn frequency is ours.
- Mod Settings per the standing law: Burn frequency/damage, Coalescence on/off,
  device availability — feature-gated, defaults = shipped.

## verify
- Quicktest: Burn fires only on RM_Contagion maps; tells precede it; a
  Coalescence grows, absorbs, emits, and dies to a Repulsor-forced Burn; a
  Sunbeam arrest stops a Contagion-touched progression; each limb renders on a
  pawn in all four facings and its removal spawns an Unfinished.
