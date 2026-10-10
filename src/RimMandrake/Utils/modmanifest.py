#!/usr/bin/env python3
"""modmanifest.py - one ordered mod manifest, and three lists compared against it.

MOD_MANIFEST_BUILD_THREE_LISTS_ONE_TRUTH (2026-10-10). Three different lists answer "what mods are we testing":

    INTENDED   infrastructure/state/modlists/manifest.<NAME>.json   ordered packageIds + the ModsConfig sha256 it
                                                                    was captured from (+ installed roots, --roots)
    NEXT LOAD  the live ModsConfig.xml - RimWorld reads it ONLY at startup, so it describes the NEXT load
    LOADED     what the running game actually loaded (a file of ids from jawa/mod_inventory / running_mods)

and nothing compared them: RimWorld's own recovery can reset ModsConfig to Core-only, `modlist_swap --restore`
silently dropped two mods (#47), and FULL.LATEST lacks some of our own newer mods. compare() names every kind of
difference: CORE_ONLY, MISSING, EXTRA, REORDERED, DUPLICATE_ID, NOT_LOADED, UNEXPECTED_LOADED. packageIds compare
lowercased, as RimWorld does.

    python3 src/RimMandrake/Utils/modmanifest.py check                     # manifest.FULL vs live ModsConfig
    python3 src/RimMandrake/Utils/modmanifest.py check --manifest MINIMAL --loaded ids.json [--roots]
    python3 src/RimMandrake/Utils/modmanifest.py diff A.xml B.xml          # any two ModsConfigs / manifests
    python3 src/RimMandrake/Utils/modmanifest.py capture FULL --from infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
    python3 src/RimMandrake/Utils/modmanifest.py gap --write Transient/x.md   # our shipping mods absent from it

check exits 0 only when every compared list matches. A test list that is DELIBERATELY not the full list (a
minimal tier) is checked with --manifest <its name>, never by reading its differences from FULL as defects.
"""
import argparse
import bisect
import hashlib
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MODLISTS = os.path.join(ROOT, "infrastructure", "state", "modlists")
SRC_ROOT = os.path.join(ROOT, "src")
SRC_TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
sys.path.insert(0, HERE)


class ManifestError(RuntimeError):
    pass


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_modsconfig(path):
    """Ordered activeMods ids exactly as written (case kept). Raises ManifestError if unreadable or empty -
    an unreadable list must never read as 'nothing differs'."""
    try:
        am = ET.parse(path).getroot().find("activeMods")
    except (OSError, ET.ParseError) as e:
        raise ManifestError("cannot read %s: %s" % (path, e))
    if am is None:
        raise ManifestError("%s has no <activeMods>" % path)
    ids = [(li.text or "").strip() for li in am.findall("li") if (li.text or "").strip()]
    if not ids:
        raise ManifestError("%s lists zero active mods" % path)
    return ids


