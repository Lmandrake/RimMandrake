#!/usr/bin/env python3
# C2/C8 run replay_worker.py as `python -E -P`, which the coverage trace cannot see (evidence_covers.HEADER):
# selftest-covers: src/RimMandrake/contracts/replay_worker.py
"""selftest_contracts -- the contracts package (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS,
CONTRACTS_REPLAY_HARDEN_OK_WITHOUT_PROOF).

stdlib (always run):
  C1  jsonl.decode never raises and every line lands as exactly one Row or Fault (fixtures + hostile lines)
  C9  jsonl exact outcomes (review #6, #7, #8, #14): nested overflow / NaN, duplicate keys, bad bytes inside a string,
      distinct byte fingerprints, BOM, CRLF, huge integers, a text stream that raises, scan_bytes accounting
  C10 compat.ledger_ts is the dispatcher's operand; falsey ts values are passed over without a crash (review #9)
  C6  the stdlib layers and the hot readers (close_evidence, dispatcher, arbiter_pending, testq) import nothing outside
      the standard library and src/RimMandrake (no pydantic)
needs pydantic:
  C3  AuditRecord == audits.schema.json: required, properties, enums, pattern, and every property's JSON type
  C5  the exported Arbiter schema files are current (export.py --check)
  C7  close_evidence_kind on a v4 line never mutates the dict (the mac is over the raw dict)
  C11 model rules (review #10-#13): legacy version types, attempt ids, impossible timestamps, evidence paths
  C12 strict replay works on BYTES: a duplicate disposition and bytes that are not UTF-8 are refused (review #5)
needs pydantic and the base commit (old readers come from git):
  C2  replay fixtures: two isolated trees, every expectation in expected.json holds, every old/new difference is
      exactly its allowances.json entry
  C4  audits.problems() decides like the old interpreter at BASE on 3000 mutated records (old run in its own tree)
  C8  the replay can see: a NEW tree with a broken audits reader and a broken testq collect path FAILS the replay
      (review #1, #2, #4); a worker running the wrong code is an instrument error; a blanket crash->skip is refused

A check that cannot run is reported with the UNMEASURED phrase and the run never ends ALL PASS (review #15).
"""
import contextlib
import copy
import io
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
if RM not in sys.path:
    sys.path.insert(0, RM)
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"
fails, skipped = [], []
n_ok = 0


def check(name, cond, detail=""):
    global n_ok
    if cond:
        n_ok += 1
    else:
        fails.append(name)
        print("FAIL %s %s" % (name, detail))


def skip(name, why):
    skipped.append(name)
    print("SKIP %s: %s -- %s" % (name, why, UNMEASURED_PHRASE))


def foreign_imports(code):
    """Run `code` in a fresh interpreter (cwd src/RimMandrake) -> (ok, modules imported from outside the standard
    library and src/RimMandrake)."""
    probe = ("import sys\n_base = set(sys.modules)\n" + code + "\nimport sys, os\nrm = os.path.realpath(%r) + os.sep\nbad = []\n"
             "for k, m in list(sys.modules.items()):\n"
             "    top = k.split('.')[0]\n"
             "    if k in _base or top in sys.stdlib_module_names or k in sys.builtin_module_names:\n"
             "        continue\n"
             "    f = getattr(m, '__file__', None)\n"
             "    if f and os.path.realpath(f).startswith(rm):\n"
             "        continue\n"
             "    bad.append(k)\n"
             "print('FOREIGN=' + ','.join(sorted(bad)))\n") % RM
    r = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, timeout=120, cwd=RM,
                       env=dict(os.environ, TESTQ_QUEUE=tempfile.gettempdir()))
    line = [x for x in r.stdout.splitlines() if x.startswith("FOREIGN=")]
    if r.returncode != 0 or not line:
        return False, (r.stdout + r.stderr)[-300:]
    bad = [x for x in line[-1][8:].split(",") if x]
    return not bad, bad


# ------------------------------------------------------------------ stdlib checks

