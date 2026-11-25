#!/usr/bin/env python3
"""Offline checks for the deviation record. No game or bridge.

The C# harness links the production core. Source checks also require the live
entry points to use it. RM_DEVIATION_SOURCE can point at a planted copy.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = Path(os.environ.get("RM_DEVIATION_SOURCE", ROOT))
BRIDGE = SOURCE / "src/RimMandrake/bridgetools/JawaBench.BridgeTools"
UTILS = SOURCE / "src/RimMandrake/Utils"
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/northstar_driver"))
from tool_schemas import parse_csharp


def wired(path, *parts):
    if not path.is_file():
        return f"{path.name} is missing"
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", path.read_text(), flags=re.S)
    return next((f"{path.name} is missing {part}" for part in parts if part not in code), None)


def settings_host():
    # Run the host's actual apply and (if present) expiry path with a fake Unity clock.
    code = LIVE.read_text()
    host = re.findall(r"^        (?:private const string Legacy[^\n]*|private static float _standaloneExpiry[^\n]*|"
                      r"internal static string Revert[^\n]*|internal static (?:string ApplySettings|void Frame)\(.*?^        })",
                      code, re.M | re.S)
    lease = re.search(r"DefaultLeaseS = (\d+)", (BRIDGE / "JawaBenchHandsCore.cs").read_text())[1]
    return "\n".join(host) + ("" if any("void Frame(" in part for part in host) else "internal static void Frame() {}") + f"""
        internal static class JawaBenchHandsCore {{ internal const float DefaultLeaseS = {lease}; }}
    """


def units():
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

    # A Windows SDK reading a \\wsl$ tree runs the harness past its 30 s hang guard (measured: >30 s there,
    # 8 s on D:), so its build goes to the machine's agent storage, a Windows-native folder.
    tmp_root = ROOT / ".git"
    if windows:
        tmp_root = Path(subprocess.check_output(
            [sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"), "rimmandrake"],
            text=True).strip()) / "scratch"
        tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="deviation-", dir=tmp_root) as tmp:
        d = Path(tmp)
        for path in (HERE / "DeviationSelfTest/Program.cs", BRIDGE / "JawaBenchDeviationCore.cs",
                     BRIDGE / "JawaBenchCondCore.cs"):
            shutil.copy2(path, d)
        (d / "SettingsHost.cs").write_text(
            "using System; using D = JawaBench.BridgeTools.JawaBenchDeviationCore;\n"
            "internal static partial class SettingsHost {\n" + settings_host() + "\n}")
        (d / "Test.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework>'
            '<OutputType>Exe</OutputType></PropertyGroup></Project>')
        env = dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT="1")
        build = subprocess.run([dotnet, "build", native(d / "Test.csproj"), "--disable-build-servers", "-v:q"],
                               cwd=d, env=env, capture_output=True, text=True, timeout=120)
        if build.returncode:
            raise RuntimeError(build.stdout + build.stderr)
        run = subprocess.run([dotnet, native(d / "bin/Debug/net8.0/Test.dll"), native(d)],
                             cwd=d, env=env, capture_output=True, text=True, timeout=30)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
    return dict(line[2:].split(" ", 1) for line in run.stdout.splitlines() if line.startswith("U "))


FIELDS = BRIDGE / "JawaBenchModSettingsFieldTools.cs"
LIVE = BRIDGE / "JawaBenchDeviations.cs"
HANDS = BRIDGE / "JawaBenchHands.cs"


def t_entries_apply_in_order_and_roll_back(units):
    return (wired(FIELDS, "JawaBenchDeviations.ApplySettings(", "JawaBenchDeviations.Setting(")
            or wired(HANDS, "JawaBenchDeviations.ApplyPlan(") or units.get("order"))


def t_failed_revert_marks_spoiled(units):
    return wired(HANDS, "JawaBenchDeviations.Record.Spoiled") or units.get("spoiled")


def t_taint_stays_after_revert(units):
    return wired(LIVE, "Scribe_Values.Look(ref tuned,") or units.get("taint")


def t_none_with_taint_is_not_clean(units):
    return (wired(UTILS / "scene.py", "rec.deviation = ", '"tainted"')
            or wired(HANDS, "JawaBenchDeviations.Revert(") or units.get("none"))


def t_receipt_lists_four_kinds_and_their_classes(units):
    return (wired(HANDS, 'd["deviation"] = JawaBenchDeviations.Record.Receipt()')
            or wired(LIVE, 'Widgets.Label(', '"OVERLAY "') or units.get("receipt"))


def t_save_dirt_clears_on_fixture_load(units):
    return wired(LIVE, "Record.Load(") or units.get("save")


def t_process_dirt_survives_fixture_load(units):
    return wired(LIVE, "Record.Load(") or units.get("process")


def t_const_is_refused_by_name(units):
    return wired(FIELDS, "JawaBenchDeviationCore.FieldRefusal(fi)") or units.get("const")


def t_static_readonly_is_refused_by_name(units):
    return wired(FIELDS, "JawaBenchDeviationCore.FieldRefusal(fi)") or units.get("readonly")


def t_canonical_save_refuses_overlay(units):
    return wired(LIVE, "JawaBenchCompanionSafety.LoadedSave(", "JawaBenchSafetyCore.IsCanonical") or units.get("canonical")


def t_second_holder_is_refused(units):
    return wired(HANDS, "Core.Admit(driver)") or units.get("holder")


def t_journal_precedes_first_write(units):
    return wired(LIVE, "deviation-journal.json") or units.get("journal")


def t_settings_write_to_disk_is_blocked(units):
    return wired(LIVE, "nameof(LoadedModManager.WriteModSettings)", "Record.BlocksSettings(") or units.get("disk")


def t_mod_writesettings_override_body_runs(units):
    # A mod's own WriteSettings override must keep running its body after a settings set:
    # LuminousPigment validation.py _apply (WriteSettings -> ApplySettings), BlueDesert weather_apply
    # (-> RM_BlueDesertWeatherTable.Apply, needs the config file) and FlowWorks live_session.py
    # b2_settings_dialog (disk round trip) all set with no session, then call WriteSettings.
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", LIVE.read_text(), flags=re.S) if LIVE.is_file() else ""
    if "nameof(Mod.WriteSettings)" in code or "typeof(Mod), \"WriteSettings\"" in code:
        return "the guard patches Mod.WriteSettings and its overrides, so an override's body never runs"
    return wired(LIVE, "nameof(LoadedModManager.WriteModSettings)") or units.get("override-body")


def t_other_hand_differs_from_compiled_default(units):
    return wired(FIELDS, "JawaBenchDeviations.ObserveDefault(") or units.get("default")


def t_standalone_settings_outlive_default_lease(units):
    result = units.get("standalone-lease")
    if result == "ok":
        return wired(HANDS, "Record.Holder == Core.Cur.Driver") or result
    return result


def t_standalone_writes_accept_two_callers(units):
    return units.get("standalone-callers")


def t_legacy_settings_replies_keep_their_shape(units):
    code = FIELDS.read_text().split("Task<object> ModSettingsField(", 1)[-1]
    if "deviation =" in code:
        return "legacy set replies acquired deviation"
    return wired(FIELDS, "new { profile = JawaBenchSafetyCore.Campaign, profileWhy = why }") or "ok"


def t_legacy_settings_refusals_keep_their_scope(units):
    if "no deviation frame driver" in LIVE.read_text():
        return "a settings write acquired a frame-driver prerequisite"
    if '"OVERLAY_HELD"' in HANDS.read_text():
        return "a plain session open refuses live standalone settings"
    return wired(HANDS, "if (!SettingsSessionOpen) return null;") or units.get("instance-readonly")


def t_companion_tool_schema_is_backward_compatible(units):
    snapshot = json.loads((UTILS / "northstar_driver/tool_schemas.json").read_text())["tools"]
    for path, name, parameters, required, optional in (
        (FIELDS, "jawa/mod_settings_field", {"action", "field", "key", "typeName", "value"}, ["typeName"], "driver"),
        (HANDS, "jawa/session", {"action", "bindings", "driver", "from", "leaseS"}, [], "overlay"),
    ):
        declared = parse_csharp(path.read_text())
        for label, schema in (("manifest", snapshot.get(name)), ("C#", declared.get(name))):
            if schema is None:
                return f"{name} is missing from {label}"
            if schema["required"] != required:
                return f"{name} {label} required {schema['required']}, expected {required}"
            if set(schema["parameters"]) != parameters | {optional}:
                return f"{name} {label} did not preserve old parameters plus optional {optional}"
    return "ok"


def main():
    tests = (
        t_entries_apply_in_order_and_roll_back,
        t_failed_revert_marks_spoiled,
        t_taint_stays_after_revert,
        t_none_with_taint_is_not_clean,
        t_receipt_lists_four_kinds_and_their_classes,
        t_save_dirt_clears_on_fixture_load,
        t_process_dirt_survives_fixture_load,
        t_const_is_refused_by_name,
        t_static_readonly_is_refused_by_name,
        t_canonical_save_refuses_overlay,
        t_second_holder_is_refused,
        t_journal_precedes_first_write,
        t_settings_write_to_disk_is_blocked,
        t_mod_writesettings_override_body_runs,
        t_other_hand_differs_from_compiled_default,
        t_standalone_settings_outlive_default_lease,
        t_standalone_writes_accept_two_callers,
        t_legacy_settings_replies_keep_their_shape,
        t_legacy_settings_refusals_keep_their_scope,
        t_companion_tool_schema_is_backward_compatible,
    )
    try:
        outcomes = units() if (BRIDGE / "JawaBenchDeviationCore.cs").is_file() else {}
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"COULD NOT LOOK at the deviation core: {exc}")
        return 1
    passed = 0
    for test in tests:
        result = test(outcomes)
        passed += result == "ok"
        print(f"{'PASS' if result == 'ok' else 'FAIL'} {test.__name__}: {result or 'production core did not run the check'}")
    print(f"deviation record: {passed} checks passed of {len(tests)}")
    return int(passed != len(tests))


if __name__ == "__main__":
    sys.exit(main())
