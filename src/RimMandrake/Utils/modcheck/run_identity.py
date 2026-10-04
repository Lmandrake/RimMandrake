"""modcheck.run_identity -- RUN IDENTITY, DEPLOY FINGERPRINT and per-chain MODAL CHECK (observatory S1).

Rules: design/RimMandrake/bridge_validation_observatory.md section 2.4 ("Unknown is never clean").

REUSED, not rebuilt:
  * deploy_custom_mods.compare / tree / split_held / load_holds / mod_dirs -- the deploy tool's own
    plan logic decides what is shippable, what is held (DEPLOY_HOLD.txt) and what differs, so the
    fingerprint can never disagree with `deploy_custom_mods.py`'s plan about "in sync".
  * `<dll>.srchash` sidecars (winbuild) -- recorded beside each deployed DLL's own hash.
  * MIRROR_HEAD (mirror.py) when the run executes from the writer-free mirror (no .git there).

A run (job) records, per mod it validates, a fingerprint at START and again at END of the suite. A deploy
is "proven fresh" only when BOTH are in-sync, their content hashes are identical (nothing redeployed
mid-run) and the repo side matched HEAD (clean tree in a git checkout, or the mirror, which is origin/main).
Anything else -- drift, not deployed, a hash that moved, a dirty tree, a missing end fingerprint -- is NOT
proven, and a missing fingerprint is the old `deploy-fresh-unrecorded` unknown.

Hash scope (stated, not hidden): .dll/.xml/.json/.cs-less data files are content-hashed in full; other
payload files (textures, sounds) are compared by SIZE only, because hashing a mod's art over drvfs on every
run costs minutes. A texture swapped for one of identical byte length would not show here.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
for _p in (_UTILS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

HASHED_EXTS = {".dll", ".xml", ".json", ".txt", ".cs"}
MODAL_DIALOGS = ("Dialog_NamePlayerFactionAndSettlement", "Dialog_ModSettings")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def _rolled(root, rels):
    h = hashlib.sha256()
    for rel in sorted(rels):
        p = os.path.join(root, rel)
        try:
            tag = _sha(p) if os.path.splitext(rel)[1].lower() in HASHED_EXTS else "size:%d" % os.path.getsize(p)
        except OSError:
            tag = "unreadable"
        h.update(("%s\0%s\n" % (rel.replace(os.sep, "/"), tag)).encode())
    return h.hexdigest()[:16]


# ------------------------------------------------------------------ run identity

def _git(root, *args, timeout=30):
    """Run `git -C <root> args` and return the CompletedProcess. Under Windows python.exe (the runner's interpreter) a
    \\\\wsl.localhost\\<distro>\\... checkout has no usable Windows git, so the repo identity read 'unknown' and EVERY
    run's deploy fingerprint was 'unproven' (load 13): there git runs inside WSL through wsl.exe."""
    if os.name == "nt":
        norm = root.replace("/", "\\")
        low = norm.lower()
        for pre in ("\\\\wsl.localhost\\", "\\\\wsl$\\"):
            if low.startswith(pre):
                rest = norm[len(pre):].split("\\")[1:]          # drop the distro name
                return subprocess.run(["wsl.exe", "-e", "git", "-C", "/" + "/".join(rest)] + list(args),
                                      capture_output=True, text=True, timeout=timeout)
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=timeout)


def git_state(root=ROOT):
    """{"source": git|mirror|unknown, "sha": ...}. One git call; never raises."""
    if os.path.exists(os.path.join(root, ".git")):
        try:
            r = _git(root, "rev-parse", "HEAD")
            if r.returncode == 0:
                return {"source": "git", "sha": r.stdout.strip()}
        except Exception:                                         # noqa: BLE001
            pass
    mh = os.path.join(root, "MIRROR_HEAD")
    if os.path.isfile(mh):
        try:
            return {"source": "mirror", "sha": open(mh, encoding="utf-8").read().strip().split()[0]}
        except Exception:                                         # noqa: BLE001
            pass
    return {"source": "unknown", "sha": None}


def src_dirty(src_dir, root=ROOT):
    """True/False in a git checkout (uncommitted change under the mod's source dir); None when unknowable."""
    if not os.path.exists(os.path.join(root, ".git")):
        return None
    try:
        r = _git(root, "status", "--porcelain", "--", src_dir, timeout=60)
        return bool(r.stdout.strip()) if r.returncode == 0 else None
    except Exception:                                             # noqa: BLE001
        return None


def new_identity(job_id, run_id):
    return {"run_id": run_id, "job": job_id, "host_os": os.name, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "git": git_state()}


# ------------------------------------------------------------------ deploy fingerprint

