"""rimdrive.verify -- L2: the rule that a mutation must prove itself.

THE RULE THIS MODULE EXISTS TO ENFORCE (unchanged from rimbench.core, which
this replaces -- see that module's own docstring for the incidents that
established it)

    `success: true` from RimBridge means the tool RAN, not that the game
    CHANGED.

Two things are NEW here relative to rimbench's `mutate()`, both owner-ruled
2026-09-12 (design/RimMandrake/bridge_library_design.md §1, §6.5):

1. **UNVERIFIED is no longer silent.** rimbench's `set_stuff` with no `at`
   returned a bare `True` when there was nothing to read back -- an
   unverifiable write dressed as a verified one. Here `verify()` may return
   the `UNVERIFIED` sentinel instead of True/False, and `mutate()` records it
   on `session.unverified` rather than treating it as success. A modcheck
   component containing one reports PASS(UNVERIFIED n), never a clean PASS.

2. **A reconnect never triggers a blind retry.** `Session.call()` raises
   `Reconnected` when a timeout poisons the socket (skill rimbridge §1); this
   module catches that, drops back to `verify()` on an INDEPENDENT channel,
   and treats a still-false post-condition as genuinely unknown
   (`Indeterminate`), not as license to re-issue a call whose idempotence was
   never declared. The one exception is a caller who explicitly marks the
   call `idempotent=True` -- then, and only then, `do()` runs a second time.
"""


class Unchanged(Exception):
    """A mutation reported success and the world did not change."""


class Indeterminate(Exception):
    """The socket died mid-mutation and reconnecting did not resolve it.

    Whether the original call landed is genuinely unknown. This is raised
    instead of guessing, because guessing here is exactly the silent-failure
    class this module exists to kill.
    """


class Reconnected(Exception):
    """Signal from `Session.call()`: the socket died mid-call and was reopened.

    The call's effect is unknown until a post-condition says otherwise. Lives
    here (L2) rather than in `session` (L1) because "what to do about it" is
    entirely this module's rule -- `session.py` only raises it, never
    interprets it.
    """


UNVERIFIED = object()
"""Sentinel a `verify()` callback returns when no independent read-back
channel exists for this write at all (rimbench's `set_stuff` with no `at` is
the canonical example). Distinguishable from both a truthy result and a plain
`False` no-op -- `mutate()` branches on identity (`is UNVERIFIED`), so a
verifier must return this object itself, never a value that merely looks
like it."""


def mutate(session, what, do, verify, idempotent=False):
    """Run `do()` on `session`, then require `verify()` truthy on an
    INDEPENDENT channel -- never the mutating call's own response.

    Returns whatever `verify()` returned (truthy, or the `UNVERIFIED`
    sentinel), or `None` for a recorded no-op under `strict=False`.

    Raises:
        Unchanged      -- `verify()` read false and `session.strict` is True.
        Indeterminate  -- the socket died mid-`do()`, reconnected, and
                          `verify()` still reads false (see module docstring).
    """
    reconnected = False
    try:
        do()
    except Reconnected:
        reconnected = True

    session.mutations += 1
    got = verify()

    if reconnected and got is not UNVERIFIED and not got:
        if idempotent:
            try:
                do()
            except Reconnected:
                pass
            got = verify()
        if got is not UNVERIFIED and not got:
            raise Indeterminate(
                "%s: the socket died mid-call and reconnected; the "
                "post-condition still reads false (idempotent=%s). The "
                "call's effect on the game is UNKNOWN -- check by hand "
                "before assuming either outcome." % (what, idempotent))

    if got is UNVERIFIED:
        session.unverified.append(what)
        session.log("UNVERIFIED: %s (no independent read-back channel)" % what)
        return UNVERIFIED

    if got:
        return got

    session.no_ops.append(what)
    if session.strict:
        raise Unchanged(
            "%s reported success but the world did not change. "
            "See skills/rimbridge/references/traps.md." % what)
    session.log("NO-OP: %s" % what)
    return None