def c1(CJ, FX, families):
    hostile = ["", "  ", "{", "[1]", "null", "1e999", '{"a": NaN}', '{"a":1,"a":2}', "\ufffd", "\x00", FX.DEEP_LINE,
               b"\xff\xfe{}", '{"x": "' + "y" * 100000 + '"}']
    lines = hostile + [b for fam in families for b, _ in FX.load_bytes(fam)]
    raised = 0
    for strict in (False, True):
        for i, ln in enumerate(lines):
            try:
                r = CJ.decode(ln, i, strict=strict)
                check("C1 one outcome", (r.ok and hasattr(r, "value")) or (not r.ok and r.code), repr(ln)[:60])
            except BaseException:  # noqa: BLE001
                raised += 1
    check("C1 decode never raises", raised == 0, "%d raised" % raised)
    rows, faults = CJ.scan(hostile)
    check("C1 scan accounts every line", len(rows) + len(faults) == len(hostile))
    check("C1 deep is too_deep", CJ.decode(FX.DEEP_LINE).code == CJ.TOO_DEEP)


def c9(CJ):
    def both(line, lenient, strict_code, name):
        try:
            lo, st = CJ.decode(line), CJ.decode(line, strict=True)
        except Exception as e:  # noqa: BLE001
            check("C9 %s decodes without raising" % name, False, repr(e))
            return None, None
        check("C9 %s lenient" % name, (lo.ok if lenient == "row" else lo.code == lenient), lo)
        check("C9 %s strict" % name, (st.ok if strict_code == "row" else (not st.ok and st.code == strict_code)), st)
        return lo, st

    both('{"a": {"b": 1e999}}', "row", 'nonfinite', "nested overflow")          # review #6: parse_float path
    both('{"a": [1, -1e400]}', "row", 'nonfinite', "nested negative overflow")
    both('{"a": {"b": NaN}}', "row", 'nonfinite', "nested NaN")
    both('{"a": {"b": 1, "b": 2}}', "row", 'dup_key', "nested duplicate key")
    both('{"a": 1.5e10}', "row", "row", "finite float")
    lo, st = both(b'{"x": "\xff"}', "row", 'not_utf8', "bad byte inside a string")   # review #7
    check("C9 lenient keeps U+FFFD", lo is not None and lo.ok and lo.value == {"x": "\ufffd"}, getattr(lo, "value", None))
    both('{"x": "\ufffd"}', "row", 'replacement_char', "a str line holding U+FFFD")
    both("{\"x\": \"\ufffd\"}".encode(), "row", "row", "valid UTF-8 bytes of U+FFFD")  # real character, not damage
    try:
        fa, fb = CJ.decode(b'{"x": "\xff"}', strict=True), CJ.decode(b'{"x": "\xfe"}', strict=True)
    except Exception as e:  # noqa: BLE001
        fa = fb = types.SimpleNamespace(sha256=repr(e))
    check("C9 fingerprints differ for different bytes", fa.sha256 != fb.sha256, (fa.sha256, fb.sha256))
    import hashlib
    check("C9 fingerprint is over the original bytes", fa.sha256 == hashlib.sha256(b'{"x": "\xff"}').hexdigest())
    both('\ufeff{"a": 1}', 'not_json', 'not_json', "BOM (str)")
    both(b'\xef\xbb\xbf{"a": 1}', 'not_json', 'not_json', "BOM (bytes)")
    both('{"a": 1}\r\n', "row", "row", "CRLF")
    both('{"a": ' + "1" * 5000 + "}", 'not_json', 'not_json', "huge integer (int max str digits)")
    both('{"a": ' + "1" * 4000 + "}", "row", "row", "big integer under the limit")
    # review #8: a text stream that raises mid-iteration is accounted, not raised
    bad = io.TextIOWrapper(io.BytesIO(b'{"a": 1}\n' + b"\xff" * 9000 + b'\n{"b": 2}\n'), encoding="utf-8")
    try:
        rows, faults = CJ.scan(bad)
        check("C9 raising stream -> unreadable_stream fault",
              faults and faults[-1].code == 'unreadable_stream', [f.code for f in faults])
    except Exception as e:  # noqa: BLE001
        check("C9 scan over a raising stream never raises", False, repr(e))
    if not hasattr(CJ, "scan_bytes"):
        check("C9 scan_bytes exists (binary path, review #8)", False)
        return
    rows, faults = CJ.scan_bytes(b'{"a": 1}\n\xff\xff\n{"b": 2}\n\n')
    check("C9 scan_bytes accounts every physical line", len(rows) + len(faults) == 4, (rows, faults))
    check("C9 scan_bytes keeps the line after bad bytes", [r.value for r in rows] == [{"a": 1}, {"b": 2}], rows)
    rows, faults = CJ.scan_bytes(io.BytesIO(b'{"a": 1}\n{"b": "\xff"}\n'), strict=True)
    check("C9 scan_bytes strict names not_utf8", [f.code for f in faults] == ['not_utf8'], faults)


