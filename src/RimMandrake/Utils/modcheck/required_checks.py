"""modcheck.required_checks -- the REQUIRED-CHECK MANIFEST (observatory step S0).

Rules: design/RimMandrake/bridge_validation_observatory.md section 2.4 (normative).

One row per mod that has a `validation.py` or a validation walk. Each mod lists the
checks a run is EXPECTED to produce, with their source:

  north_star_bar   a must-show line of a VALIDATED, hash-matching `## north star`
                   section -- the owner's bar (owner=True)
  must_show_line   a must-show line of a DRAFT section -- agent-seeded (owner=False)
  script_check     a `with t.component(...)` block in validation.py, enumerated
                   offline by the same no-op probe `floor`/`runner` use (owner=False)
  checkout_row     a row the mod's CHECKOUT emits (walk header `checkout: <script>`; the
                   script's declared_rows()) that no script_check already mirrors; a
                   mirroring script_check carries `checkout_row` instead (owner=False)

`cannot_show` lines are listed with required=False: no component is obliged to claim
them (`northstar.text_for`), so they never enter the denominator.

This module only READS walks and scripts; it never edits a north-star section.

    python3 required_checks.py            rebuild required_checks.json
    python3 required_checks.py --check    exit 1 if the committed manifest is stale
    python3 required_checks.py --mod X    print one mod's rows

Known limit, stated rather than hidden: the offline probe makes every bridge verb a
no-op, so a component declared only inside a branch that depends on a live result is
invisible here. The report shows such components as `observed, not in manifest`.
"""
import contextlib
import hashlib
import io
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for _p in (_HERE, _UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import northstar  # noqa: E402
import walklint   # noqa: E402

ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
MANIFEST = os.path.join(_HERE, "required_checks.json")
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")


def _rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:16]


def script_checks(mod_dir):
    """[(chain, component, toggle, shows)] declared by `mod_dir/validation.py`, or
    raises. Each chain is probed on a FRESH no-op context, mirroring
    Suite.components_declared but keeping the names (that function drops them)."""
    import runner
    from suite import _DeclarationProbe
    with contextlib.redirect_stdout(io.StringIO()):
        suite = runner.load_validation(mod_dir)
    out = []
    for chain, fn in suite.chains:
        probe = _DeclarationProbe()
        with contextlib.redirect_stdout(io.StringIO()):
            fn(probe)
        for c in probe.components:
            out.append((chain, c.name, c.toggle, list(c.shows)))
    return out


