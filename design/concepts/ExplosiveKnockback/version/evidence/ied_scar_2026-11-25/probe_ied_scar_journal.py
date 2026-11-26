"""probe_ied_scar_journal.py - hunt step for RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE (kind C, EXPLORED).

The 0.2.0 IED scar was missing in 1 of 12 blasts (visit 1: sc_blast_show once, probe_ied_scar.py 8 of 8 laid). LayScar
now writes one "scar" journal record per blast (laid, or why the cell refused: RM_KnockbackShow.ScarRefusal) and
RM_Patch_Filth_ScarGone writes "scar_gone" with the calls that removed a scar. This probe sets off N IEDs on soil, a
muffalo beside every other one, the way sc_blast_show does (camera on the pad, Crush damage over its hit points, a
300-tick settle), and prints per pad: the scar at 300 ticks and every scar record of its blast. A miss now names its cause.

    python.exe -c "import sys, runpy; sys.path.insert(0, r'src\\RimMandrake\\Utils'); runpy.run_path(r'<this file, Windows path>', run_name='__main__')"
"""
import json

import scene
from scene import cond as c

GAME = "ArchSmall"
STATION = (20, 20, 110, 48)
N = 24
PADS = {"ied%d" % i: (6 + 12 * (i % 8), 6 + 13 * (i // 8)) for i in range(N)}
BEASTS = {"beast%d" % i: (PADS["ied%d" % i][0] + 3, PADS["ied%d" % i][1]) for i in range(0, N, 2)}
SETTLE = 300
HALF = 4
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"

probe = scene.contract(
    claim="an IED blast on soil lays our crater scar, and the scar is still there 300 ticks later",
    kind="C",
    exposure=c.state("ied0_x", "positionInt") == "gone",
    success=[c.played(SETTLE)],
    forbidden=[],
    end=SETTLE, limit=N * SETTLE + 900)


def rect(pad, h=HALF):
    x, z = PADS[pad]
    return (STATION[0] + x - h, STATION[1] + z - h, 2 * h + 1, 2 * h + 1)


def scars(s, pad):
    return [str(v.v) for v in s.read_many(rect=rect(pad), path="def.defName") if v.state == "ok" and str(v.v).startswith("RM_KnockbackBlast")]


def jlines(s):
    v = s.read("static:" + JOURNAL, "lines")
    return [str(x) for x in v.v] if v.state == "ok" and isinstance(v.v, (list, tuple)) else None


def recs(before, after):
    if before is None or after is None:
        return None
    new = after[len(before):] if after[:len(before)] == before else [x for x in after if x not in set(before)]
    out = []
    for line in new:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") in ("scar", "scar_gone"):
            out.append({k: r[k] for k in ("type", "tick", "at", "def", "laid", "why", "cell", "mode", "by") if k in r})
    return out


with scene.open(GAME, contract=probe, needs={"mods": ["ExplosiveKnockback"], "map": "fresh:quicktest", "calm": "standard"}) as s:
    s.stage(station=STATION,
            terrain={p: dict(rect=(x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1), terrain="Soil") for p, (x, z) in PADS.items()},
            things={p + "_x": dict(thing="TrapIED_HighExplosive", at=xz) for p, xz in PADS.items()},
            cast={b: dict(kind="Muffalo", at=xz) for b, xz in BEASTS.items()})
    out = []
    for pad in sorted(PADS, key=lambda p: int(p[3:])):
        x, z = PADS[pad]
        s.raw("rimworld/jump_camera_to_cell", x=STATION[0] + x, z=STATION[1] + z)
        j0 = jlines(s)
        hp = s.read(pad + "_x", "hitPointsInt")
        s.act.damage(pad + "_x", (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name=pad)
        now = scars(s, pad)
        s.run(until=SETTLE, limit=SETTLE + 120)
        later = scars(s, pad)
        log = recs(j0, jlines(s))
        laid = [r for r in (log or []) if r.get("type") == "scar"]
        if log is None:
            verdict = "JOURNAL_UNREAD"
        elif later:
            verdict = "OK"
        elif not laid:
            verdict = "NO_SCAR_RECORD"
        elif not any(r.get("laid") for r in laid):
            verdict = "REFUSED:" + ",".join(str(r.get("why")) for r in laid)
        else:
            verdict = "LAID_THEN_GONE"
        out.append(verdict.split(":")[0])
        print("PAD %s beast=%s verdict=%s | at 0 ticks %s | at %d %s | journal %s"
              % (pad, ("beast%d" % int(pad[3:])) in BEASTS, verdict, now, SETTLE, later, log))
print("TALLY %s" % {v: out.count(v) for v in sorted(set(out))})
