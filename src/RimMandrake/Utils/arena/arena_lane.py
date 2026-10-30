#!/usr/bin/env python3
r"""arena_lane.py — the live-lane wrapper (harness step 12, design §1.5).

Design: design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.5 (the live lanes), §1.2 step 8 (what the gate
reads from a lane), §1.7 (the event log); the reload rule M1 in testpilot_merged_2026-10-29.md §2.2 (each reload logs
the rule it met and the measured reload cost it used). Build ticket ARENA_LANE_BUILD_MINIMAL_LIST_ONLY.

There are two lanes, one game each: `steve` (SteveDesktop) and `archmagi` (the owner's machine). Whichever arm holds a
lane does every live act through a `Lane` so that each act is logged once, by harness code, in the §1.7 schema:

    live_take     rimflow bridge take --host <h> --idle-ok --for "arena <arm> ..."   (the delegated take)
    reload        stop, profile swap, deploy, launch, quicktest; detail carries the deploy and the MEASURED
                  launch-to-ready seconds; `rule` is the M1 rule the caller says it met (R0..R3)
    canary        pass | fail; a failed canary also writes `invalid` (never `fail`: the run is re-queued)
    live_release  modlist_swap --restore --apply, then every mod this hold deployed is redeployed from origin/main
                  (deploy_custom_mods --mod M --apply --prune, in the runner's own clone checked out at origin/main):
                  the candidate's mod FILES must not stay in the owner's game (ARENA_LANE_RESTORE_MAIN_MOD_FILES).
                  `minutes` = restore time (list + files), charged to the arm that swapped

ENFORCED HERE (each one a refusal, LaneRefused, before anything is touched):
  * profile `full` is refused in trial mode (owner 2026-10-29: no full-list profile in the trial). Only `minimal`
    (modlist_swap --minimal, modlist_swap.MINIMAL, 26 mods measured 2026-10-30) and `minimal+deps` (modset_builder --tier <tier>) exist.
  * never a flyer's flight (standing ruling; the lane's `bridge take --idle-ok` refuses flight wording too, but the lane refuses
    first).
  * never a canonical world save: loading a save whose name is the canon start save (canon_save.py) is refused, and
    the canary is red on such a map.
  * no C# deploy while the game runs (the DLL is locked).
  * his presence at the machine never gates, delays, yields or aborts a lane (owner 2026-10-30: "I really, really
    need you to strip "when I come back to the machine" as an event for anything changing. It's causing so many
    problems and I don't need it."). There is no owner probe and no owner-return abort; a lane config's old
    `owner_playing` key is ignored. His explicit OWNER bridge hold still refuses the take, at any
    age (the lane's take is the delegated `--idle-ok` one).

THE CANARY (§1.2 step 8): a live colonist and the vanilla spawn probe (modcheck/validity.canary, reused, not copied);
a Player.log written since this lane's own launch; the expected game version (lane config `game_version`, pinned once
with `pin-version`); the deployed sha equal to the candidate sha and every deployed mod active; a map that is not the
canonical save. Any check that cannot be read is a red canary (UNMEASURED is never a pass: instrument_traps).

    python3 src/RimMandrake/Utils/arena/arena_lane.py status   [--lane L]
    python3 src/RimMandrake/Utils/arena/arena_lane.py pin-version --lane L --version "1.6.4871 rev591"   # the exact Player.log build line
    python3 src/RimMandrake/Utils/arena/arena_lane.py load-times [--lane L]

Files (all under <arena> = arena_tasks.arena_root(), outside git):
    <arena>/lanes/config.json          {lane: {game_version, trial}}
    <arena>/lanes/load_times.jsonl     one line per measured reload: lane, profile, tier, launch_to_ready_s
    <arena>/events/<arm>.jsonl         the §1.7 log (through `emit`, the thin adapter below)

EVENT LOG ADAPTER. FOUNDRY's event-log library (ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE) had not landed on
origin/main when this was written. `emit()` uses it if a module `arena_events` with `append(record)` is importable,
and otherwise appends the same record itself (flock, one JSON line, `writer: "arena_lane"`). Swap in one place.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
REPO = UTILS.parent.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(UTILS))
import arena_safe_git as SG  # noqa: E402  (every git call on a clone the lane does not own the .git of)
import arena_tasks  # noqa: E402  (arena_root, the one arena path resolver)

LANES = {"steve": {"host": "stevedesktop"},
         "archmagi": {"host": "archmagi"}}
PROFILES = ("minimal", "minimal+deps")
EVENTS = ("freeze", "assign", "pass_start", "pass_end", "build_end", "test_start", "test_end", "gate", "judge",
          "critic_round", "live_take", "live_release", "reload", "canary", "card", "owner_touch", "defect", "invalid",
          "switch", "stop")
RELOAD_RULES = ("R0", "R1", "R2", "R3")
# A minimal+deps tier may add at most this many mods to the minimal list in trial mode. Measured 2026-10-30 over
# modset_builder.TIERS against modlist_swap's 26-mod MINIMAL: named dependency tiers add 1-18 (bench 18); the
# acc_2026* acceptance lists add 31-46 and are not an item's load dependencies.
TRIAL_MAX_EXTRA = 20
WRITER = "arena_lane"
RIMFLOW = REPO / "src" / "RimMandrake" / "rimflow" / "cli.py"


class LaneRefused(Exception):
    """A lane refusal. Nothing was touched; the message says what and why."""


class RestoreFailed(LaneRefused):
    """The owner's mod list could not be put back. Loud, but it says nothing about the candidate under test."""


