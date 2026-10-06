"""modcheck/reviewmap.py -- the pieces every Northstar "for the human" review-map builder shares.

Used by src/RimMandrake/GimmeSomeSlack/save_review_map.py and src/RimMandrake/FlowWorks/review_map.py
(NORTHSTAR_PROCESS_RETRO_1 candidate helpers: kill_hostiles, save_keeper). Only what both builders need:

  * saves_stat / free_save_name / save_keeper -- a keeper savegame with the before/after Saves stat. rimworld/save_game
    has silently written the CURRENT slot instead of saveName, so a save is OK only when exactly one NEW file named
    <name>.rws appeared and no existing file changed size or mtime or vanished.
  * sweep_pawns -- owner 2026-10-05: "kill all hostiles on any review map". With no keep rects it is the GSS sweep
    (jawa/destroy_bulk nonColonists + incident queue cleared). With keep rects (stations that HOLD animals or
    prisoners on purpose) every non-colonist outside them is removed and the ones inside are kept.
  * label_line -- one jawa/review_label op line, with the separator and newlines made safe.
  * LiveBridge -- a plain socket to the bridge (python.exe on the Windows side; WSL cannot reach it).

Selftest: selftest_reviewmap.py (fake bridge, 0 game).
"""
import json
import os
import time

SAVES = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Ludeon Studios",
                     "RimWorld by Ludeon Studios", "Saves")


def saves_stat(saves=None):
    d = saves or SAVES
    return {n: (os.path.getsize(os.path.join(d, n)), int(os.path.getmtime(os.path.join(d, n))))
            for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))}


def free_save_name(base, existing):
    """base if base.rws is not taken, else base_b, base_c, ... (saves stay until the owner says delete)."""
    if base + ".rws" not in existing:
        return base
    for c in "bcdefghijklmnopqrstuvwxyz":
        if "%s_%s.rws" % (base, c) not in existing:
            return "%s_%s" % (base, c)
    raise ValueError("no free name for %s" % base)


def judge_save(before, after, name):
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    gone = sorted(set(before) - set(after))
    return dict(ok=(new == [name + ".rws"] and not changed and not gone), new=new, changed=changed, gone=gone)


def save_keeper(B, name, saves=None, wait_s=30.0, poll_s=1.0, stat=saves_stat, sleep=time.sleep):
    """Save the live game as <name>.rws and prove it: -> dict(ok, name, new, changed, gone, tool). Refuses (ok False,
    refused=...) when <name>.rws already exists; never overwrites."""
    before = stat(saves)
    if name + ".rws" in before:
        return dict(ok=False, name=name, refused="%s.rws already exists" % name, new=[], changed=[], gone=[], tool=None)
    r = B.call("rimworld/save_game", saveName=name)
    t0 = time.time()
    after = before
    while True:
        sleep(poll_s)
        after = stat(saves)
        if name + ".rws" in after or time.time() - t0 > wait_s:
            break
    sleep(poll_s)                                   # let the writer finish: a size still growing reads as "changed"
    after = stat(saves)
    out = judge_save(before, after, name)
    out.update(name=name, tool=r.get("success") if isinstance(r, dict) else r)
    return out


def _inside(x, z, rects):
    return any(rx <= x < rx + rw and rz <= z < rz + rh for rx, rz, rw, rh in rects)


def sweep_pawns(B, keep_rects=()):
    """-> dict(matched, removed, kept). Non-colonist pawns outside keep_rects are removed (no corpse, no explosion:
    destroy_bulk), the incident queue is emptied. Pawns inside keep_rects are kept (a held creature, a prisoner)."""
    keep_rects = list(keep_rects)
    if not keep_rects:
        r = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        B.call("jawa/incident_queue_clear")
        return dict(matched=r.get("matchedCount"), removed=r.get("matchedCount"), kept=0)
    rows = B.call("jawa/list_pawns", limit=500).get("pawns") or []
    kept, out = [], []
    for p in rows:
        if p.get("dead") or (p.get("isPlayer") and p.get("intelligence") == "Humanlike"):
            continue
        x, z = pawn_xz(p)
        (kept if x is not None and _inside(x, z, keep_rects) else out).append(p)
    if out and not kept:            # nothing held on purpose: the clean route (no corpse, no boomalope blast)
        r = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        B.call("jawa/incident_queue_clear")
        return dict(matched=len(out), removed=r.get("matchedCount"), kept=0)
    removed = 0
    # destroy_bulk has no exclusion list, so with keep rects the outsiders are killed per id (a corpse is left
    # outside the stations; builders sweep with NO keep rects before they spawn their held creatures, so this
    # path only meets what arrived after the build).
    for p in out:
        r = B.call("jawa/pawn_force_incapacitate", pawn=str(p.get("id")), action="kill")
        removed += 1 if r.get("success") else 0
    B.call("jawa/incident_queue_clear")
    return dict(matched=len(out), removed=removed, kept=len(kept))


def pawn_xz(p):
    if "x" in p and "z" in p:
        return p.get("x"), p.get("z")
    pos = p.get("position") or p.get("pos")
    if isinstance(pos, dict):
        return pos.get("x"), pos.get("z")
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        return pos[0], pos[-1]
    if isinstance(pos, str) and "," in pos:
        v = [s.strip(" ()") for s in pos.split(",")]
        try:
            return int(v[0]), int(v[-1])
        except ValueError:
            return None, None
    return None, None


def label_line(x, z, text, sub="", col="#ffd27f", size="medium", tag=""):
    clean = lambda s: str(s).replace("|", "/").replace("\n", " ").replace("\r", " ")
    return "%d|%d|%s|%s|%s|%s|%s" % (x, z, clean(text), clean(sub), col, size, tag)


class LiveBridge(object):
    """call / ticks over the RimBridge socket (python.exe only: RimBridge binds Windows loopback)."""

    def __init__(self):
        import sys
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if here not in sys.path:
            sys.path.insert(0, here)
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()

    def call(self, tool, **kw):
        r = self.S.call(tool, kw, check=False) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:  # noqa: BLE001
                pass
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=120000)
