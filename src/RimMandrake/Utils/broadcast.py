#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""broadcast.py — the OWNER speaks to every agent window at once.

    ./src/RimMandrake/Utils/broadcast.py "Game is up"
    ./src/RimMandrake/Utils/broadcast.py --all "WRAP is initiated"
    ./src/RimMandrake/Utils/broadcast.py --to CHECK,BUILD "Game is loading"
    ./src/RimMandrake/Utils/broadcast.py --list

⭐ SAYING IT IS RECORDING IT. A message that announces game state also appends the
OWNER's `game` event, so there is no second command to forget:

    "Game is up"          -> UP          "Game is loading"   -> LOADING
    "Game is down"        -> DOWN        "WRAP is initiated" -> GOING_DOWN
    "at the main menu"    -> UP          "deploying"         -> DEPLOYING

It prints what it recorded. Prose that merely mentions the game records nothing.

🔴 THIS IS A USER TOOL. AGENTS DO NOT RUN IT — with ONE carve-out, added 2026-08-22.
⭐ THE CARVE-OUT: when the owner SAYS "game up" / "game down" / "game loading" to an
agent, that agent runs `./game <state> --said "<his words>"` immediately, which lands
here. He ruled it identical to him typing it himself: *"make it so that when I say game
up, game down, game loading it is IDENTICAL to that !./game command."* It is a relay of
his sentence, in the moment, and nothing else — ⛔ a state an agent INFERRED, and any
message that is not a game state, remain his alone.
Owner's ruling, 2026-08-19: agents do not message each other, at all. `SendMessage`
and `ListAgents` are DENIED to them in `.claude/settings.json`, so an agent has no
way to reach a peer through the supported channel. This script deliberately goes
around that — it writes the peer socket directly, which permission rules do not
gate — and that is exactly why **only the owner may run it.** An agent that runs
this to talk to another agent is breaking the ruling by the back door.

WHAT IT IS FOR, and nothing else: announcing a change of GAME STATE that every
seat must know at the same moment — *game is up* · *game is loading* · *WRAP is
initiated*. Not findings, not specs, not handoffs. Those are queue items.

HOW IT WORKS
------------
Every live Claude Code session publishes itself under ~/.claude/sessions/ :

    <pid>.json                 name, cwd, kind, status, messagingSocketPath
    <pid>.<sha256>.key         {"peerToken": "<hex32>", ...}

We read both, then speak the session inbox protocol over the unix socket:

    {"type":"auth","token":"<peerToken>"}\\n
    {"msgV":1,"msg_id":"<uuid>","type":"user","priority":"next",
     "message":{"role":"user","content":
       "<cross-session-message from-name=\\"OWNER\\" from-mode=\\"bypass\\">\\nTEXT\\n</cross-session-message>"}}\\n

⚠️ The frame is READ OFF THE INSTALLED CLI (2.1.238), not documented. If a Claude
Code upgrade changes it, this script starts failing and the fix is to re-read it.
It is pinned in one place — `frame()` below — for exactly that reason.
🔴 `from-mode="bypass"` and those two newlines are LOAD-BEARING, not decoration.
Without them every window holds the message behind an accept/reject dialog. Why,
exactly, is the next section.

🔴 WHY EVERY WINDOW ASKED "accept / reject" — SETTLED 2026-08-21, and fixed below
--------------------------------------------------------------------------------
Read out of the installed CLI binary, `~/.local/share/claude/versions/2.1.238`.
Function names are minified and will change on upgrade; the byte offsets are for
2.1.238 only. Re-read them, do not trust them, after any upgrade.

🔑 THE FIELD IS NOT A FRAME FIELD. It is an ATTRIBUTE ON THE MESSAGE TAG.
`hkb()` at ~303,726,700 builds the tag, and the last attribute it appends is:

    if (o) i.push(`from-mode="${o}"`)           // o = the sender's mode
    hId = ["bypass", "prompting"]                // the only two legal values

