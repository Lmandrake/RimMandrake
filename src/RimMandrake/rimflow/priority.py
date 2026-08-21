#!/usr/bin/env python3
"""rimflow/priority.py — "what should I do next", answered deterministically.

WHY DETERMINISTIC MATTERS MORE THAN CLEVER
==========================================
Four seats and a human all ask this question, and they must get the same answer for
the same ledger. A ranking that depends on who asked, or on when, produces two seats
each confident they are working the top item — which is what the six markdown queues
did, because "top" meant "whatever is highest in MY file".

So: pure function of (ledger, seat, game state). No randomness, no recency bias, no
model in the loop. Same inputs, same item, every time.

    rimflow next --seat BUILD

      filter  owner   == BUILD
      filter  state   == ready
      filter  blocked == false
      filter  target  == the active version, normally v1
      filter  needs   is satisfiable in the CURRENT GAME STATE
      sort    1. this_deployment  desc     ← the live window is closing
              2. v1 row           asc      ← the campaign's own order
              3. created_at       asc      ← oldest first, so nothing starves

🔑 THE `needs` FILTER IS THE WHOLE POINT, AND IT IS NOT `blocked`.
An item whose `needs` cannot be met is **not offered** — but it is **not blocked**
either. `blocked` means something is WRONG and someone must act. `needs` means the
WINDOW IS CLOSED and will open on its own. Writing both into one prose field is why
the old board could report neither, and why "waiting for the game" looked identical
to "broken" for months.
"""
from . import model

# Which `needs` are satisfiable in which game state. ⚠️ `harvest` and `owner` are NOT
# functions of game state alone — they are passed in, because the ledger cannot know
# whether the owner is at the keyboard or whether a log has already been mined.
BY_GAME = {
    "offline":  lambda g, ctx: True,
    "deploy":   lambda g, ctx: g == "DEPLOYING",
    "game-up":  lambda g, ctx: g == "UP",
    "bridge":   lambda g, ctx: g == "UP" and ctx.get("bridge_holder") == "CHECK",
    "harvest":  lambda g, ctx: bool(ctx.get("harvest_pending")),
    "owner":    lambda g, ctx: ctx.get("mode") != "afk",
}


def satisfiable(item, world, ctx=None):
    ctx = dict(ctx or {})
    ctx.setdefault("bridge_holder", world.bridge_holder)
    fn = BY_GAME.get(item.needs)
    if fn is None:
        return False                    # an unknown `needs` is never offered
    return fn(world.game, ctx)


def _row_key(item):
    """V1 row, ascending, with unrowed items LAST rather than first.

    ⚠️ Sorting `None` first would put every unplanned item ahead of the campaign's own
    order, which inverts the intent: a row number means someone decided where this
    sits, and an item with no row has not been placed yet.
    """
    try:
        return (0, int(str(item.row)))
    except (TypeError, ValueError):
        return (1, 0)


def rank(world, seat, target="v1", ctx=None):
    """-> [Item], best first. Pure. Empty is a legitimate and common answer."""
    out = []
    for it in world.items.values():
        if it.owner != seat:
            continue
        if it.state != "ready":
            continue
        if it.blocked:
            continue
        if target and it.target not in (None, target):
            continue
        if not satisfiable(it, world, ctx):
            continue
        out.append(it)
    out.sort(key=lambda i: (not i.this_deployment, _row_key(i),
                            i.created_at or "", i.id))
    return out


def next_item(world, seat, target="v1", ctx=None):
    r = rank(world, seat, target, ctx)
    return r[0] if r else None


def why_not(world, seat, iid, target="v1", ctx=None):
    """Why is this item not being offered? One reason per line, in filter order.

    ⭐ This is the command that stops the guessing. "It is not in my queue" was
    unanswerable before, because the queue was prose; here every filter can say
    exactly why it rejected an item, and the answer is the same for everyone.
    """
    it = world.items.get(iid)
    if it is None:
        return ["%s has never been filed." % iid]
    out = []
    if it.owner != seat:
        out.append("owned by %s, not %s. Filing work for another seat is normal; "
                   "working it is not." % (it.owner, seat))
    if it.state != "ready":
        if it.state == "proposed":
            miss = model._missing(it)
            out.append("state is `proposed`: items/%s.md is missing %s, so it cannot "
                       "enter `ready`." % (iid, " and ".join("## " + m for m in miss))
                       if miss else "state is `proposed` and has not been claimed.")
        elif it.state == "done":
            out.append("closed at %s. It will never be offered again — that is the "
                       "point of an append-only record." % (it.closed_sha or "?"))
        else:
            out.append("state is `%s`." % it.state)
    if it.blocked:
        out.append("BLOCKED: %s%s" % (it.blocked_reason,
                                      (" (on %s)" % it.blocked_on) if it.blocked_on else ""))
    if target and it.target not in (None, target):
        out.append("targeted at %s, and the active version is %s. That is a planning "
                   "decision, not a defect." % (it.target, target))
    if not satisfiable(it, world, ctx):
        out.append("needs `%s`, and the game is %s. ⚠️ This is NOT blocked — nothing "
                   "is wrong, the window is simply closed and will reopen."
                   % (it.needs, world.game))
    return out or ["It IS being offered. Check `rimflow next --seat %s`." % seat]
