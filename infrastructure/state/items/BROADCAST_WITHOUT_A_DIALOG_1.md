# BROADCAST_WITHOUT_A_DIALOG_1 — the owner's announcements should not need three clicks

## spec

🔴 **OWNER, 2026-08-21:** *"When the user uses that command, it should NOT force each of
the other windows to click through 'accept' or 'reject.' That defeats the point of the
broadcast. But only the user should be able to do that, not agents."*

**The cause is settled and is NOT the setting.** Full write-up is in
`src/RimMandrake/Utils/broadcast.py`'s docstring; the short form:

- `crossSessionInbound` accepts exactly `accept | hold | refuse` — read off the installed
  binary 2.1.238 as `N1i={accept:0,hold:1,refuse:2}`. **There is no stronger value**, and
  the repo has held `accept` since 2026-08-19.
- 🔑 **A permission-mode rule overrides it.** When the two sides are in different classes,
  the receiver holds regardless: a receiver that BYPASSES permissions holds every message
  unless the SENDER also identifies as bypassing. The agent windows run in bypass;
  `broadcast.py` is a plain socket writer and does not so identify. ⇒ held, by design.

**The fix:** make `broadcast.py` declare the sender-bypass class in its handshake or
frame, so it matches the windows it is talking to.

⛔ **THE ONE THING THAT MUST NOT BE GUESSED: the field name.** REP could not pin it from
`strings` on the binary and deliberately stopped rather than inventing one. It is **not**
in `~/.claude/sessions/<pid>.json` — those carry pid, sessionId, cwd, status, `peerProtocol`
and `peerFeatures`, and no permission mode. Read the CLI's own outbound peer send and take
the field from there, the same way `frame()` was originally derived.
⚠️ **A guessed field is worse than the dialog**: the send still succeeds, the message is
still held, and it looks fixed.

✅ **The owner-only property needs no work and must not be re-engineered.** Auto-delivery
does not open agent-to-agent messaging: agents are refused at the SENDING end by
`.claude/hooks/block_peer_messages.py`, and an agent running `broadcast.py` at all is
already the violation. ⛔ Do not try to make the RECEIVER distinguish the owner — it cannot
see sender identity, only the permission-mode class, and no hook fires on receipt.

⚠️ **Pin the version.** `frame()` was read off 2.1.237, the box now runs 2.1.238, and this
is undocumented internals. Whatever is added goes in `frame()` beside it, with the version
it was read from, so the next upgrade has one place to re-check.

## verify

- The field is quoted with where it was read from — a CLI code path, not a doc, not a
  guess.
- `broadcast.py --to <one seat> "test"` delivers into a bypass-mode window with **no
  accept/reject dialog**, witnessed by the owner.
- `SendMessage` from an agent to a seat is still refused by the hook. Re-run
  `.claude/hooks/selftest_queue_lint.py` and the peer-block selftest if one exists.
- `crossSessionInbound` is still `accept` and was not changed to chase this.

## criteria

The owner types one command and every window has the announcement, with nothing to click —
and an agent still cannot reach a peer by any route.
