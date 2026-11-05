# ENACT_X_FIX_PURGE_OF_KEPT_ART

Found in the independent review of ART_MARKS (e4aaf37692), 2026-10-26. The card (owner 2026-10-26 19:06,
delegation_policy 2.3) says his ✕ on a kept or in-game picture ARCHIVES it, "never a purge". `enact.build_plan`
still PURGES in two branches that run before the new archive branch:

1. Pictures live in a Graphic_Random folder: the folder retire+purge branch (`P["retire"]` with `xed` +
   `P["purge"]` with `release`) — an in-game picture, purged.
2. Pictures kept only by an older keep of the same row or an alias (`_older_own` / same-row keep, the
   ENACT_KEEP_AGE_FIX logic): that keep is not counted as protection, so the ✕ purges a picture he once kept.

Also a design question: archiving a live single-texture slot with no replacement pick leaves the texPath with no
file (missing texture in game).

Fix shape: route both branches through `P["archive"]` (bytes kept, `art.py restore`), keeping the newest-mark-wins
check; decide the empty-slot case (hold the ✕ as a conflict until a pick exists, or archive and retire the def's
texture). Interacts with ENACT_KEEP_AGE_FIX and the 2026-10-10 "Put them on the sheet" card — read both first.
Evidence: /mnt/d/ClaudeWork/rimmandrake/review_delegation_builds/ (PROGRESS.md, d_enact.diff).
