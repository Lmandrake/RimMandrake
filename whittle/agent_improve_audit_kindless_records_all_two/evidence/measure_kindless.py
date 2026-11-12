#!/usr/bin/env python3
"""Measurement for AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO. Read-only: the change records, git history of the
lessons inbox, the ledger shards, the Relentless store and the ops alarms. Optional argv[1]: a directory holding the
pre-change agent_improve.py (git archive of the commit before the fix) for the old-vs-new gather comparison."""
import calendar, collections, glob, importlib.util, json, os, re, subprocess, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
import agent_improve as A  # noqa: E402

def ep(s):
    try:
        return calendar.timegm(time.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return None

def count(changes_dir):
    """-> (kindless, total, rows): the one reader, used on the real records and on the probe alike."""
    recs = sorted(glob.glob(os.path.join(changes_dir, "*.json")))
    rows = [(os.path.basename(p), json.load(open(p))) for p in recs]
    return sum(1 for _n, d in rows if not d.get("source_kinds")), len(rows), rows


print("## 1. change records on file: source_kinds == [] out of all")
CH = os.path.join(REPO, "infrastructure/state/agent_improve/changes")
recs = sorted(glob.glob(os.path.join(CH, "*.json")))
k, n, rows = count(CH)
for name, d in rows:
    print("  %-28s day %s  pieces %d  source_kinds %r" % (name, d["day"], len(d["pieces"]), d.get("source_kinds")))
print("  KINDLESS %d of %d records" % (k, n))

# Sanity probe: a record written to disk by the production apply_change (temp git repo, fake publish), from a real
# lesson in the inbox that carries an item: footer, read back by the same count(). It can fail: if apply_change
# wrote [] or the reader could not see the list, it reads 1 of 1 kindless.
import shutil, tempfile
real = [p for p in sorted(glob.glob(os.path.join(REPO, "infrastructure/state/lessons/*.md"))) if A.lessons.item_of(p)
        and A.lessons.item_of(p) != "NONE"]
with tempfile.TemporaryDirectory() as tmp:
    repo, les = os.path.join(tmp, "repo"), os.path.join(tmp, "lessons")
    os.makedirs(os.path.join(repo, "skills", "probe"))
    os.makedirs(les)
    open(os.path.join(repo, "skills", "probe", "SKILL.md"), "w").write("# Probe\n\n- one line.\n")
    open(os.path.join(repo, "skills", "validate_skills.py"), "w").write("import sys\nsys.exit(0)\n")
    g = lambda *a: subprocess.run(["git", "-c", "user.email=p@p", "-c", "user.name=p", *a], cwd=repo, check=True,
                                  capture_output=True, text=True).stdout
    g("init", "-q"); g("add", "-A"); g("commit", "-qm", "base")
    shutil.copy(real[0], les)
    body = open(real[0], encoding="utf-8").read()
    open(os.path.join(les, os.path.basename(real[0])), "w", encoding="utf-8").write(
        "\n".join(l for l in body.splitlines() if not l.startswith("home:")) + "\nhome: probe\n")
    A.REPO, A.SKILLS = repo, os.path.join(repo, "skills")
    ent = A.target_entry("probe", 1, A.lesson_pieces(les, 0, 2 ** 31))
    res = A.resolve_target("probe")
    _nf, diff, _p = A.build_change(ent, res, open(os.path.join(repo, "skills/probe/SKILL.md")).read(),
                                   {"cites": [0], "fix_layer": "prompt", "recheck": "x",
                                    "edits": [{"old": "- one line.\n", "new": "- one line, probed.\n"}]})
    pub = lambda msg, paths, r: (g("add", "--", *paths) or True, g("commit", "-qm", "probe", "--", *paths) or
                                 g("rev-parse", "HEAD").strip())
    pch = os.path.join(repo, "infrastructure/state/agent_improve/changes")
    ok, why = A.apply_change({"target": "probe", "day": "2026-11-11", "path": res["path"], "verdict": "KEEP",
                              "judge": {"reasons": "probe", "violated": None}, "cites": [0], "recheck": "x", "diff": diff},
                             ent, os.path.join(tmp, "out"), repo=repo, publish=lambda m, p, r: (True, pub(m, p, r)[1]),
                             changes_dir=pch, delegated_dir=os.path.join(repo, "infrastructure/state/delegated"),
                             pk_level=0)
    pk, pn, prow = count(pch)
    print("  sanity probe: apply_change (L0, temp repo) on the real lesson %s (item: %s) wrote %s with source_kinds %r;"
          " the same reader counts KINDLESS %d of %d there (apply ok=%s)"
          % (os.path.basename(real[0]), A.lessons.item_of(real[0]), prow[0][0] if prow else "-",
             prow[0][1].get("source_kinds") if prow else None, pk, pn, ok))
    A.REPO = REPO

print("\n## 2. could the two records regain kinds from a sound source?")
for p in recs:
    d = json.load(open(p))
    for pc in d["pieces"]:
        rel = "infrastructure/state/lessons/" + os.path.basename(pc["path"])
        add = subprocess.run(["git", "log", "--all", "--diff-filter=A", "--format=%h %s", "--", rel],
                             cwd=REPO, capture_output=True, text=True).stdout.strip().splitlines()[-1]
        body = subprocess.run(["git", "show", "%s:%s" % (add.split()[0], rel)], cwd=REPO, capture_output=True, text=True).stdout
        t, seat = A.lessons.parse_name(rel)
        items = set()
        for ln in open(os.path.join(REPO, "infrastructure/state/ledger/events/%s.jsonl" % seat), errors="replace"):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            tt = ep(r.get("ts"))
            if tt and abs(tt - t) <= 3600 and r.get("id"):
                items.add(r["id"])
        print("  %s (%s): whole lesson body names an item -> kind %r; adding commit %r -> kind %r;"
              " seat %s touched %d distinct items within 1 h of it (%s)"
              % (os.path.basename(p), os.path.basename(rel), A.kind_of_text(body), add, A.kind_of_text(add[11:]),
                 seat, len(items), ", ".join(sorted({A.kind_of_text(i) or "?" for i in items}))))

print("\n## 3. how often a piece names its kind: first line (old) vs whole text (new)")
out = subprocess.run(["git", "log", "--all", "--diff-filter=A", "--format=@%h", "--name-only", "--",
                      "infrastructure/state/lessons/"], cwd=REPO, capture_output=True, text=True).stdout
first_add, cur = {}, None
for ln in out.splitlines():
    if ln.startswith("@"):
        cur = ln[1:]
    elif ln.endswith(".md") and not ln.endswith("README.md"):
        first_add.setdefault(ln, cur)
n = k_old = k_new = 0
for f, c in first_add.items():
    body = subprocess.run(["git", "show", "%s:%s" % (c, f)], cwd=REPO, capture_output=True, text=True).stdout
    if body:
        n += 1
        k_old += bool(A.kind_of_text(A.first_line(body)))
        k_new += bool(A.kind_of_text(body))
print("  every lesson ever filed (body at its adding commit): %d; kinded by first line %d (%.0f%%), by whole body %d (%.0f%%)"
      % (n, k_old, 100.0 * k_old / n, k_new, 100.0 * k_new / n))
live = sorted(glob.glob(os.path.join(REPO, "infrastructure/state/lessons/*.md")))
live = [p for p in live if A.lessons.parse_name(p)[0] is not None]
lb = [open(p, encoding="utf-8").read() for p in live]
print("  the live inbox: %d lessons; an item named in the first line %d, anywhere in the text %d, an item: footer %d"
      % (len(lb), sum(bool(A.kind_of_text(A.first_line(b))) for b in lb), sum(bool(A.kind_of_text(b)) for b in lb),
         sum(bool(A.lessons.item_of(p)) for p in live)))
src = A.default_src()
ps = A.collect(0, time.time() + 1, src)
c, k = collections.Counter(), collections.Counter()
for p in ps:
    kk = p["kind"].split(":")[0]
    c[kk] += 1
    k[kk] += bool(A.task_kind(p))
print("  every piece collect() sees now (new code), n / kinded:", {x: "%d / %d" % (c[x], k[x]) for x in sorted(c)})

if len(sys.argv) > 1:
    print("\n## 4. ordinary use: gather at L1 (bar: 2 task kinds) on the real sources, old code vs new")
    spec = importlib.util.spec_from_file_location("old_ai", os.path.join(sys.argv[1], "agent_improve.py"))
    sys.path.insert(0, sys.argv[1])
    O = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(O)
    for day in ["2026-11-%02d" % d for d in range(4, 12)]:
        po, pn = O.gather(day, src, A.LEVELS[1]), A.gather(day, src, A.LEVELS[1])
        kh = lambda pk: sorted(t for t, w in pk["held"].items() if "task kinds" in w)
        print("  %s  signalled old %-24s new %-40s held-for-kinds old %d new %d"
              % (day, [t["target"] for t in po["targets"]], [t["target"] for t in pn["targets"]], len(kh(po)), len(kh(pn))))
