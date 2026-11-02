#!/usr/bin/env python3
"""Selftest: the PAINT mod list holds only NEEDED mods, each with a reason that is still true.

Owner, by card 2026-10-20 (PAINT_LIST_BUILD_ONLY_THE_NEEDED_MODS): "Likely mid-size, but really only NEEDED mods
incl. our own; Baroque Biomes needed" -- the mods needed to represent the world, the gravship and the player
characters. The list is infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml; the reason for every
member is infrastructure/state/modlists/PAINT.reasons.json. Checks:
  1. reasons name exactly the list's members (no unexplained member, no reason for a non-member);
  2. all six ludeon ids are members (every DLC is assumed);
  3. every reason's need is CORE/WORLD/SHIP/CHARACTERS/TOOL/CLOSURE; a CLOSURE reason's parent is a member and its
     edge still holds: kind=dep -> the parent's About.xml (ours: src, composed rm.biomes: its compose members;
     third party: mod_facts) names the member as a modDependency, or mod_facts records a class_ref/hard_dep edge
     (16 of the 2026-11-01 edges rest on that class_ref record alone; mod_facts is a dated harvest, and it was already
     wrong about rm.biomes' About deps, which is why ours are read from src);
     kind=defref -> the def name still appears in the parent's src Defs/Patches XML (ours only);
  4. dependency closure: every member's hard modDependency (v1.6 included) is a member;
  5. every non-TOOL member is on FULL.LATEST (the dev list) -- a mod retired from the game is retired from PAINT;
  6. no member is a packageId folded into the composed mandrake.rm.biomes.
Probes (the instrument can see), each required to raise its own failure message: an injected unexplained member, a
reason row for a non-member, a bad need value, a dropped ludeon id, a retired (not-on-LATEST) WORLD member, a dropped
dependency, a synthetic v1.6-only About dependency left out of the list, and a stale defref edge. Offline: reads src/, the committed modlists and mod_facts.jsonl only.

    python3 src/RimMandrake/Utils/selftest_paint_list.py
"""
import glob, json, os, sys, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import biomes_compose  # noqa: E402

ML = os.path.join(REPO, "infrastructure/state/modlists")
PAINT = os.path.join(ML, "ModsConfig.PAINT.RULED_2026-10-20.xml")
REASONS = os.path.join(ML, "PAINT.reasons.json")
LATEST = os.path.join(ML, "ModsConfig.FULL.LATEST.xml")
FACTS = os.path.join(REPO, "design/RimMandrake/mod_audit/facts/mod_facts.jsonl")
SRC = os.path.join(REPO, "src")
LUDEON = {"ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
          "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"}
NEEDS = {"CORE", "WORLD", "SHIP", "CHARACTERS", "TOOL", "CLOSURE"}


def modlist(path):
    return [li.text.strip().lower() for li in ET.parse(path).getroot().find("activeMods")]


def about_deps(root):
    d = {(li.findtext("packageId") or "").strip().lower() for li in root.findall("modDependencies/li")}
    for v in root.findall("modDependenciesByVersion"):
        for ver in v:
            if ver.tag == "v1.6":
                d |= {(li.findtext("packageId") or "").strip().lower() for li in ver.findall("li")}
    return d - {""}


