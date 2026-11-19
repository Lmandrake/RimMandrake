#!/usr/bin/env python3
"""probe_result.py — one result type for a read of the outside world (systemd, a file, the store, another program).

Page: design/specs/2026-11-19-probe-result/boundary.md (tests: selftest_probe_result.py). Owner, 2026-11-17: "No data,
failure, an answer of zero, or an answer of 'empty set' are all different cases and will be differentiated in return
values everywhere." A read returns exactly one of four answers:

    value(x)               looked, and this is what was there (x may be 0, [] or None: a measured answer)
    empty()                looked, and nothing was there
    could_not_look(cause)  the instrument could not see (systemctl failed, a file unreadable, the store locked)
    failed(cause)          the question was asked and broke (a crash, a reply that does not parse)

Each answer has .kind, .ok (true for the first two) and .cause (None for the first two). A looked answer reads as its
content: truth, iteration, len, index, `in`, int, float and .value. A blind answer raises NotAnswered, naming its
cause, the moment it is used as a truth value, a list or a number, so `answer or []` raises in its first test run
instead of reading as "nothing there". Read a blind one by its .kind and .cause.
"""
import operator

KINDS = ("value", "empty", "could_not_look", "failed")
_SAID = {"could_not_look": "COULD NOT LOOK", "failed": "FAILED"}


class NotAnswered(Exception):
    """A could-not-look or failed answer was used as an answer. .answer is it."""

    def __init__(self, answer):
        self.answer = answer
        super().__init__("%s (used as an answer)" % answer)


class Answer:
    __slots__ = ("kind", "cause", "_v")

    def __init__(self, kind, v=None, cause=None):
        self.kind, self._v, self.cause = kind, v, cause

    @property
    def ok(self):
        return self.kind in ("value", "empty")

    @property
    def value(self):
        if not self.ok:
            raise NotAnswered(self)
        return self._v

    def __bool__(self):
        return bool(self.value)

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, i):
        return self.value[i]

    def __contains__(self, x):
        return x in self.value

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __index__(self):
        return operator.index(self.value)

    def __str__(self):
        return str(self._v) if self.ok else "%s: %s" % (_SAID[self.kind], self.cause)

    def __repr__(self):
        return "Answer(%s, %r)" % (self.kind, self._v if self.ok else self.cause)


def value(x):
    """Looked, and x was there. A looked Answer passes through; a blind one raises rather than be hidden."""
    if isinstance(x, Answer):
        x.value     # noqa: B018  raises NotAnswered on a blind answer
        return x
    return Answer("value", x)


def empty():
    """Looked, and nothing was there: reads as an empty list."""
    return Answer("empty", [])


def _blind(kind, cause):
    if cause is None or not str(cause).strip():
        raise ValueError("a %s answer needs its cause" % kind)
    return Answer(kind, cause=str(cause))


def could_not_look(cause):
    """The instrument could not see. Raises NotAnswered when used as an answer."""
    return _blind("could_not_look", cause)


def failed(cause):
    """The question broke. Raises NotAnswered when used as an answer."""
    return _blind("failed", cause)
