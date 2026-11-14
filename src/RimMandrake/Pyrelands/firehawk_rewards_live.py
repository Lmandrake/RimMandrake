"""Live tests of the fire-hawk's hunt rewards and its map-wide ember carry, built WITH their items (owner, 2026-11-13: "Yes,
from now on, we build the test at the same time as the item, both offline and online versions. then they get consolidated
into the formal tests."). Chains of the Pyrelands suite (validation.py registers them through register()):

  firehawk_first_sighting_letter   RIMMANDRAKE_ANNOUNCE_FIREHAWK_EMBER_LETTER_ON_FIRST_SIGHTING: a staged hawk carries an ember
                                   on the home map, unfogged -> exactly one ThreatSmall letter pointing at it; a second hawk
                                   carrying -> still one; toggle off and re-armed -> none.
  firehawk_crestfeather_yield      the crestfeather trophy item (its id keeps the filed spelling, see
                                   selftest_pyrelands_firehawk_crestfeather.py): 400 fire-hawks butchered through the patched
                                   Pawn.ButcherProducts under a fixed seed -> the 35 % yield within 4 sigma, and the trophy's
                                   Beauty and MarketValue as the running game computes them equal the def's.
  firehawk_mapwide_carry           RIMMANDRAKE_TRIPLE_FIREHAWK_REACH_PREFERS_FARTHEST_FUEL (owner, 2026-11-13: "Carry distance
                                   should actually be anywhere on the map, unlimited. To the largest fuel source easily
                                   found."): the map's plants cleared, a fire beside the hawk, a small patch near and a large
                                   one far away, each ringed by a firebreak -> the ember's drop cell (CompFireHawkSpread's
                                   lastDropCell, a STATE read) lies in the far patch.

Flight is never watched or pictured (flyers are not live-tested visually unattended): every verdict here is a state read
(jawa/comp_read, jawa/letter_list, jawa/static_call). UNRUN as written 2026-11-13 (no game in the building run). Run:
    modcheck run Pyrelands --chains firehawk_first_sighting_letter,firehawk_crestfeather_yield,firehawk_mapwide_carry
`python3 <this file> --selftest` checks the pure readers offline.
"""
import math
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SIGHT = "RimMandrake.Pyrelands.GameComponent_RM_FireHawkSighting"
TROPHY_PATCH = "RimMandrake.Pyrelands.ButcherTrophyPatch"
TROPHY = "RM_PristineFirehawkCrestfeather"
YIELD_N, YIELD_SEED = 400, 20261113
LOOK_WAIT = 300        # one sighting look is every 250 ticks (RM_FireHawkRewardsKernel.SightingLookIntervalTicks)


def keyed(key):
    root = ET.parse(os.path.join(HERE, "Languages", "English", "Keyed", "Pyrelands.xml")).getroot()
    el = root.find(key)
    return el.text if el is not None else None


def trophy_def_stats():
    """-> (label, Beauty, MarketValue, chance) from the def files on disk: the live reads must equal these."""
    d = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Items", TROPHY + ".xml")).getroot().find("ThingDef")
    hawk = [x for x in ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_PyrelandsFauna.xml")).getroot().iter("ThingDef")
            if x.findtext("defName") == "RM_FireHawk"][0]
    ext = [li for li in hawk.iter("li") if (li.get("Class") or "").endswith("RM_ButcherTrophyExtension")][0]
    return (d.findtext("label"), float(d.findtext("statBases/Beauty")), float(d.findtext("statBases/MarketValue")),
            float(ext.findtext("chance")))


def parse_kv(text):
    """'YIELD n=400 trophies=140 beauty=40 label=pristine firehawk crestfeather' -> dict; the label runs to the end."""
    out = {}
    if not isinstance(text, str):
        return out
    m = re.search(r"\blabel=(.*)$", text)
    if m:
        out["label"] = m.group(1).strip()
        text = text[:m.start()]
    for k, v in re.findall(r"(\w+)=(\S+)", text):
        out[k] = v
    return out


