#!/usr/bin/env python3
"""Regenerate the malformed-record fixture corpus (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS step 0).

    python3 src/RimMandrake/contracts/fixtures/make_fixtures.py        # rewrites <family>.jsonl + expected.json here

One file per record family, one line per failure class seen in the reviews. expected.json says, per line, which class
it is, where that class was found, and the decision of three readers:
  old     -- the program's reader as it was before contracts (accept / refuse / skip / crash)
  new     -- the wired reader now (accept / refuse / skip / crash)
  strict  -- the strict contract run in shadow on the line's BYTES (strict JSON, then the pydantic model)
  allow   -- where old and new differ: the id of the one entry in allowances.json that names that difference
contracts.replay runs old and new in two isolated processes (replay_worker.py) and checks every row of this table;
a difference with no `allow`, or one that does not match its allowance exactly, fails the replay.
Families: close_evidence, audits, verdicts, tiers_history, ledger_events, sessions (whole documents),
testq_results (testq.reconcile's collect path) and testq_orphans (testq.drain_outbox's orphan path; same lines).
close_evidence lines are sealed with ce_fixture.key (a fixture key, not a secret: it guards nothing real).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "..", "Utils")
KEY_FILE = os.path.join(HERE, "ce_fixture.key")

A, R, C = "accept", "refuse", "crash"
#: Placeholder for a line nested 200000 deep (400 KB: not committed). load() expands it; json.loads raises
#: RecursionError on it (measured: 100000 deep raises under python 3.14, 50000 does not).
DEEP = "#DEEP#"
DEEP_LINE = "[" * 200000 + "]" * 200000


def load_bytes(family):
    """-> [(raw line bytes, expected-row)] for one family, placeholders expanded. The bytes are what a reader sees."""
    with open(os.path.join(HERE, "expected.json"), encoding="utf-8") as f:
        exp = json.load(f)[family]
    with open(os.path.join(HERE, family + ".jsonl"), "rb") as f:
        raw = f.read().split(b"\n")[:-1]
    assert len(raw) == len(exp), (family, len(raw), len(exp))
    return [(DEEP_LINE.encode() if b == DEEP.encode() else b, e) for b, e in zip(raw, exp)]


def load(family):
    """-> [(line, expected-row)]: load_bytes with each line as str (surrogateescape keeps undecodable bytes)."""
    return [(b.decode("utf-8", "surrogateescape"), e) for b, e in load_bytes(family)]


def _ce_module():
    if not os.path.isfile(KEY_FILE):
        import secrets
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            f.write(secrets.token_hex(32) + "\n")
    os.environ["RM_CLOSE_EVIDENCE_KEY"] = KEY_FILE
    sys.path.insert(0, os.path.abspath(UTILS))
    import close_evidence as CE
    return CE


def close_evidence_lines(CE):
    key = CE._key()
    sha = "0123456789abcdef0123456789abcdef01234567"
    base = {"v": 4, "ts": "2026-10-27T12:00:00+00:00", "nonce": "ab" * 16, "tool": "selftest",
            "clone": "/home/mandrake/rm/bench", "sha": sha, "dirty": False, "dirty_n": 0, "dirty_paths": [],
            "start": {"sha": sha, "dirty": False, "dirty_n": 0}, "paths": ["src/x.py"], "covers": ["src/x.py"],
            "result": "PASS", "item": None, "seat": "BENCH",
            "who": {"agent": "x", "seat": "BENCH", "seat_from": "env", "seat_raw": "BENCH", "session": "s"},
            "origin": {"via": "inproc", "start": "snapshot", "end": "git", "tree": "isolated", "who": "whoami",
                       "pid": 1, "host": "h"},
            "live_only": False, "variant": None, "detail": {}}
    good = json.dumps(CE.seal(base, key))
    fail = json.dumps(CE.seal(dict(base, result="FAIL", nonce="cd" * 16), key))
    dmg = fail.replace(sha, sha[:-1] + "8", 1)     # one hex digit of the sha changed after sealing
    out = []

    def add(line, cls, where, old, new, strict, why="", allow=""):
        out.append({"line": line, "class": cls, "where": where, "old": old, "new": new, "strict": strict, "why": why,
                    "allow": allow})

    add(good, "valid_v4", "baseline", A, A, A)
    add(fail, "valid_v4_fail", "baseline", A, A, A)
    add(good[: len(good) // 2], "torn_line", "review AA8 (torn line blinds 38 days)", R, R, R)
    add(dmg, "damaged_sha", "review AB5 / arbiter_code #1 (damaged FAIL sha)", A, A, A,
        "valid JSON and well-shaped: only close_evidence.mac_ok can refuse it (it does: lookup -> UNMEASURED)")
    add(good, "same_second_replay", "arbiter_code #3 / AD5 (replayed PASS)", A, A, A,
        "an exact duplicate decodes fine; lookup's seen_macs dedupe drops it (nonce makes real repeats distinct)")
    add(json.dumps(dict(json.loads(good), mac="\u00e9")), "non_ascii_mac", "arbiter_code #5 (mac 'e-acute')", A, A, R,
        "the reader accepts the JSON; mac_ok refuses it (AC5); strict refuses mac not 64 hex")
    add(good[:-1] + ', "sha": "%s"}' % ("f" * 40), "duplicate_key", "review AB6 (duplicate top-level key)", A, A, R,
        "json.loads keeps the last value; strict JSON refuses dup_key; lookup's _top_level treats it as ambiguous")
    add(good.replace('"detail": {}', '"detail": {"note": "\ufffd\ufffd"}'), "replacement_char",
        "UTF-8 damage read with errors=replace", A, A, A, "decodes; strict-JSON notes replacement_char; mac fails")
    add(json.dumps({"v": 1, "ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": sha, "result": "PASS"}),
        "legacy_v1", "review Z (v1 never evidence)", A, A, A, "strict reads it as CloseEvidenceLegacy: never evidence")
    add(json.dumps({"v": 2, "ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": sha, "result": "PASS"}),
        "legacy_v2", "review Z", A, A, A, "legacy")
    add(json.dumps({"v": 3, "ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": sha, "result": "PASS"}),
        "legacy_v3", "review AB2 (v3 never evidence)", A, A, A, "legacy")
    add(json.dumps({"ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": sha, "result": "PASS"}),
        "legacy_vless", "review AA5 (v-less legacy hole)", A, A, A, "legacy")
    add(good.replace('"v": 4', '"v": 4.0', 1), "unsupported_version_float", "version confusion", A, A, R,
        "schema_problems: 4.0 == 4 so it looks v4; strict refuses a float version")
    add(good.replace('"v": 4', '"v": 5', 1), "unsupported_version_5", "unsupported version", A, A, R,
        "strict: v5 is neither v4 nor legacy")
    add('[1]', "not_object_list", "non-object JSON", R, R, R)
    add('null', "not_object_null", "non-object JSON", R, R, R)
    add('"text"', "not_object_string", "non-object JSON", R, R, R)
    add(good.replace('"detail": {}', '"detail": {"x": NaN}'), "nonfinite", "NaN in a record", A, A, R,
        "Python json accepts NaN; strict JSON refuses nonfinite (no other JSON reader would parse the line)")
    add(good.replace('"detail": {}', '"detail": {"x": 1e999}'), "nonfinite_overflow", "review contracts #6", A, A, R,
        "1e999 overflows to inf through parse_float, not parse_constant; strict JSON refuses it")
    add(good.replace('"detail": {}', '"detail": {"note": "\udcff"}'), "not_utf8_in_string",
        "review contracts #7 (a raw 0xff inside a string)", A, A, R,
        "the file is read with replacement, so the reader accepts; strict refuses the bytes as not_utf8")
    add(good.replace('"v": 4', '"v": true', 1), "version_bool", "version confusion", A, A, R,
        "a bool v is neither v4 nor a legacy integer version")
    add(json.dumps({"v": 1.0, "ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": sha, "result": "PASS"}),
        "legacy_version_float", "review contracts #10", A, A, R, "Literal[1,2,3] matched 1.0 by equality")
    add(json.dumps({"v": None, "ts": "2026-09-01T00:00:00+00:00", "tool": "t", "sha": sha, "result": "PASS"}),
        "legacy_version_null", "review contracts #10", A, A, R, "an explicit null is not the v-less legacy form")
    add(good.replace("2026-10-27T12:00:00+00:00", "2026-99-99T99:99:99+00:00", 1), "impossible_ts",
        "review contracts #12", A, A, R, "the ISO pattern matched an impossible date")
    add("\ufeff" + good, "bom", "UTF-8 BOM on a line", R, R, R, "json.loads refuses a str starting with a BOM")
    add(DEEP, "too_deep", "absurd nesting", C, R, R,
        "DISAGREEMENT (intended): json.loads raises RecursionError, which read_all did not catch -> the caller "
        "crashed; contracts.jsonl refuses the line as too_deep and counts it like any unreadable line",
        allow="CE_TOO_DEEP")
    add(good.replace('"sha": "%s"' % sha, '"sha": 12345', 1), "sha_wrong_type", "type confusion", A, A, R,
        "schema_problems checks presence, not types; strict refuses an int sha")
    add("", "blank", "blank line", "skip", "skip", "skip")
    add("   ", "whitespace", "blank line", "skip", "skip", "skip")
    return out


def audits_lines():
    L = {"ts": "2026-10-27T00:00:00Z", "item": "X_Y_Z", "sha": "abcdef1", "run": "r1", "why_picked": "random",
         "flags": [], "verdict": "SOUND", "defect_class": None, "evidence": ["D:\\a.txt"]}
    out = []

    def add(d, cls, where, old, new, strict, why="", raw=None, allow=""):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why, "allow": allow})

    add(L, "valid", "baseline", A, A, A)
    add(dict(L, extra_field=1), "extra_field", "additionalProperties true", A, A, A)
    add(dict(L, verdict="DEFECT"), "defect_without_class", "x-conditionals", R, R, R)
    add(dict(L, defect_class="check"), "sound_with_class", "x-conditionals", R, R, R)
    add(dict(L, waiting_for="/x"), "waiting_on_sound", "x-conditionals", R, R, R)
    add(dict(L, sha="HEAD"), "sha_not_hex", "pattern", R, R, R)
    add(dict(L, sha="abcdef1\n"), "sha_trailing_newline", "pattern via re.search", A, A, A,
        "audits.problems used re.search: `$` matches before a final newline, so 'abcdef1\\n' passed; the model keeps "
        "that (compat). Filed as a finding, not changed here")
    add(dict(L, item=""), "empty_item", "minLength", R, R, R)
    add(dict(L, flags=[1]), "flag_not_string", "items.type", R, R, R)
    add(dict(L, verdict=True), "verdict_bool", "enum", R, R, R)
    add(None, "torn", "review AA8 class", R, R, R, raw=json.dumps(L)[:40])
    add(None, "null_list", "dispatcher_full #5 class", R, R, R, raw="[null]")
    add(None, "dup_key", "review AB6 class", A, A, R, raw=json.dumps(L)[:-1] + ', "verdict": "SOUND"}',
        why="json.loads keeps the last value; strict JSON refuses dup_key")
    add(None, "too_deep", "absurd nesting", C, R, R, raw=DEEP, allow="AUDITS_TOO_DEEP",
        why="DISAGREEMENT (intended): RecursionError used to escape parse(); now 'line N is not JSON'")
    add(None, "blank", "blank line", "skip", "skip", "skip", raw="")
    return out


def verdict_lines():
    V = {"item": "X_Y_Z", "sha": "abcdef1", "disposition": "PASS", "causes": [], "interim": None,
         "evidence": ["D:\\ClaudeWork\\rimmandrake\\arbiter\\x.md"], "ts": "2026-10-27T00:00:00Z"}
    out = []

    def add(d, cls, where, old, new, strict, why="", raw=None, allow=""):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why, "allow": allow})

    add(V, "valid", "arbiter.md fields", A, A, A)
    add(dict(V, disposition="FAIL-module", causes=["check"]), "valid_fail_tagged", "arbiter.md", A, A, A)
    add(dict(V, disposition="Pass"), "misspelt_disposition", "read_stores", R, R, R)
    add(dict(V, item=""), "empty_item", "read_jsonl truthy rule", R, R, R)
    add(dict(V, sha="HEAD"), "sha_head", "tiers_history writes sha HEAD", A, A, R,
        "compat only needs a truthy sha; strict needs 7-40 hex: 'HEAD' cannot be joined to a commit")
    add({k: v for k, v in V.items() if k != "causes"}, "missing_causes", "arbiter.md", A, A, R,
        "compat reads item/sha/disposition only; strict needs every arbiter.md field")
    add(dict(V, sha=1234567), "sha_int", "type confusion", A, A, R, "truthy int passes compat; strict refuses")
    add(dict(V, ts="yesterday"), "bad_ts", "digest review #8 (invalid ts)", A, A, R,
        "compat ignores ts; strict needs ISO UTC Z")
    add(dict(V, surplus=1), "extra_field", "closed type", A, A, R, "strict is extra=forbid")
    add(dict(V, evidence=[""]), "evidence_empty_path", "review contracts #13", A, A, R, "an empty evidence path")
    add(dict(V, evidence=["relative.txt"]), "evidence_relative", "review contracts #13", A, A, R,
        "evidence must be absolute Windows paths")
    add(dict(V, ts="2026-99-99T99:99:99Z"), "impossible_ts", "review contracts #12", A, A, R,
        "the ISO pattern matched an impossible date")
    add(None, "dup_disposition", "review contracts #5", A, A, R,
        raw=json.dumps(dict(V, disposition="FAIL-check"))[:-1] + ', "disposition": "PASS"}',
        why="json.loads keeps the LAST disposition (PASS); strict JSON refuses the duplicate key before the model")
    add(None, "null_list", "dispatcher_full #5 class", R, R, R, raw="[null]")
    add(None, "torn", "review AA8 class", R, R, R, raw=json.dumps(V)[:30])
    add(None, "too_deep", "absurd nesting", C, R, R, raw=DEEP, allow="VERDICTS_TOO_DEEP",
        why="DISAGREEMENT (intended): RecursionError used to escape read_jsonl (a crash, not 'unreadable')")
    add(None, "blank", "blank line", "skip", "skip", "skip", raw="")
    return out


def tiers_lines():
    """arbiter_tiers' tiers_history.jsonl through arbiter_pending.read_jsonl(path, item/sha/decision)."""
    T = {"generated": "2026-10-27T00:00:00Z", "item": "X_Y_Z", "sha": "abcdef1", "tier": "T0_PASS",
         "calibration": False, "decision": "PASS"}
    out = []

    def add(d, cls, where, old, new, strict, why="", raw=None, allow=""):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why, "allow": allow})

    add(T, "valid", "arbiter_tiers fields", A, A, A)
    add(dict(T, sha="HEAD"), "sha_head", "TIERS_HISTORY_FIX_SYMBOLIC_HEAD_SHA (4 real rows)", A, A, R,
        "compat needs a truthy sha; strict needs hex")
    add(dict(T, decision=""), "empty_decision", "read_jsonl truthy rule", R, R, R)
    add({k: v for k, v in T.items() if k != "generated"}, "missing_generated", "strict field", A, A, R,
        "compat reads item/sha/decision only")
    add(dict(T, generated="2026-99-99T99:99:99Z"), "impossible_ts", "review contracts #12", A, A, R,
        "the ISO pattern matched an impossible date")
    add(dict(T, tier="T9"), "unknown_tier", "closed enum", A, A, R, "compat ignores tier")
    add(None, "null_list", "non-object JSON", R, R, R, raw="[null]")
    add(None, "torn", "review AA8 class", R, R, R, raw=json.dumps(T)[:30])
    add(None, "too_deep", "absurd nesting", C, R, R, raw=DEEP, allow="TIERS_TOO_DEEP",
        why="DISAGREEMENT (intended): RecursionError used to escape read_jsonl (a crash, not 'unreadable')")
    add(None, "blank", "blank line", "skip", "skip", "skip", raw="")
    return out