# ---------------------------------------------------------------- paths, config, event log

def lane_paths(root: Path | None = None) -> dict:
    r = Path(root) if root else arena_tasks.arena_root()
    return {"root": r, "lanes": r / "lanes", "config": r / "lanes" / "config.json",
            "load_times": r / "lanes" / "load_times.jsonl", "events": r / "events"}


def swap_marker(p: dict, lane: str) -> Path:
    """Exists while a lane's mod list is swapped and not yet restored. It outlives a killed runner, so the next hold
    of the lane knows the owner's list is not back and restores it on release (self-healing, and `status` shows it)."""
    return p["lanes"] / ("%s.swapped.json" % lane)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_config(p: dict) -> dict:
    try:
        return json.loads(p["config"].read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def write_config(p: dict, cfg: dict):
    p["lanes"].mkdir(parents=True, exist_ok=True)
    tmp = p["config"].with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, p["config"])


def lane_config(p: dict, lane: str) -> dict:
    """The lane's settings with defaults: the trial is on, no version pinned. An old `owner_playing` key is dropped
    (owner 2026-10-30: his coming back to the machine is not an event)."""
    c = dict(read_config(p).get(lane) or {})
    c.pop("owner_playing", None)
    c.setdefault("trial", True)
    c.setdefault("game_version", None)
    return c


