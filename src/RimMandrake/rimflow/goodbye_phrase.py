"""The one rule for "his WHOLE message is a goodbye" (CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME), shared by the
UserPromptSubmit hook (.claude/hooks/conductor_goodbye.py) and `seat_restart.py request` (which refuses a Conductor
restart unless his last message is still that goodbye).

norm: case-folded, apostrophes dropped, every run of non-word characters (Unicode-aware: punctuation, emoji,
spaces) read as one space. Letters of ANY script stay, so "goodbye 取消" or "bye ñandú" is not a goodbye (blind review
2026-10-29 P1-6: the old [^a-z0-9] rule erased them and fired).
"""
import re

DEFAULT_PHRASES = ("goodbye", "good bye", "bye", "gn", "good night", "goodnight", "done for now", "thats all")
_APOS = re.compile(r"['’‘`ʼ]")
_SEP = re.compile(r"[\W_]+", re.UNICODE)
_SENTENCE = re.compile(r"[.!?\n]+")
TRAILING = ("goodbye", "good bye")


def norm(text):
    t = _APOS.sub("", (text or "").casefold())
    return _SEP.sub(" ", t).strip()


def phrases(cfg, default=DEFAULT_PHRASES):
    """-> the normalized phrases of a seat_restart seat cfg (its goodbye_phrases), else the defaults."""
    out = []
    for p in (cfg or {}).get("goodbye_phrases") or default or ():
        n = norm(p) if isinstance(p, str) else ""
        if n and n not in out:
            out.append(n)
    return out


def is_goodbye(text, phr):
    """His whole message, or (owner 2026-11-01) a last sentence that says goodbye: the text before it goes to the next
    window. Only the word itself ends a longer message; "bye", "gn" or "that's all" could end an ordinary request."""
    n = norm(text)
    if not n:
        return False
    if n in set(phr or ()):
        return True
    t = (text or "").rstrip()
    last = _SENTENCE.split(t.rstrip(".! \n"))[-1]
    return not t.endswith("?") and len(_SENTENCE.split(t)) > 1 and norm(last) in TRAILING
