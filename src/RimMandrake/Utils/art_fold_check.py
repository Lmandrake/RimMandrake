#!/usr/bin/env python3
"""art_fold_check.py -- prove each folded *ArtOverride creature still resolves in its owner mod.

ART_OVERRIDE_FOLD_ALL_1 (precedent SILOOTH_ART_FOLD_1, 616bbcdf3). The standalone *ArtOverride
mods painted over a donor's art by shipping loose PNGs at the donor's own texPath. Folding moves
that art into the mod that owns the creature and deletes the standalone mod. The fold is data:
`art_fold_manifest.json` beside this script, one row per creature. Per row this checks, offline:

  GONE       the standalone override folder no longer exists.
  RESOLVES   every group's `new` texPath has its facings (default north/south/east) as real
             RGBA PNGs with visible pixels under <owner>/Textures/ (the mask `<base>_<f>m` is
             never counted as a facing).
  PATCHED    when new != old: some Operation in <owner>/<patch> carries `<texPath>new</texPath>`,
             and the donor's own Defs XML still holds `old` as a texPath literal, so a
             value-matched patch has something to match. Donor not on disk -> UNMEASURED.
  NO-DANGLE  no XML under src/ still names `old` as a texPath unless `old` itself resolves to a
             texture in one of our mods (a same-path row keeps it on purpose).
  UNLISTED   the override's packageId appears in no About.xml, no compose list, and no modlist
             snapshot (infrastructure/state/modlists/, deployed/config/).
  KEPT       mode "dead" rows: the `kept` path (where the bytes survive) exists.

Sanity probe: the manifest's Silooth row (the precedent, folded by hand) must pass, and
--selftest builds a throwaway repo where every check goes red once.

    python3 src/RimMandrake/Utils/art_fold_check.py            one line per creature + summary
    python3 src/RimMandrake/Utils/art_fold_check.py --selftest
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MANIFEST = os.path.join(HERE, "art_fold_manifest.json")
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
DONOR_ROOTS = (STEAM + "/common/RimWorld/Mods", STEAM + "/workshop/content/294100")
FACINGS = ("north", "south", "east")
_donor_cache = {}


def _alpha_ok(path):
    from PIL import Image
    im = Image.open(path)
    if im.mode != "RGBA":
        return "mode %s, no alpha" % im.mode
    if im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox() is None:
        return "no visible pixels"
    return None


def donor_dir(pid, hint=None, roots=DONOR_ROOTS):
    """Folder of the installed mod whose own <packageId> is pid (deps lists ignored)."""
    pid = pid.lower()
    if pid in _donor_cache:
        return _donor_cache[pid]
    cands = [hint] if hint else []
    cands += [os.path.dirname(os.path.dirname(a)) for r in roots
              for a in glob.glob(os.path.join(glob.escape(r), "*", "About", "About.xml"))]
    for d in cands:
        try:
            own = (ET.parse(os.path.join(d, "About", "About.xml")).getroot().findtext("packageId") or "").strip()
        except Exception:
            continue
        if own.lower() == pid:
            _donor_cache[pid] = d
            return d
    _donor_cache[pid] = None
    return None


def donor_has_literal(d, lit):
    pat = re.compile(r">\s*" + re.escape(lit) + r"\s*<")
    for f in glob.glob(os.path.join(glob.escape(d), "**", "*.xml"), recursive=True):
        if "/About/" in f:
            continue
        try:
            if pat.search(open(f, encoding="utf-8", errors="replace").read()):
                return True
        except OSError:
            pass
    return False


def _src_texpath_index(repo):
    idx = {}
    for f in glob.glob(os.path.join(repo, "src", "**", "*.xml"), recursive=True):
        try:
            t = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in re.finditer(r"<texPath>\s*([^<]+?)\s*</texPath>", t):
            idx.setdefault(m.group(1), set()).add(os.path.relpath(f, repo))
    return idx


def _resolves_anywhere(repo, lit):
    for f in FACINGS[:1] + ("south",):
        if glob.glob(os.path.join(glob.escape(repo), "src", "*", "*", "Textures", lit + "_" + f + ".png")):
            return True
    return bool(glob.glob(os.path.join(glob.escape(repo), "src", "*", "*", "Textures", lit + ".png")))


def _listing_files(repo):
    out = glob.glob(os.path.join(repo, "src", "*", "*", "About", "About.xml"))
    out += glob.glob(os.path.join(repo, "infrastructure", "state", "modlists", "*"))
    out += glob.glob(os.path.join(repo, "deployed", "config", "*"))
    out += glob.glob(os.path.join(repo, "src", "**", "*compose*"), recursive=True)
    out = [f for f in out if os.path.isfile(f)]
    try:   # tracked files only: an untracked bridge backup is another window's live state, not a snapshot
        import subprocess
        tr = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True, check=True).stdout
        tracked = {os.path.join(repo, x) for x in tr.decode().split("\0") if x}
        out = [f for f in out if f in tracked]
    except (subprocess.CalledProcessError, OSError):
        pass
    return out


def check(rows, repo=REPO, donor_roots=DONOR_ROOTS, check_donor=True):
    texidx = _src_texpath_index(repo)
    listings = [(f, open(f, encoding="utf-8", errors="replace").read().lower()) for f in _listing_files(repo)]
    results = []
    for r in rows:
        bad, unmeasured = [], []
        owner = os.path.join(repo, r["owner"])
        if r.get("override") and os.path.exists(os.path.join(repo, r["override"])):
            bad.append("GONE: %s still exists" % r["override"])
        if r.get("kept") and not os.path.exists(os.path.join(repo, r["kept"])):
            bad.append("KEPT: %s missing" % r["kept"])
        ptxt = None
        if r.get("patch"):
            pp = os.path.join(owner, r["patch"])
            if os.path.exists(pp):
                ptxt = open(pp, encoding="utf-8").read()
                try:
                    ET.fromstring(ptxt.encode("utf-8"))
                except ET.ParseError as e:
                    bad.append("PATCHED: %s does not parse (%s)" % (r["patch"], e))
            else:
                bad.append("PATCHED: %s missing" % r["patch"])
        for g in r.get("groups", []):
            old, new = g["old"], g["new"]
            for f in g.get("facings", FACINGS):
                p = os.path.join(owner, "Textures", new + "_" + f + ".png")
                if not os.path.exists(p):
                    bad.append("RESOLVES: %s_%s.png not in %s" % (new, f, r["owner"]))
                else:
                    why = _alpha_ok(p)
                    if why:
                        bad.append("RESOLVES: %s_%s.png %s" % (new, f, why))
            if new != old:
                # donor_literal false: only our own defs ever drew `old` (edited in place), no donor slot to patch
                if g.get("donor_literal", True) and (ptxt is None or "<texPath>%s</texPath>" % new not in ptxt):
                    bad.append("PATCHED: no operation sets texPath %s" % new)
                if check_donor and r.get("donor") and g.get("donor_literal", True):
                    d = donor_dir(r["donor"], r.get("donor_hint"), donor_roots)
                    if d is None:
                        unmeasured.append("donor %s not on disk" % r["donor"])
                    elif not donor_has_literal(d, old):
                        bad.append("PATCHED: donor %s has no texPath %s to match" % (r["donor"], old))
                users = texidx.get(old, set())
                if users and not _resolves_anywhere(repo, old):
                    bad.append("NO-DANGLE: %s still name %s, which no mod of ours ships" % (sorted(users)[:3], old))
        pid = (r.get("packageId") or "").lower()
        if pid:
            hits = [os.path.relpath(f, repo) for f, t in listings if pid in t]
            if hits:
                bad.append("UNLISTED: %s named in %s" % (pid, hits[:3]))
        results.append((r["creature"], bad, unmeasured))
    return results


def selftest():
    from PIL import Image
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        def png(rel, visible=True):
            p = os.path.join(td, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            Image.new("RGBA", (8, 8), (9, 9, 9, 255 if visible else 0)).save(p)

        def w(rel, text):
            p = os.path.join(td, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(text)
        donor = os.path.join(td, "donors", "D1")
        w("donors/D1/About/About.xml", "<ModMetaData><packageId>x.donor</packageId></ModMetaData>")
        w("donors/D1/Defs/a.xml", "<Defs><PawnKindDef><texPath>d/Fake/Fake</texPath></PawnKindDef></Defs>")
        op = '<Patch><Operation Class="PatchOperationConditional"><xpath>/Defs/PawnKindDef//texPath[text()="d/Fake/Fake"]</xpath><match Class="PatchOperationReplace"><xpath>/Defs/PawnKindDef//texPath[text()="d/Fake/Fake"]</xpath><value><texPath>O/Own/Fake/Fake</texPath></value></match></Operation></Patch>'
        for f in FACINGS:
            png("src/T/Own/Textures/O/Own/Fake/Fake_%s.png" % f)
        w("src/T/Own/About/About.xml", "<ModMetaData><packageId>x.own</packageId></ModMetaData>")
        w("src/T/Own/Patches/Fold.xml", op)
        base = {"creature": "good", "override": "src/T/FakeArtOverride", "packageId": "x.fakeartoverride",
                "owner": "src/T/Own", "donor": "x.donor", "patch": "Patches/Fold.xml",
                "groups": [{"old": "d/Fake/Fake", "new": "O/Own/Fake/Fake"}]}
        cases = [(dict(base), None)]
        cases.append((dict(base, creature="still-there"), "GONE"))
        cases.append((dict(base, creature="no-facing", groups=[{"old": "d/Fake/Fake", "new": "O/Own/Nope/Fake"}]), "RESOLVES"))
        cases.append((dict(base, creature="no-patch", patch="Patches/Missing.xml"), "PATCHED"))
        cases.append((dict(base, creature="donor-lacks", groups=[{"old": "d/Gone/Gone", "new": "O/Own/Fake/Fake"}]), "donor x.donor has no texPath"))
        cases.append((dict(base, creature="dangling"), "NO-DANGLE"))
        cases.append((dict(base, creature="listed"), "UNLISTED"))
        cases.append((dict(base, creature="dead-lost", mode="dead", groups=[], kept="src/T/Own/Nothing"), "KEPT"))
        for row, want in cases:
            if row["creature"] == "still-there":
                w("src/T/FakeArtOverride/About/About.xml", "<x/>")
            if row["creature"] == "dangling":
                w("src/T/Other/Defs/x.xml", "<Defs><texPath>d/Fake/Fake</texPath></Defs>")
            if row["creature"] == "listed":
                w("infrastructure/state/modlists/ModsConfig.x.xml", "<li>x.fakeartoverride</li>")
            _donor_cache.clear()
            (name, bad, unm), = check([row], td, (os.path.join(td, "donors"),))
            ok = (not bad and not unm) if want is None else any(want in b for b in bad)
            print("%-4s %-12s %s" % ("PASS" if ok else "FAIL", name, bad or "clean"))
            fails += not ok
            for junk in ("src/T/FakeArtOverride", "src/T/Other", "infrastructure"):
                import shutil
                shutil.rmtree(os.path.join(td, junk), ignore_errors=True)
    print("%d/%d selftest cases passed" % (len(cases) - fails, len(cases)))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-donor", action="store_true", help="skip donor XML reads (Mac / no Steam)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rows = json.load(open(MANIFEST))["rows"]
    res = check(rows, check_donor=not a.no_donor)
    red = unm = 0
    probe = None
    for name, bad, um in res:
        tag = "RED" if bad else ("UNMEASURED" if um else "ok")
        red += bool(bad)
        unm += bool(um and not bad)
        if name == "Silooth":
            probe = not bad
        print("%-10s %-28s %s" % (tag, name, "; ".join(bad + um)))
    print("%d creatures, %d red, %d unmeasured; sanity probe Silooth %s" % (
        len(res), red, unm, {True: "PASS", False: "FAIL", None: "ABSENT"}[probe]))
    return 1 if (red or not probe) else 0


if __name__ == "__main__":
    sys.exit(main())
