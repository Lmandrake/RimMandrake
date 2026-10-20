#!/usr/bin/env python3
"""Permanent archive of every mod ever on the owner's list: design/RimMandrake/mod_archive/ALL_ORIGINAL_MODS.tsv.
  mod_archive.py build            regenerate the TSV + about/*.xml from lists, git history and docs (idempotent)
  mod_archive.py check            every id in every FULL.* list, every LATEST commit and every wave removed list is a row; exit 1 if not
  mod_archive.py add <packageId> --lifecycle RETIRED-WAVE3 --date YYYY-MM-DD --doc <path> --reason "..." [--reconsider "..."] [--name N]
                                  upsert one row by hand (use after a new retirement; `build` keeps manual fields in overrides.tsv)
Not hooked into anything; run by hand after a retirement. Offline."""
import csv, glob, json, os, re, shutil, subprocess, sys, argparse, xml.etree.ElementTree as ET
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
A = R + "/design/RimMandrake/mod_archive/"
TSV, OVR = A + "ALL_ORIGINAL_MODS.tsv", A + "overrides.tsv"
ML = R + "/infrastructure/state/modlists/"
WR = R + "/design/RimMandrake/world_remake_2026-10-19/"
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps/"
COLS = "packageId name name_source workshop_id folder_name author supported_versions lifecycle lifecycle_date ruling_doc current_profile reason reconsider_when first_seen_list last_seen_list".split()

def ids_of(text):
    try: return [e.text.strip() for e in ET.fromstring(text).find("activeMods") if e.text]
    except Exception: return []

def lists():
    """ordered [(label, [ids])]: working-tree FULL-like lists, then LATEST history oldest..newest."""
    out = []
    for f in sorted(glob.glob(ML + "ModsConfig*.xml")):
        b = os.path.basename(f)
        if "WAVE2_2026" in b and not b.startswith("ModsConfig.FULL") or "RULED" in b or "MINIMAL" in b or "VANILLA" in b: continue
        i = ids_of(open(f, encoding="utf-8").read())
        if len(i) > 100: out.append((b, i))
    h = subprocess.run(["git", "-C", R, "log", "--reverse", "--format=%h %ad", "--date=short", "--", "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml"], capture_output=True, text=True).stdout.split("\n")
    hist = []
    for l in h:
        if not l.strip(): continue
        sha, d = l.split()
        t = subprocess.run(["git", "-C", R, "show", "%s:infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml" % sha], capture_output=True, text=True).stdout
        hist.append(("LATEST@%s %s" % (sha, d), ids_of(t)))
    return hist + out

def removed_lists():
    """wave removed sets: {label: {lowerid: why}}"""
    d = {}
    byname = {n: i for n, i in lists()}
    pre, w1 = byname.get("ModsConfig.FULL.PRE_WAVE1.xml", []), set(x.lower() for x in byname.get("ModsConfig.FULL.WAVE1_498_2026-10-19.xml", []))
    d["WAVE1"] = {x.lower(): "in PRE_WAVE1 (542), absent from WAVE1_498" for x in pre if x.lower() not in w1}
    w2 = {}
    p = ML + "wave2_removed_118.txt"
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            if l.startswith("#") or "\t" not in l: continue
            c = l.rstrip("\n").split("\t"); w2[c[0].lower()] = (c[2] if len(c) > 2 else "")
    d["WAVE2"] = w2
    return d

def about_index():
    idx = {}
    for root in (STEAM + "workshop/content/294100/*/", STEAM + "common/RimWorld/Mods/*/"):
        for dd in glob.glob(root):
            for a in glob.glob(dd + "[Aa]bout/[Aa]bout.xml"):
                try:
                    pid = (ET.parse(a).getroot().findtext("packageId") or "").strip().lower()
                except Exception: continue
                if pid: idx.setdefault(pid, (a, dd.rstrip("/")))
    for a in glob.glob(R + "/src/**/About/About.xml", recursive=True):
        try: pid = (ET.parse(a).getroot().findtext("packageId") or "").strip().lower()
        except Exception: continue
        if pid: idx.setdefault(pid, (a, os.path.dirname(os.path.dirname(a))))
    return idx

