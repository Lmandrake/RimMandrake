#!/usr/bin/env python3
"""Retirement Wave 3 preparation (offline). Reproduces 14_wave3_prep.md's numbers.

Usage: wave3_prep.py <ids.txt> <workdir>

Same instrument as wave2_prep.py, with the guard test that Wave 2 got wrong fixed
(Transient/live_testing_2026-10-20a/RESULTS.md, commit c674b7832):
  * a PatchOperationConditional guards a reference ONLY when the reference sits in its <match>
    branch and its xpath names the def, or its xpath is a pure def-exists test
    (...[defName="X"] with nothing after the predicate). A Conditional on a CHILD of the def
    whose <nomatch> Adds to the def is NOT a guard: the Add fails once the def is gone.
  * a PatchOperationFindMod naming a dropped mod guards only its <match> branch.
  * MayRequire / MayRequireAnyOf naming a dropped mod guards its subtree.
Also scans our C# for string literals naming a dropped def, and reports src files that name the
dropped mods' packageIds / C# namespaces.
"""
import json, os, re, subprocess, sys, xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LIST = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml")
SHIP = os.path.join(REPO, "infrastructure/state/cherrypicker/CherryPicker.SHIP.xml")
sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
import game_paths  # noqa: E402
CAP = game_paths.DEF_DUMP
DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"


def wsl(p):
    return "/mnt/" + p[0].lower() + "/" + p[3:].replace("\\", "/")


def def_exists_test(xp, names):
    for n in names:
        if re.search(r"defName\s*=\s*[\"']%s[\"']\s*\]\s*$" % re.escape(n), xp.strip()):
            return True
    return False


