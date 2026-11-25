#!/usr/bin/env python3
"""Offline checks for the patch switch (JawaBenchPatchSwitch.cs). No game or bridge.

The C# harness compiles the production pure core (JawaBenchPatchSwitchCore.cs) with
PatchSwitchSelfTest/Program.cs on plain .NET. The source checks hold the Harmony side of the
tool to what the core cannot see: one Unpatch of one method, the deviation entry, the repay,
the refusal before any write, and the counter order that answers inlining (04_live_tuning.md E9).
RM_PATCH_SWITCH_SOURCE can point at a planted copy of the repo tree.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = Path(os.environ.get("RM_PATCH_SWITCH_SOURCE", ROOT))
BRIDGE = SOURCE / "src/RimMandrake/bridgetools/JawaBench.BridgeTools"
TOOL = BRIDGE / "JawaBenchPatchSwitch.cs"
CORE = BRIDGE / "JawaBenchPatchSwitchCore.cs"
PROGRAM = SOURCE / "src/RimMandrake/bridgetools/PatchSwitchSelfTest/Program.cs"


def code(path):
    if not path.is_file():
        return None
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", path.read_text(), flags=re.S)


def wired(path, *parts):
    text = code(path)
    if text is None:
        return f"{path.name} is missing"
    return next((f"{path.name} is missing {part}" for part in parts if part not in text), None)


def dotnet_and_native():
    dotnet = shutil.which("dotnet")
    windows = not dotnet and shutil.which("wslpath")
    if windows:
        from glob import glob
        dotnet = next(iter(sorted(glob("/mnt/c/Users/*/.dotnet/dotnet.exe")) +
                           [p for p in ("/mnt/c/Program Files/dotnet/dotnet.exe",) if os.path.isfile(p)]),
                      shutil.which("dotnet.exe"))
    if not dotnet:
        raise RuntimeError("no .NET SDK could be located")

    def native(path):
        return subprocess.check_output(["wslpath", "-w", str(path)], text=True).strip() if windows else str(path)
    return dotnet, native, windows


def units():
    dotnet, native, windows = dotnet_and_native()
    # As selftest_deviation_record.py: a Windows SDK builds on Windows-native agent storage, not on \\wsl$.
    tmp_root = ROOT / ".git"
    if windows:
        tmp_root = Path(subprocess.check_output(
            [sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"), "rimmandrake"],
            text=True).strip()) / "scratch"
        tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="patchswitch-", dir=tmp_root) as tmp:
        d = Path(tmp)
        for path in (PROGRAM, CORE):
            shutil.copy2(path, d)
        (d / "Test.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework>'
            '<OutputType>Exe</OutputType></PropertyGroup></Project>')
        env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1")
        build = subprocess.run([dotnet, "build", native(d / "Test.csproj"), "--disable-build-servers", "-v:q"],
                               cwd=d, env=env, capture_output=True, text=True, timeout=180)
        if build.returncode:
            raise RuntimeError(build.stdout + build.stderr)
        run = subprocess.run([dotnet, native(d / "bin/Debug/net8.0/Test.dll")],
                             cwd=d, env=env, capture_output=True, text=True, timeout=60)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
    return dict(line[2:].split(" ", 1) for line in run.stdout.splitlines() if line.startswith("U "))


def unit(name):
    def test(outcomes):
        return outcomes.get(name)
    test.__name__ = "t_unit_" + name.replace("-", "_")
    return test


def t_core_is_pure(_):
    text = code(CORE)
    if text is None:
        return "JawaBenchPatchSwitchCore.cs is missing"
    bad = [u for u in re.findall(r"^\s*using\s+([A-Za-z.]+)\s*;", text, re.M) if u.split(".")[0] in ("HarmonyLib", "Verse", "RimWorld", "UnityEngine")]
    return f"the core uses {', '.join(bad)}" if bad else "ok"


def t_off_takes_one_method_off_one_original(_):
    text = code(TOOL)
    if text is None:
        return "JawaBenchPatchSwitch.cs is missing"
    if "UnpatchAll" in text:
        return "the switch calls UnpatchAll, which takes every patch of an owner off"
    return wired(TOOL, "new Harmony(row.Owner).Unpatch(spec.Original, spec.Method)") or "ok"


def t_on_puts_back_kind_priority_before_after(_):
    return wired(TOOL, "new HarmonyMethod(spec.Method) { priority = row.Priority, before = row.Before, after = row.After }",
                 'prefix: row.Kind == "prefix" ? again : null', 'postfix: row.Kind == "postfix" ? again : null',
                 'transpiler: row.Kind == "transpiler" ? again : null', 'finalizer: row.Kind == "finalizer" ? again : null',
                 "new Harmony(row.Owner).Patch(spec.Original") or "ok"


def t_off_is_a_put_back_overlay_entry_that_taints(_):
    return wired(TOOL, 'new D.Entry("overlay", "PUT BACK", "process", row.Id, null, "off", () => State(spec), v => Switch(spec, v))',
                 "JawaBenchDeviations.ApplySettings(") or "ok"


def t_on_repays_its_entry_only(_):
    return wired(TOOL, "JawaBenchDeviations.Record.Repay(") or "ok"


def t_off_refuses_before_it_writes(_):
    text = code(TOOL)
    if text is None:
        return "JawaBenchPatchSwitch.cs is missing"
    line = re.search(r"P\.OffRefusal\(picked, JawaBenchPatchSwitch\.SaveRefusal\) \?\? JawaBenchPatchSwitch\.Off\(", text)
    if not line:
        return "off does not run OffRefusal (with the save refusal) before Off"
    save = re.search(r"internal static string SaveRefusal\(\)(.*?)\n        }", text, re.S)
    if not save or "JawaBenchDeviations.CanonicalRefusal()" not in save[1] or "JawaBenchSafetyCore.Test" not in save[1]:
        return "the save refusal does not read the profile and CanonicalRefusal"
    return "ok"


def t_patch_counter_is_armed_before_the_original_is_rebuilt(_):
    text = code(TOOL)
    if text is None:
        return "JawaBenchPatchSwitch.cs is missing"
    arm = re.search(r"internal static string Arm\(Spec spec\)(.*?)\n        }", text, re.S)
    if not arm:
        return "no Arm"
    body = arm[1]
    marks = ["counter.Patch(spec.Method", "counter.Unpatch(spec.Original", "counter.Patch(spec.Original"]
    where = [body.find(m) for m in marks]
    if -1 in where:
        return "Arm is missing " + marks[where.index(-1)]
    if where != sorted(where):
        return "Arm does not patch the patch method first and then rebuild the original's counter (E9)"
    return "ok"


def t_counter_hooks_are_contained(_):
    text = code(TOOL)
    if text is None:
        return "JawaBenchPatchSwitch.cs is missing"
    for hook in ("CountPatchPre", "CountOriginalPre"):
        m = re.search(r"private static void " + hook + r"\(MethodBase __originalMethod\)\s*{\s*try\s*{\s*Calls\.Hit\(Key\(__originalMethod\)\);\s*}\s*"
                      r"catch \(Exception\)\s*{\s*Calls\.Fault\(\);\s*}\s*}", text)
        if not m:
            return hook + " is not a void prefix whose whole body is a contained Calls.Hit"
    return "ok"


def t_tool_name_is_registered_once(_):
    hits = []
    for path in BRIDGE.glob("*.cs"):
        if '"jawa/patch_switch"' in path.read_text():
            hits.append(path.name)
    return "ok" if hits == ["JawaBenchPatchSwitch.cs"] else f"the tool name is in {hits or 'no file'}"


UNITS = ("id", "select", "ours", "jawabench", "off-refusals", "on-refusals", "count-refusals", "counters", "order-kept")


def main():
    tests = [unit(n) for n in UNITS] + [
        t_core_is_pure, t_off_takes_one_method_off_one_original, t_on_puts_back_kind_priority_before_after,
        t_off_is_a_put_back_overlay_entry_that_taints, t_on_repays_its_entry_only, t_off_refuses_before_it_writes,
        t_patch_counter_is_armed_before_the_original_is_rebuilt, t_counter_hooks_are_contained, t_tool_name_is_registered_once,
    ]
    try:
        outcomes = units() if CORE.is_file() and PROGRAM.is_file() else {}
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"COULD NOT LOOK at the patch switch core: {exc}")
        return 1
    passed = 0
    for test in tests:
        result = test(outcomes)
        passed += result == "ok"
        print(f"{'PASS' if result == 'ok' else 'FAIL'} {test.__name__}: {result or 'the unit did not run'}")
    print(f"patch switch: {passed} checks passed of {len(tests)} ({len(outcomes)} C# units read)")
    return int(passed != len(tests))


if __name__ == "__main__":
    sys.exit(main())
