"""Whole text, never a silent cut.

Owner, 2026-11-12, on learning that 687 of 813 stored judge refusals ended at character 600: "WHY would anything cut off
text at 600 characters?! please get rid of these arbitrary cuts!" (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS; refusal-contract
spec T9, design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md.)

So a detail, reason, why, verdict, evidence or note is stored WHOLE. Two helpers exist for the few places with a REAL
bound, and nothing else may cut:

- `fit(text, limit)`  a field with a real size bound: a ledger event must stay under `model.PIPE_BUF` (4096 bytes, one
                      atomic O_APPEND), an argv element under the kernel's 128 KiB. The text is returned whole when it
                      fits; otherwise the whole text is written to a side file and the field holds the head that fits plus
                      a pointer and the full length: `... [+N chars; whole text (M chars): <path>]`.
- `clip(text, n, where)`  a one-line DISPLAY view of a text already stored whole at `where`: it says it is cut and
                      where the rest is, instead of ending mid-sentence.

Side files are content-addressed (same text -> same file), so a caller that compares `fit(t, n)` with a stored field
gets the same string every time. `RM_FULLTEXT_DIR` overrides the side directory (selftests point it at a temp dir).
The lint `selftest_no_bare_cuts.py` fails on a new bare `[:NNN]` cut on a text field.
"""
import hashlib
import os

DEFAULT_DIRS = ("/mnt/d/ClaudeWork/rimmandrake/fulltext", os.path.expanduser("~/.cache/rimmandrake/fulltext"))
ARGV_MAX = 100_000          # one argv element; Linux MAX_ARG_STRLEN is 131072 bytes, kept clear of it for UTF-8


def side_dir():
    d = os.environ.get("RM_FULLTEXT_DIR")
    if d:
        return d
    for c in DEFAULT_DIRS:
        if os.path.isdir(os.path.dirname(c)):
            return c
    return DEFAULT_DIRS[-1]


def keep(text):
    """Write `text` whole to the side store. -> its path (content-addressed: the same text is the same file)."""
    text = "" if text is None else str(text)
    d = side_dir()
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, hashlib.sha256(text.encode("utf-8")).hexdigest()[:20] + ".txt")
    if not os.path.exists(path):
        tmp = "%s.tmp.%d" % (path, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    return path


def fit(text, limit, tail=False):
    """`text` if it is at most `limit` chars; else the head (or, with tail=True, the end) that fits with a pointer to the
    whole text, kept in a side file. The result is never longer than `limit` (when limit allows the pointer at all)."""
    text = "" if text is None else str(text)
    if len(text) <= limit:
        return text
    path = keep(text)
    mark = " [+%d chars; whole text (%d chars): %s]"
    room = max(0, limit - len(mark % (len(text), len(text), path)))
    shown = text[len(text) - room:] if tail else text[:room]
    m = mark % (len(text) - len(shown), len(text), path)
    return (m.lstrip() + " " + shown) if tail else (shown + m)


def clip(text, n, where):
    """A one-line view of a text stored whole at `where` (a path, a store row, a command that prints it)."""
    text = "" if text is None else str(text)
    if len(text) <= n:
        return text
    return "%s ... (+%d chars, full: %s)" % (text[:n], len(text) - n, where)


def read(path):
    """The whole text behind a pointer `fit` wrote."""
    with open(path, encoding="utf-8") as f:
        return f.read()
