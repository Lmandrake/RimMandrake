#!/usr/bin/env python3
"""
extract_mlie_sounds.py - one-shot extraction+remap for MLIE_FAUNA_ABSORPTION_1's
sound-absorption slice (owner ruling 2026-09-02: "Absorb all the sounds
absolutely.").

Pulls every AudioClip out of mlie.starwarsanimalcollection's AssetBundle,
writes them as WAV files under src/RimStarWars/SWBestiary/Sounds/SWanimals/,
and rewrites the donor's SoundDefs XML with an RSW_-prefixed defName for
every entry (clipPath folder name is kept identical - only the top-level mod
changes, so the internal SWanimals/<name> reference needs no per-entry edit).

Not reusable machinery like extract_bundle.py - this is a single-purpose
script for one absorption pass, kept for provenance/re-run rather than as a
general tool. Run with python.exe (Windows) - UnityPy is only installed
there in this environment, not under WSL's python3.
"""
import json
import os
import re
import xml.etree.ElementTree as ET

import UnityPy

BUNDLE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3497316713\AssetBundles\Mlie_StarWarsAnimalCollection"
SRC_SOUNDDEFS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3497316713\1.6\Defs\SoundDefs\Sounds_SWanimals.xml"
OUT_SOUNDS_DIR = r"D:\Luke\dev\Rimworld\src\RimStarWars\SWBestiary\Sounds\SWanimals"
OUT_DEFS_PATH = r"D:\Luke\dev\Rimworld\src\RimStarWars\SWBestiary\Defs\SoundDefs\SoundDefs_SWBestiary.xml"
OUT_MAP_PATH = r"D:\Luke\dev\Rimworld\infrastructure\state\facts\mlie_sound_defname_map.json"

PREFIX = "RSW_"


def extract_audio():
    os.makedirs(OUT_SOUNDS_DIR, exist_ok=True)
    env = UnityPy.load(BUNDLE)
    written = {}
    failed = []
    for obj in env.objects:
        if obj.type.name != "AudioClip":
            continue
        try:
            data = obj.read()
        except Exception as e:
            failed.append((f"path_id {obj.path_id}", str(e)))
            continue
        name = str(getattr(data, "m_Name", "") or "")
        try:
            samples = data.samples
        except Exception as e:
            failed.append((name, str(e)))
            continue
        if not samples:
            failed.append((name, "no samples returned"))
            continue
        for fname, raw in samples.items():
            out_path = os.path.join(OUT_SOUNDS_DIR, fname)
            with open(out_path, "wb") as f:
                f.write(raw)
            written[name] = fname
    return written, failed


def transform_defs(written: dict):
    tree = ET.parse(SRC_SOUNDDEFS)
    root = tree.getroot()
    defs = root.findall("SoundDef")
    name_map = {}
    n_ok = 0
    n_missing_audio = []
    for d in defs:
        dn = d.find("defName")
        old_name = dn.text
        new_name = PREFIX + old_name
        dn.text = new_name
        name_map[old_name] = new_name
        if old_name not in written:
            n_missing_audio.append(old_name)
        n_ok += 1

    new_root = ET.Element("Defs")
    for d in defs:
        new_root.append(d)
    ET.indent(new_root, space="  ")
    os.makedirs(os.path.dirname(OUT_DEFS_PATH), exist_ok=True)
    tree_out = ET.ElementTree(new_root)
    tree_out.write(OUT_DEFS_PATH, encoding="utf-8", xml_declaration=True)

    os.makedirs(os.path.dirname(OUT_MAP_PATH), exist_ok=True)
    with open(OUT_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(name_map, f, indent=2, sort_keys=True)

    return n_ok, n_missing_audio


def main():
    written, failed = extract_audio()
    print(f"extracted {len(written)} audio clips, {len(failed)} failures")
    for name, err in failed:
        print(f"  FAIL {name}: {err}")

    n_ok, missing = transform_defs(written)
    print(f"transformed {n_ok} SoundDefs")
    if missing:
        print(f"  {len(missing)} defs have NO matching extracted audio (name mismatch, needs investigation):")
        for m in missing:
            print(f"    {m}")

    total_bytes = sum(
        os.path.getsize(os.path.join(OUT_SOUNDS_DIR, f))
        for f in os.listdir(OUT_SOUNDS_DIR)
    )
    print(f"total audio on disk: {total_bytes} bytes ({total_bytes / 1024 / 1024:.1f} MB), {len(os.listdir(OUT_SOUNDS_DIR))} files")


if __name__ == "__main__":
    main()
