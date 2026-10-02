"""modcheck.surprise -- the evidence protocol that runs the moment a detector says SURPRISE/FATAL.

Plan section 6 as revised by section 10.3/10.9 (GPT review): EVIDENCE BEFORE ACTION.
  1. verified pause (never steps a tick just to refresh the frame: stepping can spread fire, apply
     damage or kill a pawn, i.e. mutate the evidence),
  2. the sidecar JSON is written ATOMICALLY first (the structured state is the authoritative
     evidence; the image is supplementary and its failure never aborts the capture),
  3. clear debug windows, frame the cause, take ONE screenshot with a unique file name,
  4. verify the file is a real, stable PNG; compare its hash with the previous shot of this run,
  5. rewrite the sidecar with the image facts.

A bland map (helpers.prepare_bland_map) is what makes the picture useful: after it the frame holds
only the colonists, the subject and the intruder, so the cause jumps out.

Nothing here decides anything. It records.
"""
import hashlib
import json
import os
import re
import struct
import sys
import time

import clockgate

PNG_SIG = b"\x89PNG\r\n\x1a\n"
MIN_PNG_BYTES = 20 * 1024          # a real 1080p frame of this game is megabytes; flat frames still > 20 KB


def to_local_path(path):
    """The bridge returns Windows paths (`C:\\Users\\...`); under WSL python3 translate them."""
    if not path:
        return path
    if sys.platform == "win32":
        return path
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", path)
    if m:
        return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return path


def png_info(path):
    """Structure check, not a size threshold (GPT review: a fixed 0.5 MB bar rejects valid frames).
    Returns {"ok", "bytes", "width", "height", "md5", "why"}."""
    p = to_local_path(path)
    out = {"ok": False, "bytes": None, "width": None, "height": None, "md5": None, "why": ""}
    try:
        size = os.path.getsize(p)
        out["bytes"] = size
        with open(p, "rb") as f:
            data = f.read()
    except OSError as e:
        out["why"] = "unreadable: %s" % e
        return out
    if data[:8] != PNG_SIG:
        out["why"] = "not a PNG (bad signature)"
        return out
    try:
        w, h = struct.unpack(">II", data[16:24])
    except struct.error:
        out["why"] = "truncated IHDR"
        return out
    out["width"], out["height"] = w, h
    out["md5"] = hashlib.md5(data).hexdigest()
    if w < 200 or h < 200:
        out["why"] = "implausible dimensions %dx%d" % (w, h)
    elif size < MIN_PNG_BYTES:
        out["why"] = "only %d bytes" % size
    elif not data.rstrip(b"\x00").endswith(b"IEND\xaeB`\x82"):
        out["why"] = "no IEND chunk (file still being written or truncated)"
    else:
        out["ok"] = True
    return out


def wait_stable(path, polls=6, gap_s=0.1, sleep=time.sleep):
    """Wait for the size to stop changing (the bridge returns before the write may finish)."""
    p = to_local_path(path)
    last = -1
    for _ in range(polls):
        try:
            size = os.path.getsize(p)
        except OSError:
            size = -2
        if size == last and size > 0:
            return True
        last = size
        sleep(gap_s)
    return False


def unique_name(mod, chain, detector, tick, seq):
    safe = lambda s: re.sub(r"[^A-Za-z0-9_.-]+", "-", str(s))[:40]
    return "%s__%s__%s__t%s__%03d" % (safe(mod), safe(chain), safe(detector), tick, seq)


def _atomic_write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(tmp, path)


def _compact_snapshot(snap, hits):
    """Only what a human (or a later judge) needs: the tick, the involved pawns, the letters."""
    ids = set()
    for h in hits:
        ev = h.evidence or {}
        for k in ("id",):
            if ev.get(k):
                ids.add(ev[k])
        for p in ev.get("pawns", []) or []:
            ids.add(p.get("id"))
        for p in ev.get("animals", []) or []:
            ids.add(p.get("id"))
        for i in ev.get("ids", []) or []:
            ids.add(i)
    return {"tick": snap.get("tick"), "epoch": snap.get("epoch"), "map_id": snap.get("map_id"),
            "pawns": [p for p in snap.get("pawns", []) if p.get("id") in ids],
            "letters": snap.get("letters", [])[-25:], "story": snap.get("story"),
            "fires": len([t for t in snap.get("things", []) if t.get("def") == "Fire"]),
            "conditions": snap.get("conditions")}


