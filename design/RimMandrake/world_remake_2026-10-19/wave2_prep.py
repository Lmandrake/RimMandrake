#!/usr/bin/env python3
"""Retirement Wave 2 preparation (offline). Reproduces 08_wave2_prep.md's numbers.

Usage: wave2_prep.py <ids.txt> <workdir>
  ids.txt   one packageId per line (the drops)
  workdir   scratch output dir (Transient/...)

Steps, all read-only against the game install:
  1. dropped defNames: defs in the live DefDump capture whose every defining package is a drop,
     plus <defName>s in the drops' own XML (catches Cherry-Picker-cut defs absent from the dump),
     minus every name that a RETAINED mod or Core/DLC also declares (grep of their XML).
  2. Cherry Picker: SHIP keys whose def is a dropped defName -> trimmed key list + candidate profile.
  3. our src: every reference to a dropped defName in an ACTIVE src mod, with its guard
     (FindMod naming a drop / Conditional / MayRequire); unguarded refs are printed.
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


def main():
    idsf, W = sys.argv[1], sys.argv[2]
    os.makedirs(W, exist_ok=True)
    wave = {l.strip().lower() for l in open(idsf) if l.strip()}
    act = [li.text.strip().lower() for li in ET.parse(LIST).getroot().find("activeMods")]
    man = json.load(open(os.path.join(CAP, "manifest.json")))
    capmods = {m["packageId"].lower() for m in man["mods"]}
    print("capture", CAP, "mods", len(capmods), "list", len(act), "capture==list", capmods == set(act))
    roots = {m["packageId"].lower(): wsl(m["rootDir"]) for m in man["mods"]}
    # 1a. dump attribution
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
    # 1b. drops' own XML
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
    # 1c. collisions with retained mods + Core/DLC
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
    print("dropped defNames", len(D), "(dump", len(drop_dump), "xml-only", len(xml_only), "collide", len(col & cand), ")")
    # 2. Cherry Picker
    keys = [li.text.strip() for li in ET.parse(SHIP).getroot().find("ModSettings/keys")]
    gone = [k for k in keys if k.partition("/")[2] in D]
    open(os.path.join(W, "cp_wave2_keys.txt"), "w").write("\n".join(gone) + "\n")
    print("CP SHIP keys", len(keys), "dropped", len(gone), "kept", len(keys) - len(gone))
    # 3. our src refs
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
    refs, bad = 0, []
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
                        ok = False
                        for a in stack:
                            c = a.get("Class") or ""
                            if "FindMod" in c and any((li.text or "").strip().lower() in wavenames
                                                      for li in a.findall("mods/li")):
                                ok = True
                            if "Conditional" in c and any(n in (a.findtext("xpath") or "") for n in hit):
                                ok = True
                            for at in ("MayRequire", "MayRequireAnyOf"):
                                if a.get(at) and set(re.split(r"[,\s]+", a.get(at).lower())) & wave:
                                    ok = True
                        if not ok:
                            bad.append((os.path.relpath(path, REPO), e.tag, sorted(hit)))
                    for c in e:
                        walk(c, stack)
                walk(root, [])
    json.dump(bad, open(os.path.join(W, "src_unguarded.json"), "w"), indent=1)
    print("src refs to dropped defs", refs, "unguarded", len(bad))
    for b in bad:
        print("  UNGUARDED", *b)


if __name__ == "__main__":
    main()
