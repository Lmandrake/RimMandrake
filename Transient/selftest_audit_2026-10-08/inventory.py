#!/usr/bin/env python3
"""Static + recorded-timing inventory of every selftest the runner discovers. Audit only."""
import csv, json, re, sys, statistics
from pathlib import Path
REPO = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils"))
import run_selftests as R  # discovery is the runner's own, never a re-implementation
tests, excl = R.find_selftests()
TIM = {k: json.load(open(f)) for k, f in [("foundry", "/home/mandrake/.seat-tmp/FOUNDRY/selftest_timings.json"),
       ("bench", "/home/mandrake/.seat-tmp/BENCH/selftest_timings.json"), ("tmp", "/tmp/selftest_timings.json")]}
PK = {}
for f in ["/home/mandrake/.seat-tmp/FOUNDRY/selftest_peaks.json", "/home/mandrake/.seat-tmp/BENCH/selftest_peaks.json", "/tmp/selftest_peaks.json"]:
    for k, v in json.load(open(f)).items():
        PK[k] = max(PK.get(k, 0), v)
FLAGS = {
 "subprocess": r"\bsubprocess\.|os\.system\(|Popen\(",
 "spawns_python": r"sys\.executable|\[\s*['\"]python3",
 "python_exe": r"python\.exe|\.exe['\"]",
 "git": r"['\"]git['\"]|\bgit (?:-C|log|status|diff|rev-parse|show|init|commit|ls-files)",
 "drvfs": r"/mnt/[cd]/|[CD]:\\\\|Program Files|steamapps",
 "sleep": r"time\.sleep\(",
 "network": r"urllib|requests\.|socket\.|http\.client|curl",
 "defdump": r"def_dump|defdump|refresh\.py|dump_dir|DefDump|official",
 "savegame": r"\.rws\b",
 "modsconfig": r"ModsConfig",
 "bridge": r"rimbridge|bridge_client|GABP|jawa/",
 "tempdir": r"tempfile\.|mkdtemp|TemporaryDirectory",
 "copytree": r"copytree",
 "walks_repo": r"rglob\(|os\.walk\(|glob\.glob\(.*\*\*",
 "modpack_harness": r"import selftest_modpack_lint",
 "threads": r"ThreadPool|ProcessPool|multiprocessing",
}
rows = []
for p in tests:
    rel = p.relative_to(REPO).as_posix()
    txt = p.read_text(errors="replace")
    r = {"rel": rel, "lines": txt.count("\n") + 1}
    ts = [TIM[k].get(rel) for k in TIM]
    for k, v in zip(TIM, ts): r["t_" + k] = v if v is not None else ""
    known = [t for t in ts if t is not None]
    r["t_median"] = round(statistics.median(known), 1) if known else ""
    r["peak_mb"] = round(PK[rel] / 2**20) if rel in PK else ""
    for k, pat in FLAGS.items(): r[k] = len(re.findall(pat, txt))
    r["sub_calls"] = len(re.findall(r"subprocess\.(?:run|call|check_output|check_call|Popen)\(", txt))
    m = re.search(r"H\.run\(\s*['\"](\w+)['\"],\s*['\"]([\w.]+)['\"]", txt)
    r["lint_target"] = m.group(2) if m else ""
    r["plants"] = len(re.findall(r"^\s*\(\s*['\"]", txt, re.M)) if m else ""
    # file under test: selftest_X.py -> X.py / lint_X*.py in same dir, else first sibling import
    stem = p.stem[len("selftest_"):] if p.stem.startswith("selftest_") else ""
    cand = [c for c in ([p.with_name(stem + ".py")] if stem else []) if c.exists()]
    if r["lint_target"]: cand = [p.with_name(r["lint_target"])]
    if not cand:
        for imp in re.findall(r"^\s*(?:from|import)\s+([\w.]+)", txt, re.M):
            c = p.with_name(imp.split(".")[0] + ".py")
            if c.exists() and c != p and "selftest" not in c.name: cand = [c]; break
    r["under_test"] = cand[0].relative_to(REPO).as_posix() if cand else ""
    doc = re.search(r'"""(.*?)(?:\n|""")', txt, re.S)
    r["doc"] = (doc.group(1).strip() if doc else "")[:110]
    r["timeout_tag"] = R.per_test_timeout(p)
    rows.append(r)
out = REPO / "Transient/selftest_audit_2026-10-08/selftest_inventory.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
# sanity probe: known selftests must be found
names = {Path(r["rel"]).name for r in rows}
for probe in ("selftest_memwatch.py", "selftest_flyer_lock.py"):
    print("PROBE", probe, "FOUND" if probe in names else "MISSING")
tm = [r["t_median"] for r in rows if r["t_median"] != ""]
print(f"discovered {len(tests)} runnable, {len(excl)} excluded; timed {len(tm)}; sum median {sum(tm):.0f}s; untimed {len(rows)-len(tm)}")
print("wrote", out)
