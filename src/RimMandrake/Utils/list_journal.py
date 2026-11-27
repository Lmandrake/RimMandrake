#!/usr/bin/env python3
"""list_journal.py - which list a game's next load reads, and whether modset_builder wrote it last.

RIMMANDRAKE_TRACE_ARCHSMALL_TIER_SWAP_UNDONE_BEFORE_LAUNCH (page: design/specs/2026-11-27-list-drift-at-launch/boundary.md).
On 2026-11-26 `modset_builder.py --tier flowworks_list --apply` wrote ArchSmall's list at 03:47 PST, and by the 04:08
launch an older list was back (md5 a1069dfb, mtime 00:30:14: a copy that kept its source's mtime). The writer is still
unknown, and the run recorded a tier that the game did not load. This module makes the next case visible where it
matters:

  record(config, game, act, ...)   modset_builder calls it after each verified write of the live list: one journal row.
  launch_line(config, game)        game_instance.launch calls it just before the start: one line that names the list the
                                   load reads (md5, count, mtime) and says `= tier T, written by OWNER at HH:MM` when it is
                                   modset_builder's last write, or `LIST CHANGED since ...` with the copy that holds the
                                   same bytes and mtime when one is known. It journals a `launch` row either way.

Nothing here refuses or writes a list: the line informs and the load goes on. Neither call ever raises; a journal that
could not be read or written says so in the line ("could not look"), never as a match or a change.

The journal: <agent storage>/modset_swaps/list_writes.<game letter>.jsonl (RM_LIST_JOURNAL_DIR overrides the folder).

    python3 src/RimMandrake/Utils/list_journal.py show [ArchSmall]     the last rows of a game's journal
"""
import glob
import hashlib
import json
import os
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

DIR_ENV = "RM_LIST_JOURNAL_DIR"
TAIL_BYTES = 1 << 20        # the last rows are all a reader needs; a journal grows by one short row per write or launch
COPY_GLOB = ("**/ModsConfig*.xml",)


class CouldNotLook(Exception):
    """The journal, or the list, could not be read: a third answer, never 'no write on record' or 'changed'."""


def journal_dir():
    d = os.environ.get(DIR_ENV, "").strip()
    if d:
        return d
    import rmpaths      # agent storage; fails by name when unset (RmDataRootUnset), never a fallback into a clone
    return rmpaths.rm_str("modset_swaps")


def journal_path(game):
    return os.path.join(journal_dir(), "list_writes.%s.jsonl" % (game or "a"))


def read_list(config):
    """-> {md5, n, mtime, size} of the list at `config`; raises CouldNotLook when it cannot be read or parsed."""
    try:
        with open(config, "rb") as f:
            data = f.read()
        st = os.stat(config)
        act = ET.fromstring(data).find("activeMods")
        n = 0 if act is None else len(list(act))
    except (OSError, ET.ParseError) as e:
        raise CouldNotLook("%s: %s" % (config, e))
    return {"md5": hashlib.md5(data).hexdigest(), "n": n, "mtime": st.st_mtime, "size": len(data)}


def _norm(p):
    return os.path.normcase(os.path.abspath(p))


def _test_list(config):
    """A list under the system temp folder, with no RM_LIST_JOURNAL_DIR set, is a selftest's: it is never journaled, so
    no test writes the real journal (selftest_game_instance and selftest_modset_reset_repair reach these calls)."""
    if os.environ.get(DIR_ENV, "").strip():
        return False
    top = _norm(tempfile.gettempdir())
    return _norm(config).startswith(top + os.sep)


def _append(game, row):
    path = journal_path(game)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def record(config, game, act, tier=None, by=None):
    """Journal one verified write of `config` by modset_builder (act: apply, restore, restore-own, repair-reset,
    restore-full) -> None, or the reason it could not be journaled (the write itself already happened)."""
    if _test_list(config):
        return None
    try:
        cur = read_list(config)
        _append(game, {"at": time.time(), "act": act, "tier": tier, "by": by, "config": _norm(config), "pid": os.getpid(),
                       "argv": " ".join(sys.argv), **cur})
        return None
    except Exception as e:      # noqa: BLE001 - a journal is never a reason to fail the write it describes
        return "list journal not written: %s: %s" % (type(e).__name__, e)


def rows(game):
    """-> the journal's rows, oldest first ([] when no journal exists: nothing was ever recorded); CouldNotLook when it
    exists and cannot be read. A torn last line is skipped; any other unreadable line is skipped too."""
    path = journal_path(game)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - TAIL_BYTES))
            text = f.read().decode("utf-8", "replace")
    except OSError as e:
        raise CouldNotLook("journal %s: %s" % (path, e))
    out = []
    for line in text.splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if isinstance(r, dict):
            out.append(r)
    return out


