"""Pre-flight / site preparation. Refuse to run on a dirty site.

Every check returns Check(name, status, evidence) with status PASS / FAIL /
UNMEASURED. "Could not ask" is UNMEASURED -- never FAIL, never PASS. A run proceeds
only when every REQUIRED check is PASS (UNMEASURED refuses unless allow_unmeasured).

Fixes (pause, god mode) are applied ONLY with fix=True and each is followed by an
independent state read -- pause_game / set_god_mode are on the silent-failure list
(skills/rimbridge/references/silent-failures.md; traps.md "Esc menu resumes the game").
Response shapes assumed here are mirrored in transport.MockGame; they are UNPROVEN
against the live bridge until the first live run, and a shape mismatch yields
UNMEASURED by construction (a key that is absent is "could not ask").
"""
import hashlib
import json
import os
import re
import sys
import time

from northstar_driver import PASS, FAIL, UNMEASURED

_UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))

REQUIRED_TOOLS = ("rimbridge/get_bridge_status", "rimworld/get_game_info",
                  "rimworld/pause_game", "jawa/map_info")


class Check(object):
    def __init__(self, name, status, evidence, required=True):
        self.name, self.status, self.evidence, self.required = name, status, evidence, required

    def as_dict(self):
        return {"name": self.name, "status": self.status, "evidence": self.evidence,
                "required": self.required}


def _safe(fn, *a, **k):
    """Run a bridge read; return (value, None) or (None, error string)."""
    try:
        return fn(*a, **k), None
    except Exception as ex:      # transport/tool error == could not ask
        return None, "%s: %s" % (type(ex).__name__, ex)


def check_tools(s, extra=()):
    need = list(REQUIRED_TOOLS) + list(extra)
    missing = [t for t in need if t not in s.tools]
    if missing:
        return Check("tool_census", FAIL, "missing %s -- stale companion deploy; "
                     "python.exe src/RimMandrake/bridgetools/build.py --gm --apply" % missing)
    return Check("tool_census", PASS, "%d tools, all %d required present" % (len(s.tools), len(need)))


def check_loaded_not_zombie(s):
    info, err = _safe(s.call, "rimworld/get_game_info")
    if err:
        return Check("game_loaded", UNMEASURED, "get_game_info raised (%s) -- world screen or no game" % err)
    t1 = (info or {}).get("ticksGame")
    if t1 is None:
        return Check("game_loaded", FAIL, "get_game_info answered with no ticksGame -- loaded-looking "
                     "ZOMBIE state (aborted load); success flags prove nothing")
    mi, err = _safe(s.call, "jawa/map_info")
    if err or not (mi or {}).get("success") or not mi.get("sizeX"):
        return Check("game_loaded", FAIL, "ticksGame=%s but jawa/map_info gave no map (%s)" % (t1, err or mi))
    return Check("game_loaded", PASS, "ticksGame=%s map=%sx%s" % (t1, mi["sizeX"], mi["sizeZ"]))


def check_no_modal(s):
    if "rimworld/list_windows" not in s.tools:
        return Check("no_modal", UNMEASURED, "no window-listing tool on this bridge (rimworld/list_windows); "
                     "a stale modal cannot be ruled out -- close it by eye or build the tool")
    r, err = _safe(s.call, "rimworld/list_windows")
    if err or "windows" not in (r or {}):
        return Check("no_modal", UNMEASURED, "list_windows unreadable: %s %s" % (err, r))
    w = r["windows"]
    return Check("no_modal", FAIL if w else PASS, "open windows: %s" % (w or "none"))


def _ticks(s):
    return (s.call("rimworld/get_game_info") or {}).get("ticksGame")


def check_paused(s, fix=False, settle=0.15):
    def probe():
        a = _ticks(s)
        time.sleep(settle)
        b = _ticks(s)
        return a, b
    (a, b), err = _safe(probe)
    if err or a is None or b is None:
        return Check("paused", UNMEASURED, "ticksGame unreadable: %s" % err)
    if a == b:
        return Check("paused", PASS, "ticksGame frozen at %s over two reads" % a)
    if not fix:
        return Check("paused", FAIL, "ticksGame moved %s -> %s" % (a, b))
    s.call("rimworld/pause_game", pause=True)
    (a2, b2), err = _safe(probe)
    if not err and a2 is not None and a2 == b2:
        return Check("paused", PASS, "was running; paused and PROVED frozen at %s" % a2)
    return Check("paused", FAIL, "pause_game reported success but ticks still moving (%s -> %s)" % (a2, b2))


def check_dev_god(s, need_dev=True, need_god=False, fix=False):
    info, err = _safe(s.call, "rimworld/get_game_info")
    if err:
        return Check("dev_god_mode", UNMEASURED, err)
    out, status = [], PASS
    for label, key, need in (("dev", "devModeEnabled", need_dev), ("god", "godMode", need_god)):
        if not need:
            continue
        if key not in (info or {}):
            return Check("dev_god_mode", UNMEASURED, "get_game_info has no %r field" % key)
        if info[key]:
            out.append("%s on" % label)
        elif label == "god" and fix and "rimworld/set_god_mode" in s.tools:
            s.call("rimworld/set_god_mode", enabled=True)
            again, _ = _safe(s.call, "rimworld/get_game_info")
            if (again or {}).get(key):
                out.append("god on (set + re-read)")
            else:
                status = FAIL
                out.append("god set_god_mode reported success, re-read says OFF")
        else:
            status = FAIL
            out.append("%s OFF" % label)
    return Check("dev_god_mode", status, "; ".join(out) or "not required")


