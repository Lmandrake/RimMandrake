import ast, json, os, subprocess, sys, time
REPO = sys.argv[1]; OUT = sys.argv[2]
sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/rimflow"))
import light_scan as LS
FW = "src/RimMandrake/FlowWorks/northstar/concept_scenes.py"
def src_at(rev):
    return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, FW)], capture_output=True, text=True, check=True).stdout
def body(src, scene):
    tree = ast.parse(src)
    target = None
    for n in tree.body:   # scene_x = _run('scene_x', _body)
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == scene for t in n.targets) \
                and isinstance(n.value, ast.Call) and len(n.value.args) >= 2 and isinstance(n.value.args[1], ast.Name):
            target = n.value.args[1].id
    target = target or scene
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == target:
            return target, ast.get_source_segment(src, n)
    raise KeyError(scene)
def bar_words(bid):
    for f in ("tree.json", "record.json"):
        d = json.load(open(os.path.join(REPO, "design/concepts/FlowWorks", f)))
        found = []
        def walk(n):
            if isinstance(n, dict):
                if n.get("id") == bid:
                    found.append(n)
                for v in n.values(): walk(v)
            elif isinstance(n, list):
                for v in n: walk(v)
        walk(d)
        if found:
            n = found[0]
            return json.dumps({k: v for k, v in n.items() if k not in ("hash", "held", "signature")}, indent=1)
    return None
tt = json.load(open(os.path.join(REPO, "design/concepts/FlowWorks/version/test_table.json")))
CASES = [("bad", "99ff70d91a", "sc_coating_wash"), ("bad", "99ff70d91a", "sc_walk"),
         ("good", "HEAD", "sc_fill_front"), ("good", "HEAD", "sc_one_surface"), ("good", "HEAD", "sc_geyser_tub")]
rec = {"ticket": "RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED", "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
       "list": "scene_asks_bar", "model": "sonnet", "keep_rule": "flags both bad and at most one good", "cases": []}
raw = {}
def runner(argv, **kw):
    r = subprocess.run(argv, **kw); raw["stdout"] = r.stdout; return r
for kind, rev, sc in CASES:
    entry = tt["tests"][sc]["entry"]
    fn, text = body(src_at(rev), entry)
    bars = [b["id"] for b in tt["bars"] if sc in (b.get("decides") or [])]
    words = "\n\n".join("%s:\n%s" % (b, bar_words(b)) for b in bars)
    raw.clear()
    r = LS.scan("scene_asks_bar", "FlowWorks %s (%s at %s)" % (sc, fn, rev), {"bar": words, "scene": text}, runner=runner)
    try:
        w = json.loads(raw.get("stdout") or "{}")
    except ValueError:
        w = {}
    rec["cases"].append({"kind": kind, "rev": rev, "test": sc, "function": fn, "bars": bars,
                         "input_chars": len(words) + len(text), "ran": r["ran"], "ok": r["ok"],
                         "did_not_run": r["did_not_run"], "answers": r["answers"], "refusals": r["refusals"],
                         "usd": r["usd"], "usage": w.get("usage"), "model_usage": w.get("modelUsage")})
    print(kind, sc, "ok" if r["ok"] else "FLAGGED", r["did_not_run"] or "", r["usd"])
bad = [c for c in rec["cases"] if c["kind"] == "bad"]; good = [c for c in rec["cases"] if c["kind"] == "good"]
dnr = [c["test"] for c in rec["cases"] if c["did_not_run"]]
flag_bad = sum(1 for c in bad if c["ok"] is False); flag_good = sum(1 for c in good if c["ok"] is False)
rec["verdict"] = ("did not run on %s: no verdict" % dnr) if dnr else (
    "KEPT" if flag_bad == 2 and flag_good <= 1 else "NOT KEPT") + " (flagged %d of 2 bad, %d of 3 good)" % (flag_bad, flag_good)
rec["usd_total"] = sum(c["usd"] or 0 for c in rec["cases"])
json.dump(rec, open(OUT, "w"), indent=1)
print(rec["verdict"], rec["usd_total"])
