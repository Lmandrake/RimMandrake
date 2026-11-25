A next Design Version keeps the last version's version/bars.md unless the lock re-pins it. Then the preflight pin check reads the old pins and refuses locked files that did not change after the new lock (ExplosiveKnockback 0.2.0: 4 false C12 refusals). Before you trust a C12 refusal, compare each file with its blob at VERSION.json locked_from_commit. If the file matches that blob, the pin is stale; it is not a changed bar.
item: RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE
home: design/specs/2026-11-13-maturation-pipeline.md
