rimflow verify --criterion with --sha set to a later build (a descendant, e.g. the owner's walk build) records the run and prints PUBLISHED, but the pass moves nothing: model._apply_run treats a run whose sha is not the item's built sha as stale. Record a walk or later live pass with --sha <the item's built sha from rimflow show>, even when that sha never reached origin.
item: BIGNET_PROOF_FIX_SIZE_NOT_RESTORED
home: skills/using-rimflow
