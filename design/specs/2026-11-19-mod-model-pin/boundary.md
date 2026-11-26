# BOUNDARY: one mod's builders on a pinned model, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/mod_model.py`, the store's `mod_models` table and `pipe model` in `control.py`, and the
launch sites that read them: `maturation_dispatch.py` (`decide`, `execute`, `launch_stage`, `road_back_holder`,
`cert_launch`, `launch_kind`, `_tick`), `maturation_autonomy.py` (`_gate`, `_execute_one`) and `role_launch.py`
(`launch_role`, `launch`). Item: `RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS`. Written 2026-11-19. Each
promise has a test of its name in `src/RimMandrake/rimflow/selftest_mod_model_pin.py`. No test launches a model run: every
launcher is a fake that records the argv it was given.

## ACCEPTS (the only inputs the route is built for)

- **a-pin-is-an-alias-with-a-full-id.** A pin names a tier of `role_launch.TIERS` (`fable`, `opus`, `sonnet`). The
  environment names the tier's id (`role_launch.resolve_model`, the one alias table:
  `design/specs/2026-11-22-run-spend-and-model-alias/boundary.md`), and that id has a row in
  `role_launch.MODEL_PRICES`.
- **one-pin-per-mod.** A pin is per mod, keyed as the control store keys a mod (the concept folder's name).
- **caps-priced-for-opus.** Every cap a pin scales was set from Opus 5.5 runs (`mod_model.CAPS_PRICED_FOR`).

## DOES NOT SURVIVE (not promised)

- **a-pin-set-inside-one-tick.** The Dispatch tick reads the pins once; a pin set after that read binds at the next
  tick. A run already live keeps the model it started on.
- **a-codex-runner.** A Designer run on the codex runner is not a Claude model; a pin does not change it.
- **the-test-pilot.** An rm-testpilot sitting runs on its own pilot tier (`run_store.pilot_tier`), pinned or not.
- **limits-not-priced-here.** `stage_ceiling_tokens` (a ceiling, the Conductor's) and the Designer's advisory weighted-token
  budget are not scaled; at Fable's price both fill twice as fast. Filed:
  `RIMMANDRAKE_PRICE_CEILING_AND_DESIGNER_TOKENS_FOR_PINNED_MODEL`.

## PROMISES (each one is owed a test of the same name)

- **a-pin-is-set-and-lifted-in-the-store.** `pipe model <Mod> fable --why ...` writes one act and the pin reads back at
  once, with no publish; `pipe model <Mod> default --why ...` lifts it.
- **an-unknown-pin-is-refused-by-name.** A model that is not pinnable (`haiku`, a typo), or a tier whose variable
  is unset, is refused with its name, and nothing is written.
- **no-pin-reads-empty-not-unreadable.** A store with no pin reads `{}`; a store that cannot be read raises
  Unreadable, never `{}`.
- **pinned-offline-build-launches-on-the-pin.** For a pinned mod the offline build's launch is given model `fable`,
  the detached run's claude argv reads `--model claude-fable-5-2`, and `launch_kind` prints `fable`.
- **unpinned-mod-keeps-the-global-model.** For a mod with no pin every launch reads the shipped model and cap.
- **judges-and-live-driver-keep-their-models.** For a pinned mod the blind challenge launches on the shipped model with
  `blind_cap_tokens`, and in-game acceptance on `ingame_model` with `ingame_cap_tokens`.
- **every-builder-kind-launches-on-the-pin.** For a pinned mod the steward, the fixer, the holder and the builder on red
  deciders are given model `fable` (their launch and `launch_kind`).
- **build-cap-scales-by-the-pin-price.** A pinned mod's `cap_tokens`, `steward_cap_tokens` and `fix_cap_tokens` are the
  shipped caps times the price ratio (2 for Fable 5.2 over Opus 5.5), enforced through `spend_watchdog.wrap` (`--cap-usd`, the caps turned to list
  dollars at the launch alone by `role_launch.weighted_to_list_usd`),
  never `--max-budget-usd`, and no cap or spend is written into the brief.
- **designer-run-now-chain-and-sweep-launch-on-the-pin.** A Designer run on a pinned mod's concept, asked by
  `run-now`, by the harvest's chain (`chain_ask`) or by the orphan sweep (`chain_sweep`), launches with
  `--model claude-fable-5-2` and its run budget scaled; on an unpinned concept, `--model opus` and the shipped budget.
- **designer-launch-names-its-mod.** A Designer launch is admitted by the control store under its concept's mod, so a
  `pipe off <Mod>` refuses it at its start check.
- **an-unreadable-pin-launches-nothing.** When the pins cannot be read, the tick launches nothing (each mod held
  UNREADABLE) and a Designer launch is refused by control, naming the cause.
- **a-pin-it-cannot-price-launches-nothing.** A pin whose model is not pinnable or has no price, met at the tick, is a
  decision `model_unknown` naming it, and nothing launches on that mod.

## LIMITS

- **The scale (2 for Fable 5.2).** Guards: a runaway unattended burn (owner 2026-11-12: "Don't let any burn go to 90M
  this time ok?"). Evidence that the unscaled cap misfires: 48 of 194 Opus build runs cost over $7.50 and 12 reached
  $15, so at Fable's 2x price about a quarter would stop mid-run; 3 of 111 Designer runs cost over $4 against its $8
  stop. The ratio is computed from `MODEL_PRICES`, never typed in.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
