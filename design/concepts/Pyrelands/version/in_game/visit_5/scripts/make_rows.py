#!/usr/bin/env python3
"""Build rows.jsonl for Pyrelands visit 5 from the per-chain result JSONs (evidence/pv5_<label>.json), the script logs,
the identity line and overrides.json (per test: which label to read, class, repair, unrepaired, owner, filed, detail).
A check reads its entry's components when the entry names components of the chain, else every component of the chain."""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
VD = os.path.normpath(os.path.join(H, ".."))
E = os.path.join(VD, "evidence")
ROOT = os.path.normpath(os.path.join(VD, *[".."] * 6))
REL = os.path.relpath(VD, ROOT)
T = json.load(open(os.path.join(ROOT, "design/concepts/Pyrelands/version/test_table.json")))["tests"]
IDENT = json.load(open(os.path.join(E, "identity_pyrelands.json")))
OV = json.load(open(os.path.join(H, "overrides.json"))) if os.path.exists(os.path.join(H, "overrides.json")) else {}
TOUCHED = set(open(os.path.join(H, "touched.txt")).read().split())   # rerun_relation.py RERUN lines; the rest carry visit 3
HELD = ["weather: Clear locked at the site's start", "storyteller quiet, incident queue cleared"]


def chain_of(cmd):
    m = re.search(r"--chains (\S+)", cmd or "")
    return m.group(1) if m else None


def read_chain(label, chain, entry):
    p = os.path.join(E, "pv5_%s.json" % label)
    if not os.path.exists(p):
        return "UNMEASURED", "not run: no %s" % os.path.relpath(p, ROOT), None, False
    d = json.load(open(p))
    if d.get("refused"):
        return "UNMEASURED", "driver refused: %s" % d["refused"], p, False
    comps = [c for c in d.get("components", []) if c.get("chain") in str(chain).split(",")]   # a command may name two chains
    pick = [c for c in comps if c.get("name") == entry or str(c.get("name")).startswith(entry + "#")] or comps
    if not pick:
        return "UNMEASURED", "chain %s wrote no component rows" % chain, p, True
    log = open(os.path.join(E, "run_%s.log" % label), encoding="utf-8", errors="replace").read() \
        if os.path.exists(os.path.join(E, "run_%s.log" % label)) else ""
    det = {}
    for ln in log.splitlines():
        m = re.match(r"component ((?:%s)/[^:]+): (\{.*)" % "|".join(re.escape(c) for c in str(chain).split(",")), ln)
        if m:
            try:
                det[m.group(1)] = json.loads(m.group(2)).get("detail")
            except ValueError:
                pass
    vs = [c["verdict"] for c in pick]
    v = "FAIL" if "FAIL" in vs else ("UNMEASURED" if any(x != "PASS" for x in vs) else "PASS")
    parts = ["%s %s%s" % (c["name"], c["verdict"], (": " + str(det.get("%s/%s" % (c.get("chain"), c["name"])))[:300])
                          if c["verdict"] != "PASS" and det.get("%s/%s" % (c.get("chain"), c["name"])) else "") for c in pick]
    return v, "; ".join(parts), p, True


def read_script(label):
    p = os.path.join(E, "script_%s.log" % label)
    if not os.path.exists(p):
        return "UNMEASURED", "not run: no %s" % os.path.relpath(p, ROOT), None
    txt = open(p, encoding="utf-8", errors="replace").read()
    rc = OV.get("_script_rc", {}).get(label)
    if rc is None and os.path.exists(os.path.join(E, "runner.log")):
        for ln in open(os.path.join(E, "runner.log")):   # the last run of this script names its exit code
            m = re.match(r"DONE \+?script:\S*?([^/@\s]+?)(?:\.py)?(?:@(\S+))? reload_rc=\S+ rc=(\d+)", ln)
            if m and (m.group(2) or m.group(1)) == label:
                rc = int(m.group(3))
    tail = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("[bridge split]")][-3:]
    v = {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}.get(rc, "UNMEASURED")
    return v, " | ".join(tail)[:400], p


def prior_rows(tid, e, o):
    """The earlier runs of a repaired or re-run check, each with its class: one row per run, before the counted one."""
    out = []
    for pr in o.get("prior") or []:
        ch = chain_of(e.get("command"))
        v, detail, ev, site = read_chain(pr["label"], ch, e.get("entry") or ch)
        r = {"test": tid, "verdict": v, "site_checked": bool(site), "game": "archmagi", "mod_sha": IDENT["mod_sha"],
             "command": e.get("command"), "evidence": os.path.relpath(ev, ROOT) if ev else None,
             "held": pr.get("held", HELD), "detail": detail, "run": pr["label"]}
        for k in ("class", "note"):
            if k in pr:
                r[k] = pr[k]
        ident = json.load(open(os.path.join(E, o["identity"]))) if o.get("identity") else IDENT
        if o.get("identity"):
            r["mod_sha"] = ident.get("mod_sha", r["mod_sha"])
        r.update({k: ident[k] for k in ("mod_hash", "game_build", "active_mods", "tier", "full_list", "unit") if k in ident})
        out.append(r)
    return out


