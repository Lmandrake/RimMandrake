#!/usr/bin/env python3
"""Melee Animation's natural lasso spawn chance: read it, or write it to 0 (LASSO_CONFIG_UNSET_1).

The setting is `AM.AMSettings.Settings.LassoSpawnChance` (float, default 0.2f; Keyed label
"Lasso Commonality"). Melee Animation's SimpleSettings scribes each field by its own name with
`Scribe_Values.Look(ref v, Name, default)` (Epicguru/Melee-Animation, Source/1.6/AnimationMod/
AMSettings/SimpleSettings.cs), so a value equal to the default is NOT written: an absent element
means 0.2 is live. The only way to make 0 stick is to write the element explicitly.

The game reads this file at load; a running game keeps the value it loaded, and closing Melee
Animation's settings dialog in a running game rewrites the file from memory. Apply at game-down,
or apply while up and keep the dialog shut until the next load.

  --check   exit 0 if the live file's <ModSettings> holds <LassoSpawnChance>0</...>, else exit 1
  --apply   back the file up to agent storage, then set the element to 0 (idempotent)
  --file P  operate on P instead of the live Config file (tests)
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FILE_NAME = "Mod_2944488802_Core.xml"      # workshop 2944488802 = Melee Animation, Mod class "Core"
ELEMENT = "LassoSpawnChance"
_ELEM = re.compile(r"<%s>([^<]*)</%s>" % (ELEMENT, ELEMENT))
_MODSETTINGS_OPEN = re.compile(r'<ModSettings\s+Class="AM\.AMSettings\.Settings"\s*>')


def live_path():
    import game_paths as GP
    return os.path.join(GP.LOCALLOW, "Config", FILE_NAME)


def read_value(text):
    """The written value as a string, or None when the element is absent (default 0.2 live)."""
    m = _ELEM.search(text)
    return m.group(1).strip() if m else None


def is_zero(value):
    try:
        return value is not None and float(value) == 0.0
    except ValueError:
        return False


def set_zero(text):
    """Return text with LassoSpawnChance = 0 inside AM's ModSettings. Raises if the block is absent."""
    if _ELEM.search(text):
        return _ELEM.sub("<%s>0</%s>" % (ELEMENT, ELEMENT), text, count=1)
    m = _MODSETTINGS_OPEN.search(text)
    if not m:
        raise ValueError('no <ModSettings Class="AM.AMSettings.Settings"> block')
    nl = "\r\n" if "\r\n" in text else "\n"
    # Indent like the block's own children (the line after the opening tag).
    rest = text[m.end():]
    ind = re.match(r"\s*?(?:\r?\n)([ \t]*)", rest)
    indent = ind.group(1) if ind else "\t\t"
    return text[:m.end()] + nl + indent + "<%s>0</%s>" % (ELEMENT, ELEMENT) + rest


def backup_dir():
    tool = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
    out = subprocess.run([sys.executable, tool], capture_output=True, text=True, timeout=60)
    base = out.stdout.strip()
    if out.returncode != 0 or not base:
        raise SystemExit("meleeanim_lasso_setting: cannot read agent storage: %s" % out.stderr.strip())
    return os.path.join(base, "rimmandrake", "backups", "config")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--no-backup", action="store_true", help="tests only")
    a = ap.parse_args(argv)
    path = a.file or live_path()
    if not os.path.isfile(path):
        print("FAIL %s absent (absence = default 0.2 live)" % path)
        return 1
    with open(path, encoding="utf-8-sig", newline="") as fh:
        text = fh.read()
    val = read_value(text)
    if a.check:
        ok = is_zero(val)
        print("%s %s %s=%s" % ("PASS" if ok else "FAIL", path, ELEMENT,
                               val if val is not None else "absent (default 0.2)"))
        return 0 if ok else 1
    if is_zero(val):
        print("UNCHANGED %s already %s=0" % (path, ELEMENT))
        return 0
    new = set_zero(text)
    if not a.no_backup:
        d = backup_dir()
        os.makedirs(d, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(d, "%s.BEFORE-lasso0-%s.xml" % (FILE_NAME[:-4], stamp))
        shutil.copy2(path, bak)
        print("backup %s" % bak)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write(new)
    print("WROTE %s %s: %s -> 0" % (path, ELEMENT, val if val is not None else "absent"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