def read_ids(path):
    """A ModsConfig .xml, a manifest .json, or a loaded-ids file (JSON list of ids / of {packageId}, or one per line)."""
    if path.endswith(".xml"):
        return read_modsconfig(path)
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as e:
        raise ManifestError("cannot read %s: %s" % (path, e))
    try:
        data = json.loads(raw)
    except ValueError:
        return [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
    if isinstance(data, dict):
        for k in ("ids", "mods", "activeMods", "result", "payload"):
            if k in data:
                data = data[k]
                break
        if isinstance(data, dict):
            for k in ("mods", "ids", "runningMods"):
                if k in data:
                    data = data[k]
                    break
    if not isinstance(data, list):
        raise ManifestError("%s: no id list found" % path)
    out = []
    for x in data:
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            v = x.get("packageId") or x.get("PackageId") or x.get("id")
            if v:
                out.append(v)
    if not out:
        raise ManifestError("%s: id list is empty" % path)
    return out


def manifest_from_ids(name, ids, source, modsconfig_path=None, roots=None):
    m = {"name": name, "captured": time.strftime("%Y-%m-%dT%H:%M:%S"), "source": source, "count": len(ids),
         "ids": list(ids)}
    if modsconfig_path:
        m["modsconfig_sha256"] = _sha(modsconfig_path)
    if roots is not None:
        m["roots"] = {i.lower(): roots.get(i.lower(), []) for i in ids}
    return m


def manifest_path(name_or_path):
    if os.path.exists(name_or_path):
        return name_or_path
    return os.path.join(MODLISTS, "manifest.%s.json" % name_or_path)


def load_manifest(name_or_path):
    p = manifest_path(name_or_path)
    try:
        with open(p, encoding="utf-8") as fh:
            m = json.load(fh)
    except (OSError, ValueError) as e:
        raise ManifestError("cannot read manifest %s: %s" % (p, e))
    if not m.get("ids"):
        raise ManifestError("manifest %s has no ids" % p)
    return m, p


def _dupes(ids):
    seen, d = set(), []
    for i in ids:
        k = i.lower()
        if k in seen and k not in d:
            d.append(k)
        seen.add(k)
    return d


def _moved(intended, actual):
    """ids (lowercase) that are out of relative order: the complement of a longest increasing subsequence of the
    intended positions taken in actual order. The minimal set whose moves explain the reorder."""
    pos = {}
    for n, i in enumerate(intended):
        pos.setdefault(i, n)
    seq = [(pos[i], i) for i in actual if i in pos]
    tails, tails_idx, prev = [], [], [None] * len(seq)
    for k, (p, _) in enumerate(seq):
        j = bisect.bisect_left(tails, p)
        if j == len(tails):
            tails.append(p)
            tails_idx.append(k)
        else:
            tails[j] = p
            tails_idx[j] = k
        prev[k] = tails_idx[j - 1] if j else None
    keep = set()
    k = tails_idx[-1] if tails_idx else None
    while k is not None:
        keep.add(k)
        k = prev[k]
    return [seq[k][1] for k in range(len(seq)) if k not in keep]


def is_core_only(ids):
    return bool(ids) and all(i.lower().startswith("ludeon.") for i in ids)


def compare(intended, next_load, loaded=None):
    """-> {clean, kinds, problems, missing, extra, reordered, duplicates, not_loaded, unexpected_loaded}."""
    I = [i.lower() for i in intended]
    N = [i.lower() for i in next_load]
    r = {"intended": len(I), "next_load": len(N), "kinds": [], "problems": []}
    sI, sN = set(I), set(N)
    r["missing"] = [i for i in I if i not in sN]
    r["extra"] = [i for i in N if i not in sI]
    r["duplicates"] = _dupes(N)
    firstN = list(dict.fromkeys(N))                     # a duplicate is DUPLICATE_ID, not also a reorder
    r["reordered"] = _moved(list(dict.fromkeys(i for i in I if i in sN)), [i for i in firstN if i in sI])
    if is_core_only(N) and not is_core_only(I):
        r["kinds"].append("CORE_ONLY")
        r["problems"].append("next load is Core/DLC only (%d ids) - RimWorld reset the list; read the FIRST "
                             "exception of the run that reset it" % len(N))
    if r["missing"]:
        r["kinds"].append("MISSING")
        r["problems"].append("%d intended ids absent from the next load: %s" % (len(r["missing"]),
                                                                                  ", ".join(r["missing"][:20])))
    if r["extra"]:
        r["kinds"].append("EXTRA")
        r["problems"].append("%d ids in the next load not intended: %s" % (len(r["extra"]),
                                                                            ", ".join(r["extra"][:20])))
    if r["duplicates"]:
        r["kinds"].append("DUPLICATE_ID")
        r["problems"].append("listed twice: %s" % ", ".join(r["duplicates"]))
    if r["reordered"]:
        r["kinds"].append("REORDERED")
        r["problems"].append("%d ids out of intended relative order (minimal moved set): %s" % (
            len(r["reordered"]), ", ".join(r["reordered"][:20])))
    r["not_loaded"] = r["unexpected_loaded"] = []
    if loaded is not None:
        L = [i.lower() for i in loaded]
        sL = set(L)
        r["not_loaded"] = [i for i in I if i not in sL]
        r["unexpected_loaded"] = [i for i in L if i not in sI]
        if r["not_loaded"]:
            r["kinds"].append("NOT_LOADED")
            r["problems"].append("%d intended ids NOT loaded by the running game: %s" % (
                len(r["not_loaded"]), ", ".join(r["not_loaded"][:20])))
        if r["unexpected_loaded"]:
            r["kinds"].append("UNEXPECTED_LOADED")
            r["problems"].append("%d loaded ids not intended: %s" % (len(r["unexpected_loaded"]),
                                                                      ", ".join(r["unexpected_loaded"][:20])))
    r["clean"] = not r["problems"]
    return r


# ------------------------------------------------------------------------------------------- disk scans

def _about_id(d):
    try:
        n = ET.parse(os.path.join(d, "About", "About.xml")).getroot().find("packageId")
        return (n.text or "").strip().lower() if n is not None and n.text else None
    except (OSError, ET.ParseError):
        return None


def installed_roots():
    """{packageId: [root dirs]} across the game's Mods folder and the Steam workshop."""
    from game_paths import LOCAL_MODS, WORKSHOP
    out = {}
    for base in (LOCAL_MODS, WORKSHOP):
        try:
            names = sorted(os.listdir(base))
        except OSError as e:
            raise ManifestError("cannot list %s: %s" % (base, e))
        for n in names:
            pid = _about_id(os.path.join(base, n))
            if pid:
                out.setdefault(pid, []).append(os.path.join(base, n))
    return out


def duplicate_roots(roots, ids):
    return {i.lower(): roots[i.lower()] for i in ids if len(roots.get(i.lower(), [])) > 1}


def shipping_ids():
    """({packageId: src dir} for every mod under src/<tier>/ we build, {ids folded into a composed mod})."""
    out, folded_ids = {}, set()
    try:
        import biomes_compose
        folded = set(biomes_compose.folded_sources(SRC_ROOT))
    except Exception as e:                      # say so; never silently treat members as standalone
        raise ManifestError("cannot read the compose manifest: %s" % e)
    for tier in SRC_TIERS:
        d = os.path.join(SRC_ROOT, tier)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            p = os.path.join(d, n)
            pid = _about_id(p)
            if not pid:
                continue
            if tier == "RimMandrake" and n in folded:
                folded_ids.add(pid)
            else:
                out[pid] = os.path.relpath(p, ROOT)
    return out, folded_ids


def shipping_gap(manifest_ids, ours, folded_ids=()):
    s = {i.lower() for i in manifest_ids}
    return {"absent": sorted(i for i in ours if i not in s and i not in folded_ids),
            "folded_but_listed": sorted(i for i in folded_ids if i in s)}


# ------------------------------------------------------------------------------------------------- CLI

def _print(r, label):
    print("%s: %s (intended %d, next load %d%s)" % (
        label, "CLEAN" if r["clean"] else "DIFFERS " + ",".join(r["kinds"]), r["intended"], r["next_load"],
        "" if not r.get("not_loaded") and not r.get("unexpected_loaded") else ", loaded compared"))
    for p in r["problems"]:
        print("  - " + p)


def cmd_check(a):
    from game_paths import MODS_CONFIG
    man, mpath = load_manifest(a.manifest)
    cfg = a.config or MODS_CONFIG
    nxt = read_modsconfig(cfg)
    loaded = read_ids(a.loaded) if a.loaded else None
    r = compare(man["ids"], nxt, loaded)
    print("manifest %s (%d ids, captured %s from %s)" % (os.path.relpath(mpath, ROOT), len(man["ids"]),
                                                          man.get("captured"), man.get("source")))
    print("next load %s sha256 %s" % (cfg, _sha(cfg)[:16]))
    src = man.get("source") and os.path.join(ROOT, man["source"])
    if src and os.path.exists(src) and man.get("modsconfig_sha256") and _sha(src) != man["modsconfig_sha256"]:
        print("  ! the manifest's source file changed since capture: re-capture or diff it")
    _print(r, "check")
    if a.roots:
        dups = duplicate_roots(installed_roots(), man["ids"])
        for i, rs in dups.items():
            print("  - DUPLICATE_ROOT %s: %s" % (i, " | ".join(rs)))
        if dups:
            r["clean"] = False
    if a.json:
        print(json.dumps(r, indent=1))
    return 0 if r["clean"] else 1


def cmd_diff(a):
    A, B = read_ids(a.a), read_ids(a.b)
    r = compare(A, B)
    print("A %s (%d)  ->  B %s (%d)" % (a.a, len(A), a.b, len(B)))
    _print(r, "diff")
    return 0 if r["clean"] else 1


def cmd_capture(a):
    ids = read_ids(a.src)
    roots = installed_roots() if a.roots else None
    m = manifest_from_ids(a.name, ids, os.path.relpath(os.path.abspath(a.src), ROOT),
                          modsconfig_path=a.src if a.src.endswith(".xml") else None, roots=roots)
    out = manifest_path(a.name) if not os.path.exists(a.name) else a.name
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=1)
        fh.write("\n")
    print("captured %s: %d ids -> %s" % (a.name, len(ids), os.path.relpath(out, ROOT)))
    return 0


