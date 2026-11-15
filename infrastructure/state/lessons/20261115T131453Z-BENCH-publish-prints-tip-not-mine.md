./publish printed PUBLISHED 76fcfbea62 (and 'close with --sha 76fcfbea6234'), but that was a peer window's ledger-only commit made in the same clone 9 s after mine and pushed in the same landing; my work was 03aefb9edb. rimflow close refused ('touches nothing but the ledger') and a verify pass got recorded on the wrong sha. Before close/verify, find your own sha with git log --oneline -3 origin/main -- <your path>, never trust the PUBLISHED line when the clone is shared.
item: RIMMANDRAKE_FIX_RESTART_HELD_BY_OWN_HELPERS_DRIVER_LOCK
home: .claude/skills/clone-landing-commits
