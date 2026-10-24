#!/usr/bin/env python3
"""ikee_swap.py -- runbook step 6 (Transient/phase0_L1_runbook.md): replace the save's ikee `AA_Eyeling` "Marquee"
with our `RM_Ikee`, re-bond it with Yeku, save under the donor-free name. Owner ruling 2026-10-15, by card: the
ikee is replaced at the live round, not hand-edited offline.

    python3 src/RimMandrake/Utils/ikee_swap.py                       # DRY RUN (default): prints every call, runs none
    python.exe src/RimMandrake/Utils/ikee_swap.py --live --yes-i-know-this-is-live [--save-as NAME]

Preconditions for --live (not checked by asking anyone): the candidate save is LOADED on the donor-free list, this
seat holds the bridge (`rimflow bridge who`), python.exe (WSL cannot reach the bridge). Every call goes through
rimbridge_client.RimBridge in-process with an argv-free JSON payload, so no shell word-splitting can mangle it
(the zsh trap the printed lines also avoid: each is one complete command, JSON in single quotes).

WHAT THE OFFLINE CHECK CHANGED (save_adoption_check.py, 2026-10-18): the runbook expected Scribe to DROP both
AA_Eyeling pawns on the donor-free list. It does not: Alpha Memes (`sarg.alphamemes`, kept) ships its own
`AA_Eyeling` (ThingDef + PawnKindDef, body AM_EyeBody), so Marquee loads as Alpha Memes' eyeling, still bonded.
Hence step 4 below: drop the bond, make it factionless, manhunter, and kill it through kill_hostiles (destroy_batch
never touches pawns; there is no plain despawn tool). If Marquee did NOT load, step 4 is skipped and the recorded
cell is used. The world-pawn eyeling (AA_Eyeling657692, no faction, no relations) is left alone (runbook 6.4).

Each step asserts `success` and the fact it exists to change; the first failed assertion STOPS the run (the save
is not written). The save is backed up byte-exact first, and the written file is stat'd afterwards because
`rimworld/save_game` has reported success while writing a different slot (skills/rimbridge/references/
silent-failures.md).
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SAVE = "CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18"
YEKU = "Human470530"
OLD = "AA_Eyeling669122"
OLD_DEF = "AA_Eyeling"
CELL = (175, 134)
NAME = "Marquee"
NEW_KIND = "RM_Ikee"
RETIRED = ("mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts",
           "sarg.alphabiomes")
BACKUPS = rm_win("scratch", "save_backups")
CLIENT = "python.exe src/RimMandrake/Utils/rimbridge_client.py --yes-i-know-this-is-live --timeout 120"


class Stop(Exception):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _pawn(reply):
    ps = (reply or {}).get("pawns") or []
    return ps[0] if ps else None


class Swap(object):
    def __init__(self, live, rb=None, save=SAVE, save_as=None, saves_dir=None, backups=BACKUPS, out=print):
        self.live, self.rb, self.out = live, rb, out
        self.save, self.save_as = save, save_as or save
        self.saves_dir, self.backups = saves_dir, backups
        self.log, self.n = [], 0
        self.new_id = "<NEW_ID>"

    # --------------------------------------------------------------- plumbing
    def call(self, tool, why, **params):
        self.n += 1
        line = "%s --call %s --json '%s'" % (CLIENT, tool, json.dumps(params, separators=(",", ":")))
        self.out("%2d. %s\n    %s" % (self.n, why, line))
        if not self.live:
            return None
        r = self.rb.call(tool, params)
        r = r.get("result", r) if isinstance(r, dict) and "result" in r and isinstance(r["result"], dict) else r
        self.log.append({"n": self.n, "tool": tool, "params": params, "reply": r})
        if not isinstance(r, dict) or r.get("success") is False:
            raise Stop("step %d %s failed: %s" % (self.n, tool, json.dumps(r, default=str)[:400]))
        return r

    def need(self, cond, what, got=None):
        if self.live and not cond:
            raise Stop("assertion failed: %s (got %s)" % (what, json.dumps(got, default=str)[:300]))
        if self.live:
            self.out("    ok: %s" % what)

    # --------------------------------------------------------------- the steps
    def run(self):
        path = os.path.join(self.saves_dir or "<Saves>", self.save + ".rws")
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        bak = os.path.join(self.backups, "%s.rws.bak-pre-ikee-swap-%s" % (self.save, stamp))
        self.out(" 0. (local) back up the save byte-exact, record sha256\n    copy %s -> %s" % (path, bak))
        before = None
        if self.live:
            os.makedirs(self.backups, exist_ok=True)
            shutil.copy2(path, bak)
            before = sha256(path)
            self.need(sha256(bak) == before, "backup sha256 matches the save (%s)" % before[:16])

        info = self.call("rimworld/get_game_info", "the game is Playing (a map is loaded)")
        self.need(info and "Play" in json.dumps(info), "game is Playing", info)
        hs = self.call("jawa/companion_handshake", "companion profile (spawn/kill tools must not be refused)")
        rm = self.call("jawa/running_mods", "no retired donor in the running list", details=False, assembly="")
        if self.live:
            ids = [str(x).lower() for x in (rm.get("packageIds") or rm.get("mods") or []) if isinstance(x, str)] or \
                  [str(m.get("packageId", "")).lower() for m in (rm.get("mods") or []) if isinstance(m, dict)]
            self.need(ids and not set(ids) & set(RETIRED), "running list read and donor-free (%d mods)" % len(ids),
                      sorted(set(ids) & set(RETIRED)))
        y = self.call("jawa/pawn_get", "Yeku is on the map", pawn=YEKU)
        self.need(_pawn(y) is not None, "Yeku found", y)
        old = None
        live, self.live = self.live, False          # print the probe like any step, but run it tolerant of "absent"
        self.call("jawa/pawn_get", "is the old ikee loaded? (expected YES: Alpha Memes ships AA_Eyeling)", pawn=OLD)
        self.live = live
        if self.live:
            try:
                r = self.rb.call("jawa/pawn_get", {"pawn": OLD})
                old = _pawn(r.get("result", r) if isinstance(r, dict) else r)
            except Exception:                                            # noqa: BLE001
                old = None
            self.log.append({"n": self.n, "tool": "jawa/pawn_get", "params": {"pawn": OLD}, "found": old is not None})
            self.out("    old ikee %s" % ("PRESENT (def %s)" % old.get("def") if old else "absent: Scribe dropped it"))
        cell = CELL
        if old is not None or not self.live:
            if old is not None and isinstance(old.get("position"), dict):
                cell = (old["position"].get("x", CELL[0]), old["position"].get("z", CELL[1]))
            self.out("    -- old ikee present: remove it without a bond-death thought (next 5 calls)")
            self.call("jawa/pawn_relations", "drop Yeku's Bond to the old ikee FIRST (no 'bonded animal died')",
                      pawn=YEKU, action="remove", relation="Bond", otherPawn=OLD)
            self.call("jawa/set_pawn_faction", "make the old ikee factionless (not a colony animal)",
                      pawn=OLD, faction="none")
            self.call("jawa/pawn_mental", "manhunter, so kill_hostiles can reach it", pawn=OLD, action="start",
                      state="ManhunterPermanent", forced=True)
            dry = self.call("jawa/kill_hostiles", "DRY RUN: exactly the old ikee would die", pawnDef=OLD_DEF,
                            dryRun=True)
            if self.live:
                ids = [p.get("id") for p in (dry.get("killedPawns") or [])]
                self.need(ids == [OLD], "the dry run names only %s" % OLD, dry)
            k = self.call("jawa/kill_hostiles", "kill it and destroy the corpse", pawnDef=OLD_DEF,
                          destroyCorpses=True)
            if self.live:
                self.need([p.get("id") for p in (k.get("killedPawns") or [])] == [OLD], "killed exactly %s" % OLD, k)
        sp = self.call("jawa/spawn_pawn", "spawn our RM_Ikee at the old cell, player faction (= tame)",
                       kindDef=NEW_KIND, x=cell[0], z=cell[1], faction="player", count=1)
        if self.live:
            got = (sp.get("pawns") or [{}])[0]
            self.new_id = got.get("id")
            self.need(self.new_id, "spawned one %s (%s)" % (NEW_KIND, self.new_id), sp)
        self.call("jawa/set_pawn_identity", "name it Marquee", pawn=self.new_id, single=NAME)
        b = self.call("jawa/animal_bond", "bond Yeku and the new ikee", pawn=YEKU, animal=self.new_id, chance=1.0)
        rel = self.call("jawa/pawn_relations", "VERIFY by state read: Yeku's Bond points at the new ikee",
                        pawn=YEKU, action="list")
        if self.live:
            self.need(self.new_id in json.dumps(rel) and "Bond" in json.dumps(rel), "Bond to %s listed" % self.new_id,
                      rel)
            self.need(OLD not in json.dumps(rel), "no relation to the old ikee remains", rel)
        np_ = self.call("jawa/pawn_get", "VERIFY: the new pawn is RM_Ikee, named Marquee, player", pawn=self.new_id)
        if self.live:
            j = json.dumps(_pawn(np_))
            self.need(NEW_KIND in j and NAME in j, "def %s and name %s read back" % (NEW_KIND, NAME), _pawn(np_))
        t0 = datetime.datetime.now().timestamp()
        self.call("rimworld/save_game", "save under the donor-free name", saveName=self.save_as)
        dest = os.path.join(self.saves_dir or "<Saves>", self.save_as + ".rws")
        self.out("after: stat %s: mtime after step 9, sha256 differs from the backup" % dest)
        if self.live:
            self.need(os.path.isfile(dest) and os.path.getmtime(dest) >= t0 - 2, "the named file was written", dest)
            self.need(sha256(dest) != before or self.save_as != self.save, "its content changed", dest)
        self.out("then, offline, WSL (no game): python3 src/RimMandrake/Utils/save_adoption_check.py --save '%s'\n"
                 "    expect: the ikee row gone, RM_Ikee present, control <def>Human</def> = 75; and\n"
                 "    MEASURE_ALLOW_SCAN=1 grep -c '<def>RM_Ikee</def>' -> >= 1 ; '<def>AA_Eyeling</def>' -> 1 "
                 "(the world pawn, left alone)" % dest.replace("<Saves>", "$SAVES"))
        return {"backup": bak, "newId": self.new_id, "calls": self.log}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--yes-i-know-this-is-live", action="store_true")
    ap.add_argument("--save", default=SAVE, help="the loaded save's name (no .rws)")
    ap.add_argument("--save-as", help="name to save under (default: the loaded save's name)")
    ap.add_argument("--out", help="JSON record of every call and reply (live)")
    a = ap.parse_args(argv)
    if a.live and not a.yes_i_know_this_is_live:
        print("REFUSING --live without --yes-i-know-this-is-live: this drives the running game")
        return 2
    rb, saves = None, None
    try:
        from game_paths import SAVES
        saves = SAVES
    except Exception:                                                    # noqa: BLE001
        pass
    if a.live:
        import rimbridge_client as R
        h, p, t = R.resolve_endpoint()
        rb = R.RimBridge(host=h, port=p, token=t, timeout=120.0)
        rb.connect()
    print("IKEE SWAP -- %s (save %s -> %s)\n" % ("LIVE" if a.live else "DRY RUN: nothing is called", a.save,
                                                 a.save_as or a.save))
    sw = Swap(a.live, rb, a.save, a.save_as, saves)
    try:
        rec = sw.run()
    except Stop as exc:
        print("\nSTOPPED: %s\nNothing after this step ran; the save was NOT written by this script." % exc)
        rec, code = {"stopped": str(exc), "calls": sw.log}, 1
    else:
        code = 0
        print("\n%s" % ("DONE: new ikee %s" % rec["newId"] if a.live else "DRY RUN complete: %d calls listed" % sw.n))
    if a.out:
        json.dump(rec, open(a.out, "w", encoding="utf-8"), indent=1, default=str)
    return code


if __name__ == "__main__":
    sys.exit(main())
