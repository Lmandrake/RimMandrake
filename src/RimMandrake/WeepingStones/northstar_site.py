"""WeepingStones' site preconditions for the northstar driver. `preflight(s) -> [str]`: every failed
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

SETTINGS = "RimMandrake.WeepingStones.RM_WeepingStonesSettings"
DEFAULTS = {"stockedPoolsEnabled": True}
MIN_MAP = 150               # the suite's pad sits 45 cells off the map centre and is 29 wide
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DRIFT_NEEDLES = ("WeepingStones", "EnvironmentalHazards")


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
        wrong = site.read_settings(s, SETTINGS, DEFAULTS)
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
