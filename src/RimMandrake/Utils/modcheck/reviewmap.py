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
  * sign_sub / write_signs -- REVIEW SIGNS (owner, 2026-10-15: "I need text signs added to the savegame to tell me
    what to DO at each station"). sign_sub makes a station label's multi-line sub (LOOK / DO / DECIDE, joined by the
    two-character escape \\n the JawaBench drawer breaks on). The labels travel with a save as a sidecar,
    <SaveDataFolder>/JawaBenchReviewSigns/<save>.txt: the companion writes it on every SaveGame and reads it back on
    load; write_signs writes the same file offline (and save_keeper does when given the label ops), so a keeper made
    before the companion learned this still gets its signs.
  * sign_book / place_signs -- THE SIGNS THAT ARE IN THE SAVE (BENCH, 2026-10-15: they "must survive a plain load by
    the owner with no agent tool touching the game first"). One vanilla Novel per station, placed by jawa/review_sign:
    its title (shown on mouse-over and the inspect pane) is "SIGN <n> <name> - DO: ...", its info card (the i button)
    holds the whole sign. Vanilla fields only, so any plain load shows them. The overlay labels above are the extra
    that draws every sign at once whenever the companion is awake.
  * LiveBridge -- a plain socket to the bridge (python.exe on the Windows side; WSL cannot reach it).

Selftest: selftest_reviewmap.py (fake bridge, 0 game).
"""
import json
import os
import time

_PROFILE = os.environ.get("USERPROFILE") or ("/mnt/c/Users/Mandrake" if os.path.isdir("/mnt/c/Users/Mandrake") else "")
SAVES = os.path.join(_PROFILE, "AppData", "LocalLow", "Ludeon Studios", "RimWorld by Ludeon Studios", "Saves")
SIGNS = os.path.join(os.path.dirname(SAVES), "JawaBenchReviewSigns")   # the companion's sidecar folder
SIGN_BREAK = "\\n"          # the two characters backslash + n: one line break in a drawn sub
SIGN_WIDTH = 60


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


def save_keeper(B, name, saves=None, wait_s=30.0, poll_s=1.0, stat=saves_stat, sleep=time.sleep, signs=None):
    """Save the live game as <name>.rws and prove it: -> dict(ok, name, new, changed, gone, tool, signs). Refuses (ok
    False, refused=...) when <name>.rws already exists; never overwrites. `signs` = the label ops pinned on the map:
    on an ok save they are written to the save's sign sidecar (write_signs)."""
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
    if signs and out["ok"]:
        out["signs"] = write_signs(name, signs, folder=os.path.join(os.path.dirname(saves), "JawaBenchReviewSigns")
                                   if saves else None)
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


def _wrap(text, width):
    out, cur = [], ""
    for w in str(text).split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])


def sign_sub(first="", look="", do="", decide="", width=SIGN_WIDTH, max_lines=6):
    """-> one label sub: `first` (the station's clause, the only line drawn zoomed out), then LOOK / DO / DECIDE, each
    wrapped to `width`, at most `max_lines` lines in all (the last one ends '...' when cut)."""
    lines = _wrap(first, width) if first else []
    for head, body in (("LOOK", look), ("DO", do), ("DECIDE", decide)):
        if body:
            lines += _wrap("%s: %s" % (head, body), width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:width - 3].rstrip() + "..."
    return SIGN_BREAK.join(l.replace("|", "/") for l in lines)


def weak_spot_sign(first, look, do, weak, width=SIGN_WIDTH, max_lines=6):
    """A sign from a station card that names its SUSPECTED WEAK SPOT (the GSS and FlowWorks cards): LOOK = what is
    staged (may be empty when another label already says it), DO = the first poke, DECIDE = whether that weak spot
    shows, in the card's own words."""
    return sign_sub(first, look, do, weak_decide(weak), width, max_lines)


def weak_decide(weak):
    """A card's suspected weak spot as the sign's DECIDE question ('weak spot:' prefix dropped)."""
    w = str(weak or "").strip()
    if w.lower().startswith("weak spot:"):
        w = w[len("weak spot:"):].strip()
    return ("is this fault there? " + w) if w else "does it work and look right?"


def signs_path(save, folder=None):
    return os.path.join(folder or SIGNS, "%s.txt" % save)


def write_signs(save, ops, folder=None, map_id=None):
    """Write a save's sign sidecar from label ops ('x|z|text|sub|col|size|tag' lines, as jawa/review_label add takes).
    map_id None = the header names no map and the companion puts them on the current map. -> the path written."""
    path = signs_path(save, folder)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [ln.strip("\r ") for ln in (ops if isinstance(ops, str) else "\n".join(ops)).split("\n")]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# map %s\n" % ("?" if map_id is None else map_id))
        f.write("\n".join(ln for ln in lines if ln) + "\n")
    return path


SIGN_PREFIX = "SIGN "        # jawa/review_sign clears and lists Books whose title starts with this


def sign_book(x, z, key, name, clause="", look="", do="", decide="", more=""):
    """-> one jawa/review_sign place op 'x|z|title|body'. Title: 'SIGN <key> <name> - DO: <do>' (one line: what the
    owner sees on mouse-over); body: name, clause, LOOK / DO / DECIDE, then `more`, joined by the \\n escape."""
    clean = lambda t: " ".join(str(t).replace("|", "/").split())  # noqa: E731
    title = "%s%s %s" % (SIGN_PREFIX, key, clean(name)) + (" - DO: %s" % clean(do) if do else "")
    body = ["%s  %s" % (key, clean(name))] + ([clean(clause)] if clause else []) + [""]
    body += ["%s: %s" % (h, clean(t)) for h, t in (("LOOK", look), ("DO", do), ("DECIDE", decide)) if t]
    if more:
        body += ["", clean(more)]
    return "%d|%d|%s|%s" % (x, z, title, SIGN_BREAK.join(body))


def place_signs(B, ops):
    """Replace this map's sign books: clear every 'SIGN ' book, place `ops` (a list or newline string). -> the place
    result (success, placed[], refused[], count)."""
    B.call("jawa/review_sign", action="clear", prefix=SIGN_PREFIX)
    text = ops if isinstance(ops, str) else "\n".join(ops)
    return B.call("jawa/review_sign", action="place", ops=text)


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
