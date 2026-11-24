#!/usr/bin/env python3
"""loaded_build.py - compare what a running game has LOADED with what was meant (the receipt of jawa/running_mods loadedOf=ours).

Page: design/specs/2026-11-23-loaded-receipt/boundary.md. `build_match.py loaded` is its command line; build_match.identity
hashes the deployed FOLDER and says nothing about the process. A loaded module's id (MVID) is written by the compiler into the
DLL; a DLL file holds the loaded code exactly when its bytes hold that id.

verdict  MATCH            every DLL of the mod is loaded, and the loaded id is in the deployed file and in the committed file;
                          the running list is the expected list; the game is the expected game
         WRONG_BUILD      a loaded id is in neither or only one of them (named), or the file changed after the load
         NOT_LOADED       a DLL of the mod is not loaded (named)
         FOREIGN_COPY     a DLL was loaded from outside the mod's folder
         WRONG_LIST, WRONG_GAME   with the first difference
         NO_ASSEMBLY      the mod ships no DLL: its loaded code cannot be identified (never MATCH)
         COULD_NOT_LOOK   the receipt, a file or the expectation could not be read (cause in why)
A fault that was seen outranks one that could not be looked for. Exit 0 MATCH, 1 a fault, 2 COULD_NOT_LOOK, 4 NO_ASSEMBLY."""
import hashlib
import json
import os
import subprocess
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
MATCH, WRONG_BUILD, NOT_LOADED, FOREIGN, WRONG_LIST, WRONG_GAME, NO_ASM, BLIND = (
    "MATCH", "WRONG_BUILD", "NOT_LOADED", "FOREIGN_COPY", "WRONG_LIST", "WRONG_GAME", "NO_ASSEMBLY", "COULD_NOT_LOOK")
FAULTS = (WRONG_GAME, WRONG_BUILD, FOREIGN, NOT_LOADED, WRONG_LIST)
EXIT = {MATCH: 0, BLIND: 2, NO_ASM: 4}
CALL = {"details": False, "assembly": "", "loadedOf": "ours"}


def norm(p):
    p = str(p or "").strip().lower()
    return p[:-len("_steam")] if p.endswith("_steam") else p


def fingerprint(ids):
    """Equal to JawaBenchReceiptCore.Fingerprint."""
    return "sha256:" + hashlib.sha256("".join(norm(i) + "\n" for i in ids).encode("utf-8")).hexdigest()


def holds_mvid(raw, mvid):
    """True/False, or None when there are no bytes or no id. Equal to JawaBenchReceiptCore.HoldsMvid."""
    try:
        want = uuid.UUID(str(mvid))
    except (ValueError, AttributeError):
        return None
    if not raw or want.int == 0:
        return None
    return want.bytes_le in raw


def _bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def dlls(folder):
    """{file name lower: [paths]} of every DLL in an Assemblies folder under `folder`; None when there is no folder."""
    if not folder or not os.path.isdir(folder):
        return None
    out = {}
    for root, dirs, names in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if d.lower() not in ("bin", "obj", ".git", "source"))
        if os.path.basename(root).lower() == "assemblies":
            for n in sorted(names):
                if n.lower().endswith(".dll"):
                    out.setdefault(n.lower(), []).append(os.path.join(root, n))
    return out


def _file_name(location):
    return str(location or "").replace("\\", "/").rsplit("/", 1)[-1].lower()


def _any_holds(paths, mvid):
    got = [holds_mvid(_bytes(p), mvid) for p in paths]
    return True if True in got else (None if None in got else False)


