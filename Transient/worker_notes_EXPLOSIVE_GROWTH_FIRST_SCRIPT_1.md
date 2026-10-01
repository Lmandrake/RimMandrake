# Worker note EXPLOSIVE_GROWTH_FIRST_SCRIPT_1

status: AUTHORED, offline-proven, READY TO RUN (nothing run live; no bridge touched)

Files: `src/RimMandrake/ExplosiveGrowth/validation.py` (33 chains, 41 components, 25 settings in
`suite.toggles`, all 25 claimed by a component), `northstar_plan.py`, `northstar_site.py`,
`design/validation_walks/RimMandrake/ExplosiveGrowth.md` (51 `## must be true` lines, each ending
in `-> chain.component` or `-> UNCOVERED: why`; every component is named by exactly one line; no
north-star section, state DRAFT, nothing hashed), and tier `explosivegrowth_solo` in
`src/RimMandrake/Utils/modset_builder.py` (bridge + engine only; the existing `explosivegrowth` tier
adds the campaign mod `mandrake.rut.plantgrowth`, which this RM-tier script must not need).

Offline proof: `northstar_driver cli.py run --mock --mod ExplosiveGrowth --plan ... --mock-skip-site`
runs all 33 chains to completion (mock has no `jawa/set_plants`, so growth chains record mock FAILs;
expected). `lint_calls.py` over the three .py files: 0 problems over 31 literal-named calls.
`modcheck lint`: 0 FAIL. `modcheck floor --all`: ExplosiveGrowth row `walk yes, subj ok, no bar`
(DRAFT, no hashed bars, so no bar can be uncovered; the toggle floor is 25/25 by construction).
`modcheck doctor`: only the existing WARN class WALK_WITHOUT_CAPABILITY (no rimflow capability row).

## live-run sheet

Prereqs: bridge free (`python3 src/RimMandrake/rimflow/cli.py bridge who`), then
`bridge take --for "ExplosiveGrowth north-star first run"`.
1. Kill the game FIRST (modset_builder refuses while Player.log is < 3 minutes old).
2. `python3 src/RimMandrake/Utils/modset_builder.py --tier explosivegrowth_solo --apply`
   (snapshot taken; restore later with `--restore`). Tier = the bridge + `mandrake.rm.explosivegrowth`
   + Core and the four DLCs; Harmony resolves automatically. Deploy first if the game copy drifts:
   `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod ExplosiveGrowth` (dry run) then `--apply`;
   a stale DLL makes `startup_log_clean` FAIL on the missing self-test line, which is the point.
3. Launch via Steam. Tier is 3 mods: expect `Bridge token:` in ~25-90 s. Then a TEMPERATE quicktest map:
   `rimworld/start_debug_game_ready {"readiness":"playable","pauseIfNeeded":true}` (~2 min). The map must
   be 8-38 C at the centre or preflight refuses (a cold map makes every plant dormant: that is a SITE fault).
4. One line (python.exe, from the repo root):
   `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod ExplosiveGrowth --plan src/RimMandrake/ExplosiveGrowth/northstar_plan.py`
   Results: `Transient/northstar/ExplosiveGrowth_<stamp>.json`; per-component progress prints `[eg] ...` to stderr.
5. Release the bridge; `modset_builder.py --restore`.

Site prerequisites: map >= 100 on both axes, dev mode on, a player-faction map (the suite spawns one
colonist for `burst_hurts_pawns` only), centre cell at 8-38 C, no modal dialog (a stale `Verse.FloatMenu`
blocks debug tools silently). God mode not needed. The suite clears 40x40 at the anchor itself, lays Soil,
unroofs, unfogs, locks Clear weather and jumps the clock to the next midday (so the light factor is nonzero).
Pre-flight also checks all 25 settings equal their shipped defaults.

Tick budget (default settings): ~20,000 game ticks in total: soak_length 5,400; charge_hours 4,300;
churn_off ~3,200; churn_cycle ~3,200; suppression_on ~2,500; ground_tell on/off 700 each; everything else
instant. Waits > 3,000 run at Ultrafast with the real clock polled; shorter ones use `t.wait_ticks`
(~53 ticks/s). Expect roughly 10-15 minutes of wall clock for the whole run.