def yield_verdict(kv, n, chance, beauty, value, label):
    """-> (ok, why). Pure; --selftest drives it."""
    if not kv or "trophies" not in kv:
        return None, "no YIELD reply"
    got = int(kv["trophies"])
    sigma = math.sqrt(n * chance * (1 - chance))
    if got == 0:
        return False, "0 crestfeathers from %d hawks: the ButcherProducts patch is not live" % n
    if abs(got - n * chance) > 4 * sigma:
        return False, "%d crestfeathers from %d hawks, expected %.0f +- %.0f (4 sigma)" % (got, n, n * chance, 4 * sigma)
    if abs(float(kv.get("beauty", "nan")) - beauty) > 1e-3:
        return False, "in-game Beauty %s, the def says %s" % (kv.get("beauty"), beauty)
    if abs(float(kv.get("marketValue", "nan")) - value) > 1e-3:
        return False, "in-game MarketValue %s, the def says %s" % (kv.get("marketValue"), value)
    if kv.get("label") != label:
        return False, "in-game label %r, ruled %r" % (kv.get("label"), label)
    return True, "%d/%d crestfeathers (%.1f %%), Beauty %s, MarketValue %s" % (got, n, 100.0 * got / n, kv["beauty"], kv["marketValue"])


def parse_cell(text):
    """comp_read renders an IntVec3 as '(x, y, z)' -> (x, z), or None (Invalid is (-1000, -1000, -1000))."""
    m = re.search(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", str(text or ""))
    if not m or int(m.group(1)) < 0:
        return None
    return int(m.group(1)), int(m.group(3))


def in_rect(cell, rect):
    x, z, w, h = rect
    return cell is not None and x <= cell[0] < x + w and z <= cell[1] < z + h


def register(suite, V):
    """Adds the three chains to the Pyrelands suite. V is validation.py's namespace (its helpers and constants)."""

    def letters(t, label):
        r = t.bridge_call("jawa/letter_list") or {}
        if not isinstance(r, dict) or r.get("success") is False:
            V._unmeasured(t, "jawa/letter_list gave no answer: %r" % (r,))
        # the label comes back as a TaggedString object ({"RawText": ...}), never a bare string: compare its text (live
        # 2026-11-13, a sent letter read as 0 letters)
        text = lambda v: v.get("RawText") if isinstance(v, dict) else v
        return [l for l in (r.get("letters") or []) if text(l.get("label")) == label]

    def comp(t, hawk, members):
        r = t.bridge_call("jawa/comp_read", thing=hawk, comp="CompFireHawkSpread", members=members) or {}
        return (r.get("values") or {}) if isinstance(r, dict) else {}

    def carrying(t, hawk):
        return str(comp(t, hawk, "CarryingEmber").get("CarryingEmber", "")).strip().lower() == "true"

    def until_carrying(t, hawk, samples=100):
        for _ in range(samples):          # every 60 ticks, as the firehawk chain: a sortie is short
            V._wait(t, 60)
            if carrying(t, hawk):
                return True
        return False

    def static(t, typ, method, args=""):
        r = t.bridge_call("jawa/static_call", type=typ, method=method, args=args) or {}
        return r.get("result") if isinstance(r, dict) and r.get("success") else None

    def stage_fire(t, rect):
        x, z = t.anchor
        V._plants(t, "RM_FE_Plant_EmberGrass", rect)
        V._fire(t, (x - 2, z - 2, 4, 4), size=0.5)

    @suite.chain("firehawk_first_sighting_letter")
    @V._teardown(fire=True)
    def firehawk_first_sighting_letter(t):
        V._pad(t, V.PAD_HAWK)
        t.clear_area(size=V.TEST_SIZE)
        rect = V._rect(t)
        x, z = t.anchor
        label = keyed("RM_FireHawkSightedLabel")
        with V._comp(t, "firehawk_first_sighting_letter_once"):
            V._set(t, {"burnLineEnabled": True, "fireHawkSpreadEnabled": True, "fireHawkSightingLetterEnabled": True})
            t.bridge_call("jawa/set_fog", action="unfog", rect=V._whole(t))
            V._firebreak(t, rect)
            V._soil(t, rect)
            V._note(t, "rearm", static(t, SIGHT, "ProbeRearmForLiveTest"))
            base = len(letters(t, label))
            stage_fire(t, rect)
            a = V._spawn_wild(t, "RM_FireHawk", x + 8, z)
            if V._live(t) and not until_carrying(t, a):
                V._unmeasured(t, "hawk %s never carried an ember in 6000 ticks beside a live fire: no sighting to letter" % a)
            V._wait(t, LOOK_WAIT)
            got = letters(t, label)
            V._note(t, "letters after the first carrying hawk", got)
            V._note(t, "state", static(t, SIGHT, "ProbeState"))
            if V._live(t):
                if len(got) - base != 1:
                    V._fail("%d new %r letters after hawk %s carried an ember on the home map, ruled exactly 1" % (len(got) - base, label, a))
                new = got[-1]
                if new.get("defName") != "ThreatSmall":
                    V._fail("the letter is %s, ruled ThreatSmall" % new.get("defName"))
                if a not in (new.get("lookTargetIds") or []):
                    V._fail("the letter does not point at hawk %s: %r" % (a, new.get("lookTargetIds")))
            # a second hawk, a fresh fire: the letter is once per game
            stage_fire(t, rect)
            b = V._spawn_wild(t, "RM_FireHawk", x - 8, z)
            if V._live(t) and not until_carrying(t, b):
                V._unmeasured(t, "the second hawk %s never carried an ember: the once-only half is unjudged" % b)
            V._wait(t, LOOK_WAIT)
            if V._live(t) and len(letters(t, label)) - base != 1:
                V._fail("a second carrying hawk (%s) sent another letter: %d in all" % (b, len(letters(t, label)) - base))
        with V._comp(t, "firehawk_first_sighting_letter_toggle_off", toggle="fireHawkSightingLetterEnabled"):
            V._set(t, {"fireHawkSightingLetterEnabled": False})
            V._note(t, "rearm", static(t, SIGHT, "ProbeRearmForLiveTest"))
            before = len(letters(t, label))
            stage_fire(t, rect)
            c = V._spawn_wild(t, "RM_FireHawk", x, z + 8)
            if V._live(t) and not until_carrying(t, c):
                V._unmeasured(t, "hawk %s never carried an ember with the letter off: unjudged" % c)
            V._wait(t, LOOK_WAIT)
            state = static(t, SIGHT, "ProbeState")
            V._note(t, "state with the toggle off", state)
            if V._live(t) and (len(letters(t, label)) != before or "announced=True" in str(state)):
                V._fail("the toggle is off and a letter was sent (%d new; %s)" % (len(letters(t, label)) - before, state))
        t.screenshot(rect=rect)

    @suite.chain("firehawk_crestfeather_yield")
    def firehawk_crestfeather_yield(t):
        label, beauty, value, chance = trophy_def_stats()
        with V._comp(t, "firehawk_crestfeather_yield_and_stats", beyond_toggle=True):
            reply = static(t, TROPHY_PATCH, "ProbeButcherYield", "%d|%d" % (YIELD_N, YIELD_SEED))
            V._note(t, "butcher yield", reply)
            if not V._live(t):
                return
            if not str(reply or "").startswith("YIELD"):
                V._unmeasured(t, "ProbeButcherYield gave no YIELD line: %r" % (reply,))
            ok, why = yield_verdict(parse_kv(reply), YIELD_N, chance, beauty, value, label)
            if ok is None:
                V._unmeasured(t, why)
            if not ok:
                V._fail(why)

    @suite.chain("firehawk_mapwide_carry")
    @V._teardown(fire=True)
    def firehawk_mapwide_carry(t):
        V._pad(t, V.PAD_HAWK)
        x, z = t.anchor
        sx, sz = V._map_size(t)
        source = (x - 4, z - 4, 8, 8)
        near = (x + 12, z - 3, 6, 6)                       # inside the old 18-cell carry: must NOT win
        far = (sx - 50, sz // 2 - 15, 30, 30)              # the largest fuel on the map, ~150 cells off on a 250 map
        with V._comp(t, "firehawk_ember_lands_in_the_largest_far_patch"):
            V._set(t, {"burnLineEnabled": False, "fireHawkSpreadEnabled": True})
            # in 20-row strips: one whole-map CLEAR outran the bridge's 30 s call limit (live 2026-11-13, chain UNMEASURED)
            for sz0 in range(0, sz, 20):
                t.bridge_call("jawa/set_plants", ops="CLEAR:%d,%d,%d,%d" % (0, sz0, sx, min(20, sz - sz0)))
            t.bridge_call("jawa/set_fog", action="unfog", rect=V._whole(t))
            for r in (source, near, far):
                V._firebreak(t, r)
                V._soil(t, r)
                V._plants(t, "RM_FE_Plant_EmberGrass", r)
            V._fire(t, (x - 2, z - 2, 4, 4), size=0.5)
            hawk = V._spawn_wild(t, "RM_FireHawk", x - 10, z)
            drop, seen_job = None, False
            for _ in range(200):                           # 12000 ticks: a map-length carry is long
                V._wait(t, 60)
                seen_job = seen_job or V._job_of(t, hawk) == V.FIRE_HAWK_JOB
                vals = comp(t, hawk, "drops,lastDropCell,lastDropLit")
                if str(vals.get("drops", "0")).strip() not in ("", "0"):
                    drop = parse_cell(vals.get("lastDropCell"))
                    V._note(t, "first drop", vals)
                    break
            V._note(t, "patches", {"source": source, "near": near, "far": far, "map": (sx, sz)})
            if not V._live(t):
                return
            if drop is None:
                if seen_job:
                    V._fail("hawk %s took the ember job and dropped nothing in 12000 ticks" % hawk)
                V._unmeasured(t, "hawk %s never started an ember sortie beside a live fire" % hawk)
            if not in_rect(drop, far):
                where = "the near patch" if in_rect(drop, near) else "the source patch" if in_rect(drop, source) else "outside every patch"
                V._fail("the ember landed at %s, in %s; the largest fuel is the far patch %r" % (drop, where, far))


def selftest():
    bad = []
    kv = parse_kv("YIELD n=400 seed=1 trophies=140 products=1200 chance=0.35 beauty=40 marketValue=350 stackLimit=5 label=pristine firehawk crestfeather")
    if kv.get("label") != "pristine firehawk crestfeather" or kv.get("trophies") != "140":
        bad.append("parse_kv %r" % kv)
    cases = [
        (dict(kv), True),
        (dict(kv, trophies="0"), False),
        (dict(kv, trophies="60"), False),
        (dict(kv, beauty="-4"), False),
        (dict(kv, marketValue="180"), False),
        (dict(kv, label="pristine emberhawk crestfeather"), False),
        ({}, None),
    ]
    for k, want in cases:
        ok, why = yield_verdict(k, 400, 0.35, 40.0, 350.0, "pristine firehawk crestfeather")
        if ok is not want:
            bad.append("yield_verdict %r -> %r (%s), want %r" % (k, ok, why, want))
    if parse_cell("(12, 0, 200)") != (12, 200) or parse_cell("(-1000, -1000, -1000)") is not None or parse_cell(None) is not None:
        bad.append("parse_cell")
    if not in_rect((5, 5), (0, 0, 6, 6)) or in_rect((6, 5), (0, 0, 6, 6)) or in_rect(None, (0, 0, 6, 6)):
        bad.append("in_rect")
    if keyed("RM_FireHawkSightedLabel") != "Fire-hawk carrying an ember":
        bad.append("keyed label %r" % keyed("RM_FireHawkSightedLabel"))
    if trophy_def_stats() != ("pristine firehawk crestfeather", 40.0, 350.0, 0.35):
        bad.append("trophy_def_stats %r" % (trophy_def_stats(),))
    for b in bad:
        print("SELFTEST FAIL", b)
    print("firehawk_rewards_live selftest: %s" % ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    import sys
    sys.exit(selftest() if sys.argv[1:2] == ["--selftest"] else (print(__doc__) or 0))
