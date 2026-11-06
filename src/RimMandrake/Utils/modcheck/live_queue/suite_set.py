"""suite_set: which modcheck suites the situational pass runs, derived from disk (SUITE_REGISTRY_WIDEN_FORTY_SEVEN_STRAYS).

    python3 src/RimMandrake/Utils/modcheck/live_queue/suite_set.py            the table: every disk suite, IN or OUT, why
    python3 src/RimMandrake/Utils/modcheck/live_queue/suite_set.py --check    exit 0 when jobs.suite_mods() and
                                                                              rollout_gate read exactly this set

Until 2026-11-06 jobs.suite_mods() read the modcheck status registry (modcheck_status.json), which only knows a mod
after someone ran it: on 2026-11-02 the registry offered 57 suites while 105 were on disk. The set is now derived:

  * a SUITE is a mod folder src/Rim*/<Mod>/ whose validation.py declares a module-level `suite =` (what runner loads);
  * a suite COMPOSES onto the minimal list (prep_wsl.py: MINIMAL + every suite's closure, one game session) unless
      - its walk doc (design/validation_walks/<Tier>/<Mod>.md, any tier) declares `list: full` -- its own author says the
        minimal list cannot exercise it, so on the shared minimal session it would only fail for want of donors; or
      - its composed closure (runner.composed_ids -- About.xml hard dependencies, the mod, its tier closure --
        followed through every one of our own mods it names, transitive()) names a
        packageId that is neither Ludeon (base game and every DLC, always assumed), on ModsConfig.MINIMAL.xml, nor one
        of our own mods under src/ -- a donor the minimal list does not carry;
  * a suite whose About.xml or walk doc cannot be read stays IN, so situational_rerun reports the load error instead
    of the set hiding it.

The OUT suites still run on their own lists through `modcheck run <Mod>`; they are only absent from the one shared
minimal session. Pure functions take `root`, so the selftest builds a fake tree.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from common import ROOT   # noqa: E402

SUITE_RE = re.compile(r"^suite\s*=", re.M)
LIST_RE = re.compile(r"^list:\s*(.*)$", re.M | re.I)
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
MINIMAL_REL = os.path.join("infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")


def disk_suites(root=ROOT):
    """{mod folder name: tier} for every src/Rim*/<Mod>/validation.py with a module-level `suite`."""
    out = {}
    for p in sorted(glob.glob(os.path.join(root, "src", "Rim*", "*", "validation.py"))):
        mod_dir = os.path.dirname(p)
        try:
            with open(p, encoding="utf-8") as f:
                if not SUITE_RE.search(f.read()):
                    continue
        except OSError:
            pass                    # unreadable: still a suite the pass owes
        out[os.path.basename(mod_dir)] = os.path.basename(os.path.dirname(mod_dir))
    return out


def minimal_ids(root=ROOT):
    """Lower-cased packageIds of ModsConfig.MINIMAL.xml's <activeMods> (parsed, never grepped)."""
    am = ET.parse(os.path.join(root, MINIMAL_REL)).getroot().find("activeMods")
    return {(li.text or "").strip().lower() for li in (am if am is not None else [])} - {""}


def walk_list(mod, tier, root=ROOT):
    """The walk doc's `list:` header text, or None when there is no walk doc or no such line. The doc's own tier first,
    then any tier: a mod that changed tier keeps its old walk doc (LanternDeeps, WeatherSuite on 2026-11-06)."""
    walks = os.path.join(root, "design", "validation_walks")
    p = os.path.join(walks, tier, mod + ".md")
    if not os.path.isfile(p):
        p = next(iter(sorted(glob.glob(os.path.join(walks, "Rim*", mod + ".md")))), p)
    try:
        with open(p, encoding="utf-8") as f:
            m = LIST_RE.search(f.read())
    except OSError:
        return None
    return m.group(1).strip() if m else None


def classify(mod, list_line, closure, minimal, ours):
    """-> (composes, reason). Pure. `closure` is the composed packageId list, or an Exception when it would not read."""
    if list_line is not None and re.match(r"full\b", list_line, re.I):
        return False, "walk doc declares `list: %s`" % list_line[:60]
    if isinstance(closure, Exception):
        return True, "closure unreadable (%s): kept, so the pass reports it" % closure
    foreign = [p for p in closure if not p.startswith("ludeon.") and p not in minimal and p not in ours]
    if foreign:
        return False, "closure needs %s, not on the minimal list" % ", ".join(foreign)
    return True, "minimal + our own mods" + ("" if list_line else " (no walk-doc list: line)")


