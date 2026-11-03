#!/usr/bin/env python3
"""Offline test of meleeanim_lasso_setting.py on fixture copies (LASSO_CONFIG_UNSET_1)."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import meleeanim_lasso_setting as M  # noqa: E402

BOM = "﻿"
LIVE_SHAPE = (BOM + '<?xml version="1.0" encoding="utf-8"?>\r\n<SettingsBlock>\r\n'
              '\t<ModSettings Class="AM.AMSettings.Settings">\r\n\t\t<animSettings>\r\n\t\t\t<keys />\r\n'
              '\t\t</animSettings>\r\n\t\t<IsFirstTimeRunning>False</IsFirstTimeRunning>\r\n'
              '\t</ModSettings>\r\n</SettingsBlock>')
fails = []


def check(name, cond):
    print("%s %s" % ("PASS" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, M.FILE_NAME)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(LIVE_SHAPE)
    # sanity probe: the instrument sees an absent element as FAIL, not PASS
    check("absent element -> check exit 1", M.main(["--check", "--file", p]) == 1)
    check("apply exit 0", M.main(["--apply", "--file", p, "--no-backup"]) == 0)
    check("check after apply exit 0", M.main(["--check", "--file", p]) == 0)
    raw = open(p, encoding="utf-8", newline="").read()
    check("BOM kept", raw.startswith(BOM))
    check("CRLF kept, no bare LF", "\n" not in raw.replace("\r\n", ""))
    check("element inside ModSettings", raw.index("<LassoSpawnChance>0</LassoSpawnChance>")
          < raw.index("</ModSettings>") and raw.index("<ModSettings") < raw.index("<LassoSpawnChance>"))
    check("indent matches siblings", "\r\n\t\t<LassoSpawnChance>0</LassoSpawnChance>\r\n" in raw)
    check("other settings untouched", "<IsFirstTimeRunning>False</IsFirstTimeRunning>" in raw)
    check("idempotent: one element after second apply",
          M.main(["--apply", "--file", p, "--no-backup"]) == 0
          and open(p, encoding="utf-8").read().count("<LassoSpawnChance>") == 1)
    # a non-zero written value is rewritten, and fails check before
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(LIVE_SHAPE.replace("<IsFirstTimeRunning>", "<LassoSpawnChance>0.35</LassoSpawnChance><IsFirstTimeRunning>"))
    check("nonzero -> check exit 1", M.main(["--check", "--file", p]) == 1)
    M.main(["--apply", "--file", p, "--no-backup"])
    check("nonzero rewritten to 0", M.read_value(open(p, encoding="utf-8-sig").read()) == "0")
    check("absent file -> check exit 1", M.main(["--check", "--file", os.path.join(d, "nope.xml")]) == 1)
    check("is_zero parses '0.0'", M.is_zero("0.0") and not M.is_zero("0.2") and not M.is_zero(None))

print("RESULT %s" % ("FAIL " + ", ".join(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