def last_write(config, game):
    """-> the newest non-launch row for this exact list file, or None; CouldNotLook when the journal cannot be read."""
    want = _norm(config)
    for r in reversed(rows(game)):
        if r.get("act") != "launch" and r.get("config") == want:
            return r
    return None


def _when(ts, with_day=False):
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S %Z" if with_day else "%H:%M %Z", time.localtime(float(ts)))
    except (TypeError, ValueError):
        return "unknown time"


def same_copies(cur, roots, config):
    """-> paths under `roots` (ModsConfig*.xml files) holding the same bytes as `cur` AND the same mtime (to the
    second): the copies a mtime-keeping copy could have come from. The live list itself is left out."""
    hits, live = [], _norm(config)
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for pat in COPY_GLOB:
            for p in glob.glob(os.path.join(root, pat), recursive=True):
                try:
                    if _norm(p) == live or int(os.stat(p).st_mtime) != int(cur["mtime"]):
                        continue
                    with open(p, "rb") as f:
                        if hashlib.md5(f.read()).hexdigest() == cur["md5"]:
                            hits.append(p)
                except OSError:
                    continue
    return sorted(hits)


def launch_line(config, game, label=None, roots=None):
    """-> one line naming the list that the coming load reads, against modset_builder's last write of it. Journals a
    `launch` row. Never raises."""
    label = label or "game %s" % game
    try:
        cur = read_list(config)
    except CouldNotLook as e:
        return "list: COULD NOT LOOK at the list %s will load (%s)" % (label, e)
    what = "md5 %s (%d mods, mtime %s)" % (cur["md5"][:8], cur["n"], _when(cur["mtime"], True))
    try:
        last = last_write(config, game)
    except Exception as e:     # noqa: BLE001 - CouldNotLook, and an unset agent storage (RmDataRootUnset), read here
        return "list %s; COULD NOT LOOK at modset_builder's journal (%s: %s)" % (what, type(e).__name__, e)
    drift = None
    if last is None:
        line = "list %s; no modset_builder write of it on record for %s" % (what, label)
    elif last.get("md5") == cur["md5"]:
        line = "list %s = %s%s, written by %s at %s" % (
            what, "tier %s" % last["tier"] if last.get("tier") else "the %s" % last.get("act"),
            "" if last.get("tier") else " of modset_builder", last.get("by") or "modset_builder", _when(last.get("at")))
        drift = False
    else:
        drift = True
        try:
            copies = same_copies(cur, roots if roots is not None else [journal_dir()], config)
        except Exception:      # noqa: BLE001 - the search is a clue; its failure is said, never a crash
            copies = None
        line = ("LIST CHANGED since modset_builder's last write (%s, md5 %s, by %s at %s): %s loads %s, not written by "
                "modset_builder; %s" % (
                    "tier %s" % last["tier"] if last.get("tier") else last.get("act"), str(last.get("md5"))[:8],
                    last.get("by") or "modset_builder", _when(last.get("at")), label, what,
                    "same bytes and mtime as %s" % ", ".join(copies) if copies else
                    "no copy with the same bytes and mtime found" if copies is not None else "the copy search failed"))
    if _test_list(config):
        return line
    try:
        _append(game, {"at": time.time(), "act": "launch", "config": _norm(config), "drift": drift,
                       "last_at": last.get("at") if last else None, "pid": os.getpid(), **cur})
    except Exception as e:      # noqa: BLE001
        line += " (launch not journaled: %s)" % e
    return line


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != "show":
        print(__doc__.strip().splitlines()[0])
        print("usage: list_journal.py show [game]")
        return 2
    game = "a"
    if len(argv) > 1:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rimflow"))
        import game_names
        try:
            game = game_names.letter(argv[1])
        except Exception as e:      # noqa: BLE001 - an unknown name is refused by name
            print("REFUSED: %s" % e)
            return 3
    try:
        rs = rows(game)
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    if not rs:
        print("no rows in %s" % journal_path(game))
        return 0
    for r in rs[-20:]:
        print("%s  %-12s %-24s %-14s md5 %s  %s mods%s" % (
            _when(r.get("at"), True), r.get("act"), r.get("tier") or "-", r.get("by") or "-", str(r.get("md5"))[:8],
            r.get("n"), "  DRIFT" if r.get("drift") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
