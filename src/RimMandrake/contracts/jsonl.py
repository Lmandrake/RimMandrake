"""contracts.jsonl -- the one JSONL line policy. STDLIB ONLY: the dispatcher tick, close_evidence (imported by every
recording tool) and the SteveDesktop worker import this without paying for pydantic.

Every physical line becomes exactly one of:
  Row(n, value, notes)    -- the line decoded to a JSON object; `notes` are strict-mode observations about a line the
                             lenient (today's) rule still accepts: dup_key, nonfinite, replacement_char, not_utf8;
  Fault(n, code, reason)  -- an explicit, accounted refusal with the sha256 of the line's ORIGINAL bytes (bytes in ->
                             those bytes, str in -> its UTF-8) and a short decoded snippet.
decode() never raises (RecursionError on absurd nesting included). scan_bytes() accounts every physical line of a
binary stream; scan() over an iterable of already-decoded lines cannot see bytes its iterator failed to decode, so an
iterator error ends the scan with one `unreadable_stream` Fault instead of raising (use scan_bytes for full accounting).

LENIENT decision == `json.loads(line)` succeeding and giving a dict: exactly what every reader did before this module,
so wiring it in changes no reader's accept/refuse decision. STRICT is the same plus refusal of every note; callers
that want a stricter contract ask for it explicitly (and the replay tool reports both).

Fault codes:  blank, not_json, not_object, too_deep, unreadable_stream   (lenient)
Note codes:   dup_key, nonfinite, replacement_char (a str line), not_utf8 (a bytes line)   (strict only)
"""
import hashlib
import json

BLANK, NOT_JSON, NOT_OBJECT, TOO_DEEP = "blank", "not_json", "not_object", "too_deep"
UNREADABLE_STREAM = "unreadable_stream"
DUP_KEY, NONFINITE, REPLACED, NOT_UTF8 = "dup_key", "nonfinite", "replacement_char", "not_utf8"
LENIENT_CODES = (BLANK, NOT_JSON, NOT_OBJECT, TOO_DEEP, UNREADABLE_STREAM)
NOTE_CODES = (DUP_KEY, NONFINITE, REPLACED, NOT_UTF8)
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

    def __init__(self, n, code, reason, raw="", text=None):
        """`raw` is the line as it arrived (bytes or str): the fingerprint covers exactly that, so two different
        corrupt byte strings never share a sha256 (review contracts #7). `text` is the decoded form for the snippet."""
        self.n, self.code, self.reason = n, code, reason
        b = raw.encode("utf-8", "surrogatepass") if isinstance(raw, str) else bytes(raw or b"")
        self.sha256 = hashlib.sha256(b).hexdigest()
        t = text if text is not None else raw
        self.snippet = t[:SNIPPET] if isinstance(t, str) else repr(t[:SNIPPET])

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


def _finite_float(s):
    """parse_float for strict mode: '1e999' overflows to inf without ever reaching parse_constant (review #6)."""
    f = float(s)
    if f != f or f in (float("inf"), float("-inf")):
        raise ValueError("non-finite number %s" % s)
    return f


def strict_notes(line, raw=None):
    """-> the note codes for a line the lenient rule accepted (a second, stricter parse; only when asked for).
    `raw` (the original bytes, when the caller had bytes) decides not_utf8 exactly; without it a U+FFFD in the text
    is the only trace of replaced damage (replacement_char)."""
    notes = []
    try:
        json.loads(line, object_pairs_hook=_pairs_strict)
    except _Dup:
        notes.append(DUP_KEY)
    except (ValueError, RecursionError):
        pass
    try:
        json.loads(line, parse_constant=_nonfinite, parse_float=_finite_float)
    except (ValueError, RecursionError):
        notes.append(NONFINITE)
    if raw is not None:
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            notes.append(NOT_UTF8)
    elif "�" in line:
        notes.append(REPLACED)
    return notes


def decode(line, n=0, strict=False, need_object=True):
    """One physical line (str, or bytes decoded UTF-8 with replacement) -> Row or Fault. Never raises."""
    raw = line
    if not isinstance(line, str):
        try:
            raw = bytes(line)
            line = raw.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            return Fault(n, NOT_JSON, "undecodable: %s" % type(e).__name__, b"")
    else:
        raw = None
    orig = raw if raw is not None else line
    if not line.strip():
        return Fault(n, BLANK, "blank line", orig, line)
    try:
        v = json.loads(line)
    except RecursionError:
        return Fault(n, TOO_DEEP, "nesting too deep to decode", orig, line)
    except ValueError as e:
        return Fault(n, NOT_JSON, "not JSON: %s" % str(e)[:120], orig, line)
    if need_object and not isinstance(v, dict):
        return Fault(n, NOT_OBJECT, "a JSON %s, not an object" % type(v).__name__, orig, line)
    notes = strict_notes(line, raw) if strict else ()
    if strict and notes:
        return Fault(n, notes[0], "strict: %s" % ", ".join(notes), orig, line)
    return Row(n, v, notes)


def scan(lines, strict=False, need_object=True, start=1):
    """lines -> (rows, faults); every line the iterable yields lands in exactly one list, blanks as Fault(code=blank).
    Never raises: if the iterable itself raises (a text stream meeting bytes that are not UTF-8), the scan stops with
    one Fault(code=unreadable_stream) for the line it could not obtain -- the lines after it are NOT accounted, which
    is why binary input belongs in scan_bytes()."""
    rows, faults = [], []
    n = start - 1
    it = iter(lines)
    while True:
        try:
            ln = next(it)
        except StopIteration:
            break
        except Exception as e:  # noqa: BLE001 - accounted, never raised
            faults.append(Fault(n + 1, UNREADABLE_STREAM, "stream raised %s; the rest is unread" % type(e).__name__))
            break
        n += 1
        r = decode(ln, n, strict=strict, need_object=need_object)
        (rows if r.ok else faults).append(r)
    return rows, faults


def scan_bytes(fh_or_bytes, strict=False, need_object=True, start=1):
    """A binary stream (or bytes) -> (rows, faults), split into physical lines on b"\\n" BEFORE decoding, so every
    line is accounted whatever its bytes (an empty tail after the last newline is not a line)."""
    data = fh_or_bytes if isinstance(fh_or_bytes, (bytes, bytearray)) else fh_or_bytes.read()
    parts = bytes(data).split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return scan(parts, strict=strict, need_object=need_object, start=start)


def tally(faults):
    out = {}
    for f in faults:
        out[f.code] = out.get(f.code, 0) + 1
    return out