def c10(CC):
    for v in (None, 0, False, [], {}, ""):
        check("C10 ledger_ts(%r) is ''" % (v,), CC.ledger_ts({"ts": v}) == "")
    check("C10 ledger_ts absent", CC.ledger_ts({}) == "")
    check("C10 ledger_ts str", CC.ledger_ts({"ts": "2026-10-27T00:00:00Z"}) == "2026-10-27T00:00:00Z")
    check("C10 truthy non-str unusable", not CC.ledger_event_usable({"ts": 5}))
    sys.path.insert(0, os.path.join(RM, "rimflow"))
    import dispatcher
    src = open(dispatcher.__file__, encoding="utf-8").read()
    check("C10 dispatcher compares the shared operand", "CC.ledger_ts(ev) > since_iso" in src)
    with tempfile.TemporaryDirectory(prefix="selftest_contracts_") as clone:
        d = os.path.join(clone, "infrastructure", "state", "ledger", "events")
        os.makedirs(d)
        with open(os.path.join(d, "BENCH.jsonl"), "w", encoding="utf-8") as f:
            for v in (None, 0, False, [], {}):
                f.write(json.dumps({"ts": v, "seat": "BENCH", "event": "note"}) + "\n")
            f.write(json.dumps({"ts": "2026-10-27T12:00:00Z", "seat": "BENCH", "event": "note"}) + "\n")
        with open(os.path.join(d, "BENCH.jsonl"), "ab") as f:
            # a bad byte inside a VALUE: the line is skipped whole, never accepted with U+FFFD in its id (commissioning)
            f.write(b'{"ts": "2026-10-27T13:00:00Z", "seat": "BENCH", "event": "note", "id": "X_\xff_Y"}\n')
            # a lone CR splits lines as text mode did (the old reader), so both events are seen
            f.write(b'{"ts": "2026-10-27T14:00:00Z", "seat": "BENCH", "event": "a"}\r'
                    b'{"ts": "2026-10-27T15:00:00Z", "seat": "BENCH", "event": "b"}\r\n')
        try:
            got = dispatcher.seat_events_since(clone, "BENCH", "2026-10-27T00:00:00Z")
            check("C10 falsey ts and a damaged line passed over, CR splits like text mode", [e["ts"] for e in got] == ["2026-10-27T12:00:00Z", "2026-10-27T14:00:00Z", "2026-10-27T15:00:00Z"], got)
        except Exception as e:  # noqa: BLE001
            check("C10 falsey ts never crash the tick", False, repr(e))


def c6():
    for code in ("from contracts import jsonl, compat, blind_core",
                 "import sys; sys.path.insert(0, 'Utils'); import close_evidence",
                 "import sys; sys.path.insert(0, 'rimflow'); import arbiter_pending",
                 "import sys; sys.path.insert(0, 'rimflow'); import dispatcher",
                 "import sys; sys.path.insert(0, 'Utils/testq'); import testq"):
        ok, bad = foreign_imports(code)
        check("C6 stdlib + RimMandrake only: " + code.split(";")[-1].strip(), ok, bad)
    ok, bad = foreign_imports("from contracts import models")
    check("C6 the instrument sees a foreign import (models -> pydantic)", not ok and "pydantic" in bad, bad)


# ------------------------------------------------------------------ pydantic checks

