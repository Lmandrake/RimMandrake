A work-bundle id (WB-<system>-YYYYMMDD-HHMMSS) carries the UTC time of its launch, not Pacific. Read it as Pacific and a failure looks 8 hours later than its fix: 6 'not a ledger item' failures looked like 16:41 PST, after the 08:42 PST fix, and were really 08:41 PST, before it. Convert the id time, or read the record's 'at' field (epoch), before you say whether a fix came before or after a failure.
item: RIMMANDRAKE_REPAIR_ONBOARDING_LAUNCH_SO_BUNDLES_FILL_MEDIAN_ONE
home: skills/using-rimflow
