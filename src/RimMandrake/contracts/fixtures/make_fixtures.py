#!/usr/bin/env python3
"""Regenerate the malformed-record fixture corpus (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS step 0).

    python3 src/RimMandrake/contracts/fixtures/make_fixtures.py        # rewrites <family>.jsonl + expected.json here

One file per record family, one line per failure class seen in the reviews. expected.json says, per line, which class
it is, where that class was found, and the decision of three readers:
  old     -- the program's reader as it was before contracts (accept / refuse / crash)
  new     -- the wired reader now (accept / refuse); differs from old only where the `why` says so
  strict  -- the strict pydantic contract run in shadow (accept / refuse)
selftest_contracts checks every one of those against the real readers; contracts.replay reports the same table.
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


def load(family):
    """-> [(line, expected-row)] for one family, placeholders expanded."""
    with open(os.path.join(HERE, "expected.json"), encoding="utf-8") as f:
        exp = json.load(f)[family]
    with open(os.path.join(HERE, family + ".jsonl"), "rb") as f:
        raw = f.read().split(b"\n")[:-1]
    lines = [b.decode("utf-8", "surrogateescape") for b in raw]
    assert len(lines) == len(exp), (family, len(lines), len(exp))
    return [(DEEP_LINE if ln == DEEP else ln, e) for ln, e in zip(lines, exp)]


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

    def add(line, cls, where, old, new, strict, why=""):
        out.append({"line": line, "class": cls, "where": where, "old": old, "new": new, "strict": strict, "why": why})

    add(good, "valid_v4", "baseline", A, A, A)
    add(fail, "valid_v4_fail", "baseline", A, A, A)
    add(good[: len(good) // 2], "torn_line", "review AA8 (torn line blinds 38 days)", R, R, R)
    add(dmg, "damaged_sha", "review AB5 / arbiter_code #1 (damaged FAIL sha)", A, A, A,
        "valid JSON and well-shaped: only close_evidence.mac_ok can refuse it (it does: lookup -> UNMEASURED)")
    add(good, "same_second_replay", "arbiter_code #3 / AD5 (replayed PASS)", A, A, A,
        "an exact duplicate decodes fine; lookup's seen_macs dedupe drops it (nonce makes real repeats distinct)")
    add(json.dumps(dict(json.loads(good), mac="\u00e9")), "non_ascii_mac", "arbiter_code #5 (mac 'e-acute')", A, A, R,
        "the reader accepts the JSON; mac_ok refuses it (AC5); strict refuses mac not 64 hex")
    add(good[:-1] + ', "sha": "%s"}' % ("f" * 40), "duplicate_key", "review AB6 (duplicate top-level key)", A, A, A,
        "json.loads keeps the last value; strict-JSON notes dup_key; lookup's _top_level treats it as ambiguous")
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
    add(good.replace('"detail": {}', '"detail": {"x": NaN}'), "nonfinite", "NaN in a record", A, A, A,
        "Python json accepts NaN; strict-JSON notes nonfinite (no other JSON reader would parse the line)")
    add("\ufeff" + good, "bom", "UTF-8 BOM on a line", R, R, R, "json.loads refuses a str starting with a BOM")
    add(DEEP, "too_deep", "absurd nesting", C, R, R,
        "DISAGREEMENT (intended): json.loads raises RecursionError, which read_all did not catch -> the caller "
        "crashed; contracts.jsonl refuses the line as too_deep and counts it like any unreadable line")
    add(good.replace('"sha": "%s"' % sha, '"sha": 12345', 1), "sha_wrong_type", "type confusion", A, A, R,
        "schema_problems checks presence, not types; strict refuses an int sha")
    add("", "blank", "blank line", "skip", "skip", "skip")
    add("   ", "whitespace", "blank line", "skip", "skip", "skip")
    return out


def audits_lines():
    L = {"ts": "2026-10-27T00:00:00Z", "item": "X_Y_Z", "sha": "abcdef1", "run": "r1", "why_picked": "random",
         "flags": [], "verdict": "SOUND", "defect_class": None, "evidence": ["D:\\a.txt"]}
    out = []

    def add(d, cls, where, old, new, strict, why="", raw=None):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why})

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
    add(None, "dup_key", "review AB6 class", A, A, A, raw=json.dumps(L)[:-1] + ', "verdict": "SOUND"}',
        why="json.loads keeps the last value; strict-JSON notes dup_key")
    add(None, "too_deep", "absurd nesting", C, R, R, raw=DEEP,
        why="DISAGREEMENT (intended): RecursionError used to escape parse(); now 'line N is not JSON'")
    add(None, "blank", "blank line", "skip", "skip", "skip", raw="")
    return out


def verdict_lines():
    V = {"item": "X_Y_Z", "sha": "abcdef1", "disposition": "PASS", "causes": [], "interim": None,
         "evidence": ["D:\\ClaudeWork\\rimmandrake\\arbiter\\x.md"], "ts": "2026-10-27T00:00:00Z"}
    out = []

    def add(d, cls, where, old, new, strict, why="", raw=None):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why})

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
    add(None, "null_list", "dispatcher_full #5 class", R, R, R, raw="[null]")
    add(None, "torn", "review AA8 class", R, R, R, raw=json.dumps(V)[:30])
    add(None, "too_deep", "absurd nesting", C, R, R, raw=DEEP,
        why="DISAGREEMENT (intended): RecursionError used to escape read_jsonl (a crash, not 'unreadable')")
    return out


def ledger_event_lines():
    E = {"ts": "2026-10-27T12:00:01Z", "seat": "BENCH", "event": "note", "id": "X"}
    # seat_events_since has no refusal: a line is returned (accept), passed over (skip) or kills the tick (crash).
    out = []

    def add(raw, cls, where, old, new, strict, why=""):
        out.append({"line": raw, "class": cls, "where": where, "old": old, "new": new, "strict": strict, "why": why})

    add(json.dumps(E), "valid", "baseline", A, A, A)
    add(json.dumps(dict(E, seat="FOUNDRY")), "other_seat", "seat filter", "skip", "skip", A)
    add(json.dumps(dict(E, ts="2026-10-26T00:00:00Z")), "before_cutoff", "since filter", "skip", "skip", A)
    add(b"\xff\xfe not utf-8".decode("latin-1"), "not_utf8", "byte damage in a shard", C, "skip", R,
        "DISAGREEMENT (intended): the shard was opened strict UTF-8; one bad byte raised UnicodeDecodeError out of "
        "the read loop and crashed the tick. Now read with errors=replace and the line is passed over. The fixture "
        "line is written as raw bytes 0xff 0xfe (see main)")
    add("[1]", "not_object", "dispatcher seat_events_since", C, "skip", R,
        "DISAGREEMENT (intended): ev.get on a list raised AttributeError and crashed the dispatcher tick")
    add(json.dumps(dict(E, ts=5)), "ts_int", "type confusion", C, "skip", R,
        "DISAGREEMENT (intended): 5 > str raised TypeError and crashed the tick")
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
                    "old": old, "new": new, "strict": strict, "why": why})

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

    def add(d, cls, where, old, new, strict, why="", raw=None):
        out.append({"line": raw if raw is not None else json.dumps(d), "class": cls, "where": where, "old": old,
                    "new": new, "strict": strict, "why": why})

    add(r, "valid", "baseline", A, A, A)
    add(dict(r, moot_markers=["c1"], bounced_for_markers=["c1"]), "undeclared_markers",
        "worker writes fields testq_schema.json lacks", A, A, A, "declared in the strict model; schema drift filed")
    add({"schema": "testq.result/1", "rows": []}, "rows_only", "GPT design: schema-tag-only check", A, A, R,
        "testq.py checks only the schema tag, then reads res['outcome'] (KeyError); strict and validate_result "
        "refuse; testq.py now logs the shadow refusal")
    add(dict(r, outcome="INVALID"), "invalid_without_cause", "validate_result rule", A, A, R,
        "compat reads the tag only")
    add(dict(r, surplus=1), "extra_field", "closed type", A, A, R, "strict is extra=forbid")
    add(dict(r, schema="testq.result/2"), "unsupported_version", "unsupported version", R, R, R)
    add(None, "torn", "truncated file", R, R, R, raw=json.dumps(r)[:50])
    add(None, "not_object", "non-object JSON", C, R, R,
        "DISAGREEMENT (intended): testq.py at base did res.get('schema') on whatever read_json returned; a JSON list "
        "in done/ raised AttributeError and stopped collect/orphans. compat.testq_result_readable refuses it",
        raw="[null]")
    return out


def main():
    CE = _ce_module()
    fams = {"close_evidence": close_evidence_lines(CE), "audits": audits_lines(), "verdicts": verdict_lines(),
            "ledger_events": ledger_event_lines(), "sessions": session_obs(), "testq_results": testq_results()}
    expected = {}
    for fam, rows in fams.items():
        with open(os.path.join(HERE, fam + ".jsonl"), "wb") as f:
            for r in rows:
                raw = r["line"].encode("latin-1") if r["class"] == "not_utf8" else r["line"].encode("utf-8")
                f.write(raw + b"\n")
        expected[fam] = [{k: v for k, v in r.items() if k != "line"} for r in rows]
    with open(os.path.join(HERE, "expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=1)
        f.write("\n")
    print("wrote %s" % ", ".join("%s %d" % (k, len(v)) for k, v in fams.items()))


if __name__ == "__main__":
    main()
