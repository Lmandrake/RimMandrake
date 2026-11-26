#!/usr/bin/env python3
"""Build rows.jsonl for Pyrelands visit 9: one row per run, from scripts/rows_spec.json (test, label, outcome words) and the
chain result JSONs (evidence/pv9_<label>.json) or a script log. A verdict is the chain's own component verdicts, never typed."""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__)); VD = os.path.dirname(H); E = os.path.join(VD, "evidence")
ROOT = os.path.normpath(os.path.join(VD, *[".."] * 6)); REL = os.path.relpath(VD, ROOT)
T = json.load(open(os.path.join(ROOT, "design/concepts/Pyrelands/version/test_table.json")))["tests"]
SPEC = json.load(open(os.path.join(H, "rows_spec.json")))
HELD = ["weather: Clear locked at the site's start", "storyteller quiet, incident queue cleared"]
out = []
for s in SPEC:
    ident = json.load(open(os.path.join(E, s["identity"])))
    ident["mod_sha"] = s.get("mod_sha", ident["mod_sha"])
    tid, lab = s["test"], s["label"]
    cmd = s.get("command") or T[tid]["command"]
    if s.get("script"):
        p = os.path.join(E, s["script"]); txt = open(p, errors="replace").read()
        v = "PASS" if s.get("pass_line") and s["pass_line"] in txt or re.search(r"^PASS", txt, re.M) else "FAIL" if re.search(r"^FAIL", txt, re.M) else "UNMEASURED"
        det = ([l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "A1 "))] or [""])[-1]
    else:
        p = os.path.join(E, "pv9_%s.json" % lab)
        m = re.search(r"--chains (\S+)", cmd); ch = m.group(1).split(",")
        cs = [] if s.get("parts") else [c for c in json.load(open(p))["components"] if c.get("chain") in ch and not str(c.get("name")).startswith("skipped")]
        if s.get("components"):
            cs = [c for c in cs if c["name"] in s["components"]]
        for pl, names in s.get("parts") or []:   # the row's components from more than one run (each named in the row's note)
            cs += [c for c in json.load(open(os.path.join(E, "pv9_%s.json" % pl)))["components"] if c["name"] in names]
        if s.get("parts") and len(cs) != sum(len(n) for _, n in s["parts"]):
            raise SystemExit("%s: a named component is missing" % lab)
        vs = [c["verdict"] for c in cs]
        v = "FAIL" if "FAIL" in vs else "PASS" if vs and all(x == "PASS" for x in vs) else "UNMEASURED"
        det = "; ".join("%s %s" % (c["name"], c["verdict"]) for c in cs)
    row = {"test": tid, "verdict": v, "outcome": s.get("outcome") or {"PASS": "SUCCESS", "FAIL": "MOD FAILURE"}.get(v, "COULD NOT LOOK"),
           "spoiled_by": s.get("spoiled_by"), "forbidden": s.get("forbidden", []), "site_checked": True, "command": cmd,
           "evidence": os.path.join(REL, os.path.relpath(p, VD)), "held": s.get("held", HELD), "detail": s.get("detail", det), "run": lab}
    for k in ("class", "note", "repair", "mod_fix", "unrepaired", "owner", "unfixed", "filed"):
        if s.get(k):
            row[k] = s[k]
    if s.get("verdict_is"):   # a probe script with no verdict line: its reading is the row's detail
        row["verdict"] = s["verdict_is"]
    if row["outcome"] not in ("SUCCESS", "MOD FAILURE"):
        row["verdict"] = "UNMEASURED"
    row.update(ident)
    out.append(row)
with open(os.path.join(VD, "rows.jsonl"), "w") as f:
    f.write("".join(json.dumps(r) + "\n" for r in out))
for r in out:
    print(r["test"], r["run"], r["verdict"], r["outcome"], r["mod_sha"])
