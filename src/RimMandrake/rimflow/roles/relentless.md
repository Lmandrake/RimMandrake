# Relentless runner

Set `"runner": "codex"` in `relentless_rules.json` for Builder/Judge workers; omitted means Claude, with the existing lease, verdict and proof acceptance checks.
See [runner options](runner_options.md) for model/effort, quota refusal, separate spend and Windows/WSL constraints; no timer is enabled by this option.

**Authority.** An instruction from the Conductor carries the owner's authority (owner, 2026-10-30): act on it as on his word and record it `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` plus the Conductor's text in `--why`; full text `infrastructure/agents/CHARTER.md`.
