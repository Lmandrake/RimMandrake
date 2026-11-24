#!/usr/bin/env python3
"""Lint: a time budget in pipeline machinery names its danger, and is at least 10 times the longest real run it guards.

Owner, 2026-11-24: *"Why do we have time budgets all over? ... Aren't time budgets for detecting out-of-control or stuck
programs? Why do we have them set to within 10% of what the process really needs?"* The rule: root CLAUDE.md section "No
limit without the danger it guards". Page: design/specs/2026-11-24-time-budgets/boundary.md. Census: census.md beside it.

A budget is found by its name and a number: a `timeout=` argument, a constant, a parameter default or an argparse
default in .py; a key in .json; Timeout*Sec, RuntimeMaxSec, WatchdogSec and --max-seconds in a systemd unit; `timeout N` in
.sh. A name from time_budget.py (CALL_S, PUBLISH_S) is not a number of its own, and is green.

A budget is GREEN when one of these holds:
1. Its tag names `danger=` and `longest=`, and the number is at least FACTOR times `longest`. The tag is a `# budget:`
   comment on the line or in the lines just above it (in .json the string `_<key>` beside the key):
       # budget: danger=a hung git holds the tick; evidence=<incident, date>; longest=12s (<record>)
   `# budget: class=publish` names a class of time_budget.CLASSES, which holds both once. `stays=<reason>` after it keeps a
   number under FACTOR times (an owner's limit, a machine-safety brake, or a number that does not end live work).
   In place of `longest=`, a tag with no record of the run says one of three things:
       `never reached in the 14 days to <date>; no record of its run`    the records of reaches were read, and show none
       `its reach leaves no record; no record of its run`                a reach could not have been seen
       `ends no work: <what happens when the time passes>`               a refresh, an alarm, a wait, a size
   `longest=UNMEASURED` is RED: it is no class (owner, 2026-11-24: "They aren't unmeasured... we can measure them."). A NEW
   budget takes a time_budget.py name, or the time of one measured run.
2. It is in time_budgets.json: a budget that stood before this lint (2026-11-24), at that value or higher, with its
   `longest_s`. An entry with no `longest_s` has no class, and is RED. An entry is held to FACTOR unless it has `stays`. A
   lowered number is a new budget.
3. It stands inside a test and is in time_budgets.json with `in_test`: a budget that stood when the lint began to read the
   tests. The runner's guard ends the test, so nobody measured it. A NEW or lowered one is checked as any budget, and
   `# budget: fixture` is green there: a number that the test feeds to the code under test.

    python3 src/RimMandrake/Utils/time_budget_lint.py            report; exit 0 green, 1 red, 2 UNMEASURED (blind)
    python3 src/RimMandrake/Utils/time_budget_lint.py --list     every budget found, tab-separated
    python3 src/RimMandrake/Utils/time_budget_lint.py --prune    drop entries of budgets that are gone
"""
import ast
import fnmatch
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import time_budget  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KNOWN = os.path.join(HERE, "time_budgets.json")
PIPELINE = "src/RimMandrake/Utils/pipeline_tests.json"
# machinery that ends work by the clock and is not in pipeline_files
ALSO = ("src/RimMandrake/Utils/publish.py", "src/RimMandrake/Utils/publish_tree_checks.json", "src/RimMandrake/Utils/run_selftests.py",
        "src/RimMandrake/Utils/call_deadline_lint.py", "src/RimMandrake/Utils/progress_guard.py",
        "src/RimMandrake/Utils/time_budget.py", "src/RimMandrake/Utils/metronome.py",
        "src/RimMandrake/Utils/scratch_reap.py", "src/RimMandrake/Utils/rimbridge_client.py",
        "src/RimMandrake/Utils/slot_rules.json", "src/RimMandrake/rimflow/dispatcher.py",
        "src/RimMandrake/rimflow/dispatcher_schedule.json", "src/RimMandrake/rimflow/role_launch.py",
        "src/RimMandrake/Utils/systemd/*", "src/RimMandrake/Utils/testq/*.py",
        "infrastructure/stevedesktop/*.py", "infrastructure/stevedesktop/*.sh")
