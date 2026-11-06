#!/usr/bin/env python3
"""selftest_relentless_seeds.py - the seed bank's construction and the counting rules, on planted results."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "Utils"))
from selftest_own_dirs import own_dir_for_run  # noqa: E402
own_dir_for_run("relentless_seeds")     # every mkdtemp below lands in one dir that goes even when the run is killed
os.environ["RM_SEEDS_PRIVATE"] = tempfile.mkdtemp(prefix="seedpriv")
import relentless_seeds as S     # noqa: E402
import relentless_trust as T     # noqa: E402

FAILS = []


def check(name, ok, got=None):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append((name, got))


def git(d, *a, inp=None):
    return subprocess.run(["git", *a], cwd=d, input=inp, capture_output=True, text=True, check=True).stdout.strip()


def repo():
    d = tempfile.mkdtemp(prefix="seedrepo")
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "user.email", "a@b")
    git(d, "config", "user.name", "a")
    Path(d, ".claude/agents").mkdir(parents=True)
    Path(d, ".claude/agents/rm-judge.md").write_text("old judge\n")
    Path(d, "m.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "base")
    base = git(d, "rev-parse", "HEAD")
    Path(d, "m.py").write_text("a = 10\nb = 2\nc = 3\nd = 4\ne = 50\n")
    Path(d, "new.py").write_text("x = 1\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "the fix SECRETWORD")
    fix = git(d, "rev-parse", "HEAD")
    git(d, "tag", "future")
    return d, base, fix


def delivered(d, k):
    dest = Path(tempfile.mkdtemp(prefix="seeddest"), "case")
    return S.deliver(d, k, dest), str(dest)


def test_hunks_and_candidates():
    d, base, fix = repo()
    diff = git(d, "diff", "-U0", base, fix, "--", "m.py")
    hunks = S.split_hunks(diff + "\n")
    check("two hunks, each with its header", len(hunks) == 2 and all(p == "m.py" and "diff --git" in t for p, t in hunks), hunks)
    k = {"cls": "hunk_green", "fix": fix, "base": base, "item": "SD_X", "patch": hunks[1][1]}
    sha, c = delivered(d, k)
    check("one hunk out, the other kept", Path(c, "m.py").read_text() == "a = 10\nb = 2\nc = 3\nd = 4\ne = 5\n",
          Path(c, "m.py").read_text())
    check("the candidate is base + one commit", git(c, "rev-parse", sha + "^") == base)
    check("nothing in the delivered clone reaches the fix", "SECRETWORD" not in git(c, "log", "--all", "--format=%B")
          and subprocess.run(["git", "cat-file", "-e", fix], cwd=c, capture_output=True).returncode != 0
          and "future" not in git(c, "for-each-ref") and git(c, "remote") == "" )
    check("the Marker's definition is today's, the tree reads clean",
          Path(c, ".claude/agents/rm-judge.md").read_text() == (S.REPO / ".claude/agents/rm-judge.md").read_text()
          and git(c, "status", "--porcelain") == "", git(c, "status", "--porcelain"))
    # held in a reflog of the source, the fix must still not cross
    check("the source keeps the fix, the delivery does not", subprocess.run(
        ["git", "cat-file", "-e", fix], cwd=d, capture_output=True).returncode == 0)


def test_one_path_all_classes():
    d, base, fix = repo()
    _, c = delivered(d, {"cls": "all_red", "fix": fix, "base": base, "item": "SD_A", "paths": ["m.py", "new.py"]})
    check("all_red: source back at base, added file gone", Path(c, "m.py").read_text().startswith("a = 1\n")
          and not Path(c, "new.py").exists())
    d, base, fix = repo()
    want = git(d, "rev-parse", fix + "^{tree}")
    s1 = S.build_commit(d, {"cls": "control", "fix": fix, "base": base, "item": "SD_B"})
    check("control: the fix's tree on one commit", git(d, "rev-parse", s1 + "^{tree}") == want
          and git(d, "rev-parse", s1 + "^") == base)
    msg = {git(d, "log", "-1", "--format=%an|%B", s1).replace("SD_B", "ID")}
    check("message and author carry nothing of the class", msg == {"relentless worker|ID: the item's work"}, msg)
    d, base, fix = repo()
    Path(d, "infrastructure/state/code_review").mkdir(parents=True)
    Path(d, "infrastructure/state/code_review/h.jsonl").write_text("m.py hash\n")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "the fix's bookkeeping")
    fix2 = git(d, "rev-parse", "HEAD")
    git(d, "reset", "-q", "--soft", base)
    git(d, "commit", "-qm", "squashed fix")
    fix2 = git(d, "rev-parse", "HEAD")
    for cls, kw in (("control", {}), ("all_red", {"paths": ["m.py", "new.py"]})):
        sha = S.build_commit(d, dict(cls=cls, fix=fix2, base=base, item="SD_C", **kw))
        check("%s: a recorded review hash does not reach the Marker" % cls,
              "code_review" not in git(d, "ls-tree", "-r", "--name-only", sha))


def r(item, cls, verdict, **kw):
    return dict(item=item, cls=cls, verdict=verdict, contaminated=[], **kw)


def test_counting():
    res = [r("a", "hunk_red", "FAIL", path="x/foo.py", reasons="foo.py loses the guard"),
           r("b", "hunk_red", "FAIL", path="x/foo.py", reasons="the proof crashed"),
           r("c", "hunk_red", "PASS", path="x/foo.py"),
           r("b2", "hunk_red", "FAIL", path="x/foo.py", reasons="myfoo.py is wrong, as is foo.pyc"),
           r("e", "hunk_green", "PASS", path="x/g.py"),
           r("f", "hunk_green", "PASS", path="x/g.py"),
           r("g", "hunk_green", None),
           dict(r("h", "hunk_green", "PASS"), contaminated=["books"]),
           r("i", "control", "PASS"), r("j", "control", "FAIL", reasons="bad"), r("k", "escaped", "FAIL", reasons="z")]
    keys = [dict(item=x["item"], cls=x["cls"]) for x in res] + [dict(item="d", cls="hunk_green"), dict(item="z", cls="hunk_green")]
    reads = {"d": "equivalent", "e": "observable", "f": "observable", "g": "observable", "h": "observable"}
    c = T.compute(res, reads, keys)
    x = c["classes"]["hunk_red"]
    check("caught counts FAIL; on target is the whole name", (x["caught"], x["n"], x["on_target"]) == (3, 4, 1), x)
    g = c["classes"]["hunk_green"]
    check("equivalent never ran and is listed", (g["caught"], g["n"], g["removed"]) == (0, 2, 1) and c["removed_equivalent"] == ["d"], g)
    check("a planned case with no result is unrun, in neither count", g["unrun"] == 1 and c["unread"] == ["z"], g)
    check("planned adds up", g["planned"] == g["n"] + g["unrun"] + g["lost"] + g["contaminated"] + g["removed"], g)
    check("lost is neither caught nor a miss", c["lost"] == ["g"])
    check("contaminated is dropped and listed", c["contaminated"] == ["h"])
    check("control false fail, with reasons", (c["control"]["false_fail"], c["control"]["n"]) == (1, 2)
          and c["control"]["reasons"] == {"j": "bad"})
    check("escaped has no on-target test", c["classes"]["escaped"]["on_target"] is None)
    check("on target: a name with a space", T.on_target({"path": "src/a b.py", "reasons": "Regression in src/a b.py"}))
    check("on target: a Windows path", T.on_target({"path": "src/a.py", "reasons": r"Regression in C:\repo\src\a.py"}))
    check("on target: another file is no hit", not T.on_target({"path": "src/a.py", "reasons": "b.py and ba.py and a.pyc"}))
    check("on target: a longer extension is no hit", not T.on_target({"path": "src/a.py", "reasons": "in a.py.bak and a.py-old"}))
    check("on target: end of sentence is a hit", T.on_target({"path": "src/a.py", "reasons": "the guard in a.py."}))
    lo, hi = T.wilson(0, 30)
    check("Wilson is Wilson at zero, not 3/n", lo == 0.0 and 0.11 < hi < 0.12, hi)
    live = {"done": 0, "ended": 0, "first_checks": 0, "first_fails": 0}
    check("rule of three is said apart", "at most 25% (rule of three)" in T.rule3(0, 12, "misses") and T.rule3(1, 12, "x") == "")
    empty = T.render(T.compute([]), live, "x")
    check("an empty measure prints UNMEASURED, never 0", "| Finish rate | UNMEASURED |" in empty and "0 of" not in empty, empty)
    text = T.render(c, live, "accepted by Judge at E1", {"in_set": 5, "dropped_at_delivery": [{}]})
    check("never says trusted", "trusted" not in text.lower())
    check("the report carries the population and the control's reason", "in_set" in text and "control FAIL j: bad" in text, text)


def test_counting_weak():
    res = [r("a", "hunk_green", "FAIL", path="x/g.py", reasons="g.py wrong"), r("b", "hunk_green", "WEAK", path="x/g.py"),
           r("c", "hunk_green", "PASS", path="x/g.py"), r("d", "control", "WEAK"), r("e", "control", "PASS"),
           r("f", "control", "FAIL", reasons="bad")]
    c = T.compute(res, {"a": "observable", "b": "observable", "c": "observable"}, [dict(item=x["item"], cls=x["cls"]) for x in res])
    g = c["classes"]["hunk_green"]
    check("WEAK on a seed is no catch and no miss", (g["caught"], g["weak"], g["n"]) == (1, 1, 3), g)
    x = c["control"]
    check("WEAK on a control is no false fail, and is counted", (x["false_fail"], x["weak"], x["n"], x["weak_items"]) == (1, 1, 3, ["d"]), x)
    check("WEAK is no lost run", not c["lost"])
    text = T.render(c, {"done": 0, "ended": 0, "first_checks": 2, "first_fails": 0, "first_weak": 1}, "x")
    check("the report prints WEAK apart", "1 more WEAK" in text and "Control WEAK" in text and "first-check WEAK rate | 1 of 2" in text, text)
    a = [{"end": "proof_weak"}, {"end": "done"}]
    live = T.live_rates([], [a])
    check("a first WEAK counts as a first check", (live["first_checks"], live["first_weak"], live["first_fails"]) == (1, 1, 0), live)


def test_box_transcripts_need_no_session():
    d = Path(tempfile.mkdtemp())
    f = d / "projects" / "-x" / "abc.jsonl"
    f.parent.mkdir(parents=True)
    f.write_text(json.dumps({"message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls /rm/bench"}}]}}) + "\n", encoding="utf-8")
    check("a box is scanned with no session id", S.tool_inputs(None, str(d)) == [{"command": "ls /rm/bench"}])
    check("an empty box stays unscanned", S.tool_inputs(None, tempfile.mkdtemp()) is None)


def test_arm_pins_one_marker():
    d = Path(tempfile.mkdtemp(prefix="arm-"))
    old = S.PRIVATE
    S.PRIVATE = d
    try:
        S.pin_arm("v1", "fp1")
        S.pin_arm("v1", "fp1")
        check("an arm has its own results dir", S.results_dir(True, "v1") == d / "results_v1" and S.results_dir(True) == d / "results_wall")
        try:
            S.pin_arm("v1", "fp2")
            check("a second Marker in one arm is refused", False)
        except SystemExit as e:
            check("a second Marker in one arm is refused", "another Marker" in str(e), e)
    finally:
        S.PRIVATE = old
    now = S.fingerprint()
    orig = S.W.RULE
    S.W.RULE = orig[:1]
    try:
        check("the fingerprint covers the Marker's words", S.fingerprint() != now)
    finally:
        S.W.RULE = orig


def test_contamination_scan():
    k = {"fix": "abcdef0123456789abcd"}
    C = lambda *cmds, **kw: S.contamination([{"command": c} for c in cmds], k, **kw)    # noqa: E731
    verdict = "python3 %s verdict --item X --nonce n PASS 'all good'" % S.BOOKS_VERB
    check("the verdict command is clean", C(verdict) == [], C(verdict))
    check("a read chained to the verdict is seen", "/relentless/" in C(verdict + "; cat /home/mandrake/rm/relentless/store/x"))
    check("a pipe after the verdict is seen", C(verdict + " | tee /home/mandrake/rm/relentless/x") != [])
    check("a read of the keys is seen", C("cat %s/keys/E1.json" % S.PRIVATE) != [])
    check("a tool input other than a command is seen", S.contamination([{"file_path": "/home/mandrake/rm/bench/x"}], k) == ["/rm/bench"])
    check("the books beyond the verdict are seen", C("git -C /home/mandrake/rm/relentless/books log") == ["/relentless/"])
    check("a seat clone is seen", C("ls /home/mandrake/rm/bench") == ["/rm/bench"])
    check("the repo's own arena folder is no alarm", C("ls src/RimMandrake/Utils/arena/") == [])
    check("shell quoting does not hide the arena", C("cat %s/are''na/judge/hidden/T.json" % "/mnt/d/ClaudeWork/rimmandrake") != [])
    own = "/home/mandrake/rm/relentless-seeds/cases/SD_A-a1"
    check("its own case dir is no alarm", C("ls %s/src" % own, own=own) == [])
    check("the case parent is", C("ls /home/mandrake/rm/relentless-seeds/cases", own=own) == ["relentless-seeds"])
    check("cd to its own case, then the verdict, is clean", C("cd %s; %s" % (own, verdict), own=own) == [])
    check("cd && verdict is clean", C("cd %s && %s" % (own, verdict), own=own) == [])
    check("a status echo after the verdict is clean", C("cd %s; %s; echo exit=$?" % (own, verdict), own=own) == [])
    check("2>&1 on the verdict is clean", C(verdict + " 2>&1") == [])
    check("a tail on the verdict is clean", C(verdict + " | tail -3") == [])
    check("a verdict with an extra word is not exempt", C(verdict + " /home/mandrake/rm/bench/x") != [])
    check("a read on a new line after the verdict is seen", C(verdict + "\ncat /home/mandrake/rm/relentless/store/x") != [])
    check("a read inside the reasons is seen", C("python3 %s verdict --item X --nonce n PASS \"$(cat /home/mandrake/rm/bench/x)\"; true" % S.BOOKS_VERB) == ["/rm/bench"])
    check("a read after a shell comment trick is seen", C(verdict + "; cat x#y /home/mandrake/rm/bench/f") == ["/rm/bench"])
    check("cd own, verdict, then a read is seen", C("cd %s; %s; cat /home/mandrake/rm/relentless/store/x" % (own, verdict), own=own) != [])
    check("a read between cd and the verdict is seen",
          C("cd %s; cat /home/mandrake/rm/relentless/store/x; %s" % (own, verdict), own=own) != [])
    check("the fix's sha is seen", C("git show abcdef0123") == ["abcdef0123"])
    for q in ("'&&'", '"&&"', "\\&\\&", "';'"):
        c = "cat -- %s %s --item /rm/foundry/secret --nonce N accept reasons" % (q, "python3 " + S.BOOKS_VERB + " verdict")
        check("a quoted operator hides no read: %s" % q, "/rm/foundry" in C(c), C(c))
    check("an operator inside the reasons is still the verdict",
          C("python3 %s verdict --item X --nonce n PASS 'a && b'" % S.BOOKS_VERB) == [])
    ev = []
    S.contamination([{"command": "ls /home/mandrake/rm/bench/src"}], k, evidence=ev)
    check("a hit keeps the text around it", len(ev) == 1 and ev[0]["hit"] == "/rm/bench" and "ls /home/mandrake/rm/bench/src" in ev[0]["text"])
    check("no transcript is not clean", S.contamination(None, k) == ["unscanned"])
    nested = {"message": {"content": [{"type": "text", "text": "cat /rm/bench"}, {"type": "tool_use", "input": {"command": "x"}}]},
              "toolUseResult": {"inner": [{"type": "tool_use", "input": {"file_path": "y"}}]}}
    check("tool calls are found at any depth, text is not one", list(S.tool_calls(nested)) == [{"command": "x"}, {"file_path": "y"}]
          or sorted(map(str, S.tool_calls(nested))) == sorted(map(str, [{"command": "x"}, {"file_path": "y"}])))


def test_outcome_reads_lines():
    check("sh syntax error is broken, not red", S.outcome(2, "sh: 1: Syntax error: \"(\" unexpected") == "broken")
    check("a FAIL line is red", S.outcome(1, "[1/1] FAIL  0.1s  a.py") == "red")
    check("a PASS line is green", S.outcome(0, "[1/1] PASS  0.1s  a.py") == "green")
    check("a CRASH line is broken", S.outcome(1, "[1/1] CRASH  0.1s  a.py") in ("broken", "red"))


def test_split_and_pick_are_hash_only():
    a = {("t%d" % i): int(S.h("split|t%d" % i)[:8], 16) % 100 for i in range(300)}
    check("the hash spreads", 25 < sum(v < 16 for v in a.values()) < 70)
    d, base, fix = repo()
    Path(d, "m.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")
    git(d, "checkout", "-q", "-f", "main")
    t = {"base_sha": base, "prompt": "w", "criteria": "c"}

    def hid(label=None, rc=()):
        return {"fix_sha": fix, "label": label, "reworks": [], "rework_candidates": list(rc), "fix_files": ["m.py"]}
    tasks = {n: (dict(t, id=n, proof="p"), hid()) for n in ("a", "b", "c", "d")}
    tasks["esc"] = (dict(t, id="esc", proof="p"), hid("Escaped"))
    tasks["rw"] = (dict(t, id="rw", proof="p"), hid(rc=["later"]))
    fixok = {"kind": "fix", "out": "green"}
    h0 = {"kind": "hunk", "out": "green", "hunk": 0, "path": "m.py"}
    h1 = {"kind": "hunk", "out": "red", "hunk": 1, "path": "m.py"}
    census = {"a": [fixok, h0, h1], "b": [dict(fixok, out="red"), h0], "c": [fixok, h1], "d": [dict(fixok, out="broken"), h1],
              "rw": [fixok, h0], "esc": []}
    keys, frame = S.pick_set("E1", {n: "E1" for n in tasks}, tasks, census, d, 1e12)
    cls = sorted((k["task"], k["cls"]) for k in keys)
    check("one seed per task, a fix not green gives none, an escape is taken whatever",
          ("esc", "escaped") in cls and not [c for c in cls if c[0] in ("b", "d")]
          and len({c[0] for c in cls if c[1] != "control"}) == len([c for c in cls if c[1] != "control"]), cls)
    check("a rework candidate is in no class", not [c for c in cls if c[0] == "rw"], cls)
    check("the frame says what it cut", (frame["in_set"], frame["fix_green"], frame["fix_broken"], frame["in_frame"]) == (6, 3, 1, 2), frame)
    check("the hunk comes with its whole patch", all("diff --git" in k["patch"] for k in keys if "hunk" in k["cls"]), keys)
    check("the words are kept for the reader and the Marker", all(k["words"].startswith("w") for k in keys))
    check("a picking is repeatable", S.pick_set("E1", {n: "E1" for n in tasks}, tasks, census, d, 1e12)[0] == keys)


def test_pick_fresh_takes_only_unrun_cases():
    d, base, fix = repo()
    Path(d, "m.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")
    git(d, "checkout", "-q", "-f", "main")
    t = {"base_sha": base, "prompt": "w", "criteria": "c"}
    hid = {"fix_sha": fix, "label": None, "reworks": [], "rework_candidates": [], "fix_files": ["m.py"]}
    tasks = {n: (dict(t, id=n, proof="p"), hid) for n in ("a", "b", "c", "e2")}
    fixok = {"kind": "fix", "out": "green"}
    h0 = {"kind": "hunk", "out": "green", "hunk": 0, "path": "m.py"}
    h1 = {"kind": "hunk", "out": "red", "hunk": 1, "path": "m.py"}
    census = {n: [fixok, h0, h1] for n in tasks}
    split = {"a": "E1", "b": "E1", "c": "tune", "e2": "E2"}
    old = [{"cls": "control", "task": "a"}, {"cls": "hunk_green", "task": "b", "hunk": 0}, {"cls": "all_red", "task": "c"}]
    used = S.used_cases([old])
    check("used cases are read by class", used == ({"a"}, {("b", 0)}, {"c"}), used)
    keys, frame = S.pick_fresh("W1", ["E1", "tune"], split, tasks, census, d, 1e12, used)
    cases = {(k["task"], k["cls"], k.get("hunk")) for k in keys}
    check("no control run twice, no hunk taken twice", ("a", "control", None) not in cases
          and ("b", "hunk_green", 0) not in cases, cases)
    check("E2 is never drawn from", not [c for c in cases if c[0] == "e2"], cases)
    check("fresh controls and seeds are both found", {c[1] for c in cases} >= {"control", "hunk_green", "hunk_red"}, cases)
    check("one seed per task", len([c for c in cases if c[1] != "control"]) == len({c[0] for c in cases if c[1] != "control"}), cases)
    check("a fresh picking is repeatable", S.pick_fresh("W1", ["E1", "tune"], split, tasks, census, d, 1e12, used)[0] == keys)
    try:
        S.pick_fresh("W1", ["E2"], split, tasks, census, d, 1e12, used)
        check("E2 as a source is refused", False)
    except SystemExit:
        check("E2 as a source is refused", True)


def test_assign_rare_class_first():
    capable = {"x": ["hunk_green", "hunk_red"], "y": ["hunk_green"], "z": ["hunk_green", "all_red"], "w": ["all_red", "hunk_red"]}
    got = S.assign(list(capable), capable)
    placed = sum(got.values(), [])
    check("no task twice, none lost while a class has room", sorted(placed) == sorted(capable), got)
    check("the one-class task keeps its class", "y" in got["hunk_green"], got)
    quota = dict(S.QUOTA)
    many = {"t%d" % i: ["hunk_green"] for i in range(40)}
    got = S.assign(list(many), many)
    check("a quota is a ceiling", len(got["hunk_green"]) == quota["hunk_green"], got)


def test_census_log():
    log = Path(tempfile.mkdtemp(prefix="seedlog"), "c.jsonl")
    S.append_row(log, {"task": "a", "kind": "fix"})
    with open(log, "a", encoding="utf-8") as f:
        f.write('  tail of a torn row"}\n')
    S.append_row(log, {"task": "b", "kind": "fix"})
    check("a torn row is no row, the rest stand", [r["task"] for r in S.census_rows(log)] == ["a", "b"])
    with open(log, "a", encoding="utf-8") as f:
        f.write('{"task":"T","kind":')
    S.append_row(log, {"task": "T", "kind": "fix"})
    check("a retry after a torn row is kept", [r["task"] for r in S.census_rows(log)] == ["a", "b", "T"])
    fresh = Path(log.parent, "new.jsonl")
    S.append_row(fresh, {"task": "x"})
    check("a first row on a new log", S.census_rows(fresh) == [{"task": "x"}] and fresh.read_bytes().count(b"\n") == 1)


def test_second_read_frozen():
    keys = S.PRIVATE / "keys"
    keys.mkdir(parents=True, exist_ok=True)
    (keys / "FRZ.json").write_text(json.dumps([{"item": "FRZ_c1", "cls": "other"}]), encoding="utf-8")
    d = S.PRIVATE / "results_frz"
    d.mkdir(exist_ok=True)
    (d / "OTHER_SET.json").write_text("{}", encoding="utf-8")
    seen = []
    real = S.sh
    S.sh = lambda *a, **k: seen.append(a)
    try:
        import types
        out = S.PRIVATE / "reads" / "FRZ.answer.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text("", encoding="utf-8")
        S.cmd_read(types.SimpleNamespace(set="FRZ"))
        check("another set's results freeze nothing", len(seen) == 1, seen)
        (d / "FRZ_c1.json").write_text("{}", encoding="utf-8")
        try:
            S.cmd_read(types.SimpleNamespace(set="FRZ"))
            check("a measured case freezes the second reads", False)
        except SystemExit as e:
            check("a measured case freezes the second reads", "frozen" in str(e), e)
        check("and no read was spent", len(seen) == 1, seen)
    finally:
        S.sh = real


def test_verdict_and_journal():
    check("the walled verdict is the verdict", S.is_verdict({"command": 'python3 /b/x/verdict FAIL "a b"'}, "/b/x"))
    check("a chained walled verdict is not", not S.is_verdict({"command": 'python3 /b/x/verdict FAIL "a" ; cat y'}, "/b/x"))
    check("a walled verdict names no contaminant", S.contamination(
        [{"command": 'python3 /b/x/verdict FAIL "see /rm/bench"'}], {"fix": "f" * 40}, "/b/x", "/b/x") == [])
    check("words must match the prompt's verdict", not S.is_verdict({"command": "python3 src/x.py verdict --item X --nonce n PASS r"}))
    check("no command, no verdict", not S.is_verdict({"file_path": "x"}))
    item = "SD_J"
    check("a new case has used no attempts", S.attempts_used(item) == 0)
    S.journal(item, {"state": "started", "attempt": 1})
    S.journal(item, {"item": item, "verdict": None})
    S.journal(item, {"state": "started", "attempt": 2})
    check("attempts count across invocations, by the started rows", S.attempts_used(item) == 2)
    old = S.PRIVATE
    S.PRIVATE = Path(tempfile.mkdtemp(prefix="jr-"))
    try:
        S.journal("SD_T", {"state": "started"})
        with open(S.PRIVATE / "attempts/SD_T.jsonl", "a", encoding="utf-8") as f:
            f.write('{"state":"started"')
        check("a torn journal line is skipped, not fatal", S.attempts_used("SD_T") == 1)
        S.journal("SD_T", {"state": "started"})
        check("an append after a torn line is its own row", S.attempts_used("SD_T") == 2)
        for bad in ("wall", "", "a/b", ".."):
            try:
                S.pin_arm(bad, "fp")
                check("arm name refused: %r" % bad, False)
            except SystemExit:
                check("arm name refused: %r" % bad, True)
    finally:
        S.PRIVATE = old

    class Store:
        def load(self, i):
            return {"check": {"verdict": self.v}}
        v = None

    class Rl:
        def verdict(self, store, i, n, word, why, at):
            store.v = word

    box = tempfile.mkdtemp(prefix="pv-")
    st = Store()
    check("no verdict file, no word", S.poll_verdict(Rl(), st, "I", "n", box) is None)
    Path(box, "verdict.json").write_text('{"word": "FAIL", "reasons": "r", "at": 1}', encoding="utf-8")
    check("a verdict written before the Marker exits is taken on the reread", S.poll_verdict(Rl(), st, "I", "n", box) == "FAIL")


def test_compare_against_step0():
    """Step 3: the same set read twice. Pairs only cases counted on both sides; a real read is apart from `unscanned`."""
    keys = [dict(item=i, cls=c) for i, c in (("a", "hunk_green"), ("b", "hunk_green"), ("c", "control"), ("d", "control"),
                                              ("e", "hunk_red"), ("q", "hunk_green"))]
    base = [r("a", "hunk_green", "FAIL", secs=10, tokens=5), r("b", "hunk_green", "PASS", secs=30, tokens=7),
            r("c", "control", "FAIL", reasons="x"), dict(r("d", "control", "PASS"), contaminated=["books"]),
            r("e", "hunk_red", "FAIL"), r("q", "hunk_green", "PASS")]
    arm = [dict(r("a", "hunk_green", "PASS", secs=20, tokens=0), walled=True), dict(r("b", "hunk_green", "PASS"), walled=True),
           dict(r("c", "control", "WEAK"), walled=True), dict(r("d", "control", "PASS"), walled=True),
           dict(r("e", "hunk_red", "FAIL"), walled=True, contaminated=["unscanned"])]
    x = T.compare(base, arm, {"a": "observable", "b": "observable", "q": "equivalent"}, keys, arm_print="f" * 64)
    check("pairs: a flips, b holds, c flips; d and e not paired (one side out)",
          x["pairs"] == {"hunk_green": {"FAIL>PASS": 1, "PASS>PASS": 1}, "control": {"FAIL>WEAK": 1}}, x["pairs"])
    check("flips name the case", x["flips"] == [("a", "hunk_green", "FAIL", "PASS"), ("c", "control", "FAIL", "WEAK")], x["flips"])
    check("an equivalent-removed case is never paired", "q" not in str(x["flips"]))
    check("real read vs unscanned kept apart", x["contam_base"] == (["d"], []) and x["contam_arm"] == ([], ["e"]),
          (x["contam_base"], x["contam_arm"]))
    check("a walled token count of 0 is no measurement", x["tokens"] == (7, None) and x["secs"] == (30, 20), (x["tokens"], x["secs"]))
    check("the arm's Marker comes from arm.json", x["fingerprints"][1] == ["f" * 12])
    text = T.render_compare(x, "S")
    check("render: paired column, UNMEASURED tokens, flips listed",
          "FAIL>PASS 1" in text and "| Median tokens | 7 | UNMEASURED |" in text and "flip a (hunk_green): FAIL -> PASS" in text, text)


def main():
    test_hunks_and_candidates()
    test_one_path_all_classes()
    test_counting()
    test_counting_weak()
    test_compare_against_step0()
    test_arm_pins_one_marker()
    test_box_transcripts_need_no_session()
    test_contamination_scan()
    test_outcome_reads_lines()
    test_split_and_pick_are_hash_only()
    test_assign_rare_class_first()
    test_pick_fresh_takes_only_unrun_cases()
    test_census_log()
    test_second_read_frozen()
    test_verdict_and_journal()
    if FAILS:
        print(json.dumps(FAILS, default=str)[:1500])
    print("selftest_relentless_seeds:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