Expected on `explosivegrowth_solo`: the five donor-top chains (`top_burst`, `top_tinder`, `top_slime`,
`top_rupture`, `top_flush`) and `burst_hurts_pawns` record UNMEASURED "donor plant ... not loaded" BY DESIGN
(Alpha Biomes `AB_`, `RG_`, Pyrelands `RM_FE_` plants). They run for real on a list that carries the donors
(the owner's full list); that is a follow-up, not a defect. `report_reads_registry` expects >= 20 soaking
plant defs, which vanilla + 4 DLCs satisfy (CALIBRATING floor).

### what each result means
- boot_defs.startup_log_clean: FAIL = registry empty / error logged / self-test line missing (stale DLL). UNMEASURED = the startup line scrolled out of the log buffer (rerun right after launch).
- boot_defs.harmony_patches_attached: FAIL = one of the 5 patches is not attached under owner id `mandrake.rm.explosivegrowth`. UNMEASURED = the tool shape differs (`methods[].postfixes[].owner`).
- registry_report / soak_footprint: FAIL = engine not reading plants / soak grid not registering (MOD). UNMEASURED = debug action logged nothing (check Player.log for `Reached max messages limit`: HARNESS/SITE).
- soak_x10_default / soak_multiplier_tuned / master_switch_off: FAIL = ratio of `Growth rate` percent (soaked vs same-def unsoaked control) is not the setting (1 when refused). UNMEASURED = control rate 0 (SITE: night/cold) or no `Growth rate: N%` line in the inspect pane (HARNESS: shape).
- soak_length: FAIL = soak ended early or never. soak_exempt_plants: FAIL = Report cannot see the soaked bush (instrument) or exempt count wrong (registry).
- churn_cycle: FAIL points at the stage: not charging after 2 passes (the 2026-09-26 bug class), still charging after ChargeAll+2500 ticks, plant survived, no RawRice, no sprouts. UNMEASURED "SITE: ... dormant" = cold/dark/infertile.
- ground_tell_on/off, churn_off, charge_hours, suppression_on/off: see the walk lines; each states the quantity it reads (plant count near the cell, RawRice things, Report fields).
- flip_* : FAIL = the setting field is mistyped or not a static; no behaviour implied.
- settings_restored: FAIL = an earlier arm leaked a non-default (the arms restore in `finally` with the guard bypassed, so this should never fail).

## break-proofs (how each check is made to FAIL; none run, all are one-line)

Every behavioural arm has a natural negative control in the same chain or its sibling:
- soak x10: `soak_multiplier_tuned` (x3) and `master_switch_off` (x1) read the SAME inspect line; a postfix that is absent reads x1 and FAILS `soak_x10_default`. To prove live: set `soakMultiplier=1` before the run (ratio 1 vs expected 10).
- soak footprint / registry: run with `enabled=False` armed before `soak_cells_registered` -> action logs `soaked 0 cells` -> FAIL (range 25-37). Registry: an empty `byIndex` prints `soaking=0` -> FAIL.
- soak_length: `defaultSoakHours=24` instead of 2 fails the `end soaked == 0` arm.
- exempt plants: the control bush must read `immature=1` first (sanity probe: the Report can see a soaked plant); remove `Plant_TreeAnima` from `BuiltinExempt` and `topNone/exempt` drops by one -> FAIL. Set `cavePlantsNeverSoak=false` + rebuild and the Agarilux counts as immature.
- churn: the original `StepCharge` bug (dormant decays) reads `charging=0` -> FAIL at "should be charging=1". Break the top: `churnEnabled=false` is exactly `churn_off`, which must NOT destroy the plant; the two chains disagree if the setting is ignored.
- ground tell: on/off pair; ignoring the setting makes one of them fail.
- charge_hours: with 6 h the plant is still standing ~4,300 ticks in -> FAIL; so a clock that ignores the setting fails.
- suppression: `suppression_off` is the control; ignoring the setting makes `suppressed` nonzero there.
- tops (donor lists): each has an on/off pair where off must read the Churn signature (no hay / no slime / no blood / no cloud / giant dies). A top that ignores its toggle fails the off arm; a top that never fires fails the on arm.
- flips: write alt, read back; a field renamed in C# makes `mod_settings_field` fail.
- Instrument guards: `_act` UNMEASURED when no debug log line arrives; `_report` UNMEASURED on unknown shape; `_rate` UNMEASURED when the inspect line is absent. Nothing passes on "could not ask".

## theories this script already encodes as ruled out
See the walk's `## anti-guessing notes` (7 lines: charge-clock decay, cold map, log cap, stale drain_log,
x/z are the virtual mouse, stale deployed DLL, plantgrowth tier).

## unproven shapes (first live run settles them; all degrade to UNMEASURED)
`effects.logs` row shape; plant inspect `Growth rate: N%` wording; `jawa/pawn_get` `hediffs`;
`jawa/harmony_patches` `methods[].postfixes[].owner`; `jawa/time_clock` `hour`. If the first run shows a
shape is wrong, that is a HARNESS finding: fix the helper (`_log_texts`, `_rate`, `_report`) and rerun.

## missing tool (to file; named in the walk as EXPLOSIVE_GROWTH_PROBE_TOOL_1)
A companion `[Tool]` reading `Plant.YieldNow` on a charging plant, the charge record (stage/charge) for a
cell, and rupture-zone membership would turn the three UNCOVERED player-verb lines (harvest jackpot, cut
gamble, rupture mutation) and the visual tell stages into state checks. Not filed here (no rimflow writes
from this worktree); the seat may `rimflow file` it.

## UNCOVERED, with reason
visual/audio tell ladder (judge pass); rupture mutation (statistical); harvest jackpot; last-swing gamble
(need a pawn + tool); irrigation, gradient surge, Flooded Canyon flood, soaking weather, BloomBurst (other
mods or the campaign layer own the trigger).
