from pathlib import Path
p=Path(__file__).resolve().parents[3]/'src/RimMandrake/HugeThings/northstar/titan_test_races_live.py'
s=p.read_text().replace('R4 t2_holes_thin_roofs_and_crushes_walls RoofWallProbe: a T2 stepping into a roofed wall cell holes RoofConstructed and damages\n                                    or breaks the wood wall; the control leaves both.', 'R4 t2_holes_thin_roofs_and_crushes_walls (compatibility ID): RoofWallProbe assigns Position (teleport), not a path/job.\n                                    T2 holes RoofConstructed in both modes; default Walls/Slots preserves wood wall, legacy\n                                    wake damages it. Forced-out control preserves roof/wall in both. L1 integration only.')
s=s.replace('THICK_ROOF_PENALTY =', 'ROOF_ROW = ROW_PLACEHOLDER\nTHICK_ROOF_PENALTY =',1).replace('ROOF_ROW = ROW_PLACEHOLDER','ROOF_ROW = "t2_holes_thin_roofs_and_crushes_walls"\nROOF_FIELDS = ("giantAnimalsEnabled", "wakeEnabled", "wakeRoofHolingEnabled", "titanClearingEnabled", "wallsSlotsEnabled")')
a=s.index('def judge_roof('); b=s.index('\n\ndef judge_thick',a)
s=s[:a]+'''def judge_roof(t2, ctl, mode=None):
    """Judge measured Position-setter integration, never a walked path/clearing job.

    Mode is raw setting readbacks, not a caller's label. Unknown/missing/malformed
    measurements have no verdict. Wrong measured outcomes FAIL in either mode.
    """
    if not isinstance(mode, dict) or any(not isinstance(mode.get(f), str) or
            mode[f].lower() not in ("true", "false") for f in ROOF_FIELDS):
        return None, "unmeasured/malformed roof-wall mode: %r" % mode
    if any(mode[f].lower() != "true" for f in ROOF_FIELDS if f != "wallsSlotsEnabled"):
        return None, "roof/wake/clearing prerequisites disabled: %r" % mode
    active = all(mode[f].lower() == "true" for f in
                 ("giantAnimalsEnabled", "wakeEnabled", "titanClearingEnabled", "wallsSlotsEnabled"))

    def parse(txt):
        if not isinstance(txt, str):
            return None
        match = re.fullmatch(r"(\\w+) tier=(\\w+) roofAfter=(\\w+) wallHpBefore=(\\d+) "
                             r"wallHpAfter=(\\d+) wallDestroyed=(True|False)", txt)
        if not match:
            return None
        name, tier, roof, before, after, destroyed = match.groups()
        before, after = int(before), int(after)
        gone = destroyed == "True"
        if before <= 0 or not 0 <= after <= before or gone != (after == 0):
            return None
        return name, tier, roof, before, after, gone

    t, c = parse(t2), parse(ctl)
    if t is None or c is None:
        return None, "invalid/non-positive/inconsistent probe data: %s || %s" % (t2, ctl)
    d = ("Position-setter teleport L1 (no path/job); WallsSlotsActive=%s; T2 roof=%s wall %d->%d "
         "destroyed=%s; forced-out control roof=%s wall %d->%d destroyed=%s" %
         (active, t[2], t[3], t[4], t[5], c[2], c[3], c[4], c[5]))
    identity = t[:2] == (T2, "T2") and c[:2] == (CTL, "None")
    wall_ok = (t[4] == t[3] and not t[5]) if active else t[4] < t[3]
    control_ok = c[2] == "RoofConstructed" and c[4] == c[3] and not c[5]
    return ("PASS" if identity and t[2] == "none" and wall_ok and control_ok else "FAIL"), d


def roofwall_row(R, cells):
    """Reusable bounded R4: both actual modes, a T2 + forced-out control per mode.

    Snapshot raw settings before any write; read all mode fields before and after
    each call. Each arm needs both successful probes and a stable measured mode.
    Restoring settings is part of this row's pass condition.
    """
    prior = {f: R.get(f) for f in ROOF_FIELDS}
    arms, errors = [], []
    status = "UNMEASURED"
    if any(not isinstance(v, str) or v.lower() not in ("true", "false") for v in prior.values()):
        R.row(ROOF_ROW, status, "HARNESS", "cannot snapshot raw roof settings: %r" % prior)
        return
    try:
        for slots in (True, False):
            expected = {f: str(slots if f == "wallsSlotsEnabled" else True) for f in ROOF_FIELDS}
            if any(not R.put(f, v) for f, v in expected.items()):
                raise RuntimeError("mode write refused")
            probes = []
            for kind in (T2, CTL):
                before = {f: R.get(f) for f in ROOF_FIELDS}
                ok, txt = False, None
                for x, z in cells:
                    ok, txt = R.hook("RoofWallProbe", "%s|%d,%d" % (kind, x, z))
                    if ok or "not usable" not in txt:
                        break
                after = {f: R.get(f) for f in ROOF_FIELDS}
                stable = before == after and all(isinstance(before.get(f), str) and
                         before[f].lower() == expected[f].lower() for f in ROOF_FIELDS)
                probes.append(dict(kind=kind, ok=ok, raw=txt, before=before, after=after, stable=stable))
            if all(p["ok"] and p["stable"] for p in probes):
                st, detail = judge_roof(probes[0]["raw"], probes[1]["raw"], probes[0]["before"])
            else:
                st, detail = None, "probe failed or actual settings missing/changed"
            arms.append(dict(mode="default Walls/Slots" if slots else "legacy wake", probes=probes,
                             status=st or "UNMEASURED", detail=detail))
        status = "FAIL" if any(a["status"] == "FAIL" for a in arms) else (
                 "PASS" if len(arms) == 2 and all(a["status"] == "PASS" for a in arms) else "UNMEASURED")
    except Exception as ex:
        errors.append(str(ex))
    finally:
        for f, v in prior.items():
            try:
                if not R.put(f, v) or R.get(f) != v:
                    errors.append("raw restore mismatch: " + f)
            except Exception as ex:
                errors.append("restore %s: %s" % (f, ex))
        if errors:
            status = "UNMEASURED"
        R.roofwall_evidence = dict(prior=prior, arms=arms, errors=errors, status=status)
        R.row(ROOF_ROW, status, "MOD" if status in ("PASS", "FAIL") else "HARNESS",
              "Position-setter L1 only; " + json.dumps(R.roofwall_evidence, sort_keys=True))
''' + s[b:]
a=s.index('    rw2, rwc = probe("RoofWallProbe"');b=s.index('\n    tr2, trc',a)
s=s[:a]+'    roofwall_row(R, cells)\n'+s[b:]
p.write_text(s)
