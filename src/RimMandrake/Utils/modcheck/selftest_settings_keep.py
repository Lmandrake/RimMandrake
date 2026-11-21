"""selftest_settings_keep.py -- offline checks of settings_keep.py and its run_identity hooks.

    python3 src/RimMandrake/Utils/modcheck/selftest_settings_keep.py

Item RIMMANDRAKE_RESTORE_SLACK_LOOK_FILE_AFTER_PROOF_LEFT_EXTCORD: ST4 left <style>ExtensionCord</style> on disk and the
next load started on that look. Temp folders only; never a real game's Config folder.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import settings_keep as SK  # noqa: E402
import run_identity as RI  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))
    if not cond:
        FAILS.append(name)


def mkdir(files):
    d = os.path.join(tempfile.mkdtemp(), "Config")
    os.makedirs(d)
    for n, t in files.items():
        write(d, n, t)
    return d


def write(d, n, t):
    with open(os.path.join(d, n), "wb") as f:
        f.write(t.encode("latin-1"))


def read(d, n):
    p = os.path.join(d, n)
    return open(p, "rb").read().decode("latin-1") if os.path.exists(p) else None


GSS, AER, OTHER, NEW = ("Mod_GimmeSomeSlack_GimmeSomeSlackMod.xml", "Mod_GimmeSomeSlack_AerialLinesMod.xml",
                        "Mod_FlowWorks_FlowWorksMod.xml", "Mod_GimmeSomeSlack_NewMod.xml")
JAWA = "\xef\xbb\xbf<SettingsBlock><ModSettings><style>StarWarsJawa</style></ModSettings></SettingsBlock>"
EXT = JAWA.replace("StarWarsJawa", "ExtensionCord")

# 1. a run that changes the files: every one of the mod's files ends as found
d = mkdir({GSS: JAWA, AER: "<a>1</a>", OTHER: "<f>1</f>"})
k = SK.Keep("GimmeSomeSlack", d)
rec = k.take()
check("1 take reads the found look", rec["found"].get(GSS) == "StarWarsJawa", rec)
check("1 take writes the sidecar before the run", os.path.exists(k.sidecar))
write(d, GSS, EXT)                     # what ST4 did
write(d, AER, "<a>2</a>")
write(d, NEW, "<n/>")
write(d, OTHER, "<f>2</f>")
back = k.put_back()
check("1 the found bytes are back, BOM included", read(d, GSS) == JAWA, back)
check("1 every file of the mod is back", read(d, AER) == "<a>1</a>")
check("1 a file the run made is removed", read(d, NEW) is None)
check("1 the record names the look at the end and after", back["at_end"].get(GSS) == "ExtensionCord" and back["after"].get(GSS) == "StarWarsJawa", back)
check("1 the sidecar is removed", not os.path.exists(k.sidecar))
check("1 control: another mod's file is not ours to keep", read(d, OTHER) == "<f>2</f>")

# 2. control: a run that changes nothing rewrites nothing
d = mkdir({GSS: JAWA})
k = SK.Keep("GimmeSomeSlack", d)
k.take()
check("2 control: nothing changed, nothing rewritten", k.put_back()["rewritten"] == [])

# 3. a killed run (no finally): the next take on that game puts the found file back before it reads
d = mkdir({GSS: JAWA})
SK.Keep("GimmeSomeSlack", d).take()
write(d, GSS, EXT)
k = SK.Keep("GimmeSomeSlack", d)
r = k.take()
check("3 the next take puts the killed run's file back first", r.get("stale_sidecar_put_back") == [GSS] and r["found"][GSS] == "StarWarsJawa", r)
k.put_back()
check("3 and that run ends on the found look", read(d, GSS) == JAWA)

# 4. could not look and found none are different answers
r = SK.Keep("GimmeSomeSlack", os.path.join(tempfile.mkdtemp(), "nope")).take()
check("4 no Config folder reads unmeasured, never a found set", "unmeasured" in r and "found" not in r, r)
d = mkdir({OTHER: "<f/>"})
k = SK.Keep("GimmeSomeSlack", d)
check("4 a mod with no settings file reads found {}", k.take().get("found") == {})
write(d, GSS, EXT)
k.put_back()
check("4 and a file the run made is then removed", read(d, GSS) is None)
check("4 put_back with nothing taken says so", SK.Keep("GimmeSomeSlack", d).put_back() == {"put_back": "nothing taken"})

# 5. the run_identity hooks: run_start keeps, run_end puts back and records both
d = mkdir({GSS: JAWA})
RI.SETTINGS_CONFIG_DIR = d
real_fp = RI.mod_fingerprint
RI.mod_fingerprint = lambda mod, dm=None, mods_dir=None: {"state": "in-sync"}
try:
    ident = RI.run_start("GimmeSomeSlack", "proof_all")
    write(d, GSS, EXT)
    ident = RI.run_end(ident, "GimmeSomeSlack")
finally:
    RI.mod_fingerprint = real_fp
sf = ident.get("settings_files") or {}
check("5 run_end puts the file back", read(d, GSS) == JAWA, sf)
check("5 the identity records found, at_end and after", sf.get("found", {}).get(GSS) == "StarWarsJawa" and
      sf.get("at_end", {}).get(GSS) == "ExtensionCord" and sf.get("after", {}).get(GSS) == "StarWarsJawa", sf)
check("5 control: run_end without a run_start keeps nothing", RI.run_end({}, "GimmeSomeSlack").get("settings_files") is None)

print("\n%s" % ("ALL PASS" if not FAILS else "FAILED: %s" % FAILS))
sys.exit(1 if FAILS else 0)
