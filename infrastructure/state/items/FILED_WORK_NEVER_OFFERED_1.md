## spec
🔴 **The DECIDE→BUILD handoff does not work, and nothing reports it.** Measured 2026-08-21
against the rendered queue.

`priority.py`'s docstring is explicit — `rimflow next --seat <ME>` applies
`filter state == ready`. **`proposed` items are never offered.**

`POLICY.md:185` tells every seat their turn is *"three commands, in this order, and no
others"*, ending in `next --seat <ME>`. ⛔ **There is no fourth command telling a seat to
read its queue file and `claim`.**

⇒ **An item filed FOR another seat lands in `proposed` and is never surfaced by the only
command that seat is instructed to run.**

**Measured on BUILD's board, 2026-08-21:**

| state | items |
|---|---|
| `ready` — actually offerable | **3** |
| `doing` | 3 |
| 🔴 `proposed` — filed, complete, and invisible | **15 of 21** |

Seven of those fifteen were filed by DECIDE in a single night: `IMPERIAL_RAID_ROSTER_1`,
`IMPERIAL_VOCABULARY_KEYED_1`, `PIRATE_VESSEL_RESTORED_1`, `CAST_XML_REGENERATE_1`,
`CAST_PARSER_KIT_FIELDS_1`, `FACTION_FIXEDNAME_ELEVEN_1`, `RAIN_DRY_THE_LOWLANDS_1` — plus
`FACTION_ICONS_BESPOKE_1`, which the owner asked for by name and which ranks **21st of 21**.

⚠️ **This is not the same defect as `NEEDS_HAS_NO_SETTER_1`**, though they compound: that one
makes `needs` wrong, this one makes the item unreachable whatever `needs` says.

🔑 **Two candidate fixes, and the second is probably right:**
1. **Offer `proposed` items to their owner**, marked as unclaimed, so `next` says *"this was
   filed for you — claim it"*. Keeps the claim step, removes the invisibility.
2. **Add the claim step to `POLICY.md`'s start-of-turn contract** as a fourth command. ⚠️
   Weaker: it relies on every seat reading a doc, and the docstring says the whole point of
   `next` is that the answer does not depend on who is reading what.

⛔ **Do not "fix" it by having the filing seat mark the item `ready`.** `claim` reaching
`ready` only when the prose is complete is a real check and it belongs to the owning seat.

## verify
`rimflow next --seat BUILD` offers, or explicitly names, an item that was filed for BUILD by
another seat and has never been claimed. Today it does not.

## criteria
No item can be complete, filed, unblocked and still absent from the only command its owner
is told to run.

---

## ✅ FIXED by REP, 2026-08-21

**Re-measured before fixing, and it had grown:** BUILD held **21** proposed, **18 of them
spec-complete**, against 3 offered. Fleet-wide **28 finished specs were unreachable** —
BUILD 18, CHECK 7, DECIDE 2, REP 1.

**The fix, in `cli.py`:** `next` now falls through to `_claimable()` before saying
"nothing". If the seat owns `proposed` items that are unblocked, on-target and
spec-complete, it prints the top one and the exact verb — `rimflow claim <ID>` — instead
of an empty answer.

⚠️ **`priority.rank()` is deliberately UNCHANGED.** `ready` still means claimed, the claim
stays an explicit act of taking the work, and the rendered NEXT section still shows only
claimed items. The defect was never that `rank()` was wrong; it was that an empty answer
lied about there being nothing to do.

⭐ **And the other half, which the item did not ask for but is the same wound:** when there
is genuinely nothing claimable, `_nothing()` now lists proposals that CANNOT be claimed
because their `items/<ID>.md` is missing sections, naming the sections. Previously those
sat in a generic bucket reading `state is proposed`, which told nobody that the filer
still owed prose.

Two selftests, asserting both directions: a spec-complete handoff is offered with its
claim verb, and a prose-less proposal is still refused and names what it lacks.
`selftest_cli.py` 24/24; model 37/37, render 16/16, importer 21/21 unchanged.

🔑 **What this does NOT fix, and somebody should:** `POLICY.md` still tells every seat its
turn is *"three commands, in this order, and no others"*, and `claim` is not among them.
The tool now surfaces the work, but the doctrine still has no step for taking it.
