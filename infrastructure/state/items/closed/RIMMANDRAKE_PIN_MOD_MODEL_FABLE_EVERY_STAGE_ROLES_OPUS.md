# RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS

## spec
The owner admitted WreckedMachines on 2026-11-19 (~8:35 AM PST, `RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST`)
in answer to CARD B, which proposed: "Take the next mod entering the pipeline and let Fable build it start to finish."
Today the pipeline cannot pin one mod to Fable. Measured in the bench clone at 03252bb8bc:

1. Stage 1, the Designer: `role_launch.py run-now` has no `--model`. The Designer role is `"model": "opus"` in
   `dispatcher_schedule.json` (every role is opus). `MODELS_OK = ("opus", "sonnet")` (role_launch.py l.166) refuses
   fable in `model_by_mode`. `MODEL_VARS` (l.231) has no fable entry. The command passes `role["model"]` raw to
   `claude --model` (l.3391), and the alias `fable` resolves to claude-fable-5-1 (measured 2026-11-12,
   detached_helper.py l.82). The ladder means Fable 5.2, so it must pass `claude-fable-5-2`.
2. Stages 3 to 7 (offline build, fixer, steward, holder, builder on red deciders): `maturation_dispatch.py` reads one
   global `cfg["model"]` / `cfg["steward_model"]` (l.1411, 1417, 2177, 2309, launch_kind l.3200-3223). There is no
   per-mod field. `maturation.launch_mod` already accepts `--model fable` (l.3958) and detached_helper already maps it
   to `claude-fable-5-2` (MODEL_IDS l.83), so only the choice is missing, not the plumbing.
3. Judges and the live driver stay as they are, by the owner's model ladder (2026-11-12, `~/.claude/CLAUDE.md`): "opus
   for ... judging another agent's work" and "Fable is never used for: ... waiting on a live resource". So the blind
   challenge (JUDGE_MODELS), the Designer's exam reviewers, the coverage judge and the in-game driver (LIVE_MODELS =
   ("opus",), maturation.py l.3012) keep their own models. "Fable builds it start to finish" is read as: every
   builder role at every stage is Fable; every judging or live role is not. This reading is the Conductor's
   delegated call; see the question below.

## the smallest change (do not widen it)
- `maturation_dispatch.json`: a new map `"mod_models": {"WreckedMachines": "fable"}`.
- `maturation_dispatch.py`: one helper `build_model(cfg, mod)` returning `cfg["mod_models"].get(mod)` or the old
  global; called at the builder launches (l.1411, 1417, the non-in-game branch of l.2177, the steward l.2309) and in
  `launch_kind` so the dry-run table prints the true model. In-game and the blind judges keep `ingame_model` /
  JUDGE_MODELS.
- `role_launch.py`: a Designer launch whose request carries a concept reads the same map for the concept's mod and
  passes `--model claude-fable-5-2` (add `"fable"` to MODELS_OK and a MODEL_IDS-style full-id map, as
  detached_helper does). Read the map where the command is built (l.3391), not in the `run-now` CLI: a harvest chain
  and the orphan sweep also launch through a `run_now` request (`chain_ask`, measured 2026-11-19 with
  `D:\ClaudeWork\rimmandrake\helpers\wm_admit_20261119\probe_sweep.py`), and a run they start must be Fable too.
  DesignerCodex and the exam reviewers are unchanged.
Effort [guess ~60 to 100 lines plus one selftest; one builder session].

## the dollar stops are priced for opus (measured 2026-11-19; a ceiling, so the Conductor's act)
`role_launch.MODEL_PRICES` puts claude-fable-5-2 at exactly 2x claude-opus-5-5 on every field, and `spend_watchdog.py`
stops a run at its cap in list dollars at its own model's prices. Measured run costs:
- Designer (`run_budget_usd` $8): 111 runs with a cost in `D:\ClaudeWork\rimmandrake\dispatcher\roles`, p50 $1.38,
  p90 $2.92, max $5.06; 3 of 111 cost over $4, so at 2x they would pass the $8 stop.
- Detached runs on a $15 budget (`cap_usd`, the offline builder's): 194 runs in
  `D:\ClaudeWork\rimmandrake\dispatcher\detached`, p50 $4.12; 48 cost over $7.50 and 12 already reached $15.
  At 2x about a quarter would be stopped mid-run.
Evidence: `D:\ClaudeWork\rimmandrake\helpers\wm_admit_20261119\designer_costs.txt` and `build_costs2.txt`.
The caps are our own rule, not his bar (his bar is "Don't let any burn go to 90M", 2026-11-12). Without a per-mod
cap at the price ratio, the experiment loses about a quarter of its build runs to the stop, and a stopped run is
compared with an opus run that was never stopped. The builder of this ticket adds `"mod_cap_x": {"WreckedMachines": 2}`
next to `mod_models`, or the Conductor rules that the caps stay, before the first WreckedMachines build launches.
The builder does not set the value itself.

## question for the Conductor (relay only if he must rule)
Does "start to finish" include the stage-6 in-game driver? His ladder says Fable never waits on a live resource; his
2026-11-16 ruling put the Test Pilot (a live sitting) on Fable. Until he rules, in-game stays opus.

## criteria
For WreckedMachines, every builder launch (Designer run-now, offline build, fixer, steward, holder, builder on red
deciders) passes model `claude-fable-5-2`; for every other mod the model is unchanged (opus); judges and the in-game
driver are unchanged for every mod.

## verify
Acceptance test: a selftest (in `selftest_maturation_dispatch.py` and `selftest_role_launch.py`) that, with
`mod_models = {"WreckedMachines": "fable"}`, (1) `launch_kind` and the captured launch argv for a WreckedMachines
offline_build row read `fable` and the detached command reads `--model claude-fable-5-2`; (2) the same rows for
Graffiti read `opus`; (3) a WreckedMachines blind_challenge and in_game row keep their judge/live model; (4)
`role_launch.py run-now --role Designer --concept design/concepts/WreckedMachines` (dry run, no --apply) builds a
command with `--model claude-fable-5-2`, and with `--concept design/concepts/Graffiti` builds `--model opus`. Watch it
fail first on the current code.
