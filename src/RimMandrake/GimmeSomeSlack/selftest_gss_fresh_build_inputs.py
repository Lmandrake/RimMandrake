#!/usr/bin/env python3
"""RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES: the three visit-2 walk lines on the full-list review map were the
walk's own instruments, each Verse-bound (no offline C# harness runs them), so the guards are on the source:

  fresh inputs   every from-scratch CordBuilder build that is compared with the live cords (the GSS probe's `fresh`, the
                 JawaBench playtest's cords/soak/save_reload_b compare) takes production's map inputs from ONE function,
                 RM_MapComponent_CordGraph.MapBuildOptions (settings + tap ids + each run's stored look via Core UseLooks).
                 The playtest built with bare settings: every styled run (station 5 Modern, station 31 Industrial) was
                 keyed by the default look, 65-91 edges "missing" and as many "extra". The look rule itself is Core only.
  settle         save_reload_b reads the loaded cords after GSettle (laid everything planned, and built at least once since
                 the load), not after 6 fixed frames: on the 170-edge review map the read saw 116 edges and "lost" a line.
  look pick      the ui conduit-look check picks one of the mod's own look rows, never a row another mod puts in every
                 float menu ("Search Option" on the full list, which changed nothing: Industrial -> Industrial).

--mutate is implicit: each guard is run again on text with the original defect restored and must go red.
Exit 0 PASS, 1 FAIL. Prints each guard's cases read."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
JB = os.path.join(os.path.dirname(HERE), "bridgetools", "JawaBench.BridgeTools", "JawaBenchGssPlaytest.cs")


def read(p):
    return open(p, encoding="utf-8").read()


def body(text, header, close="\n        }\n"):
    i = text.find(header)
    if i < 0:
        return None
    j = text.find(close, i)
    return text[i:j if j > 0 else len(text)]


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def sources():
    """Every C# file that can build cords outside Core: GSS Source (not Core/, SelfTest/, bin, obj) and the JawaBench playtest."""
    out = {}
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("Core", "SelfTest", "bin", "obj")]
        for n in files:
            if n.endswith(".cs"):
                p = os.path.join(root, n)
                out[os.path.relpath(p, os.path.dirname(HERE))] = read(p)
    out[os.path.relpath(JB, os.path.dirname(HERE))] = read(JB)
    return out


COMP = os.path.join("GimmeSomeSlack", "Source", "RM_MapComponent_CordGraph.cs")
MBO = "internal static BuildOptions MapBuildOptions(Map map"
FRESH = "internal static List<LaidPiece> FreshBuild(Map map)"
# StyleProbe prints the settings' default pile (a read of the setting, not a build)
ALLOW_SETTINGS = re.compile(r"F\(\"pileArt\", S\(GimmeSomeSlackSettings\.BuildOptions\(\)\.Pile\.ToString\(\)\)\)")


def check_inputs(files):
    out, read_n = [], 0
    comp = files.get(COMP, "")
    mbo = body(comp, MBO)
    fresh = body(comp, FRESH)
    if mbo is None:
        return ["RM_MapComponent_CordGraph has no MapBuildOptions(Map ...): no one recipe for a map's build inputs"], 0
    for need in ("GimmeSomeSlackSettings.BuildOptions()", "StraightPlugIds = CordWorldAdapter.TapIds(map)", "ConduitStylePicker.CellStyles(map)", ".UseLooks("):
        if need not in mbo:
            out.append("MapBuildOptions lacks " + need)
    if fresh is None or "MapBuildOptions(map" not in fresh or "new CordBuilder()" not in fresh:
        out.append("RM_MapComponent_CordGraph.FreshBuild(Map) is missing or does not build a new CordBuilder on MapBuildOptions")
    reb = body(comp, "public void Rebuild(bool complete)")
    if reb is None or "MapBuildOptions(map" not in reb:
        out.append("production Rebuild does not take its options from MapBuildOptions")
    for name, text in sorted(files.items()):
        t = strip_comments(text)
        if name == COMP:
            # the one recipe and the fresh build are the only places in the component that may name the raw inputs
            t = t.replace(strip_comments(mbo), "").replace(strip_comments(fresh or ""), "")
            t = t.replace("private readonly CordBuilder builder = new CordBuilder();", "")
        read_n += 1
        t2 = ALLOW_SETTINGS.sub("", t)
        if re.search(r"GimmeSomeSlackSettings\.BuildOptions\(\)", t2):
            out.append(name + ": builds options from bare settings (take MapBuildOptions)")
        if re.search(r"\bPileAt\s*=|\bPlugBootAt\s*=", t):
            out.append(name + ": sets PileAt/PlugBootAt itself (the look rule is Core BuildOptions.UseLooks, reached via MapBuildOptions)")
        if re.search(r"new\s+(?:GCore\.)?CordBuilder\s*\(\s*\)", t):
            out.append(name + ": makes its own CordBuilder (a from-scratch build is RM_MapComponent_CordGraph.FreshBuild)")
    jb = files[os.path.relpath(JB, os.path.dirname(HERE))]
    jfresh = body(jb, "internal static Dictionary<string, object> Fresh(Map m)", "\n            }\n")
    if jfresh is None or "RM_MapComponent_CordGraph.FreshBuild(m)" not in jfresh:
        out.append("JawaBench GssLambdaHome.Fresh does not compare with RM_MapComponent_CordGraph.FreshBuild(m)")
    elif '"extra "' not in jfresh:
        out.append("JawaBench Fresh names only fresh-side keys: a live-only key is never shown")
    return out, read_n


