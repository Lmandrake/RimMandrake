#!/usr/bin/env python3
"""Selftest for the mission page (MISSION_PAGE_BUILD_READ_ONLY_STATE): planted faults through the real CLI and the real
brief.page route, on a fixture mod with a repo's shape. A healthy fixture must read MET first, so a page that says
UNMEASURED to everything fails here; then each fault must take the row off PROVEN. The whole fixture tree is
snapshotted around each read: the page writes itself and nothing else. The last check renders a real mod and holds the
real tree to the same promise.
"""
import atexit
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.dont_write_bytecode = True
BASE = Path(tempfile.mkdtemp(prefix="st_mission_page_"))
atexit.register(shutil.rmtree, BASE, True)
os.environ["TMPDIR"] = tempfile.tempdir = str(BASE / "tmp")
(BASE / "tmp").mkdir()
ROOT = BASE / "root"
ENV = {"RM_MISSION_ROOT": str(ROOT), "RM_MISSION_LEDGER": str(BASE / "ledger.jsonl"), "RM_PULSE_STATE": str(BASE / "pulse"),
       "RELENTLESS_ROOT": str(BASE / "rel"), "RM_OPS_WATCH_DIR": str(BASE / "ops"), "RM_TIME_LEDGER": str(BASE / "time.json")}
os.environ.update(ENV)
(BASE / "pulse").mkdir()
sys.path.insert(0, str(HERE))
import brief          # noqa: E402
import mission_page   # noqa: E402

MOD = "Fixtmod"
MOD_DIR = ROOT / "src" / "RimMandrake" / MOD
WALK = ROOT / "design" / "validation_walks" / "RimMandrake" / f"{MOD}.md"
STATUS = ROOT / "infrastructure" / "state" / "modcheck_status.json"
RESULT = ROOT / "results" / "fix.json"
LONG_ID = "bar_with_a_very_long_identifier_that_a_phone_has_to_wrap_somewhere_or_it_scrolls_sideways"
BARS = ["alpha_reads", LONG_ID, "never_broken"]
ITEM = "FIXTMOD_LOOM_BUILD_STILL_WEAVING"
ASK = "FIXTMOD_COLOUR_PICK_HE_WILL_KNOW"
FAILS = []
NOW = time.time()
DAY = 86400.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:300]}"))
    if not cond:
        FAILS.append(name)


def jw(p, doc):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc), encoding="utf-8")


def ev(ago, event, iid, **kw):
    t = NOW - ago
    return {"seat": "BENCH", "event": event, "id": iid, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)),
            "tsn": int(t * 1e9), **kw}


def good_rows():
    return [{"id": "c1", "status": "PASS", "shows": ["alpha_reads"]}, {"id": "chain." + LONG_ID, "status": "PASS"},
            {"id": "never_broken", "status": "PASS"}, {"id": "unrelated", "status": "FAIL"}]


def now_hash():
    return mission_page._private("status").mod_hash(str(MOD_DIR))


def res(rows, **kw):
    jw(RESULT, {"mod": MOD, "mod_hash": now_hash(), "rows": rows, **kw})


def build():
    """A healthy fixture: a validated north star, every bar proven, one run 3 days old."""
    shutil.rmtree(ROOT, True)
    (MOD_DIR / "About").mkdir(parents=True)
    (MOD_DIR / "About" / "About.xml").write_text("<ModMetaData/>", encoding="utf-8")
    (MOD_DIR / "Defs.xml").write_text("<Defs/>", encoding="utf-8")
    WALK.parent.mkdir(parents=True)
    WALK.write_text("# fixture\n\n## north star\nstate: DRAFT\nvalidated-hash:\n\n### must show\n"
                    f"- [ ] `alpha_reads` — it reads.\n- [ ] `{LONG_ID}` — wraps.\n\n### cannot show\n"
                    "- [ ] `never_broken` — never <b>broken</b>.\n", encoding="utf-8")
    mission_page._private("northstar").record_validation(str(WALK), "fixture")
    jw(STATUS, {MOD: {"status": "GREEN", "ts": NOW - 3 * DAY, "hash": now_hash(),
                      "source": {"result": "results/fix.json"}}})
    res(good_rows())
    jw(ROOT / "infrastructure" / "state" / "priority_list.json",
       {"set_at": "2026-11-01T00:00:00Z", "set_by": "Producer", "entries": [{"id": ITEM, "reading": {"mod": MOD}}]})
    jw(BASE / "ops" / "plan_advance.json", {ITEM: {"spec": {"mod": MOD}, "best": 3, "rose_t": NOW - 4.5 * DAY}})
    jw(BASE / "time.json", {"mods": {MOD: {"at": NOW - 7200, "hours": dict(zip(mission_page.CATEGORIES, (1, 2, 3, 4, 5, 6)))}}})
    jw(BASE / "rel" / "store" / "items" / ITEM / "state.json", {"status": "running", "gen": 2, "last_beat": NOW - 120})
    events = [ev(9 * DAY, "file", ITEM, title="<i>Loom</i> build", kind="task", target="v1", needs="offline", **{"for": "BENCH"}),
              ev(2 * DAY, "start", ITEM),
              ev(5 * DAY, "file", ASK, title="Pick a colour", kind="task", target="v1", needs="owner", **{"for": "BENCH"})]
    (BASE / "ledger.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")


