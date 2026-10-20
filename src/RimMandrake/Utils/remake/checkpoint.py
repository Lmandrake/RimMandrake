#!/usr/bin/env python3
"""World-remake checkpoints C1-C3 (runbook 06 §4) and the settings snapshot (gate G3), with sha256.

Runbook gates served: G3 (mod settings frozen: C3 + `verify --against-live`), G17 (checkpoints exist: `status`).

    checkpoint.py make   --ids C2,C3 [--root /mnt/d/ClaudeWork/remake] [--date 2026-10-20]
    checkpoint.py verify <root>/<date>/<Cid>              # copies still match their manifest (integrity)
    checkpoint.py verify <root>/<date>/<Cid> --against-live   # live files unchanged since the snapshot (G3)
    checkpoint.py status [--root R] [--date D]            # G17: PASS only if C1, C2, C3 exist and verify clean
    checkpoint.py restore <root>/<date>/<Cid>             # prints the copy-back plan; --apply --game-is-down writes

What each checkpoint copies (sources are read-only; the copy never writes the live folder):
  C1  the whole Saves folder (6.3 GB on 2026-10-19; slow /mnt/c -> /mnt/d copy)
  C2  live Config/ModsConfig.xml + the repo's infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml
  C3  Config/Mod_*.xml (includes Cherry Picker's Mod_3521312241_Mod_CherryPicker.xml), Config/Mod_*/ folders,
      Config/GravshipExport/, Config/Prefs.xml, Config/ModSettingsFrameworkMod_Settings.xml, and ModsConfig.xml
      again (so C3 alone answers "what was the list when the settings were frozen")
  Backups beside live files (*.bak*, *.tuned, ModsConfig.*.xml variants) are NOT settings and are skipped.

Each checkpoint dir holds MANIFEST.json (rel, role, size, sha256 of the source as read) and SHA256SUMS
(`sha256sum -c SHA256SUMS` works from inside the dir). A make never overwrites: an existing non-empty
<date>/<Cid> makes it refuse (pass --suffix to make a second one).

Exit codes: 0 ok/PASS · 1 FAIL (difference found) · 2 UNMEASURED (cannot read what it must judge) · 3 refused.
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.dirname(HERE))
try:
    import game_paths  # noqa: E402
    LOCALLOW_DEFAULT = game_paths.LOCALLOW
except Exception:  # pragma: no cover
    LOCALLOW_DEFAULT = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"
ROOT_DEFAULT = "/mnt/d/ClaudeWork/remake"
FULL_LATEST = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml")
CHERRY = "Mod_3521312241_Mod_CherryPicker.xml"
SKIP_PATTERNS = ("*.bak*", "*.tuned", "*.belt_bak*", "*.pre_*")


def sha256(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(bufsize), b""):
            h.update(b)
    return h.hexdigest()


def _walk_files(d):
    for dp, dn, fn in os.walk(d):
        dn.sort()
        for f in sorted(fn):
            yield os.path.join(dp, f)


def sources(cid, locallow, full_latest=FULL_LATEST):
    """[(abs_src, rel_in_checkpoint, role)] for one checkpoint. Missing REQUIRED sources raise FileNotFoundError."""
    cfg = os.path.join(locallow, "Config")
    out = []
    if cid == "C1":
        saves = os.path.join(locallow, "Saves")
        if not os.path.isdir(saves):
            raise FileNotFoundError(saves)
        for p in _walk_files(saves):
            out.append((p, os.path.join("Saves", os.path.relpath(p, saves)), "save"))
    elif cid == "C2":
        mc = os.path.join(cfg, "ModsConfig.xml")
        if not os.path.isfile(mc):
            raise FileNotFoundError(mc)
        out.append((mc, "Config/ModsConfig.xml", "live ModsConfig"))
        if os.path.isfile(full_latest):
            out.append((full_latest, "repo/ModsConfig.FULL.LATEST.xml", "repo FULL.LATEST"))
    elif cid == "C3":
        if not os.path.isdir(cfg):
            raise FileNotFoundError(cfg)
        names = sorted(os.listdir(cfg))
        for n in names:
            p = os.path.join(cfg, n)
            if any(fnmatch.fnmatch(n, s) for s in SKIP_PATTERNS):
                continue
            if os.path.isfile(p) and fnmatch.fnmatch(n, "Mod_*.xml"):
                out.append((p, "Config/" + n, "cherry picker" if n == CHERRY else "mod settings"))
            elif os.path.isdir(p) and n.startswith("Mod_"):
                for q in _walk_files(p):
                    out.append((q, "Config/" + os.path.relpath(q, cfg), "mod settings folder"))
        for n, role in (("Prefs.xml", "game prefs"), ("ModSettingsFrameworkMod_Settings.xml", "mod settings"),
                        ("ModsConfig.xml", "live ModsConfig")):
            p = os.path.join(cfg, n)
            if os.path.isfile(p):
                out.append((p, "Config/" + n, role))
        gx = os.path.join(cfg, "GravshipExport")
        if os.path.isdir(gx):
            for q in _walk_files(gx):
                out.append((q, "Config/" + os.path.relpath(q, cfg), "gravship export"))
        if not any(r == "cherry picker" for _, _, r in out):
            out.append((os.path.join(cfg, CHERRY), "Config/" + CHERRY, "cherry picker (MISSING)"))
    else:
        raise ValueError("unknown checkpoint %r (C1, C2, C3)" % cid)
    return out


def copy_hashed(src, dst):
    """Copy src->dst hashing the bytes as read; re-hash dst; return (sha, size). Raises on mismatch."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    h = hashlib.sha256()
    n = 0
    with open(src, "rb") as fi, open(dst, "wb") as fo:
        for b in iter(lambda: fi.read(1 << 20), b""):
            h.update(b)
            fo.write(b)
            n += len(b)
    shutil.copystat(src, dst)
    s = h.hexdigest()
    if sha256(dst) != s:
        raise IOError("copy mismatch: %s" % dst)
    return s, n


