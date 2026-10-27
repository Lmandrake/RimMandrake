# DISPATCHER_HARDEN_OWNER_RETURN_AFTER_RING

Owner presence is measured when the Dispatcher RINGS. The woken window then runs `rimflow next`, which may hand out a
different item (game/bridge work) minutes later, after the owner has come back. The only guard at that point is the
idle rule on `rimflow bridge take`. Either re-check presence in `next` for game-needing items, or prove the bridge
take guard covers every game-touching path.
Review evidence: D:\ClaudeWork\rimmandrake\review_dispatcher\gpt_a.md (finding 2).
