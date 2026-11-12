#!/usr/bin/env python3
"""relentless_integrity.py - the gate a tick passes before it staffs anything after an unclean stop.
RELENTLESS_BOOT_HARDEN_TRUSTED_ZEROS. After the 2026-11-01 disk outage relentless restarted and acted on damaged state:
workers leased onto clones holding 369 NUL-filled tracked files, a proof_weak taken from a checker whose output was a
0-byte file, a clone removed with no bundle. `git status` is blind to a file zeroed in place (size and stat kept), so
the scan reads content: a tracked file whose tail is all NUL, or that is empty, is hashed and compared with the index.

When: no record of a clean tick end (first boot), a gap since the last clean tick end over `gap_s`, or the kernel's
OOM-kill count moved since (a step-down killed something mid-write). Otherwise the gate costs one small file read.
On damage: a damaged clone is quarantined (damaged files put back from the index, the WIP bundled onto the item, the
clone removed so its next lease rebuilds it), an empty or NUL verdict is MISSING and its check re-queued, the Conductor
log is told, and anything not repaired here blocks the tick: nothing is staffed on damaged state.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import time

EMPTY_BLOB = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
TAIL = 512
DEFAULTS = {"gap_s": 900}


def cfg(r):
    return dict(DEFAULTS, **((r or {}).get("integrity") or {}))


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- content readings

def nul_or_empty(path):
    """-> "empty", "nul" (the whole tail NUL), or None. A file that cannot be read is "unreadable"."""
    try:
        size = os.lstat(path).st_size
        if size == 0:
            return "empty"
        with open(path, "rb") as f:
            f.seek(max(0, size - TAIL))
            tail = f.read(TAIL)
    except OSError:
        return "unreadable"
    return "nul" if tail and not tail.strip(b"\0") else None


def json_damage(path):
    """-> None for a whole JSON file; else why it is no reading at all (empty, NUL, unparseable)."""
    bad = nul_or_empty(path)
    if bad:
        return bad
    try:
        with open(path, "rb") as f:
            data = f.read()
        if b"\0" in data:
            return "nul bytes"
        json.loads(data.decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        return "unparseable: %s" % str(e)[:80]
    return None


def jsonl_damage(path):
    """-> None, or a count of NUL bytes and torn lines. History, not state: it alarms and never blocks."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    nul = data.count(b"\0")
    torn = 0
    for ln in data.split(b"\n"):
        ln = ln.strip(b"\0").strip()
        if ln:
            try:
                json.loads(ln.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                torn += 1
    return "%d NUL bytes, %d torn lines" % (nul, torn) if nul or torn else None


def clone_damage(c, timeout=600):
    """-> [(path, why)] tracked files whose content is not the index's while git status would say nothing: a NUL tail
    or an empty file where the index holds a non-empty blob. Hash-confirmed, so a file legitimately ending in NUL that
    matches its blob is no damage. Raises when git cannot list the clone (the caller treats that as damage)."""
    r = subprocess.run(["git", "ls-files", "-s", "-z"], cwd=c, capture_output=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("git ls-files: %s" % r.stderr.decode("utf-8", "replace"))
    suspect = []
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        head, path = rec.split(b"\t", 1)
        mode, sha, _stage = head.decode().split()
        if mode not in ("100644", "100755"):
            continue
        p = path.decode("utf-8", "surrogateescape")
        bad = nul_or_empty(os.path.join(c, p))
        if bad == "empty" and sha == EMPTY_BLOB:
            continue
        if bad:
            suspect.append((p, sha, bad))
    if not suspect:
        return []
    h = subprocess.run(["git", "hash-object", "--no-filters", "--stdin-paths"], cwd=c, capture_output=True, timeout=timeout,
                       input="\n".join(p for p, _, _ in suspect).encode("utf-8", "surrogateescape"))
    got = h.stdout.decode().split() if h.returncode == 0 else []
    if len(got) != len(suspect):      # an unreadable file fails the batch: every suspect stands
        return [(p, bad) for p, _, bad in suspect]
    return [(p, bad) for (p, sha, bad), now in zip(suspect, got) if now != sha]


def objstore_damage(git_dir):
    """-> [why] for a shared object store: an empty or NUL-tailed pack or index, an empty loose object."""
    out = []
    for p in glob.glob(os.path.join(git_dir, "objects", "pack", "*.pack")) + glob.glob(os.path.join(git_dir, "objects", "pack", "*.idx")):
        bad = nul_or_empty(p)
        if bad:
            out.append("%s: %s" % (p, bad))
    for p in glob.glob(os.path.join(git_dir, "objects", "??", "*")):
        try:
            if os.lstat(p).st_size == 0:
                out.append("%s: empty loose object" % p)
        except OSError:
            pass
    return out


# ---------------------------------------------------------------- when

def _oom(fx):
    """The kernel OOM-kill count, None when it cannot be read: a dead reading never stops the gate."""
    try:
        return fx.oom_kills()
    except Exception:  # noqa: BLE001
        return None


def record_path(store):
    return store.p("integrity.json")


def read_record(store):
    try:
        with open(record_path(store), encoding="utf-8") as f:
            rec = json.load(f)
        return rec if isinstance(rec, dict) else None
    except (OSError, ValueError):
        return None


def due(store, fx, r, now):
    """-> why the gate must run now, or None."""
    rec = read_record(store)
    if rec is None:
        return "no clean tick on record (first boot, or the record itself is damaged)"
    if rec.get("blocked"):
        return "the last gate found damage it could not repair"
    end = rec.get("clean_end")
    if not isinstance(end, (int, float)):
        return "no clean tick end on record"
    if now - end > cfg(r)["gap_s"]:
        return "%d s since the last clean tick ended" % (now - end)
    oom = _oom(fx)
    if oom is not None and rec.get("oom") is not None and oom > rec["oom"]:
        return "the kernel OOM-killed %d since the last clean tick" % (oom - rec["oom"])
    return None


def mark_clean(store, fx, now):
    """The tick ended whole: the next one need not look unless a gap or an OOM kill comes between."""
    rec = read_record(store) or {}
    if rec.get("blocked"):
        return
    rec.update({"clean_end": now, "oom": _oom(fx)})
    store._write(record_path(store), json.dumps(rec, sort_keys=True))


# ---------------------------------------------------------------- the scan and its repairs

def states(store):
    """Every record that reads; a damaged one is the scan's to report, never a crash here."""
    out = []
    for i in store.items():
        try:
            st = store.load(i)
        except (OSError, ValueError):
            continue
        if st:
            out.append(st)
    return out


def owner_of(store, c):
    """-> (state, "work"|"check"|None) for the record that names clone c."""
    for st in states(store):
        if st.get("clone") == c:
            return st, "work"
        if (st.get("check") or {}).get("clone") == c:
            return st, "check"
    return None, None


def quarantine(store, fx, c, bad, now):
    """Put the damaged files back from the index, bundle what is left onto the item, remove the clone. -> None when it
    went, else why it stays (it then blocks)."""
    if fx.clone_busy(c):
        return "a process is still in it"
    st, kind = owner_of(store, c)
    item = (st or {}).get("item") or os.path.basename(c)
    paths = [p for p, _ in bad]
    r = subprocess.run(["git", "checkout-index", "-f", "-z", "--stdin"], cwd=c, capture_output=True, timeout=600,
                       input="\0".join(paths).encode("utf-8", "surrogateescape"))
    if r.returncode:
        return "restore from the index: %s" % r.stderr.decode("utf-8", "replace")
    if clone_damage(c):
        return "still damaged after the restore from the index"
    try:
        bundle = fx.bundle_clone(item, c)
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
        return "bundle: %s" % str(e)
    with store.lock():
        cur = store.load(item) if st else None
        if cur and kind == "work" and bundle:
            cur["bundle"] = bundle
            store.save(cur)
    if st:
        store.learn(item, "\n%s relentless: your clone was found damaged after an unclean stop (%d tracked files NUL or "
                    "empty in place: %s). Those files were put back from the index, so an unstaged edit to them is lost; "
                    "the rest of the WIP is in %s and comes back on the next clone.\n"
                    % (iso(now), len(paths), ", ".join(paths[:5]), bundle))
    try:
        shutil.rmtree(c)
    except FileNotFoundError:
        pass
    except OSError as e:
        return "remove: %s" % str(e)
    store.journal({"at": iso(now), "do": "clone_quarantined", "clone": os.path.basename(c), "item": item,
                   "damaged": len(paths), "bundle": bundle})
    return None


def run_out_missing(run):
    """A run's output file that is empty or NUL is no output: -> the reason, or None."""
    out = (run or {}).get("out")
    if not out:
        return None
    if not os.path.exists(out):
        return None     # never written is no evidence of damage; the shell makes the file when the unit starts
    return json_damage(out)


def verdicts(store, fx, now, found):
    """A verdict whose run left an empty or NUL output after an unclean stop is MISSING, never a verdict: the check is
    re-queued (the candidate checked again), and that is no lost checker."""
    for st in states(store):
        chk = st.get("check") or {}
        if st.get("status") != "checking" or chk.get("verdict") is None:
            continue
        why = run_out_missing(chk.get("run"))
        if not why or fx.alive(chk.get("run")):
            continue
        with store.lock():
            cur = store.load(st["item"])
            if cur.get("status") != "checking" or (cur.get("check") or {}).get("nonce") != chk.get("nonce"):
                continue
            cur["status"] = "candidate"
            cur["check"] = None
            store.save(cur)
        store.journal({"at": iso(now), "do": "verdict_missing", "item": st["item"], "word": chk.get("verdict"),
                       "why": "checker output %s: %s" % (why, chk["run"].get("out"))})
        found.append({"what": "verdict", "item": st["item"], "why": why, "repaired": "re-queued the check"})


def scan(store, fx, r, now, objstore=None):
    """-> {"found": [...], "blocking": [...]}. Repairs what it can; whatever is left in blocking stops the tick."""
    found, blocking = [], []
    for p in glob.glob(store.p("items", "*", "state.json")):
        why = json_damage(p)
        if why:
            blocking.append({"what": "state", "path": p, "why": why})
    for p in glob.glob(store.p("*.json")):
        if os.path.basename(p) == "integrity.json":
            continue
        why = json_damage(p)
        if why:
            found.append({"what": "store file", "path": p, "why": why})
    for p in glob.glob(store.p("items", "*", "receipts", "*.json")):
        why = json_damage(p)
        if why:      # read_receipt already takes it as no receipt: worker_lost, never a finish
            found.append({"what": "receipt", "path": p, "why": why, "repaired": "read as no receipt"})
    for p in glob.glob(store.p("*.jsonl")):
        why = jsonl_damage(p)
        if why:
            found.append({"what": "history", "path": p, "why": why})
    for p in glob.glob(store.p("**", "*.tmp.*"), recursive=True):
        try:
            if now - os.lstat(p).st_mtime > cfg(r)["gap_s"]:
                os.remove(p)
                found.append({"what": "orphan tmp", "path": p, "why": "a write that never landed", "repaired": "removed"})
        except OSError:
            pass
    if not blocking:
        verdicts(store, fx, now, found)
    if objstore and os.path.isdir(objstore):
        for why in objstore_damage(objstore):
            blocking.append({"what": "object store", "path": objstore, "why": why})
    for c in fx.pool_clones():
        if not os.path.isdir(os.path.join(c, ".git")):
            continue
        try:
            bad = clone_damage(c)
        except (RuntimeError, OSError, subprocess.SubprocessError) as e:
            blocking.append({"what": "clone", "path": c, "why": "unreadable: %s" % str(e)})
            continue
        if not bad:
            continue
        stays = quarantine(store, fx, c, bad, now)
        row = {"what": "clone", "path": c, "why": "%d tracked files NUL or empty in place: %s"
               % (len(bad), ", ".join(p for p, _ in bad[:5]))}
        if stays:
            blocking.append(dict(row, stays=stays))
        else:
            found.append(dict(row, repaired="quarantined: bundled and removed, rebuilt on the next lease"))
    return {"found": found, "blocking": blocking}


def gate(store, fx, r, now, acts, objstore=None):
    """-> True when the tick may go on. Runs the scan only when due(); a blocked gate rescans each tick until clean."""
    why = due(store, fx, r, now)
    if not why:
        return True
    res = scan(store, fx, r, now, objstore)
    rec = read_record(store) or {}
    said = rec.get("blocking_said")
    sig = sorted("%s|%s" % (x["what"], x.get("path") or x.get("item")) for x in res["blocking"])
    rec.update({"verified_at": now, "why": why, "found": res["found"][:50], "blocking": res["blocking"][:50],
                "blocked": bool(res["blocking"])})
    if not res["blocking"]:
        rec.update({"clean_end": now, "oom": _oom(fx), "blocking_said": None})
    store._write(record_path(store), json.dumps(rec, sort_keys=True))
    acts.append({"do": "integrity", "why": why, "found": len(res["found"]), "blocking": len(res["blocking"])})
    if res["found"] or res["blocking"]:
        text = "integrity gate (%s): %d found, %d blocking. %s" % (
            why, len(res["found"]), len(res["blocking"]),
            "; ".join("%s %s: %s" % (x["what"], os.path.basename(x.get("path") or x.get("item") or ""), x["why"])
                      for x in (res["blocking"] + res["found"])[:6]))
        store.journal({"at": iso(now), "do": "alarm", "kind": "integrity_damage", "why": text})
        if res["blocking"] and sig != said:      # once per distinct damage, not once per two-minute tick
            rec["blocking_said"] = sig
            store._write(record_path(store), json.dumps(rec, sort_keys=True))
            fx.conductor_alarm(text + " - relentless staffs nothing until this is repaired; record: " + record_path(store))
    return not res["blocking"]