def ledger_event_lines():
    E = {"ts": "2026-10-27T12:00:01Z", "seat": "BENCH", "event": "note", "id": "X"}
    # seat_events_since has no refusal: a line is returned (accept), passed over (skip) or kills the tick (crash).
    out = []

    def add(raw, cls, where, old, new, strict, why="", allow=""):
        out.append({"line": raw, "class": cls, "where": where, "old": old, "new": new, "strict": strict, "why": why,
                    "allow": allow})

    add(json.dumps(E), "valid", "baseline", A, A, A)
    add(json.dumps(dict(E, seat="FOUNDRY")), "other_seat", "seat filter", "skip", "skip", A)
    add(json.dumps(dict(E, ts="2026-10-26T00:00:00Z")), "before_cutoff", "since filter", "skip", "skip", A)
    add(b"\xff\xfe not utf-8".decode("latin-1"), "not_utf8", "byte damage in a shard", C, "skip", R,
        "DISAGREEMENT (intended): the shard was opened strict UTF-8; one bad byte raised UnicodeDecodeError out of "
        "the read loop and crashed the tick. Now read with errors=replace and the line is passed over. The fixture "
        "line is written as raw bytes 0xff 0xfe (see main)", allow="LEDGER_NOT_UTF8")
    add("[1]", "not_object", "dispatcher seat_events_since", C, "skip", R,
        "DISAGREEMENT (intended): ev.get on a list raised AttributeError and crashed the dispatcher tick",
        allow="LEDGER_NOT_OBJECT")
    add(json.dumps(dict(E, ts=5)), "ts_int", "type confusion", C, "skip", R,
        "DISAGREEMENT (intended): 5 > str raised TypeError and crashed the tick", allow="LEDGER_TS_TRUTHY_NONSTRING")
    for name, val, st in (("null", None, A), ("zero", 0, R), ("false", False, R), ("empty_list", [], R),
                          ("empty_object", {}, R)):
        add(json.dumps(dict(E, ts=val)), "ts_falsey_" + name, "review contracts #9 (falsey ts)", "skip", "skip", st,
            "`ts or ''` is the operand in BOTH the guard and the comparison (compat.ledger_ts): '' sorts before "
            "every cutoff, so the event is passed over, old and new alike; strict wants a string or null")
    add(DEEP, "too_deep", "absurd nesting", C, "skip", R, allow="LEDGER_TOO_DEEP",
        why="DISAGREEMENT (intended): RecursionError escaped `except ValueError` and crashed the tick")
    add(json.dumps(dict(E, ts="yesterday")), "ts_not_iso", "digest review #8 (invalid ts)", A, A, R,
        "a non-ISO ts string compares lexicographically ('y' > '2'), so it counts as after any cutoff; strict "
        "refuses it. Filed, not changed (decision preserved)")
    add(json.dumps(E)[:25], "torn", "review AA8 class", "skip", "skip", R)
    add("", "blank", "blank line", "skip", "skip", "skip")
    return out