The receiver's gate, `Enm()` at ~313,486,900, decides it:

    let o = oXr(n)                       // OUR mode: "bypass" | "prompting"
    let i = (t || nXr()) ? e?.fromMode : undefined
    if (i !== undefined)
        return i === o ? {policy:"accept"} : {policy:"hold", holdCause:"mode-mismatch"}
    return o === "bypass" ? {policy:"hold",   holdCause:"no-mode-asserted"}
                          : {policy:"accept", holdCause:"bypass-default"}

⇒ The agent windows run bypass, this script asserted no mode, so every message
landed on `no-mode-asserted` and was held. Asserting `from-mode="bypass"` takes
the `i === o` branch and is delivered with nothing to click.

⚠️ THREE THINGS THAT MUST BE EXACTLY RIGHT, or the tag is not a peer message at all.
`EId()` parses it with one anchored regex and then RE-SERIALISES the captured
groups and compares to the original — `if (v1r(...) !== n) return;` — so anything
it cannot reproduce byte-for-byte is silently not parsed, `origin.fromMode` comes
back undefined, and you are back to the dialog while believing you fixed it.

  1. ATTRIBUTE ORDER IS FIXED: from, from-session, hop-chain, from-name, from-mode.
  2. THE BODY IS NEWLINE-DELIMITED: `<tag ...>\n BODY \n</tag>`. This script had
     no newlines before today, so its tag never parsed even as a from-name.
  3. THE BODY IS NOT HTML-ESCAPED. The CLI escapes nothing; it only scrubs a
     nested copy of the tag (`h1r`). We used to send `&amp;` and `&lt;`, which
     reached the owner's seats as literal entities.

🔴 AND IT IS BEHIND A FEATURE GATE: `nXr()` is `it("tengu_harbor_kite_mode_emit",
false)`. If that gate is OFF the receiver ignores `from-mode` entirely and holds
regardless. It reads **true** on this machine (`~/.claude.json`,
`cachedGrowthBookFeatures.tengu_harbor_kite_mode_emit`). If broadcasts start
being held again after an upgrade, check that gate before touching anything here.

⚠️ AND `crossSessionInbound: "accept"` IN THIS REPO IS A NO-OP — do not read the
repo setting as the thing making delivery work. `bnm()` takes policySettings /
flagSettings / userSettings as given, but local/project settings only RATCHET
STRICTER: `if (N1i[n] > N1i[e ?? "accept"]) e = n`, with N1i={accept:0,hold:1,
refuse:2}. A project-scoped `accept` never exceeds the default and is discarded,
so `njt()` returns undefined and the permission-mode rule above decides it. The
repo setting still matters — it is what keeps anyone setting `hold` or `refuse`
there — but it cannot grant delivery. Nothing about it was changed for this fix.

⛔ WHAT WILL NOT FIX IT, all checked so they are not tried again:
  * a stronger `crossSessionInbound` — the enum is {accept,hold,refuse} and there
    is no fourth value; at repo scope `accept` does not even apply
  * a hook on receipt — no hook event fires on receiving a peer message
  * gating on `from-name="OWNER"` — the receiver never sees sender identity, only
    the sender's permission-mode class
  * the `selfSent` route — `pFl()` grants it for a presented CHILD token, and
    `~/.claude/sessions/<pid>.<sha>.key` publishes only `peerToken`/`procStart`

✅ AND THE SAFETY PROPERTY SURVIVES THE FIX, which is why the fix is worth making.
Auto-delivery does NOT open agent-to-agent messaging: agents are blocked at the
SENDING end by `.claude/hooks/block_peer_messages.py`, and an agent running THIS
script is already the violation. Nothing about inbound needs to distinguish the
owner, because nothing else can legitimately reach the socket.