def check_settle(jb):
    out = []
    srb = body(jb, "private static IEnumerable<PWait> GScnSaveReloadB(GCtx c)")
    if srb is None:
        return ["no GScnSaveReloadB"]
    i_read = srb.find("GSnapshot(c.map")
    i_settle = srb.find("GSettle(c.map")
    if i_read < 0 or i_settle < 0 or i_settle > i_read:
        out.append("save_reload_b reads the loaded cords before GSettle (a fixed frame count reads a half-laid map)")
    if "GFrames(6)" in srb:
        out.append("save_reload_b still waits a fixed 6 frames")
    settle = body(jb, "private static IEnumerable<PWait> GSettle(Map m")
    if settle is None or "Builds" not in settle:
        out.append("GSettle does not wait for the component's first build (after a load LastPending reads 0 before any build)")
    if '"settle"' not in srb:
        out.append("save_reload_b does not record how the settle ended (frames, pending)")
    return out


def check_pick(jb):
    m = re.search(r"FloatMenuOption pick = (.*?);", jb)
    if not m:
        return ["no designator look pick found"]
    expr = m.group(1)
    out = []
    if "GLookRow(" not in expr:
        out.append("the designator look pick takes any row not marked current: " + expr.strip())
    if body(jb, "private static bool GLookRow(") is None:
        out.append("no GLookRow helper")
    return out


def main():
    files = sources()
    jbname = os.path.relpath(JB, os.path.dirname(HERE))
    jb = files[jbname]
    f_in, n = check_inputs(files)
    f_set = check_settle(jb)
    f_pick = check_pick(jb)
    fails = f_in + f_set + f_pick
    print("fresh inputs: %d file(s) read, %d finding(s)" % (n, len(f_in)))
    print("settle: %d finding(s)   look pick: %d finding(s)" % (len(f_set), len(f_pick)))
    # can-fail: the visit-2 defects restored in memory must each be caught
    mut = dict(files)
    mut[jbname] = jb.replace("GSS.RM_MapComponent_CordGraph.FreshBuild(m)",
                             "new GCore.CordBuilder().Build(GSS.CordWorldAdapter.Snapshot(m), GSS.GimmeSomeSlackSettings.BuildOptions(), cc => GSS.CordWorldAdapter.IsLive(m, cc))", 1)
    if mut[jbname] == jb or not check_inputs(mut)[0]:
        fails.append("instrument blind: the bare-settings playtest fresh build not caught")
    comp = files[COMP]
    mut = dict(files)
    mut[COMP] = comp.replace(".UseLooks(", ".UseLooksNot(", 1)
    if mut[COMP] == comp or not check_inputs(mut)[0]:
        fails.append("instrument blind: MapBuildOptions without the run looks not caught")
    probe_name = os.path.join("GimmeSomeSlack", "Source", "GimmeSomeSlackProbe.cs")
    mut = dict(files)
    mut[probe_name] = files[probe_name] + "\nclass X { void Y() { var o = new BuildOptions(); o.PileAt = null; } }\n"
    if not check_inputs(mut)[0]:
        fails.append("instrument blind: a second copy of the look rule not caught")
    i = jb.find("GSettle(c.map")
    if i < 0 or not check_settle(jb[:i] + "GFrames(6)" + jb[i + len("GSettle(c.map"):]):
        fails.append("instrument blind: the fixed-frame save_reload_b read not caught")
    m = re.search(r"FloatMenuOption pick = (.*?);", jb)
    if not m or not check_pick(jb.replace(m.group(0), 'FloatMenuOption pick = dopts?.FirstOrDefault(o => !o.Label.Contains("(current)"));', 1)):
        fails.append("instrument blind: the first-not-current pick not caught")
    for f in fails:
        print("FAIL", f)
    print("selftest_gss_fresh_build_inputs:", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