def session_obs():
    """Whole `claude agents --json` documents (one per line here), not records of a stream."""
    good = [{"pid": 1, "cwd": "/home/mandrake/rm/bench", "kind": "interactive", "startedAt": 1761600000000,
             "sessionId": "00000000-0000-0000-0000-000000000001", "name": "AGENT BENCH", "status": "idle"},
            {"id": "bg1", "cwd": "/home/mandrake/rm/bench", "kind": "background", "startedAt": 1761600000000,
             "sessionId": "00000000-0000-0000-0000-000000000002", "name": "helper", "state": "blocked"}]
    out = []

    def add(doc, cls, where, old, new, strict, why=""):
        out.append({"line": doc if isinstance(doc, str) else json.dumps(doc), "class": cls, "where": where,
                    "old": old, "new": new, "strict": strict, "why": why, "allow": ""})

    add(good, "valid", "captured 2026-10-27 shape", A, A, A)
    add([], "empty", "no sessions", A, A, A)
    add([None], "null_entry", "dispatcher_full #5 ([null] observation)", R, R, R)
    add({"sessions": good}, "not_list", "shape drift", R, R, R)
    add([dict(good[0], status=3)], "status_int", "type confusion", A, A, R, "strict: status must be a string")
    add([dict(good[0], name=None)], "unnamed", "find_session by name", A, A, A)
    return out