def main():
    idsf, W = sys.argv[1], sys.argv[2]
    os.makedirs(W, exist_ok=True)
    wave = {l.strip().lower() for l in open(idsf) if l.strip()}
    act = [li.text.strip().lower() for li in ET.parse(LIST).getroot().find("activeMods")]
    man = json.load(open(os.path.join(CAP, "manifest.json")))
    capmods = {m["packageId"].lower() for m in man["mods"]}
    print("capture", os.path.basename(CAP), "mods", len(capmods), "list", len(act), "capture==list", capmods == set(act))
    print("wave ids on list", sorted(wave & set(act)), "missing", sorted(wave - set(act)))
    roots = {m["packageId"].lower(): wsl(m["rootDir"]) for m in man["mods"]}
    json.dump(roots, open(os.path.join(W, "roots.json"), "w"))
    by = {}
    for f in os.listdir(os.path.join(CAP, "defs")):
        try:
            j = json.load(open(os.path.join(CAP, "defs", f)))
        except Exception:
            continue
        for d in j.get("defs", []):
            by.setdefault((j["defType"], d["defName"]), set()).add((d.get("packageId") or "").lower())
    names = {}
    for (t, n), v in by.items():
        names.setdefault(n, set()).update(v)
    drop_dump = {n for n, v in names.items() if v <= wave}
    pat = re.compile(r"<defName>\s*([^<\s]+)\s*</defName>")
    xmld = {}
    for w in wave:
        for dp, _, fn in os.walk(roots[w]):
            if any(s in dp for s in ("/Patches", "/Languages", "/About")):
                continue
            for f in fn:
                if f.lower().endswith(".xml"):
                    try:
                        s = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
                    except OSError:
                        continue
                    for d in pat.findall(s):
                        xmld.setdefault(d, set()).add(w)
    xml_only = {n for n in xmld if n not in names}
    cand = drop_dump | xml_only
    ret = sorted({v for k, v in roots.items() if k not in wave} | {DATA})
    pf = os.path.join(W, "cand_pat.txt")
    open(pf, "w").write("\n".join("<defName>%s</defName>" % n for n in sorted(cand)) + "\n")
    col = set()
    for i in range(0, len(ret), 40):
        r = subprocess.run(["grep", "-rhoF", "--include=*.xml", "-f", pf] + ret[i:i + 40],
                           capture_output=True, text=True)
        col |= {m for m in pat.findall(r.stdout)}
    D = cand - col
    json.dump(sorted(D), open(os.path.join(W, "dropped_defnames.json"), "w"))
    per = {}
    for n in D:
        for p in (names.get(n) or xmld.get(n) or {"?"}):
            per[p] = per.get(p, 0) + 1
    print("dropped defNames", len(D), "(dump", len(drop_dump), "xml-only", len(xml_only), "collide", len(col & cand), ")", per)
    keys = [li.text.strip() for li in ET.parse(SHIP).getroot().find("ModSettings/keys")]
    gone = [k for k in keys if k.partition("/")[2] in D]
    open(os.path.join(W, "cp_wave3_keys.txt"), "w").write("\n".join(gone) + ("\n" if gone else ""))
    print("CP SHIP keys", len(keys), "dropped", len(gone), "kept", len(keys) - len(gone))
    Dn = {n for n in D if not n.islower() and len(n) >= 4}
    wavenames = {}
    for p in wave:
        try:
            wavenames[ET.parse(roots[p] + "/About/About.xml").getroot().findtext("name").strip().lower()] = p
        except Exception:
            pass
    srcmods = {}
    for dp, _, fn in os.walk(os.path.join(REPO, "src")):
        if dp.endswith("/About") and "About.xml" in fn:
            try:
                pid = ET.parse(os.path.join(dp, "About.xml")).getroot().findtext("packageId").strip().lower()
            except Exception:
                continue
            if pid in act:
                srcmods[os.path.dirname(dp)] = pid
    tok = re.compile(r"[A-Za-z_][A-Za-z0-9_\-]*")
    refs, bad, guarded = 0, [], []
    for r, pid in sorted(srcmods.items()):
        for dp, dn, fn in os.walk(r):
            if any(x in dp.split("/") for x in ("obj", "bin", "Languages")):
                continue
            for f in fn:
                if not f.endswith(".xml") or f == "About.xml":
                    continue
                path = os.path.join(dp, f)
                try:
                    root = ET.parse(path).getroot()
                except ET.ParseError:
                    continue

                def walk(e, stack):
                    nonlocal refs
                    stack = stack + [e]
                    own = set(tok.findall(e.text or "")) if (e.text and e.text.strip() and len(e) == 0) else set()
                    hit = own & Dn
                    if hit:
                        refs += 1
                        why = None
                        for i, a in enumerate(stack):
                            branch = stack[i + 1].tag if i + 1 < len(stack) else None
                            c = a.get("Class") or ""
                            if "FindMod" in c and branch == "match" and any(
                                    (li.text or "").strip().lower() in wavenames for li in a.findall("mods/li")):
                                why = "FindMod"
                            if "Conditional" in c:
                                xp = a.findtext("xpath") or ""
                                if branch == "match" and any(n in xp for n in hit):
                                    why = "Conditional-match"
                                elif def_exists_test(xp, hit):
                                    why = "Conditional-defexists"
                            for at in ("MayRequire", "MayRequireAnyOf"):
                                if a.get(at) and set(re.split(r"[,\s]+", a.get(at).lower())) & wave:
                                    why = "MayRequire"
                        rec = (os.path.relpath(path, REPO), e.tag, sorted(hit))
                        (guarded if why else bad).append(rec + ((why,) if why else ()))
                    for c in e:
                        walk(c, stack)
                walk(root, [])
    json.dump(bad, open(os.path.join(W, "src_unguarded.json"), "w"), indent=1)
    json.dump(guarded, open(os.path.join(W, "src_guarded.json"), "w"), indent=1)
    print("src XML refs to dropped defs", refs, "guarded", len(guarded), "unguarded", len(bad))
    for b in bad:
        print("  UNGUARDED", *b)
    # C# string literals naming a dropped def
    cs = []
    lit = re.compile(r'"([A-Za-z_][A-Za-z0-9_]{3,})"')
    for r in srcmods:
        for dp, dn, fn in os.walk(r):
            if any(x in dp.split("/") for x in ("obj", "bin")):
                continue
            for f in fn:
                if f.endswith(".cs"):
                    p = os.path.join(dp, f)
                    for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                        for m in lit.findall(line):
                            if m in Dn:
                                cs.append((os.path.relpath(p, REPO), i, m))
    print("C# literals naming dropped defs", len(cs))
    for c in cs:
        print("  CS", *c)


if __name__ == "__main__":
    main()
