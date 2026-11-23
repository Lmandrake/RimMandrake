#!/usr/bin/env python3
"""Blind lane 1, GimmeSomeSlack 0.1.1, cycle 1: the shipped settings as text (the mod_settings floor: "defaults that equal the
shipped behaviour"). For each settings file: every saved field's initialiser equals its Scribe default (a player who never
opened the window and one who saved an untouched window play the same game), and every slider's range holds its default.
    python3 blind_settings.py [--mod-root <dir>]    one JSON row per line; exit 0 = no FAIL row"""
import argparse, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
FILES = ["Source/Aerial/AerialSettings.cs", "Source/GimmeSomeSlackMod.cs", "Source/Core/ConduitPlacementGate.cs", "Source/Core/RebuildGate.cs"]
CONSTS = {"AerialMath.DripLoopsDefault": None}


def norm(v):
    v = v.strip()
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)f?", v)
    if m: return float(m.group(1))
    return v.split(".")[-1] if re.fullmatch(r"[A-Za-z_][\w.]*", v) and v not in ("true", "false") else v


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mod-root", default=MOD)
    a = ap.parse_args()
    km = open(os.path.join(a.mod_root, "Source/Aerial/AerialMath.cs")).read()
    m = re.search(r"public const bool DripLoopsDefault = (true|false);", km)
    rows, mism, slid, n_sc, n_sl, unread = [], [], [], 0, 0, []
    for f in FILES:
        p = os.path.join(a.mod_root, f)
        if not os.path.exists(p): unread.append(f); continue
        src = open(p).read()
        if m: src = src.replace("AerialMath.DripLoopsDefault", m.group(1))
        fields = {mm.group(2): mm.group(3) for mm in re.finditer(r"public static (\w+) (\w+) = ([^;]+);", src)}
        for mm in re.finditer(r"Scribe_Values\.Look\(ref (\w+), \"(\w+)\", ([^)]+)\)", src):
            name, default = mm.group(1), mm.group(3)
            if name not in fields: continue
            n_sc += 1
            if "LegacyName" in default: continue   # an "unset" sentinel for a renamed key, migrated on load: not a default
            if norm(fields[name]) != norm(default): mism.append("%s %s: initialiser %s, saved default %s" % (f, name, fields[name], default))
        for mm in re.finditer(r"(\w+) = (?:Mathf\.Round(?:ToInt)?\()?list\.Slider\((\w+), (-?[\d.]+)f, (-?[\d.]+)f\)", src):
            name, lo, hi = mm.group(2), float(mm.group(3)), float(mm.group(4))
            if name not in fields: continue
            n_sl += 1
            d = norm(fields[name])
            if not isinstance(d, float) or not (lo <= d <= hi): slid.append("%s %s default %s outside slider %s..%s" % (f, name, fields[name], lo, hi))
    rows.append(dict(id="settings_initialiser_equals_saved_default", bars=["mod_settings", "settings_switch_cleanly"], kind="sweep",
                     verdict="FAIL" if mism or unread or not n_sc else "PASS", cases=n_sc,
                     detail="%d saved settings across %d files; initialiser != Scribe default: %s; unread %s" % (n_sc, len(FILES), mism[:8], unread)))
    rows.append(dict(id="settings_default_inside_slider", bars=["mod_settings"], kind="sweep",
                     verdict="FAIL" if slid or not n_sl else "PASS", cases=n_sl,
                     detail="%d sliders with a literal range; a default outside its slider: %s" % (n_sl, slid[:8])))
    for r in rows: print(json.dumps(r))
    sys.exit(1 if any(r["verdict"] == "FAIL" for r in rows) else 0)


main()
