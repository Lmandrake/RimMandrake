Codex workers now have distinct seats: CODEX_ARCHMAGI_FWDRAIN and CODEX_STEVEDESKTOP_HUGETHINGS, covering handoffs, ledger shards, bridge holds, lessons, queues and host guards. Codex BENCH handoffs are refused.
Both loops’ next-round prompts and scripts were updated without restarting either loop. SteveDesktop’s future service launch uses its own name.
PUBLISHED identity: 5d3a2a8bec25bef5c5944ab3f842a012526e9814
PUBLISHED queue follow-up: 55c26b2175c649b1fb9cbf5d1b3452fce92b2984
Hard stops now send one phone notice with metered reset/restart timing; wake messages identify the account switcher. The existing restart-on-reset guard was retained and tested.
PUBLISHED stop notices: d8962501650ee180c4d60a16989d3f344488ab72
Tests: all 12 relevant selftest files passed. Fleet commands and phone delivery were faked; loop scripts passed shell syntax checks.
UNVERIFIED: real phone delivery, real fleet restart and next-round identity adoption. No real fleet-stop or fleet-start was triggered.
Remaining: account-plan still runs from the dispatch clone; deployment there is left under the task’s prohibition on touching another clone. SteveDesktop’s inherited host-guard lock keeps its existing label until the running loop ends.