def mod_fingerprint(mod, dm=None, mods_dir=None):
    """Fingerprint of one mod's repo-vs-deployed state NOW. `dm` is the deploy module (injectable for tests).
    Never raises: a failure is state `unknown` with the reason."""
    fp = {"mod": mod, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "state": "unknown", "reason": None}
    try:
        if dm is None:
            import deploy_custom_mods as dm
        dirs = dm.mod_dirs()
        src = dirs.get(mod)
        if src is None:
            fp["reason"] = "no source dir with About/About.xml for %s" % mod
            return fp
        dst = os.path.join(mods_dir or dm.LOCAL_MODS, mod)
        fp["src_dir"] = os.path.relpath(src, dm.ROOT).replace(os.sep, "/")
        if not os.path.isdir(dst):
            fp["state"], fp["reason"] = "not-deployed", dst
            return fp
        s_all, d_all = dm.tree(src), dm.tree(dst)
        holds = dm.load_holds()
        _, held = dm.split_held(holds, mod, sorted(s_all))
        held_set = {r for r, _h in held}
        s_rels = s_all - held_set
        d_rels = d_all - held_set
        new, changed, gone, same = dm.compare(src, dst)
        new = [r for r in new if r not in held_set]
        changed = [r for r in changed if r not in held_set]
        gone = [r for r in gone if r not in held_set]
        fp["src_hash"], fp["deployed_hash"] = _rolled(src, s_rels), _rolled(dst, d_rels)
        fp["n_src"], fp["n_deployed"], fp["n_held"] = len(s_rels), len(d_rels), len(held_set)
        fp["drift"] = {"new": len(new), "changed": len(changed), "gone": len(gone),
                       "sample": (new + changed + gone)[:5]}
        fp["state"] = "in-sync" if not (new or changed or gone) else "drift"
        dlls = []
        for rel in sorted(r for r in d_rels if r.lower().endswith(".dll")):
            side = os.path.join(src, rel + ".srchash")
            dlls.append({"dll": rel.replace(os.sep, "/"), "sha": _sha(os.path.join(dst, rel)),
                         "srchash": open(side, encoding="utf-8").read().strip()[:64] if os.path.isfile(side) else None})
        fp["dlls"] = dlls
        fp["src_dirty"] = src_dirty(src, dm.ROOT)
    except Exception as e:                                        # noqa: BLE001
        fp["state"], fp["reason"] = "unknown", "%s: %s" % (type(e).__name__, str(e)[:200])
    return fp


def proves_fresh(start, end, git=None):
    """(proven: bool, why: str). The ONLY path from a recorded fingerprint to a deploy attestation."""
    if not isinstance(start, dict) or not isinstance(end, dict):
        return False, "fingerprint missing at start or end"
    for tag, fp in (("start", start), ("end", end)):
        if fp.get("state") != "in-sync":
            return False, "%s state is %s" % (tag, fp.get("state"))
        if not fp.get("src_hash") or fp.get("src_hash") != fp.get("deployed_hash"):
            return False, "%s repo hash != deployed hash" % tag
        if fp.get("src_dirty"):
            return False, "%s repo source had uncommitted changes (does not match HEAD)" % tag
    if start.get("mod") != end.get("mod"):
        return False, "start/end name different mods"
    if start["src_hash"] != end["src_hash"] or start["deployed_hash"] != end["deployed_hash"]:
        return False, "content changed between start and end of the run"
    src = (git or {}).get("source")
    if src == "git" and start.get("src_dirty") is None:
        return False, "git checkout but dirtiness unknowable"
    if src not in ("git", "mirror"):
        return False, "no repo identity (neither a git checkout nor a mirror stamp)"
    return True, "in-sync at start and end, hashes unchanged, repo matches %s %s" % (src, ((git or {}).get("sha") or "")[:10])


# ------------------------------------------------------------------ modal check

def modal_sweep(call, dialogs=MODAL_DIALOGS):
    """Close each force-pause dialog type and RECORD what was found. `call` is session.call.
    -> {"found_open": bool, "dialogs": {type: closedCount|None}, "errors": [...]}. Never raises.
    found_open is True when any dialog was open (closedCount > 0): the chain that just ended, or the
    setup before this one, ran with a modal up -- the report treats that as a modal-open taint."""
    out = {"found_open": False, "dialogs": {}, "errors": []}
    for d in dialogs:
        try:
            r = call("jawa/window_list_close", action="close", typeName=d, closeAll=True)
            if isinstance(r, dict) and r.get("content") and isinstance(r["content"], list):
                try:
                    r = json.loads(r["content"][0]["text"])
                except Exception:                                 # noqa: BLE001
                    pass
            # The tool answers "nothing open" as success:false + "No open window's type name contains ..." -- the CLEAN
            # state, and the normal one. Recorded as an error it made every chain's modal check "failed" and every
            # verdict of the run unknown (load 13, 22:41 runs). Only that exact answer reads as closedCount 0.
            if isinstance(r, dict) and r.get("success") is False and \
                    str(r.get("message") or "").startswith("No open window"):
                out["dialogs"][d] = 0
                continue
            if not isinstance(r, dict) or r.get("success") is False:
                out["dialogs"][d] = None
                out["errors"].append("%s: %s" % (d, (r or {}).get("message") if isinstance(r, dict) else r))
                continue
            n = r.get("closedCount")
            out["dialogs"][d] = n
            if n:
                out["found_open"] = True
        except Exception as e:                                    # noqa: BLE001 - housekeeping, never a verdict
            out["dialogs"][d] = None
            out["errors"].append("%s: %s: %s" % (d, type(e).__name__, str(e)[:100]))
    return out
