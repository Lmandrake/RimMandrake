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

# The seats that may HOLD the bridge — since redesign #4 (2026-08-27) either live
# window; CHECK stays for ledger history. One-driver-at-a-time is cmd_bridge's holder
# guard. Listed here because offering a bridge item to a seat that cannot take the
# lock is offering work it cannot start.
BRIDGE_SEATS = ("BENCH", "FOUNDRY", "CHECK")

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
                                and ctx.get("seat") in (None,) + BRIDGE_SEATS
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


def state_reason(it):
    """Why this item's `state` keeps it out of `rank()`, or None if it is `ready`.

    Split out of `why_not` so the one sentence a stuck seat reads can be exercised
    without building a world around it.
    """
    if it.state == "ready":
        return None
    if it.state == "proposed":
        # 🔴 NOT A GATE, AND THIS LINE USED TO SAY IT WAS. Until 2026-09-03 it read
        # "items/<ID>.md is missing ## spec …, so it cannot enter `ready`", which is
        # the completeness gate the owner ordered removed on 2026-08-21 — *"make
        # everyone able to work on anything in their queue independent of the V&V plan
        # attached right away"*. `model._apply_item_verb`'s `claim` has not enforced it
        # since, and selftest_model pins its absence in two places; only this sentence
        # survived, in the ONE command a stuck seat runs to find out what to do. A
        # removed gate that still answers the "why can't I work this" question has not
        # been removed. Missing sections are reported as INFORMATION, never a reason.
        miss = model._missing(it)
        thin = ("  Thin: no %s — worth writing, never a precondition."
                % ", ".join("## " + m for m in miss)) if miss else ""
        return ("state is `proposed` — nobody has claimed it yet. `rimflow claim %s` "
                "makes it yours and offerable.%s" % (it.id, thin))
    if it.state == "done":
        return ("closed at %s. It will never be offered again — that is the "
                "point of an append-only record." % (it.closed_sha or "?"))
    return "state is `%s`." % it.state


def needs_reason(it, world, seat, ctx=None):
    """Why this item's `needs` window is shut, in words that say whether to WAIT.

    🔑 Never say "will reopen" about a window that only reopens if a HUMAN acts. A
    bridge held by another seat, or free and untaken, is a thing to DO, not a thing to
    wait for, and saying otherwise is what stranded this item for days.
    """
    holder = (ctx or {}).get("bridge_holder", world.bridge_holder)
    if it.needs == "bridge" and seat not in BRIDGE_SEATS:
        return ("needs `bridge`, and %s cannot hold the lock — one driver at a "
                "time (CHARTER.md). Hand it to a live window: "
                "`rimflow reassign %s --to FOUNDRY`." % (seat, it.id))
    if it.needs == "bridge" and world.game in LIVE and holder and holder != seat:
        return ("needs `bridge`, and %s is holding it. This is NOT blocked and it "
                "will NOT reopen on its own — it reopens when %s runs "
                "`rimflow bridge release`." % (holder, holder))
    # 🔴 `harvest` AND `owner` ARE NOT FUNCTIONS OF GAME STATE, and the stock sentence
    # below told every seat that they were: "needs `harvest`, and the game is UP …
    # the window is simply closed and will reopen" is false twice over — the game
    # state is not the reason, and nothing reopens either window on its own. That is
    # the same defect the bridge branch above was written to cure (a wrong reason
    # strands the item and the seat believes waiting is the right move), left in place
    # for the two `needs` values whose gate `BY_GAME` reads out of `ctx`, not `g`.
    if it.needs == "harvest":
        return ("needs `harvest`, and no harvest is pending. ⚠️ NOT blocked, and NOT "
                "about the game: it opens when a log is actually mined, which is a "
                "thing to DO. If it never needed one, `rimflow needs %s --to offline`."
                % it.id)
    if it.needs == "owner":
        return ("needs `owner`, and the mode is afk — he is not at the keyboard. "
                "⚠️ NOT blocked, and NOT about the game: it reopens when he is back, "
                "not when the game moves. Take offline work and leave this filed.")
    # ⚠️ Deliberately NOT special-cased: `needs: bridge` while the game is DOWN.
    # There the stock wording is TRUE — the window really does reopen on its own,
    # when the game next comes up. Only a LIVE game with the lock unavailable is
    # the case that never reopens by itself. Rewriting the game-DOWN message too
    # was an over-reach and selftest_cli caught it.
    return ("needs `%s`, and the game is %s. ⚠️ This is NOT blocked — nothing "
            "is wrong, the window is simply closed and will reopen."
            % (it.needs, world.game))


def why_not(world, seat, iid, target="v1", ctx=None):
    """Why is this item not being offered? One reason per line, in filter order.

    ⭐ This is the command that stops the guessing. "It is not in my queue" was
    unanswerable before, because the queue was prose; here every filter can say
    exactly why it rejected an item, and the answer is the same for everyone.

    ⚠️ The filters below are `rank()`'s, in `rank()`'s order. If one of them stops
    matching, `why` starts explaining a decision `next` did not make.
    """
    it = world.items.get(iid)
    if it is None:
        return ["%s has never been filed." % iid]
    out = []
    if it.owner != seat:
        out.append("owned by %s, not %s. Filing work for another seat is normal; "
                   "working it is not." % (it.owner, seat))
    state = state_reason(it)
    if state:
        out.append(state)
    if it.blocked:
        out.append("BLOCKED: %s%s" % (it.blocked_reason,
                                      (" (on %s)" % it.blocked_on) if it.blocked_on else ""))
    if target and it.target not in (None, target):
        out.append("targeted at %s, and the active version is %s. That is a planning "
                   "decision, not a defect." % (it.target, target))
    if not satisfiable(it, world, ctx, seat):
        out.append(needs_reason(it, world, seat, ctx))
    return out or ["It IS being offered. Check `rimflow next --seat %s`." % seat]