NAME = re.compile(r"timeout|deadline|budget_s\b|max_seconds|max_wait|max_age|lease|expir|silence|silent_s|stall|hung|stale|"
                  r"fresh|ttl|grace|blind_s|limit_s\b|cap_s\b|(^|_)(max|wait|stop|wall|bound|kill|limit|recover|verify|"
                  r"handoff|cleanup|cooldown|live|call|cmd|run|start|probe|reader|git|load|hold|settle)_s$|_max_s$|"
                  r"run_max|pre_launch_max|_wait$", re.I)
NOT_TIME = re.compile(r"usd|chars|bytes|_mb|_gb|count|tries|attempts|tokens|pct|lines", re.I)
UNIT_LINE = re.compile(r"^(Timeout(?:Start|Stop)?Sec|RuntimeMaxSec|WatchdogSec)=(.+)$")
MAX_SECONDS = re.compile(r"--max-seconds[ =](\d+)")
SH_TIMEOUT = re.compile(r"\btimeout\s+(?:-\S+\s+)*(\d+)([smh]?)\s")
SPAN = {"": 1, "s": 1, "sec": 1, "min": 60, "m": 60, "h": 3600}


class Budget:
    def __init__(self, rel, line, scope, name, value, tag, kind):
        self.rel, self.line, self.scope, self.name, self.value, self.tag, self.kind = rel, line, scope, name, value, tag, kind

    @property
    def key(self):
        return "%s::%s::%s" % (self.rel, self.scope, self.name)


def seconds(name, value):
    n = name.rsplit(".", 1)[-1]
    if re.search(r"ms$", n):
        return value / 1000.0
    if re.search(r"(^|_)(min|minutes)$", n, re.I):
        return value * 60.0
    if re.search(r"(^|_)(h|hours)$", n, re.I):
        return value * 3600.0
    if re.search(r"(^|_)days$", n, re.I):
        return value * 86400.0
    return float(value)


NO_RECORD = re.compile(r"(never reached in the 14 days to \d{4}-\d\d-\d\d|its reach leaves no record); no record of its run")
NO_WORK = re.compile(r"\bends no work: \S")
FIXTURE = re.compile(r"^fixture\b")


def is_test(rel):
    base = os.path.basename(rel)
    return base.startswith("selftest") or "/acceptance/" in rel or base.endswith(("_accept.py", "_mutants.py"))


def parse_tag(text):
    """-> {danger, longest (seconds, None = no record), state, stays} or None when the text is no tag. `state` is the class:
    RECORD, NEVER REACHED, REACH NOT RECORDED, ENDS NO WORK, or NO CLASS (an UNMEASURED longest run)."""
    m = re.search(r"\bclass=([a-z_]+)", text or "")
    if m:       # a class names its danger and its longest real run once (time_budget.CLASSES)
        c = time_budget.CLASSES.get(m.group(1))
        return {"danger": c["danger"], "longest": float(c["longest_s"]), "state": "RECORD", "stays": ""} if c else None
    if not text or "danger=" not in text:
        return None
    f = dict((m.group(1), m.group(2).strip()) for m in re.finditer(
        r"(danger|evidence|longest|stays)=(.*?)(?=;\s*(?:(?:danger|evidence|longest|stays)=|never reached|its reach leaves|ends no work:)|$)",
        text, re.S))
    if not f.get("danger") or f["danger"].lower().startswith(("none", "unknown")):
        return None
    if "longest=" not in text:
        m = NO_RECORD.search(text)
        state = (("NEVER REACHED" if m.group(1).startswith("never") else "REACH NOT RECORDED") if m else
                 "ENDS NO WORK" if NO_WORK.search(text) else None)
        return {"danger": f["danger"], "longest": None, "state": state, "stays": f.get("stays") or ""} if state else None
    m = re.match(r"(\d+(?:\.\d+)?)\s*(ms|s|min|h)?\b", f.get("longest", ""))
    if m:
        longest = float(m.group(1)) * {"ms": 0.001, "s": 1, None: 1, "min": 60, "h": 3600}[m.group(2)]
    elif f.get("longest", "").upper().startswith("UNMEASURED"):
        longest = None
    else:
        return None
    return {"danger": f["danger"], "longest": longest, "state": "NO CLASS" if longest is None else "RECORD",
            "stays": f.get("stays") or ""}


