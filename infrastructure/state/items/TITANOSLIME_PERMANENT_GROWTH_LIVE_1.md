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

## RESULT — proven live, 2026-09-21

Tested on a throwaway `start_debug_game_ready` scratch map (never the campaign save), one
Titanoslime (`RM_Titanoslime58137`), bridge taken/released around the session. Values read
as RAW SCRIBED FIELDS off `.rws` saves parsed with `xml.etree.ElementTree` (never the
inspect string, never a bare `success: true`) — comp fields on this mod are Scribed flat
onto the Pawn element (no `<comps>` wrapper node), confirmed by reading the raw XML.

- **Baseline** (spawn roll): `absorbedMass=4`, `ageTracker.lockedLifeStageIndex=1`.
- **Growth, real path**: fed a rat corpse, `absorbedMass` rose to `4.01200008` via the
  ordinary `TickRecordPoll` → `AddMass(+)` path (not the dev gizmo) — confirms the positive
  side of the mechanism before testing permanence.
- **All three shrink paths driven simultaneously, shipped default
  (`titanoslimeReversible=false`)**: forced `Food` need to 0 (Starving) and kept it there;
  held off any `RM_SlimeTerrain`-tagged terrain for 70,000 ticks (`ticksOffSlime` read back
  as `70000`, past the 60,000 dry threshold); applied 35 Blunt damage (armor-penetration
  1.0) to cross the shed threshold — a `RM_Gelatid` visibly spawned (shed confirmed firing)
  and `damageSinceShed` reset to 0 (confirmed in the raw save). **`absorbedMass` stayed at
  `4.01200008` and `lockedLifeStageIndex` stayed `1` through all three** — the gelatid
  proves the shed event ran; the unchanged mass proves `AddMass`'s negative-delta gate
  blocked it, same for the decay paths that had been live-attempting a cut every 2500-tick
  interval for the whole 70k-tick window.
- **Save/load round trip**: saved, reloaded (`mapCount` went 0→1 across three polls, ~6s),
  re-read the same pawn from a fresh save taken right after load with zero ticks stepped —
  `absorbedMass=4.01200008`, `lockedLifeStageIndex=1`, identical. Permanence survives
  serialization.
- **Control — flip `titanoslimeReversible` ON** (`jawa/mod_settings_field`,
  `RimMandrake.GelatinousSlime.SlimeSettings`, confirmed `False→True`), reapplied the same
  35 Blunt-damage shed stimulus: **`absorbedMass` dropped `4.01200008 → 3.01200008`** (exactly
  `-massPerShed`), a second gelatid spawned. This is the falsification control the spec asked
  for — the SAME stimulus that was blocked under the default now succeeds once the gate is
  open, so the permanence result is the gate working, not a broken shrink mechanism.
- Setting restored to shipped default (`titanoslimeReversible=false`) before release; game
  left paused; bridge released; all seven throwaway `TITANOSLIME_LIVETEST_*.rws` saves
  deleted (pure verification snapshots, not review saves — nothing kept per repo default).

**Criteria met in full.** Closed.
