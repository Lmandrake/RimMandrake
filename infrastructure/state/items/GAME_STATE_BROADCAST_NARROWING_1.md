# GAME_STATE_BROADCAST_NARROWING_1 — RULED 2026-09-03: leave it as is

**Owner's ruling (question card, 2026-09-03): "Leave it as is."** The broadcast
keeps announcing every state to every other window, unchanged. The draft
narrowing below was NOT adopted; it stays as the record of what was considered.
Nothing to build, nothing to propagate — no doc instructs the narrowing.

# (superseded draft below — 🔴 needed one word from the owner)

Owner, 2026-09-02: *"Should we get rid of that broadcast message of game is up, etc.?
It doesn't seem to have a function anymore and can even distract."*

## spec

**He is right about the half he named, and the reason is measurable.** `rimflow next`
now takes its own reading and corrects the ledger without anyone announcing anything —
observed twice this session: `⚙️ game state corrected UP → DOWN (measured: tasklist.exe
lists no RimWorldWin64)`. For **UP** and **DOWN**, the announcement carries nothing the
board cannot get itself, so its only remaining effect on a window is the interruption.

**What the measurement cannot see, and the announcement can:**
- **LOADING.** The process exists for the whole ~25-minute cold load, so `tasklist` reads
  UP while the bridge is a zombie. This is the state that has actually cost sessions.
- **DEPLOYING / GOING-DOWN.** Intent, not observable state. A window must not write a
  companion DLL while the game runs, and the shutdown window is when DLLs deploy.

**And the distraction is narrower than it looks.** `./game` already skips the window it
is typed in (`AGENT BENCH skipped (this window)`). Every interruption therefore comes
from announcing in a *different* window than the one he is talking to — which is what
happened at 20:49 today.

## the draft ruling — his yes commits it

> **Keep the ledger stamp. Deliver the announcement only to a window that holds an open
> item whose `needs` is `game-up`, `bridge`, `harvest` or `deploy`.**

That is computable from the ledger at send time, it removes the interruption for a window
sitting with him or doing offline work, and it keeps the one function worth keeping:
waking a window that is genuinely blocked waiting for the game.

⚠️ The alternative he floated — removing delivery entirely — costs exactly that wake.
A blocked window would then idle until its next `rimflow next`, which may be a long time
if it is deep in a single long task. Cheap to accept, but it should be accepted knowingly
rather than as a side effect of killing the noise.

⛔ Not in scope: the cross-window channel itself. This is the game-state relay, which is
that channel's single deliberate carve-out (CLAUDE.md), and narrowing its recipients does
not reopen agent-to-agent messaging.

## verify
`./game up` run from a window with no game-blocked items reaches nobody; run while a
window holds a `needs: game-up` item, it reaches exactly that window; the ledger event is
identical in both cases.

## criteria
He is not interrupted by a state the board can measure for itself, and a window blocked
on the game still learns when the game arrives.
