"""showcase_common.py -- the shared plumbing of the two HugeThings promise showcases (owner ruling 2026-11-11,
design/RimMandrake/hugethings_codex_2026-11-09/ANSWERS_OWNER.md answers 1-2): showcase_titan_live.py and
showcase_plants_live.py. Pure plumbing, no verdicts of its own:

  Showcase    rows {id, criterion, status PASS|FAIL|UNMEASURED, cls MOD|SITE|HARNESS, detail}, a truncated call log, and
              PHASES run strictly in order: each phase is stamped (startTick/endTick from jawa/site_state, UTC) and a phase
              that does not PASS stops the run; every later phase's rows are written UNMEASURED and its stamps stay null.
              Nothing is ever reordered or skipped past a failure.
  Settings    snapshot of RM_HugeThingsSettings fields first, writes through put(), exact restore().
  LiveSite    the registered disposable test site (Utils/modcheck/test_site_saves): load it, save a UNIQUE scene-begin
              snapshot, reload that snapshot, quiet the world (helpers.quiet_world); restore() puts the settings transaction
              back and reloads the snapshot. The same pattern as trunk_doors_live.py main().
  preflight   jawa/running_mods: the packages a showcase needs are loaded and the loaded RM_HugeThings.dll is this clone's.

Live imports (validation_core, test_site_saves, helpers, clockgate) are LAZY so the offline selftest needs no game paths.
"""
import hashlib
import json
import os
import re
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
MAP_RECT = "0,0,250,250"
# safe_advance stop kinds (JawaBenchVitalsCore.DefaultStopKinds minus the ones a showcase causes ON PURPOSE): a dying titan
# (death, hurt, downed of a non-colonist), scavengers walking in (hostile_arrival) and a titan breaking walls
# (threat_structure) would otherwise latch and stop the clock mid-phase.
STOP_ON = "colonist_hostile,modal_stuck,colony_loss,clock_discontinuity,cancel"
LOG_CHARS = 600


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def kv(text):
    return dict(re.findall(r"(\w+)=([^\s|\]]+)", str(text)))


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class Showcase(object):
    def __init__(self, bridge, out, script, item, required, ticker=None):
        self.b, self.out, self.script, self.item = bridge, out, script, item
        self.required = list(required)
        self.ticker = ticker
        self.rows, self.phases, self.log = [], [], []
        self.rec = dict(script=script, item=item, started=utc())
        self.stopped_by = None
        self.scene = 1                # a restore-and-reload starts a new scene: its clock restarts, order is per scene

    # ---------------------------------------------------------------- bridge
    def call(self, tool, **kw):
        try:
            r = self.b.call(tool, **kw) or {}
        except Exception as ex:  # noqa: BLE001
            r = {"success": False, "error": "call raised: %r" % (ex,)}
        if not isinstance(r, dict):
            r = {"success": False, "raw": r}
        self.log.append(dict(tool=tool, args=kw, result=str(r)[:LOG_CHARS]))
        return r

    def hook(self, typ, method, args=""):
        r = self.call("jawa/static_call", type=typ, method=method, args=args)
        res = r.get("result")
        txt = str(res if res is not None else (r.get("error") or r.get("message") or r))
        return (r.get("success") is True and isinstance(res, str) and not res.startswith("FAIL")), txt

    def now(self):
        t = self.call("jawa/site_state").get("ticksGame")
        return t if type(t) is int else None

    def ticks(self, n):
        """Advance n ticks (live: clockgate.advance_chunk, paused sub-steps); returns the MEASURED tick delta (None unreadable)."""
        before = self.now()
        if self.ticker is not None:
            self.ticker(int(n))
        else:
            self.call("rimworld/step_game_ticks", ticks=int(n))
        after = self.now()
        return after - before if before is not None and after is not None else None

    def pawn(self, pid, rect=MAP_RECT):
        """The list_pawns row of pid on the map (None when absent: dead, despawned or never there)."""
        r = self.call("jawa/list_pawns", rect=rect, limit=1000)
        for p in r.get("pawns") or []:
            if p.get("id") == pid:
                return p
        return None

    def things(self, rect, defname=None):
        kw = dict(rect=rect, limit=5000)
        if defname:
            kw["defName"] = defname
        r = self.call("jawa/list_things", **kw)
        rows = r.get("things")
        if not isinstance(rows, list) or r.get("countMatched") not in (None, len(rows)):
            return None
        return rows

    def reach(self, pawn, x, z):
        """Paused path read (trunk_doors_live.Run.reach): can `pawn` walk onto x,z now? None when unreadable."""
        r = self.call("jawa/order_pawn", pawnId=pawn, x=x, z=z, pathEndMode="oncell", waitTicks=0, unpause=False, draft=True)
        self.call("jawa/stop_job", pawnId=pawn, mode="stopall")
        rows = r.get("pawns") or []
        if len(rows) != 1 or type(rows[0].get("canReach")) is not bool:
            return None
        return rows[0]["canReach"]

    # ---------------------------------------------------------------- rows and phases
    def row(self, rid, crit, status, cls, detail, **extra):
        d = dict(id=rid, item=self.item, criterion=crit, status=status, cls=cls, detail=str(detail)[:900])
        d.update(extra)
        self.rows.append(d)
        print("  %-26s %-10s %-7s %s" % (rid, status, cls, str(detail)[:300]), flush=True)
        self.save()
        return status

    def run_phases(self, phases):
        """phases: [(name, fn, row_ids)] in the ONLY order they may run. fn(self) -> 'PASS'|'FAIL'|'UNMEASURED'."""
        for order, (name, fn, row_ids) in enumerate(phases, 1):
            ph = dict(order=order, phase=name, scene=self.scene, status=None, startTick=None, endTick=None, startUtc=None, endUtc=None,
                      rows=list(row_ids))
            self.phases.append(ph)
            if self.stopped_by is not None:
                ph["status"] = "UNMEASURED"
                ph["gatedBy"] = self.stopped_by
                for rid in row_ids:
                    if not any(r["id"] == rid for r in self.rows):
                        self.row(rid, name, "UNMEASURED", "HARNESS",
                                 "gated: phase %s ended %s, so %s was not run (the order is fixed, never reordered)"
                                 % (self.stopped_by, self.phase_status(self.stopped_by), name))
                continue
            ph["startTick"], ph["startUtc"] = self.now(), utc()
            try:
                status = fn(self)
            except Exception as ex:  # noqa: BLE001
                status = "UNMEASURED"
                ph["error"] = repr(ex)
            for rid in row_ids:       # a phase that forgot a row never reads as complete
                if not any(r["id"] == rid for r in self.rows):
                    self.row(rid, name, "UNMEASURED", "HARNESS", "phase %s wrote no row %s (%s)" % (name, rid, ph.get("error", "")))
            mine = [r for r in self.rows if r["id"] in row_ids]
            if status == "PASS" and not all(r["status"] == "PASS" for r in mine):
                status = "FAIL" if any(r["status"] == "FAIL" for r in mine) else "UNMEASURED"
            ph["status"] = status
            ph["endTick"], ph["endUtc"] = self.now(), utc()
            if status != "PASS":
                self.stopped_by = name
            self.save()
        return self.stopped_by is None

    def phase_status(self, name):
        return next((p["status"] for p in self.phases if p["phase"] == name), None)

    def ordered(self):
        """True when the phases that ran carry stamps proving their order: each start >= the previous end, end >= start."""
        last, scene = None, None
        for p in self.phases:
            if p["startTick"] is None or p.get("foreignClock"):
                continue              # a phase run inside another save's scene: its ticks are that save's, UTC orders it
            if p.get("scene") != scene:
                last, scene = None, p.get("scene")
            if p["endTick"] is None or p["endTick"] < p["startTick"] or (last is not None and p["startTick"] < last):
                return False
            last = p["endTick"]
        return True

    def summary(self):
        from live_results import aggregate
        s = aggregate(self.rows, self.required)
        s["phases_in_order"] = self.ordered()
        s["stopped_by"] = self.stopped_by
        return s

    def exit_code(self):
        """Lightspeed exit (proof contract): 0 every required row PASS; 1 a MOD FAIL among them; 2 could not ask.
        A run that only went UNMEASURED (site, harness, a crash) never exits 1: that would charge the mod.
        An unrestored site or settings is never 0: the scene was not left as found."""
        unrestored = self.rec.get("site_restore_errors") or self.rec.get("settings_restore_bad")
        if self.summary().get("gameplay_pass") and not self.rec.get("error") and not unrestored:
            return 0
        req = set(self.required)
        if any(r["id"] in req and r.get("status") == "FAIL" and r.get("cls") == "MOD" for r in self.rows):
            return 1
        return 2

    def save(self):
        if not self.out:
            return
        d = os.path.dirname(self.out)
        if d:
            os.makedirs(d, exist_ok=True)
        rec = dict(self.rec, when=utc(), rows=self.rows, phases=self.phases, summary=self.summary(), calls=self.log)
        with open(self.out, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, default=str)


