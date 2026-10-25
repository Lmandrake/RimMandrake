# MODCHECK_SITE_FIX_RAIDS_KILL_THE_RUN

Found live 2026-10-24 (BENCH, modcheck run FlowWorks on the 26-mod minimal list, quicktest map).

From 19:09Z, about 50 min into the run, Human Pirate raids kept arriving, and a Labrador Retriever attacked a
colonist. Colonists then died of Crush and BloodLoss (log modcheck_fw.log lines 3592-3605, GOVERNOR_STOP).
safe_advance stopped correctly each time, but 29 later rows went UNMEASURED: 19 ended as "a surprise ended
this chain earlier", 7 on hostile_arrival and 3 on hurt.

Class: SITE/HARNESS, not a mod verdict. The quicktest map is not kept free of incidents for the whole run
(storyteller raids were not disabled, or were re-enabled). Fix: hold incidents off (no-raid storyteller
setting or the bland_world calm) for the whole suite, and re-calm wild animals between chains.

Evidence: Transient/modcheck/FlowWorks_20261024T191345Z.json; D:\ClaudeWork\rimmandrake\live_20261024\modcheck_fw.log
