"""probe_ied_scar.py - hunt step for RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE (kind C, EXPLORED).

Question: when an IED blast on soil leaves no scar (1 of 3 runs of sc_blast_show, visit 1), was the scar never laid
(FilthMaker.TryMakeFilth refused in LayScar) or laid and then removed inside the 300-tick settle?
What the answer changes: "never laid" points at the cell the postfix writes to; "laid, then gone" points at whatever
removes a 1-thickness filth (SteadyEnvironmentEffects, cleaning, a spawn that wipes filth).

Eight IED pads on soil, 12 cells apart, four with a muffalo two cells off the centre (the candidate: blood on the cell).
Each pad: damage the IED to set it off; read our scar and every def on the centre cell at once (0 ticks); run 300 ticks;
read again. Prints one line per pad and a tally.

    python.exe src\\RimMandrake\\Utils\\scene.py explore design\\concepts\\ExplosiveKnockback\\version\\in_game\\visit_1\\scripts\\probe_ied_scar.py
"""
import scene
from scene import cond as c

GAME = "ArchSmall"
STATION = (20, 20, 110, 30)
N = 8
PADS = {"ied%d" % i: (6 + 12 * (i % 8), 8 + 14 * (i // 8)) for i in range(N)}
BEASTS = {"beast%d" % i: (PADS["ied%d" % i][0] + 2, PADS["ied%d" % i][1]) for i in range(0, N, 2)}
SETTLE = 300
HALF = 4

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


def defs_in(s, r):
    return [str(v.v) for v in s.read_many(rect=r, path="def.defName") if v.state == "ok"]


def scars(names):
    return [n for n in names if n.startswith("RM_KnockbackBlast")]


with scene.open(GAME, contract=probe, needs={"mods": ["ExplosiveKnockback"], "map": "fresh:quicktest", "calm": "standard"}) as s:
    s.stage(station=STATION,
            terrain={p: dict(rect=(x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1), terrain="Soil") for p, (x, z) in PADS.items()},
            things={p + "_x": dict(thing="TrapIED_HighExplosive", at=xz) for p, xz in PADS.items()},
            cast={b: dict(kind="Muffalo", at=xz) for b, xz in BEASTS.items()})
    out = []
    for pad in sorted(PADS, key=lambda p: int(p[3:])):
        x, z = PADS[pad]
        s.raw("rimworld/jump_camera_to_cell", x=x, z=z)
        centre = (STATION[0] + x, STATION[1] + z, 1, 1)
        before = defs_in(s, centre)
        hp = s.read(pad + "_x", "hitPointsInt")
        s.act.damage(pad + "_x", (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name=pad)
        now_c, now_pad = defs_in(s, centre), scars(defs_in(s, rect(pad)))
        s.run(until=SETTLE, limit=SETTLE + 120)
        later_c, later_pad = defs_in(s, centre), scars(defs_in(s, rect(pad)))
        beast = ("beast%d" % int(pad[3:])) in BEASTS
        verdict = "OK" if later_pad else ("NEVER_LAID" if not now_pad else "LAID_THEN_GONE")
        out.append(verdict)
        print("PAD %s beast=%s verdict=%s | centre before %s | at 0 ticks: centre %s, pad scars %s | at %d: centre %s, pad scars %s"
              % (pad, beast, verdict, before, now_c, now_pad, SETTLE, later_c, later_pad))
    w = s.raw("jawa/quiet_site", action="read") or {}
    print("WEATHER/CALM %s" % {k: w.get(k) for k in ("weather", "controls") if k in w})
print("TALLY %s" % {v: out.count(v) for v in sorted(set(out))})
