"""Visit 2 rows: one row per in-game check from the driver's evidence JSONs (python3, offline).

A check's verdict is read from every component of the chain(s) it runs (components marked 'chain not run' are skipped):
any FAIL -> FAIL, else any UNMEASURED -> UNMEASURED, else PASS (none read -> UNMEASURED). Each row merges the identity
line build_match.py printed for the loaded tier (evidence/identity_<tier>.json). ANNOT adds class / repair / unrepaired
/ owner / filed for a non-PASS row, written by the driver after the diagnosis. Rows are written in order; a later run
of the same check is a later row.
  python3 .../make_rows.py <test>=<evidence json>[,<json>...][#chainA+chainB][@tier] ...   (appends to rows.jsonl)"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(V2, *[".."] * 5))
REL = os.path.relpath(V2, ROOT)
DRIVER = ("python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan "
          "src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains %s")
ANNOT_FILE = os.path.join(HERE, "annotations.json")


def verdict(paths, chains):
    comps = []
    for p in paths:
        d = json.load(open(os.path.join(ROOT, p)))
        for c in d.get("components") or []:
            det = str(c.get("detail") or c.get("evidenceFull") or "")
            if "chain not run" in det or (chains and c.get("chain") not in chains):
                continue
            comps.append(c)
    vs = [c.get("verdict") for c in comps]
    v = "FAIL" if "FAIL" in vs else "UNMEASURED" if ("UNMEASURED" in vs or not vs) else "PASS"
    bad = ["%s %s: %s" % (c.get("verdict"), c.get("name"), str(c.get("evidenceFull") or "")[:220])
           for c in comps if c.get("verdict") != "PASS"]
    return v, len(comps), bad


def main(argv):
    annot = json.load(open(ANNOT_FILE)) if os.path.exists(ANNOT_FILE) else {}
    out = []
    for spec in argv:
        test, _, rest = spec.partition("=")
        rest, _, tier = rest.partition("@")
        tier = tier or "pyrelands"
        rest, _, only = rest.partition("#")
        paths = rest.split(",")
        chains = set()
        for p in paths:
            d = json.load(open(os.path.join(ROOT, p)))
            chains |= set(d.get("chains_selected") or [])
        if only:
            chains &= set(only.split("+"))
        v, n, bad = verdict(paths, chains)
        ident = json.load(open(os.path.join(V2, "evidence", "identity_%s.json" % tier)))
        row = {"test": test, "verdict": v, "site_checked": True, "game": "archmagi",
               "mod_sha": ident.get("mod_sha"), "command": DRIVER % ",".join(sorted(chains)),
               "evidence": paths[0] if len(paths) == 1 else paths, "held": [],
               "site": "NS_Pyrelands_site_1_bf7f9e1fe4_visit2 (tile 3), reloaded before the run; the driver re-ran gate B "
                       "(plan.preflight) and refuses a dirty site",
               "components": n}
        if bad:
            row["not_pass"] = bad
        row.update({k: v2 for k, v2 in ident.items() if k not in row or k in ("mod_sha", "game")})
        row.update(annot.get(test, {}).get(paths[0], annot.get(test, {}).get("*", {})))
        out.append(row)
    with open(os.path.join(V2, "rows.jsonl"), "a", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    for r in out:
        print(r["test"], r["verdict"], r.get("class", ""), r["components"])


if __name__ == "__main__":
    main(sys.argv[1:])
