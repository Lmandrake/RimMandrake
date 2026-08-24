## spec
`src/RimMandrake/rimflow/priority.py` line 52:

    "bridge": lambda g, ctx: g in LIVE and ctx.get("bridge_holder") == "CHECK",

A `needs: bridge` item is offered **only while CHECK is actively holding the bridge
lock**. The seat that OWNS the item is never consulted. With the bridge free — the
normal state — every `needs: bridge` item on the board is invisible to everyone,
including CHECK.

Found 2026-08-24 with the game UP and the bridge free: DECIDE's only open item
(`AUTHORED_KINDS_MUST_FIELD_1`, now BUILD's) was withheld, and `rimflow why` said
*"the window is simply closed and will reopen"* — it does not reopen on its own.
That is the exact failure the file's own comment at lines 63-70 calls the worst thing
it can produce: the work exists, someone is waiting on it, and no command mentions it.

## verify
With `world.game == "UP"` and `bridge_holder` unset, `rimflow next --seat CHECK` must
offer a `needs: bridge` item. A seat that is not holding the bridge should be told to
take it, not told nothing exists.

## criteria
No `needs: bridge` item is unofferable to its own owner purely because the lock is free.
`why` must never say "will reopen" about a window that only reopens if someone acts.

## watch out
⚠️ The gate is also the bridge's mutual exclusion — POLICY.md line 101 makes the bridge
CHECK's instrument and says other seats borrow it by filing for CHECK. Do not fix this
by letting four seats drive the bridge at once. The likely shape is: offerable when the
lock is free OR held by this seat, and the offer carries `rimflow bridge take`.
⚠️ `satisfiable()` does not currently receive the seat; `rank()` does. Threading it
through is part of the change.