def walk_checkout(walk_path):
    """The `checkout:` header of a walk (repo-relative script path), or None. Read from the header lines above
    the first `## ` heading only -- never from inside a section (the north star is hash-bound)."""
    with open(walk_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                return None
            if line.lower().startswith("checkout:"):
                v = line.split(":", 1)[1].split()
                return v[0] if v else None
    return None


_ENUM = ("import importlib.util, json, os, sys\n"
         "p = sys.argv[1]; sys.path.insert(0, os.path.dirname(p))\n"
         "s = importlib.util.spec_from_file_location('_checkout_' + os.path.basename(p)[:-3], p)\n"
         "m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
         "f = getattr(m, 'declared_rows', None)\n"
         "print('ROWS_JSON ' + json.dumps(f() if f else None))\n")


def checkout_rows(script_rel):
    """The row ids the checkout script declares it emits (its `declared_rows()`), enumerated in a SUBPROCESS so
    the checkout's own module names (`validation`, ...) never collide with the suites loaded here. Raises."""
    import subprocess
    p = os.path.join(ROOT, script_rel)
    if not os.path.isfile(p):
        raise FileNotFoundError("checkout script %s does not exist" % script_rel)
    r = subprocess.run([sys.executable, "-c", _ENUM, p], capture_output=True, text=True, timeout=300, cwd=ROOT)
    for ln in reversed(r.stdout.splitlines()):
        if ln.startswith("ROWS_JSON "):
            rows = json.loads(ln[len("ROWS_JSON "):])
            if rows is None:
                raise ValueError("%s has no declared_rows()" % script_rel)
            return rows
    raise RuntimeError("enumerating %s printed no ROWS_JSON (exit %s): %s"
                       % (script_rel, r.returncode, (r.stdout + r.stderr).strip()[-300:]))


def _mod_dirs():
    out = {}
    for tier in TIERS:
        base = os.path.join(ROOT, "src", tier)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if os.path.isfile(os.path.join(base, name, "validation.py")):
                out.setdefault(name, []).append(os.path.join(base, name))
    return out


def _add_checkout(row, script_rel):
    """Join the checkout's row ids onto the manifest row. A script_check whose component name IS a checkout row id
    (validation.py's mirror chains: FlowWorks core_live_rows, GSS live_battery / proof_all_only_rows) is marked
    `checkout_row` -- the same check, never counted twice. Every other declared row becomes its own required
    check `checkout/<row id>` (source checkout_row). A failed enumeration is recorded, never hidden."""
    row["checkout"] = {"script": script_rel, "rows": None, "error": None}
    try:
        rids = checkout_rows(script_rel)
    except Exception as e:  # noqa: BLE001 - recorded, never hidden
        row["checkout"]["error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        return
    row["checkout"]["rows"] = len(rids)
    want = set(rids)
    mirrored = set()
    for c in row["checks"]:
        if c["source"] == "script_check":
            comp = c["id"].split("/", 1)[-1]
            if "#" not in comp and comp in want:
                c["checkout_row"] = comp
                mirrored.add(comp)
    seen = set()
    for rid in rids:
        if rid in mirrored or rid in seen:
            continue
        seen.add(rid)
        row["checks"].append({"id": "checkout/" + rid, "source": "checkout_row", "owner": False,
                              "required": True, "checkout_row": rid})


def build():
    dirs = _mod_dirs()
    walks = {os.path.splitext(os.path.basename(w))[0]: w
             for w in walklint.find_walks(ROOT)}
    mods = {}
    for mod in sorted(set(dirs) | set(walks)):
        row = {"script": None, "script_sha": None, "walk": None,
               "ns_state": None, "load_error": None, "checks": []}
        claimed = {}
        if mod in dirs:
            if len(dirs[mod]) > 1:
                row["load_error"] = "ambiguous: %s" % [_rel(d) for d in dirs[mod]]
            else:
                d = dirs[mod][0]
                row["script"] = _rel(os.path.join(d, "validation.py"))
                row["script_sha"] = _sha(os.path.join(d, "validation.py"))
                try:
                    seen = {}
                    for chain, comp, toggle, shows in script_checks(d):
                        cid = "%s/%s" % (chain, comp)
                        seen[cid] = seen.get(cid, 0) + 1
                        if seen[cid] > 1:
                            cid = "%s#%d" % (cid, seen[cid])
                        row["checks"].append({
                            "id": cid, "source": "script_check", "owner": False,
                            "required": True, "toggle": toggle, "shows": shows})
                        for s in shows:
                            claimed.setdefault(s, []).append(cid)
                except Exception as e:  # recorded, never hidden
                    row["load_error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        if mod in walks:
            ns = northstar.parse(walks[mod])
            row["walk"] = _rel(walks[mod])
            row["ns_state"] = ns["state"]
            owner = ns["state"] == northstar.VALIDATED
            for pol, ids in (("must", ns["must_show"]), ("cannot", ns["cannot_show"])):
                for i in ids:
                    if pol == "must":
                        src = "north_star_bar" if owner else "must_show_line"
                    else:
                        src = "cannot_show_bar" if owner else "cannot_show_line"
                    row["checks"].append({
                        "id": "ns:" + i, "source": src, "owner": owner,
                        "required": pol == "must", "polarity": pol,
                        "claimed_by": claimed.get(i, [])})
            co = walk_checkout(walks[mod])
            if co:
                _add_checkout(row, co)
        mods[mod] = row
    body = json.dumps(mods, sort_keys=True)
    return {"version": 1,
            "rules": "design/RimMandrake/bridge_validation_observatory.md section 2.4",
            "generator": "src/RimMandrake/Utils/modcheck/required_checks.py",
            "manifest_hash": hashlib.sha256(body.encode()).hexdigest()[:16],
            "mods": mods}


def load(path=MANIFEST):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def summary_line(man):
    mods = man["mods"]
    n = lambda src: sum(1 for m in mods.values() for c in m["checks"] if c["source"] == src)
    return ("%d mods (%d scripts, %d walks, %d load errors); required: %d north_star_bar + "
            "%d must_show_line + %d script_check + %d checkout_row" % (
                len(mods), sum(1 for m in mods.values() if m["script"]),
                sum(1 for m in mods.values() if m["walk"]),
                sum(1 for m in mods.values() if m["load_error"]),
                n("north_star_bar"), n("must_show_line"), n("script_check"), n("checkout_row")))


def _write(man):
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("{\n")
        f.write('"version": %d,\n"rules": %s,\n"generator": %s,\n"manifest_hash": %s,\n"mods": {\n'
                % (man["version"], json.dumps(man["rules"]), json.dumps(man["generator"]),
                   json.dumps(man["manifest_hash"])))
        items = sorted(man["mods"].items())
        for k, (mod, row) in enumerate(items):
            f.write("%s: %s%s\n" % (json.dumps(mod), json.dumps(row, sort_keys=True),
                                    "," if k < len(items) - 1 else ""))
        f.write("}\n}\n")


def main(argv):
    man = build()
    if "--mod" in argv:
        mod = argv[argv.index("--mod") + 1]
        print(json.dumps(man["mods"].get(mod), indent=1))
        return 0
    if "--check" in argv:
        try:
            old = load()
        except (OSError, ValueError):
            print("required_checks.json missing or unreadable")
            return 1
        if old.get("manifest_hash") != man["manifest_hash"]:
            print("STALE: committed %s, current %s -- rerun required_checks.py"
                  % (old.get("manifest_hash"), man["manifest_hash"]))
            return 1
        print("current %s" % man["manifest_hash"])
        return 0
    _write(man)
    print("wrote %s  hash %s" % (_rel(MANIFEST), man["manifest_hash"]))
    print(summary_line(man))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
