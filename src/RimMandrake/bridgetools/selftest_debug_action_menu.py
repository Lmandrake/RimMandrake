#!/usr/bin/env python3
"""selftest_debug_action_menu.py - offline guard for BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE.

The defect: rimworld/execute_debug_action opened a debug action's FloatMenu ('Tanks: fill ALL on map to max (pick
liquid)'), and it was gone before the next bridge call, so its options could never be read or picked. The fix is the
companion tool jawa/debug_action_menu, whose whole point is that the action runs, the menu is read and the option is
picked in ONE main-thread slice - no frame passes in which the menu can vanish. A refactor that splits that slice (a
second InvokeAsync, or the read moved after it) silently brings the bug back, so this pins it from the source:

  * the tool is declared, GM-classed (debug-invoke family) and on the must-be-off-in-campaign tripwire;
  * its body holds exactly ONE MainThread.InvokeAsync, and the action invoke, the FloatMenu read and the option's
    action all sit inside that lambda; a menu left standing is pinned (vanishIfMouseDistant false);
  * the live proof's constants name the two real FlowWorks debug actions, and its inspect-string parser reads the
    FlowWorks key text (Languages/English/Keyed/LiquidTank_Keys.xml) correctly, full and part-full;
  * the live proof file names that script for A1, with a criteria line.
Exit 0 all pass, 1 any fail. No game, no dotnet, no Windows program.
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(HERE, "JawaBench.BridgeTools")
ITEM = "BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE"

fails = []


def check(ok, name, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else ": " + str(detail)))
    if not ok:
        fails.append(name)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    tool_src = read(os.path.join(SRC, "JawaBenchDebugActionMenuTool.cs"))
    safety = read(os.path.join(SRC, "JawaBenchSafetyCore.cs"))

    # sanity probe: the instrument sees the surface at all (a broken glob would make every 'absent' check pass)
    declared = set()
    for f in os.listdir(SRC):
        if f.endswith(".cs"):
            declared.update(re.findall(r'\[Tool\(\s*"(jawa/[A-Za-z0-9_/]+)"', read(os.path.join(SRC, f))))
    check(len(declared) >= 300 and "jawa/static_call" in declared, "census_sees_the_tool_surface", len(declared))
    check("jawa/debug_action_menu" in declared, "tool_declared")
    check('["jawa/debug_action_menu"] = FDebugInvoke' in safety, "tool_in_debug_invoke_family")
    m = re.search(r"MustBeOffInCampaign\s*=\s*\{(.*?)\};", safety, re.S)
    check(bool(m) and '"jawa/debug_action_menu"' in m.group(1), "tool_on_campaign_off_tripwire")

    body_m = re.search(r"public static async Task<object> DebugActionMenu\((.*)", tool_src, re.S)
    body = body_m.group(1) if body_m else ""
    check(bool(body), "tool_method_found")
    n_hops = body.count("MainThread.InvokeAsync")
    check(n_hops == 1, "exactly_one_main_thread_slice", n_hops)
    hop = body.find("MainThread.InvokeAsync")
    inv = body.find("method.Invoke(null, null)")
    read_menu = body.find("OfType<FloatMenu>()", inv if inv >= 0 else 0)
    pick = body.find("chosen.action()")
    check(hop >= 0 and inv > hop, "action_invoked_inside_the_slice", (hop, inv))
    check(read_menu > inv > 0, "menu_read_after_invoke_in_same_slice", (inv, read_menu))
    check(pick > read_menu > 0, "pick_runs_in_same_slice", (read_menu, pick))
    check("TryRemove(target, false)" in body and body.find("TryRemove(target, false)") < pick, "menu_closed_before_option_runs")
    check('GetField("vanishIfMouseDistant"' in tool_src and "DamVanishField.SetValue(fm, false)" in body, "leftover_menu_pinned")
    check("DebugActionType.Action" in body and "GetParameters().Length != 0" in body, "map_click_tools_refused_by_name")

    # Semantics, not just presence (blind check at 52203cfa: an inverted filter and a guarded pick both stayed green).
    # (a) 'lists the liquids': the menus read are exactly the ones the action ADDED - a snapshot taken before the
    #     invoke, and a filter that keeps windows NOT in it. Inverting it reads no new menu at all.
    snap = re.search(r"var\s+before\s*=\s*new\s+HashSet<Window>\(\s*Find\.WindowStack\.Windows\s*\)\s*;", body)
    check(bool(snap) and snap.start() < inv, "before_snapshot_taken_before_invoke", snap and (snap.start(), inv))
    newf = re.search(r"menus\s*=\s*Find\.WindowStack\.Windows\.OfType<FloatMenu>\(\)\s*\.Where\(\s*(\w+)\s*=>\s*!\s*before\.Contains\(\s*\1\s*\)\s*\)\s*\.ToList\(\)\s*;", body)
    check(bool(newf) and newf.start() > inv, "menus_read_are_the_new_ones", "want menus = ...Where(w => !before.Contains(w)).ToList(); after the invoke")
    check(len(re.findall(r"before\.Contains", body)) == 1, "one_before_filter_only", len(re.findall(r"before\.Contains", body)))
    # (b) 'picking one fills every tank': the chosen option's action runs UNCONDITIONALLY once the pick is accepted -
    #     the try block holds exactly the call, and nothing between the menu close and the call can skip it.
    tryblk = re.search(r"try\s*\{\s*chosen\.action\(\)\s*;\s*\}", body)
    check(bool(tryblk), "option_action_runs_unconditionally", "want exactly 'try { chosen.action(); }'")
    rm_at = body.find("TryRemove(target, false)")
    between = body[rm_at:tryblk.start()] if (tryblk and rm_at >= 0) else ""
    between_code = re.sub(r"//[^\n]*", "", between)
    check(rm_at >= 0 and tryblk is not None and re.fullmatch(r"TryRemove\(target, false\);\s*", between_code) is not None,
          "nothing_between_close_and_pick", between_code.strip()[:120])
    chosen_m = re.search(r"FloatMenuOption\s+chosen\s*=\s*opts\[\s*idx\s*\]\s*;", body)
    check(bool(chosen_m) and chosen_m.start() < rm_at, "chosen_is_the_indexed_option")
    check(re.search(r"\bif\s*\(\s*(false|!\s*true)\s*\)", body) is None and "#if" not in body, "no_dead_branch_in_tool_body")

    # the live proof: its action names are the real ones, its parser reads the real key text
    spec = importlib.util.spec_from_file_location("pdam", os.path.join(HERE, "prove_debug_action_menu.py"))
    pdam = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    spec.loader.exec_module(pdam)
    tank_debug = read(os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "Debug", "FlowWorksTankDebug.cs"))
    names = set(re.findall(r'\[DebugAction\(CAT,\s*"([^"]+)"', tank_debug))
    for const in ("FILL_ALL", "EMPTY_ALL"):
        leaf = getattr(pdam, const).split("\\")[-1]
        check(leaf in names, "proof_names_real_action_" + const, (leaf, sorted(names)))
    keys = read(os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Languages", "English", "Keyed", "LiquidTank_Keys.xml"))
    km = re.search(r"<RM_LiquidTankHolding>(.*?)</RM_LiquidTankHolding>", keys)
    check(bool(km), "holding_key_found")
    if km:
        tpl = km.group(1)
        full = tpl.replace("{0}", "Fresh water").replace("{1}", "1,200 L").replace("{2}", "1,200 L")
        part = tpl.replace("{0}", "Fuel oil").replace("{1}", "40 L").replace("{2}", "1,200 L")
        check(pdam.holding(["Some base line", full]) == ("Fresh water", "1,200 L", "1,200 L"), "parser_reads_full", pdam.holding([full]))
        h = pdam.holding([part])
        check(h is not None and h[0] == "Fuel oil" and h[1] != h[2], "parser_reads_part_full", h)
        check(pdam.holding(["Empty"]) is None, "parser_reads_empty_as_nothing")

    lp = os.path.join(REPO, "infrastructure", "state", "live_proofs", ITEM + ".txt")
    cr = os.path.join(REPO, "infrastructure", "state", "live_proofs", ITEM + ".criteria")
    lpt = read(lp) if os.path.exists(lp) else ""
    check(re.search(r"^live-proof A1: .*prove_debug_action_menu\.py", lpt, re.M) is not None, "live_proof_A1_names_the_script")
    check(os.path.exists(cr) and re.search(r"^A1 L2: ", read(cr), re.M) is not None, "criteria_A1_present")

    print("%s %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