def load_world():
    """-> (src_dirs {pid: [dirs]}, deps {pid: set}, facts {pid: row}, folded {pid}) from src/ and mod_facts."""
    dirs, deps = {}, {}
    for a in glob.glob(os.path.join(SRC, "*", "*", "About", "About.xml")):
        try:
            r = ET.parse(a).getroot()
        except ET.ParseError as e:
            print("WARN  unparseable %s (%s): its deps fall back to mod_facts" % (os.path.relpath(a, REPO), e))
            continue
        pid = (r.findtext("packageId") or "").strip().lower()
        if pid:
            dirs.setdefault(pid, []).append(os.path.dirname(os.path.dirname(a)))
            deps.setdefault(pid, set()).update(about_deps(r))
    m = biomes_compose.load_manifest(SRC)
    folded = set(biomes_compose.folded_ids(SRC))
    target = m["about"]["packageId"].lower()
    tier = os.path.join(SRC, biomes_compose.TIER_DIR)
    tdirs, tdeps = [], set()
    for e in biomes_compose.composed_entries(m):
        d = os.path.join(tier, e["source"])
        tdirs.append(d)
        try:
            tdeps |= about_deps(ET.parse(os.path.join(d, "About", "About.xml")).getroot())
        except (OSError, ET.ParseError):
            pass
    dirs[target] = tdirs
    deps[target] = tdeps - folded - {target}
    facts = {}
    for line in open(FACTS, encoding="utf-8"):
        j = json.loads(line)
        facts[j["packageId"].lower()] = j
    return dirs, deps, facts, folded


def hard_deps(pid, w):
    dirs, deps, facts, _ = w
    if pid in deps:
        return deps[pid]
    f = facts.get(pid) or {}
    d = {x.lower() for x in f.get("dependencies") or []}
    d |= {x.lower() for x in (f.get("dependencies_by_version") or {}).get("v1.6") or []}
    return d


def class_edge(child, parent, w):
    """mod_facts records parent -> child as class_ref / hard_dep."""
    for d in (w[2].get(child) or {}).get("dependants_detail") or []:
        if d["packageId"].lower() == parent and {"class_ref", "hard_dep", "hard_dep_v1.6"} & set(d["kinds"]):
            return True
    return False


def names_def(parent, name, w):
    for d in w[0].get(parent, []):
        for dp, _, fn in os.walk(d):
            if "Languages" in dp or "Source" in dp:
                continue
            for f in fn:
                if f.endswith(".xml"):
                    try:
                        if name in open(os.path.join(dp, f), encoding="utf-8", errors="replace").read():
                            return True
                    except OSError:
                        pass
    return False


def check(members, reasons, latest, w):
    """-> list of failure strings."""
    bad = []
    ms = set(members)
    for p in members:
        if p not in reasons:
            bad.append("UNEXPLAINED member %s: add a reason to PAINT.reasons.json or drop it from the list" % p)
    for p in reasons:
        if p not in ms:
            bad.append("REASON for non-member %s: delete the row" % p)
    for p in sorted(LUDEON - ms):
        bad.append("DLC missing: %s (every DLC is assumed)" % p)
    for p, r in reasons.items():
        if p not in ms:
            continue
        need = r.get("need")
        if need not in NEEDS:
            bad.append("%s: need %r not one of %s" % (p, need, sorted(NEEDS)))
        if not (r.get("why") or "").strip():
            bad.append("%s: empty why" % p)
        if need == "CLOSURE":
            par, kind = r.get("of", ""), r.get("kind")
            if par not in ms:
                bad.append("%s: CLOSURE parent %s is not a member (stale: drop %s or re-justify)" % (p, par, p))
            elif kind == "dep":
                if p not in hard_deps(par, w) and not class_edge(p, par, w):
                    bad.append("%s: STALE edge, %s no longer depends on it (drop it or re-justify)" % (p, par))
            elif kind == "defref":
                if not par.startswith("mandrake."):
                    bad.append("%s: defref parent %s is not ours (only our Defs are read)" % (p, par))
                elif not names_def(par, r.get("def", "\0"), w):
                    bad.append("%s: STALE edge, %s's src no longer names %s (drop it or re-justify)"
                               % (p, par, r.get("def")))
            else:
                bad.append("%s: CLOSURE kind %r not dep/defref" % (p, kind))
        if need != "TOOL" and not p.startswith("ludeon.") and p not in latest:
            bad.append("%s: not on FULL.LATEST (retired from the game => retire from PAINT, or tag TOOL)" % p)
    for p in members:
        for q in sorted(hard_deps(p, w)):
            if q not in ms:
                bad.append("CLOSURE gap: %s hard-depends on %s, which is not a member" % (p, q))
        if p in w[3]:
            bad.append("%s is folded into mandrake.rm.biomes; it is not a mod of its own" % p)
    return bad


