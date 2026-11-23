#!/usr/bin/env python3
"""selftest_follow_through.py - the weekly follow-through audit (follow_through.py).

Item RIMMANDRAKE_BUILD_FOLLOW_THROUGH_AUDIT_LOWER_RATE_IS_HEADLINE; page design/specs/2026-11-23-follow-through-audit/
boundary.md (each t_ function is one promise of it, by the same name). Offline: fake worlds and events, a scratch
record root (RM_FOLLOW_THROUGH_ROOT), scratch transcripts, a scratch reading. No ledger write, no launch, no model.
Written before the module; seen failing on the base (follow_through.py absent).
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "rimflow"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"

FAILS = []
X = {}
NOW = 1795600000.0          # 2026-11-24 PST, a fixed clock
DAY = 86400.0


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class It(object):
    def __init__(self, iid, state="ready", kind="task", owner="BENCH", created=None, wait=None, title="t"):
        self.id, self.state, self.kind, self.owner, self.title = iid, state, kind, owner, title
        self.created_at = created
        self.wait_until, self.wait_reason = wait, ("why" if wait else None)
        self.blocked, self.blocked_reason, self.caused_by = False, None, None

    @property
    def open(self):
        return self.state not in ("done", "dropped", "superseded")


class World(object):
    def __init__(self, *items):
        self.items = {i.id: i for i in items}


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def F():
    import follow_through
    return follow_through


# ---- one test per promise ---------------------------------------------------------------------------------------

def t_sample_draws_n_the_same_for_a_seed_and_keeps_none():
    s = F().sample({"a": list(range(50)), "b": [1, 2], "c": None}, 20, "x")
    chk(len(s["a"]) == 20 and len(set(s["a"])) == 20, "20 of 50, none twice")
    chk(s["b"] == [1, 2], "a stream shorter than n is drawn whole")
    chk(s["c"] is None, "a stream that could not be read stays None")
    chk(F().sample({"a": list(range(50))}, 20, "x") == {"a": s["a"]}, "the same seed, the same draw")
    chk(F().sample({"a": list(range(50))}, 20, "y")["a"] != s["a"], "another seed, another draw")
    chk(F().sample({"a": []}, 20, "x")["a"] == [], "an empty stream is [] (looked, none), not None")


def t_rates_count_outcome_and_disposed_and_the_headline_is_the_lower():
    r = F().rates({"talk": ["outcome", "disposed", "moved", "nothing", "not_a_need"], "pipe": ["outcome", "moved"]})
    chk(r["by_stream"]["talk"] == 0.5, "outcome+disposed of four counted; not_a_need leaves the count")
    chk(r["headline"] == 0.5 and r["unmeasured"] == [], "headline is the lower rate")
    r = F().rates({"talk": ["moved"], "pipe": ["outcome"]})
    chk(r["headline"] == 0.0 and r["by_stream"]["talk"] == 0.0, "a judged stream with none followed is 0.0")


def t_rates_keep_no_verdicts_apart_from_zero():
    r = F().rates({"talk": ["not_a_need"], "pipe": ["outcome"]})
    chk(r["by_stream"]["talk"] is None and r["unmeasured"] == ["talk"] and r["headline"] is None,
        "only not_a_need is unmeasured, and the headline waits")
    r = F().rates({"talk": None, "pipe": []})
    chk(r["unmeasured"] == ["talk", "pipe"] and r["headline"] is None, "None and [] are both unmeasured")
    chk(F().rates({})["headline"] is None, "no stream: headline None")


def t_rates_refuse_an_unknown_verdict():
    for bad in ("done", None, "Outcome"):
        try:
            F().rates({"talk": ["outcome", bad]})
            chk(False, "verdict %r refused" % (bad,))
        except ValueError as e:
            chk(repr(bad) in str(e) and "not_a_need" in str(e), "verdict %r refused by name, with the five" % (bad,))


def t_hands_off_reads_closed_items_only_and_none_is_never_a_guess():
    h = F().hands_off
    chk(h([{"closed": True, "window_acts": 0}, {"closed": True, "window_acts": 3}, {"closed": False, "window_acts": 0}])
        == {"share": 0.5, "closed": 2, "hands_off": 1}, "open item not counted")
    chk(h([])["share"] is None and h([])["closed"] == 0, "no closed item: None, closed 0")
    chk(h([{"closed": True, "window_acts": None}, {"closed": True, "window_acts": 0}])["share"] is None,
        "an unreadable count makes the share None")


def t_window_act_is_an_event_by_the_conductors_hands():
    w = F().window_act
    chk(w({"seat": "BENCH"}) is True and w({"seat": "CONDUCTOR"}) is True, "window seats")
    chk(w({"seat": "OWNER", "ranBy": "BENCH"}) is True and w({"seat": "OWNER", "ranBy": "AGENT"}) is True,
        "his authority, the window's hands (or its subagent's)")
    chk(w({"seat": "BENCH", "role_unit": "rm-detached-x"}) is False, "a launched run is not the window")
    chk(w({"seat": "OWNER"}) is False, "OWNER with no ranBy is his own hands")
    chk(w({"seat": "RUNNER"}) is False and w({"seat": "DISPATCHER"}) is False, "other seats")
    chk(w({"event": "note"}) is None, "no seat: could not read")


def t_the_week_is_seven_days_before_the_date_pacific():
    lo, hi = F().week("2026-11-29")
    chk(iso(hi) == "2026-11-29T08:00:00Z" and iso(lo) == "2026-11-22T08:00:00Z", "00:00 PST, seven days")
    for bad in ("2026-11-29T00", "11/29/2026", None, ""):
        try:
            F().week(bad)
            chk(False, "week(%r) refused" % (bad,))
        except ValueError:
            chk(True, "week(%r) refused" % (bad,))
    chk(F().latest_sunday(F().week("2026-11-30")[1] + 3600) == "2026-11-29", "a Monday's latest Sunday")
    chk(F().latest_sunday(F().week("2026-11-29")[1] + 3600) == "2026-11-29", "a Sunday is its own latest Sunday")


def t_pipe_stream_is_the_first_left_open_per_item_in_the_week():
    lo, hi = 1000.0, 2000.0
    ev = [{"event": "note", "id": "A", "_ts": 1100, "text": "LEFT OPEN: the live half"},
          {"event": "note", "id": "A", "_ts": 1200, "text": "LEFT OPEN: still the live half"},
          {"event": "note", "id": "B", "_ts": 1300, "text": "**Left open:** a second run"},
          {"event": "note", "id": "C", "_ts": 1400, "text": "Closed with no `LEFT OPEN:` note left"},
          {"event": "note", "id": "D", "_ts": 900, "text": "LEFT OPEN: before the week"},
          {"event": "note", "id": "E", "_ts": 2000, "text": "LEFT OPEN: at the week's end, the next week's"},
          {"event": "close", "id": "F", "_ts": 1500, "text": "LEFT OPEN: not a note"}]
    n = F().pipe_needs(ev, lo, hi)
    chk([x["item"] for x in n] == ["A", "B"], "one per item, first in the week, emphasis allowed, mentions not")
    chk(n[0]["text"] == "LEFT OPEN: the live half", "the first note is the need")


def _transcript(d, recs):
    p = os.path.join(d, "t%d.jsonl" % len(os.listdir(d)))
    with open(p, "w") as f:
        for i, (t, text) in enumerate(recs):
            f.write(json.dumps({"type": "user", "uuid": "u%d-%s" % (i, p), "timestamp": iso(t), "origin": {"kind": "human"},
                                "promptSource": "typed", "message": {"role": "user", "content": text}}) + "\n")
    return p


def t_talk_stream_is_none_when_it_cannot_be_read_and_drops_machine_text():
    tf = F().talk_needs
    d = tempfile.mkdtemp(dir=X["top"])
    lo, hi = NOW - 7 * DAY, NOW
    n, c, _ = tf(lo, hi, cfg={})
    chk(n is None and "Conductor seat" in c, "no Conductor seat configured: None, said")
    n, c, _ = tf(lo, hi, cfg={"session_name": "CONDUCTOR"}, now_paths=[])
    chk(n is None and "no transcript" in c, "no transcript in the week: None, said")
    n, c, _ = tf(lo, hi, cfg={"session_name": "CONDUCTOR"}, now_paths=[os.path.join(d, "gone.jsonl")])
    chk(n is None and "could be read" in c, "no transcript readable: None, said")
    p = _transcript(d, [(NOW - 2 * DAY, "please fix the drawbridge art today"),
                        (NOW - 1 * DAY, "wake. Fresh CONDUCTOR window after a restart"),
                        (NOW - 8 * DAY, "before the week")])
    n, c, notes = tf(lo, hi, cfg={"session_name": "CONDUCTOR"}, now_paths=[p])
    chk(c is None and [x["text"] for x in n] == ["please fix the drawbridge art today"],
        "his typing kept; machine text and out-of-week dropped")
    chk(any("machine text" in s for s in notes), "the machine text is counted in a note")
    p2 = _transcript(d, [(NOW - 9 * DAY, "only old words")])
    n, c, _ = tf(lo, hi, cfg={"session_name": "CONDUCTOR"}, now_paths=[p2])
    chk(n == [] and c is None, "read, nothing typed in the week: [], not None")


def t_beside_numbers_read_the_ledger_and_say_unmeasured_when_blind():
    w = World(It("OLD", kind="owed", created=iso(NOW - 3 * DAY)),
              It("YOUNG", kind="owed", created=iso(NOW - 2 * 3600)),
              It("WAITED", kind="owed", created=iso(NOW - 5 * DAY), wait=iso(NOW - 3 * 3600)),
              It("CLOSED", kind="owed", state="done", created=iso(NOW - 9 * DAY)),
              It("OTHER", kind="owed", owner="RUNNER", created=iso(NOW - 9 * DAY)),
              It("W1", wait=iso(NOW - 2 * DAY)), It("W2", wait=iso(NOW - 2 * DAY)), It("W3", wait=iso(NOW + DAY)))
    d = F().debts(w, NOW)
    chk(d.get("count") == 1 and d["rows"][0]["id"] == "OLD", "only the Conductor's open debt ripe over a day")
    chk("unmeasured" in F().debts(object(), NOW), "a world that cannot be read: UNMEASURED, never 0")
    ev = [{"event": "note", "id": "W2", "_ts": NOW - DAY, "seat": "BENCH"}]
    wp = F().waits_past(w, ev, NOW)
    chk(wp["count"] == 2 and wp["of"] == 4 and sorted(r["id"] for r in wp["rows"]) == ["W1", "WAITED"],
        "past their date with no event since (W2 was looked at; W3 is ahead)")
    h = F().homeless([], NOW, cfg={"session_name": "CONDUCTOR"}, now_paths=[])
    chk("unmeasured" in h and "count" not in h, "no transcript: homeless UNMEASURED, never 0")
    dd = tempfile.mkdtemp(dir=X["top"])
    p = _transcript(dd, [(NOW - DAY, "move the pump art to the left please now"),
                         (NOW - DAY + 60, "write the drawbridge page for me tonight please")])
    said = [{"event": "note", "seat": "OWNER", "_ts": NOW - DAY + 30, "ownerSaid": "move the pump art to the left please now"}]
    h = F().homeless(said, NOW, cfg={"session_name": "CONDUCTOR"}, now_paths=[p])
    chk(h.get("count") == 1 and h["of"] == 2 and "drawbridge" in h["rows"][0]["text"], "a quoted message has a home")


def _rec(date="2026-11-29", talk=("t1", "t2"), pipe=("p1",)):
    return {"week_ending": date, "week": ["a", "b"], "read_at": "c", "seed": F().seed_of(date), "n": 20,
            "streams": {"talk": None if talk is None else [{"id": i, "when": "w", "text": "x\ny", "verdict": None,
                                                            "evidence": ""} for i in talk],
                        "pipe": [{"id": i, "when": "w", "text": "z", "verdict": None, "evidence": ""} for i in pipe]},
            "sizes": {"talk": None if talk is None else len(talk), "pipe": len(pipe)},
            "unreadable": {} if talk is not None else {"talk": "no transcript of a CONDUCTOR window"},
            "notes": {}, "load": {"acts": 3, "unreadable": 0}, "hands_off": {"share": None, "closed": 0, "hands_off": 0},
            "closed_items": [], "debts": {"count": 0, "rows": []}, "waits": {"count": 0, "of": 0, "rows": []},
            "homeless": {"unmeasured": "no transcript"}, "planted": {"id": "P", "unmeasured": "not filed"},
            "rates": None}


def _main(*argv):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = F().main(list(argv))
    return rc, buf.getvalue()


def t_sample_write_never_overwrites_verdicts():
    rec = _rec()
    rec["streams"]["talk"][0]["verdict"] = "outcome"
    p = F().record_path("2026-11-29")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(rec, f)
    rc, out = _main("sample", "--week-ending", "2026-11-29", "--write")
    chk(rc == 3 and "already holds verdicts" in out and p in out, "refused, names the record")
    chk(json.load(open(p))["streams"]["talk"][0]["verdict"] == "outcome", "the verdict is still there")
    os.remove(p)
    saved = F().draw
    try:
        F().draw = lambda date: _rec(date)
        rc, out = _main("sample", "--week-ending", "2026-11-29", "--write")
        chk(rc == 0 and os.path.exists(p) and os.path.exists(F().page_path("2026-11-29")), "a fresh record is written")
        rc, out = _main("sample", "--week-ending", "2026-11-29", "--write")
        chk(rc == 0, "a record with no verdict may be drawn again")
    finally:
        F().draw = saved
        os.remove(p)


def t_judged_holds_only_when_every_need_has_a_verdict_evidence_and_the_page_has_rates():
    j, date = F().judged, "2026-12-06"
    rc, text = j(date)
    chk(rc == 1 and "no record" in text, "no record yet: fails, with the command that passes")
    p = F().record_path(date)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write("{torn")
    chk(j(date)[0] == 2, "a record that cannot be read: 2")
    rec = _rec(date)
    rec["streams"]["talk"][0].update(verdict="outcome", evidence="abc1234")
    with open(p, "w") as f:
        json.dump(rec, f)
    rc, text = j(date)
    chk(rc == 1 and "lack a verdict" in text and "t2" in text, "a need with no verdict: fails, named")
    for x in rec["streams"]["talk"] + rec["streams"]["pipe"]:
        x.update(verdict="moved", evidence="BENCH:1")
    rec["streams"]["pipe"][0]["evidence"] = "  "
    with open(p, "w") as f:
        json.dump(rec, f)
    rc, text = j(date)
    chk(rc == 1 and "p1" in text, "a verdict with no evidence line: fails, named")
    rec["streams"]["pipe"][0]["evidence"] = "BENCH:1"
    with open(p, "w") as f:
        json.dump(rec, f)
    rc, text = j(date)
    chk(rc == 1 and "rates" in text, "every verdict but no rates: fails")
    rc, _ = _main("rates", "--week-ending", date, "--write")
    rc2, text = j(date)
    chk(rc == 0 and rc2 == 0 and "0%" in text, "after rates --write: holds (headline 0%)")
    with open(F().page_path(date), "a") as f:
        f.write("edited by hand\n")
    chk(j(date)[0] == 1, "a page that is not the record's: fails")
    rec = json.load(open(p))
    rec["streams"]["pipe"][0]["verdict"] = "done"
    with open(p, "w") as f:
        json.dump(rec, f)
    chk(j(date)[0] == 1, "an unknown verdict: fails")


def t_the_page_says_unmeasured_for_each_stream_it_could_not_read():
    rec = _rec(talk=None)
    page = F().render(rec)
    chk("UNMEASURED: no transcript of a CONDUCTOR window" in page, "the unread stream names its cause")
    chk("Headline (the lower rate)**: UNMEASURED (not judged yet)" in page, "an unjudged headline says so")
    chk(" 0%" not in page, "no 0% anywhere while nothing is judged")
    rec = _rec()
    for x in rec["streams"]["talk"]:
        x.update(verdict="not_a_need", evidence="e")
    rec["streams"]["pipe"][0].update(verdict="outcome", evidence="e")
    rec["rates"] = F().rates(F().judged_lists(rec))
    page = F().render(rec)
    chk("UNMEASURED (no drawn need was a need)" in page and "100%" in page and "Unmeasured streams: talk" in page,
        "a stream with only not_a_need is unmeasured, not 0")


def t_tick_files_once_launches_the_reader_once_and_is_dry_by_default():
    date = "2026-11-29"
    rp = os.path.join(X["top"], "reading.json")
    calls = []

    def cli(args, apply):
        calls.append((args[0], args[1], apply))
        return 0, "ok"

    def launch(d, rid, apply):
        calls.append(("launch", rid, apply))
        return 0, "launched"

    base = dict(cli=cli, launch=launch, reading_path=rp, gate=None, runs={"n": 0, "live": []})
    r = F().tick(apply=False, date=date, now=NOW, fx=dict(base, world=World()))
    chk([c[2] for c in calls] == [False, False, False] and [x["action"] for x in r["actions"]] ==
        ["plant", "file_reader", "launch"], "dry: the same plan, every call told apply=False")
    chk(F()._cli(["file", "X"], False)[1].startswith("would run") and
        F().launch(date, "X", False)[1].startswith("would launch"), "the real writers do nothing when dry")
    chk(json.load(open(rp))["apply"] is False, "the dry beat writes its reading")
    del calls[:]
    F().tick(apply=True, date=date, now=NOW, fx=dict(base, world=World()))
    chk([(c[0], c[2]) for c in calls] == [("file", True), ("file", True), ("launch", True)] and
        calls[0][1] == F().planted_id("2026-12-06") and calls[1][1] == F().reader_id(date),
        "apply: plant next week's need, file this week's reader, launch")
    filed = World(It(F().planted_id("2026-12-06")), It(F().reader_id(date)))
    for runs, want in (({"n": 1, "live": []}, "reader_ran"), ({"n": 1, "live": ["u"]}, "reader_live"),
                       ({"n": None, "live": None}, "blind")):
        del calls[:]
        r = F().tick(apply=True, date=date, now=NOW, fx=dict(base, world=filed, runs=runs))
        chk(calls == [] and [x["action"] for x in r["actions"]] == [want], "second beat: nothing again (%s)" % want)
    del calls[:]
    r = F().tick(apply=True, date=date, now=NOW, fx=dict(base, world=filed, gate="the pipeline is paused"))
    chk(calls == [] and r["actions"][0]["action"] == "held", "a gate holds the launch")
    done = World(It(F().planted_id("2026-12-06")), It(F().reader_id(date), state="done"))
    r = F().tick(apply=True, date=date, now=NOW, fx=dict(base, world=done))
    chk([x["action"] for x in r["actions"]] == ["reader_done"], "a closed reader item: nothing")
    del calls[:]
    r = F().tick(apply=True, date="2026-11-22", now=NOW, fx=dict(base, world=World()))
    chk(calls == [] and [x["action"] for x in r["actions"]] == ["not_yet"], "before FIRST_WEEK: nothing")


def t_the_planted_need_is_read_from_outside():
    pid = "P"
    chk(F().planted_reading(World(), [], pid) == {"id": pid, "unmeasured": "not filed"}, "not filed: UNMEASURED")
    ev = [{"event": "file", "id": pid, "_ts": 1000.0, "seat": "BENCH", "role_unit": "rm-follow-through.service"},
          {"event": "claim", "id": pid, "_ts": 2000.0, "seat": "BENCH", "role_unit": "rm-detached-x"},
          {"event": "close", "id": pid, "_ts": 1000.0 + 7200, "seat": "BENCH", "role_unit": "rm-detached-x"}]
    r = F().planted_reading(World(It(pid, state="done")), ev, pid, runs=1)
    chk(r["state"] == "done" and r["window_acts"] == 0 and r["runs"] == 1 and r["closed_by"] == "rm-detached-x"
        and r["hours"] == 2.0, "closed by a run after 2 h with no window act")
    ev.insert(2, {"event": "note", "id": pid, "_ts": 3000.0, "seat": "BENCH"})
    r = F().planted_reading(World(It(pid, state="done")), ev, pid, runs=1)
    chk(r["window_acts"] == 1, "a window note counts as an act")
    r = F().planted_reading(World(It(pid, state="ready")), ev[:2], pid, runs=0)
    chk(r["state"] == "ready" and "closed" not in r, "open: no close time")




def main():
    top = tempfile.mkdtemp(prefix="selftest_follow_through_")
    X["top"] = top
    saved = {k: os.environ.get(k) for k in ("RM_FOLLOW_THROUGH_ROOT", "RM_FOLLOW_THROUGH_DIR")}
    os.environ["RM_FOLLOW_THROUGH_ROOT"] = os.path.join(top, "root")
    os.environ["RM_FOLLOW_THROUGH_DIR"] = os.path.join(top, "state")
    try:
        for t in (t_sample_draws_n_the_same_for_a_seed_and_keeps_none,
                  t_rates_count_outcome_and_disposed_and_the_headline_is_the_lower,
                  t_rates_keep_no_verdicts_apart_from_zero,
                  t_rates_refuse_an_unknown_verdict,
                  t_hands_off_reads_closed_items_only_and_none_is_never_a_guess,
                  t_window_act_is_an_event_by_the_conductors_hands,
                  t_the_week_is_seven_days_before_the_date_pacific,
                  t_pipe_stream_is_the_first_left_open_per_item_in_the_week,
                  t_talk_stream_is_none_when_it_cannot_be_read_and_drops_machine_text,
                  t_beside_numbers_read_the_ledger_and_say_unmeasured_when_blind,
                  t_sample_write_never_overwrites_verdicts,
                  t_judged_holds_only_when_every_need_has_a_verdict_evidence_and_the_page_has_rates,
                  t_the_page_says_unmeasured_for_each_stream_it_could_not_read,
                  t_tick_files_once_launches_the_reader_once_and_is_dry_by_default,
                  t_the_planted_need_is_read_from_outside):
            print("-- " + t.__name__[2:])
            try:
                t()
            except Exception as e:  # noqa: BLE001
                chk(False, "%s (raised %s: %s)" % (t.__name__, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(top, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
