"""titan_test_races_live.py -- the five titan rows that needed a body-size 8/20 creature (TITANIC_BODYSIZE_TEST_RACE_1, criterion A2),
driven with the harness-only test races of src/RimMandrake/HugeThingsTestRaces on whatever Playing map is current.

  python3 src/RimMandrake/HugeThings/northstar/titan_test_races_live.py [--site X,Z] [--out FILE]

LIST: Huge Things (mandrake.rm.hugethings) + Huge Things Test Races (mandrake.rm.hugethingstestraces), all five DLC; nothing else.
The probes are the static hooks in Source/Titanic/Events/TitanValidationHooks.cs, called through jawa/static_call. The map is
DIRTIED (a T3 and a T2 are killed into corpses): use a throwaway quicktest map. Settings touched are snapshotted and restored.

Rows {id, criterion, status PASS|FAIL|UNMEASURED, cls MOD|SITE|HARNESS, detail}; JSON -> Transient/modcheck/ by default.
  R1 t2_t3_tiers                    TierReport: T2 race reads T2, T3 reads T3, the forced-out control None, Elephant T1;
                                    tiered races carry CompTitanicWake.
  R2 t3_corpse_becomes_a_harvest_site KillTitanAt T3 -> one more RM_TitanicCorpseSite; KillTitanAt T2 -> none more.
  R3 butcher_yield_curve_reduces_t1_t2_yield ButcherYieldReport: T2 meat = control meat x the kernel factor (< 1), within
                                    per-pawn rounding; the same-mass forced-out control is unreduced.
  R4 t2_holes_thin_roofs_and_crushes_walls RoofWallProbe: a T2 stepping into a roofed wall cell holes RoofConstructed and damages
                                    or breaks the wood wall; the control leaves both.
  R5 thick_roof_route_excluded      ThickRoofCostProbe: a T2's step cost under RoofRockThick >= 2000 and above open ground;
                                    the control's two costs are equal.
Refuses to judge (UNMEASURED SITE) when the custom tier ladder (tierThresholdsCustom, startup-read) is on.
Exit 0 when all five rows are PASS or a FAIL classified MOD (the criterion: each row gets a verdict); 1 otherwise.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

ITEM = "TITANIC_BODYSIZE_TEST_RACE_1"
HOOKS = "RimMandrake.TitanicCreatures.TitanValidationHooks"
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
T2, T3, CTL = "RM_TestTitanT2", "RM_TestTitanT3", "RM_TestTitanT2Control"
FIELDS = {"giantAnimalsEnabled": True, "wakeEnabled": True, "wakeRoofHolingEnabled": True, "yieldCurveEnabled": True,
          "roofAvoidanceEnabled": True, "corpseSiteEnabled": True}
THICK_ROOF_PENALTY = 2000.0          # Patch_ThickRoofAvoidance.ThickRoofPenalty
ROWS = ("t2_t3_tiers", "t3_corpse_becomes_a_harvest_site", "butcher_yield_curve_reduces_t1_t2_yield",
        "t2_holes_thin_roofs_and_crushes_walls", "thick_roof_route_excluded")


def kv(txt, key):
    m = re.search(r"\b%s=(\S+)" % re.escape(key), txt or "")
    return m.group(1) if m else None


def parse_tiers(txt):
    """TierReport text -> {kind: {tier, adultTier, bodySize, wakeComp}}."""
    out = {}
    for part in (txt or "").split(" | "):
        name = part.split(" ", 1)[0]
        out[name] = {k: kv(part, k) for k in ("tier", "adultTier", "bodySize", "wakeComp")}
    return out


def sites(txt):
    m = re.match(r"sites=(\d+)", txt or "")
    return int(m.group(1)) if m else None


class Run(object):
    def __init__(self, rb, out):
        self.rb, self.out, self.rows, self.log = rb, out, [], []

    def call(self, tool, **kw):
        try:
            r = self.rb.call(tool, kw) or {}
        except Exception as ex:  # noqa: BLE001
            r = {"success": False, "error": "call raised: %s" % ex}
        self.log.append((tool, kw, str(r)[:400]))
        return r

    def hook(self, method, args=""):
        r = self.call("jawa/static_call", type=HOOKS, method=method, args=args)
        txt = str(r.get("result") if r.get("result") is not None else r.get("error") or r.get("message") or r)
        print("    %s(%s) -> %s" % (method, args, txt[:400]), flush=True)
        return r.get("success") is True and not txt.startswith("FAIL"), txt

    def get(self, f):
        return self.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=f).get("value")

    def put(self, f, v):
        # restore-check: ok -- main() snapshots FIELDS first and puts every one back in its finally
        return self.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=f, value=str(v)).get("success")

    def ticks(self, n):
        done = 0
        while done < n:
            k = min(1000, n - done)
            self.call("rimworld/step_game_ticks", ticks=k)
            done += k

    def row(self, rid, status, cls, detail):
        self.rows.append(dict(id=rid, item=ITEM, criterion="A2", status=status, cls=cls, detail=detail))
        print("  %-42s %-10s %-7s %s" % (rid, status, cls, detail[:300]), flush=True)
        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.out), exist_ok=True)
        with open(self.out, "w", encoding="utf-8") as f:
            json.dump(dict(script="titan_test_races_live.py", item=ITEM, when=time.strftime("%Y-%m-%dT%H:%M:%S"), rows=self.rows,
                           calls=self.log), f, indent=1, default=str)


def verdict(rows):
    """0 when every one of ROWS has exactly a PASS or a MOD-classified FAIL; 1 otherwise (UNMEASURED, HARNESS, missing)."""
    got = {r["id"]: r for r in rows}
    for rid in ROWS:
        r = got.get(rid)
        if r is None or not (r["status"] == "PASS" or (r["status"] == "FAIL" and r["cls"] == "MOD")):
            return 1
    return 0


def judge_tiers(rep):
    want = {T2: "T2", T3: "T3", CTL: "None", "Elephant": "T1"}
    bad = [k for k, v in want.items() if rep.get(k, {}).get("tier") != v or rep.get(k, {}).get("adultTier") != v]
    bad += ["%s wakeComp" % k for k in (T2, T3) if rep.get(k, {}).get("wakeComp") != "True"]
    return bad


def judge_yield(t2, ctl):
    """(status, detail) from two ButcherYieldReport lines. Each of n pawns rounds its meat once (GenMath.RoundRandom), so the
    T2 total sits within n of control x factor."""
    try:
        n = int(kv(t2, "n"))
        m2, mc, f = int(kv(t2, "meat")), int(kv(ctl, "meat")), float(kv(t2, "factor"))
        fc = float(kv(ctl, "factor"))
    except (TypeError, ValueError):
        return None, "unparsable: %s || %s" % (t2, ctl)
    d = "T2 meat=%d control meat=%d factor=%.4f (control factor %.4f) expected %.1f +- %d" % (m2, mc, f, fc, mc * f, n)
    if kv(ctl, "tier") != "None" or fc != 1.0:
        return "FAIL", "control is tiered or curved: " + d
    if mc <= 0:
        return None, "control butchered no meat: " + d
    ok = f < 1.0 and m2 < mc and abs(m2 - mc * f) <= n
    return ("PASS" if ok else "FAIL"), d


def judge_roof(t2, ctl):
    try:
        hb, ha = int(kv(t2, "wallHpBefore")), int(kv(t2, "wallHpAfter"))
        cb, ca = int(kv(ctl, "wallHpBefore")), int(kv(ctl, "wallHpAfter"))
    except (TypeError, ValueError):
        return None, "unparsable: %s || %s" % (t2, ctl)
    holed = kv(t2, "roofAfter") == "none"
    crushed = kv(t2, "wallDestroyed") == "True" or ha < hb
    ctl_clean = kv(ctl, "roofAfter") == "RoofConstructed" and kv(ctl, "wallDestroyed") == "False" and ca == cb
    d = "T2 roofAfter=%s wall %d->%d; control roofAfter=%s wall %d->%d" % (kv(t2, "roofAfter"), hb, ha, kv(ctl, "roofAfter"), cb, ca)
    return ("PASS" if holed and crushed and ctl_clean else "FAIL"), d


def judge_thick(t2, ctl):
    try:
        o2, k2 = float(kv(t2, "costOpen")), float(kv(t2, "costThick"))
        oc, kc = float(kv(ctl, "costOpen")), float(kv(ctl, "costThick"))
    except (TypeError, ValueError):
        return None, "unparsable: %s || %s" % (t2, ctl)
    ok = k2 >= THICK_ROOF_PENALTY and k2 > o2 and kc == oc
    return ("PASS" if ok else "FAIL"), "T2 open=%.1f thick=%.1f; control open=%.1f thick=%.1f" % (o2, k2, oc, kc)


def body(R, cells):
    ok, txt = R.hook("TierReport", "%s,%s,%s,Elephant" % (T2, T3, CTL))
    rep = parse_tiers(txt) if ok else {}
    if not ok or any(k not in rep or rep[k].get("tier") is None for k in (T2, T3, CTL)):
        R.row("t2_t3_tiers", "UNMEASURED", "HARNESS", "test races not readable (is mandrake.rm.hugethingstestraces on the list?): "
              + txt[:200])
        return
    bad = judge_tiers(rep)
    R.row("t2_t3_tiers", "FAIL" if bad else "PASS", "MOD", ("wrong: %s; " % bad if bad else "") + txt[:300])

    # R4 / R5 first: they need clean open cells, and R2 leaves corpses and sites behind.
    def probe(method, kind):
        for (x, z) in cells:
            ok, t = R.hook(method, "%s|%d,%d" % (kind, x, z))
            if ok:
                return t
            if "not usable" not in t:
                return None
        return None

    rw2, rwc = probe("RoofWallProbe", T2), probe("RoofWallProbe", CTL)
    st, d = judge_roof(rw2, rwc) if rw2 and rwc else (None, "no usable cell or probe failed: %s || %s" % (rw2, rwc))
    R.row("t2_holes_thin_roofs_and_crushes_walls", st or "UNMEASURED", "MOD" if st else "SITE", d)

    tr2, trc = probe("ThickRoofCostProbe", T2), probe("ThickRoofCostProbe", CTL)
    st, d = judge_thick(tr2, trc) if tr2 and trc else (None, "no usable cell or probe failed: %s || %s" % (tr2, trc))
    R.row("thick_roof_route_excluded", st or "UNMEASURED", "MOD" if st else "SITE", d)

    ok2, y2 = R.hook("ButcherYieldReport", T2)
    okc, yc = R.hook("ButcherYieldReport", CTL)
    st, d = judge_yield(y2, yc) if ok2 and okc else (None, "hook failed: %s || %s" % (y2, yc))
    R.row("butcher_yield_curve_reduces_t1_t2_yield", st or "UNMEASURED", "MOD" if st else "HARNESS", d)

    ok, before = R.hook("SiteReport")
    n0 = sites(before) if ok else None
    (x, z), (x2, z2) = cells[0], cells[1]
    ok3, k3 = R.hook("KillTitanAt", "%s|%d,%d" % (T3, x, z))
    R.ticks(300)
    _, mid = R.hook("SiteReport")
    ok2, k2 = R.hook("KillTitanAt", "%s|%d,%d" % (T2, x2, z2))
    R.ticks(300)
    _, after = R.hook("SiteReport")
    n1, n2 = sites(mid), sites(after)
    if n0 is None or n1 is None or n2 is None or not ok3 or not ok2:
        R.row("t3_corpse_becomes_a_harvest_site", "UNMEASURED", "HARNESS", "sites %r/%r/%r kills %s || %s" % (n0, n1, n2, k3, k2))
        return
    good = "tier=T3" in k3 and "tier=T2" in k2 and n1 == n0 + 1 and n2 == n1
    R.row("t3_corpse_becomes_a_harvest_site", "PASS" if good else "FAIL", "MOD",
          "sites before=%d after T3 kill=%d after T2 kill=%d; %s; %s" % (n0, n1, n2, k3[:120], k2[:120]))


NO_VERDICT = 2      # exit code: the proof never reached the game (not PASS 0, not FAIL 1); the live round reruns/restages


def open_bridge():
    """-> a connected RimBridge, or None after printing why. An unreachable bridge (WSL python3, no game, no log) is a
    harness fact that says nothing about the mod, so the caller exits NO_VERDICT, never FAIL: two A2 'FAIL's
    (2026-11-02T20:21Z, 2026-11-03T06:01Z) were this traceback exiting 1."""
    from rimbridge_client import RimBridge, RimBridgeError, discover_from_log
    try:
        host, port, token = discover_from_log()
        rb = RimBridge(host, port, token, timeout=180.0)
        rb.connect()
        return rb
    except (RimBridgeError, OSError) as e:
        print("UNMEASURED: the bridge could not be reached, no verdict (exit %d): %s" % (NO_VERDICT, str(e)[:400]), flush=True)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="", help="first probe cell X,Z (default: map centre, then offsets)")
    ap.add_argument("--out", default=os.path.join(REPO, "Transient", "modcheck",
                                                  "titan_test_races_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args()
    rb = open_bridge()
    if rb is None:
        return NO_VERDICT
    with rb:
        R = Run(rb, a.out)
        snap = dict((f, R.get(f)) for f in FIELDS)
        if any(v is None for v in snap.values()):
            R.row("settings_snapshot", "UNMEASURED", "HARNESS", "could not read %r" % snap)
            print("rows -> %s" % a.out)
            return 1
        mi = R.call("jawa/map_info")
        size = mi.get("size") or mi.get("mapSize") or {}
        try:
            cx, cz = int(size.get("x")) // 2, int(size.get("z")) // 2
        except (TypeError, ValueError, AttributeError):
            cx = cz = 125
        if a.site:
            cx, cz = [int(v) for v in a.site.split(",")]
        cells = [(cx + dx, cz + dz) for dx, dz in ((0, 0), (12, 0), (-12, 0), (0, 12), (0, -12), (12, 12), (-12, -12), (20, 20))]
        try:
            unset = [f for f, v in FIELDS.items() if not R.put(f, v) or str(R.get(f)).lower() != str(v).lower()]
            custom = R.get("tierThresholdsCustom")
            if str(custom).lower() != "false":
                # a startup-read setting: the expected tiers are the default 4/8/20 ladder, so a custom one cannot be judged here
                R.row("settings_ladder", "UNMEASURED", "SITE", "tierThresholdsCustom=%r: the ladder is not the default 4/8/20" % custom)
            elif unset:
                R.row("settings_set", "UNMEASURED", "HARNESS", "could not set %r: no row can be judged" % unset)
            else:
                body(R, cells)
        finally:
            lost = [f for f, v in snap.items() if not R.put(f, v) or str(R.get(f)).lower() != str(v).lower()]
            if lost:
                print("RESTORE FAILED for %r (wanted %r)" % (lost, dict((f, snap[f]) for f in lost)), flush=True)
            R.save()
    print("rows -> %s" % a.out)
    v = verdict(R.rows)
    print("VERDICT: %s (%d rows)" % ("PASS" if v == 0 else "FAIL", len(R.rows)))
    return v


if __name__ == "__main__":
    sys.exit(main())