EXTRA = set(OV.get("_extra_tests", []))   # untouched checks an owed case asked this visit to run (a row each)
rows = []
for tid, e in sorted(T.items()):
    if str(e.get("stage")) != "6" or (tid not in TOUCHED and tid not in EXTRA):
        continue
    o = OV.get(tid, {})
    rows.extend(prior_rows(tid, e, o))
    cmd = e.get("command")
    if o.get("verdict_fixed"):
        v, detail, ev, site = o["verdict_fixed"], o.get("detail", ""), o.get("evidence"), o.get("site_checked", False)
    elif cmd.startswith("python.exe src/RimMandrake/Utils/northstar_driver"):
        ch = chain_of(cmd)
        v, detail, ev, site = read_chain(o.get("label", ch), ch, e.get("entry") or ch)
    else:
        lab = os.path.basename(cmd.split()[1])[:-3]
        v, detail, ev = read_script(o.get("label", lab))
        site = ev is not None
    row = {"test": tid, "verdict": v, "site_checked": bool(site), "game": "archmagi", "mod_sha": IDENT["mod_sha"],
           "command": cmd, "evidence": os.path.relpath(ev, ROOT) if ev else None, "held": o.get("held", HELD),
           "detail": o.get("detail_prefix", "") + detail, "run": o.get("label") or "(table command)"}
    for k in ("class", "repair", "unrepaired", "owner", "filed", "mod_fix", "unfixed", "planted_faults", "note"):
        if k in o:
            row[k] = o[k]
    if "unrepaired" in o and row["verdict"] != "UNMEASURED":   # a needed check not shown both ways is not counted
        row["detail"] = "not counted (unrepaired, see `unrepaired`); its components read %s: %s" % (row["verdict"], row["detail"])
        row["verdict"] = "UNMEASURED"
    ident = json.load(open(os.path.join(E, o["identity"]))) if o.get("identity") else IDENT   # a full-list row's own line
    if o.get("identity"):
        row["mod_sha"] = ident.get("mod_sha", row["mod_sha"])
    row.update({k: ident[k] for k in ("mod_hash", "game_build", "active_mods", "tier", "full_list", "unit") if k in ident})
    rows.append(row)
with open(os.path.join(VD, "rows.jsonl"), "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
from collections import Counter
last = {}
for r in rows:
    last[r["test"]] = r
print(len(rows), "rows;", len(last), "checks; last rows:", dict(Counter(r["verdict"] for r in last.values())))
for r in last.values():
    if r["verdict"] != "PASS":
        print("%-11s %-32s %s %s" % (r["verdict"], r["test"], r.get("class", "-"), r["detail"][:150]))


# the Exit block: each check's last row; a check counts pass only when its last row is PASS with the site checked
def exit_block():
    strange = [json.loads(x) for x in open(os.path.join(VD, "strange.jsonl")) if x.strip()]
    open_n = sum(1 for x in strange if x.get("status") not in ("explained", "filed"))
    ing = ", ".join("%s: %s" % (k, ("pass" if (r["verdict"] == "PASS" and r["site_checked"]) else
                                    "fail" if r["verdict"] == "FAIL" else "unmeasured"))
                    for k, r in sorted(last.items()))
    met = all(r["verdict"] == "PASS" and r["site_checked"] for r in last.values()) and open_n == 0
    return ("## Exit\n\n```\ningame_rows: {%s}\nstrange_open: %d\nsavegame: %s\nexit_met: %s\n```\n"
            % (ing, open_n, SAVE, "true" if met else "false"))


_ws = os.path.join(E, "walk_save_full.json")   # the labelled save on his full list (walk_save.py ..._FULL): sc_walk is a full-list check
SAVE = ((json.load(open(_ws)).get("save") or {}).get("path") or "").replace("/", "\\") if os.path.exists(_ws) else None
if "--exit" in sys.argv:
    p = os.path.join(VD, "SUMMARY.md")
    s = open(p).read()
    i = s.index("## Exit")
    open(p, "w").write(s[:i] + exit_block())
    print("Exit block written")
