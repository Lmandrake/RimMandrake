"""Acceptance test for RIMMANDRAKE_FREE_PYRE_SITE_SKY_TUTOR_PINS_CLEAR_FOREVER (WSL python3, repo root): the quiet storyteller every
Pyrelands test site is saved with must not be a tutorial storyteller. Vanilla WeatherDecider.ChooseNextWeather returns Clear
whenever TutorSystem.TutorialMode && ClearWeatherAllowed, and Pyrelands ApplySettings always lists Clear (weight 0), so a
Tutor site never leaves Clear. Exit 0 ok, 1 FAIL (watched: FAIL on base 9894d872fe with Tutor; ok with Cassandra), 2 UNMEASURED.
Expected: 1 row ok. The live half: on a reloaded NS_Pyrelands site, jawa/static_call RimWorld.TutorSystem get_TutorialMode = False."""
import re, glob, sys, xml.etree.ElementTree as ET
src = open("src/RimMandrake/Pyrelands/preflight_pyrelands.py").read()
name = re.search(r'^QUIET_STORYTELLER\s*=\s*"([^"]+)"', src, re.M).group(1)
tm = None
for f in glob.glob("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/*/Defs/Storyteller*/*.xml"):
    for d in ET.parse(f).getroot():
        if d.findtext("defName") == name:
            tm = (d.findtext("tutorialMode") or "false").strip().lower()
if tm is None:
    print("UNMEASURED: no StorytellerDef %s in Data/*/Defs/Storyteller*" % name); sys.exit(2)
ok = tm != "true"
print("%s QUIET_STORYTELLER=%s tutorialMode=%s (a tutorial storyteller makes WeatherDecider pick Clear forever)" % ("ok" if ok else "FAIL", name, tm))
sys.exit(0 if ok else 1)
