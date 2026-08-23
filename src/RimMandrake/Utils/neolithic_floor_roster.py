#!/usr/bin/env python3
r"""neolithic_floor_roster.py - the "bows and knives" floor, measured rather than listed.

WHY THIS EXISTS
---------------
WEAPON_FLOOR_BOWS_KNIVES_1 (owner, 2026-08-22): *"The cheap end should be bows and
knives for anyone... but it's ok if you make them cheaper so that nobody just spawns
with fists."* DECIDE owes **the roster** - which defs across the live mod set are the
neolithic floor, what each costs, and which tags reach them.

Three sources, and they disagree in a way that matters:

  1. the def dump          post-inheritance, post-patch. Has the tags and the prices.
  2. the Cherry Picker cfg the LIVE cut list. A def can be present in the dump and
                           cut in the config - the dump is a snapshot, the config is now.
  3. ModsConfig.xml        which mods were loaded when the dump was taken.

🔴 A CUT WEAPON STILL APPEARS IN THE DUMP. Cherry Picker removes at runtime, so a def
sitting in the dump with `weaponTags: []` may be a weapon the config killed, not a
weapon whose author forgot to tag it. This script joins the two and says which.

⚠️ THE DUMP GOES STALE THE MOMENT THE CONFIG CHANGES. It reports the dump's capture
date beside the config's mtime and refuses to call a def's tag state CURRENT when the
config is newer.

    python3 src/RimMandrake/Utils/neolithic_floor_roster.py
    python3 src/RimMandrake/Utils/neolithic_floor_roster.py --csv <out.csv>
"""
from __future__ import annotations
import argparse, csv, json, os, sqlite3, sys, datetime as dt
from collections import defaultdict

DB = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
      "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
CP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
      "RimWorld by Ludeon Studios/Config/Mod_3521312241_Mod_CherryPicker.xml")

# 🔑 What counts as the floor. NOT "everything at techLevel Neolithic" - that set
# includes 30 tusks, horns and survival tools that are weapons only because the engine
# says a tusk can be swung. The floor is a weapon a pawn KIND could be handed.
EXCLUDE_SUBSTR = ("Tusk", "Horn", "Fangs", "Tooth", "Spike", "SurvivalTools_",
                  "WoodLog", "CrystalWood", "BoneItem")


def load_cut() -> set[str]:
    """Every `ThingDef/<name>` line in the live Cherry Picker config."""
    cut = set()
    if not os.path.exists(CP):
        return cut
    with open(CP, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("<li>ThingDef/") and line.endswith("</li>"):
                cut.add(line[len("<li>ThingDef/"):-len("</li>")])
    return cut


def market_value(fields: dict):
    """MarketValue off statBases. ⚠️ None is UNMEASURED, never 0 - a stuffed weapon
    carries its value in the stuff and several defs inherit a value the dump does not
    resolve. A price filter that reads None as cheap is lying in the safe direction."""
    sb = fields.get("statBases")
    if not isinstance(sb, list):
        return None
    for s in sb:
        if isinstance(s, dict) and s.get("stat") == "MarketValue":
            return s.get("value")
    return None


def collect():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cut = load_cut()
    rows, tagmap = [], defaultdict(list)
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        isd = d.get("is", {})
        if not isd.get("weapon"):
            continue
        # 🔴 A BOTTLE IS A MELEE WEAPON TO THE ENGINE. Whiskey, gin, rum and beer all
        # pass `is.weapon` at techLevel Neolithic, and three of them were tagged into
        # the melee pools once before weapon_tag_audit.py started excluding them.
        if isd.get("ingestible"):
            continue
        f = d["fields"]
        for t in (f.get("weaponTags") or []):
            tagmap[t].append(d["defName"])
        if f.get("techLevel") != "Neolithic":
            continue
        name = d["defName"]
        if any(s in name for s in EXCLUDE_SUBSTR):
            continue
        rows.append({
            "defName": name,
            "label": d.get("label") or "",
            "mod": d.get("modName") or "",
            "melee": "melee" if isd.get("meleeWeapon") else ("ranged" if isd.get("rangedWeapon") else "?"),
            "cut": "CUT" if name in cut else "",
            "weaponTags": "|".join(f.get("weaponTags") or []),
            "weaponClasses": "|".join(f.get("weaponClasses") or []),
            "marketValue": market_value(f),
            "stuff": "|".join(f.get("stuffCategories") or []),
        })
    rows.sort(key=lambda r: (r["cut"], r["melee"], r["defName"]))
    return rows, tagmap, cut


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    args = ap.parse_args()
    if not os.path.exists(DB):
        print(f"UNMEASURED no defs.sqlite at {DB} - run `measure build`")
        return 2
    rows, tagmap, cut = collect()

    cap = sqlite3.connect(f"file:{DB}?mode=ro", uri=True).execute(
        "SELECT value FROM provenance WHERE key='captured_utc'").fetchone()
    cap = cap[0] if cap else "?"
    cp_m = dt.datetime.utcfromtimestamp(os.path.getmtime(CP)).isoformat() + "Z" if os.path.exists(CP) else "?"
    stale = cp_m > cap
    print(f"dump captured {cap} | cherrypicker mtime {cp_m}"
          + ("   🔴 CONFIG IS NEWER - tag state for anything cut or un-cut since is STALE" if stale else ""))
    live = [r for r in rows if not r["cut"]]
    print(f"MEASURED {len(rows)} neolithic weapon defs after excluding tusks/tools; "
          f"{len(live)} survive the live cut list, {len(rows)-len(live)} are CUT")
    untagged = [r for r in live if not r["weaponTags"]]
    print(f"🔴 {len(untagged)} SURVIVING floor weapons carry NO weaponTags - unreachable by any kind: "
          + ", ".join(r["defName"] for r in untagged[:12]))
    for w in ("ranged", "melee"):
        sub = [r for r in live if r["melee"] == w]
        print(f"  surviving {w}: {len(sub)} — "
              + ", ".join(f"{r['defName']}({r['marketValue'] if r['marketValue'] is not None else 'UNMEASURED'})"
                          for r in sub))
    for t in sorted(k for k in tagmap if k.startswith("Neolithic")):
        print(f"  {t:26s} {len(tagmap[t]):4d} carriers")
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} rows -> {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
