# RIMMANDRAKE_RESET_GRAFFITI_MESSAGE_COUNTERS_EACH_GAME

Found by the Stage 2 preflight of Graffiti 0.1.0 (steward run RIMMANDRAKE_STEWARD_GRAFFITI_PREFLIGHT_STAGE, 2026-11-15); table `design/concepts/Graffiti/version/test_table.json`, record `design/concepts/Graffiti/version/preflight.json`.

## spec
Test T_MSG_COUNTERS_RESET in the table, specified at Stage 2, built at Stage 3 (red first). Observes: GraffitiSocial.messagesSent and messagesKept read 0 at a new game's start (held walk defect #6)
File: `src/RimMandrake/Utils/selftest_graffiti_message_counters.py`. Reads: src/RimMandrake/Graffiti/Source/GraffitiSocial.cs, src/RimMandrake/Graffiti/Source/RM_GraffitiSocialProof.cs

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_graffiti_message_counters.py` exits 0 on the shipped mod and goes red on a planted mutant of the behaviour (watched failing 2026-11-15: the file does not exist yet). Expected: 1 pass.