def transitive(mod, direct, ours):
    """Every packageId `mod` needs loaded, dependencies before dependents, ACROSS our own mods: runner.composed_ids is
    one level deep, so SithLine -> Armoury -> two donor frameworks read as clean (review, 2026-11-06). Pure:
    `direct(name)` -> composed packageIds (raises when unreadable: the caller keeps the suite IN and says so);
    `ours` maps packageId -> our deployable name. A cycle is cut at the first repeat."""
    out, seen = [], set()

    def walk(name):
        if name in seen:
            return
        seen.add(name)
        for pid in direct(name):
            sub = ours.get(pid)
            if sub and sub != name:
                walk(sub)
            if pid not in out:
                out.append(pid)
    walk(mod)
    return out


def _biomes_target():
    """(target name, {folded source folder}) of the composed Biomes mod, or (None, set())."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
    import biomes_compose
    src = os.path.join(ROOT, "src")
    m = biomes_compose.load_manifest(src)
    return (m["target"], set(biomes_compose.folded_sources(src))) if m else (None, set())


def direct_fn():
    """runner.composed_ids, plus the composed Biomes target (a name with no folder): its closure is every folded
    source's, so a suite that needs mandrake.rm.biomes also needs what the folded mods depend on (review, 2026-11-06)."""
    import runner
    target, sources = _biomes_target()

    def direct(name):
        if target is not None and name == target:
            own = [p for p, n in runner.src_mods_by_id().items() if n == target]
            out = []
            for src in sorted(sources):
                out.extend(p for p in runner.composed_ids(src) if p not in out and p not in own)
            return out + own        # every folded source's deps BEFORE the composed mod itself
        return runner.composed_ids(name)
    return direct


def closure(mod):
    """transitive() over the real tree."""
    import runner
    return transitive(mod, direct_fn(), runner.src_mods_by_id())


def deploy_plans(mod):
    """The deploy_custom_mods.py argvs (without --apply) that put `mod` and every one of OUR mods in its transitive
    closure in the game folder: runner.deploy_args_for per folder, one `--compose biomes` for the composed target."""
    import runner
    ours = runner.src_mods_by_id()
    target, _sources = _biomes_target()
    names = [mod] + [ours[p] for p in closure(mod) if p in ours and ours[p] != mod]
    plans = []
    for n in names:
        argv = ["--compose", "biomes"] if n == target else runner.deploy_args_for(n)
        if argv and argv not in plans:
            plans.append(argv)
    return plans


def table(root=ROOT):
    """[(mod, tier, composes, reason)] for every disk suite, sorted by mod. The closures are read from the real tree
    (runner has no root); `root` steers the suite census, walk docs and MINIMAL."""
    import runner
    minimal = minimal_ids(root)
    ours_map = runner.src_mods_by_id(root)
    ours = set(ours_map)
    direct = direct_fn()
    rows = []
    for mod, tier in sorted(disk_suites(root).items()):
        try:
            cl = transitive(mod, direct, ours_map)
        except Exception as e:                                  # noqa: BLE001
            cl = e
        ok, why = classify(mod, walk_list(mod, tier, root), cl, minimal, ours)
        rows.append((mod, tier, ok, why))
    return rows


def situational_suites(root=ROOT):
    """The sorted suites the shared minimal session runs."""
    return [m for m, _t, ok, _w in table(root) if ok]


def main(argv):
    rows = table()
    ins = [r for r in rows if r[2]]
    print("%d disk suites: %d compose onto the minimal list, %d run only on their own list" %
          (len(rows), len(ins), len(rows) - len(ins)))
    for mod, tier, ok, why in rows:
        if "--check" not in argv or not ok:
            print("  %-4s %-26s %-12s %s" % ("IN" if ok else "OUT", mod, tier, why))
    if "--check" not in argv:
        return 0
    import jobs
    import rollout_gate
    probs = []
    want = [r[0] for r in ins]
    got = jobs.suite_mods()
    if got != want:
        probs.append("jobs.suite_mods() differs: extra %s, missing %s" % (sorted(set(got) - set(want)),
                                                                          sorted(set(want) - set(got))))
    if sorted(rollout_gate.disk_suites()) != want:
        probs.append("rollout_gate.disk_suites() does not read this set")
    if len(rows) != len(disk_suites()) or not all(r[3] for r in rows):
        probs.append("a disk suite went unclassified")
    if not ins:
        probs.append("an empty set: the instrument cannot see the suites")
    for p in probs:
        print("FAIL " + p)
    print("PASS suite_set --check" if not probs else "FAIL suite_set --check")
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
