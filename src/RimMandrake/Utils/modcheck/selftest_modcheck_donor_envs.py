"""selftest_modcheck_donor_envs -- MODCHECK_DONOR_ENVIRONMENTS_1, offline.

Armoury and Wrecked Machines each keep their modcheck test environment in `modcheck_env.py` beside their
validation.py. This proves, without the game:
  1. the file exists beside validation.py, and TIERS[<mod>] carries exactly its ids (plus the bridge) and opts in
     with `modcheck_closure`, so `runner.closure_ids` composes them on `modcheck run <Mod>`;
  2. every hard `<modDependencies>` id of the mod's About.xml, and the mod itself, is in the list;
  3. Armoury's list forbids ModularWeapons2 and carries no retired KotOR donor;
  4. when the installed mods are readable (Archmagi), each tier closes with nothing missing and no refusal, and
     every non-DLC member of the closure is already named in modcheck_env.py (the list IS the closure);
  5. `compose_test_list` compares packageIds case-blind, so MINIMAL's `Neronix17.OuterRim.Core` is not added twice;
  6. live-proof A2 ("VFEFactory + VE Framework, no other VE mod") needs both and names every installed Vanilla
     Expanded packageId but those two as a --without, and live_def_check.condition reads UNMEASURED on a running
     load that holds any one of them.

    python3 src/RimMandrake/Utils/modcheck/selftest_modcheck_donor_envs.py
"""
import os
import re
import shlex
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, UTILS)

import modset_builder  # noqa: E402
import runner  # noqa: E402
import live_def_check  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


MODS = (("Armoury", "src/RimStarWars/Armoury", "armoury"),
        ("WreckedMachines", "src/RimMandrake/WreckedMachines", "wreckedmachines"))


def t_env_files_and_tiers():
    for name, rel, tier in MODS:
        mod_dir = os.path.join(ROOT, rel)
        env = rel + "/modcheck_env.py"
        check("%s: modcheck_env.py beside validation.py" % name,
              os.path.isfile(os.path.join(ROOT, env)) and os.path.isfile(os.path.join(mod_dir, "validation.py")))
        ids, forbid = modset_builder.mod_env(env)
        t = modset_builder.TIERS.get(tier)
        check("%s: tier %r exists" % (name, tier), t is not None)
        if t is None:
            continue
        check("%s: tier carries exactly the env ids plus the bridge" % name,
              t["want"] == [modset_builder.BRIDGE] + ids, t["want"])
        check("%s: tier opts in to the modcheck closure" % name, t.get("modcheck_closure") is True)
        check("%s: tier forbids what the env forbids" % name, t.get("forbid") == forbid, t.get("forbid"))
        check("%s: tier names its env file" % name, t.get("env_file") == env, t.get("env_file"))
        got = runner.closure_ids(name, None)
        check("%s: runner.closure_ids composes the env" % name,
              got == [modset_builder.BRIDGE] + ids, got)
        deps = runner.mod_dependency_ids(mod_dir)
        own = runner.mod_package_id(mod_dir).lower()
        miss = [d for d in deps + [own] if d != modset_builder.HARMONY and d not in ids]
        check("%s: every About.xml hard dependency and the mod itself are in the env" % name, not miss, miss)
        check("%s: env ids are unique" % name, len(set(ids)) == len(ids), ids)


def t_armoury_donors_out():
    ids, forbid = modset_builder.mod_env("src/RimStarWars/Armoury/modcheck_env.py")
    check("Armoury: ModularWeapons2 forbidden", "kaitorisenkou.modularweapons2" in forbid, forbid)
    bad = [p for p in ids if "modularweapons" in p or p.startswith("guy762.")]
    check("Armoury: no MW2 or retired KotOR donor in the env", not bad, bad)


def t_closure_on_installed():
    installed = modset_builder.scan()
    if len(installed) < 10:
        # The instrument cannot see the mods here (not Archmagi): say so, never pass it as a result.
        print("SKIP closure-on-installed: %d mods readable (UNMEASURED off Archmagi)" % len(installed))
        return
    for name, rel, tier in MODS:
        ids, _ = modset_builder.mod_env(rel + "/modcheck_env.py")
        ordered, missing, refusals = modset_builder.resolve_tier(tier, installed)
        check("%s: tier closes with nothing missing" % name, not missing, missing)
        check("%s: tier is not refused" % name, not refusals, refusals)
        extra = [p for p in ordered
                 if not p.startswith("ludeon.") and p not in ids
                 and p not in (modset_builder.BRIDGE, modset_builder.HARMONY, modset_builder.ZOOM)]
        check("%s: the closure adds nothing the env does not name" % name, not extra, extra)
        check("%s: all five DLC in the list" % name,
              sum(1 for p in ordered if p.startswith("ludeon.rimworld.")) == 5, ordered)


