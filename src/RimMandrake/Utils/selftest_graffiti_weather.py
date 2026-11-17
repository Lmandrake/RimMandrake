#!/usr/bin/env python3
# selftest-timeout: 600   (one staged net8 build of the Graffiti kernel harness, ~1-2 min; --mutants adds three more)
"""T_WEATHER_OFFLINE (RIMMANDRAKE_PIN_GRAFFITI_WEATHER_FADE_CURVE_OFFLINE): Graffiti's paint weathering pinned offline, no game.

Two halves:
  kernel  RM_GraffitiKernel.WeatherDays / WeatherFade / WeatherStep (src/RimMandrake/Graffiti/Source/Kernel/RM_GraffitiKernel.cs), run as
          the `weather` family of the kernel fuzz harness (src/RimMandrake/Graffiti/Source/SelfTest/GraffitiFuzz.cs): a roofed mark
          outlives an open one for every GraffitiForm and craft; alpha (1 - fade) is 1 before 60% of a life and 0 at its end; the fade and
          its drawn step never come back. The family also runs its checks on six planted formula mutants and fails if any survives.
  source  the permanent-mark rule lives in Filth_Mark (Verse, cannot be loaded offline), so it is checked by a narrow source read:
          WeatherStepNow returns step 0 with fade 0 for a permanent mark before any weather is worked out; every write of weatherStep
          comes from WeatherStepNow; the only weathering-away Destroy is gated on WeatherStepNow's fade. And the life WeatherStepNow asks
          the kernel for is the mark's own: WeatherDays' `outdoors` is `!Map.roofGrid.Roofed(Position)` (the kernel proves roofed outlasts
          open, but an inverted argument in the caller turned that round and stayed green: blind challenge cycle 2,
          RIMMANDRAKE_CHECK_GRAFFITI_WEATHER_CALLER_ROOF_KERNEL_NEVER_SAW). Five planted source mutants must each turn that read red, every run.

    python3 src/RimMandrake/Utils/selftest_graffiti_weather.py [--mutants] [--fuzz-seed N]

--mutants also rebuilds the harness against three mutated copies of the kernel (roof and rain swapped, fade from 50%, never quite gone),
staged under the winbuild root, never the real file, and requires each to go red. Exit 0 = every check green; 1 = a check red; 2 = the
build or a source read could not be made (UNMEASURED).
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import graffiti_src_read as S  # noqa: E402
import winbuild  # noqa: E402

SOURCE = os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source")
SELFTEST = os.path.join(SOURCE, "SelfTest")
KERNEL = os.path.join(SOURCE, "Kernel")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGraffiti.SelfTest.csproj")
DLL_REL = "bin\\Release\\net8.0\\RimMandrakeGraffiti.SelfTest.dll"

# ---------------------------------------------------------------- the permanent-mark rule, by source read

def permanent_rule(sources):
    """-> list of failures (empty = the rule holds in this source)."""
    fails = []
    hits = S.find_method(sources, "WeatherStepNow")
    if len(hits) != 1:
        return ["UNREAD: expected one WeatherStepNow declaration, found %d" % len(hits)]
    _, params, body = hits[0]
    out = re.search(r"\bout\s+float\s+(\w+)", params)
    if not out:
        return ["UNREAD: WeatherStepNow has no `out float` fade"]
    fv = out.group(1)
    first_fade = re.search(r"\bRM_GraffitiKernel\.WeatherFade\s*\(|\b%s\s*=(?!=)(?!\s*0f\s*;)" % re.escape(fv), body)
    stop = first_fade.start() if first_fade else len(body)
    head = body[:stop]
    if not re.search(r"\b%s\s*=\s*0f\s*;" % re.escape(fv), head):
        fails.append("WeatherStepNow does not set fade to 0 before any weather is worked out")
    guarded = False
    for m in re.finditer(r"\bif\s*\(", head):
        close = S._match(head, m.end() - 1, "(", ")")
        if close < 0:
            continue
        cond = head[m.end():close]
        if re.match(r"\s*return\s+0\s*;", head[close + 1:]) and any(t in ("permanent", "this.permanent") for t in S.top_level_terms(cond, "||")):
            guarded = True
    if not guarded:
        fails.append("WeatherStepNow has no `if (permanent || ...) return 0;` ahead of the weather: a permanent mark would fade")
    # every write of weatherStep comes from WeatherStepNow (directly, or a local assigned from it in the same method)
    writes = 0
    for f, text in sorted(sources.items()):
        for m in re.finditer(r"\bweatherStep\s*=(?!=)\s*([^;]+);", text):
            writes += 1
            rhs = m.group(1).strip()
            if "WeatherStepNow(" in rhs:
                continue
            local = re.fullmatch(r"\w+", rhs)
            if local and re.search(r"\b(?:int|var)\s+%s\s*=\s*[\w.]*WeatherStepNow\s*\(" % re.escape(rhs), text[max(0, m.start() - 1500):m.start()]):
                continue
            fails.append("%s writes weatherStep = %s, not WeatherStepNow's step: a permanent mark could be drawn faded" % (f, rhs))
    if writes == 0:
        fails.append("UNREAD: no write of weatherStep found anywhere")
    # the weathering-away Destroy is gated on WeatherStepNow's fade
    gates = 0
    for f, text in sorted(sources.items()):
        for m in re.finditer(r"\bWeatherStepNow\s*\(\s*out\s+float\s+(\w+)\s*\)", text):
            v = m.group(1)
            window = text[m.end():m.end() + 1200]
            d = window.find(".Destroy(")
            if d < 0:
                continue
            gates += 1
            if not re.search(r"\bif\s*\(\s*%s\s*>=\s*1f\s*\)" % re.escape(v), window[:d]):
                fails.append("%s destroys a weathered mark on something other than WeatherStepNow's fade >= 1" % f)
    if gates == 0:
        fails.append("UNREAD: no weathering-away Destroy found beside a WeatherStepNow call")
    # the life asked for is this mark's, under its own roof: WeatherDays(form, craft, outdoors = !roofed at the mark's cell, id)
    call = re.search(r"\bRM_GraffitiKernel\.WeatherDays\s*\(", body)
    if not call:
        fails.append("UNREAD: WeatherStepNow does not call RM_GraffitiKernel.WeatherDays")
    else:
        close = S._match(body, call.end() - 1, "(", ")")
        args = S.top_level_terms(body[call.end():close], ",") if close > 0 else []
        if len(args) != 4:
            fails.append("UNREAD: WeatherStepNow's WeatherDays call has %d arguments, not 4" % len(args))
        elif not re.fullmatch(r"!\s*(?:this\.)?Map\s*\.\s*roofGrid\s*\.\s*Roofed\s*\(\s*(?:this\.)?Position\s*\)", args[2].strip()):
            fails.append("WeatherStepNow passes outdoors = `%s`, not `!Map.roofGrid.Roofed(Position)`: the roof could be read the wrong way round" % args[2].strip())
    return fails


SOURCE_MUTANTS = [
    ("the guard forgets permanent", "Filth_Mark.cs", "if (permanent || placedTick == -1", "if (placedTick == -1"),
    ("the guard inverted", "Filth_Mark.cs", "if (permanent || placedTick == -1", "if (!permanent && placedTick == -1"),
    ("a step written from age, not WeatherStepNow", "GraffitiSocial.cs", "m.weatherStep = step;", "m.weatherStep = 4;"),
    ("weathered away by age alone", "GraffitiSocial.cs", "if (fade >= 1f)", "if (Find.TickManager.TicksGame - m.placedTick > 3600000)"),
    ("the roof read the wrong way round", "Filth_Mark.cs", "!Map.roofGrid.Roofed(Position), thingIDNumber", "Map.roofGrid.Roofed(Position), thingIDNumber"),
]


def source_half():
    sources = S.read_source(SOURCE)
    fails = permanent_rule(sources)
    unread = [f for f in fails if f.startswith("UNREAD")]
    for f in fails:
        print("FAIL permanent rule: " + f)
    if not fails:
        print("permanent rule: a permanent mark never fades (WeatherStepNow guard, %s)" % "every weatherStep write and the weathering-away Destroy read")
    blind = []
    for name, rel, old, new in SOURCE_MUTANTS:
        if rel not in sources or old not in sources[rel]:
            blind.append("mutant '%s': its anchor is gone from %s (re-anchor it)" % (name, rel))
            continue
        mutated = dict(sources)
        mutated[rel] = sources[rel].replace(old, new, 1)
        red = permanent_rule(mutated)
        print("  source mutant '%s': %s" % (name, "RED (caught)" if red else "GREEN (survived)"))
        if not red:
            blind.append("mutant '%s' survived the permanent-rule read" % name)
    for b in blind:
        print("FAIL " + b)
    return (2 if unread else 1) if (fails or blind) else 0

# ---------------------------------------------------------------- the kernel half

KERNEL_MUTANTS = [
    ("roof and rain swapped", "float days = outdoors ? 22f : 44f;", "float days = outdoors ? 44f : 22f;"),
    ("fade from 50%", "float f = (ageDays / lifeDays - 0.6f) / 0.4f;", "float f = (ageDays / lifeDays - 0.5f) / 0.5f;"),
    ("never quite gone", "return f < 0f ? 0f : (f > 1f ? 1f : f);", "return f < 0f ? 0f : (f > 0.9f ? 0.9f : f);"),
]


def run_dll(dll_win, extra):
    return winbuild.run_interop([winbuild.dotnet_exe(), dll_win, "--fuzz-only", "weather", *extra], cwd=winbuild.BUILD_ROOT, timeout=300)


def kernel_mutants():
    """Rebuild the harness on a staged copy with one kernel mutation at a time -> list of survivors / UNREAD notes."""
    with open(os.path.join(KERNEL, "RM_GraffitiKernel.cs"), encoding="utf-8-sig") as fh:
        real = fh.read()
    stage = os.path.join(winbuild.BUILD_ROOT, "GraffitiWeatherMutant_%d" % os.getpid())
    src = os.path.join(stage, "Source")
    bad = []
    try:
        shutil.rmtree(stage, ignore_errors=True)
        shutil.copytree(SELFTEST, os.path.join(src, "SelfTest"), ignore=shutil.ignore_patterns("bin", "obj"))
        os.makedirs(os.path.join(src, "Kernel"))
        for f in ("GraffitiForm.cs", "GraffitiCategory.cs"):
            shutil.copy2(os.path.join(SOURCE, f), os.path.join(src, f))
        proj = os.path.join(src, "SelfTest", os.path.basename(CSPROJ))
        for name, old, new in KERNEL_MUTANTS:
            if real.count(old) != 1:
                bad.append("kernel mutant '%s': anchor not found once in the kernel (re-anchor it)" % name)
                continue
            with open(os.path.join(src, "Kernel", "RM_GraffitiKernel.cs"), "w", encoding="utf-8") as fh:
                fh.write(real.replace(old, new))
            rc = winbuild.run_dotnet(winbuild.win(proj), os.path.dirname(proj), "Release", [])
            if rc:
                bad.append("kernel mutant '%s': build failed (%d), not measured" % (name, rc))
                continue
            r = winbuild.run_interop_captured([winbuild.dotnet_exe(), winbuild.win(os.path.join(src, "SelfTest")) + "\\" + DLL_REL,
                                               "--fuzz-only", "weather"], cwd=winbuild.BUILD_ROOT, capture_output=True, text=True,
                                              errors="replace", timeout=300)
            first = next((l for l in (r.stdout or "").splitlines() if l.startswith("FAIL weather seed")), "")
            print("  kernel mutant '%s': %s %s" % (name, "RED (caught)" if r.returncode else "GREEN (survived)", first[:160]))
            if not r.returncode:
                bad.append("kernel mutant '%s' survived the weather family" % name)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return bad


def main(argv):
    src_rc = source_half()
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GraffitiWeatherSelfTest", extra_dirs=[KERNEL])
    if rc:
        print("T_WEATHER_OFFLINE: UNMEASURED - harness build failed (%d)" % rc)
        return 2
    extra = []
    if "--fuzz-seed" in argv:
        extra = ["--fuzz-seed", argv[argv.index("--fuzz-seed") + 1]]
    k_rc = run_dll(winbuild.staged_win(rec, SELFTEST) + "\\" + DLL_REL, extra)
    m_bad = kernel_mutants() if "--mutants" in argv else []
    for b in m_bad:
        print("FAIL " + b)
    parts = ["kernel weather family %s" % ("green" if k_rc == 0 else "RED"),
             "permanent rule %s" % {0: "green", 1: "RED", 2: "UNREAD"}[src_rc]]
    if "--mutants" in argv:
        parts.append("kernel mutants %s" % ("all red" if not m_bad else "%d not caught" % len(m_bad)))
    ok = k_rc == 0 and src_rc == 0 and not m_bad
    print("T_WEATHER_OFFLINE: %s (%s)" % ("PASS" if ok else ("UNMEASURED" if src_rc == 2 else "FAIL"), "; ".join(parts)))
    return 0 if ok else (2 if src_rc == 2 and k_rc == 0 else 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
