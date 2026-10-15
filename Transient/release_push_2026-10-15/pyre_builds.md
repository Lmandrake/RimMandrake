# Pyrelands BENCH builds — 2026-10-15

Owner, 2026-10-15: "No withheld functionality. Build it all, test it all, get it all working."
Offline only (no deploy, no bridge). One section per item; updated as each lands.

## 1. STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY
state: BUILT offline (companion built with --gm, NOT deployed - no deploy this session)
- `jawa/static_call` now coerces any Thing/Pawn parameter from an exact ThingID (`Human123`) or a bare
  thingIDNumber, current map first then every map; refused with up to 12 candidate ThingIDs when absent or
  of the wrong type; reply carries `thingArgs[]` (how each was resolved).
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCompanionProbeTools.cs`
- Pyrelands `furnace_warmth` row: a second colonist 11 cells off as the control; bar = `OffsetFor(beside) > 0`
  and `OffsetFor(away) == 0` via `jawa/static_call RimMandrake.Pyrelands.FurnaceWarmthField.OffsetFor <ThingID>`;
  `jawa/thing_ambient_temp` delta recorded beside it (not graded: three other mods postfix the same getter).
  UNMEASURED (not PASS) if the companion is not the widened one.
- live proof (game down for the deploy): `python3 src/RimMandrake/bridgetools/build.py --gm --apply`, then
  `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\northstar_driver\cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains furnace_warmth --no-record`

## 2. ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE
state: BUILT offline (FireEcologyHook.dll + .srchash committed; not deployed). Dome ART not generated: filed
`ASHWALLOW_DOME_SKETCH_AWAITS_ITS_NEW_BODY`.
- `Source/RM_BurrowHeatReaction.cs` (new): Pawn.PostApplyDamage postfix - a heat-category hit (armorCategory Heat:
  Flame/Burn/Beam/any modded incendiary) starts RM_Burrow at once, InterruptForced, with a heat hold (600 ticks,
  `PyrelandsTuning.BurrowHeatHoldTicks`); a hit while domed extends the hold. Refused for dead/downed/mental-state
  animals. PawnRenderNode_AnimalPart.GraphicFor postfix draws `RM_BurrowOnFireExtension.domeTexPath` while
  RM_Burrowed holds; RM_Burrowed now sets forceRenderTreeRecache. No art at the path = standing body + one log warning.
  `ProbeDome(Pawn)` for the script.
- RM_JobDriver_Burrow surfaces only when no fire is near AND the heat hold has run out (`RM_FireEcoKernel.BurrowMayEmerge`);
  hold saved in ExposeData. Kernel decisions fuzzed (256-row DomeOnHeatHit table + hold/emerge boundaries).
- New setting `burrowDomeOnHeatHit` (default ON, greyed under burrowOnFireEnabled), in preflight DEFAULTS.
- RM_Ashwallow: `domeOnHeatHit`, `domeTexPath = Things/Pawn/Animal/Pyrelands/Ashwallow/AshwallowDome` (art absent).
- Script: chain `heat_dome` (pad 60,60): `ashwallow_domes_on_heat_hit` (Burn hit, no ground fire -> burrowed + RM_Burrow
  + hold running; body draws the dome path when the art exists; surfaced after hold+300) and
  `ashwallow_heat_dome_toggle_off`.
- Why no art: the installed body is still the 10-03 "terran hippo" the owner ruled REDO on 10-11; the redo render
  (`D:\Luke\dev\_artpipe\_artsrc\enact_f6734fd2_ashwallow_v1_east\`) exists but is not installed, and no codex CLI
  is on this seat's PATH. A dome matched to the outgoing body would be drawn twice.
- live proof (deploy Pyrelands + the widened companion first, game down):
  `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\northstar_driver\cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --chains heat_dome --no-record`

## 3. TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED / TESTENV_BURROW_COLD_PROVE_RELOAD_PER_TRIAL
state: BUILT (committed into the repo; offline-checked)
- The diag chain (`Transient/bench_live_20261014/burrow/validation_with_diag_chain.py`, appended to an out-of-repo
  validation.py copy) now lives in `src/RimMandrake/Pyrelands/validation.py` as `burrowers_diag`, registered ONLY when
  `PYRE_BURROW_DIAG=1` (a normal suite run never sees it; declaration probe: 30 chains off, 31 on, both clean). Defaults
  are one near trial per reload; heat-guarded like every non-needs row; JSON only when BURROW_DIAG_OUT is set.
- Runner: `src/RimMandrake/Pyrelands/diag/burrow_trials.sh FIRST LAST [FP] [TAG] [TILE]` - reloads the site fixture before
  every trial, runs from the read-only mirror, output to `D:\Luke\dev\_rmscratch\burrow_trials` (outside the repo).
  Dropped the scratch copy's RM_ALLOW_CONCURRENT_BRIDGE=1 override.
- live proof (bridge held, pyrelands tier up, fixture built): `src/RimMandrake/Pyrelands/diag/burrow_trials.sh 1 3`
  -> each trial `[diag]` with burrowedAt set and `burrowers_dive_diag PASS`, colonists unharmed.
