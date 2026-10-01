# worker note BACTA_FIRST_SCRIPT_1 — first north-star script for Bacta (mandrake.rsw.bacta)

Status: READY TO RUN (offline proof done; no live run, bridge not touched).

Files: `src/RimStarWars/Bacta/validation.py` (8 chains, 35 components, 12 toggles/tunables listed) · `northstar_plan.py`
(USE_SUITE, EXPECT_MODS mandrake.rsw.bacta, registers `mock_extension`) · `northstar_site.py` (preflight) · `northstar_mock.py`
(in-memory Bacta + 15 BACTA_MOCK_BREAK modes) · `selftest_bacta_mock.py` · walk `design/validation_walks/RimStarWars/Bacta.md`
(DRAFT, no north star section, so `modcheck floor` says "no bar", not REFUSED). Harness edit: `transport.py` MockGame.ext hook +
`cli.py` open_session(plan) so a plan can bring its own offline model (nothing else changed).

## Offline proof
- `python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Bacta --plan src/RimStarWars/Bacta/northstar_plan.py --mock-skip-site` -> 35/35 components PASS.
- `python3 src/RimStarWars/Bacta/selftest_bacta_mock.py` -> clean all-PASS and each of 15 injected defects flips exactly its named component to FAIL.
- `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py src/RimStarWars/Bacta/validation.py` -> rc 0, no UNCHECKED.
- `modcheck floor --all`: Bacta row `no bar` (DRAFT walk; verdict is never REFUSED).

## How each check is broken live (prove it can fail)
| component | break it |
|---|---|
| defs_resolve / tank_def_wiring | deploy a copy with a def renamed or the immersion comp removed |
| trader_stock_patch_landed, doctor_recipes_patch_landed | change a patch xpath (a patch matching nothing logs nothing) |
| settings_ship_defaults | leave a prior run's setting changed |
| heals_fresh_wound_at_tuned_rate, drains_bacta | set woundHealPerDay/fluidCostPerDay by hand, or comment the call in TryHealPawn |
| never_regrows_never_touches_brain | delete the `Hediff_MissingPart` or `IsBrainOrMind` guard in BactaHealingUtility |
| scar_erasure_off | remove the `scarErasureEnabled` gate |
| unpowered_tank_does_not_heal | drop `Powered` from `Active`/CompTick |
| needs_held_while_immersed | remove HoldNeedsSteady |
| dry_tank / eject | remove the autoEject gate |
| droid assist | ignore `medicalDroidEnabled` in DroidAssisting |
| patch off / revival off / window | remove the `fieldItemsEnabled` / `revivalEnabled` / window gate |

## LIVE-RUN SHEET
1. Tier: `python3 src/RimMandrake/Utils/modset_builder.py --tier bacta` (dry run; `--apply` swaps ModsConfig: refuses within 3 min of a Player.log write, kill the game first). Tier `bacta` = Core + all five DLCs + RimBridge + mandrake.rsw.bacta (3 mods with dependencies). Not applied here.
2. Launch via Steam, wait for `Bridge token:` (small list, about 1-2 min, not 15).
3. Needs a PLAYING colony map with the centre 40x40 free and >= 80x80 (use `rimworld/start_debug_game_ready`; read the FIRST exception in Player.log if it fails). Colony pawns not required: the suite spawns its own `Colonist` pawns. No god mode needed.
4. Hold the bridge (`rimflow bridge take --for "BACTA_FIRST_SCRIPT_1"`), then one line:
   `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Bacta --plan src/RimStarWars/Bacta/northstar_plan.py`
   Results: `Transient/northstar/Bacta_<utc>.json`; per-component progress lines `[bacta] ...` on stderr.
5. Tick budget: about 55,000 game ticks in total (heals 2500+2500+3000 plus refuel/enter 1400 each chain; scar 3500; power 3000; dry 4500; droid 1400; patch 1800; revival 4500 plus fixtures). `t.wait_ticks` measured ~53 ticks/s, so expect 15-25 minutes. The longest single wait is 3000 ticks.
6. Order matters little: each chain rebuilds its own site and restores shipped settings at its start. Settings are static fields, never persisted (jawa/mod_settings_field does not write ModSettings.xml).

## What a PASS / FAIL / UNMEASURED means
- content.* PASS: defs/patches/settings load as shipped. FAIL names the missing def or the patch that matched nothing: MOD (def/patch). `no_bacta_errors_*` FAIL: first Error line naming Bacta (log buffer is bounded; PASS late in a long session is weaker, a Player.log read is the authority).
- tank_heals PASS = the central law holds live. `heals_fresh_wound_at_tuned_rate` FAIL with drop near 0 and `enters_and_reports_off` PASS: CompTick not running (MOD). Drop correct but `never_regrows...` FAIL: MOD law broken.
- UNMEASURED always names why: typically `Refuel`/`EnterBuilding` not accepted (SITE: pawn cannot reach/reserve), spawned stack not found (HARNESS), no 'Bacta: n / m' inspect line, search_debug_actions returned no 'Make injuries permanent' (HARNESS: result shape never seen live). Fix the cause, never loosen the check.
- scar chain: if the pre-enter injury is removed when made permanent the component is UNMEASURED (fixture), not PASS.
- UNCOVERED by design: infection assist and immunity (no ImmunityRecord tool; WoundInfection kills on add), spray / doctor bills / potency / droid multiplier, visuals.

## Unverified assumptions to watch on the first live run (shapes I could not see offline)
- `jawa/ordered_job` targetAId/targetBId for vanilla `Refuel` (A=tank, B=fuel stack, count) and `EnterBuilding` (A=tank), `UseItem` (A=item); `RSW_CarryCorpseToBactaTank` (A=corpse, B=tank, from the driver source).
- `jawa/inspect_string` rows key `inspect` as a list (per its docs); `jawa/drain_log` rows `type`/`text`; `jawa/get_defs deep=True` showing `stockGenerators` contents (else UNMEASURED); `Muffalo.recipes` includes vanilla AdministerMechSerumHealer (control).
- A Bomb on a colonist (`jawa/damage`, up to 6 hits, allowColonists) makes a corpse; the build site for a 1x2 tank at rot 2 leaves a reachable interaction cell.
- Pawns immersed are ejected at the first 250-tick pass if nothing healable is left, so every chain adds its wound BEFORE EnterBuilding (walk anti-guessing note).