class Settings(object):
    """Snapshot first, write through put(), restore exactly (titan_events_live.py main())."""

    def __init__(self, sc, fields, typ=SETTINGS):
        self.sc, self.fields, self.typ, self.prior = sc, list(fields), typ, {}

    def get(self, f):
        return self.sc.call("jawa/mod_settings_field", typeName=self.typ, action="get", field=f).get("value")

    def snapshot(self):
        self.prior = dict((f, self.get(f)) for f in self.fields)
        return all(v is not None for v in self.prior.values())

    def put(self, f, v):
        # restore-check: ok -- snapshot() runs before any put and restore() runs in every driver's finally
        if f not in self.prior:
            self.prior[f] = self.get(f)
        self.sc.call("jawa/mod_settings_field", typeName=self.typ, action="set", field=f, value=str(v))
        got = self.get(f)
        try:
            return float(got) == float(v)
        except (TypeError, ValueError):
            return str(got).lower() == str(v).lower()

    def restore(self):
        bad = []
        for f, v in self.prior.items():
            if v is None:
                continue
            self.sc.call("jawa/mod_settings_field", typeName=self.typ, action="set", field=f, value=str(v))
            if str(self.get(f)).lower() != str(v).lower():
                bad.append(f)
        return bad


def preflight(sc, packages):
    """(ok, detail): the needed packages are loaded and the loaded RM_HugeThings.dll is this clone's build."""
    r = sc.call("jawa/running_mods", assembly="RM_HugeThings", details=True)
    ids = [str(x).lower() for x in r.get("packageIds") or []]
    if not ids:
        return False, "running_mods unreadable: %s" % str(r)[:200]
    missing = [p for p in packages if p not in ids]
    if missing:
        return False, "not loaded: %s" % missing
    dll = os.path.join(MOD, "Assemblies", "RM_HugeThings.dll")
    matches = (r.get("assembly") or {}).get("matches") or []
    if not os.path.isfile(dll):
        return False, "no clone DLL at %s" % dll
    want = sha_file(dll)
    if len(matches) != 1 or matches[0].get("sha256") != want:
        return False, "loaded RM_HugeThings.dll differs from this clone (%s)" % [m.get("sha256") for m in matches]
    return True, "loaded %d packages incl. %s; RM_HugeThings.dll sha256 %s" % (len(ids), packages, want[:12])


