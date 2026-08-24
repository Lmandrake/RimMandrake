# Archived: the handoff files nobody read

> 🗑️ **DELETED 2026-08-24 on the owner's order — "delete the superseded".** Both files are
> gone from the tree; git holds them at `5a83dcfa` and earlier. This README survives as the
> record of WHY the handoff-as-a-file mechanism died: **the handoff is the `note` on the last
> `seat` event in the ledger**, and nothing ever read these.

`HANDOFF_CHECK.md` and `HANDOFF_REP.md` were moved here 2026-08-22, on the owner's ruling,
after a sweep found that **nothing in the repo read either one** — no hook, no tool, no
seat doc named them. `HANDOFF_CHECK.md` had been written an hour before it was archived.

🔑 **The channel that actually works is `/remember`.** Its store lives outside this repo
and is injected into a seat's context by the `SessionStart` hook, which is where the
handoff a waking seat actually sees comes from. These two files were a parallel channel
with a writer and no reader.

⛔ **Do not restore them.** If a handoff needs to survive a session, run `/remember`. If it
needs to reach a specific seat, it is an item: `rimflow file --for <SEAT>`.
