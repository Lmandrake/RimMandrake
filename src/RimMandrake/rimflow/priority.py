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
# ⚠️ `GOING_DOWN` COUNTS AS THE GAME BEING UP, and this is the whole point of having a
# separate state for it: the process is still running and the bridge still answers. It
# is the window CLOSING, not closed — CHECK drops postponable offline work and runs live
# items only. Treating it as down would silently stop offering live work at precisely
# the moment there is least time left to do it.
LIVE = ("UP", "GOING_DOWN")

# 🔴 The only seat that may HOLD the bridge — POLICY.md line 91, enforced in
# model.py's `bridge` verb. It lives here too because offering a bridge item to a seat
# that cannot take the lock is offering work it cannot start, which is the same
# stranding the gate fix exists to remove, just further along.
BRIDGE_SEAT = "CHECK"

# Unrecognised `needs` values seen this process, so `next` can report them instead of
# swallowing the items that carry them. See `satisfiable`.
UNKNOWN_NEEDS = set()

BY_GAME = {
    "offline":  lambda g, ctx: True,
    "deploy":   lambda g, ctx: g == "DEPLOYING",
    "game-up":  lambda g, ctx: g in LIVE,
    # 🔴 Corrected 2026-08-26 (BRIDGE_GATE_HARDCODES_CHECK_1). This used to read
    #     ctx.get("bridge_holder") == "CHECK"
    # which offered a `needs: bridge` item ONLY while CHECK was actively holding the
    # lock. With the bridge free — the normal state — every bridge item on the board was
    # invisible to every seat INCLUDING CHECK, and `why` told them the window "will
    # reopen", which it never does on its own. That is the silently-unofferable failure
    # this file's own comment below calls the worst thing it can produce.
    # ✅ Offerable when the game is live, the asking seat is one that MAY hold the
    # bridge, and the lock is free or already its own. The offer carries
    # `rimflow bridge take`.
    # ⚠️ The seat test is NOT redundant. Bridge items do get owned by other seats in
    # practice — the item that exposed this defect was one — and POLICY.md line 92 says
    # they borrow by filing for CHECK. Offering BUILD a bridge item it can never take
    # would trade a silent withholding for a visible dead end. `why_not` names the
    # reassignment instead.
    "bridge":   lambda g, ctx: (g in LIVE
                                and ctx.get("seat") in (None, BRIDGE_SEAT)
                                and ctx.get("bridge_holder") in (None, ctx.get("seat"))),
    "harvest":  lambda g, ctx: bool(ctx.get("harvest_pending")),
    "owner":    lambda g, ctx: ctx.get("mode") != "afk",
}


def satisfiable(item, world, ctx=None, seat=None):
    """⚠️ `seat` is optional so old two-arg callers keep working, but WITHOUT it a
    `needs: bridge` item is only satisfiable while the lock is free. Pass it from any
    caller that knows who is asking, or the queue file and `next` will disagree."""
    ctx = dict(ctx or {})
    ctx.setdefault("bridge_holder", world.bridge_holder)
    if seat is not None:
        ctx.setdefault("seat", seat)
    fn = BY_GAME.get(item.needs)
    if fn is None:
        # 🔴 FAIL OPEN, and say so — corrected 2026-08-22. This used to `return False`
        # with the comment "an unknown `needs` is never offered", which made a typo or a
        # new NEEDS value hide an item from every seat, for ever, with nothing reporting
        # it. ⛔ Silently unofferable is the worst failure this file can produce: the
        # work exists, someone is waiting on it, and no command will ever mention it.
        # ✅ Offering an item whose window may be shut costs one seat one look.
        UNKNOWN_NEEDS.add(item.needs)
        return True
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
        if not satisfiable(it, world, ctx, seat):
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
    if not satisfiable(it, world, ctx, seat):
        # 🔑 Never say "will reopen" about a window that only reopens if a HUMAN acts.
        # A bridge held by another seat, or free and untaken, is a thing to DO, not a
        # thing to wait for, and saying otherwise is what stranded this item for days.
        holder = (ctx or {}).get("bridge_holder", world.bridge_holder)
        if it.needs == "bridge" and seat != BRIDGE_SEAT:
            out.append("needs `bridge`, and the bridge is %s's — POLICY.md line 91, "
                       "one driver at a time. %s can never take the lock, so this item "
                       "cannot be worked here however the game is doing. Hand it over: "
                       "`rimflow reassign %s --to %s`."
                       % (BRIDGE_SEAT, seat, iid, BRIDGE_SEAT))
        elif it.needs == "bridge" and world.game in LIVE and holder and holder != seat:
            out.append("needs `bridge`, and %s is holding it. This is NOT blocked and it "
                       "will NOT reopen on its own — it reopens when %s runs "
                       "`rimflow bridge release`." % (holder, holder))
        # ⚠️ Deliberately NOT special-cased: `needs: bridge` while the game is DOWN.
        # There the stock wording is TRUE — the window really does reopen on its own,
        # when the game next comes up. Only a LIVE game with the lock unavailable is
        # the case that never reopens by itself. Rewriting the game-DOWN message too
        # was an over-reach and selftest_cli caught it.
        else:
            out.append("needs `%s`, and the game is %s. ⚠️ This is NOT blocked — nothing "
                       "is wrong, the window is simply closed and will reopen."
                       % (it.needs, world.game))
    return out or ["It IS being offered. Check `rimflow next --seat %s`." % seat]