🔑 By DEFAULT this only reaches windows whose cwd is this repo, so the owner's
other projects never get fleet traffic. `--all` overrides that.
"""
import json
import os
import re
import socket
import sys
import uuid

SESSIONS = os.path.expanduser("~/.claude/sessions")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))   # Utils -> RimMandrake -> src -> repo
KEY_RE = re.compile(r"^(\d+)\.[0-9a-f]{64}\.key$")


def sessions():
    """Every live session: the .json record, joined to its peerToken."""
    tokens = {}
    try:
        names = os.listdir(SESSIONS)
    except OSError:
        return []
    for fn in names:
        m = KEY_RE.match(fn)
        if not m:
            continue
        try:
            with open(os.path.join(SESSIONS, fn), encoding="utf-8") as fh:
                tokens[int(m.group(1))] = json.load(fh).get("peerToken")
        except Exception:
            pass
    out = []
    for fn in names:
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(SESSIONS, fn), encoding="utf-8") as fh:
                rec = json.load(fh)
        except Exception:
            continue
        sock = rec.get("messagingSocketPath")
        # 🔑 The socket file EXISTING is the liveness test. A record whose process
        # has gone leaves the .json behind; the socket goes with the process.
        if not sock or not os.path.exists(sock):
            continue
        rec["peerToken"] = tokens.get(rec.get("pid"))
        out.append(rec)
    return sorted(out, key=lambda r: r.get("name") or "")


def in_repo(rec):
    """Is this window sitting in THIS repo? ⚠️ `os.path.realpath("")` returns the
    CALLER's cwd, so `realpath(rec.get("cwd") or "")` read a record with no cwd as
    in-repo whenever broadcast is run from the repo — which is always, via `./game`.
    A window we cannot place is not here."""
    cwd = rec.get("cwd")
    return bool(cwd) and os.path.realpath(cwd) == os.path.realpath(REPO)


TAG = "cross-session-message"

# 🔴 READ OFF THE INSTALLED CLI, ~/.local/share/claude/versions/2.1.238 — undocumented
# internals, pinned here so an upgrade has ONE place to re-check. See the module
# docstring for the exact functions and offsets.
FRAME_READ_FROM_CLI_VERSION = "2.1.238"

# The two legal values of the tag's `from-mode` attribute (`hId` in the binary).
# "bypass" is what the agent windows run as, and matching it is the whole fix.
SENDER_MODES = ("bypass", "prompting")
SENDER_MODE = "bypass"


def tag_body(text):
    """The CLI does NOT escape the body (`v1r` passes it through). It only scrubs a
    nested copy of the tag so a message cannot forge its own envelope — `h1r`
    rewrites the opening `<` to `<\\`. Approximated here for the two literal
    forms; anything more exotic than that is not something the owner types."""
    return (text.replace("<" + TAG, "<\\" + TAG)
                .replace("</" + TAG, "<\\/" + TAG))


def frame(text, sender="OWNER", mode=SENDER_MODE):
    """⚠️ The wire format, pinned in one place. See the module docstring.

    ⛔ THE THREE THINGS THE PARSER WILL NOT FORGIVE, because it re-serialises what
    it matched and compares byte-for-byte before believing any of it:
      * attribute order — from, from-session, hop-chain, from-name, FROM-MODE last
      * `>\n` before the body and `\n<` after it
      * `from-name` carrying a quote or an angle bracket (the CLI strips them, so
        a tag that keeps them cannot round-trip)
    Break any one and the message is not recognised as a peer message at all: it
    still arrives, it still waits behind accept/reject, and it looks fixed.
    """
    name = "".join(c for c in sender if c not in '"<>\r\n').strip() or "OWNER"
    attrs = ' from-name="%s"' % name
    if mode:
        if mode not in SENDER_MODES:
            raise ValueError("from-mode must be one of %r" % (SENDER_MODES,))
        attrs += ' from-mode="%s"' % mode
    content = "<%s%s>\n%s\n</%s>" % (TAG, attrs, tag_body(text), TAG)
    return json.dumps({
        "msgV": 1,
        "msg_id": str(uuid.uuid4()),
        "type": "user",
        "priority": "next",
        "message": {"role": "user", "content": content},
    })


def send(rec, text, sender="OWNER"):
    if not rec.get("peerToken"):
        return "no peer token"
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(rec["messagingSocketPath"])
        s.sendall((json.dumps({"type": "auth", "token": rec["peerToken"]}) + "\n").encode())
        s.sendall((frame(text, sender) + "\n").encode())
        s.close()
        return None
    except Exception as e:                       # noqa: BLE001 - report, never raise
        return "%s: %s" % (type(e).__name__, e)


# ---------------------------------------------------------------------------
# GAME STATE — the owner says it, this records it
# ---------------------------------------------------------------------------
# 🔴 OWNER, 2026-08-21: "change the python implementation of the user declaring the
# game up or down to a simple broadcast message, not a python script."
#
# Before this, announcing a load was TWO acts: a broadcast so the seats heard it, and
# `rimflow game UP --seat OWNER` so the board believed it. The second was forgotten
# every time — the board sat at DOWN through an entire session on 2026-08-21 while the
# game was up, so every item gated on `needs: game-up` stayed unoffered.
#
# 🔑 Now the sentence IS the command. The owner types what he was going to type anyway
# and the ledger event is a side effect of being understood.
#
# ⚠️ DELIBERATELY CONSERVATIVE. It matches whole phrases, not the bare word "game", and
# it prints what it recorded so a wrong guess is visible in the same breath. Prose that
# merely mentions the game records nothing — silence is the safe failure here, because a
# WRONG game state is worse than none: `satisfiable()` gates bridge work on it.
GAME_PHRASES = [
    # order matters — the first match wins, so the specific ones come first
    ("GOING_DOWN", ("going down", "wrap is initiated", "wrap initiated",
                    "about to close", "closing the game", "shutting down")),
    ("LOADING",    ("is loading", "game loading", "loading now", "loading the game")),
    ("DEPLOYING",  ("deploying", "deploy window", "is deploying")),
    ("UP",         ("game is up", "game up", "at the main menu", "main menu",
                    "game's up", "we are up", "it is up", "it's up")),
    ("DOWN",       ("game is down", "game down", "game's down", "is closed",
                    "has closed", "went down", "is unstable", "brought it down")),
]


def game_state_in(text):
    """-> the state this sentence announces, or None.

    🔴 THE EARLIEST PHRASE IN THE SENTENCE WINS, not the earliest in the table —
    fixed 2026-09-03. `./game <state> ["note"]` appends the owner's free-text note
    after an em dash, so the note sits *downstream* of the word that names the state;
    a table-order scan let it overrule the command. `./game down "after deploying the
    mods"` stamped DEPLOYING and `./game up "closing the game window later"` stamped
    GOING_DOWN — the state the owner explicitly typed, silently replaced by a word in
    his aside, on the one variable `satisfiable()` gates bridge work on. Table order
    still breaks a tie at the same position, which is what keeps the specific phrases
    ahead of the general ones.
    """
    low = " %s " % " ".join(text.lower().split())
    best, at = None, len(low)
    for state, phrases in GAME_PHRASES:
        for p in phrases:
            i = low.find(p)
            if i != -1 and i < at:
                best, at = state, i
    return best


def record_game(state, text):
    """Append the OWNER's `game` event. Never fatal — the message still goes out."""
    import subprocess
    cli = os.path.join(REPO, "src/RimMandrake/rimflow/cli.py")
    if not os.path.exists(cli):
        return "rimflow not found; state NOT recorded"
    # \U0001f534 CAPTURE WHO ACTUALLY RAN THIS before forcing OWNER — added 2026-08-25.
    # `RIMFLOW_SEAT="OWNER"` below is a CONSTANT, not identity, and `frame()` stamps
    # from-name="OWNER" on every message for the same reason: this tool was built on
    # the assumption only the owner would run it. On 2026-08-25 `./game up --help`
    # fired twice from some window and NOTHING in the message or the ledger could say
    # which — the owner asked "who keeps saying this?" and the honest answer was that
    # the system cannot know. It can now.
    # \u26a0 RIMFLOW_SEAT is almost never set in a seat's shell — it is only source #1
    # of four in rimflow's own resolve_seat(). Reading it alone would make this whole
    # field silently never fire, which is the defect class it exists to catch. So it
    # walks the same order rimflow does, minus --seat, which is not ours to see.
    ran_by = (os.environ.get("RIMFLOW_SEAT")
              or os.environ.get("AGENT_SEAT") or "").strip().upper()
    if not ran_by:
        sid = os.environ.get("CLAUDE_SESSION_ID")
        if sid:
            try:
                with open(os.path.join(REPO, ".claude", "session_roles", sid),
                          encoding="utf-8") as fh:
                    for w in fh.read().replace("-", " ").split():
                        if w.upper() in ("BENCH", "FOUNDRY", "DECIDE", "BUILD", "CHECK",
                                         "REP", "OWNER"):
                            ran_by = w.upper()
                            break
            except OSError:
                pass
    env = dict(os.environ, RIMFLOW_SEAT="OWNER")
    if ran_by and ran_by != "OWNER":
        env["RIMFLOW_RAN_BY"] = ran_by
    # \u2b50 Carry his verbatim words onto the event when an agent is relaying him
    # (./game --said "..."), so the ledger records WHO authorized the state and not
    # merely that it changed. Absent -> the event is OWNER's, unattributed, as before.
    said = (os.environ.get("RIMFLOW_OWNER_SAID") or "").strip()
    extra = ["--owner-said", said] if said else []
    try:
        p = subprocess.run([sys.executable, cli, "game", state] + extra,
                           capture_output=True, text=True, timeout=30,
                           cwd=REPO, env=env)
    except Exception as e:                       # noqa: BLE001 - never gate the send
        return "state NOT recorded: %s" % e
    if p.returncode:
        return "state NOT recorded: %s" % (p.stderr or p.stdout or "?").strip()[:160]
    return None


