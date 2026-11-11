"""Windows Python, field-only L1 warning contract; no map, save or ticks advanced.

Initializer and absent-key Scribe evidence is source evidence. A loaded original
of six can be an explicit persisted customization, not a failed shipped default.
Sanitize touches other numeric settings: snapshot its complete assignment set,
restore original bridge strings in finally without sanitizing again, and require
actual matching readbacks. Never call WriteSettings or reset all settings.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

MOD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOD.parent / "Utils"))
from validation_core import Bridge  # noqa: E402
import game_paths  # noqa: E402

SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
KERNEL = "RimMandrake.TitanicCreatures.RM_TitanicKernel"
WARNING = "titanEventWarningHours"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--deployed-mod", type=Path, default=Path(game_paths.LOCAL_MODS) / "HugeThings")
    a = ap.parse_args()
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "level": "L1",
              "scope": "field-only; no map/save/scene/crossing or time advancement",
              "calls": [], "errors": [], "restoration": {"attempted": False, "ok": False}}
    a.out.parent.mkdir(parents=True, exist_ok=True)

    def persist():
        a.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def require(ok, message):
        if not ok:
            raise RuntimeError(message)

    b = None
    originals = {}
    config_dir = Path(game_paths.MODS_CONFIG).parent

    def settings_files():
        # Hash only this mod's settings, never Player.log or endpoint credentials.
        return {p.name: digest(p) for p in config_dir.glob("Mod_*.xml")
                if "hugethings" in p.name.lower()}

    def call(tool, **params):
        # Schemas are discovered and checked before constructing any tool calls.
        require(set(params) <= declared[tool], "undeclared parameters: " + tool)
        entry = {"tool": tool, "params": params}
        report["calls"].append(entry)
        try:
            result = b.call(tool, **params)
            entry["result"] = result
            persist()
            require(result.get("success") is True, "missing/refused success: " + tool)
            return result
        except Exception as exc:
            entry["error"] = str(exc)
            persist()
            raise

    def field(action, name, value=None):
        params = dict(typeName=SETTINGS, action=action, field=name)
        if value is not None:
            params["value"] = value
        r = call("jawa/mod_settings_field", **params)
        require(r.get("fieldKind") == "static", "not a static setting: " + name)
        return r

    def read(name):
        r = field("get", name)
        require(isinstance(r.get("value"), str), "unreadable setting: " + name)
        return r["value"]

    def invoke(type_name, method, args=""):
        return call("jawa/static_call", type=type_name, method=method, args=args)

    try:
        src = MOD / "Source/RM_HugeThingsSettings.cs"
        text = src.read_text(encoding="utf-8")
        body = text.split("public static void Sanitize()", 1)[1].split("\n        }", 1)[0]
        statements = body.strip().lstrip("{").strip().split(";")
        require(all(not s.strip() or re.fullmatch(
            r"\s*\w+\s*=\s*RM_TitanicKernel\.SaneSetting\([^;]+\)\s*", s)
            for s in statements), "Sanitize has unaccounted side effects")
        names = re.findall(r"^\s*(\w+)\s*=", body, re.M)
        numeric = set(re.findall(r"public static (?:float|int|double) (\w+)\s*=", text))
        require(names and len(set(names)) == len(names) and set(names) <= numeric,
                "Sanitize assignments are not understood numeric static fields")
        checks = {
            "initializer_two": bool(re.search(r"public static float titanEventWarningHours = 2f;", text)),
            "scribe_absent_key_two": 'Scribe_Values.Look(ref titanEventWarningHours, "titanEventWarningHours", 2f);' in text,
            "sanitize_fallback_two": 'SaneSetting(titanEventWarningHours, 0.5f, 24f, 2f)' in body,
            "slider_unchanged": 'list.Slider(titanEventWarningHours, 0.5f, 24f)' in text,
        }
        report.update(source_sha256=digest(src), script_sha256=digest(Path(__file__)),
                      source_checks=checks, sanitize_fields=names)
        require(all(checks.values()), "source default/range contract mismatch")
        dll = MOD / "Assemblies/RM_HugeThings.dll"
        stamp = dll.with_suffix(".dll.srchash")
        # The stamp lists every compiled input; verify it against these exact bytes.
        stamp_text = stamp.read_text(encoding="utf-8")
        stamp_rows = re.findall(r"^([0-9a-f]{64}) (.+)$", stamp_text, re.M)
        require(stamp_rows, "empty source stamp")
        for expected, name in stamp_rows:
            require(digest(src.parent / name.strip()) == expected, "stamp/source mismatch: " + name)
        require("# dll: " + digest(dll) in stamp_text, "stamp/DLL mismatch")
        installed = a.deployed_mod / "Assemblies" / dll.name
        installed_stamp = installed.with_suffix(".dll.srchash")
        report["artifact"] = {"repo_sha256": digest(dll), "deployed_sha256": digest(installed),
                              "source_stamp": stamp_text, "stamp_sha256": digest(stamp),
                              "deployed_stamp_sha256": digest(installed_stamp)}
        require(digest(dll) == digest(installed) and digest(stamp) == digest(installed_stamp),
                "deployed artifact does not match source-built pair")
        b = Bridge()
        tools = b.S.list_tools()
        report["jawa_tool_count"] = sum(t.get("name", "").startswith("jawa/") for t in tools)
        wanted = ("jawa/mod_settings_field", "jawa/static_call")
        schemas = {t["name"]: t for t in tools if t.get("name") in wanted}
        report["schemas"] = schemas
        declared = {name: b.S._declared_params(schemas.get(name)) for name in wanted}
        require(all(declared.values()), "missing live tool schema")
        require({"typeName", "action", "field", "value"} <= declared[wanted[0]] and
                {"type", "method", "args"} <= declared[wanted[1]], "unexpected live schemas")
        listing = call(wanted[0], typeName=SETTINGS, action="list")
        rows = {r["name"]: r for r in listing.get("fields", [])}
        for name in names:
            require(rows.get(name, {}).get("kind") == "static" and
                    rows[name].get("type") in ("Single", "Int32", "Double"), "missing numeric field: " + name)
            originals[name] = read(name)
        report["originals"] = originals.copy()
        report["loaded_original_warning"] = originals[WARNING]
        report["settings_files_before"] = settings_files()
        persist()
        # Snapshot must be complete before the first mutation.
        report["restoration"]["attempted"] = True
        field("set", WARNING, "NaN")
        require(read(WARNING) == "NaN", "invalid input did not read back as NaN")
        invoke(SETTINGS, "Sanitize")
        fallback = read(WARNING)
        report["invalid_fallback_readback"] = fallback
        require(float(fallback) == 2, "NaN fallback is not two")
        ticks = invoke(KERNEL, "WarningTicks", fallback)
        report["two_hour_ticks"] = ticks.get("result")
        require(str(ticks.get("result")) == "5000", "two hours did not produce 5000 ticks")
        field("set", WARNING, "6")
        require(float(read(WARNING)) == 6, "custom six write mismatch")
        invoke(SETTINGS, "Sanitize")
        custom = read(WARNING)
        report["custom_six_readback"] = custom
        require(float(custom) == 6, "valid custom six changed")
        ticks = invoke(KERNEL, "WarningTicks", custom)
        report["six_hour_ticks"] = ticks.get("result")
        require(str(ticks.get("result")) == "15000", "six hours did not produce 15000 ticks")
    except Exception as exc:
        report["errors"].append(str(exc))
    finally:
        if report["restoration"]["attempted"]:
            restored = {}
            failures = []
            for name, value in originals.items():
                try:
                    field("set", name, value)
                    restored[name] = read(name)
                    require(restored[name] == value, "restore readback mismatch: " + name)
                except Exception as exc:
                    failures.append(str(exc))
            report["restoration"].update(readbacks=restored, failures=failures,
                                          ok=not failures and restored == originals)
            report["settings_files_after"] = settings_files()
            if report["settings_files_before"] != report["settings_files_after"]:
                report["errors"].append("settings file bytes changed")
        if b is not None:
            b.S.close()
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        report["ok"] = not report["errors"] and report["restoration"]["ok"]
        persist()
    print(json.dumps({k: report.get(k) for k in ("ok", "errors", "loaded_original_warning",
                     "invalid_fallback_readback", "two_hour_ticks", "custom_six_readback", "six_hour_ticks")}))
    print("restoration:", report["restoration"]["ok"], "receipt:", a.out)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
