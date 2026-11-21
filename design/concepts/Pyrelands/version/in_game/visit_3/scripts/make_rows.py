#!/usr/bin/env python3
"""Build rows.jsonl for Pyrelands visit 3 from the per-chain result JSONs (evidence/pv3_<label>.json), the script logs,
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
HELD = ["weather: Clear locked at the site's start", "storyteller quiet, incident queue cleared"]


def chain_of(cmd):
    m = re.search(r"--chains (\S+)", cmd or "")
    return m.group(1) if m else None


def read_chain(label, chain, entry):
    p = os.path.join(E, "pv3_%s.json" % label)
    if not os.path.exists(p):
        return "UNMEASURED", "not run: no %s" % os.path.relpath(p, ROOT), None, False
    d = json.load(open(p))
    if d.get("refused"):
        return "UNMEASURED", "driver refused: %s" % d["refused"], p, False
    comps = [c for c in d.get("components", []) if c.get("chain") == chain]
    pick = [c for c in comps if c.get("name") == entry or str(c.get("name")).startswith(entry + "#")] or comps
    if not pick:
        return "UNMEASURED", "chain %s wrote no component rows" % chain, p, True
    log = open(os.path.join(E, "run_%s.log" % label), encoding="utf-8", errors="replace").read() \
        if os.path.exists(os.path.join(E, "run_%s.log" % label)) else ""
    det = {}
    for ln in log.splitlines():
        m = re.match(r"component (%s/[^:]+): (\{.*)" % re.escape(chain), ln)
        if m:
            try:
                det[m.group(1)] = json.loads(m.group(2)).get("detail")
            except ValueError:
                pass
    vs = [c["verdict"] for c in pick]
    v = "FAIL" if "FAIL" in vs else ("UNMEASURED" if any(x != "PASS" for x in vs) else "PASS")
    parts = ["%s %s%s" % (c["name"], c["verdict"], (": " + str(det.get("%s/%s" % (chain, c["name"])))[:300])
                          if c["verdict"] != "PASS" and det.get("%s/%s" % (chain, c["name"])) else "") for c in pick]
    return v, "; ".join(parts), p, True


def read_script(label):
    p = os.path.join(E, "script_%s.log" % label)
    if not os.path.exists(p):
        return "UNMEASURED", "not run: no %s" % os.path.relpath(p, ROOT), None
    txt = open(p, encoding="utf-8", errors="replace").read()
    rc = OV.get("_script_rc", {}).get(label)
    tail = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("[bridge split]")][-3:]
    v = {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}.get(rc, "UNMEASURED")
    return v, " | ".join(tail)[:400], p


rows = []
for tid, e in sorted(T.items()):
    if str(e.get("stage")) != "6":
        continue
    o = OV.get(tid, {})
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
           "detail": o.get("detail_prefix", "") + detail}
    for k in ("class", "repair", "unrepaired", "owner", "filed", "mod_fix", "unfixed", "planted_faults", "note"):
        if k in o:
            row[k] = o[k]
    row.update({k: IDENT[k] for k in ("mod_hash", "game_build", "active_mods", "tier", "unit") if k in IDENT})
    rows.append(row)
with open(os.path.join(VD, "rows.jsonl"), "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
from collections import Counter
print(len(rows), dict(Counter(r["verdict"] for r in rows)))
for r in rows:
    if r["verdict"] != "PASS":
        print("%-11s %-32s %s %s" % (r["verdict"], r["test"], r.get("class", "-"), r["detail"][:150]))
