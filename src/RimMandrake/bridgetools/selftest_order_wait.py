#!/usr/bin/env python3
"""Compile the bridge wait policy with a .NET 8 SDK and check its tool wiring. No game or bridge."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CS = HERE / "JawaBench.BridgeTools"
CORE = CS / "JawaBenchWaitCore.cs"
WAITER = CS / "JawaBenchWait.cs"
WAIT_TOOLS = {
    "JawaBenchJobTools.cs": ("OrderedJob", "DoBillNow"),
    "JawaBenchTerrainTools.cs": ("OrderPawn",),
    "JawaBenchZoneTools.cs": ("PrioritizedWork",),
    "JawaBenchAbilityTools.cs": ("PawnUseAbility", "PawnUseVerb"),
    "JawaBenchFlightTools.cs": ("PawnFlight",),
    "JawaBenchMapCompTiming.cs": ("MapCompTiming",),
}
PROJECT = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="CORE_PATH" />
    <Compile Include="WAITER_PATH" />
  </ItemGroup>
</Project>"""
PROGRAM = """
using System;
using JawaBench.BridgeTools;
using static JawaBench.BridgeTools.JawaBenchWaitCore;

static void Check(string name, string want, string got)
{
    if (want != got) throw new Exception($"{name}: expected {want ?? "(wait)"}, got {got ?? "(wait)"}");
}

switch (args[0])
{
    case "pause":
        Check("first paused sample", null, End(0, 60, false, false, true, false));
        Check("paused from start", "paused", End(0, 60, false, false, true, true));
        Check("first pause midway", null, End(17, 60, false, false, true, false));
        Check("paused midway", "paused", End(17, 60, false, false, true, true));
        Check("call set speed", null, End(0, 60, false, true, true, true));
        Check("call set speed and stalled", "timeout", End(0, 60, true, true, true, true));
        Check("unpaused and stalled", null, End(0, 60, false, false, false, false));
        Check("unpaused stalled to limit", "timeout", End(0, 60, true, false, false, false));
        Check("zero tick wait", "ticks", End(0, 0, false, false, true, false));
        Check("target tick on deadline", "ticks", End(60, 60, true, false, false, false));
        await JawaBenchTerrainTools.TestWait("paused", 1, 0, false, false,
            (100, true, 1), (100, true, 1));
        await JawaBenchTerrainTools.TestWait("paused", 3, 17, false, false,
            (100, false, 1), (110, true, 1), (117, true, 1), (117, true, 1));
        await JawaBenchTerrainTools.TestWait("ticks", 3, 60, true, false,
            (100, true, 1), (100, true, 1), (100, false, 1), (160, false, 1));
        break;
    case "arrival":
        Check("already there", "arrived", End(0, 300, false, false, true, false, 0));
        Check("one still en route", null, End(20, 300, false, false, false, false, 1));
        Check("last pawn arrived or gone", "arrived", End(30, 300, false, false, false, false, 0));
        Check("no pawn", null, End(30, 300, false, false, false, false));
        Check("arrival disabled waits for ticks", "ticks", End(300, 300, false, false, false, false));
        Check("arrival on deadline", "arrived", End(300, 300, true, false, false, false, 0));
        await JawaBenchTerrainTools.TestWait("arrived", 0, 0, false, true, (100, true, 0));
        // One pawn is en route, then disappears from the order map.
        await JawaBenchTerrainTools.TestWait("arrived", 1, 30, false, true,
            (100, false, 1), (130, false, 0));
        await JawaBenchTerrainTools.TestWait("ticks", 2, 60, false, false,
            (100, false, 1), (130, false, 0), (160, false, 0));
        break;
}
"""
STUBS = """
using System;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace Verse
{
    static class Current { public static object Game = new object(); }
    static class Find { public static TickManager TickManager = new TickManager(); }
    class TickManager { public int TicksGame; public bool Paused; }
}

namespace RimBridgeServer.Sdk
{
    interface IRimBridgeContext { FakeMainThread MainThread { get; } }
    class FakeMainThread : IRimBridgeContext
    {
        public FakeMainThread MainThread => this;
        public (int ticks, bool paused, int pending)[] Samples;
        public int Reads, Pending;

        public Task<T> InvokeAsync<T>(Func<T> read, CancellationToken token)
        {
            token.ThrowIfCancellationRequested();
            (Find.TickManager.TicksGame, Find.TickManager.Paused, Pending) = Samples[Reads++];
            return Task.FromResult(read());
        }
    }
}

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        internal static async Task TestWait(string end, int polls, int ticks, bool speedChanged,
            bool stopOnArrival, params (int ticks, bool paused, int pending)[] samples)
        {
            var main = new FakeMainThread { Samples = samples };
            var result = await WaitForGameTicks(main, CancellationToken.None, 100, 60, 1,
                speedChanged, stopOnArrival ? () => main.Pending : null, pollMs: 0);
            if (result.waitEnded != end || result.polls != polls || result.ticks != 100 + ticks
                || main.Reads != polls + 1 || (end == "paused" && !result.pausedDuringWait))
                throw new Exception($"expected {end} after {polls} delayed polls and {ticks} ticks, got {result}");
        }
    }
}
"""


