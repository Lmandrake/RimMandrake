"""contracts.jsonl -- the one JSONL line policy. STDLIB ONLY: the dispatcher tick, close_evidence (imported by every
recording tool) and the SteveDesktop worker import this without paying for pydantic.

Every physical line becomes exactly one of:
  Row(n, value, notes)    -- the line decoded to a JSON object; `notes` are strict-mode observations about a line the
                             lenient (today's) rule still accepts: dup_key, nonfinite, replacement_char;
  Fault(n, code, reason)  -- an explicit, accounted refusal with the raw line's sha256 and a short snippet.
Nothing raises (RecursionError on absurd nesting included) and nothing is dropped without a Fault.

LENIENT decision == `json.loads(line)` succeeding and giving a dict: exactly what every reader did before this module,
so wiring it in changes no reader's accept/refuse decision. STRICT is the same plus refusal of every note; callers
that want a stricter contract ask for it explicitly (and the replay tool reports both).

Fault codes:  blank, not_json, not_object, too_deep   (lenient)
Note codes:   dup_key, nonfinite, replacement_char      (strict only)
"""
import hashlib
import json

BLANK, NOT_JSON, NOT_OBJECT, TOO_DEEP = "blank", "not_json", "not_object", "too_deep"
DUP_KEY, NONFINITE, REPLACED = "dup_key", "nonfinite", "replacement_char"
LENIENT_CODES = (BLANK, NOT_JSON, NOT_OBJECT, TOO_DEEP)
NOTE_CODES = (DUP_KEY, NONFINITE, REPLACED)
SNIPPET = 160


class Row:
    __slots__ = ("n", "value", "notes")

    def __init__(self, n, value, notes=()):
        self.n, self.value, self.notes = n, value, tuple(notes)

    ok = True

    def __repr__(self):
        return "Row(%d%s)" % (self.n, ", notes=%r" % (self.notes,) if self.notes else "")


class Fault:
    __slots__ = ("n", "code", "reason", "sha256", "snippet")

    def __init__(self, n, code, reason, raw=""):
        self.n, self.code, self.reason = n, code, reason
        b = raw.encode("utf-8", "surrogatepass") if isinstance(raw, str) else bytes(raw or b"")
        self.sha256 = hashlib.sha256(b).hexdigest()
        self.snippet = raw[:SNIPPET] if isinstance(raw, str) else repr(raw[:SNIPPET])

    ok = False

    def as_dict(self):
        return {"n": self.n, "code": self.code, "reason": self.reason, "sha256": self.sha256, "snippet": self.snippet}

    def __repr__(self):
        return "Fault(%d, %s: %s)" % (self.n, self.code, self.reason)


class _Dup(Exception):
    pass


def _pairs_strict(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise _Dup(k)
        seen.add(k)
    return dict(pairs)


def _nonfinite(c):
    raise ValueError("non-finite number %s" % c)


def strict_notes(line):
    """-> the note codes for a line the lenient rule accepted (a second, stricter parse; only when asked for)."""
    notes = []
    try:
        json.loads(line, object_pairs_hook=_pairs_strict)
    except _Dup:
        notes.append(DUP_KEY)
    except (ValueError, RecursionError):
        pass
    try:
        json.loads(line, parse_constant=_nonfinite)
    except (ValueError, RecursionError):
        notes.append(NONFINITE)
    if "�" in line:
        notes.append(REPLACED)
    return notes


def decode(line, n=0, strict=False, need_object=True):
    """One physical line -> Row or Fault. Never raises."""
    if not isinstance(line, str):
        try:
            line = line.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            return Fault(n, NOT_JSON, "undecodable: %s" % type(e).__name__, b"")
    if not line.strip():
        return Fault(n, BLANK, "blank line", line)
    try:
        v = json.loads(line)
    except RecursionError:
        return Fault(n, TOO_DEEP, "nesting too deep to decode", line)
    except ValueError as e:
        return Fault(n, NOT_JSON, "not JSON: %s" % str(e)[:120], line)
    if need_object and not isinstance(v, dict):
        return Fault(n, NOT_OBJECT, "a JSON %s, not an object" % type(v).__name__, line)
    notes = strict_notes(line) if strict else ()
    if strict and notes:
        return Fault(n, notes[0], "strict: %s" % ", ".join(notes), line)
    return Row(n, v, notes)


def scan(lines, strict=False, need_object=True, start=1):
    """lines -> (rows, faults); every line lands in exactly one list, blanks as Fault(code=blank)."""
    rows, faults = [], []
    for n, ln in enumerate(lines, start):
        r = decode(ln, n, strict=strict, need_object=need_object)
        (rows if r.ok else faults).append(r)
    return rows, faults


def tally(faults):
    out = {}
    for f in faults:
        out[f.code] = out.get(f.code, 0) + 1
    return out
