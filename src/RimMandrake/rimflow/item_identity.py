"""The mod that an item names: one rule, one home (design/specs/2026-11-22-item-identity/boundary.md).

Readers ask `item_mod`; none keeps a rule of its own. A run's launch record (`RM_CONTROL_MOD`) outranks this guess, so
a reader that has the record reads the record first.
"""
import re

# Short names that are not in the mod's own name. The only table of them.
ALIASES = {"HOSE": "FlowWorks", "FW": "FlowWorks"}


def mod_tokens(folder, words_too=True):
    """-> {token: score}: the squashed name scores highest, then initials (3+ letters), 7+ letter words (only when
    words_too) and aliases."""
    words = re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", folder)
    out = {folder.upper().replace("_", ""): 100 + len(folder)}
    ini = "".join(w[0] for w in words).upper()
    if len(ini) >= 3:
        out.setdefault(ini, len(ini))
    for w in words if words_too else ():
        if len(w) >= 7:
            out.setdefault(w.upper(), len(w))
    for a, m in ALIASES.items():
        if m == folder:
            out.setdefault(a, len(a))
    return out


def named_mod(words, mods, words_too=True):
    """-> (named, mod): whether the words name any mod, and the one they name best (None on a tie)."""
    cands = {"".join(words[i:i + n]) for i in range(len(words)) for n in (1, 2, 3) if i + n <= len(words)}
    score = {}
    for f in mods:
        s = max([v for k, v in mod_tokens(f, words_too).items() if k in cands] or [0])
        if s:
            score[f] = s
    if not score:
        return False, None
    top = max(score.values())
    win = [f for f, s in score.items() if s == top]
    return True, (win[0] if len(win) == 1 else None)


def item_mod(item, mods, title=None):
    """The mod an item id names, else the one its title names, else None (also on a tie). A title names a mod only by
    its whole name, its initials or an alias: one word of it ("Mandrake", "patches") is ordinary prose there."""
    named, mod = named_mod([w for w in str(item or "").upper().split("_") if w], mods)
    if named:
        return mod
    named, mod = named_mod(re.findall(r"[A-Z0-9]+", str(title or "").upper()), mods, words_too=False)
    return mod if named else None