def c3(CM):
    sys.path.insert(0, os.path.join(RM, "rimflow"))
    import audits
    sch = audits.schema()
    fields = CM.AuditRecord.model_fields
    req = sorted(k for k, f in fields.items() if f.is_required())
    check("C3 required", req == sorted(sch["required"]), (req, sch["required"]))
    check("C3 properties", sorted(fields) == sorted(sch["properties"]), sorted(set(fields) ^ set(sch["properties"])))
    for k in ("why_picked", "verdict"):
        lit = fields[k].annotation.__args__
        check("C3 enum " + k, list(lit) == sch["properties"][k]["enum"], (lit, sch["properties"][k]["enum"]))
    check("C3 sha pattern", sch["properties"]["sha"]["pattern"] == CM.HEX7_40)
    # every property's JSON type, value by value (review #16): the model's type errors == the schema's type rule
    import pydantic
    base = {"ts": "2026-10-27T00:00:00Z", "item": "X_Y_Z", "sha": "abcdef1", "run": "r1", "why_picked": "rank",
            "flags": [], "verdict": "UNRESOLVED", "defect_class": None, "evidence": ["D:\\a"], "waiting_for": None}
    samples = {"string": "x", "number": 1.5, "integer": 2, "boolean": True, "null": None, "array": ["x"],
               "object": {"k": "v"}}
    jtype = {"string": str, "null": type(None), "array": list, "object": dict}
    typed = 0
    for k, p in sch["properties"].items():
        if "type" not in p:
            continue
        allowed = p["type"] if isinstance(p["type"], list) else [p["type"]]
        for sname, sval in list(samples.items()) + [("array_of_int", [1])]:
            want = any(isinstance(sval, jtype.get(t, ())) and not isinstance(sval, bool) or
                       (t == "boolean" and isinstance(sval, bool)) for t in allowed)
            if sname == "array_of_int":
                want = "array" in allowed and p.get("items", {}).get("type") != "string"
            d = dict(base, **{k: sval})
            try:
                CM.AuditRecord.model_validate(d)
                type_err = False
            except pydantic.ValidationError as e:
                type_err = any(x["loc"] and x["loc"][0] == k and x["type"].endswith("_type") for x in e.errors())
            check("C3 type %s=%s" % (k, sname), want == (not type_err), (allowed, type_err))
            typed += 1
    check("C3 type checks ran", typed >= 50, typed)


def c7(CM, FX):
    ev = [json.loads(b) for b, e in FX.load_bytes("close_evidence") if e["class"] in ("valid_v4", "valid_v4_fail")]
    check("C7 has a v4 fixture", bool(ev))
    for d in ev:
        before = json.dumps(d, sort_keys=True)
        kind, _ = CM.close_evidence_kind(d)
        check("C7 kind v4", kind == "v4", kind)
        check("C7 dict unchanged", json.dumps(d, sort_keys=True) == before)
    return ev