def cmd_gap(a):
    man, mpath = load_manifest(a.manifest)
    ours, folded_ids = shipping_ids()
    g = shipping_gap(man["ids"], ours, folded_ids)
    lines = ["# Proposal: our mods absent from manifest %s" % man["name"], "",
             "Generated by `python3 src/RimMandrake/Utils/modmanifest.py gap` on %s. **A proposal for the owner, "
             "not an edit** - FULL.LATEST is unchanged. Each row is a mod we build under `src/` whose packageId is "
             "absent from the manifest (%d ids, from `%s`). Members folded into the composed `mandrake.rm.biomes` "
             "are excluded (they load inside it). Approve per row: add to FULL, or mark not-shipping." % (
                 time.strftime("%Y-%m-%d %H:%M"), len(man["ids"]), man.get("source")), "",
             "| packageId | source | add to FULL? |", "|---|---|---|"]
    lines += ["| `%s` | `%s` | |" % (i, ours[i]) for i in g["absent"]]
    if g["folded_but_listed"]:
        lines += ["", "Folded members still listed standalone (would load twice or not at all): " +
                  ", ".join("`%s`" % i for i in g["folded_but_listed"])]
    text = "\n".join(lines) + "\n"
    if a.write:
        with open(a.write, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("gap: %d absent, %d folded-but-listed -> %s" % (len(g["absent"]), len(g["folded_but_listed"]),
                                                             a.write))
    else:
        print(text)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--manifest", default="FULL")
    c.add_argument("--config", help="ModsConfig to treat as the next load (default: the live one)")
    c.add_argument("--loaded", help="file of ids the running game loaded")
    c.add_argument("--roots", action="store_true", help="also scan installed roots for duplicate packageIds")
    c.add_argument("--json", action="store_true")
    d = sub.add_parser("diff")
    d.add_argument("a")
    d.add_argument("b")
    k = sub.add_parser("capture")
    k.add_argument("name")
    k.add_argument("--from", dest="src", required=True)
    k.add_argument("--roots", action="store_true")
    g = sub.add_parser("gap")
    g.add_argument("--manifest", default="FULL")
    g.add_argument("--write")
    a = ap.parse_args(argv)
    try:
        return {"check": cmd_check, "diff": cmd_diff, "capture": cmd_capture, "gap": cmd_gap}[a.cmd](a)
    except ManifestError as e:
        print("modmanifest: UNMEASURED - %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
