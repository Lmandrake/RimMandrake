#!/usr/bin/env python3
"""T_ROUND6_GAPS (RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS): the 17 round-6 coverage gaps stay closed.

The coverage judge rm-coverage-judge-1794750987 returned 18 gaps on design/concepts/Pyrelands (coverage_verdict.json); his
card 2026-11-15 (OWNER:1794774724955142310, "Fix the 17 gaps, one final look") fixes g1, g2 and g4-g18; g3 is Polish and
out (version/polish.md). One check per fixed gap reads the concept's scenes.json, tree.json, sheet.md, record.json and
floor.json for the shape the gap's would_pass names, and the Designer's own gates (concept_tree lint, scene_errors,
showcase_check) must stay clean. Every check fails on the base the card was recorded on (7c9f5784b1).

  python3 <this file>                 exit 0 = every gap check and gate PASS, 1 = FAIL
  python3 <this file> --entry-points  exit 0 = every scene owed by the round-6 parts item has its entry point in its script
                                      (the acceptance test of RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN)
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = os.path.join(REPO, "design", "concepts", "Pyrelands")
SETTINGS_CS = os.path.join(HERE, "Source", "RM_PyrelandsMod.cs")
PARTS_ITEM = "RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN"
APPROVAL_DAY = "2026-10-16"   # his art-sheet approval, OWNER:1792122659817386516
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))


def load():
    j = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))  # noqa: E731
    sheet = open(os.path.join(D, "sheet.md"), encoding="utf-8").read()
    return j("scenes.json"), j("tree.json"), sheet, j("record.json"), j("floor.json")


def words(*parts):
    out = []
    for p in parts:
        if isinstance(p, dict):
            out.append(words(*p.values()))
        elif isinstance(p, list):
            out.append(words(*p))
        elif p is not None:
            out.append(str(p))
    return " ".join(out)


class Concept(object):
    def __init__(self):
        self.sc, self.tree, self.sheet, self.rec, self.floor = load()
        self.scenes = {s["id"]: s for s in self.sc["scenes"]}
        self.leaves = {x["id"]: x for x in self.tree["leaves"]}
        self.rest = {c["capability"]: c for c in self.sc.get("coverage_rest", [])}
        self.inv = {e["id"]: e for e in self.rec["inventory"]}
        tt = json.load(open(os.path.join(D, "version", "test_table.json"), encoding="utf-8"))
        self.tests = tt["tests"]

    def scene(self, sid):
        return self.scenes.get(sid) or {}

    def does(self, lid):
        m = re.search(r"^- \[leaf:%s\] (.+)$" % re.escape(lid), self.sheet, re.M)
        return m.group(1) if m else ""

    def section(self, name):
        m = re.search(r"^## %s\n(.*?)(?=^## |\Z)" % re.escape(name), self.sheet, re.M | re.S)
        return m.group(1) if m else ""

    def scenes_for(self, lid):
        return [s for s in self.sc["scenes"] if lid in s.get("requirement", [])]

    def item_exists(self, iid):
        base = os.path.join(REPO, "infrastructure", "state", "items")
        return any(os.path.exists(os.path.join(base, sub, iid + ".md")) for sub in ("", "closed"))


def need(cond, why, errs):
    if not cond:
        errs.append(why)


def g1(c):
    e = []
    lf = c.leaves.get("furnacebeast_warms") or {}
    need("RM_FurnaceHideBank" in words(lf.get("experience"), lf.get("oracle_proposed"), lf.get("scenario")),
         "leaf furnacebeast_warms does not state the furnace-hide heat bank", e)
    need("heat bank" in c.does("furnacebeast_warms"), "the furnacebeast_warms does-line does not state the heat bank", e)
    sc = [s for s in c.scenes_for("furnacebeast_warms") if "RM_FurnaceHideBank" in words(s.get("start"), s.get("action"),
                                                                                           s.get("expect"))]
    need(bool(sc), "no acceptance scene stages the furnace-hide heat bank", e)
    for s in sc:
        t = words(s.get("start"), s.get("action"), s.get("expect"))
        need("RM_FurnaceHide" in t.replace("RM_FurnaceHideBank", ""), "%s does not yield RM_FurnaceHide" % s["id"], e)
        need("butcher" in t.lower(), "%s does not butcher a furnace-beast for the hide" % s["id"], e)
        need("no bank" in words(s.get("control")).lower(), "%s control is not a twin room with no bank" % s["id"], e)
        need("fuel" in t and "power" in t, "%s does not assert no fuel and no power" % s["id"], e)
        sky = [x for x in c.sc["showcases"] if x["id"] == "sky_and_shelter"]
        need(bool(sky) and s["id"] in sky[0]["scenes"], "%s is not staged in showcase sky_and_shelter" % s["id"], e)
    return e


def g2(c):
    e = []
    need(not [x["id"] for x in c.sc["showcases"] if "inv_biome_self_contained" in x.get("exercises", [])],
         "a showcase claims inv_biome_self_contained though no scene in it uses the payload, ports or text", e)
    row = c.rest.get("inv_biome_self_contained") or {}
    need(bool(row), "coverage_rest has no inv_biome_self_contained row", e)
    checks = row.get("checks") or []
    need("T_SELF_CONTAINED_OFFLINE" in checks, "the inv_biome_self_contained row names no T_SELF_CONTAINED_OFFLINE", e)
    for t in checks:
        f = (c.tests.get(t) or {}).get("file")
        need(bool(f) and os.path.exists(os.path.join(REPO, f)), "check %s is no test_table test with a file on disk" % t, e)
    why = words(row.get("why"))
    for k in ("RM_AcousticPayload_Pyrelands", "RM_RetiredMutatorPorts_Pyrelands", "campaign"):
        need(k in why, "the inv_biome_self_contained row's why does not name %s" % k, e)
    return e


def scribed_fields():
    src = open(SETTINGS_CS, encoding="utf-8").read()
    src = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", src, flags=re.S))
    return re.findall(r"Scribe_Values\.Look\(\s*ref\s+(\w+)\s*,", src)


def g4(c):
    e = []
    row = c.rest.get("inv_settings_gate") or {}
    m = row.get("settings_map")
    need(isinstance(m, dict) and m, "coverage_rest inv_settings_gate has no settings_map", e)
    if isinstance(m, dict):
        fields = scribed_fields()
        need(len(fields) >= 40, "the Scribe read of RM_PyrelandsMod.cs sees only %d settings (instrument blind?)" % len(fields), e)
        missing = [f for f in fields if f not in m]
        need(not missing, "settings_map lists no check for %s" % ", ".join(missing), e)
        extra = [k for k in m if k not in fields]
        need(not extra, "settings_map names settings the mod does not scribe: %s" % ", ".join(extra), e)
        for k, v in m.items():
            refs = v if isinstance(v, list) else []
            need(bool(refs), "settings_map %s names nothing" % k, e)
            for r in refs:
                if r in c.scenes:
                    need(k in words(c.scenes[r].get("control"), c.scenes[r].get("action")),
                         "settings_map %s -> %s, whose action or control never turns %s" % (k, r, k), e)
                elif r not in c.tests and r not in c.leaves:
                    need(False, "settings_map %s -> %s is no scene, leaf or test_table id" % (k, r), e)
        for k in ("crossBiomeEnabled", "crossBiomeEverywhere", "crossBiomeBiomeList", "crossBiomeCoverage"):
            need("T_SELF_CONTAINED_OFFLINE" in (m.get(k) or []), "settings_map %s is not checked for its unsupported label" % k, e)
    need(bool((c.floor.get("lines", {}).get("mod_settings") or {}).get("establishes")), "floor.json mod_settings has no establishes", e)
    need("switch the other mechanics off and on" not in words(c.scene("sc_walk"), row.get("why")),
         "sc_walk or the coverage_rest why still rests on 'switch the other mechanics off and on'", e)
    return e


def g5(c):
    e = []
    roof = [s for s in c.sc["scenes"] if s["id"] != "sc_walk" and "CompWithersUnderRoof" in words(s.get("start"), s.get("expect"),
                                                                                                    s.get("control"))]
    need(bool(roof), "no scene but sc_walk reads roof withering (CompWithersUnderRoof)", e)
    for s in roof:
        ctl = words(s.get("control"))
        need("unroofed" in ctl and "PyrelandsMechanicsGate" in ctl, "%s control lacks the unroofed twin or the gate-off case" % s["id"], e)
    thirst = [s for s in c.sc["scenes"] if s["id"] != "sc_walk" and "RM_Thirst" in words(s.get("start"), s.get("expect"))]
    need(bool(thirst), "no scene but sc_walk reads the cast's slow thirst (RM_Thirst)", e)
    for s in thirst:
        ctl = words(s.get("control"))
        # the gate-off overlap map was removed as no bar needs it (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN,
        # f3b1999757, version/polish.md); the vanilla herd animal stays the control
        need("vanilla" in ctl, "%s control lacks the vanilla herd animal" % s["id"], e)
    pb = words(c.inv["inv_plant_roster"].get("parts_covered_by"))
    ab = words(c.inv["inv_animal_roster"].get("parts_covered_by"))
    need(any(s["id"] in pb for s in roof), "inv_plant_roster parts_covered_by does not name the roof scene", e)
    need(any(s["id"] in ab for s in thirst), "inv_animal_roster parts_covered_by does not name the thirst scene", e)
    return e


def g6(c):
    e = []
    s = c.scene("sc_ash_ground")
    st, ex, ctl = words(s.get("start")), words(s.get("expect")), words(s.get("control"))
    need("at least one standing-water body" in st, "sc_ash_ground does not assert a standing-water body at start", e)
    need("a map with none is correct" not in ex, "sc_ash_ground still passes the ring with no water", e)
    need("0.85" in ex and "most cells" not in ex, "sc_ash_ground expect does not tie deep ash to the 0.85 bar", e)
    # the gate-off regeneration (the case without the standing-water genstep) was removed as no bar needs it
    # (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN, f3b1999757, version/polish.md): not owed any more
    return e


def g7(c):
    e = []
    s = c.scene("sc_ash_ground")
    t = words(s.get("action"), s.get("expect"))
    need("PyrelandsAshCover" in t and "PyrelandsAshDust" in t, "sc_ash_ground does not expect the ash cover and the plant dust", e)
    need("capture pair" in t, "sc_ash_ground takes no capture pair of the ash drawing", e)
    need("depth cleared" in words(s.get("control")), "sc_ash_ground control has no depth-cleared twin for the drawing", e)
    return e


def g8(c):
    e = []
    s = c.scene("sc_no_rain")
    t = words(s.get("start"), s.get("action"), s.get("expect"))
    need("GameCondition_ForceWeather" in t and "PyrelandsNoOrdinaryRain" in t, "sc_no_rain does not force Rain through a game condition", e)
    # the vanilla temperate control was replaced by the gate-off roll on the same site (f3b1999757, version/polish.md)
    need("gives Rain" in words(s.get("control")) and "pyrelandsEnabled" in words(s.get("control")),
         "sc_no_rain control does not show the same forced roll gives Rain with the mechanics off", e)
    need("force rain" in words(c.leaves["no_ordinary_rain"].get("scenario")).lower(), "leaf no_ordinary_rain scenario omits forced weather", e)
    return e


def g9(c):
    e = []
    s = c.scene("sc_heat_dome")
    ex = words(s.get("expect"))
    need("the dome graphic drawn at +60" not in ex, "sc_heat_dome still accepts 'the dome graphic drawn'", e)
    need("bodyGraphic" in ex and "AshwallowDome" in ex and "differ" in ex,
         "sc_heat_dome does not require the domed body graphic (AshwallowDome) to differ from the standing one", e)
    need("capture" in words(s.get("action")), "sc_heat_dome takes no capture of the domed animal", e)
    tex = os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "Pyrelands", "Ashwallow")
    need(all(os.path.exists(os.path.join(tex, "AshwallowDome_%s.png" % f)) for f in ("north", "south", "east")),
         "the dome sprite AshwallowDome_* the scene reads is not on disk", e)
    need("dome sprite is the standing body" not in words(c.rec), "record.json still says the dome sprite is the standing body", e)
    return e


def g10(c):
    e = []
    s = c.scene("sc_furnace_giant")
    t = words(s.get("action"), s.get("expect"))
    need("every RM_Pyrelands roster kind" in t, "sc_furnace_giant reads only the ullai", e)
    need("at least twice" in words(s.get("expect")), "sc_furnace_giant states no margin over every other kind", e)
    # round 9 (rm-coverage-judge-1794938181): a bar is an experience, never a tuning number (owner 2026-11-16, bar_rule)
    pin = re.findall(r"\b\d+\.\d+\b|\bsize \d", words(s.get("expect"), json.dumps(s.get("control"))))
    need(not pin, "sc_furnace_giant pins a size: %r" % pin, e)
    return e


def g11(c):
    e = []
    ex = words(c.scene("sc_firehawk_rewards").get("expect"))
    need("RM_FireHawkSightedLabel" in ex and "ember" in ex and "label" in ex, "sc_firehawk_rewards does not read the letter's words", e)
    need("MarketValue" in ex and "Beauty" in ex, "sc_firehawk_rewards does not read the crestfeather's value and beauty", e)
    return e


def added_art():
    """Texture paths (no .png, no facing suffix) added under Pyrelands/Textures since his approval day, and every texPath our
    Defs borrow from outside our Textures folder."""
    out = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--since=%sT12:00" % APPROVAL_DAY, "--name-only",
                          "--format=", "--", "src/RimMandrake/Pyrelands/Textures"], capture_output=True, text=True, check=True).stdout
    tex = os.path.join(HERE, "Textures")
    added = set()
    for p in out.split():
        rel = p.replace("src/RimMandrake/Pyrelands/Textures/", "")
        if rel.endswith(".png") and os.path.exists(os.path.join(tex, rel)):
            added.add(re.sub(r"(_north|_south|_east|_west)?\.png$", "", rel))
    ours = set()
    for root, _, files in os.walk(tex):
        for f in files:
            ours.add(os.path.relpath(os.path.join(root, f), tex).replace(os.sep, "/"))
    borrowed = set()
    for root, _, files in os.walk(os.path.join(HERE, "Defs")):
        for f in [f for f in files if f.endswith(".xml")]:
            for t in re.findall(r"<texPath>([^<]+)</texPath>", open(os.path.join(root, f), encoding="utf-8").read()):
                if not any(o.startswith(t) for o in ours):
                    borrowed.add(t)
    return added, borrowed


def g12(c):
    e = []
    row = c.rest.get("inv_art_and_text") or {}
    lst = row.get("post_approval_art")
    need(isinstance(lst, list) and lst, "coverage_rest inv_art_and_text has no post_approval_art list", e)
    if isinstance(lst, list):
        added, borrowed = added_art()
        need(len(added) >= 5, "the git read of art added after %s sees only %d paths (instrument blind?)" % (APPROVAL_DAY, len(added)), e)
        need(bool(borrowed), "the texPath read sees no borrowed art, but the crestfeather borrows ThrumboHorn (instrument blind?)", e)
        listed = [x.get("tex") for x in lst if isinstance(x, dict) and x.get("tex")]
        for t in sorted(added | borrowed):
            need(any(t.startswith(l) for l in listed), "post_approval_art does not list %s" % t, e)
        for x in lst:
            v, it = x.get("judge"), x.get("item")
            need(bool(v) or (bool(it) and c.item_exists(it)), "post_approval_art %s has no judge verdict and no filed item" % x.get("tex"), e)
        for f in ("grass lifecycle", "kept-art judge digest", "dome sprite"):
            need(f in words(lst), "post_approval_art omits the open follow-up '%s'" % f, e)
    return e


def g13(c):
    e = []
    s = c.scene("sc_burn_line_walks")
    t = words(s.get("action"), s.get("expect"))
    need("capture" in t and ("each game hour" in t or "each hour" in t) and "capture hour asserted" in t, "sc_burn_line_walks takes no hourly asserted captures", e)
    need(s.get("hold") == "owner_review" or "savegame" in words(s.get("restore")), "sc_burn_line_walks neither holds nor keeps a save", e)
    return e


def g14(c):
    e = []
    s = c.scene("sc_burn_compounds")
    need("vitals" in words(s.get("start")) and "incidents" in words(s.get("start")), "sc_burn_compounds start has no vitals and incident guard", e)
    need("vitals" in words(s.get("expect")), "sc_burn_compounds expect does not assert the vitals unchanged", e)
    return e


def g15(c):
    e = []
    s = c.scene("sc_grass_regreens")
    st, ex, ctl = words(s.get("start")), words(s.get("expect")), words(s.get("control"))
    need("before any test action" in st, "sc_grass_regreens' cover census is not on a fresh map before any test action", e)
    # his card 2026-11-17 (OWNER:1794926128945577969): the grass shares are tuning, the bar is the experience
    need("carpeted" in ex and "dense cover on open ground" not in ex,
         "sc_grass_regreens does not say open ground reads carpeted", e)
    need(not re.search(r"\d%|\b0\.\d", ex), "sc_grass_regreens pins a grass share in its expect (tuning, not a bar)", e)
    need("grey ash over grass" in ex, "sc_grass_regreens does not rule out grass hidden under ash", e)
    need("plantDensity" in ctl and "lower" in ctl, "sc_grass_regreens control has no same-seed lower-density map", e)
    need("density enforcer" in words(s.get("control", {}).get("rules_out")), "sc_grass_regreens rules_out does not name the enforcer", e)
    return e


def g16(c):
    e = []
    ex = words(c.scene("sc_foreign_arrivals").get("expect"))
    need("IncidentWorker_HerdMigration" in ex and "CanFireNow" in ex and "RM_Ullai" in ex,
         "sc_foreign_arrivals does not assert a live herd migration can fire and brings RM_Ullai", e)
    lf = words(c.leaves["ullai_cross_the_map_as_vanilla_herds"].get("oracle_proposed"))
    need("T_CUT_STAYS_CUT" in lf and "selftest_pyrelands_cut_stays_cut.py" in lf, "the ullai leaf oracle does not name T_CUT_STAYS_CUT", e)
    need("sc_foreign_arrivals" in words(c.inv["inv_ullai_herd_giant"].get("parts_covered_by")),
         "inv_ullai_herd_giant parts_covered_by does not name sc_foreign_arrivals", e)
    return e


G17 = [  # (behaviour, the words a leaf experience and a does-line must carry, the scene that tests it)
    ("fire sense", "steps away from fire", "sc_fire_sense"),
    ("eat before fire duty", "eats before", "sc_fire_sense"),
    ("wet roots", "cooler", "sc_ash_watered"),
    ("seek-burn", "flies to a burn", "sc_firehawk"),
    ("fire-cast top-up", "two fire-hawks and eight ashwallows", "sc_populations"),
    ("roof withering", "withers under a roof", None),
    ("slow thirst", "slow thirst", None),
]


def g17(c):
    e = []
    for what, key, sid in G17:
        leaf_hit = [x["id"] for x in c.tree["leaves"] if key in words(x.get("experience"))]
        need(bool(leaf_hit), "no leaf experience states %s ('%s')" % (what, key), e)
        need(any(key in c.does(l) for l in leaf_hit), "no sheet does-line states %s ('%s')" % (what, key), e)
        if sid and leaf_hit:
            need(any(l in c.scene(sid).get("requirement", []) for l in leaf_hit),
                 "%s's requirement is no leaf that states %s" % (sid, what), e)
    return e


def g18(c):
    e = []
    want = {"inv_firefoam_sprayer", "inv_sand_shovel", "inv_firehawk_hunt_rewards"}
    four = [s for s in c.sc["showcases"][3:] if want <= set(s.get("exercises", []))]
    need(bool(four), "no fourth showcase exercises the firefoam sprayer, the sand shovel and the hunt rewards", e)
    need(not want & set(c.rest), "coverage_rest still lists %s" % ", ".join(sorted(want & set(c.rest))), e)
    need("solace" in c.section("delegated"), "the sheet's delegated section does not name the solace showcase", e)
    return e


def gates(c):
    import concept_tree as CT
    import designer_stage as DS
    e = []
    r = subprocess.run([sys.executable, os.path.join(REPO, "src", "RimMandrake", "rimflow", "concept_tree.py"), "lint", D],
                       capture_output=True, text=True)
    # The floor moved on 2026-11-21 (cba242eda8: a mechanic works by its conditions) under the rule that a current version
    # converts at its next version and no current bar moves, so a floor stamp older than the floor is next-version work,
    # not a reopened round-6 gap. Only that one lint line is set aside; any other line, or a refusal with no line, fails.
    lines = [x.strip()[2:] for x in r.stdout.splitlines() if x.strip().startswith("- ")]
    rest = [x for x in lines if not x.startswith("floor.hash is not the current floor's")]
    need(r.returncode == 0 or (lines and not rest), "concept_tree lint: %s" % ("; ".join(rest) or (r.stdout + r.stderr).strip()[-400:]), e)  # cut-ok: a selftest's report line
    e += ["scene_errors: " + x for x in DS.scene_errors(c.sc, c.tree, REPO)]
    owner_ev = CT.owner_events(REPO)
    e += ["showcase_check: " + x for x in DS.showcase_check(c.sc, c.rec, c.tree, owner_ev, REPO, concept="Pyrelands")]
    return e


CHECKS = [("g1", g1), ("g2", g2), ("g4", g4), ("g5", g5), ("g6", g6), ("g7", g7), ("g8", g8), ("g9", g9), ("g10", g10),
          ("g11", g11), ("g12", g12), ("g13", g13), ("g14", g14), ("g15", g15), ("g16", g16), ("g17", g17), ("g18", g18),
          ("gates", gates)]


def entry_points(c):
    import designer_stage as DS
    def items(s):
        v = s.get("owed_parts_item")
        return (v if isinstance(v, list) else [v]) + [s.get("entry_point_item")]
    owed = [s for s in c.sc["scenes"] if PARTS_ITEM in items(s)]
    bad = [s["id"] for s in owed if not DS.entry_point_exists(REPO, s.get("entry_point"))]
    print("%d scene(s) owed by %s; entry point missing: %s" % (len(owed), PARTS_ITEM, ", ".join(bad) or "none"))
    return 1 if bad or not owed else 0


def main(argv):
    c = Concept()
    if "--entry-points" in argv:
        return entry_points(c)
    failed = 0
    for gid, fn in CHECKS:
        try:
            errs = fn(c)
        except Exception as ex:  # a crash is a FAIL, never a skip
            errs = ["check crashed: %r" % ex]
        failed += bool(errs)
        print("%s %s%s" % ("FAIL" if errs else "PASS", gid, "" if not errs else ": " + "; ".join(errs)[:900]))
    print("%s: %d of %d checks failed" % ("FAIL" if failed else "PASS", failed, len(CHECKS)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