def c11(CM, FX, v4):
    leg = {"ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": "0" * 40, "result": "PASS"}
    for v, ok in ((1, True), (2, True), (3, True), ("absent", True), (1.0, False), (True, False), (None, False),
                  ("1", False), (4.0, False), (0, False)):
        d = dict(leg) if v == "absent" else dict(leg, v=v)
        kind, e = CM.close_evidence_kind(d)
        check("C11 legacy v=%r" % (v,), (kind != "fault") == ok, (kind, e[:1] if kind == "fault" else ""))
    for v in (4.0, True, "4"):
        kind, e = CM.close_evidence_kind(dict(v4[0], v=v))
        check("C11 v4 v=%r refused" % (v,), kind == "fault", kind)
    tq = json.loads(FX.load_bytes("testq_results")[0][0])
    job = tq["job"]
    for att, ok in ((job + ".a1", True), (job + ".a12", True), (job + ".a", False), (job + ".aanything", False),
                    (job + ".a0", False), (job + ".a1x", False), (job + ".a\uff11", False), ("other.a1", False),
                    (job + ".a1\n", False)):
        e = CM.errors(CM.TestqResult, dict(tq, attempt=att))
        check("C11 attempt %r" % att[len(job):] if att.startswith(job) else "C11 attempt %r" % att, (not e) == ok, e[:1])
    ver = json.loads(FX.load_bytes("verdicts")[0][0])
    for ts, ok in (("2026-10-27T12:00:00Z", True), ("2026-99-99T99:99:99Z", False), ("2026-02-30T00:00:00Z", False),
                   ("2026-10-27T24:00:00Z", False), ("2026-10-27T12:00:60Z", False)):
        check("C11 verdict ts %s" % ts, (not CM.errors(CM.ArbiterVerdict, dict(ver, ts=ts))) == ok)
    for ts, ok in (("2026-10-27T12:00:00Z", True), ("2026-13-01T00:00:00Z", False)):
        check("C11 ledger ts %s" % ts, (not CM.errors(CM.LedgerEventMin, {"ts": ts, "seat": "B", "event": "e"})) == ok)
        th = json.loads(FX.load_bytes("tiers_history")[0][0])
        check("C11 tiers generated %s" % ts, (not CM.errors(CM.TiersHistoryRow, dict(th, generated=ts))) == ok)
    for off, ok in (("+00:00", True), ("+05:30", True), ("Z", True), ("+25:00", False), ("+05:99", False)):
        e = CM.errors(CM.LedgerEventMin, {"ts": "2026-09-01T00:00:00" + off})
        check("C11 ledger ts offset %s" % off, (not e) == ok, e[:1])
    for ev, ok in ((["D:\\ClaudeWork\\x.md"], True), (["\\\\host\\share\\x"], True), ([""], False),
                   (["relative.txt"], False), (["/mnt/d/x"], False), (["D:relative"], False), ([], False),
                   (["D:\\ok", ""], False)):
        check("C11 evidence %r" % (ev,), (not CM.errors(CM.ArbiterVerdict, dict(ver, evidence=ev))) == ok)


def c12(RP):
    ver = '{"item": "X_Y_Z", "sha": "abcdef1", "disposition": "FAIL-check", "causes": ["check"], "interim": null, ' \
          '"evidence": ["D:\\\\a\\\\b.md"], "ts": "2026-10-27T12:00:00Z", "disposition": "PASS"}'
    st, why = RP.strict("verdicts", ver.encode())
    check("C12 duplicate disposition refused on the bytes", (st, why) == ("refuse", "dup_key"), (st, why))
    st, why = RP.strict("ledger_events", b'{"ts": "2026-10-27T12:00:00Z", "seat": "\xff", "event": "e"}')
    check("C12 bytes that are not UTF-8 refused", (st, why) == ("refuse", "not_utf8"), (st, why))
    check("C12 input class not_utf8", RP.input_class("ledger_events", b'{"a": "\xff"}') == "not_utf8")
    check("C12 input class ts_nonstr", RP.input_class("ledger_events", b'{"ts": 5}') == "ts_nonstr")


# ------------------------------------------------------------------ replay checks (pydantic + git)

def c2(RP, tmp):
    trees = RP.make_trees(os.path.join(tmp, "c2"), RP.BASE)
    allow = RP.load_allowances()
    work = os.path.join(tmp, "c2", "work")
    os.makedirs(work)
    rep = RP.run_fixtures(trees, work, allow)
    check("C2 fixture lines", rep["lines"] >= 100, rep["lines"])
    check("C2 every family present", sorted(rep["families"]) == sorted(RP.FAMILIES), rep["families"])
    check("C2 expectations", not rep["expectation_misses"], rep["expectation_misses"][:3])
    check("C2 no unexplained diff", not rep["unexplained"], [(d["family"], d["class"]) for d in rep["unexplained"]])
    check("C2 every allowance exercised", sorted(rep["allowed_diffs"]) == sorted(allow), rep["allowed_diffs"])
    return trees