def read_tsv(p):
    if not os.path.exists(p): return {}
    return {r["packageId"].lower(): r for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t")}

def write_tsv(rows):
    with open(TSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(COLS)
        for k in sorted(rows): w.writerow([str(rows[k].get(c, "")).replace("\t", " ").replace("\n", " ") for c in COLS])

def addback():
    """reconsider-when from 07_deeper_drops tables (last column of rows naming a backticked packageId) and 09 recommendations."""
    d = {}
    for fn in ("07_deeper_drops.md",):
        for l in open(WR + fn, encoding="utf-8"):
            if l.startswith("|") and "`" in l:
                c = [x.strip() for x in l.strip().strip("|").split("|")]
                m = re.search(r"`([a-z0-9_.\-]+)`", c[0], re.I)
                if m and len(c) >= 3: d[m.group(1).lower()] = c[-1]
    return d

def build():
    L = lists(); rem = removed_lists(); facts = {}
    for l in open(R + "/design/RimMandrake/mod_audit/facts/mod_facts.jsonl", encoding="utf-8"):
        r = json.loads(l); facts[r["packageId"].lower()] = r
    ai = about_index(); ab = addback(); ovr = read_tsv(OVR)
    rb = {}
    for n in ("DEV", "TEST", "AUTHORING", "SHIP"):
        for x in ids_of(open(ML + "ModsConfig.%s.RULED_2026-10-20.xml" % n, encoding="utf-8").read()): rb.setdefault(x.lower(), []).append(n)
    for x in ids_of(open(ML + "ModsConfig.PAINT.RULED_2026-10-20.xml", encoding="utf-8").read()): rb.setdefault(x.lower(), []).append("PAINT")
    w380 = {x.lower() for x in ids_of(open(ML + "ModsConfig.FULL.WAVE2_380_2026-10-19.xml", encoding="utf-8").read())}
    tsv07 = {}
    for r in csv.DictReader(open(WR + "07_profile_assignment.tsv", encoding="utf-8"), delimiter="\t"): tsv07[r["packageId"].lower()] = r
    keepcut = json.load(open(R + "/Transient/retirement_keepcut_sheet_2026-10-20.decisions.json"))["decisions"] if os.path.exists(R + "/Transient/retirement_keepcut_sheet_2026-10-20.decisions.json") else {}
    drops = {k.lower() for k, v in keepcut.items() if v.get("decision") == "cut" and "DROP" in v.get("note", "").upper()}
    first, last, disp = {}, {}, {}
    for lab, ids in L:
        for x in ids:
            k = x.lower(); disp.setdefault(k, x); first.setdefault(k, lab); last[k] = lab
    rows = {}
    copied = 0
    for k in sorted(disp):
        f = facts.get(k, {}); a = ai.get(k)
        name, src = "", "UNKNOWN"
        if a:
            try:
                r_ = ET.parse(a[0]).getroot(); name = (r_.findtext("name") or "").strip(); src = "About.xml (src)" if a[0].startswith(R) else "About.xml (disk)"
                auth = (r_.findtext("author") or (r_.findtext("authors") or "")).strip()
                vers = ",".join(li.text.strip() for li in (r_.find("supportedVersions") if r_.find("supportedVersions") is not None else []) if li.text)
            except Exception: auth = vers = ""
        else: auth = vers = ""
        if not name and f: name, src = f.get("name", ""), "mod_facts.jsonl"
        if f:
            auth = auth or f.get("author") or ""; vers = vers or ",".join(f.get("supported_versions") or [])
        wid = (f.get("workshop_id") or "") if f else ""
        fold = os.path.basename(a[1]) if a else (os.path.basename((f.get("folder") or "").replace("\\", "/")) if f else "")
        if a and not wid and "workshop" in a[1]: wid = os.path.basename(a[1])
        if k in drops: lc, ld, doc = "DROPPED-BY-KEEPCUT", "2026-10-20", "world_remake_2026-10-19/11_ruled_keepcut.md"; why = keepcut.get(next(o for o in keepcut if o.lower() == k), {}).get("note", "")
        elif k in w380: lc, ld, doc, why = "ACTIVE-380", "", "", ""
        elif k in rem["WAVE2"]: lc, ld, doc, why = "RETIRED-WAVE2", "2026-10-19", "world_remake_2026-10-19/08_wave2_prep.md", rem["WAVE2"][k]
        elif k in rem["WAVE1"]: lc, ld, doc, why = "RETIRED-WAVE1", "2026-10-19", "mod_audit/RETIREMENT_WAVE_1.md", rem["WAVE1"][k]
        else: lc, ld, doc, why = "RETIRED-EARLIER", "", "see last_seen_list (removed after that list)", "removed from the list before PRE_WAVE1 (542) was captured; reason is in that period's ledger/journal"
        prof = ",".join(rb.get(k, [])) or "-"
        if lc.startswith("RETIRED") or lc.startswith("DROPPED"): prof = "-"
        t = tsv07.get(k)
        if t and lc.startswith("ACTIVE"): why = (t.get("reason") or "").split("|")[0].strip()
        row = dict(packageId=disp[k], name=name, name_source=src, workshop_id=wid, folder_name=fold, author=auth, supported_versions=vers,
                   lifecycle=lc, lifecycle_date=ld, ruling_doc=doc, current_profile=prof, reason=why, reconsider_when=ab.get(k, ""),
                   first_seen_list=first[k], last_seen_list=last[k])
        if k in ovr:
            for c in COLS:
                if ovr[k].get(c): row[c] = ovr[k][c]
        rows[k] = row
        if a and not lc.startswith("ACTIVE"):
            os.makedirs(A + "about", exist_ok=True); shutil.copyfile(a[0], A + "about/%s.xml" % disp[k]); copied += 1
    for k, r in ovr.items():
        if k not in rows: rows[k] = r
    write_tsv(rows)
    print("rows", len(rows), "about copied", copied, "lifecycle", {v: sum(1 for r in rows.values() if r["lifecycle"] == v) for v in sorted({r["lifecycle"] for r in rows.values()})})

def check():
    have = set(read_tsv(TSV)); missing = set()
    for lab, ids in lists():
        missing |= {x for x in ids if x.lower() not in have}
    for lab, d in removed_lists().items(): missing |= {x for x in d if x not in have}
    print("rows", len(have), "missing", len(missing)); [print(" ", m) for m in sorted(missing)]
    return 1 if missing else 0

def add(a):
    ovr = read_tsv(OVR); r = ovr.get(a.packageId.lower(), {c: "" for c in COLS}); r["packageId"] = a.packageId
    for c, v in (("lifecycle", a.lifecycle), ("lifecycle_date", a.date), ("ruling_doc", a.doc), ("reason", a.reason), ("reconsider_when", a.reconsider), ("name", a.name)):
        if v: r[c] = v
    r["current_profile"] = "-"; ovr[a.packageId.lower()] = r
    with open(OVR, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(COLS)
        for k in sorted(ovr): w.writerow([ovr[k].get(c, "") for c in COLS])
    build()

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("cmd", choices=["build", "check", "add"]); p.add_argument("packageId", nargs="?")
    for o in ("lifecycle", "date", "doc", "reason", "reconsider", "name"): p.add_argument("--" + o, default="")
    a = p.parse_args()
    if a.cmd == "build": build()
    elif a.cmd == "check": sys.exit(check())
    else: add(a)