def snap():
    out = {}
    for p in sorted(BASE.rglob("*")):
        if p.is_file():
            out[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        elif p.is_dir():
            out[str(p) + "/"] = "dir"
    return out


def cli(*args, env=None):
    return subprocess.run([sys.executable, str(HERE / "mission_page.py"), *args], capture_output=True, text=True,
                          timeout=120, cwd=str(BASE / "tmp"), env={**os.environ, **(env or {})})


def read(*args):
    r = cli(MOD, "--json", *args)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def row(d, bar):
    return next(r for r in d["finish"]["rows"] if r["id"] == bar)


def route(path=f"/mission/{MOD}"):
    code, ctype, body = brief.page(path, lambda: {}, BASE / "pulse")
    return code, ctype, body.decode()


def statuses(d):
    return [r["status"] for r in d["finish"]["rows"]]


# ---------------------------------------------------------------- healthy: the instrument can say yes
build()
d = read()
check("healthy fixture reads MET", d["finish"]["verdict"] == "MET" and statuses(d) == ["PROVEN"] * 3, d["finish"])
check("every row carries its proof age", all(r["age"] == "proof 3 d" for r in d["finish"]["rows"]), d["finish"]["rows"])
check("running: item, seat, how long, worker beat",
      [(r["id"], r["for"], r["worker"]["beat"]) for r in d["running"]] == [(ITEM, "2 d", "2 min")], d["running"])
check("open decisions: the owner's item only, with its wait", [(r["id"], r["waiting"]) for r in d["decisions"]] == [(ASK, "5 d")], d["decisions"])
check("advance: days since the reading rose", d["advance"] == {"status": "READ", "days": 4.5}, d["advance"])
check("time ledger: six categories, with age", d["time"].get("hours", {}).get("waiting") == 6 and d["time"]["age"] == "2 h", d["time"])
code, ctype, body = route()
check("the route serves it", code == 200 and "text/html" in ctype and ">MET<" in body, body[:200])
check("page shows every row, id and age", all(b in body for b in BARS) and body.count("proof 3 d") == 3, body[:300])
check("page escapes ledger and walk text", "<i>Loom" not in body and "<b>broken" not in body, body)
check("/mission lists the mod", route("/mission")[0] == 200 and f"/mission/{MOD}" in route("/mission")[2])
check("route: unknown mod and traversal are 404", route("/mission/NoSuchMod")[0] == 404 and route("/mission/../../etc")[0] == 404)
check("route: json is the same reading", json.loads(route(f"/mission/{MOD}.json")[2])["finish"]["verdict"] == "MET")
check("CLI: unknown mod exit 2", cli("NoSuchMod").returncode == 2)

# ---------------------------------------------------------------- phone width: lists, wrapped ids, viewport
check("phone: viewport set", "width=device-width" in body)
check("phone: no table, no fixed width", "<table" not in body and "min(560px,100vw)" in body and "overflow-wrap:anywhere" in body)
check("phone: status word may wrap", ".st{white-space:normal}" in body)


# ---------------------------------------------------------------- planted faults: each takes the page off done
def fault(name, plant, want_status, bar=None, verdict="NOT MET"):
    build()
    plant()
    d = read()
    got = statuses(d) if bar is None else [row(d, bar)["status"]]
    check(f"fault: {name} reads {want_status}", set(got) == {want_status} and d["finish"]["verdict"] == verdict, (got, d["finish"]["verdict"]))
    return d


def rows_edit(fn):
    return lambda: res(fn(good_rows()))


def entry_edit(**kw):
    def go():
        doc = json.loads(STATUS.read_text(encoding="utf-8"))
        doc[MOD].update(kw)
        jw(STATUS, doc)
    return go


def owe_step4():
    (MOD_DIR / "northstar").mkdir()
    (MOD_DIR / "northstar" / "extension_proof.py").write_text("", encoding="utf-8")


fault("no row claims the bar", rows_edit(lambda rs: rs[1:]), "UNMEASURED", "alpha_reads")
d = fault("a SKIP row", rows_edit(lambda rs: [{**rs[0], "status": "SKIP"}] + rs[1:]), "UNMEASURED", "alpha_reads")
check("UNMEASURED row names why and still has an age", "SKIP" in row(d, "alpha_reads")["why"] and row(d, "alpha_reads")["age"] == "proof 3 d", row(d, "alpha_reads"))
fault("a reused row", rows_edit(lambda rs: [{**rs[0], "freshness": "reused@old.json"}] + rs[1:]), "UNMEASURED", "alpha_reads")
fault("an invalid row", rows_edit(lambda rs: [{**rs[0], "validity": "invalid"}] + rs[1:]), "UNMEASURED", "alpha_reads")
fault("a failed row", rows_edit(lambda rs: [{**rs[0], "status": "FAIL"}] + rs[1:]), "FAIL", "alpha_reads")
fault("a row with no status", rows_edit(lambda rs: [{"id": "c1", "shows": ["alpha_reads"]}] + rs[1:]), "UNMEASURED", "alpha_reads")
fault("the mod changed after the run", lambda: (MOD_DIR / "Defs.xml").write_text("<Defs><x/></Defs>", encoding="utf-8"), "STALE")
fault("result file gone", lambda: RESULT.unlink(), "UNMEASURED")
fault("result file torn", lambda: RESULT.write_text("{", encoding="utf-8"), "UNMEASURED")
fault("result of an aborted run", lambda: res(good_rows(), aborted="bridge lost"), "UNMEASURED")
fault("result of an older build", lambda: res(good_rows(), mod_hash="old"), "UNMEASURED")
d = fault("step 4 record torn: the page still renders", lambda: (owe_step4(), entry_edit(step4="garbled")()), "UNMEASURED", verdict="UNMEASURED")
check("torn record names the read that failed", "not read" in d["finish"]["rows"][0]["why"] and route()[0] == 200, d["finish"]["rows"])
fault("result of another mod", lambda: res(good_rows(), mod="Other"), "UNMEASURED")
fault("result with no mod hash", lambda: jw(RESULT, {"mod": MOD, "rows": good_rows()}), "UNMEASURED")
fault("status file nested past recursion", lambda: STATUS.write_text("[" * 100000 + "]" * 100000, encoding="utf-8"), "UNMEASURED")
fault("run with no result file", entry_edit(source={}), "UNMEASURED")
fault("result path leaves the repo", entry_edit(source={"result": "../../etc/passwd"}), "UNMEASURED")
fault("run time is text", entry_edit(ts="yesterday"), "UNMEASURED")
d = fault("run time in the future", entry_edit(ts=NOW + 9 * DAY), "UNMEASURED")
check("a future run shows no age", row(d, "alpha_reads")["age"].startswith("no proof"), row(d, "alpha_reads"))
fault("never run", lambda: jw(STATUS, {}), "UNMEASURED")
fault("entry torn", lambda: jw(STATUS, {MOD: "garbled"}), "UNMEASURED")
fault("status file torn", lambda: STATUS.write_text("<<<<<<<", encoding="utf-8"), "UNMEASURED")
d = fault("GREEN but no bars", lambda: WALK.write_text("# fixture\n\n## north star\nstate: DRAFT\n", encoding="utf-8"), "UNMEASURED", verdict="UNMEASURED")
check("no bars names it", d["finish"]["rows"][0]["why"] == "the walk has no bars", d["finish"])
d = fault("GREEN, no walk at all", lambda: WALK.unlink(), "UNMEASURED", verdict="UNMEASURED")
fault("draft north star: rows may pass, the line is not met",
      lambda: WALK.write_text(WALK.read_text(encoding="utf-8").replace("it reads.", "it reads!"), encoding="utf-8"), "PROVEN", "alpha_reads")
fault("entry not GREEN: rows pass, the line is not met", entry_edit(status="RED"), "PROVEN", "alpha_reads")


d = fault("step 4 owed and unmeasured", owe_step4, "PROVEN", "alpha_reads")
check("step 4 shows", d["finish"]["modcheck"]["step4"] == "UNMEASURED", d["finish"]["modcheck"])

# the page words, on the real route, for one planted fault: an unproved row can never print as proven
build()
rows_edit(lambda rs: rs[1:])()
body = route()[2]
piece = body[body.index("alpha_reads") - 60:body.index("alpha_reads")]
check("page: the unproved row prints UNMEASURED", "UNMEASURED" in piece and "PROVEN" not in piece, piece)
check("page: headline is NOT MET", ">NOT MET<" in body)

# ---------------------------------------------------------------- the other sections
build()
(BASE / "time.json").unlink()
d = read()
check("no time ledger: UNMEASURED, naming its item", d["time"]["status"] == "UNMEASURED" and mission_page.TIME_ITEM in d["time"]["why"], d["time"])
check("no time ledger on the page", "UNMEASURED: no time ledger" in route()[2])
(BASE / "time.json").write_text("{", encoding="utf-8")
check("torn time ledger: UNMEASURED", read()["time"]["status"] == "UNMEASURED")
jw(BASE / "time.json", {"mods": {MOD: {"at": NOW, "hours": {"selftest": 1}}}})
check("a category not recorded reads UNMEASURED, never 0", read()["time"]["hours"]["live"] == "UNMEASURED")
jw(BASE / "time.json", {"mods": {MOD: {"at": NOW + 9 * DAY, "hours": {}}}})
check("time ledger from the future: UNMEASURED", read()["time"]["status"] == "UNMEASURED")
(BASE / "time.json").write_text('{"mods": {"%s": {"at": 1%s, "hours": {}}}}' % (MOD, "0" * 400), encoding="utf-8")
check("a number past float range: UNMEASURED, not a crash", read()["time"]["status"] == "UNMEASURED" and route()[0] == 200)
(BASE / "ledger.jsonl").write_text("not json\n", encoding="utf-8")
d = read()
check("ledger unread: says so, never 'nothing running'", d["ledger_why"].startswith("ledger not read"), d)
body = route()[2]
check("ledger unread on the page", "Nothing the ledger holds" not in body and "No open item" not in body and "ledger not read" in body)
build()
(BASE / "ops" / "plan_advance.json").unlink()
check("no advance record: UNMEASURED", read()["advance"]["status"] == "UNMEASURED")
build()
jw(ROOT / "infrastructure" / "state" / "priority_list.json", {"set_at": "x", "set_by": "Producer", "entries": []})
check("not listed: UNMEASURED", read()["advance"]["why"] == "this mod is not on the priority list", read()["advance"])

# ---------------------------------------------------------------- writes nothing but itself
build()
out = BASE / "out" / "page.html"
out.parent.mkdir()
before = snap()
r = cli(MOD, "--out", str(out))
after = snap()
check("CLI --out exit 0", r.returncode == 0 and "MET" in r.stdout, r.stderr)
check("CLI --out writes the page and nothing else", {k for k in after if after[k] != before.get(k)} == {str(out)} and set(before) <= set(after),
      {k for k in after if after[k] != before.get(k)})
check("the written page is a page", ">MET<" in out.read_text(encoding="utf-8") and "href='/item/" not in out.read_text(encoding="utf-8"))
before = snap()
route(), route("/mission"), route(f"/mission/{MOD}.json"), cli(MOD, "--json"), cli(MOD)
check("routes and stdout write nothing", snap() == before)
pyc = subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, {str(HERE)!r}); import mission_page as m; "
                      "m._private('northstar'); m._private('status'); print(sys.dont_write_bytecode)"],
                     capture_output=True, text=True, timeout=60, env={**os.environ, "PYTHONPYCACHEPREFIX": str(BASE / "pyc")})
