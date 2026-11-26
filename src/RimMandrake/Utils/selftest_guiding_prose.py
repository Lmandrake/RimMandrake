#!/usr/bin/env python3
"""selftest_guiding_prose.py - the promises of design/specs/2026-11-23-guiding-prose-check/boundary.md, one test each.

Offline: no model call (the reader is a planted answer), no network, a throwaway git remote in a temp dir. Every planted
fault is one that must be caught and every must-stay-green case one that must not. Exit 0 = all pass, 1 = a case failed.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TOP, "src", "RimMandrake", "rimflow"))
import guiding_prose as G  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="rm-selftest-gprose-")
os.environ["RM_GUIDING_PROSE_DIR"] = os.path.join(TMP, "runs")
os.environ["RM_GUIDING_PROSE_READER"] = "0"
os.environ["RM_ROLE_UNIT"] = "rm-selftest-gprose"     # a launched run, never a principal, unless a test says otherwise
SPEC = os.path.join("design", "specs", "2026-11-19-plain-english-rule-docs")
# the section as it stood before de63778138e0, and as repaired there (the lines the owner quoted, word for word)
PIT_OLD = """## A pit is a SUPERDEEP cell

- The ruling is made and fully specified, and its build is in progress: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
- A pit is depth 4 on the D/F primitive that rulings 18/19 already established.
- So the fitting concept collapses to **spikes alone**. Oil and poison are FluidDefs. The oubliette is CUT.
"""
PIT_NEW = """## A pit is a SUPERDEEP cell

- The ruling is made and fully specified. Its item holds the state of the build; read the state there, with
  `rimflow show PIT_SUPERDEEP_COLLAPSE_1`: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
- A pit is depth 4 on the D/F primitive that rulings 18/19 already established. D/F is depth and fill: each cell
  has a dug depth (D) and a fill of liquid (F). Rulings 18 and 19 are in `design/RimMandrake/flowworks_mod_definition.md`
  (§20 and §21).
- So the fitting concept collapses to **spikes alone**. Oil and poison are FluidDefs. The oubliette is CUT.
"""
POOL_OLD = """## Git

- The alarm does not count two kinds of commit:
  - a trailing lesson/ledger commit (the belt carries those);
  - a commit whose content origin/main already holds under another hash.
- A pool clone with unpushed work is never reused.
- Revert if a clone strands work, or if the free space on `/` goes under the disk floor.
"""
POOL_NEW = """## Git

- The alarm does not count two kinds of commit:
  - a trailing lesson/ledger commit (the clone's return step at the end of a run bundles those into the orphans
    store, so they are not lost);
  - a commit whose content origin/main already holds under another hash.
- A pool clone with unpushed work is never reused.
- Revert the pool if a clone strands work, or if the free space on `/` goes under the disk floor. To revert the pool
  is to end the approval of reused clones for more than 4 writers, and to return to at most 4 writers at one time.