def live_bridge():
    """The standalone bridge (validation_core.Bridge: call(tool, **kw)) and a clockgate ticker on it."""
    for p in (os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import validation_core as V
    import test_site_saves as T
    import clockgate as C
    b = V.Bridge()

    def ticker(n):
        done = 0
        while done < n:
            k = min(600, n - done)
            C.advance_chunk(T.call_session(b.call), k, stop_on=STOP_ON)
            done += k
    return b, ticker


class LiveSite(object):
    """A registered disposable site restored around one showcase (trunk_doors_live.py main(), the scene-begin snapshot)."""

    def __init__(self, call, site_key, prefix):
        self.call, self.key, self.prefix = call, site_key, prefix
        self.snapshot, self.saved, self.tx, self.evidence = None, False, None, {}

    def begin(self):
        import test_site_saves as T
        import game_paths as G
        import helpers as H
        name = T.read_registry().get(self.key, {}).get("save") or T.SITES[self.key]["save"]
        if not (name and name.startswith("RM_TestSite_") and os.path.isfile(os.path.join(G.SAVES, name + ".rws"))):
            raise RuntimeError("SITE: registered site %s save %r missing" % (self.key, name))
        ld = T.load_site(self.call, self.key, name=name, map_controls=("modal_broker",))
        self.evidence["site_load"] = dict(save=name, verified=ld.get("verified"), problems=ld.get("problems"))
        if not ld.get("verified"):
            raise RuntimeError("SITE: registered site %s did not load: %s" % (self.key, ld.get("problems")))
        self.snapshot = self.prefix + uuid.uuid4().hex[:12]
        self.evidence["snapshot"] = T.save_site(self.call, self.snapshot, G.SAVES)
        self.saved = True
        bl = T.load_site(self.call, self.key, name=self.snapshot, check=False, map_controls=("modal_broker",))
        self.evidence["baseline_load"] = dict(verified=bl.get("verified"), problems=bl.get("problems"))
        if not bl.get("verified"):
            raise RuntimeError("SITE: scene-begin reload of %s failed" % self.snapshot)
        self.tx = H.SettingsTransaction(T.call_session(self.call))
        self.tx.__enter__()
        quiet = H.quiet_world(T.call_session(self.call), self.tx, wild_spawner=False, log_raids=False)
        self.evidence["quiet"] = dict(verified=quiet.verified, evidence=quiet.evidence)
        return self.evidence

    def restore(self):
        import test_site_saves as T
        errors = []
        if self.tx is not None:
            try:
                self.tx.__exit__(None, None, None)
            except Exception as ex:  # noqa: BLE001
                errors.append(repr(ex))
        if self.saved:
            try:
                rl = T.load_site(self.call, self.key, name=self.snapshot, check=False, map_controls=("modal_broker",))
                self.evidence["restore_load"] = dict(verified=rl.get("verified"), problems=rl.get("problems"))
                if not rl.get("verified"):
                    errors.append("scene-begin restoration load of %s failed" % self.snapshot)
            except Exception as ex:  # noqa: BLE001
                errors.append(repr(ex))
        self.evidence["restore_errors"] = errors
        return errors