check("the daemon's bytecode flag stays its own", pyc.stdout.startswith("False"), pyc.stdout + pyc.stderr[-200:])
check("a route's modcheck import writes no bytecode", pyc.returncode == 0 and not list((BASE / "pyc").rglob("status*.pyc")), list((BASE / "pyc").rglob("status*.pyc"))[:2])

# ---------------------------------------------------------------- the real tree: a real mod renders, and nothing moves
real_env = {k: "" for k in ENV} | {"RM_OPS_WATCH_DIR": os.environ.get("RM_OPS_WATCH_DIR_REAL", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"),
                                   "RM_PULSE_STATE": str(Path.home() / ".local" / "state" / "rm-dashboard"),
                                   "RELENTLESS_ROOT": "/home/mandrake/rm/relentless"}


def tree_state():
    """Other selftests run beside this one and leave their own __pycache__: only this page's bytecode is ours to judge."""
    git = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True, timeout=120).stdout
    st = hashlib.sha256((REPO / "infrastructure/state/modcheck_status.json").read_bytes()).hexdigest()
    return [ln for ln in git.splitlines() if "__pycache__" not in ln], st, sorted(p.name for p in HERE.glob("__pycache__/mission_page*"))


out = BASE / "out" / "real.html"
before = tree_state()
r = cli("GimmeSomeSlack", "--out", str(out), env=real_env)
check("real mod renders", r.returncode == 0 and out.is_file(), r.stderr[-300:])
check("real mod: no bar reads done unproved", "bars proven" in r.stdout, r.stdout)
check("real tree unmoved by a render", tree_state() == before)

print("FAILS:", FAILS if FAILS else "none")
sys.exit(1 if FAILS else 0)