def make(cid, root, date, locallow, suffix="", full_latest=FULL_LATEST):
    d = os.path.join(root, date, cid + suffix)
    if os.path.isdir(d) and os.listdir(d):
        print("REFUSED %s exists and is not empty (never overwritten; pass --suffix)" % d)
        return 3
    try:
        srcs = sources(cid, locallow, full_latest)
    except FileNotFoundError as e:
        print("UNMEASURED %s: source missing %s" % (cid, e))
        return 2
    os.makedirs(d, exist_ok=True)
    files, missing = [], []
    for src, rel, role in srcs:
        if not os.path.isfile(src):
            missing.append(rel)
            continue
        s, n = copy_hashed(src, os.path.join(d, rel))
        files.append({"rel": rel, "role": role, "src": src, "size": n, "sha256": s})
    man = {"checkpoint": cid, "made_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "locallow": locallow, "files": files, "missing": missing}
    json.dump(man, open(os.path.join(d, "MANIFEST.json"), "w"), indent=1)
    with open(os.path.join(d, "SHA256SUMS"), "w") as f:
        for x in files:
            f.write("%s  %s\n" % (x["sha256"], x["rel"]))
    tot = sum(x["size"] for x in files)
    print("MADE %s %d files %.1f MB -> %s%s" % (cid, len(files), tot / 1e6, d,
                                                ("  MISSING: " + ", ".join(missing)) if missing else ""))
    return 1 if missing else 0


def _load(d):
    p = os.path.join(d, "MANIFEST.json")
    if not os.path.isfile(p):
        return None
    return json.load(open(p))


def verify(d, against_live=False, locallow=None, quiet=False):
    man = _load(d)
    if man is None:
        print("UNMEASURED no MANIFEST.json in %s" % d)
        return 2
    bad = []
    if not man["files"]:
        print("UNMEASURED %s manifest lists 0 files" % d)
        return 2
    if against_live:
        ll = locallow or man["locallow"]
        cfg_live = os.path.join(ll, "Config")
        if not os.path.isdir(cfg_live):
            print("UNMEASURED live Config not readable: %s" % cfg_live)
            return 2
        for x in man["files"]:
            src = x["src"] if locallow is None else x["src"].replace(man["locallow"], locallow, 1)
            if not os.path.isfile(src):
                bad.append(("GONE", x["rel"]))
            elif sha256(src) != x["sha256"]:
                bad.append(("CHANGED", x["rel"]))
        try:
            now = {rel for _, rel, _ in sources(man["checkpoint"], ll, FULL_LATEST)}
        except FileNotFoundError:
            now = set()
        known = {x["rel"] for x in man["files"]} | set(man.get("missing", []))
        bad += [("NEW", r) for r in sorted(now - known)]
    else:
        # make() exits 1 on a missing source; the copy verify must not turn that into a PASS
        bad += [("MISSING", r) for r in man.get("missing", [])]
        for x in man["files"]:
            p = os.path.join(d, x["rel"])
            if not os.path.isfile(p):
                bad.append(("GONE", x["rel"]))
            elif sha256(p) != x["sha256"]:
                bad.append(("CORRUPT", x["rel"]))
    mode = "live" if against_live else "copy"
    if bad:
        print("FAIL %s %s: %d of %d differ" % (man["checkpoint"], mode, len(bad), len(man["files"])))
        for k, r in bad[:40]:
            print("  %-7s %s" % (k, r))
        return 1
    if not quiet:
        print("PASS %s %s: %d files match" % (man["checkpoint"], mode, len(man["files"])))
    return 0


def status(root, date):
    base = os.path.join(root, date)
    worst = 0
    for cid in ("C1", "C2", "C3"):
        d = os.path.join(base, cid)
        if not os.path.isdir(d):
            print("FAIL %s absent (%s)" % (cid, d))
            worst = max(worst, 1)
            continue
        worst = max(worst, verify(d))
    print("G17 %s" % {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[worst])
    return worst


def restore(d, apply=False, game_is_down=False, locallow=None):
    man = _load(d)
    if man is None:
        print("UNMEASURED no MANIFEST.json in %s" % d)
        return 2
    ll = locallow or man["locallow"]
    plan = []
    for x in man["files"]:
        if x["rel"].startswith("repo/"):
            continue  # repo files are restored by git, not by this tool
        plan.append((os.path.join(d, x["rel"]), os.path.join(ll, x["rel"])))
    for s, t in plan[:20]:
        print("  %s -> %s" % (s, t))
    print("PLAN %d files back to %s%s" % (len(plan), ll, "" if apply else " (dry run; --apply --game-is-down writes)"))
    if not apply:
        return 0
    if not game_is_down:
        print("REFUSED --apply needs --game-is-down (copy back only with RimWorld closed: it rewrites settings on exit)")
        return 3
    if verify(d, quiet=True) != 0:
        print("REFUSED the checkpoint copy does not match its manifest")
        return 3
    for s, t in plan:
        os.makedirs(os.path.dirname(t), exist_ok=True)
        shutil.copy2(s, t)
    print("RESTORED %d files" % len(plan))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("make")
    m.add_argument("--ids", default="C2,C3")
    m.add_argument("--root", default=ROOT_DEFAULT)
    m.add_argument("--date", default=datetime.date.today().isoformat())
    m.add_argument("--locallow", default=LOCALLOW_DEFAULT)
    m.add_argument("--suffix", default="")
    v = sp.add_parser("verify")
    v.add_argument("dir")
    v.add_argument("--against-live", action="store_true")
    v.add_argument("--locallow", default=None)
    s = sp.add_parser("status")
    s.add_argument("--root", default=ROOT_DEFAULT)
    s.add_argument("--date", default=datetime.date.today().isoformat())
    r = sp.add_parser("restore")
    r.add_argument("dir")
    r.add_argument("--apply", action="store_true")
    r.add_argument("--game-is-down", action="store_true")
    r.add_argument("--locallow", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "make":
        rc = 0
        for cid in [x.strip().upper() for x in a.ids.split(",") if x.strip()]:
            rc = max(rc, make(cid, a.root, a.date, a.locallow, a.suffix))
        return rc
    if a.cmd == "verify":
        return verify(a.dir, a.against_live, a.locallow)
    if a.cmd == "status":
        return status(a.root, a.date)
    return restore(a.dir, a.apply, a.game_is_down, a.locallow)


if __name__ == "__main__":
    sys.exit(main())