def comment_tag(lines, i):
    """The `# budget:` text on line i (0-based) and in the comment lines just above it."""
    got = []
    for j in range(i - 1, max(-1, i - 9), -1):
        t = lines[j].strip()
        if not t.startswith("#"):
            break
        if re.match(r"#\s*budget:", t):
            got.insert(0, re.sub(r"^#\s*budget:\s*", "", t))
    m = re.search(r"#\s*budget:\s*(.*)$", lines[i])
    if m:
        got.append(m.group(1))
    return " ".join(got)


def _num(node):
    ok = (ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop)
    if not all(isinstance(n, ok) or (isinstance(n, ast.Constant) and isinstance(n.value, (int, float))) for n in ast.walk(node)):
        return None
    v = eval(compile(ast.Expression(node), "<n>", "eval"), {"__builtins__": {}})   # numbers and arithmetic only
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 else None


class _Py(ast.NodeVisitor):
    def __init__(self, rel, lines):
        self.rel, self.lines, self.stack, self.out = rel, lines, [], []

    def add(self, node, name, value, kind):
        if value is None or not NAME.search(name) or NOT_TIME.search(name):
            return
        self.out.append(Budget(self.rel, node.lineno, ".".join(self.stack) or "<module>", name, seconds(name, value),
                               comment_tag(self.lines, node.lineno - 1), kind))

    def _scope(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_ClassDef = _scope

    def visit_FunctionDef(self, node):
        a = node.args
        pos = a.posonlyargs + a.args
        pairs = list(zip(pos[len(pos) - len(a.defaults):], a.defaults)) if a.defaults else []
        pairs += [(p, d) for p, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None]
        for p, d in pairs:
            self.add(d, p.arg, _num(d), "default of %s()" % node.name)
        self._scope(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, (ast.Name, ast.Attribute)):
                self.add(node, t.id if isinstance(t, ast.Name) else t.attr, _num(node.value), "constant")
        self.generic_visit(node)

    def visit_Call(self, node):
        fn = ast.unparse(node.func)
        if fn.endswith("add_argument") and node.args and isinstance(node.args[0], ast.Constant):
            flag = str(node.args[0].value).strip("-").replace("-", "_")
            for k in node.keywords:
                if k.arg == "default":
                    self.add(node, flag, _num(k.value), "argument default")
        for k in node.keywords:
            if k.arg and k.arg not in ("default",):
                self.add(k.value, k.arg, _num(k.value), "argument of %s()" % fn)
        self.generic_visit(node)


def budgets_in_py(rel, text):
    v = _Py(rel, text.splitlines())
    v.visit(ast.parse(text))
    return v.out


def budgets_in_json(rel, text):
    out, lines = [], text.splitlines()

    def walk(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
                    if NAME.search(k) and not NOT_TIME.search(k):
                        at = next((i + 1 for i, ln in enumerate(lines) if '"%s"' % k in ln), 1)
                        out.append(Budget(rel, at, path or "<top>", k, seconds(k, v), x.get("_" + k) or "", "json"))
                else:
                    walk(v, (path + "." if path else "") + str(k))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                name = v.get("name") if isinstance(v, dict) else None
                walk(v, "%s[%s]" % (path, name or i))
    walk(json.loads(text), "")
    return out


def span(text):
    """systemd time span -> seconds, or None (infinity)."""
    t = text.strip()
    if t in ("infinity", "0"):
        return None
    parts = re.findall(r"(\d+(?:\.\d+)?)\s*([a-z]*)", t)
    s = sum(float(n) * SPAN.get(u, 1) for n, u in parts)
    return s if s > 0 else None


def budgets_in_unit(rel, text):
    out, lines = [], text.splitlines()
    for i, ln in enumerate(lines):
        m = UNIT_LINE.match(ln.strip())
        if m and span(m.group(2)):
            out.append(Budget(rel, i + 1, "<unit>", m.group(1), span(m.group(2)), comment_tag(lines, i), "unit"))
        m = MAX_SECONDS.search(ln)
        if m and not ln.lstrip().startswith("#"):
            out.append(Budget(rel, i + 1, "<unit>", "--max-seconds", float(m.group(1)), comment_tag(lines, i), "unit"))
    return out


def budgets_in_sh(rel, text):
    out, lines = [], text.splitlines()
    for i, ln in enumerate(lines):
        if not ln.lstrip().startswith("#"):
            for m in SH_TIMEOUT.finditer(ln):
                out.append(Budget(rel, i + 1, "<sh>", "timeout", float(m.group(1)) * SPAN[m.group(2)],
                                  comment_tag(lines, i), "sh"))
    return out


def scope_files(repo=REPO, files=None):
    """-> the tracked files in scope, or None when git could not be read. COULD NOT LOOK is not an empty scope."""
    if files is None:
        r = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, text=True, timeout=time_budget.CALL_S)
        if r.returncode != 0:
            return None
        files = [f for f in r.stdout.split("\0") if f]
    globs = tuple(json.load(open(os.path.join(repo, PIPELINE), encoding="utf-8"))["pipeline_files"]) + ALSO
    return [f for f in files if any(fnmatch.fnmatch(f, g) for g in globs)
            and not f.startswith(("src/RimMandrake/Utils/scene_contracts/", "infrastructure/state/"))
            and f != "src/RimMandrake/Utils/time_budgets.json"]


def scan(repo=REPO, files=None):
    """-> (budgets, unread [(rel, why)]), or (None, why) when the scope could not be read."""
    files = scope_files(repo, files)
    if files is None:
        return None, "git ls-files failed"
    out, unread = [], []
    for rel in sorted(files):
        read = (budgets_in_py if rel.endswith(".py") else budgets_in_json if rel.endswith(".json") else
                budgets_in_sh if rel.endswith(".sh") else
                budgets_in_unit if rel.endswith((".service", ".timer", ".conf", ".slice", ".path")) else None)
        if read is None:
            continue
        try:
            out += read(rel, open(os.path.join(repo, rel), encoding="utf-8").read())
        except (OSError, SyntaxError, ValueError) as e:
            unread.append((rel, "%s: %s" % (type(e).__name__, e)))
    return out, unread


def load_known(path=KNOWN):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["budgets"]


def judge(budgets, known):
    """-> red messages. A budget is matched to a known entry by its key; values are matched as a multiset."""
    reds = []
    left = {k: sorted(v["values"]) for k, v in known.items()}
    for b in sorted(budgets, key=lambda b: (b.key, b.value)):
        where = "%s:%d %s = %g s" % (b.rel, b.line, b.name, b.value)
        if is_test(b.rel) and FIXTURE.match(b.tag):
            continue
        t = parse_tag(b.tag)
        if t:
            if t["state"] == "NO CLASS":
                reds.append("%s has no class (longest=UNMEASURED): read its run from a record, or measure one run, or use a "
                            "time_budget.py name" % where)
            if t["longest"] is not None and b.value < time_budget.FACTOR * t["longest"] and not t["stays"]:
                reds.append("%s is %.1f times its longest real run (%g s): raise it to %g s, or guard on progress "
                            "(progress_guard.py)" % (where, b.value / t["longest"] if t["longest"] else 0, t["longest"],
                                                     time_budget.FACTOR * t["longest"]))
            continue
        e = known.get(b.key)
        fit = [v for v in left.get(b.key, ()) if v <= b.value]
        if not e or not fit:
            reds.append("%s is a %s and names no danger: use time_budget.CALL_S, or add `# budget: danger=...; "
                        "evidence=...; longest=<N>s (<record>, or one measured run)`%s"
                        % (where, "lowered budget" if e and left.get(b.key) else "new budget",
                           "; a number that the test feeds to the code under test: `# budget: fixture`" if is_test(b.rel) else ""))
            continue
        left[b.key].remove(fit[-1])
        longest = e.get("longest_s")
        if not longest and not (e.get("in_test") and is_test(b.rel)):
            reds.append("%s has no class: its entry in time_budgets.json holds no longest_s. Name its danger in a `# budget:` "
                        "tag, and its record or `never reached in the 14 days to <date>; no record of its run`" % where)
        elif longest and len(set(e["values"])) > 1:
            reds.append("%s has no class: its entry in time_budgets.json holds one longest_s for unlike budgets (%s). Give each "
                        "a `# budget:` tag" % (where, e["values"]))
        if longest and b.value < time_budget.FACTOR * longest and not e.get("stays"):
            reds.append("%s is %.1f times its longest real run (%g s, time_budgets.json)" % (where, b.value / longest, longest))
    return reds


def prune(budgets, known):
    """-> the entries cut to the values that are still there and untagged."""
    have = {}
    for b in budgets:
        if not parse_tag(b.tag) and not (is_test(b.rel) and FIXTURE.match(b.tag)):
            have.setdefault(b.key, []).append(b.value)
    out = {}
    for k, e in known.items():
        if k in have:
            out[k] = dict(e, values=sorted(have[k]))
    return out


def classes(budgets, known):
    """-> {class: count}. A budget inside a test is counted apart."""
    out = {}
    for b in budgets:
        t, e = parse_tag(b.tag), known.get(b.key) or {}
        k = ("IN A TEST" if is_test(b.rel) else t["state"] if t else
             "RECORD" if e.get("longest_s") and len(set(e["values"])) == 1 else "NO CLASS")
        out[k] = out.get(k, 0) + 1
    return out


def main(argv):
    budgets, unread = scan()
    if budgets is None:
        print("UNMEASURED: %s" % unread)
        return 2
    if not budgets:
        print("UNMEASURED: no time budget found (the scan is blind)")
        return 2
    known = load_known()
    if "--list" in argv:
        for b in budgets:
            print("\t".join([b.rel, str(b.line), b.scope, b.name, "%g" % b.value, b.kind, b.tag]))
        return 0
    if "--prune" in argv:
        doc = json.load(open(KNOWN, encoding="utf-8"))
        doc["budgets"] = dict(sorted(prune(budgets, known).items()))
        with open(KNOWN, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1)
            fh.write("\n")
        known = doc["budgets"]
    reds = judge(budgets, known)
    tagged = sum(1 for b in budgets if parse_tag(b.tag))
    print("time budget lint: %d budgets, %d with a tag, %d with none (time_budgets.json, or red), FACTOR %d"
          % (len(budgets), tagged, len(budgets) - tagged, time_budget.FACTOR))
    print("classes: " + ", ".join("%s %d" % kv for kv in sorted(classes(budgets, known).items())))
    for rel, why in unread:
        print("RED %s could not be read (%s)" % (rel, why))
    for r in reds:
        print("RED " + r)
    print("RESULT: %s" % ("RED %d" % (len(reds) + len(unread)) if reds or unread else "GREEN"))
    return 1 if reds or unread else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