GAME_BLOCKED_NEEDS = ("game-up", "bridge", "harvest", "deploy")


def seats_waiting_on_the_game():
    """-> {SEAT} holding an open item that is actually blocked on the game, or None.

    🔑 WHY A GAME-STATE ANNOUNCEMENT IS NARROWED (owner, 2026-09-02: *"It doesn't seem
    to have a function anymore and can even distract."*). `rimflow next` MEASURES the
    game itself now — `tasklist.exe`, and it corrects the ledger on its own — so for
    UP and DOWN the announcement tells a window nothing it could not find out, and its
    only remaining effect on a window mid-task is the interruption.

    What survives is the one job measurement cannot do: WAKING a window that is sitting
    on work it cannot start. That is exactly the set computed here.

    ⚠️ `None` means "could not tell", and every caller must then deliver to EVERYONE.
    A broadcast that silently reaches nobody because the ledger would not load is far
    worse than one that is too loud — this mechanism exists so a blocked window learns
    the game arrived, and failing closed would defeat it.
    """
    try:
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))
        from rimflow import model
        w = model.replay(model.read(model.EVENTS))
    except Exception:                            # noqa: BLE001 - never gate the send
        return None
    return {it.owner for it in w.open_items()
            if it.owner and it.needs in GAME_BLOCKED_NEEDS}