def tool(filename, name):
    code = (CS / filename).read_text(encoding="utf-8")
    return re.split(r"^        \[Tool\(", code.split(f"Task<object> {name}(", 1)[1], maxsplit=1, flags=re.M)[0]


def core_case(case):
    for source in (CORE, WAITER):
        if not source.is_file():
            return f"{source.name} is missing"
    with tempfile.TemporaryDirectory(prefix="order-wait-", dir=ROOT) as tmp:
        path = Path(tmp)
        project = PROJECT.replace("CORE_PATH", escape(CORE.as_posix())).replace("WAITER_PATH", escape(WAITER.as_posix()))
        (path / "OrderWait.csproj").write_text(project, encoding="utf-8")
        (path / "Program.cs").write_text(PROGRAM, encoding="utf-8")
        (path / "Stubs.cs").write_text(STUBS, encoding="utf-8")
        try:
            result = subprocess.run(["dotnet", "run", "--project", str(path / "OrderWait.csproj"), "--", case],
                                    cwd=path, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as error:
            return f".NET 8 harness did not run ({error})"
    return (result.stdout + result.stderr).strip() if result.returncode else None


def t_paused_wait_stops():
    for filename, names in WAIT_TOOLS.items():
        for name in names:
            body = tool(filename, name)
            if "WaitForGameTicks(" not in body or "waitEnded" not in body:
                return f"{name} has no pause-aware tick wait and waitEnded reply"
    return core_case("pause")


def t_arrival_requires_opt_in():
    body = tool("JawaBenchTerrainTools.cs", "OrderPawn")
    if not re.search(r"\bbool stopOnArrival\s*=\s*false\b", body):
        return "OrderPawn has no stopOnArrival=false parameter"
    if not re.search(r"stopOnArrival\s*\?\s*\(\)\s*=>\s*pawns\.Count\(pawn => !Gone\(pawn\) && pawn\.Position != dest\)", body):
        return "OrderPawn does not feed a pending-pawn count to the opt-in wait"
    if 'pawns.Count == 0) return Fail("No pawns matched.")' not in body:
        return "OrderPawn does not refuse an empty pawn selection"
    schema = json.loads((HERE / "../Utils/northstar_driver/tool_schemas.json").read_text(encoding="utf-8"))
    args = schema["tools"]["jawa/order_pawn"]
    if "stopOnArrival" not in args["parameters"] or "stopOnArrival" in args["required"]:
        return "tool_schemas.json does not list stopOnArrival as optional"
    return core_case("arrival")


def main():
    tests = [t_paused_wait_stops, t_arrival_requires_opt_in]
    failed = 0
    for test in tests:
        problem = test()
        failed += problem is not None
        name = test.__name__[2:]
        print(f"FAIL {name}: {problem}" if problem else f"ok   {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
