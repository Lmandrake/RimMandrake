#!/usr/bin/env python3
"""game_names.py - the one map from a game's internal key to the name people and agents read and type.

The owner named the four games (card, 2026-11-22): ArchBig, ArchSmall, Steve1, Steve2. The internal keys do not change:
a game is a letter on its machine (`a` Steam's install, `b` its own install), a bridge key is `machine[.letter]`, a
control-store scope is `game:<letter>`. Every reader shows `show(...)`; every input goes through `letter(...)` or
`key(...)`, which take the new names in any letter case and the old keys as aliases, and refuse an unknown name by
name (never a default game).

    python3 src/RimMandrake/rimflow/game_names.py            the four games, their keys and aliases

Page: design/specs/2026-11-22-game-names/boundary.md.
Tests: src/RimMandrake/rimflow/selftest_game_names.py.
"""
import os
import re
import socket
import sys

# (display name, bridge key, machine, letter). The one source: nothing else spells a game's name.
GAMES = (
    ("ArchBig", "archmagi", "archmagi", "a"),            # Steam's install on Archmagi: the full mod list, his looks
    ("ArchSmall", "archmagi.b", "archmagi", "b"),        # its own install on Archmagi (instances/b/game): tier lists
    ("Steve1", "stevedesktop", "stevedesktop", "a"),     # SteveDesktop's first game (its test lane)
    ("Steve2", "stevedesktop.b", "stevedesktop", "b"),   # SteveDesktop's second game
)
MACHINES = ("archmagi", "stevedesktop")
DEFAULT_MACHINE = "archmagi"            # absent means Archmagi, as model.DEFAULT_BRIDGE_HOST


class GameNameError(ValueError):
    """A name that is no game. str() names what was typed and the names that are known."""


def known():
    return ", ".join(n for n, _k, _m, _l in GAMES)


def machine(m=None):
    """-> the machine a letter belongs to: `m`, else RM_HOST, else this host's name; a host that is not a game machine
    (a Mac, a test box) is Archmagi, the default host, as everywhere else in rimflow."""
    m = str(m or os.environ.get("RM_HOST") or socket.gethostname()).strip().lower()
    return m if m in MACHINES else DEFAULT_MACHINE


def _norm_key(text):
    k = str(text).strip().lower()
    mach, dot, inst = k.partition(".")
    if mach in MACHINES and dot and inst == "a":
        return mach                    # machine.a is the machine's first game, the same lock as no suffix
    return k


def name_key(text):
    """-> the bridge key of a game NAME (any case), or None when `text` is not one of the four names. Old keys are not
    read here: their own parser (model.bridge_host_key) keeps its one rule for them."""
    t = str(text or "").strip().lower()
    for n, k, _m, _l in GAMES:
        if t == n.lower():
            return k
    return None


def key(text):
    """-> the bridge key ('archmagi.b') for a new name (any case) or an old key. None or '' -> None (the caller's
    default). An unknown name raises GameNameError naming it."""
    if text is None or not str(text).strip():
        return None
    t = str(text).strip()
    for n, k, _m, _l in GAMES:
        if t.lower() == n.lower():
            return k
    k = _norm_key(t)
    mach, dot, inst = k.partition(".")
    if mach in MACHINES and (not dot or re.fullmatch("[a-z]", inst)):
        return k
    raise GameNameError("no game %r (games: %s; the old keys archmagi, archmagi.b, stevedesktop, stevedesktop.b "
                        "still work)" % (text, known()))


def letter(text, mach=None):
    """-> the letter of a game on machine `mach` (default: this one) for a new name (any case), a letter, a bridge
    key, or `game:<x>`. A game of another machine, or an unknown name, raises GameNameError naming it."""
    if text is None:
        raise GameNameError("no game named (games: %s)" % known())
    t = str(text).strip()
    if t.lower().startswith("game:"):
        t = t[5:].strip()
    if re.fullmatch("[a-zA-Z]", t):
        return t.lower()
    here = machine(mach)
    try:
        k = key(t)
    except GameNameError:
        raise GameNameError("no game %r (games: %s; the letters a and b still work)" % (text, known()))
    if k is None:
        raise GameNameError("no game named (games: %s)" % known())
    m, _dot, inst = k.partition(".")
    if m != here:
        raise GameNameError("%s is a game on %s, not on this machine (%s, whose games are %s)" % (
            show_key(k), m, here, ", ".join(show(x, here) for x in ("a", "b"))))
    return inst or "a"


def show_key(k):
    """-> the name of bridge key `k` ('archmagi.b' -> 'ArchSmall'); None -> ArchBig (the default host). A key the
    owner has not named (a third game) reads as itself, never as another game's name."""
    k = _norm_key(k or DEFAULT_MACHINE)
    for n, kk, _m, _l in GAMES:
        if k == kk:
            return n
    return k


def show(g, mach=None):
    """-> the name of game letter `g` on machine `mach` (default: this one): 'b' -> 'ArchSmall' on Archmagi. None or
    '' is the machine's first game. A name or key is shown as its game; anything else reads as itself."""
    t = str(g or "a").strip()
    if t.lower().startswith("game:"):
        t = t[5:].strip()
    if re.fullmatch("[a-zA-Z]", t):
        return show_key("%s.%s" % (machine(mach), t.lower()))
    try:
        return show_key(key(t))
    except GameNameError:
        return t


def show_scope(scope):
    """'game:b' -> 'game:ArchSmall'; any other scope is returned as it is."""
    s = str(scope or "")
    return "game:" + show(s[5:]) if s.startswith("game:") else s


# "game a", "Game b's", "game:a" in a message our own code formatted -> the game's name. Not "game a run" / "game a live
# run" (English: "the first game a run may take"), which name no game.
_LETTER_TEXT = re.compile(r"\b([Gg])ame(:| )([ab])\b(?! (?:live )?run\b)")


def name_text(text, mach=None):
    """-> `text` with each game letter our messages print ("game a", "game b's", "game:b") replaced by the game's name
    on machine `mach` (default: this one). For a message built from many format strings (launch, stop, the tick's
    reasons); a reader that formats one line calls show() instead."""
    if not text:
        return text

    def sub(m):
        return ("game:" if m.group(2) == ":" else "") + show(m.group(3), mach)
    return _LETTER_TEXT.sub(sub, str(text))


def main(argv=None):
    for n, k, m, l in GAMES:
        print("%-10s  bridge key %-15s  letter %s on %s" % (n, k, l, m))
    print("(type any of these names, any letter case; the old keys and letters still work)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