def main():
    members = modlist(PAINT)
    doc = json.load(open(REASONS, encoding="utf-8"))
    reasons = doc["members"]
    latest = set(modlist(LATEST))
    w = load_world()
    fails = 0
    bad = check(members, reasons, latest, w)
    print("%s  real list: %d members, %d failure(s)" % ("PASS" if not bad else "FAIL", len(members), len(bad)))
    for b in bad:
        print("   ", b)
    fails += bool(bad)
    # probes: each must FAIL with its OWN message, or the instrument cannot see what it claims to check
    probes = []  # (name, failures, substring that must appear in one failure)
    probes.append(("unexplained member", check(members + ["probe.unexplained"], reasons,
                                               latest | {"probe.unexplained"}, w),
                   "UNEXPLAINED member probe.unexplained"))
    extra = dict(reasons, **{"probe.nonmember": {"need": "WORLD", "why": "probe"}})
    probes.append(("reason for non-member", check(members, extra, latest, w), "REASON for non-member probe.nonmember"))
    some = next(p for p, r in reasons.items() if r.get("need") == "WORLD" and p in members)
    badneed = dict(reasons, **{some: dict(reasons[some], need="BOGUS")})
    probes.append(("bad need value on %s" % some, check(members, badneed, latest, w), "%s: need 'BOGUS'" % some))
    lud = "ludeon.rimworld.odyssey"
    probes.append(("dropped %s" % lud, check([m for m in members if m != lud],
                                             {k: v for k, v in reasons.items() if k != lud}, latest, w),
                   "DLC missing: %s" % lud))
    probes.append(("retired WORLD member", check(members + ["probe.retired"],
                                                 dict(reasons, **{"probe.retired": {"need": "WORLD", "why": "probe"}}),
                                                 latest, w),
                   "probe.retired: not on FULL.LATEST"))
    dep = next(p for p, r in reasons.items() if r.get("kind") == "dep" and p in hard_deps(r["of"], w))
    probes.append(("dropped dependency %s" % dep, check([m for m in members if m != dep],
                                                      {k: v for k, v in reasons.items() if k != dep}, latest, w),
                   "CLOSURE gap: %s hard-depends on %s" % (reasons[dep]["of"], dep)))
    # a v1.6-only About dependency (no plain modDependencies entry) must reach the closure check
    host = next(p for p in members if p in w[1] and p.startswith("mandrake."))
    v16 = ET.fromstring("<ModMetaData><modDependencies/><modDependenciesByVersion><v1.5><li><packageId>"
                        "probe.v15only</packageId></li></v1.5><v1.6><li><packageId>Probe.V16Only</packageId></li>"
                        "</v1.6></modDependenciesByVersion></ModMetaData>")
    got = about_deps(v16)
    w16 = (w[0], dict(w[1], **{host: w[1][host] | got}), w[2], w[3])
    res16 = check(members, reasons, latest, w16)
    if "probe.v15only" in got:
        res16 = []  # a v1.5-only dep leaking into the 1.6 closure is its own defect: make the probe fail
    probes.append(("v1.6-only About dependency on %s" % host, res16,
                   "CLOSURE gap: %s hard-depends on probe.v16only" % host))
    dref = next(p for p, r in reasons.items() if r.get("kind") == "defref" and p in members)
    stale = dict(reasons)
    stale[dref] = dict(reasons[dref], **{"def": "RM_ProbeNoSuchDef_ZZ"})
    probes.append(("stale defref %s" % dref, check(members, stale, latest, w), "%s: STALE edge" % dref))
    for name, res, want in probes:
        ok = any(want in b for b in res)
        print("%s  probe %s -> %d failure(s), wanted %r" % ("PASS" if ok else "FAIL", name, len(res), want))
        fails += not ok
    print("RESULT", "PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
