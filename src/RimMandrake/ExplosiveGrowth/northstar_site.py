"""ExplosiveGrowth's site preconditions for the northstar driver.
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives (existing bridge tools).

The site must let plants GROW: a plant that is dormant (cold, dark, no fertility) is wet but
correctly never charges, so a cold or night map would read as a mod failure. The suite re-checks
the anchor's temperature per chain; this reads the same fact once, up front, so the run is
refused with the reason instead of recording a page of UNMEASURED."""
from northstar_driver import site

SETTINGS = "RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings"
# shipped defaults, as the strings C# prints (str(10.0) would be "10.0" and read as drift)
DEFAULTS = {
    "enabled": "True",
    "dryWetMultiplier": "10",
    "dryDryMultiplier": "0.1",
    "wetNativeMultiplier": "4",
    "treeRatio": "0.625",
    "stuntedMultiplier": "0.4",
    "vanillaCropsNeedWater": "True",
    "vanillaDryMultiplier": "0.1",
    "nearbyRadius": "2",
    "nativesSameRuleInOtherBiomes": "False",
    "defaultRuptureChance": "0.3333",
    "wetFruitFactor": "2",
    "cropSelfFruitEnabled": "True",
    "waterUseEnabled": "True",
    "cropDrawLevels": "1",
    "dormancyEnabled": "True",
    "tidalLockNoRest": "True",
    "sealedGrowersVanilla": "True",
    "waveStaggerEnabled": "False",
    "minGrowDaysToSoak": "1",
    "cavePlantsNeverSoak": "True",
    "naturalWaterEnabled": "True",
    "spillWaterEnabled": "True",
    "irrigationSoakEnabled": "True",
    "rainWaterEnabled": "True",
    "rainLingerHours": "3",
    "rainPuddlesEnabled": "True",
    "snowmeltEnabled": "True",
    "gradientSurgeSoakEnabled": "True",
    "ashFreshEnabled": "True",
    "ashFlushDays": "3",
    "chargeHours": "6",
    "maxOvergrowthScale": "2",
    "reprintIntervalTicks": "250",
    "hueShiftEnabled": "True",
    "tellSoundsEnabled": "True",
    "groundTellEnabled": "True",
    "churnEnabled": "True",
    "burstEnabled": "True",
    "burstHurtsPawns": "True",
    "tinderEnabled": "True",
    "slimeEnabled": "True",
    "ruptureEnabled": "True",
    "ruptureMutationChance": "0.08",
    "flushEnabled": "True",
    "harvestJackpotEnabled": "True",
    "lastSwingGambleEnabled": "True",
    "suppressionEnabled": "True",
}


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 100:
        bad.append("map_size: both axes must be >= 100, got %sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
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
        x, z = (mm.get("sizeX") or 250) // 2, (mm.get("sizeZ") or 250) // 2
        r = s.call("jawa/cell_temperature", cell="%d,%d" % (x, z)) or {}
        temp = r.get("temperature")
        if temp is None or not (8.0 <= float(temp) <= 38.0):
            bad.append("temperature: the map centre reads %r C; plants are dormant outside ~8-38 C, so "
                       "nothing can charge. Start a temperate quicktest map." % (temp,))
    except Exception as ex:
        bad.append("temperature: %s" % ex)
    return bad