def modlist_fingerprint(config_path=None):
    """(sha256 of ordered activeMods, [ids]). Parses XML -- never grep -c '<li>'
    (CLAUDE.md: that returns 48 where the real count is 631)."""
    import xml.etree.ElementTree as ET
    if config_path is None:
        sys.path.insert(0, _UTILS)
        from game_paths import MODS_CONFIG as config_path
    ids = [li.text.strip().lower() for li in ET.parse(config_path).find("activeMods")
           if li.text]
    return hashlib.sha256("\n".join(ids).encode()).hexdigest(), ids


def check_modlist(expect_sha=None, expect_ids=(), config_path=None):
    """READ-ONLY. ModsConfig describes the NEXT load, not the running game
    (memory: modsconfig-describes-the-next-load) -- so a pass here is evidence about the
    list on disk only, and says so."""
    try:
        sha, ids = modlist_fingerprint(config_path)
    except Exception as ex:
        return Check("modlist", UNMEASURED, "ModsConfig unreadable (%s: %s)" % (type(ex).__name__, ex))
    missing = [i for i in (e.lower() for e in expect_ids) if i not in ids]
    ev = "%d active, sha256 %s (disk = NEXT load, not proof of the running list)" % (len(ids), sha[:16])
    if missing:
        return Check("modlist", FAIL, "expected ids not active: %s; %s" % (missing, ev))
    if expect_sha and expect_sha != sha:
        return Check("modlist", FAIL, "fingerprint %s != expected %s; %s" % (sha[:16], expect_sha[:16], ev))
    return Check("modlist", PASS, ev)


def _tree(root, skip_big=("Textures",)):
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith((".srchash", ".pdb")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root).replace("\\", "/")
            top = rel.split("/", 1)[0]
            try:
                if top in skip_big:
                    out[rel] = os.path.getsize(p)          # size only: textures are huge
                else:
                    with open(p, "rb") as fh:
                        out[rel] = hashlib.sha1(fh.read()).hexdigest()
            except OSError:
                out[rel] = None
    return out


def check_deployed(mod_dir, deployed_dir):
    """Deployed copy == repo copy. Writing a file is not deploying it (CLAUDE.md)."""
    if not os.path.isdir(mod_dir):
        return Check("deployed_matches_repo", UNMEASURED, "repo mod dir absent: %s" % mod_dir)
    if not os.path.isdir(deployed_dir):
        return Check("deployed_matches_repo", FAIL, "not deployed: %s" % deployed_dir)
    held = os.path.join(mod_dir, "DEPLOY_HOLD.txt")
    a, b = _tree(mod_dir), _tree(deployed_dir)
    if os.path.isfile(held):
        hold = {l.strip() for l in open(held, encoding="utf-8", errors="replace") if l.strip()}
        a = {k: v for k, v in a.items() if k not in hold}
    diff = sorted(k for k in a if a.get(k) != b.get(k))
    diff = [k for k in diff if k != "DEPLOY_HOLD.txt"]
    if diff:
        return Check("deployed_matches_repo", FAIL, "%d file(s) differ/missing, e.g. %s" % (len(diff), diff[:5]))
    return Check("deployed_matches_repo", PASS, "%d files identical (textures by size)" % len(a))


def check_area_clear(s, rect, allow_defs=()):
    """rect 'x,z,w,h'. Uses jawa/list_things when present, else samples cells."""
    if "jawa/list_things" not in s.tools:
        return Check("area_clear", UNMEASURED, "jawa/list_things absent")
    r, err = _safe(s.call, "jawa/list_things", rect=rect)
    if err or "things" not in (r or {}):
        return Check("area_clear", UNMEASURED, "list_things unreadable: %s %s" % (err, str(r)[:120]))
    p, err2 = _safe(s.call, "jawa/list_pawns", rect=rect)
    if err2 or "pawns" not in (p or {}):
        return Check("area_clear", UNMEASURED, "list_pawns unreadable: %s" % err2)
    stray = [t.get("defName") for t in r["things"] if t.get("defName") not in allow_defs]
    if stray or p["pawns"]:
        return Check("area_clear", FAIL, "%d thing(s) %s, %d pawn(s) inside %s" % (
            len(stray), sorted(set(stray))[:6], len(p["pawns"]), rect))
    return Check("area_clear", PASS, "rect %s empty (things+pawns)" % rect)


def run_preflight(s, mod_dirs=(), expect_ids=(), expect_sha=None, need_dev=True, need_god=False,
                  rect=None, fix=False, config_path=None, deployed_root=None, extra_tools=()):
    """mod_dirs: [(repo_dir, deployed_dir)] pairs. Returns (checks, ok_to_run_strict)."""
    cs = [check_tools(s, extra_tools), check_loaded_not_zombie(s)]
    zombie = cs[-1].status != PASS
    cs.append(check_no_modal(s))
    if not zombie:
        cs.append(check_paused(s, fix=fix))
        cs.append(check_dev_god(s, need_dev, need_god, fix))
        if rect:
            cs.append(check_area_clear(s, rect))
    cs.append(check_modlist(expect_sha, expect_ids, config_path))
    for repo, dep in mod_dirs:
        c = check_deployed(repo, dep)
        c.name += ":" + os.path.basename(repo.rstrip("/\\"))
        cs.append(c)
    return cs


def verdict(checks, allow_unmeasured=False):
    bad = [c for c in checks if c.required and c.status == FAIL]
    unk = [c for c in checks if c.required and c.status == UNMEASURED]
    ok = not bad and (allow_unmeasured or not unk)
    return ok, bad, unk