def _append_jsonl(path: Path, recs: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        for r in recs:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _eventlog_lib():
    try:
        import arena_events  # noqa: F401  FOUNDRY's library, once it lands
        return arena_events if hasattr(arena_events, "append") else None
    except ImportError:
        return None


def emit(p: dict, rec: dict) -> dict:
    """Write one §1.7 event. Refuses an event name outside the schema (a typo is a lost row, not a new event)."""
    if rec.get("event") not in EVENTS:
        raise ValueError("event %r is not in the §1.7 schema" % rec.get("event"))
    for k in ("arm", "lane", "run_id"):
        if not rec.get(k):
            raise ValueError("event %s: %s missing" % (rec["event"], k))
    rec = {k: v for k, v in rec.items() if v is not None}
    rec.setdefault("ts", _now_iso())
    rec.setdefault("writer", WRITER)
    lib = _eventlog_lib()
    if lib is not None:
        lib.append(rec)
    else:
        _append_jsonl(p["events"] / ("%s.jsonl" % rec["arm"]), [rec])
    return rec


def read_events(p: dict, arm: str | None = None) -> list[dict]:
    out = []
    files = [p["events"] / ("%s.jsonl" % arm)] if arm else sorted(p["events"].glob("*.jsonl"))
    for f in files:
        if f.is_file():
            out += [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    return out


def load_times(p: dict, lane: str | None = None, ok_only: bool = True) -> list[dict]:
    """Measured launch-to-ready rows. A failed launch is not a load time: excluded unless ok_only=False."""
    if not p["load_times"].is_file():
        return []
    rows = [json.loads(x) for x in p["load_times"].read_text(encoding="utf-8").splitlines() if x.strip()]
    return [r for r in rows if (lane is None or r.get("lane") == lane) and (r.get("ok") or not ok_only)]


def same_sha(a, b) -> bool:
    """Two shas name one commit: both given, at least 10 hex, one a prefix of the other."""
    a, b = (a or "").strip().lower(), (b or "").strip().lower()
    if len(a) < 10 or len(b) < 10 or any(ch not in "0123456789abcdef" for ch in a + b):
        return False
    return a.startswith(b) or b.startswith(a)


def canonical_saves() -> set[str]:
    """Save names (no .rws) a lane may never load. Read from canon.yml through canon_save.py, never hard-coded."""
    import canon_save
    n = canon_save.start_savegame_name()
    return {n[:-4] if n.lower().endswith(".rws") else n}


def save_base(name: str) -> str:
    """The comparable form of a save name: no directory (either slash), no .rws, casefolded (Windows paths)."""
    b = str(name).replace("\\", "/").rsplit("/", 1)[-1]
    return (b[:-4] if b.lower().endswith(".rws") else b).casefold()


def is_canonical(name) -> bool:
    return bool(name) and save_base(name) in {save_base(c) for c in canonical_saves()}


def canonical_worlds() -> list[dict]:
    """{name, seed} of each canonical save's world, read from the .rws itself (Saves/ via game_paths). Raises when a
    save cannot be read: the caller turns that into a red canary.

    Why the world and not the save name: measured live 2026-10-30, rimworld/get_game_info carries no key naming the
    loaded save, so the map is identified by jawa/world_info_get's world name + seedString instead. In the canon
    start save the one <seedString> sits in <world><info> (measured: Ash'karr / safety)."""
    import re
    import xml.etree.ElementTree as ET
    from game_paths import SAVES
    out = []
    for n in sorted(canonical_saves()):
        b = (Path(SAVES) / (n + ".rws")).read_bytes()
        i = b.find(b"<world>")
        m = re.search(rb"<info>.*?</info>", b[i:i + 20000], re.S) if i >= 0 else None
        info = ET.fromstring(m.group(0)) if m else None           # an XML parser: entities and &#NN; decode
        w = {"name": info.findtext("name") if info is not None else None,
             "seed": info.findtext("seedString") if info is not None else None}
        if not (is_ident(w["name"]) and is_ident(w["seed"])):
            raise ValueError("no <world><info> name/seedString in %s.rws" % n)
        out.append(w)
    return out


def is_ident(v) -> bool:
    """A world name or seed that can be compared: a non-blank string (an error object or blank is unmeasured)."""
    return isinstance(v, str) and bool(v.strip())


def on_canonical_world(world, canon) -> bool:
    """A live world matching a canonical world on name OR seed counts as canonical (errs toward red)."""
    cf = lambda s: str(s or "").strip().casefold()  # noqa: E731
    return any((cf(world.get("name")) and cf(world.get("name")) == cf(c["name"]))
               or (cf(world.get("seed")) and cf(world.get("seed")) == cf(c["seed"])) for c in canon)


def is_seat_clone(clone) -> bool:
    """A seat's working clone (this repo, or one named bench/foundry): never checked out or reset by a lane."""
    try:
        return Path(clone).resolve() == REPO.resolve() or Path(clone).name in ("bench", "foundry")
    except (OSError, TypeError):
        return True


# ---------------------------------------------------------------- the lane

class Lane:
    """One arm's hold on one lane. Use as a context manager: release (with the owner's list restored) always runs.

    `driver` does the real acts (RealDriver) or fakes them (selftests); this class only decides, refuses and logs."""

    def __init__(self, lane: str, arm: str, driver, purpose: str, task: str | None = None, run_id: str | None = None,
                 root: Path | None = None, flyer_flight: bool = False):
        if lane not in LANES:
            raise LaneRefused("unknown lane %r (lanes: %s)" % (lane, ", ".join(LANES)))
        if flyer_flight:
            raise LaneRefused("a flyer's flight is never live-tested (standing ruling); nothing taken")
        self.lane, self.arm, self.d, self.purpose, self.task = lane, arm, driver, purpose, task
        self.host = LANES[lane]["host"]
        self.run_id = run_id or "%s-%s-%s" % (arm, lane, uuid.uuid4().hex[:8])
        self.p = lane_paths(root)
        self.cfg = lane_config(self.p, lane)
        self.held = False
        self.swapped = False           # the mod list was changed by this hold: release must restore it
        self.launched_at = None        # driver clock at this hold's own launch
        self.loaded_save = None        # None = the quicktest this lane started; else the save name loaded
        self.deployed = {"sha": None, "mods": [], "package_ids": []}
        self.profile = None
        self.expected_active = None    # package ids the profile may have active (None = unmeasured: canary red)
        self.inherited_swap = None     # a swap marker left by an earlier hold that never restored
        self.dirty_mods = []           # mods whose game copy may now be the candidate's: release redeploys main's
        self.restore_clone = None      # the clone those mods were deployed from (main is checked out there to restore)

    # -- logging
    def _ev(self, event, **kw):
        return emit(self.p, dict(arm=self.arm, lane=self.lane, run_id=self.run_id, task=self.task, event=event, **kw))

    # -- take / release
    def __enter__(self):
        self.take()
        return self

    def __exit__(self, et, ev, tb):
        self.release(aborted=et is not None, why=("%s: %s" % (et.__name__, ev)) if et else None)
        return False

    def take(self):
        ok, out = self.d.bridge_take(self.host, "arena %s %s %s: %s" % (self.arm, self.lane, self.run_id,
                                                                          self.purpose), False)
        # the third argument is the retired idle-ok flag, always False (owner 2026-10-30): drivers still take it
        self._ev("live_take", verdict="ok" if ok else "refused",
                 detail={"host": self.host, "out": (out or "")[-300:]})
        if not ok:
            raise LaneRefused("bridge take refused on %s: %s" % (self.host, (out or "").strip()[-200:]))
        self.held = True
        try:
            mk = swap_marker(self.p, self.lane)
            if mk.is_file():            # an earlier hold died with the list swapped: this release puts it back
                try:
                    self.inherited_swap = json.loads(mk.read_text(encoding="utf-8"))
                except ValueError:
                    self.inherited_swap = {"unreadable": True}
                self.swapped = True
                self.dirty_mods = list(self.inherited_swap.get("mods") or [])
                self.restore_clone = self.inherited_swap.get("clone")
        except BaseException:
            self.release(aborted=True, why="take failed after the bridge was taken")   # __exit__ will not run
            raise

    def release(self, aborted=False, why=None):
        """Restore the owner's list if this hold swapped it, release the bridge, log `live_release`. Every step is
        guarded: a failing stop or restore never skips the bridge release or the event."""
        if not self.held:
            return
        restore_s, restore_ok, restore_out, rel_ok, rel_out = 0.0, None, "", False, ""
        mods_ok, mods_out, main_sha, dirty = None, "", None, list(self.dirty_mods)
        swapped = self.swapped
        try:
            if swapped:
                t0 = self.d.clock()
                try:
                    if self.d.game_running():
                        self.d.stop_game()   # the game rewrites ModsConfig on exit: restore only once it is down
                    if self.d.game_running():
                        restore_ok, restore_out = False, ("the game is still running after stop: restore withheld "
                                                          "(its exit would overwrite ModsConfig)")
                    else:
                        restore_ok, restore_out = self.d.restore_modlist()
                except Exception as e:  # noqa: BLE001 - any failure here is a failed restore, reported below
                    restore_ok, restore_out = False, "%s: %s" % (type(e).__name__, e)
                if self.dirty_mods:      # the candidate's files out, main's back; only with the game down (DLLs)
                    try:
                        if self.d.game_running():
                            mods_ok, mods_out = False, "the game is still running: main's mod files not redeployed"
                        elif not self.restore_clone:
                            mods_ok, mods_out = False, "no clone recorded for the deployed mods: cannot redeploy main"
                        else:
                            mods_ok, mods_out, main_sha = self.d.restore_mods(list(self.dirty_mods),
                                                                              self.restore_clone)
                    except Exception as e:  # noqa: BLE001
                        mods_ok, mods_out = False, "%s: %s" % (type(e).__name__, e)
                restore_s = self.d.clock() - t0
                if restore_ok and mods_ok is not False:
                    swap_marker(self.p, self.lane).unlink(missing_ok=True)
                    self.dirty_mods = []
        finally:
            try:
                rel_ok, rel_out = self.d.bridge_release(self.host)
            except Exception as e:  # noqa: BLE001
                rel_ok, rel_out = False, "%s: %s" % (type(e).__name__, e)
            self.held = False
            self.swapped = False
            self._ev("live_release", verdict="ok" if (restore_ok is not False and mods_ok is not False and rel_ok)
                     else "error",
                     minutes=round(restore_s / 60.0, 3),
                     detail={"restored": swapped, "restore_ok": restore_ok, "restore_s": round(restore_s, 1),
                             "charged_to": ((self.inherited_swap or {}).get("arm") or self.arm) if swapped else None,
                             "aborted": aborted, "why": why,
                             "inherited_swap": self.inherited_swap,
                             "restore_out": (restore_out or "")[-300:], "release_out": (rel_out or "")[-200:],
                             "mods_restored": dirty, "mods_restore_ok": mods_ok, "main_sha": main_sha,
                             "mods_restore_out": (mods_out or "")[-300:]})
        if restore_ok is False:
            raise RestoreFailed("modlist restore FAILED on %s: the owner's list is not back: %s"
                              % (self.host, (restore_out or "").strip()[-200:]))
        if mods_ok is False:
            raise RestoreFailed("mod-file restore FAILED on %s: the candidate's files of %s may still be in the game: %s"
                                % (self.host, ", ".join(dirty), (mods_out or "").strip()[-200:]))

    def _write_marker(self):
        """Create or update the swap marker. An inherited marker keeps its arm (it is charged the restore); the
        mods and clone always carry the union this lane must redeploy from main, so a killed run still restores."""
        mk = swap_marker(self.p, self.lane)
        rec = dict(self.inherited_swap or {}) if mk.is_file() else {}
        rec.pop("unreadable", None)
        rec.setdefault("run_id", self.run_id)
        rec.setdefault("arm", self.arm)
        rec.setdefault("ts", _now_iso())
        rec["mods"] = list(self.dirty_mods)
        rec["clone"] = self.restore_clone
        self.p["lanes"].mkdir(parents=True, exist_ok=True)
        tmp = mk.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, mk)

    def _need_held(self):
        if not self.held:
            raise LaneRefused("lane %s is not held by this run" % self.lane)

    # -- profile, deploy, reload
    def check_profile(self, profile: str, tier: str | None):
        if profile == "full" or profile not in PROFILES:
            if self.cfg["trial"]:
                raise LaneRefused("profile %r refused in trial mode: the trial runs the minimal list or "
                                  "minimal plus an item's load dependencies only (owner 2026-10-29)" % profile)
            raise LaneRefused("profile %r unknown (%s)" % (profile, ", ".join(PROFILES)))
        if profile == "minimal+deps" and not tier:
            raise LaneRefused("minimal+deps needs a modset_builder --tier naming the item's load dependencies")
        if profile == "minimal+deps" and tier not in self.d.known_tiers():
            raise LaneRefused("tier %r is not a modset_builder tier: only a named minimal+deps tier is allowed in "
                              "the trial" % tier)
        if profile == "minimal" and tier:
            raise LaneRefused("profile minimal takes no tier (got %r); use minimal+deps" % tier)

    def deploy(self, mods: list[str], has_dll: bool, clone: str, sha: str):
        """deploy_custom_mods --mod <m> --apply from `clone`, which must be checked out at `sha`."""
        self._need_held()
        if has_dll and self.d.game_running():
            raise LaneRefused("C# deploy refused while the game runs: the DLL is locked")
        if is_seat_clone(clone):
            raise LaneRefused("clone %s is a seat clone: a lane deploys only from a clone it may later reset to "
                              "origin/main to restore the owner's mod files" % clone)
        head = self.d.clone_head(clone)
        if not same_sha(head, sha):
            raise LaneRefused("clone %s is at %s, not the candidate sha %s" % (clone, head, sha))
        dirty = self.d.clone_dirty(clone)
        if dirty:
            raise LaneRefused("clone %s has local changes, so it is not the candidate sha: %s" % (clone, dirty[:200]))
        if self.restore_clone and self.dirty_mods and self.restore_clone != clone:
            raise LaneRefused("this hold already deployed %s from %s; one restore clone per hold (got %s)"
                              % (", ".join(self.dirty_mods), self.restore_clone, clone))
        self.restore_clone = clone      # recorded BEFORE the first copy: a half-done deploy is still restored
        self.dirty_mods += [m for m in mods if m not in self.dirty_mods]
        self.swapped = True
        self._write_marker()
        out = []
        for m in mods:
            ok, txt = self.d.deploy(m, clone)
            out.append({"mod": m, "ok": ok, "out": (txt or "")[-200:]})
            if not ok:
                raise LaneRefused("deploy of %s failed: %s" % (m, (txt or "").strip()[-200:]))
        self.deployed = {"sha": head, "mods": list(mods), "package_ids": self.d.package_ids(mods, clone)}
        return out

    def reload(self, profile: str, tier: str | None, rule: str, mods=(), has_dll=False, clone=None, sha=None,
               why: str = ""):
        """Stop, swap the list, deploy, launch, start a quicktest; log ONE `reload` with the measured
        launch-to-ready time and the M1 rule the caller met. Returns the event."""
        self._need_held()
        if rule not in RELOAD_RULES:
            raise LaneRefused("reload rule %r is not one of %s (testpilot_merged M1)" % (rule, RELOAD_RULES))
        self.check_profile(profile, tier)
        try:                            # resolved BEFORE anything is stopped or swapped: a too-big tier never runs
            exp = self.d.expected_active(profile, tier)
            exp = {x.lower() for x in exp} if exp is not None else None
        except Exception:  # noqa: BLE001 - unmeasured; refused below for a tier, red in the canary for minimal
            exp = None
        if profile == "minimal+deps" and self.cfg["trial"]:
            try:
                base = {x.lower() for x in self.d.expected_active("minimal", None)}
            except Exception:  # noqa: BLE001
                base = None
            if exp is None or base is None:
                raise LaneRefused("tier %r: its mod set could not be resolved, so it cannot be shown to be minimal "
                                  "plus load dependencies (trial mode)" % tier)
            if len(exp - base) > TRIAL_MAX_EXTRA:
                raise LaneRefused("tier %r adds %d mods to the minimal list (trial cap %d): not an item's load "
                                  "dependencies" % (tier, len(exp - base), TRIAL_MAX_EXTRA))
        if self.d.game_running():
            self.d.stop_game()
        if self.d.game_running():
            raise LaneRefused("the game did not stop; no list swap or C# deploy while it runs")
        self.swapped = True             # from here on the owner's list may be gone: release restores it
        self._write_marker()
        ok, out = self.d.apply_minimal() if profile == "minimal" else self.d.apply_tier(tier)
        if not ok:
            raise LaneRefused("profile %s%s refused by the swap tool: %s"
                              % (profile, " (" + tier + ")" if tier else "", (out or "").strip()[-200:]))
        self.profile = {"profile": profile, "tier": tier}
        self.expected_active = exp
        deploys = self.deploy(list(mods), has_dll, clone, sha) if mods else []
        t0 = self.d.clock()
        ok, out = self.d.launch_and_wait()
        if ok:
            ok, out = self.d.start_quicktest()
        t1 = self.d.clock()
        self.launched_at = t0
        self.loaded_save = None
        ready_s = round(t1 - t0, 1)
        _append_jsonl(self.p["load_times"], [{"ts": _now_iso(), "lane": self.lane, "profile": profile, "tier": tier,
                                              "launch_to_ready_s": ready_s, "ok": ok, "run_id": self.run_id}])
        ev = self._ev("reload", rule=rule, minutes=round(ready_s / 60.0, 3), verdict="ok" if ok else "error",
                      sha=self.deployed["sha"],
                      detail={"profile": profile, "tier": tier, "launch_to_ready_s": ready_s, "deploy": deploys,
                              "has_dll": has_dll, "why": why, "out": (out or "")[-300:]})
        if not ok:
            raise LaneRefused("launch to a ready quicktest failed after %.0f s: %s" % (ready_s, (out or "")[-200:]))
        return ev

    def load_save(self, name: str):
        """Load a test fixture save. The canonical world save is refused before the bridge is asked."""
        self._need_held()
        base = name[:-4] if name.lower().endswith(".rws") else name
        if is_canonical(name):
            raise LaneRefused("save %r is the canonical world save: never loaded by a lane" % name)
        ok, out = self.d.load_save(base)
        if not ok:
            raise LaneRefused("load_save %s failed: %s" % (base, (out or "")[-200:]))
        self.loaded_save = base

    # -- canary
    def canary(self, expect_sha: str | None) -> dict:
        """Run every canary check; log `canary` (and `invalid` when red). Returns {ok, problems, facts}."""
        self._need_held()
        problems = []
        try:
            f = self.d.game_facts() or {}
        except Exception as e:  # noqa: BLE001 - a canary that cannot ask is red
            f, problems = {}, ["game facts unreadable: %s: %s" % (type(e).__name__, e)]
        probe = f.get("ingame_canary")
        if not isinstance(probe, dict):
            problems.append("in-game canary UNMEASURED (no modcheck validity.canary result)")
        elif not probe.get("ok"):
            problems += ["in-game: %s" % x for x in (probe.get("problems") or ["red, no reason given"])]
        n = f.get("live_colonists")
        if not isinstance(n, int):
            problems.append("live colonist count UNMEASURED")
        elif n <= 0:
            problems.append("no live colonist (dead colony)")
        mt = f.get("player_log_mtime")
        if self.launched_at is None:
            problems.append("this hold never launched the game: Player.log freshness has no reference")
        elif not isinstance(mt, (int, float)):
            problems.append("Player.log mtime UNMEASURED")
        elif mt < self.launched_at:
            problems.append("Player.log is stale: last written before this lane's launch")
        want_v, got_v = self.cfg.get("game_version"), f.get("game_version")
        if not want_v:
            problems.append("expected game version not pinned for lane %s (arena_lane.py pin-version)" % self.lane)
        elif not got_v:
            problems.append("game version UNMEASURED")
        elif str(got_v).strip() != str(want_v).strip():
            problems.append("game version %s, expected %s" % (got_v, want_v))
        if expect_sha:
            ds = self.deployed.get("sha") or ""
            if not same_sha(ds, expect_sha):
                problems.append("deployed sha %s is not the candidate sha %s" % (ds or "none", expect_sha))
        active = f.get("active_mods")
        if self.deployed["package_ids"]:
            if not isinstance(active, list):
                problems.append("active mod list UNMEASURED")
            else:
                low = {a.lower() for a in active}
                miss = [m for m in self.deployed["package_ids"] if m.lower() not in low]
                if miss:
                    problems.append("deployed mod(s) not active: %s" % ", ".join(miss))
        if not isinstance(active, list):
            if not self.deployed["package_ids"]:
                problems.append("active mod list UNMEASURED")
        elif self.expected_active is None:
            problems.append("the profile's expected mod set is UNMEASURED: cannot prove nothing extra is active")
        else:
            allowed = self.expected_active | {m.lower() for m in self.deployed["package_ids"]}
            extra = sorted(a for a in active if a.lower() not in allowed)
            if extra:
                problems.append("%d mod(s) active beyond the %s profile (not a trial list): %s"
                                % (len(extra), (self.profile or {}).get("profile"), ", ".join(extra[:5])))
        if self.loaded_save and is_canonical(self.loaded_save):
            problems.append("the map is the canonical world save %s" % self.loaded_save)
        w = f.get("world")
        if not isinstance(w, dict) or not is_ident(w.get("name")) or not is_ident(w.get("seed")):
            problems.append("the loaded map's world identity is UNMEASURED (no jawa/world_info_get name+seed)")
        else:
            try:
                canon = canonical_worlds()
            except Exception as e:  # noqa: BLE001 - cannot read the canon save: cannot prove we are not on it
                problems.append("the canonical world's identity is unreadable: %s: %s" % (type(e).__name__, e))
            else:
                if on_canonical_world(w, canon):
                    problems.append("the map is on the canonical world (%s / %s)" % (w.get("name"), w.get("seed")))
        res = {"ok": not problems, "problems": problems,
               "facts": {k: v for k, v in f.items() if k != "ingame_canary"},
               "ingame": probe if isinstance(probe, dict) else None}
        self._ev("canary", verdict="pass" if res["ok"] else "fail", sha=expect_sha,
                 detail={"problems": problems, "facts": res["facts"]})
        if not res["ok"]:
            self._ev("invalid", sha=expect_sha, detail={"why": "canary red", "problems": problems})
        return res


# ---------------------------------------------------------------- the real driver (live only; never run offline)

def _sh(argv, timeout=600, cwd=None):
    try:
        p = subprocess.run(argv, cwd=cwd or str(REPO), capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return 99, "%s: %s" % (type(e).__name__, e)


def _sg(clone, *a, timeout=600, transport=False, both=True):
    """git on `clone` through arena_safe_git (no replace refs, grafts, hooks, fsmonitor, filter/diff drivers, the
    clone's ssh/credential commands): the clone's .git is a build helper's. -> (rc, output). `both`: stdout+stderr
    (False: stdout only, for an answer a caller compares)."""
    try:
        p = SG.git_run(clone, *a, transport=transport, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + ((p.stderr or "") if both else "")
    except (OSError, subprocess.SubprocessError) as e:      # CloneRefused is an OSError
        return 99, "%s: %s" % (type(e).__name__, e)


class RealDriver:
    """The existing tools, called as they are. Runs on the lane's own machine, from WSL, repo root as cwd.

    UNPROVEN LIVE (owed): every method here; see the item's rimflow note."""

    def __init__(self, seat: str | None = None):
        self.seat = seat

    def _rf(self, *args):
        argv = ["python3", str(RIMFLOW)] + (["--seat", self.seat] if self.seat else []) + list(args)
        return _sh(argv, timeout=180)

    def clock(self):
        return time.time()

    def bridge_take(self, host, purpose, idle_ok=False):
        """`idle_ok` is accepted and ignored. A lane take is always the delegated take (`--idle-ok`): free, ours or
        45-min stale, never his OWNER hold at any age, never flight wording. It reads nothing about his presence
        (owner 2026-10-30); a plain take would cut a stale OWNER hold (review of 9456c1f533)."""
        rc, out = self._rf("bridge", "take", "--host", host, "--idle-ok", "--for", purpose)
        return rc == 0, out

    def bridge_release(self, host):
        rc, out = self._rf("bridge", "release", "--host", host)
        return rc == 0, out

    def game_running(self):
        import modset_builder
        return modset_builder.game_running()

    def stop_game(self):
        from northstar_driver import live_session
        try:
            live_session.stop_game()
        except SystemExit as e:
            raise LaneRefused(str(e))

    def apply_minimal(self):
        rc, out = _sh(["python3", str(UTILS / "modlist_swap.py"), "--minimal", "--apply"], timeout=300)
        return rc == 0, out

    def known_tiers(self):
        import modset_builder
        return set(modset_builder.TIERS)

    def expected_active(self, profile, tier):
        """The package ids the profile writes: modlist_swap's MINIMAL list, or the tier's resolved closure."""
        import modlist_swap
        if profile == "minimal":
            return modlist_swap.mods(modlist_swap.MINIMAL)
        import modset_builder
        pids, _missing, refusals = modset_builder.resolve_tier(tier, modset_builder.scan())
        return None if refusals else pids

    def apply_tier(self, tier):
        rc, out = _sh(["python3", str(UTILS / "modset_builder.py"), "--tier", tier, "--apply"], timeout=300)
        return rc == 0, out

    def restore_modlist(self):
        rc, out = _sh(["python3", str(UTILS / "modlist_swap.py"), "--restore", "--apply"], timeout=300)
        return rc == 0, out

    def clone_head(self, clone):
        rc, out = _sg(clone, "rev-parse", "HEAD", timeout=60, both=False)
        return out.strip() if rc == 0 else None

    def clone_dirty(self, clone):
        """'' when the clone is clean (tracked and untracked, ignored files aside); else what differs."""
        rc, out = _sg(clone, "status", "--porcelain", timeout=120, both=False)    # stdout only: stderr is not "dirty"
        return out.strip() if rc == 0 else ("git status failed: " + out.strip())

    def deploy(self, mod, clone):
        rc, out = _sh(["python3", os.path.join(clone, "src", "RimMandrake", "Utils", "deploy_custom_mods.py"),
                       "--mod", mod, "--apply"], timeout=600, cwd=clone)
        return rc == 0, out   # deploy_custom_mods --apply: 0 = repo and game agree after verify; 1 = they do not
                              # (and sys.exit(msg) crashes exit 1 too), so 1 is never a deploy

    def restore_mods(self, mods, clone):
        """Put main's version of `mods` back in the game: in `clone` (the runner's own, never a seat clone), fetch,
        detach at origin/main, clean, then deploy_custom_mods --mod M --apply --prune for each (prune: files the
        candidate ADDED are game-only once main is the source, and --apply alone keeps game-only files).
        Returns (ok, output, main_sha)."""
        if is_seat_clone(clone):
            return False, "clone %s is a seat clone: main is never checked out there by a lane" % clone, None
        out = ""
        for argv, tr in ((["fetch", "-q", "origin"], True),
                         (["checkout", "-q", "--detach", "origin/main"], False),
                         (["clean", "-fdq"], False)):
            rc, txt = _sg(clone, *argv, timeout=300, transport=tr)
            out += txt
            if rc != 0:
                return False, out + " (%s rc %d)" % (" ".join(argv), rc), None
        head = self.clone_head(clone)
        for m in mods:
            rc, txt = _sh(["python3", os.path.join(clone, "src", "RimMandrake", "Utils", "deploy_custom_mods.py"),
                           "--mod", m, "--apply", "--prune"], timeout=600, cwd=clone)
            out += txt[-400:]
            if rc != 0:
                return False, out + " (deploy %s rc %d)" % (m, rc), head
        return True, out, head

    def package_ids(self, mods, clone):
        import xml.etree.ElementTree as ET
        out = []
        for m in mods:
            # deploy_custom_mods names a mod by its bare folder, which sits one tier down: src/<Tier>/<Mod>
            # (src/RimMandrake/Visibility). Found live 2026-10-30: src/<Mod>/About never exists.
            hits = sorted((Path(clone) / "src").glob("*/%s/About/About.xml" % m))
            try:
                if len(hits) != 1:
                    raise OSError("%d About.xml for %s" % (len(hits), m))
                out.append(ET.parse(hits[0]).getroot().findtext("packageId").strip())
            except (OSError, ET.ParseError, AttributeError):
                out.append("<unreadable:%s>" % m)       # the canary then reports it not active: red, never silent
        return out

    def launch_and_wait(self):
        from northstar_driver import live_session
        try:
            live_session.launch_and_wait()
            return True, "bridge token seen"
        except SystemExit as e:
            return False, str(e)

    def start_quicktest(self):
        rc, out = _sh(["python.exe", "src/RimMandrake/bridgetools/prove_quicktest_world.py"], timeout=420)
        return rc == 0, out

    def load_save(self, name):
        return False, "load_save is not wired in the real driver yet (no task needs a fixture save)"

    def game_facts(self):
        from game_paths import PLAYER_LOG, MODS_CONFIG
        import modlist_swap
        f = {}
        try:
            f["player_log_mtime"] = os.stat(PLAYER_LOG).st_mtime
            with open(PLAYER_LOG, encoding="utf-8", errors="replace") as fh:   # the build line opens the log
                for line in fh.readlines()[:50]:
                    if line.startswith("RimWorld 1."):
                        f["game_version"] = line[len("RimWorld "):].strip()   # e.g. "1.6.4871 rev591"
                        break
        except OSError:
            pass
        f["active_mods"] = modlist_swap.mods(MODS_CONFIG)
        probe = HERE / "arena_lane_probe.py"
        rc, out = _sh(["python.exe", str(probe.relative_to(REPO)).replace("/", "\\")], timeout=300)
        got = None                      # _sh mixes stderr in: the probe's ONE JSON line is the last line opening "{"
        for line in reversed(out.strip().splitlines()):
            if line.lstrip().startswith("{"):
                try:
                    got = json.loads(line)
                    break
                except ValueError:
                    pass
        if isinstance(got, dict):
            f.update(got)
        else:
            f["probe_error"] = out[-300:]
        return f


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("--lane", choices=sorted(LANES))
    c = sub.add_parser("config")
    c.add_argument("--lane", required=True, choices=sorted(LANES))
    pv = sub.add_parser("pin-version")
    pv.add_argument("--lane", required=True, choices=sorted(LANES))
    pv.add_argument("--version", required=True)
    lt = sub.add_parser("load-times")
    lt.add_argument("--lane", choices=sorted(LANES))
    a = ap.parse_args(argv)
    p = lane_paths()
    if a.cmd == "status":
        for ln in ([a.lane] if a.lane else sorted(LANES)):
            mk = swap_marker(p, ln)
            print(ln, json.dumps(lane_config(p, ln), sort_keys=True),
                  ("LIST SWAPPED, NOT RESTORED: " + mk.read_text(encoding="utf-8").strip()) if mk.is_file() else "")
    elif a.cmd in ("config", "pin-version"):
        cfg = read_config(p)
        ent = cfg.setdefault(a.lane, {})
        ent.pop("owner_playing", None)
        if a.cmd == "pin-version":
            ent["game_version"] = a.version
        write_config(p, cfg)
        print(a.lane, json.dumps(lane_config(p, a.lane), sort_keys=True))
    elif a.cmd == "load-times":
        for r in load_times(p, a.lane, ok_only=False):
            print(json.dumps(r, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
