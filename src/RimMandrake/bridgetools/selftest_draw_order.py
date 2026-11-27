#!/usr/bin/env python3
"""Selftest: the draw-order readings of the bridge (JawaBenchDrawOrderCore.cs and its game halves, jawa/cell_draw_census in
JawaBenchDrawCensusTools.cs and jawa/pawn_render_nodes in JawaBenchPawnRenderTools.cs).

Item RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER. Unity sorts a transparent draw by its mesh's bounds
centre, and a section layer puts every print of one material into one sub-mesh, so a height change of one print inside it may
change nothing on screen. The census reads each sub-mesh's bounds and vertex heights against a probe height; the pawn read says
how a pawn is drawn this frame (one cached atlas quad, or one draw per render node) and each node's drawn height.

Checks: (1) every unit of DrawOrderSelfTest passes on the production core; (2) each planted fault (one rule broken in a copy of
the core) turns its named unit red; (3) each tool's game half calls its core rule inside its one main-thread hop, so a tool
cannot drift from the rule the units prove. No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_draw_order.py [--no-plants]"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = "JawaBenchDrawOrderCore.cs"
PROJ = os.path.join(HERE, "DrawOrderSelfTest", "DrawOrderSelfTest.csproj")
N_UNITS = 16

# (planted fault: old -> new in the core, the unit that must go red)
PLANTS = [
    ("if (s.n == 0) { s.min = y; s.max = y; }", "if (s.n == 0) { s.min = 0f; s.max = y; }", "span_first_vertex_counts"),
    ("if (y < s.min) s.min = y;", "if (y > s.min) s.min = y;", "span_min_max_of_every_vertex"),
    ("public bool Empty => n == 0;", "public bool Empty => n < 0;", "span_empty_is_empty"),
    ("public float Centre => (min + max) * 0.5f;", "public float Centre => min;", "span_centre_is_mid_of_ends"),
    ("if (centre > y + eps) return \"above\";", "if (centre > y) return \"above\";", "relation_level_inside_eps"),
    ("if (centre < y - eps) return \"below\";", "if (centre < y - eps * 4f) return \"below\";", "relation_just_past_eps"),
    ("if (centre > y + eps) return \"above\";", "if (centre < y + eps) return \"above\";", "relation_above_below"),
    ("internal const float Eps = 0.0001f;", "internal const float Eps = 0.001f;", "eps_below_one_node_layer"),
    ("return !s.Empty && s.min < y - eps && s.max > y + eps;", "return !s.Empty && (s.min < y - eps || s.max > y + eps);", "straddles_not_one_side"),
    ("return !s.Empty && s.min < y - eps && s.max > y + eps;", "return s.min < y - eps && s.max > y + eps || s.Empty;", "straddles_empty_never"),
    ("return !s.Empty && s.min < y - eps && s.max > y + eps;", "return !s.Empty && s.min <= y + eps && s.max > y + eps;", "straddles_touching_end_not"),
    ("return !s.Empty && s.min < y - eps && s.max > y + eps;", "return !s.Empty && s.min < y - eps && s.max > y + 100f;", "straddles_both_sides"),
    ("if (!valid) return \"notPreRendered\";", "if (!valid && !draw) return \"notPreRendered\";", "path_not_prerendered"),
    ("if (!draw) return \"hidden\";", "if (!draw && !useCached) return \"hidden\";", "path_hidden"),
    ("return useCached ? \"cachedAtlas\" : \"nodes\";", "return \"nodes\";", "path_cached_atlas"),
    ("return useCached ? \"cachedAtlas\" : \"nodes\";", "return \"cachedAtlas\";", "path_nodes"),
]

# (tool, its file, the calls that must sit inside its main-thread hop)
WIRING = [
    ("jawa/cell_draw_census", "JawaBenchDrawCensusTools.cs",
     [r"JawaBenchDrawOrderCore\.Span\(", r"JawaBenchDrawOrderCore\.Relation\(", r"JawaBenchDrawOrderCore\.Straddles\(",
      r"\.mesh\.bounds", r"GetInstanceID\(\)"]),
    ("jawa/pawn_render_nodes", "JawaBenchPawnRenderTools.cs",
     [r"JawaBenchDrawOrderCore\.DrawPath\(", r"JawaBenchDrawOrderCore\.Relation\(", r"\"drawRequests\"", r"\"results\"",
      r"preDrawnComputedMatrix", r"ZoomRootSize", r"renderQueue"]),
]


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def units(core_text):
    """Build the harness with this core text and run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="DrawOrder_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_draw_order.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="DrawOrderSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
        if rc:
            raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
        dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\DrawOrderSelfTest.dll"
        # hang guard: a planted core may loop; a real run of a sibling harness takes under a second (measured 2026-11-27)
        pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True,
                                           cwd="/mnt/d/Luke/dev" if os.path.isdir("/mnt/d/Luke/dev") else None, timeout=180)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built or run: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U ") and not ln.startswith("U-count"):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s %s" % (len(out), N_UNITS, pr.stdout[-300:], pr.stderr[-300:]))
    return out


def nocomment(s):
    return re.sub(r"//[^\n]*", "", s)


def tool_body(text, tool):
    s = nocomment(text)
    i = s.find('"%s"' % tool)
    j = s.find("[Tool(", i + 1) if i >= 0 else -1
    return s[i:j if j > i else len(s)] if i >= 0 else ""


def wiring():
    bad = []
    for tool, fname, pats in WIRING:
        try:
            body = tool_body(read(os.path.join(CS, fname)), tool)
        except OSError as e:
            bad.append("could not read %s: %s" % (fname, e))
            continue
        if not body:
            bad.append("%s is not declared in %s" % (tool, fname))
            continue
        if body.count("MainThread.InvokeAsync") != 1:
            bad.append("%s must have exactly one main-thread hop" % tool)
            continue
        hop = body[body.index("MainThread.InvokeAsync"):]
        for p in pats:
            if not re.search(p, hop):
                bad.append("%s lacks /%s/ in its main-thread hop" % (tool, p))
    return bad


def main(argv):
    fails, plants = [], "--no-plants" not in argv
    try:
        core = read(os.path.join(CS, CORE))
        clean = units(core)
    except (OSError, Unmeasured) as e:
        print("selftest_draw_order: UNMEASURED: %s" % e)
        return 1
    for name, res in sorted(clean.items()):
        if res != "ok":
            fails.append("unit %s on the production core: %s" % (name, res))
    fails += wiring()
    if plants:
        for old, new, unit in PLANTS:
            if old not in core:
                fails.append("plant for %s no longer matches the core (%r)" % (unit, old[:40]))
                continue
            try:
                got = units(core.replace(old, new, 1))
            except Unmeasured as e:
                fails.append("plant for %s: UNMEASURED: %s" % (unit, e))
                continue
            if got.get(unit, "").startswith("ok"):
                fails.append("plant for %s stayed green" % unit)
    for f in fails:
        print("  FAIL " + f)
    print("selftest_draw_order: %s (%d units, %d plants, %d tool wirings)" % (
        "FAIL" if fails else "PASS", len(clean), len(PLANTS) if plants else 0, len(WIRING)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