def capture(session, hits, snap, outdir, name, anchor, gate=None, prev_md5=None, screenshot=True,
            context=None):
    """Capture evidence for `hits` (all hits of one sweep: the FIRST helper would otherwise erase the
    evidence of the rest). Returns {"sidecar", "png", "png_info", "notes", "md5"}. Never raises on an
    image problem; a failure to write the sidecar IS raised (mandatory evidence)."""
    os.makedirs(outdir, exist_ok=True)
    notes = []
    sidecar = os.path.join(outdir, name + ".json")
    clockgate.ensure_paused(session)                           # 1. verified pause, no refresh tick
    drain = []
    try:
        d = session.call("jawa/drain_log", limit=20)
        drain = [(m.get("type"), (m.get("text") or "")[:300]) for m in d.get("messages", [])]
    except Exception as e:                                      # noqa: BLE001
        notes.append("drain_log failed: %r" % (e,))
    windows = []
    try:
        w = session.call("jawa/window_list_close", action="list")
        windows = w.get("windows", [])
    except Exception as e:                                      # noqa: BLE001
        notes.append("window list failed: %r" % (e,))
    record = {"name": name, "when_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "hits": [{"detector": h.detector, "severity": h.severity, "summary": h.summary,
                        "evidence": h.evidence, "suggest": list(h.suggest), "focus": h.focus,
                        "fingerprint": h.fingerprint} for h in hits],
              "snapshot": _compact_snapshot(snap, hits), "log_tail": drain, "windows": windows,
              "ledger": gate.as_dict() if gate is not None else None, "context": context or {},
              "png": None, "png_info": None, "notes": notes}
    _atomic_write_json(sidecar, record)                         # 2. mandatory evidence, before any image
    out = {"sidecar": sidecar, "png": None, "png_info": None, "notes": notes, "md5": None}
    if not screenshot:
        return out
    try:                                                        # 3. clear + frame + one shot
        session.call("jawa/clear_ui", devWindows=True, clearSelection=True)
        focus = next((h.focus for h in hits if h.focus), None) or anchor
        if focus:
            session.call("rimworld/jump_camera_to_cell", x=int(focus[0]), z=int(focus[1]))
        r = session.call("rimworld/take_screenshot", fileName=name, suppressMessage=True)
        path = (r or {}).get("path")
        if not path:
            notes.append("take_screenshot returned no path: %s" % str(r)[:200])
        else:
            wait_stable(path)
            info = png_info(path)
            out["png"], out["png_info"], out["md5"] = path, info, info.get("md5")
            if info["ok"]:                      # keep the picture NEXT TO its sidecar (the game's own
                try:                            # Screenshots folder is the wrong place to look for evidence)
                    import shutil
                    dest = os.path.join(outdir, name + ".png")
                    shutil.copy2(to_local_path(path), dest)
                    out["png"] = dest
                    out["png_original"] = path
                except OSError as e:
                    notes.append("could not copy the screenshot beside the sidecar: %s" % e)
            if not info["ok"]:
                notes.append("png not verified: %s" % info["why"])
            if prev_md5 and info.get("md5") == prev_md5:
                notes.append("identical to the previous surprise frame: may be stale or unchanged "
                             "(a paused shot can be the previous frame); trust the sidecar")
    except Exception as e:                                      # noqa: BLE001 - image is supplementary
        notes.append("screenshot failed: %r" % (e,))
    record["png"], record["png_info"], record["notes"] = out["png"], out["png_info"], notes
    _atomic_write_json(sidecar, record)                         # 5. final sidecar
    return out
