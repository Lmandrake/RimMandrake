# RIMMANDRAKE_RELOAD_SITE_AFTER_A_CHAIN_KILLS_ITS_COLONIST

When a chain kills a colonist of the test site, the next chain reloads the site once. Today every later chain of the job reads
"could not hold the site quiet: dead colonists" and measures nothing.

## Finding

Measured in `D:\ClaudeWork\rimmandrake\testq\done` on 2026-11-24:

- Pyrelands, colonist `Human75828` of the registered site save, dead after the first long chain. Six jobs lost their later chains:
  `J20261124T030434Z-ff8fc8`, `-033119Z-dd4fed`, `-034100Z-68c595`, `-035514Z-a16591`, `-160452Z-a771c4`, `-165417Z-2eaf7a`
  (14 chain holds UNMEASURED). The visit feed sends the chains again, and they die again.
- FlowWorks lost its later chains the same way in seven jobs of 2026-11-23 and -24 (`HARNESS_REPAIR_CAUSE_4AFBF8A2_3`).
- In `J20261124T160452Z-a771c4` the first chain ran for the whole burn line (2 PASS) before the colonist died, so the site save is
  good at its load `[guess ~85%: the first chain's hold passed]`. What killed the colonist was not read.

## spec

- `runner.reload_spoiled_site`, with the contract at the head of the acceptance script; `_hold_site`'s caller uses it.
- The reload loads the site save of the run, or makes the map of a run with no save, and is written on the chain's record.
- The dead-colonist check itself stays. No row is relabelled.

## verify

Acceptance test: `python3 src/RimMandrake/Utils/modcheck/acceptance_site_reload.py` prints `6/6`, exit 0. Seen failing on the
base 2026-11-24, 9:58 AM PST: `0/6`, exit 1. Then one Pyrelands lane job whose first chain is `burn_line` reads a verdict for a later chain.

## refs

file: src/RimMandrake/Utils/modcheck/runner.py
file: src/RimMandrake/Utils/modcheck/helpers.py