"""


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def faults(new, old="", path="design/RimMandrake/standing_rulings.md", door="publish"):
    return G.check_text(path, new, [old] if old else [], top=TOP, door=door)["faults"]


def kinds(new, **kw):
    return {(f["kind"], f["term"]) for f in faults(new, **kw)}


def has(new, kind, term=None, **kw):
    got = kinds(new, **kw)
    return any(k == kind and (term is None or term in t) for k, t in got), got


def t_the_list_covers_the_census():
    rows = json.load(open(os.path.join(TOP, SPEC, "census.json"), encoding="utf-8"))
    cfg = G.config()
    missing = [r["path"] for r in rows if os.path.exists(os.path.join(TOP, r["path"]))
               and not G.is_guiding(r["path"]) and r["path"] not in cfg["left_out"]]
    check(len(rows) > 100 and not missing, "list: %d census files, each matched or left out with a reason (%s)" % (len(rows), missing))
    check(all(v.strip() for v in cfg["left_out"].values()), "list: each left_out file has a reason")
    check(G.is_guiding("GUIDING_PRINCIPLES.md") and G.is_guiding("CLAUDE.md"), "list: GUIDING_PRINCIPLES.md and CLAUDE.md are guiding prose")
    check(G.is_guiding("skills/rimbridge/SKILL.md") and G.is_guiding("infrastructure/state/facts/tool_traps.md"), "list: a skill and a fact file")
    check(not G.is_guiding("design/concepts/Pyrelands/log.md") and not G.is_guiding("infrastructure/state/items/X.md"),
          "list: a concept log and an item are not guiding prose")
    check(not any(G.is_guiding(p) for p in cfg["left_out"]), "list: a left_out file is not matched, whatever glob fits it")


def t_the_three_lines_he_quoted_are_caught():
    ok, got = has(PIT_OLD, "coded-name", "D/F")
    check(ok, "his line: the D/F primitive is caught and named (%s)" % sorted(got))
    ok, got = has(POOL_OLD, "retired-name", "the belt")
    check(ok, "his line: the belt is caught and named (%s)" % sorted(got))
    ok, got = has(PIT_OLD, "state", "is in progress")
    check(ok, "his line: the build in progress is caught and named (%s)" % sorted(got))
    fs = faults(PIT_OLD) + faults(POOL_OLD)
    check(all(f["repair"] and f["line"] for f in fs), "his lines: each fault has a repair and a line")
    df = [f for f in fs if f["term"] == "D/F"]
    check(df and "A pit is a SUPERDEEP cell" in df[0]["repair"], "his line: the repair names the place for the D/F definition")


def t_the_repaired_lines_stay_green():
    for name, txt in (("pit", PIT_NEW), ("pool", POOL_NEW)):
        check(faults(txt) == [], "repaired: the %s section gives no fault (%s)" % (name, faults(txt)))


FORM = [
    ("pronoun", "It holds", "# R\n\nThe tick reads the lock. It holds the game until the run ends.\n"),
    ("pronoun", "This", "# R\n\nThe tick stops. This is the rule.\n"),
    ("pronoun", "Then it", "# R\n\nThe tick stops. Then it starts the game.\n"),
    ("long-sentence", "words", "# R\n\nThe tick reads the lock and the tick starts the game and the game loads the list and the list names the mods and the mods hold the defs today.\n"),
    ("long-sentence", "24 words", "# R\n\nRun the test of the mod that the tick named in the log of the last run before the next run of it starts.\n"),
    ("should", "should", "# R\n\nThe helper should write the note.\n"),
    ("duty-no-actor", "must be run", "# R\n\nThe test must be run before a commit.\n"),
    ("two-commands", "", "# R\n\nRun the test; write the note.\n"),
    ("state", "in progress", "# R\n\nThe move of the units is in progress.\n"),
    ("state", "currently", "# R\n\nThe page currently reads the old store.\n"),
    ("state", "", "# R\n\nThe batch holds 14 of 40 files so far.\n"),
    ("no-object", "Revert if", "# R\n\nRevert if a clone strands work.\n"),
    ("dead-path", "design/RimMandrake/no_such_file_here.md", "# R\n\nThe rule is in `design/RimMandrake/no_such_file_here.md`.\n"),
    ("dead-item", "RIMMANDRAKE_PLANT_NO_SUCH_ITEM_EVER_FILED", "# R\n\nThe rule is in RIMMANDRAKE_PLANT_NO_SUCH_ITEM_EVER_FILED.\n"),
    ("coded-name", "D/F", "# R\n\nDig to the D/F limit.\n"),
    ("coded-name", "Q11a", "# R\n\nAsk him Q11a first.\n"),
    ("look-elsewhere", "see above", "# R\n\nFor the order, see above.\n"),
    ("retired-name", "the belt", "# R\n\nGive the item to the belt.\n"),
]
GREEN = [
    ("a conditional state", "# R\n\nIf a build is in progress, wait for the run to end.\n"),
    ("a dated reading", "# R\n\nThe batch held 14 of 40 files so far on 2026-11-23.\n"),
    ("one command with its contrast", "# R\n\nRemove the wrong line; never annotate the line.\n"),
    ("a permission", "# R\n\nA seat may take a free game.\n"),
    ("a plain passive", "# R\n\nThe lock is read by the tick and no map is recorded.\n"),
    ("a duty with its actor", "# R\n\nThe test must be run by the fixer.\n"),
    ("a dummy subject", "# R\n\nIt is better to ask GPT early.\n"),
    ("a demonstrative with its noun", "# R\n\nThis rule binds. These files stay.\n"),
    ("a coded name with its meaning", "# R\n\nD31 (no tool needs his words) binds. D31 is old.\n"),
    ("a common code", "# R\n\nThe I/O error was one USB stick. The A/B ran two days. Press F5.\n"),
    ("a file that is gone, said so", "# R\n\n`src/RimMandrake/Utils/old_gone_tool.py` was deleted.\n"),
    ("a bullet that ends its lead-in", "# R\n\nDelete an extra when:\n\n- it serves no experience;\n- it fights a ruling.\n"),
    ("a sentence after a mark", "# R\n\nThe seat takes the call as a delegated decision and logs the call in the ledger. \u26d4 An unanswered card is never his approval at all.\n"),
    ("a bold lead and a lower-case name", "# R\n\n- **Check when the mechanism that makes the event began before you compare the rate of the event.** v2 read zero for one reason that the run before had found in the log.\n"),
    ("what must be done", "# R\n\nThe Conductor repairs what must be done.\n"),
    ("an indented command", "# R\n\nWrite the split:\n   python3 a.py shape x --parts j --size small --seat BENCH --why w one two three four five six seven eight nine ten eleven --publish\n"),
    ("a descriptive sentence of 24 words", "# R\n\nEach helper that the tick starts on a mod reads the list of that mod and the log of the last run on it first.\n"),
    ("what he should check", "# R\n\nPage two says what he should check.\n"),
    ("a long list after a colon", "# R\n\nThe run writes three files: the packet of the mod that it read first, the log of the visit that it made, the note that the next run reads.\n"),
    ("a bold lead and its sentence", "# R\n\n- **The tick starts no game while his hold stands on that game at all.** Each other seat reads the lock before that seat starts one.\n"),
]


def t_each_form_fault_is_caught_and_named():
    for kind, term, txt in FORM:
        ok, got = has(txt, kind, term)
        check(ok, "form: %s is caught, naming %r (%s)" % (kind, term, sorted(got)))
    for what, txt in GREEN:
        check(faults(txt) == [], "form: green on %s (%s)" % (what, faults(txt)))


BAD = ("It should be run by then, see above, and this is currently in progress on the D/F belt that nobody has ever told "
       "anyone about since the belt started")
EXEMPT = [
    ("a one-line owner quote", 'The owner, 2026-11-23: *"%s."*\n' % BAD),
    ("a plain quote", 'He said "%s."\n' % BAD),
    ("a quote over lines", 'The owner: *"It should be run,\nsee above, and this is currently in progress\non the belt."*\n'),
    ("a quote with a quote inside", 'The owner: *"It should run "now" on the belt. It is in progress."*\n'),
    ("a block quote", '> *"It should be run, see above.\n> It is in progress on the belt."*\n'),
    ("a curly quote", "He wrote “It should be run on the belt.”\n"),
    ("the card text of a brief", "## What the card said\n\nIt should be run on the belt.\n"),
    ("a table row", "| a | b |\n|---|---|\n| It should be run on the belt | D/F is in progress |\n"),
    ("a fenced block with an empty line", "```\nThe tick runs.\n\nIt should be run on the belt, see above.\n\nD/F\n```\n"),
    ("a fenced block", "```\nIt should be run on the belt. See above. D/F\n```\n"),
    ("a code span", "The page reads `It should be run on the belt`.\n"),
    ("a heading", "## It should be run on the belt, D/F, see above\n"),
    ("front matter", "---\nname: x\ndescription: It should be run on the belt, see above\n---\n\nThe tick runs.\n"),
    ("an existing path", "The rule is in `design/RimMandrake/standing_rulings.md`.\n"),
    ("a filed item id", "The item is RIMMANDRAKE_CHECK_GUIDING_PROSE_AT_WRITE_NO_SEARCHING_FOR_MEANING.\n"),
    ("a legacy id in code marks", "Read the item `PIT_SUPERDEEP_COLLAPSE_1`.\n"),
]


def t_exempt_text_stays_green():
    for what, txt in EXEMPT:
        check(faults(txt) == [], "exempt: %s (%s)" % (what, faults(txt)))
    ok, got = has("The owner: *\"Do it.\"* It should wait. The helper should go.\n", "should")
    check(ok, "exempt: the sentence after a quote is still read (%s)" % sorted(got))


def t_only_changed_sentences_are_read():
    old = PIT_OLD + "\n" + POOL_OLD
    check(G.check_text("CLAUDE.md", old, [old], top=TOP)["sentences"] == 0, "changed: an unchanged old file reads no sentence")
    check(faults(old, old) == [], "changed: an unchanged old file with many faults gives nothing")
    rewrap = old.replace("A pit is depth 4 on the D/F primitive that", "A pit is depth 4 on the D/F\n  primitive that")
    check(rewrap != old and faults(rewrap, old) == [], "changed: a re-wrapped bullet gives nothing")
    bold = old.replace("A pit is depth 4", "**A pit** is depth 4")
    check(bold != old and faults(bold, old) == [], "changed: the same words with other emphasis give nothing")
    moved = POOL_OLD + "\n" + PIT_OLD
    check(faults(moved, old) == [], "changed: moved bullets give nothing")
    one = old + "\n- The helper should write the note.\n"
    fs = faults(one, old)
    check([f["kind"] for f in fs] == ["should"] and fs[0]["line"] == one.count("\n"),
          "changed: one new bad line gives one fault at its line (%s)" % fs)
    r = G.check_files(TOP, {"CLAUDE.md": one, "PURPOSE.md": PIT_OLD}, {"CLAUDE.md": "", "PURPOSE.md": old})
    check(not [f for f in r["faults"] if f["term"] == "D/F"], "changed: a sentence moved from one rule file to another gives nothing")


class Reader:
    """A planted model: returns `answer` (or raises) and keeps each prompt."""
    def __init__(self, answer):
        self.answer, self.prompts = answer, []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


def read(answer, new=POOL_OLD, old="", status="CALIBRATED"):
    r = Reader(answer)
    return r, G.check_files(TOP, {"CLAUDE.md": new}, {"CLAUDE.md": old}, reader=r, status=lambda: status)


def t_the_reader_gets_only_what_changed():
    old = "# T\n\nOpening words.\n\n## Other\n\nThe zebra section.\n\n" + POOL_OLD
    new = old + "- The kennel is full.\n"
    r, _ = read('{"faults": []}', new, old)
    p = r.prompts[0] if r.prompts else ""
    check(len(r.prompts) == 1 and "] The kennel is full." in p, "reader: one call holds the changed sentence")
    check("A pool clone with unpushed work" in p and "zebra" not in p, "reader: the section is there, another section is not")
    check("Opening words." in p and "The one window he talks to" in p, "reader: the opening lines and the glossary are there")
    check("] A pool clone with unpushed work" not in p, "reader: an unchanged sentence is context, not a sentence to check")
    r, res = read('{"faults": []}', old, old)
    check(r.prompts == [] and res["reader"]["status"] == "not run", "reader: no changed sentence, no model call (%s)" % res["reader"])


def t_the_reader_answer_is_bound_to_the_line():
    sents = G.changed_sentences(POOL_OLD, [])
    n = [i for i, s in enumerate(sents, 1) if "the belt" in s["raw"]][0]
    ans = json.dumps({"faults": [{"n": n, "term": "carries those", "kind": "undefined", "why": "w", "define_at": "this sentence"},
                                 {"n": n, "term": "the kennel", "kind": "undefined", "why": "w", "define_at": "x"},
                                 {"n": 999, "term": "the belt", "kind": "undefined", "why": "w", "define_at": "x"}]})
    r, res = read(ans)
    mine = [f for f in res["faults"] if f["by"] == "reader"]
    check([f["term"] for f in mine] == ["carries those"] and res["reader"]["dropped"] == 2,
          "reader: a term that is not in its sentence is dropped and counted (%s, %s)" % (mine, res["reader"]))
    check(mine and mine[0]["line"] == sents[n - 1]["l0"] and "this sentence" in mine[0]["repair"], "reader: the fault has its line and its place")
    for bad, why in ((subprocess.TimeoutExpired("claude", 300), "timeout"), ("I cannot help with that.", "unreadable"),
                     ("", "empty"), (OSError("no claude"), "dead"), ('{"faults": "none"}', "shape"), ('{"faults": [3]}', "row shape")):
        _, res = read(bad)
        check(res["reader"]["status"].startswith("UNMEASURED: ") and not [f for f in res["faults"] if f["by"] == "reader"],
              "reader: %s reads UNMEASURED with its cause, never zero (%s)" % (why, res["reader"]["status"]))
    _, res = read('{"faults": []}')
    check(res["reader"]["status"] == "read", "reader: an answer with no fault reads as read")


def t_an_uncalibrated_reader_sends_nothing_back():
    ans = json.dumps({"faults": [{"n": 1, "term": "count two kinds", "kind": "undefined", "why": "w", "define_at": "x"}]})
    good = "## Git\n\n- The alarm does not count two kinds of commit.\n"
    for st in ("UNTESTED", "FAILED"):
        _, res = read(ans, good, status=st)
        check(res["faults"] == [] and len(res["shown"]) == 1 and "shown only" in G.render(res), "uncalibrated: %s is shown only (%s)" % (st, res["faults"]))
    _, res = read(ans, good)
    check(len(res["faults"]) == 1 and res["shown"] == [], "uncalibrated: CALIBRATED counts as a fault")


GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.hooksPath=/dev/null", "-c", "init.defaultBranch=main"]


def g(*a, cwd):
    return subprocess.run([*GIT, *a], cwd=cwd, check=True, capture_output=True, text=True).stdout


def repo(tmp):
    """A bare origin and a clone that holds one rule file with an old fault."""
    g("init", "-q", "--bare", os.path.join(tmp, "o.git"), cwd=tmp)
    c = os.path.join(tmp, "c")
    g("clone", "-q", os.path.join(tmp, "o.git"), c, cwd=tmp)
    for k, v in (("user.name", "t"), ("user.email", "t@example.invalid"), ("core.hooksPath", "/dev/null")):
        g("config", k, v, cwd=c)
    os.makedirs(os.path.join(c, "design/RimMandrake"))
    with open(os.path.join(c, "design/RimMandrake/debug_process.md"), "w") as f:
        f.write("# D\n\n" + PIT_OLD)
    g("add", "-A", cwd=c)
    g("commit", "-qm", "base", cwd=c)
    g("push", "-q", "origin", "HEAD:main", cwd=c)
    return c


def publish(c, *paths, **env):
    e = dict(os.environ, **env)
    import time_budget      # a publish waits for a tree-check slot on a loaded machine: 120 s cut it (2026-11-26, 336 s wait)
    return subprocess.run([sys.executable, os.path.join(HERE, "publish.py"), "-m", "s", *paths], cwd=c, capture_output=True,
                          text=True, env=e, timeout=time_budget.PUBLISH_S)


def t_a_publish_with_faults_still_lands():
    with tempfile.TemporaryDirectory() as tmp:
        c = repo(tmp)
        p = os.path.join(c, "design/RimMandrake/debug_process.md")
        with open(p, "a") as f:
            f.write("\n- The helper should give the item to the belt.\n")
        r = publish(c, "design/RimMandrake/debug_process.md")
        out = r.stdout
        check(r.returncode == 0 and "PUBLISHED " in out, "publish: lands with exit 0 (%s %s)" % (r.returncode, (out + r.stderr)[-300:]))
        check("GUIDING PROSE" in out and "the belt" in out and "REPAIR" in out and "D/F" not in out,
              "publish: the faults of the new line come back, the old lines stay silent (%s)" % out[-600:])
        check(out.find("PUBLISHED ") < out.find("GUIDING PROSE"), "publish: the faults come after the landing")
        rows = G.rows()
        sha = g("rev-parse", "origin/main", cwd=c).strip()
        check(rows and rows[-1]["door"] == "publish" and sha in rows[-1]["landed"] and rows[-1]["faults"], "publish: the run is recorded with its sha")
        n = len(G.rows())
        other = dict(os.environ, RM_DISPATCHER_STATE=os.path.join(TMP, "other"))
        other.pop("RM_GUIDING_PROSE_DIR")
        with open(p, "a") as f:
            f.write("\n- The clerk should go to the belt.\n")
        r = subprocess.run([sys.executable, os.path.join(HERE, "publish.py"), "-m", "s", "design/RimMandrake/debug_process.md"], cwd=c,
                           capture_output=True, text=True, env=other, timeout=__import__("time_budget").PUBLISH_S)
        check(r.returncode == 0 and "GUIDING PROSE" not in r.stdout and not os.path.exists(os.path.join(TMP, "other", "guiding_prose")),
              "publish: a throwaway clone with no guiding_prose.json is not read or recorded (%s)" % (r.stdout + r.stderr)[-200:])
        with open(os.path.join(c, "x.txt"), "w") as f:
            f.write("x")
        r = publish(c, "x.txt")
        check(r.returncode == 0 and "GUIDING PROSE" not in r.stdout, "publish: a landing with no rule file says nothing")
        src = open(os.path.join(HERE, "publish.py"), encoding="utf-8").read()
        i = src.index("def main(")
        check("prose_after(" in src[i:] and "prose_after(" not in src[src.index("def _publish("):i],
              "publish: the check runs in main, outside the clone lock")


def launch_main(brief, rc=0, boom=None, stand_in=False, principal=False, extra=()):
    """principal: the launch comes from the Conductor window (seat BENCH, no RM_ROLE_UNIT). extra: more launch args."""
    import detached_helper as DH
    old, oldc, own = DH.launch, G.check_brief, DH.OWN_LAUNCH
    oldenv = {k: os.environ.get(k) for k in ("RM_ROLE_UNIT", "AGENT_SEAT")}
    started = []
    try:
        if principal:
            os.environ.pop("RM_ROLE_UNIT", None)
            os.environ["AGENT_SEAT"] = "BENCH"
        DH.launch = lambda *a, **k: (started.append(a) or (rc, "launched: unit x" if rc == 0 else "refused: no"))
        DH.OWN_LAUNCH = own if stand_in else DH.launch
        if boom:
            def bad(*a, **k):
                raise boom
            G.check_brief = bad
        path = os.path.join(TMP, "b.md")
        with open(path, "w") as f:
            f.write(brief)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            got = DH.main(["launch", "--seat", "BENCH", "--item", "X_Y_Z_W", "--brief-file", path, "--budget-usd", "0"]
                          + list(extra))
        return got, buf.getvalue(), started
    finally:
        DH.launch, G.check_brief, DH.OWN_LAUNCH = old, oldc, own
        for k, v in oldenv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def t_a_launch_with_faults_still_starts():
    rc, out, started = launch_main("# Brief one\n\nThe helper should give the item to the belt.\n")
    check(rc == 0 and len(started) == 1 and out.startswith("launched: unit x"), "launch: the unit starts with exit 0")
    check("the belt" in out and "REPAIR" in out and out.find("launched") < out.find("GUIDING PROSE"), "launch: the faults come back at the end (%s)" % out)
    rc, out, _ = launch_main("# Brief two\n\nGive the next item to the belt.\n", rc=2)
    check(rc == 2 and out == "refused: no\n", "launch: a refused launch's text stays the gate's own (%r)" % out)
    n = len(G.rows())
    rc, out, _ = launch_main("# Brief six\n\nThe page should go to the belt.\n", stand_in=True)
    check(rc == 0 and out == "launched: unit x\n" and len(G.rows()) == n, "launch: another test's stand-in for launch() checks and records nothing")
    rc, out, _ = launch_main("# Brief three\n\nRun the test. Write the note.\n")
    check(rc == 0 and "GUIDING PROSE" not in out, "launch: a good brief says nothing (%s)" % out)


def t_a_sentence_already_sent_in_a_brief_is_silent():
    b = "# Brief four\n\nThe helper should send the parcel to the belt.\n"
    _, out, _ = launch_main(b)
    _, again, _ = launch_main(b + "\nThe runner should stop.\n")
    check("the belt" in out, "sent: the first launch is checked")
    check("the belt" not in again and "The runner should" in again, "sent: the second launch reads only its new sentence (%s)" % again)
    _, out, _ = launch_main("# Brief five\n\nThe clerk should wait.\n", rc=2)
    _, out, _ = launch_main("# Brief five\n\nThe clerk should wait.\n")
    check("should" in out, "sent: a refused launch sent nothing, so the next one is checked")


def t_a_principal_launch_gets_its_faults_before_the_start():
    b = "# Brief seven\n\nThe porter should carry the crate to the belt.\n"
    rc, out, started = launch_main(b, principal=True)
    check(rc == 5 and started == [], "before: the Conductor's faulty brief starts nothing and exits 5 (rc %s, %d started)" % (rc, len(started)))
    check("RETURNED BEFORE THE START" in out and "the belt" in out and "REPAIR" in out and "launched: unit" not in out,
          "before: the text names each fault and its repair, and says nothing started (%s)" % out)
    rc, out, started = launch_main(b.replace("should carry", "carries"), principal=True)
    check(rc == 5 and started == [] and "the belt" in out and "should" not in out.split("REPAIR")[0],
          "before: a repaired brief is read again and returns only what is left (%s)" % out)
    rc, out, started = launch_main(b, principal=True)
    check(rc == 0 and len(started) == 1 and out.startswith("launched: unit x") and "NOTE" in out and "the belt" in out,
          "before: the same brief launched again unchanged starts as written, its faults a NOTE after (%s)" % out)
    rc, out, started = launch_main("# Brief eight\n\nRun the test. Write the note.\n", principal=True)
    check(rc == 0 and len(started) == 1 and "GUIDING PROSE" not in out, "before: a brief with no fault starts at once (%s)" % out)
    rc, out, started = launch_main("# Brief nine\n\nThe weaver should go to the belt.\n")
    check(rc == 0 and len(started) == 1 and "the belt" in out, "before: a launch by a program or a launched run starts as before")
    rc, out, started = launch_main("# Brief ten\n\nThe baker should go to the belt.\n", principal=True, boom=RuntimeError("planted"))
    check(rc == 0 and len(started) == 1 and "UNMEASURED" in out, "before: a check that raises starts the run and says so (%s)" % out)


def t_a_brief_a_program_wrote_is_never_returned():
    """RIMMANDRAKE_HOLD_MOD_AT_ROAD_BACK_STAGE_AND_LET_BUNDLE_BRIEF_START: `./pipe bundle` writes its brief by program,
    from the Conductor window. The Conductor cannot correct that brief, so the launch starts and its faults are a NOTE."""
    b = "# Brief eleven\n\nThe tailor should carry the cloth to the belt.\n"
    rc, out, started = launch_main(b, principal=True, extra=["--by-program", "work_bundle"])
    check(rc == 0 and len(started) == 1 and out.startswith("launched: unit x"),
          "by program: a brief a program wrote starts at once from the Conductor window (rc %s, %d started: %s)" % (rc, len(started), out))
    check("the belt" in out and "RETURNED BEFORE THE START" not in out and out.find("launched") < out.find("GUIDING PROSE"),
          "by program: its faults print as a note after the start (%s)" % out)
    rc, out, started = launch_main(b.replace("tailor", "glazier"), principal=True)
    check(rc == 5 and started == [] and "RETURNED BEFORE THE START" in out,
          "by program: a brief the Conductor wrote by hand is still returned (rc %s: %s)" % (rc, out))
    rf = os.path.join(os.path.dirname(HERE), "rimflow")
    for path in ("work_bundle.py", "maturation.py", "list_dispatch.py", "red_dispatch.py", "quiet_scan.py",
                 os.path.join("..", "Utils", "follow_through.py")):
        src = open(os.path.join(rf, path), encoding="utf-8").read()
        check('"--by-program"' in src, "by program: %s names its launches --by-program" % path)


def t_a_broken_check_stops_nothing():
    rc, out, started = launch_main("# B\n\nThe cook should go to the belt.\n", boom=RuntimeError("planted"))
    check(rc == 0 and len(started) == 1 and "UNMEASURED" in out and "planted" in out, "broken: the launch goes on and says so (%s)" % out)
    with tempfile.TemporaryDirectory() as tmp:
        c = repo(tmp)
        with open(os.path.join(c, "design/RimMandrake/debug_process.md"), "a") as f:
            f.write("\n- The helper should go.\n")
        r = publish(c, "design/RimMandrake/debug_process.md", CLEAR_FINDINGS_TOOLS="/nonexistent")
        check(r.returncode == 0 and "PUBLISHED " in r.stdout and "UNMEASURED" in r.stdout and "should" not in r.stdout.split("UNMEASURED")[0].split("GUIDING")[-1],
              "broken: with no lint module the landing completes and reads UNMEASURED (%s)" % (r.stdout + r.stderr)[-400:])


def t_a_principal_gets_a_note():
    res = G.check_files(TOP, {"CLAUDE.md": "# R\n\nThe helper should go.\n"}, {"CLAUDE.md": ""})
    check("NOTE" in G.render(res, principal="conductor") and "NOTE" not in G.render(res), "principal: the Conductor's faults print as a NOTE")
    row = G.record("publish", res, env={"AGENT_SEAT": "BENCH"})
    check(row["principal"] == "conductor" and row["faults"], "principal: the record names the Conductor and holds the faults")
    row = G.record("publish", res, env={"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-x"})
    check(row["principal"] is None, "principal: a launched run is no principal")


def t_the_check_verb_exits_for_a_caller():
    def verb(*a, **env):
        return subprocess.run([sys.executable, os.path.join(HERE, "guiding_prose.py"), *a], cwd=TMP, capture_output=True, text=True,
                              env=dict(os.environ, **env), timeout=120)
    for body, rc in (("# R\n\nThe helper should go.\n", 1), ("# R\n\nThe helper runs the test.\n", 0)):
        p = os.path.join(TMP, "v%d.md" % rc)
        with open(p, "w") as f:
            f.write(body)
        r = verb("check", p)
        check(r.returncode == rc, "verb: check exits %d (%s: %s)" % (rc, r.returncode, (r.stdout + r.stderr)[-200:]))
    r = verb("check", os.path.join(TMP, "absent.md"))
    check(r.returncode == 3 and "UNMEASURED" in r.stdout + r.stderr, "verb: a file that cannot be read exits 3 (%s)" % r.returncode)
    r = verb("check", os.path.join(TMP, "v0.md"), CLEAR_FINDINGS_TOOLS="/nonexistent")
    check(r.returncode == 3, "verb: with no lint module it exits 3, never 0 (%s)" % r.returncode)


class Ledger:
    def __init__(self, ids=()):
        self.ids = ids

    def item(self, i):
        return i in self.ids


def t_one_list_for_a_meaning_nobody_finds():
    calls = []

    def run(a):
        calls.append(a)
        return 0, "ok"
    q = "Which program lands a trailing commit?"
    rc, text = G.unfindable("design/RimMandrake/standing_rulings.md", 12, "the belt", q, runner=run, tree=Ledger())
    flat = " ".join(calls[0]) if calls else ""
    check(rc == 0 and calls[0][0] == "file" and all(x in flat for x in ("standing_rulings.md:12", "the belt", q, "--caused-by")),
          "list: the first question files one ledger item with the file, the line, the term and the question (%s)" % flat)
    i = calls[0][1] if calls else ""
    check(i == G.list_id("design/RimMandrake/standing_rulings.md", "the belt") and len(i) <= 64, "list: the item's name is fixed for that term and file (%s)" % i)
    G.unfindable("design/RimMandrake/standing_rulings.md", 40, "the belt", "And here?", runner=run, tree=Ledger([i]))
    check(calls[1][:2] == ["note", i] and "And here?" in calls[1][3], "list: a later question on it is a note on that item, never a second item")
    rc, text = G.unfindable("CLAUDE.md", 12, "the belt", "  ", runner=run, tree=Ledger())
    check(rc == 2 and len(calls) == 2 and "question" in text, "list: an entry with no question is refused")


def t_the_recheck_sees_a_dead_check():
    r = G.recheck(write=False, coverage=False)
    check(r["ok"] is True and r["publish_door"] == "ok" and r["launch_door"] == "ok", "recheck: both doors return the planted fault (%s)" % r)
    for door, env in (("publish_door", {"RM_GUIDING_PROSE_CUT": "publish"}), ("launch_door", {"RM_GUIDING_PROSE_CUT": "launch"})):
        r = G.recheck(write=False, coverage=False, env=env)
        check(r["ok"] is False and r[door] != "ok" and r["cause"], "recheck: a check cut out of %s reads ok false with its cause (%s)" % (door, r))
    with tempfile.TemporaryDirectory() as tmp:
        c = repo(tmp)
        since = G.now_s() - 3600
        u = G.uncovered(c, since, rows=[])
        check(len(u) == 1 and u[0]["files"] == ["design/RimMandrake/debug_process.md"], "recheck: a landing with no record is named (%s)" % u)
        sha = g("rev-parse", "origin/main", cwd=c).strip()
        check(G.uncovered(c, since, rows=[{"landed": [sha]}]) == [], "recheck: a landing with its record is not")


def main():
    t_the_list_covers_the_census()
    t_the_three_lines_he_quoted_are_caught()
    t_the_repaired_lines_stay_green()
    t_each_form_fault_is_caught_and_named()
    t_exempt_text_stays_green()
    t_only_changed_sentences_are_read()
    t_the_reader_gets_only_what_changed()
    t_the_reader_answer_is_bound_to_the_line()
    t_an_uncalibrated_reader_sends_nothing_back()
    t_a_publish_with_faults_still_lands()
    t_a_launch_with_faults_still_starts()
    t_a_sentence_already_sent_in_a_brief_is_silent()
    t_a_principal_launch_gets_its_faults_before_the_start()
    t_a_brief_a_program_wrote_is_never_returned()
    t_a_broken_check_stops_nothing()
    t_a_principal_gets_a_note()
    t_the_check_verb_exits_for_a_caller()
    t_one_list_for_a_meaning_nobody_finds()
    t_the_recheck_sees_a_dead_check()
    print("%s: %d failure(s)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