def judge(reply, pid, deployed, source, expected_ids=None, expected_game=None, part=None):
    """reply: jawa/running_mods' reply. pid: the packageId that carries the mod. deployed, source: {name: [paths]} or None
    (could not read). expected_ids: the list the run meant, None = could not be read. expected_game: a bridge key, None =
    not asked. part: for a member composed into another mod, only its own DLLs are judged.
    -> {verdict, why[], assemblies[], game, tick, fingerprint, count}"""
    res = {"verdict": BLIND, "why": [], "assemblies": [], "game": None, "tick": None, "fingerprint": None, "count": None}
    found = []                                            # (verdict, why)

    def out():
        for v in FAULTS + (BLIND, NO_ASM):
            hit = [w for x, w in found if x == v]
            if hit:
                res["verdict"], res["why"] = v, [w for _v, w in found]
                return res
        res["verdict"] = MATCH
        return res

    if not isinstance(reply, dict) or reply.get("success") is not True:
        found.append((BLIND, "the bridge did not answer the receipt: %s" % (str(reply),)))
        return out()
    ld = reply.get("loaded")
    ids = reply.get("packageIds")
    if not isinstance(ld, dict) or not isinstance(ids, list) or not ids:
        found.append((BLIND, "the reply has no `loaded` receipt or no running list: the companion in that game is older than "
                             "the receipt, or loadedOf was not sent"))
        return out()
    res.update(game=ld.get("gameKey"), tick=reply.get("ticksGame"), fingerprint=ld.get("listFingerprint"), count=len(ids),
               gameVersion=ld.get("gameVersion"), pid=ld.get("pid"), companion=ld.get("companion"))
    if ld.get("listFingerprint") != fingerprint(ids):
        found.append((BLIND, "the receipt's fingerprint is not its own list's: one of the two was cut or changed"))
    if expected_game is not None and ld.get("gameKey") != expected_game:
        found.append((WRONG_GAME if ld.get("gameKey") else BLIND,
                      "the game is %s, not %s" % (ld.get("gameKey") or "unknown", expected_game)))
    if expected_ids is None:
        found.append((BLIND, "the expected mod list could not be read"))
    elif [norm(x) for x in ids] != [norm(x) for x in expected_ids]:
        a, b = [norm(x) for x in ids], [norm(x) for x in expected_ids]
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        found.append((WRONG_LIST, "running %d mods, expected %d; first difference at %d: running %s, expected %s"
                      % (len(a), len(b), i, a[i] if i < len(a) else "(end)", b[i] if i < len(b) else "(end)")))
    row = next((m for m in ld.get("mods") or [] if norm(m.get("packageId")) == norm(pid)), None)
    if row is None:
        found.append((NOT_LOADED if norm(pid) not in [norm(x) for x in ids] else BLIND, "%s is not in the receipt" % pid))
        return out()
    if deployed is None or source is None:
        found.append((BLIND, "the %s folder of the mod could not be read" % ("deployed" if deployed is None else "source")))
        return out()
    names = sorted(set(deployed) | set(source))
    if not names:
        found.append((NO_ASM, "%s ships no DLL: its loaded code cannot be identified" % (part or pid)))
    by_file = {}
    for a in row.get("assemblies") or []:
        by_file.setdefault(_file_name(a.get("location")), []).append(a)
    for n in names:
        rows = by_file.get(n) or []
        if not rows:
            found.append((NOT_LOADED, "%s is not loaded by %s (%s)" % (n, pid, row.get("why") or row.get("state"))))
            res["assemblies"].append({"dll": n, "verdict": NOT_LOADED})
            continue
        for a in rows:
            dep = _any_holds(deployed.get(n, []), a.get("mvid")) if n in deployed else False
            src = _any_holds(source.get(n, []), a.get("mvid")) if n in source else False
            v, why = MATCH, None
            if row.get("state") == "FOREIGN_COPY" and (a.get("name") or "?") in str(row.get("why")):
                v, why = FOREIGN, row.get("why")
            elif dep is False or src is False:
                v = WRONG_BUILD
                why = "%s: the loaded code (MVID %s) is not in the %s file" % (
                    n, a.get("mvid"), " or the ".join(k for k, ok in (("deployed", dep), ("committed", src)) if ok is False))
            elif a.get("fileHoldsLoadedCode") is False:
                v, why = WRONG_BUILD, "%s: the file on disk changed after the game loaded it" % n
            elif dep is None or src is None or a.get("fileHoldsLoadedCode") is None:
                v, why = BLIND, "%s: a file or the loaded id could not be read" % n
            if v != MATCH:
                found.append((v, why))
            res["assemblies"].append({"dll": n, "mvid": a.get("mvid"), "verdict": v, "deployed": dep, "committed": src})
    if names and row.get("state") not in ("LOADED",) and not part and not any(v in FAULTS for v, _w in found):
        found.append((BLIND, "%s reads %s in the game: %s" % (pid, row.get("state"), row.get("why"))))
    return out()


def unwrap(reply):
    """The tool's own reply out of the bridge's content envelope."""
    if isinstance(reply, dict) and isinstance(reply.get("content"), list) and reply["content"]:
        try:
            return json.loads(reply["content"][0]["text"])
        except (ValueError, KeyError, IndexError, TypeError):
            return {"success": False, "message": "the bridge's content could not be read"}
    return reply


def fetch(utils):
    """Read the receipt from the game this shell means, over the bridge (Windows python.exe: the bridge is on Windows
    loopback). -> the reply, or {"success": False, "message": cause}."""
    client = os.path.join(utils, "rimbridge_client.py")
    py = sys.executable if os.name == "nt" else "python.exe"
    try:
        if os.name != "nt":
            client = subprocess.run(["wslpath", "-w", client], capture_output=True, text=True, timeout=60).stdout.strip()
        # 300 s: a hang guard on a call that answers in under a second; a game on a stalled frame can hold it
        p = subprocess.run([py, client, "--call", "jawa/running_mods", "--json", json.dumps(CALL)],
                           capture_output=True, text=True, errors="replace", timeout=300)
        return unwrap(json.loads(p.stdout)) if p.stdout.strip() else {"success": False, "message": (p.stderr or "no answer").strip()}
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return {"success": False, "message": "%s: %s" % (type(e).__name__, e)}


def loaded(root, mod, reply, mods_dir=None, config=None, scan=None, expected_game=None):
    """The whole reading for one mod: build_match's own folders and list readers, then judge()."""
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import build_match as B
    if None in (mods_dir, config):
        m, c, _v = B._paths()
        mods_dir, config = mods_dir or m, config or c
    pid, folder = B._mod_folder(root, mod, mods_dir)
    comp = B.composed_into(root, mod)
    part = None
    if comp == B.COMPOSE_UNREADABLE:
        folder = None
    elif comp:
        pid, part, folder = comp[0], mod, os.path.join(folder, "Biomes", mod) if folder else None
    am, ids = B.active_mods(config), None
    if am:
        here, _absent, bad = B._installed_only(am, mods_dir, scan)
        ids = here if not bad else None
    out = judge(reply, pid, dlls(folder), dlls(os.path.join(root, "src", "RimMandrake", mod)), ids, expected_game, part)
    out["mod"] = mod
    return out
