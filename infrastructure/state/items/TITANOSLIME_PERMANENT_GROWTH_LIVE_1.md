# TITANOSLIME_PERMANENT_GROWTH_LIVE_1 — the one ruling from 2026-09-21 still unproven

## the ask

The owner overturned one of the Titanoslime's six shipped defaults on 2026-09-21: **growth
is PERMANENT, not reversible.** Built at `8b9483b2e` (69/69 selftests, 0 warnings), deployed
and `VERIFIED in sync` the same day.

⛔ **It was NOT proven by the cold load, and could not be** — it is runtime behaviour over
time, and a startup log can only show the def loaded. That was written down BEFORE the load
rather than discovered after, and the load's own run sheet records it as not tested.

## what is known

- **Mechanism, read not assumed:** `RM_CompEngulfer.absorbedMass` (scribed float) maps to a
  stage index via `StageFor()`, applied with `Pawn_AgeTracker.LockCurrentLifeStageIndex()`.
  Every mass-changing path — eating, absorbing prey, starvation decay, dry-ground decay,
  per-shed loss — funnels through one function, `AddMass(delta)` in `Titanoslime.cs`, which
  gates any NEGATIVE delta behind `SlimeSettings.titanoslimeReversible`.
- The change was a **default flip** of that flag, `true` → `false`, in the field initializer
  and the `Scribe_Values` fallback. The player-facing toggle stays in Mod Settings, unchecked.
- `absorbedMass` and the locked stage index are both already scribed, so permanence should
  survive save/load with no new persistence code.

## spec — what an honest test looks like

1. **A scratch map, not the campaign.** ⛔ Do not spawn one into the canonical colony or the
   founders save. `rimworld-debug-testing` covers throwaway dev quicktest colonies.
2. Spawn a Titanoslime, feed it until it advances at least one life stage, then drive it into
   every shrink path: starvation, standing off slime terrain, and wounding/shedding.
3. **Read `absorbedMass` and the life-stage index back as RAW fields** after each. Not the
   inspect string, and not `success: true`.
4. Save, reload, read them again — permanence that does not survive a round trip is not
   permanence.
5. Flip `titanoslimeReversible` ON and confirm shrinking returns. **A test that only shows
   "it did not shrink" cannot tell a working gate from a broken shrink path** — the control
   is the point.

## Watch out

- 🔴 **§4b of the `rimbridge` skill: unpausing is the most consequential call on the bridge.**
  This test needs time to pass with a large predator on the map. Keep it on a throwaway map,
  list what else is there first, and re-pause the moment the window ends.
- ⚠️ `maxPreyBodySize` is 20 and `manhunterOnDamageChance` is 1.0 — it will eat things and it
  will not disengage.
- ⚠️ The mod renders **magenta** (no art yet). Not a defect, and not evidence of anything.
- ⚠️ `GELATINOUSSLIME_FIRST_LOAD_ERRORS_1` is open against this same mod — fix those first or
  a failure here will be ambiguous.

## criteria

A Titanoslime that has grown does not shrink through any path with the shipped default, the
behaviour survives a save/load round trip, and flipping the setting on restores shrinking.
