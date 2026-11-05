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
     load that holds any one of them;
  7. every part the A1 and A2 clauses name is on its live-proof line, joined by `&&` so each must hold: A1 needs
     Armoury's closure, `--without` ModularWeapons2 (a running MW2 reads UNMEASURED), `--has` GS_Gaffi and
     kotorsound_GonkDroid (both Armoury's own defs), `--absent` SetIngredients and RecipeDefGenerator, and its
     env_verify_check; A2 `--has` both AutomatedSmelter states (WreckedMachines' own defs), `--absent`
     SetIngredients, RecipeDefGenerator and GenerateAutoProcesses (an NRE naming each reads FAIL), and its
     env_verify_check;
  8. every clause with a live-proof line has exactly one line in live_proofs/MODCHECK_DONOR_ENVIRONMENTS_1.criteria
     at a live level (L1/L2), and the reverse, and that line names the clause's witnesses, the error tokens its
     log check refuses, and `modcheck run <Mod>`, so the supervisor owes it live (gen 10 ended proof_owed on A2).

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
import live_log_check  # noqa: E402

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

# What each clause names, per tool on its line. A missing part turns the selftest red (gen 7's checker found four
# parts that could be deleted with the selftest still green).
CLAUSE_PARTS = {
    "A1": {"mod": "Armoury", "pid": "mandrake.rsw.armoury",
           "needs": ("mandrake.rsw.armoury", "ebsg.framework", "adaptive.storage.framework"),
           "without": ("kaitorisenkou.modularweapons2",),
           "has": ("ThingDef/GS_Gaffi", "SoundDef/kotorsound_GonkDroid"),
           "absent": ("SetIngredients", "RecipeDefGenerator")},
    "A2": {"mod": "WreckedMachines", "pid": "mandrake.rm.wreckedmachines",
           "needs": ("mandrake.rm.wreckedmachines",) + VE_KEEP,
           "without": (),
           "has": ("ThingDef/RM_WM_AutomatedSmelter_Kludged", "ThingDef/RM_WM_AutomatedSmelter_Repaired"),
           "absent": ("SetIngredients", "RecipeDefGenerator", "GenerateAutoProcesses")},
}


def live_line(clause, path=LIVE):
    """-> {script basename: [words after it]} of the clause's live-proof line, or None; and the raw command."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        line = [ln for ln in f if ln.startswith("live-proof %s:" % clause)]
    if len(line) != 1:
        return None, None
    cmd = line[0].split(":", 1)[1].strip()
    parts = {}
    for seg in cmd.split("&&"):
        words = shlex.split(seg)
        if len(words) >= 2 and words[0] == "python3":
            parts[os.path.basename(words[1])] = words[2:]
    return parts, cmd


def opt(words, flag):
    return [words[i + 1] for i, w in enumerate(words[:-1]) if w == flag]


def t_clause_parts_on_lines():
    for clause, want in sorted(CLAUSE_PARTS.items()):
        parts, cmd = live_line(clause)
        check("%s: exactly one live-proof line" % clause, parts is not None)
        if parts is None:
            continue
        check("%s: every step is joined by && (no ||, ;, | or &)" % clause,
              not re.search(r"\|\||;|(?<!&)&(?!&)|(?<!\|)\|(?!\|)", cmd), cmd[:120])
        ddc, llc = parts.get("live_def_check.py"), parts.get("live_log_check.py")
        check("%s: runs live_def_check, live_log_check and env_verify_check" % clause,
              ddc is not None and llc is not None and "env_verify_check.py" in parts, sorted(parts))
        if ddc is None or llc is None or "env_verify_check.py" not in parts:
            continue
        needs = [p.lower() for p in opt(ddc, "--needs")]
        without = [p.lower() for p in opt(ddc, "--without")]
        has, absent = opt(ddc, "--has"), opt(llc, "--absent")
        for p in want["needs"]:
            check("%s: --needs %s" % (clause, p), p in needs, needs)
        for p in want["without"]:
            check("%s: --without %s" % (clause, p), p in without, without)
        for k in want["has"]:
            check("%s: --has %s" % (clause, k), k in has, has)
        for t in want["absent"]:
            check("%s: live_log_check --absent %s" % (clause, t), t in absent, absent)
        check("%s: env_verify_check reads %s" % (clause, want["mod"]),
              parts["env_verify_check.py"] == [want["mod"]], parts["env_verify_check.py"])
        # the witnesses are the mod's own defs, so an unresolved one is a FAIL, never an unowned shrug
        owners = live_def_check.def_owners(list(want["has"]))
        for k in want["has"]:
            check("%s: %s is %s's own def" % (clause, k, want["mod"]), want["pid"] in (owners.get(k) or ()),
                  owners.get(k))
        # the instruments the parts feed: a forbidden mod running reads UNMEASURED; an NRE naming a token reads FAIL
        base = set(needs) | {"ludeon.rimworld", "brrainz.harmony"}
        st, _ = live_def_check.condition(needs, without, base, {})
        check("%s: condition met on its own closure" % clause, st is None, st)
        for p in want["without"]:
            st, _ = live_def_check.condition(needs, without, base | {p}, {})
            check("%s: a running %s makes the clause UNMEASURED" % (clause, p), st == live_def_check.UNMEASURED, st)
        for t in want["absent"]:
            log = ("Bridge token: x\nException in %s: System.NullReferenceException: Object reference not set\n"
                   "  at Verse.Foo.Bar () [0x00000]\n" % t)
            code, _ = live_log_check.judge(log, absent)
            check("%s: an exception naming %s reads FAIL" % (clause, t), code == live_log_check.FAIL, code)
        code, _ = live_log_check.judge("Bridge token: x\nall quiet\n", absent)
        check("%s: a clean log reads PASS" % clause, code == live_log_check.PASS, code)


CRIT = "infrastructure/state/live_proofs/MODCHECK_DONOR_ENVIRONMENTS_1.criteria"


def criteria_lines(path=CRIT):
    """-> {clause: [(level, text), ...]} of the criteria file."""
    out = {}
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        for ln in f:
            m = re.match(r"\s*([A-Z]\d+)\s+(L\d)\s*:\s*(.*)", ln)
            if m:
                out.setdefault(m.group(1), []).append((m.group(2), m.group(3)))
    return out


def live_clauses(path=LIVE):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return {m.group(1) for m in (re.match(r"live-proof ([A-Z]\d+):", ln) for ln in f) if m}


def criteria_bind_faults(crit, clauses):
    """-> list of faults binding the live-proof clauses to the criteria lines (empty when bound)."""
    faults = []
    for c in sorted(set(clauses) | set(CLAUSE_PARTS)):
        rows = crit.get(c, [])
        if len(rows) != 1:
            faults.append("%s: %d criteria lines, want 1" % (c, len(rows)))
            continue
        level, text = rows[0]
        if level not in ("L1", "L2"):
            faults.append("%s: level %s is not live (L1/L2)" % (c, level))
        want = CLAUSE_PARTS.get(c)
        if want is None:
            continue
        for k in want["has"]:
            name = k.split("/", 1)[-1]
            if name not in text and "_" + name.rsplit("_", 1)[-1] not in text:
                faults.append("%s: criteria does not name witness %s" % (c, name))
        for t in want["absent"]:
            if t not in text:
                faults.append("%s: criteria does not name refused token %s" % (c, t))
        if "modcheck run %s" % want["mod"] not in text:
            faults.append("%s: criteria does not name `modcheck run %s`" % (c, want["mod"]))
    for c in sorted(set(crit) - set(clauses)):
        faults.append("%s: criteria line with no live-proof line" % c)
    return faults


def t_criteria_bound_to_lines():
    crit, clauses = criteria_lines(), live_clauses()
    check("criteria: every live clause is A1 and A2", clauses == set(CLAUSE_PARTS), sorted(clauses))
    faults = criteria_bind_faults(crit, clauses)
    check("criteria: each live clause owed once at a live level, naming its parts", not faults, faults)
    # probes: the instrument sees each break
    drop_a2 = {k: v for k, v in crit.items() if k != "A2"}
    check("criteria probe: a missing A2 line is a fault", any(f.startswith("A2:") for f in
          criteria_bind_faults(drop_a2, clauses)))
    l0 = dict(crit, A2=[("L0", crit.get("A2", [("L1", "")])[0][1])])
    check("criteria probe: A2 at a non-live level is a fault", any("not live" in f for f in
          criteria_bind_faults(l0, clauses)))
    bare = dict(crit, A1=[("L1", "the load is fine")])
    check("criteria probe: an A1 line naming none of its parts is a fault",
          len([f for f in criteria_bind_faults(bare, clauses) if f.startswith("A1:")]) >= 4)
    check("criteria probe: a criteria clause with no live line is a fault",
          any("no live-proof line" in f for f in criteria_bind_faults(dict(crit, A3=[("L1", "x")]), clauses)))


if __name__ == "__main__":
    for t in (t_env_files_and_tiers, t_armoury_donors_out, t_closure_on_installed, t_compose_case_blind,
              t_a2_excludes_ve_siblings, t_clause_parts_on_lines, t_criteria_bound_to_lines):
        t()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