def main(argv):
    args, only, everywhere, sender = [], None, False, "OWNER"
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--all":
            everywhere = True
        elif a == "--list":
            only = "\x00list"
        elif a in ("--to", "--from"):
            # ⛔ A FLAG MISSING ITS VALUE IS A MISTYPED COMMAND, NEVER A WORD OF THE
            # MESSAGE — fixed 2026-09-03. `--to`/`--from` used to be guarded by
            # `and i + 1 < len(argv)`, so a trailing `--to` fell through to `args` and
            # `broadcast.py "Game is up" --to` announced *"Game is up --to"* to EVERY
            # window instead of the one asked for: wrong text and wrong recipients, with
            # nothing said. Same class as the `./game up --help` broadcast of 2026-08-25.
            if i + 1 >= len(argv):
                print("%s takes a value, e.g. %s BENCH" % (a, a), file=sys.stderr)
                return 2
            i += 1
            if a == "--to":
                only = [x.strip().upper() for x in argv[i].split(",") if x.strip()]
                if not only:
                    print("--to names no window", file=sys.stderr)
                    return 2
            else:
                sender = argv[i]
        elif a.startswith("--"):
            # A mistyped flag (`--al`) otherwise becomes message text AND silently
            # changes who is reached. Refusing costs nothing; the owner types prose.
            print("unknown option %r.  --all | --list | --to <names> | --from <name>" % a,
                  file=sys.stderr)
            return 2
        else:
            args.append(a)
        i += 1

    live = sessions()
    if not everywhere:
        live = [r for r in live if in_repo(r)]

    if only == "\x00list":
        for r in sessions():
            here = "  " if in_repo(r) else " *"
            print("%s %-18s %-9s pid%-8s %s"
                  % (here, r.get("name"), r.get("status"), r.get("pid"), r.get("cwd")))
        print("\n  (* = outside this repo; needs --all)")
        return 0

    text = " ".join(args).strip()
    if not text:
        print(__doc__.split("HOW IT WORKS")[0].strip())
        return 2

    if isinstance(only, list):
        live = [r for r in live if any(k in (r.get("name") or "").upper() for k in only)]
    # 🔑 Record BEFORE delivering. A seat woken by this message will run
    # `rimflow next` within the second, and it must read the new state, not the old one.
    # 🔴 AND BEFORE THE NO-RECIPIENT EXIT — fixed 2026-09-03. This block sat *after*
    # `if not live: return 1`, so `./game up` with no agent window open in this repo
    # (or a `--to` naming a window that had since exited) announced nothing AND recorded
    # nothing, exiting 1 with only "no live sessions matched" to show for it. The stamp
    # is the half that does not depend on anyone listening, and losing it is exactly the
    # failure this mechanism exists to end: the board reading DOWN for a whole session
    # while RimWorld was running.
    state = game_state_in(text)
    stamp_failed = False
    if state:
        err = record_game(state, text)
        stamp_failed = err is not None
        print("  game -> %-12s %s" % (state, err or "recorded in the ledger"))

    if not live:
        print("no live sessions matched")
        return 1

    # ⭐ NARROWED, and only for a game-state sentence. An arbitrary message the owner
    # types still reaches every window — he is addressing them, and only he can know
    # who needs it. `--all` and `--to` are explicit and are never narrowed either.
    waiting = None
    if state and not everywhere and not isinstance(only, list):
        waiting = seats_waiting_on_the_game()

    me = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")
    tried = sent = 0
    for r in live:
        name = r.get("name") or ""
        if me and r.get("messagingSocketPath") == me:
            print("  %-18s skipped (this window)" % name)
            continue
        # A window's seat is the last word of its name — "AGENT BENCH" -> BENCH.
        seat = name.upper().split()[-1] if name.split() else ""
        if waiting is not None and seat not in waiting:
            print("  %-18s not told (nothing of theirs is waiting on the game)" % name)
            continue
        tried += 1
        err = send(r, text, sender)
        if err is None:
            sent += 1
        print("  %-18s %s" % (name, err or "delivered"))

    # 🔴 THE EXIT CODE MUST NOT SAY "DONE" WHEN THE HALF THAT MATTERS DID NOT HAPPEN —
    # fixed 2026-09-03. This returned 0 unconditionally, so `./game up` exited SUCCESS
    # when `record_game` had refused (a `--said` quote the guard rejects, rimflow
    # missing, a LedgerError) and equally when every single send raised. One line reading
    # "state NOT recorded" in a column of "delivered" is easy to skim and invisible to
    # anything checking a status — which is precisely how the board came to read DOWN
    # while RimWorld was running. Meanwhile the no-recipient path already exits 1 with
    # the stamp SAFELY written, so success and failure were the wrong way round.
    # ⚠️ `tried` excludes this window and the seats deliberately not told, so narrowing
    # to nobody is not a failure — only failing everyone we actually attempted is.
    if stamp_failed or (tried and not sent):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