def t_compose_case_blind():
    xml = ("<ModsConfigData><activeMods>\n"
           "    <li>ludeon.rimworld</li>\n"
           "    <li>Neronix17.OuterRim.Core</li>\n    <li>ray1203.simplecamerasetting</li>\n"
           "  </activeMods></ModsConfigData>")
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as f:
        f.write(xml)
        path = f.name
    try:
        added = runner.compose_test_list(["neronix17.outerrim.core", "mandrake.rsw.armoury",
                                          "mandrake.rsw.armoury"], config_path=path)
        check("compose: a live id in other case is not re-added", added == ["mandrake.rsw.armoury"], added)
        with open(path, encoding="utf-8") as f:
            out = f.read().lower()
        check("compose: outerrim core listed once", out.count("neronix17.outerrim.core") == 1, out)
        check("compose: a repeated new id is written once", out.count("mandrake.rsw.armoury") == 1, out)
    finally:
        os.unlink(path)


VE_RE = re.compile(r"(vanilla[a-z]*expanded|oskarpotocki)\.")
VE_KEEP = ("oskarpotocki.vanillafactionsexpanded.core", "vanillaexpanded.vfefactory")
LIVE = "infrastructure/state/live_proofs/MODCHECK_DONOR_ENVIRONMENTS_1.txt"


def a2_condition(path=LIVE):
    """-> (needs, withouts) of live-proof A2's live_def_check call, lower-cased."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        line = [ln for ln in f if ln.startswith("live-proof A2:")]
    if len(line) != 1:
        return None, None
    words = shlex.split(line[0].split(":", 1)[1].split("&&")[0])
    needs = [words[i + 1].lower() for i, w in enumerate(words) if w == "--needs"]
    without = [words[i + 1].lower() for i, w in enumerate(words) if w == "--without"]
    return needs, without


def t_a2_excludes_ve_siblings():
    needs, without = a2_condition()
    check("A2: exactly one live-proof A2 line", needs is not None)
    if needs is None:
        return
    check("A2: needs VFEFactory and VE Framework", all(p in needs for p in VE_KEEP), needs)
    check("A2: no --without names VFEFactory or VE Framework", not [p for p in VE_KEEP if p in without], without)
    check("A2: every --without is a VE packageId", all(VE_RE.match(p) for p in without), without)
    installed = modset_builder.scan()
    if len(installed) < 10:
        print("SKIP A2 sibling coverage: %d mods readable (UNMEASURED off Archmagi)" % len(installed))
    else:
        sib = sorted(p for p in installed if VE_RE.match(p) and p not in VE_KEEP)
        check("A2: the instrument sees VE siblings (sanity: vfeproduction and vfecore installed)",
              "vanillaexpanded.vfeproduction" in sib and "vanillaexpanded.vfecore" in sib, len(sib))
        miss = [p for p in sib if p not in without]
        check("A2: every installed VE sibling is a --without (%d)" % len(sib), not miss, miss)
    # the instrument the line feeds: a sibling in the running load must make the clause UNMEASURED, never green
    base = set(VE_KEEP) | {"mandrake.rm.wreckedmachines", "ludeon.rimworld", "brrainz.harmony"}
    st, _ = live_def_check.condition(needs, without, base, {})
    check("A2: condition met on VFEFactory + VEF alone", st is None, st)
    for p in without:
        st, _ = live_def_check.condition(needs, without, base | {p}, {})
        if st != live_def_check.UNMEASURED:
            check("A2: a running %s makes the clause UNMEASURED" % p, False, st)
            break
    else:
        check("A2: each VE sibling in the running load makes the clause UNMEASURED (%d)" % len(without), bool(without))


if __name__ == "__main__":
    for t in (t_env_files_and_tiers, t_armoury_donors_out, t_closure_on_installed, t_compose_case_blind,
              t_a2_excludes_ve_siblings):
        t()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
