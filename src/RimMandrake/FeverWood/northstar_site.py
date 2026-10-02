"""FeverWood's site preconditions for the northstar driver. `preflight(s) -> [str]`: every failed
precondition, empty = clean. Dev tooling, never deployed. Built only from northstar_driver.site
primitives (existing bridge tools) plus one plan-only deploy check.

The mod ships COMPOSED inside mandrake.rm.biomes, and the driver's own deploy-fingerprint check skips
folded sources, so a run would otherwise test whatever composed copy the game folder happens to hold.
`composed_deploy_drift` runs the compose plan (read-only, never --apply) and refuses on any drift in
this mod's files or the EnvironmentalHazards kit it depends on."""
import os
import re
import subprocess

from northstar_driver import site

SETTINGS = "RimMandrake.FeverWood.RM_FeverWoodSettings"
MIN_MAP = 150               # the suite's pad sits 45 cells off the map centre and is 29 wide
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DRIFT_NEEDLES = ("FeverWood", "EnvironmentalHazards")
_SETTINGS_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "S" + "ource", "RM_FeverWoodMod.cs")


def shipped_defaults(path=_SETTINGS_SRC):
    """{field: default} for every `public static bool|int|float` of the settings class, read from the C#
    (the same derivation validation.py uses, so the two cannot disagree)."""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for m in re.finditer(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);", fh.read()):
            typ, nm, raw = m.group(1), m.group(2), m.group(3).strip()
            out[nm] = (raw == "true") if typ == "bool" else (int(raw) if typ == "int" else float(raw.rstrip("f")))
    return out


def composed_deploy_drift(root=ROOT, timeout=900):
    """Drift lines of `deploy_custom_mods.py --compose biomes` (plan only) naming this mod or its kit.
    Runs under WSL python3: the deploy tool is developed there and a Windows interpreter composes the
    same files with different line endings and reports drift. Raises on a plan that did not run."""
    p = subprocess.run(["wsl.exe", "--cd", root, "-e", "python3",
                        "src/RimMandrake/Utils/deploy_custom_mods.py", "--compose", "biomes"],
                       capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode not in (0, 1) or "Traceback" in out:
        raise RuntimeError("compose plan did not run (rc=%s): %s" % (p.returncode, out[-300:]))
    # `+`/`~` lines are drift; `-` lines are files only in the game folder (kept), the tool's only
    # reason to exit 1 when everything else is in sync
    return [ln.strip() for ln in out.splitlines()
            if re.match(r"\s+[+~]\s", ln) and any(n in ln for n in DRIFT_NEEDLES)]


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < MIN_MAP:
        bad.append("map_size: both axes must be >= %d, got %sx%s" % (MIN_MAP, mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    try:
        defaults = shipped_defaults()
        if len(defaults) < 20:
            bad.append("settings_defaults: parsed only %d fields from the C# source" % len(defaults))
        wrong = {}
        for field, want in defaults.items():           # numeric compare: C# prints 6f as "6", python as "6.0"
            r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}
            got = r.get("value")
            if isinstance(want, bool):
                same = str(got) == str(want)
            else:
                try:
                    same = abs(float(got) - float(want)) < 1e-4
                except (TypeError, ValueError):
                    same = False
            if r.get("success") is False or not same:
                wrong[field] = got
        if wrong:
            bad.append("settings_defaults: not at shipped defaults: %s" % wrong)
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    try:
        site.weather_lock(s, "Clear")
    except Exception as ex:
        bad.append("weather: %s" % ex)
    try:
        drift = composed_deploy_drift()
        if drift:
            bad.append("composed_deploy: the game's mandrake.rm.biomes differs from source in %d file(s) "
                       "(deploy_custom_mods.py --compose biomes --apply, game closed): %s" % (len(drift), drift[:3]))
    except Exception as ex:
        bad.append("composed_deploy: could not check: %s" % ex)
    return bad