def testq_results():
    J = "J20261027T120000Z-abcdef"
    r = {"schema": "testq.result/1", "job": J, "attempt": J + ".a1", "host": "stevedesktop", "runner_sha": "abc1234",
         "outcome": "DONE", "cause": None, "deployed": {}, "rows": [{"chain": None, "row": "r", "verdict": "PASS",
                                                                      "validity": None, "freshness": None, "detail": ""}],
         "counts": {"PASS": 1}, "phase_s": {}, "retries": 0, "modcheck_exit": 0, "artifacts": [],
         "started": "2026-10-27T12:00:00Z", "finished": "2026-10-27T12:10:00Z", "note": ""}
    out = []

    def add(d, cls, where, old, new, strict, why="", raw=None, allow=""):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why, "allow": allow})

    # expected decisions: (reconcile collect path, drain_outbox orphan path, strict)
    def both(d, cls, where, rec, orph, strict, why="", raw=None, allow=""):
        add(d, cls, where, rec[0], rec[1], strict, why, raw)
        out[-1]["orphans"] = {"old": orph[0], "new": orph[1], "allow": allow}

    both(r, "valid", "baseline", (A, A), (A, A), A)
    both(dict(r, moot_markers=["c1"], bounced_for_markers=["c1"]), "undeclared_markers",
         "worker writes fields testq_schema.json lacks", (A, A), (A, A), A,
         "declared in the strict model; schema drift filed")
    both({"schema": "testq.result/1", "rows": []}, "rows_only", "GPT design: schema-tag-only check", (C, C), (A, A),
         R, "reconcile checks only the schema tag, then reads res['outcome'] (KeyError, old and new: "
         "TESTQ_OUTCOME_HARDEN_TAG_ONLY_KEYERROR); drain_outbox keeps it in orphans/ on the tag alone")
    both(dict(r, outcome="INVALID"), "invalid_without_cause", "validate_result rule", (A, A), (A, A), R,
         "compat reads the tag only")
    both(dict(r, surplus=1), "extra_field", "closed type", (A, A), (A, A), R, "strict is extra=forbid")
    both(dict(r, attempt=r["job"] + ".aanything"), "attempt_malformed", "review contracts #11", (A, A), (A, A), R,
         "the strict attempt rule is <job>.a<n>")
    both(dict(r, schema="testq.result/2"), "unsupported_version", "unsupported version", (R, R), (R, R), R)
    both(None, "torn", "truncated worker line", (R, R), (R, R), R, raw=json.dumps(r)[:50])
    both(None, "not_object", "non-object JSON", (C, C), (C, R), R,
         "reconcile: old res.get('schema') and new res.get('error') (the unreadable log) BOTH raise AttributeError on "
         "a JSON list -- same decision, filed as TESTQ_HARDEN_RECONCILE_NONDICT_CRASH. drain_outbox: "
         "DISAGREEMENT (intended): old crashed, new leaves it in the worker outbox unkept",
         raw="[null]", allow="TESTQ_ORPHANS_NOT_OBJECT")
    return out


def main():
    CE = _ce_module()
    tq = testq_results()
    orph = [dict(r, old=r["orphans"]["old"], new=r["orphans"]["new"], allow=r["orphans"]["allow"]) for r in tq]
    for r in tq + orph:
        r.pop("orphans", None)
    fams = {"close_evidence": close_evidence_lines(CE), "audits": audits_lines(), "verdicts": verdict_lines(),
            "tiers_history": tiers_lines(), "ledger_events": ledger_event_lines(), "sessions": session_obs(),
            "testq_results": tq, "testq_orphans": orph}
    expected = {}
    for fam, rows in fams.items():
        with open(os.path.join(HERE, fam + ".jsonl"), "wb") as f:
            for r in rows:
                raw = (r["line"].encode("latin-1") if r["class"] == "not_utf8" else
                       r["line"].encode("utf-8", "surrogateescape"))
                f.write(raw + b"\n")
        expected[fam] = [{k: v for k, v in r.items() if k != "line"} for r in rows]
    with open(os.path.join(HERE, "expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=1)
        f.write("\n")
    print("wrote %s" % ", ".join("%s %d" % (k, len(v)) for k, v in fams.items()))


if __name__ == "__main__":
    main()