def c4(RP, CM, tmp, trees):
    sys.path.insert(0, os.path.join(RM, "rimflow"))
    import audits
    rng = random.Random(4)
    base = {"ts": "2026-10-27T00:00:00Z", "item": "X_Y_Z", "sha": "abcdef1", "run": "r1", "why_picked": "rank",
            "flags": [], "verdict": "SOUND", "defect_class": None, "evidence": ["D:\\a"]}
    vals = [None, "", "x", "DEFECT", "UNRESOLVED", "SOUND", "abcdef1\n", "ABCDEF1", 0, 1.5, True, [], ["a"], [1],
            {}, "random", "mandatory"]
    docs = []
    for _ in range(3000):
        d = copy.deepcopy(base)
        for _k in range(rng.randrange(1, 4)):
            key = rng.choice(sorted(base) + ["waiting_for", "extra"])
            if rng.random() < 0.15:
                d.pop(key, None)
            else:
                d[key] = rng.choice(vals)
        docs.append(d)
    p = os.path.join(tmp, "c4_docs.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(docs, f)
    old_tree = trees["old"][0]
    code = ("import sys, json; sys.path.insert(0, %r); import audits; "
            "assert audits.__file__.startswith(%r), audits.__file__; "
            "print(json.dumps([bool(audits.problems(d)) for d in json.load(open(%r))]))"
            % (os.path.join(old_tree, "src", "RimMandrake", "rimflow"), old_tree, p))
    r = subprocess.run([sys.executable, "-E", "-P", "-c", code], capture_output=True, text=True, timeout=120, cwd=tmp)
    if r.returncode != 0:
        check("C4 old audits ran in its own tree", False, r.stderr[-300:])
        return
    old = json.loads(r.stdout)
    new = [bool(audits.problems(d)) for d in docs]
    differ = [i for i in range(len(docs)) if old[i] != new[i]]
    for i in differ[:3]:
        print("  C4 differ:", json.dumps(docs[i]), old[i], new[i])
    check("C4 audits decision unchanged", not differ, "%d of 3000 differ" % len(differ))
    check("C4 the mutations both pass and fail (instrument sees)", 100 < sum(new) < 2900, sum(new))


def c8(RP, tmp, trees):
    allow = RP.load_allowances()
    # a NEW tree whose audits reader accepts nothing and whose testq collect path reads every result as readable
    broken = os.path.join(tmp, "c8_src")
    shutil.copytree(trees["new"][0], broken)
    ap = os.path.join(broken, "src", "RimMandrake", "rimflow", "audits.py")
    with open(ap, "a", encoding="utf-8") as f:
        f.write("\n_c8_parse = parse\nparse = lambda text: _c8_parse(text)[:0]   # selftest C8 sabotage\n")
    tp = os.path.join(broken, "src", "RimMandrake", "Utils", "testq", "testq.py")
    src = open(tp, encoding="utf-8").read()
    check("C8 testq sabotage site exists", "if not CC.testq_result_readable(res):" in src)
    with open(tp, "w", encoding="utf-8") as f:
        f.write(src.replace("if not CC.testq_result_readable(res):", "if False:"))
    t2 = RP.make_trees(os.path.join(tmp, "c8"), RP.BASE, new_tree=broken)
    work = os.path.join(tmp, "c8", "work")
    os.makedirs(work)
    rep = RP.run_fixtures(t2, work, allow)
    fams = {(d["family"], d["fixture_class"]) for d in rep["unexplained"]}
    check("C8 broken audits reader is an unexplained difference", ("audits", "valid") in fams, sorted(fams)[:6])
    check("C8 broken testq collect path is an unexplained difference",
          ("testq_results", "unsupported_version") in fams, sorted(fams)[:6])
    check("C8 testq orphan path untouched by the sabotage",
          not any(f == "testq_orphans" for f, _c in fams), sorted(fams)[:6])
    # a worker that ran other code than its tree's is an instrument error, not a result
    t3 = {"old": trees["old"], "new": (trees["new"][0], dict(trees["new"][1], audits="0" * 64))}
    w3 = os.path.join(tmp, "c8", "w3")
    os.makedirs(w3)
    try:
        RP.run_sides(t3, [RP.job(0, "audits", b"{}")], w3, chunks=1)
        check("C8 module hash mismatch is an instrument error", False)
    except RP.InstrumentError as e:
        check("C8 module hash mismatch is an instrument error", "audits" in str(e), str(e))
    # allowances are exact: the old blanket rule (any crash -> refuse/skip) is gone
    o = {"d": "crash", "exc": "RecursionError", "out": None}
    check("C8 crash->skip not allowed where the family's allowance says refuse",
          RP.compare(allow, "close_evidence", "too_deep", o, {"d": "skip", "exc": None, "out": "x"}) == "UNEXPLAINED")
    check("C8 crash->refuse not allowed for another input class",
          RP.compare(allow, "close_evidence", "not_json", o, {"d": "refuse", "exc": None, "out": "x"})
          == "UNEXPLAINED")
    check("C8 equal decisions with different results are a difference",
          RP.compare(allow, "audits", "ok", {"d": "accept", "exc": None, "out": "a"},
                     {"d": "accept", "exc": None, "out": "b"}) == "UNEXPLAINED")
    ta = {"d": "accept", "exc": None, "out": "a"}
    tb = {"d": "accept", "exc": None, "out": "b"}
    check("C8 a well-formed ok testq result whose digest drifts is NOT allowed",
          RP.compare(allow, "testq_results", "ok", ta, tb) == "UNEXPLAINED")
    check("C8 a tagged-malformed testq result's digest change is the named allowance",
          RP.compare(allow, "testq_results", "tagged_malformed", ta, tb) == "TESTQ_RESULT_BREAKING_RECORDED_INVALID")
    from contracts.fixtures import make_fixtures as FX
    good = json.loads(FX.load_bytes("testq_results")[0][0])
    check("C8 input_class: well-formed testq result is ok",
          RP.input_class("testq_results", json.dumps(good).encode()) == "ok")
    check("C8 input_class: tagged result breaking testq.result/1 is tagged_malformed",
          RP.input_class("testq_results", json.dumps(dict(good, outcome="INVALID")).encode()) == "tagged_malformed")
    check("C8 the named allowance matches",
          RP.compare(allow, "close_evidence", "too_deep", o, {"d": "refuse", "exc": None, "out": "x"})
          == "CE_TOO_DEEP")


def guard(name, fn, *a):
    try:
        return fn(*a)
    except Exception as e:  # noqa: BLE001 - a check that crashes is a failure, never a silent stop
        import traceback
        traceback.print_exc()
        check(name + " ran to the end", False, repr(e))


def main():
    from contracts import jsonl as CJ, compat as CC
    from contracts.fixtures import make_fixtures as FX
    families = ("close_evidence", "audits", "verdicts", "tiers_history", "ledger_events", "sessions",
                "testq_results", "testq_orphans")
    guard('C1', c1, CJ, FX, families)
    guard('C9', c9, CJ)
    guard('C10', c10, CC)
    guard('C6', c6)
    try:
        import pydantic  # noqa: F401
    except ImportError:
        for c in ("C2", "C3", "C4", "C5", "C7", "C8", "C11", "C12"):
            skip(c, "pydantic missing (pip install --user -r src/RimMandrake/contracts/requirements.lock)")
        return finish()
    from contracts import models as CM, replay as RP, export as EX
    guard('C3', c3, CM)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = EX.main(["--check"])
    check("C5 exported schemas current", rc == 0)
    v4 = guard('C7', c7, CM, FX) or []
    if v4:
        guard('C11', c11, CM, FX, v4)
    else:
        check('C11 has v4 fixtures', False)
    guard('C12', c12, RP)
    have_git = subprocess.run(["git", "-C", RP.REPO, "cat-file", "-e", RP.BASE + "^{commit}"],
                              capture_output=True).returncode == 0
    if not have_git:
        for c in ("C2", "C4", "C8"):
            skip(c, "base commit %s absent from this clone" % RP.BASE)
        return finish()
    tmp = tempfile.mkdtemp(prefix="selftest_contracts_")
    try:
        trees = guard('C2', c2, RP, tmp)
        if trees:
            guard('C4', c4, RP, CM, tmp, trees)
            guard('C8', c8, RP, tmp, trees)
        else:
            check('C2 built the trees', False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return finish()


def finish():
    if fails:
        print("selftest_contracts: %d ok, %d fail" % (n_ok, len(fails)))
        return 1
    if skipped:
        print("selftest_contracts: %d ok, 0 fail, %d checks skipped (%s): %s" % (n_ok, len(skipped),
                                                                               " ".join(skipped), UNMEASURED_PHRASE))
        return 0
    print("selftest_contracts: %d ok, 0 fail -- ALL PASS" % n_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
