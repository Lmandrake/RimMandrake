#!/usr/bin/env python3
"""landmark_rename_save.py - rename world landmarks in a RimWorld savegame, offline.

Landmark.name is a plain scribed string in WorldLandmarks' dictionary
(<landmarks><landmarks><keys>tile,layer</keys><values><li><def/><name/></li>...),
so a rename is a text edit of one <name> element; no world_commit, no live game.
The edit touches only those <name> bytes, so the rest of the file is byte-identical.

Each rename row is guarded: the tile must still hold the row's def and old name,
else the whole run refuses (a remade world must not be renamed from a stale list).
A backup `<save>.bak-pre-<tag>` is written before the first write and never overwritten.

  python3 landmark_rename_save.py --renames <json> --save <rws> [--save <rws> ...] [--apply --tag <tag>]

Without --apply it prints the plan and changes nothing. LANDMARK_NAMING_PASS_1.
"""
import argparse
import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


def _xml_text(raw):
    """Decode element text exactly as an XML parser does (named and numeric references)."""
    return ET.fromstring("<n>" + raw + "</n>").text or ""


def _plain_name(new):
    """True when `new` is non-blank and survives escape -> XML parse unchanged (no NUL, no control chars)."""
    try:
        return bool(new.strip()) and _xml_text(escape(new)) == new
    except ET.ParseError:
        return False


def _landmark_values_span(text):
    """(start, end) of the inner WorldLandmarks <keys>..</values> region."""
    outer = text.find("<landmarks>")
    if outer < 0:
        raise ValueError("no <landmarks> element")
    inner = text.find("<landmarks>", outer + len("<landmarks>"))
    keys = text.find("<keys>", inner)
    end = text.find("</values>", keys)
    if inner < 0 or keys < 0 or end < 0 or text.find("</landmarks>", outer) < keys:
        raise ValueError("unexpected WorldLandmarks layout")
    return keys, end


def read_landmarks(text):
    """List of dicts {tile, layer, def, name, name_span} in file order."""
    keys_at, end = _landmark_values_span(text)
    keys_end = text.index("</keys>", keys_at)
    keys = []
    pos = keys_at
    while True:
        a = text.find("<li>", pos, keys_end)
        if a < 0:
            break
        b = text.index("</li>", a)
        tile, layer = text[a + 4:b].split(",")
        keys.append((int(tile), int(layer)))
        pos = b
    vals_at = text.index("<values>", keys_end)
    rows = []
    pos = vals_at
    while True:
        a = text.find("<li>", pos, end)
        if a < 0:
            break
        b = text.index("</li>", a)
        block = text[a:b]
        if "<li>" in block[4:] or "<!--" in block or "<![CDATA[" in block:
            raise ValueError("nested <li>, comment or CDATA in a landmark value; layout changed")
        d0 = block.index("<def>") + 5
        n0 = block.index("<name>") + 6
        rows.append({"def": block[d0:block.index("</def>")],
                     "name": _xml_text(block[n0:block.index("</name>")]),
                     "name_span": (a + n0, a + block.index("</name>"))})
        pos = b
    if len(rows) != len(keys):
        raise ValueError(f"{len(keys)} keys but {len(rows)} values")
    for r, (t, l) in zip(rows, keys):
        r["tile"], r["layer"] = t, l
    return rows


def plan(text, renames):
    """[(row, rename)] or raise with every guard failure listed."""
    by_tile = {}
    for r in read_landmarks(text):
        by_tile.setdefault(r["tile"], []).append(r)
    out, bad = [], []
    for rn in renames:
        hits = [r for r in by_tile.get(rn["tile"], []) if r["def"] == rn["def"]]
        if not _plain_name(rn["new"]):
            bad.append(f"tile {rn['tile']}: new name {rn['new']!r} is not a plain XML string")
        elif len(hits) != 1:
            bad.append(f"tile {rn['tile']}: {len(hits)} landmarks of def {rn['def']}")
        elif hits[0]["name"] == rn["new"]:
            continue  # already applied
        elif hits[0]["name"] != rn["old"]:
            bad.append(f"tile {rn['tile']}: name is {hits[0]['name']!r}, row expects {rn['old']!r}")
        else:
            out.append((hits[0], rn))
    if bad:
        raise ValueError("guard refused:\n  " + "\n  ".join(bad))
    return out


def apply(text, steps):
    for row, rn in sorted(steps, key=lambda s: -s[0]["name_span"][0]):
        a, b = row["name_span"]
        text = text[:a] + escape(rn["new"]) + text[b:]
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--renames", required=True)
    ap.add_argument("--save", action="append", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--tag", help="backup suffix, required with --apply")
    a = ap.parse_args(argv)
    if a.apply and not a.tag:
        ap.error("--apply needs --tag")
    renames = json.load(open(a.renames, encoding="utf-8"))["renames"]
    staged = []  # phase 1: plan and verify every save; nothing is written unless all pass
    for path in a.save:
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        try:
            steps = plan(text, renames)
            print(f"{path}: {len(steps)} to rename, {len(renames) - len(steps)} already done")
            for row, rn in steps:
                print(f"  {rn['tile']:>6} {rn['def']}: {rn['old']!r} -> {rn['new']!r}")
            new = apply(text, steps)
            ET.fromstring(new.encode("utf-8"))  # the whole save must still parse
            if plan(new, renames):
                raise ValueError("renames did not read back")
        except (ValueError, ET.ParseError) as e:
            print(f"REFUSED {path}: {e} (no save written)")
            return 2
        bak = f"{path}.bak-pre-{a.tag}"
        if steps and a.apply and os.path.exists(bak) and os.path.getsize(bak) != os.path.getsize(path):
            print(f"REFUSED {path}: backup {bak} exists and differs in size from the save (no save written)")
            return 2
        staged.append((path, steps, new, bak))
    if not a.apply:
        return 0
    for path, steps, new, bak in staged:  # phase 2: back up, then write
        if not steps:
            continue
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        print(f"  wrote {path} ({os.path.getsize(path)} bytes); backup {bak}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
